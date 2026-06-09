"""
Sparkplug B publisher (protobuf) — parallel to JSON UNS topics.

Topics:
  spBv1.0/{group}/NBIRTH/{node}
  spBv1.0/{group}/NDEATH/{node}
  spBv1.0/{group}/DBIRTH/{node}/{device}
  spBv1.0/{group}/DDEATH/{node}/{device}
  spBv1.0/{group}/DDATA/{node}/{device}
"""
from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional, Tuple

try:
    from tahu import sparkplug_b_pb2 as spb
except ImportError:
    spb = None  # type: ignore

SPARKPLUG_NS = "spBv1.0"

# Sparkplug B DataType enum values (sparkplug_b.proto)
DT_INT32 = 3
DT_FLOAT = 9
DT_BOOLEAN = 11
DT_STRING = 12
DT_UINT64 = 8


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    if not raw:
        return default
    return raw in ("1", "true", "yes", "on")


class SparkplugBridge:
    """Builds Sparkplug B protobuf payloads and topic names."""

    def __init__(
        self,
        *,
        enabled: bool,
        group_id: str,
        node_id: str,
        device_id: str,
    ):
        self.enabled = enabled and spb is not None
        self.group_id = group_id
        self.node_id = node_id
        self.device_id = device_id
        self.seq = 0
        self.bd_seq = 0
        self.last_event = ""

    @classmethod
    def from_env(cls, mqtt_enabled: bool) -> "SparkplugBridge":
        sp_enabled = _env_bool("SPARKPLUG_ENABLED") or _env_bool("MQTT_SPARKPLUG")
        return cls(
            enabled=mqtt_enabled and sp_enabled,
            group_id=os.environ.get("SPARKPLUG_GROUP_ID", "Aspire").strip() or "Aspire",
            node_id=os.environ.get("SPARKPLUG_NODE_ID", "football-server").strip() or "football-server",
            device_id=os.environ.get("SPARKPLUG_DEVICE_ID", "match").strip() or "match",
        )

    def public_config(self) -> Dict[str, Any]:
        if not self.enabled:
            return {"enabled": False}
        return {
            "enabled": True,
            "namespace": SPARKPLUG_NS,
            "groupId": self.group_id,
            "nodeId": self.node_id,
            "deviceId": self.device_id,
            "topics": {
                "nbirth": self.topic("NBIRTH"),
                "dbirth": self.topic("DBIRTH"),
                "ddata": self.topic("DDATA"),
                "ndeath": self.topic("NDEATH"),
                "ddeath": self.topic("DDEATH"),
            },
        }

    def topic(self, msg_type: str) -> str:
        if msg_type in ("NBIRTH", "NDEATH", "NCMD", "STATE"):
            return f"{SPARKPLUG_NS}/{self.group_id}/{msg_type}/{self.node_id}"
        return f"{SPARKPLUG_NS}/{self.group_id}/{msg_type}/{self.node_id}/{self.device_id}"

    def _next_seq(self) -> int:
        self.seq = (self.seq + 1) % 256
        return self.seq

    def _payload(self) -> Any:
        assert spb is not None
        p = spb.Payload()
        p.timestamp = int(time.time() * 1000)
        p.seq = self._next_seq()
        return p

    def _add_metric(
        self,
        payload: Any,
        name: str,
        datatype: int,
        value: Any,
        *,
        include_name: bool = True,
    ) -> None:
        m = payload.metrics.add()
        if include_name:
            m.name = name
        m.datatype = datatype
        m.timestamp = payload.timestamp
        if datatype == DT_INT32:
            m.int_value = int(value)
        elif datatype == DT_UINT64:
            m.long_value = int(value)
        elif datatype == DT_FLOAT:
            m.float_value = float(value)
        elif datatype == DT_BOOLEAN:
            m.boolean_value = bool(value)
        elif datatype == DT_STRING:
            m.string_value = str(value)

    def encode_nbirth(self) -> Tuple[str, bytes]:
        p = self._payload()
        self._add_metric(p, "bdSeq", DT_UINT64, self.bd_seq)
        self._add_metric(p, "Node Control/Rebirth", DT_BOOLEAN, False)
        return self.topic("NBIRTH"), p.SerializeToString()

    def encode_ndeath(self) -> Tuple[str, bytes]:
        self.bd_seq = (self.bd_seq + 1) % 256
        p = self._payload()
        self._add_metric(p, "bdSeq", DT_UINT64, self.bd_seq)
        return self.topic("NDEATH"), p.SerializeToString()

    def encode_dbirth(self) -> Tuple[str, bytes]:
        p = self._payload()
        defs: List[Tuple[str, int]] = [
            ("score_red", DT_INT32),
            ("score_blue", DT_INT32),
            ("time_left", DT_FLOAT),
            ("autoplay", DT_BOOLEAN),
            ("ball_x", DT_FLOAT),
            ("ball_y", DT_FLOAT),
            ("possession_red", DT_INT32),
            ("possession_blue", DT_INT32),
            ("team_red", DT_STRING),
            ("team_blue", DT_STRING),
            ("last_event", DT_STRING),
        ]
        for name, dt in defs:
            self._add_metric(p, name, dt, _default_for_type(dt))
        return self.topic("DBIRTH"), p.SerializeToString()

    def encode_ddeath(self) -> Tuple[str, bytes]:
        p = self._payload()
        self._add_metric(p, "bdSeq", DT_UINT64, self.bd_seq)
        return self.topic("DDEATH"), p.SerializeToString()

    def encode_ddata(self, state: Dict[str, Any], *, event: str = "") -> Tuple[str, bytes]:
        if event:
            self.last_event = event
        score = state.get("score") or {}
        ball = state.get("ball") or {}
        stats = state.get("stats") or {}
        possession = stats.get("possession") or {}
        team_red = state.get("teamRed") or {}
        team_blue = state.get("teamBlue") or {}

        p = self._payload()
        metrics: List[Tuple[str, int, Any]] = [
            ("score_red", DT_INT32, int(score.get("Red") or 0)),
            ("score_blue", DT_INT32, int(score.get("Blue") or 0)),
            ("time_left", DT_FLOAT, float(state.get("timeLeft") or 0)),
            ("autoplay", DT_BOOLEAN, bool(state.get("autoplay"))),
            ("ball_x", DT_FLOAT, float(ball.get("x") or 0)),
            ("ball_y", DT_FLOAT, float(ball.get("y") or 0)),
            ("possession_red", DT_INT32, int(possession.get("Red") or 50)),
            ("possession_blue", DT_INT32, int(possession.get("Blue") or 50)),
            ("team_red", DT_STRING, str(team_red.get("name") or "Red")),
            ("team_blue", DT_STRING, str(team_blue.get("name") or "Blue")),
            ("last_event", DT_STRING, self.last_event),
        ]
        for name, dt, val in metrics:
            self._add_metric(p, name, dt, val, include_name=True)
        return self.topic("DDATA"), p.SerializeToString()


def _default_for_type(datatype: int) -> Any:
    if datatype == DT_INT32:
        return 0
    if datatype == DT_UINT64:
        return 0
    if datatype == DT_FLOAT:
        return 0.0
    if datatype == DT_BOOLEAN:
        return False
    if datatype == DT_STRING:
        return ""
    return 0
