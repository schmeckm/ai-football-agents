"""
Unified Namespace (UNS) MQTT bridge for Football Soccer.

Uses paho-mqtt in a background thread (reliable on Windows + uvicorn).
Optional Sparkplug B (protobuf) on spBv1.0/... topics in parallel to JSON UNS.

JSON topic tree (default prefix aspire/basel/demo/football):
  {prefix}/meta                      retained bridge info
  {prefix}/match/state               retained live match snapshot
  {prefix}/match/event/{type}        goal, kickoff, halftime, fulltime, ceremony
  {prefix}/agent/{player}/telemetry  optional per-player position (throttled)
"""
from __future__ import annotations

import json
import os
import queue
import sys
import threading
import time
import uuid
from typing import Any, Dict, Optional, Tuple, Union

from sparkplug_bridge import SparkplugBridge

try:
    import paho.mqtt.client as mqtt
    from paho.mqtt.enums import CallbackAPIVersion
except ImportError:
    mqtt = None  # type: ignore
    CallbackAPIVersion = None  # type: ignore

PublishItem = Tuple[str, Union[str, bytes], bool, bool]  # topic, payload, retain, binary


def _log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    if not raw:
        return default
    return raw in ("1", "true", "yes", "on")


class MqttBridge:
    """Threaded MQTT publisher with UNS JSON + optional Sparkplug B."""

    def __init__(
        self,
        *,
        enabled: bool,
        host: str,
        port: int,
        prefix: str,
        username: str = "",
        password: str = "",
        client_id: str = "",
        ws_url: str = "",
        agent_telemetry: bool = False,
        agent_interval_sec: float = 1.0,
        sparkplug: Optional[SparkplugBridge] = None,
    ):
        self.enabled = enabled and mqtt is not None
        self.host = host
        self.port = port
        self.prefix = prefix.rstrip("/")
        self.username = username
        self.password = password
        self.client_id = client_id or f"football-{uuid.uuid4().hex[:8]}"
        self.ws_url = ws_url.strip()
        self.agent_telemetry = agent_telemetry
        self.agent_interval_sec = max(0.5, agent_interval_sec)
        self.sparkplug = sparkplug or SparkplugBridge(enabled=False, group_id="", node_id="", device_id="")

        self.connected = False
        self.last_publish_ts = 0.0
        self.publish_count = 0
        self.sparkplug_publish_count = 0
        self.last_error: Optional[str] = None

        self._q: queue.Queue = queue.Queue()
        self._stop = threading.Event()
        self._ready = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._client: Optional[Any] = None

        self._last_agent_pub = 0.0
        self._prev_score: Optional[Tuple[int, int]] = None
        self._prev_ceremony_active = False
        self._prev_autoplay = False
        self._last_state: Optional[Dict[str, Any]] = None

    @classmethod
    def from_env(cls) -> "MqttBridge":
        prefix = os.environ.get(
            "MQTT_UNS_PREFIX",
            "aspire/basel/demo/football",
        ).strip().rstrip("/")
        mqtt_enabled = _env_bool("MQTT_ENABLED")
        return cls(
            enabled=mqtt_enabled,
            host=os.environ.get("MQTT_BROKER", "localhost").strip(),
            port=int(os.environ.get("MQTT_PORT", "1883")),
            prefix=prefix,
            username=os.environ.get("MQTT_USERNAME", "").strip(),
            password=os.environ.get("MQTT_PASSWORD", "").strip(),
            client_id=os.environ.get("MQTT_CLIENT_ID", "").strip(),
            ws_url=os.environ.get("MQTT_WS_URL", "").strip(),
            agent_telemetry=_env_bool("MQTT_AGENT_TELEMETRY"),
            agent_interval_sec=float(os.environ.get("MQTT_AGENT_INTERVAL_SEC", "1.0")),
            sparkplug=SparkplugBridge.from_env(mqtt_enabled),
        )

    def topic(self, *parts: str) -> str:
        suffix = "/".join(p.strip("/") for p in parts if p)
        return f"{self.prefix}/{suffix}" if suffix else self.prefix

    def public_config(self) -> Dict[str, Any]:
        if not self.enabled:
            return {"enabled": False, "sparkplug": self.sparkplug.public_config()}
        cfg: Dict[str, Any] = {
            "enabled": True,
            "connected": self.connected,
            "wsUrl": self.ws_url,
            "topicPrefix": self.prefix,
            "topics": {
                "meta": self.topic("meta"),
                "state": self.topic("match", "state"),
                "events": self.topic("match", "event", "#"),
                "agents": self.topic("agent", "+", "telemetry"),
            },
            "publishCount": self.publish_count,
            "sparkplugPublishCount": self.sparkplug_publish_count,
            "lastPublishTs": self.last_publish_ts,
            "sparkplug": self.sparkplug.public_config(),
        }
        return cfg

    def status(self) -> Dict[str, Any]:
        cfg = self.public_config()
        cfg["lastError"] = self.last_error
        cfg["broker"] = f"{self.host}:{self.port}" if self.enabled else None
        return cfg

    async def start(self) -> None:
        if not self.enabled:
            _log("[mqtt] disabled (set MQTT_ENABLED=1 to enable)")
            return
        if mqtt is None:
            _log("[mqtt] paho-mqtt not installed — pip install paho-mqtt")
            return
        self._stop.clear()
        self._ready.clear()
        self._thread = threading.Thread(target=self._worker, name="mqtt-bridge", daemon=True)
        self._thread.start()
        if not self._ready.wait(timeout=8.0):
            _log("[mqtt] broker not reachable — HTTP state sync still works")
        elif self.sparkplug.enabled:
            _log(f"[sparkplug] active group={self.sparkplug.group_id} node={self.sparkplug.node_id} device={self.sparkplug.device_id}")

    async def stop(self) -> None:
        if self.sparkplug.enabled and self.connected:
            self._enqueue_sparkplug_death()
        self._stop.set()
        self._q.put(None)
        if self._thread:
            self._thread.join(timeout=3.0)
        self._thread = None
        self._client = None
        self.connected = False
        self._ready.clear()

    def _make_client(self) -> Any:
        assert mqtt is not None and CallbackAPIVersion is not None
        client = mqtt.Client(CallbackAPIVersion.VERSION2, client_id=self.client_id)
        if self.username:
            client.username_pw_set(self.username, self.password or None)
        return client

    def _publish_now(self, topic: str, payload: Union[str, bytes], *, retain: bool = False) -> None:
        if not self._client:
            return
        info = self._client.publish(topic, payload, retain=retain, qos=0)
        info.wait_for_publish(timeout=5.0)
        self.last_publish_ts = time.time()
        self.publish_count += 1

    def _publish_meta(self) -> None:
        meta = {
            "service": "football-soccer",
            "prefix": self.prefix,
            "ts": time.time(),
            "topics": {
                "state": self.topic("match", "state"),
                "events": self.topic("match", "event", "#"),
            },
            "sparkplug": self.sparkplug.public_config(),
            "status": "online",
        }
        body = json.dumps(meta, separators=(",", ":"))
        self._publish_now(self.topic("meta"), body, retain=True)
        _log(f"[mqtt] retained meta → {self.topic('meta')}")

        idle = {
            "ts": time.time(),
            "stale": True,
            "data": None,
            "hint": "Waiting for match — open http://localhost:8001 and start a game",
        }
        self._publish_now(self.topic("match", "state"), json.dumps(idle, separators=(",", ":")), retain=True)
        _log(f"[mqtt] retained idle state → {self.topic('match', 'state')}")

    def _publish_sparkplug_birth(self) -> None:
        if not self.sparkplug.enabled:
            return
        for label, encoder in (("NBIRTH", self.sparkplug.encode_nbirth), ("DBIRTH", self.sparkplug.encode_dbirth)):
            topic, body = encoder()
            self._publish_now(topic, body, retain=False)
            self.sparkplug_publish_count += 1
            _log(f"[sparkplug] {label} → {topic} ({len(body)} bytes)")

    def _enqueue_sparkplug_death(self) -> None:
        if not self.sparkplug.enabled:
            return
        for topic, body in (self.sparkplug.encode_ddeath(), self.sparkplug.encode_ndeath()):
            self._q.put((topic, body, False, True))

    def _worker(self) -> None:
        assert mqtt is not None
        while not self._stop.is_set():
            client = None
            try:
                client = self._make_client()
                client.connect(self.host, self.port, keepalive=60)
                client.loop_start()
                self._client = client
                self.connected = True
                self.last_error = None
                self._ready.set()
                _log(f"[mqtt] connected {self.host}:{self.port} prefix={self.prefix}")
                self._publish_meta()
                self._publish_sparkplug_birth()
                if self._last_state:
                    self._enqueue_sparkplug_ddata(self._last_state)

                while not self._stop.is_set():
                    try:
                        item = self._q.get(timeout=0.4)
                    except queue.Empty:
                        continue
                    if item is None:
                        break
                    topic, payload, retain, binary = item
                    self._publish_now(topic, payload, retain=retain)
                    if binary:
                        self.sparkplug_publish_count += 1
                    tag = "sparkplug" if binary else "mqtt"
                    _log(f"[{tag}] publish {topic} ({len(payload)} bytes)")

            except Exception as exc:
                self.connected = False
                self._client = None
                self._ready.clear()
                self.last_error = str(exc)
                _log(f"[mqtt] disconnected ({exc}) — retry in 3s")
                time.sleep(3.0)
            finally:
                if client is not None:
                    try:
                        client.loop_stop()
                        client.disconnect()
                    except Exception:
                        pass
                self._client = None
                self.connected = False

    def _enqueue_json(self, topic: str, payload: Dict[str, Any], *, retain: bool = False) -> None:
        if not self.enabled or not self.connected:
            return
        body = json.dumps(payload, separators=(",", ":"))
        self._q.put((topic, body, retain, False))

    def _enqueue_sparkplug_ddata(self, state: Dict[str, Any], *, event: str = "") -> None:
        if not self.sparkplug.enabled or not self.connected:
            return
        topic, body = self.sparkplug.encode_ddata(state, event=event)
        self._q.put((topic, body, False, True))

    async def publish_state(self, payload: Dict[str, Any], ts: float) -> None:
        if not self.enabled:
            return
        self._last_state = payload
        envelope = {"ts": ts, "stale": False, "data": payload}
        self._enqueue_json(self.topic("match", "state"), envelope, retain=True)
        self._enqueue_sparkplug_ddata(payload)
        self._maybe_publish_events(payload, ts)
        self._maybe_publish_agent_telemetry(payload, ts)

    async def publish_event(self, event_type: str, data: Dict[str, Any], ts: Optional[float] = None) -> None:
        if not self.enabled:
            return
        ts = ts or time.time()
        topic = self.topic("match", "event", event_type)
        self._enqueue_json(topic, {"ts": ts, "type": event_type, **data})
        if self._last_state:
            self._enqueue_sparkplug_ddata(self._last_state, event=event_type)

    def _maybe_publish_events(self, payload: Dict[str, Any], ts: float) -> None:
        score = payload.get("score") or {}
        red = int(score.get("Red") or 0)
        blue = int(score.get("Blue") or 0)
        if self._prev_score is not None:
            prev_red, prev_blue = self._prev_score
            if red > prev_red:
                self._enqueue_json(self.topic("match", "event", "goal"), {
                    "ts": ts, "type": "goal",
                    "team": "Red",
                    "score": {"Red": red, "Blue": blue},
                    "teamName": (payload.get("teamRed") or {}).get("name", "Red"),
                })
                self._enqueue_sparkplug_ddata(payload, event="goal_red")
            if blue > prev_blue:
                self._enqueue_json(self.topic("match", "event", "goal"), {
                    "ts": ts, "type": "goal",
                    "team": "Blue",
                    "score": {"Red": red, "Blue": blue},
                    "teamName": (payload.get("teamBlue") or {}).get("name", "Blue"),
                })
                self._enqueue_sparkplug_ddata(payload, event="goal_blue")
        self._prev_score = (red, blue)

        ceremony = payload.get("ceremony") or {}
        ceremony_active = bool(ceremony.get("active"))
        if ceremony_active and not self._prev_ceremony_active:
            self._enqueue_json(self.topic("match", "event", "ceremony"), {
                "ts": ts, "type": "ceremony",
                "mode": ceremony.get("mode") or "ceremony",
                "team": ceremony.get("team"),
                "teamName": ceremony.get("teamName"),
                "statusPrefix": ceremony.get("statusPrefix"),
            })
            self._enqueue_sparkplug_ddata(payload, event="ceremony")
        self._prev_ceremony_active = ceremony_active

        autoplay = bool(payload.get("autoplay"))
        if autoplay and not self._prev_autoplay and not ceremony_active:
            self._enqueue_json(self.topic("match", "event", "kickoff"), {
                "ts": ts, "type": "kickoff",
                "score": {"Red": red, "Blue": blue},
                "teamRed": payload.get("teamRed"),
                "teamBlue": payload.get("teamBlue"),
            })
            self._enqueue_sparkplug_ddata(payload, event="kickoff")
        self._prev_autoplay = autoplay

    def _maybe_publish_agent_telemetry(self, payload: Dict[str, Any], ts: float) -> None:
        if not self.agent_telemetry:
            return
        if ts - self._last_agent_pub < self.agent_interval_sec:
            return
        self._last_agent_pub = ts
        players = payload.get("players") or {}
        for name, p in players.items():
            if not isinstance(p, dict):
                continue
            self._enqueue_json(self.topic("agent", name, "telemetry"), {
                "ts": ts,
                "player": name,
                "team": p.get("team"),
                "role": p.get("role"),
                "x": p.get("x"),
                "y": p.get("y"),
                "active": p.get("active", True),
            })
