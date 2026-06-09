/**
 * Spectator MQTT client (Unified Namespace) with HTTP polling fallback.
 * Loads mqtt.js from CDN when MQTT is enabled in /api/config.
 */
(function (global) {
  const MQTT_CDN = "https://unpkg.com/mqtt@5.10.1/dist/mqtt.min.js";

  function loadScript(src) {
    return new Promise((resolve, reject) => {
      if (global.mqtt) {
        resolve(global.mqtt);
        return;
      }
      const s = document.createElement("script");
      s.src = src;
      s.async = true;
      s.onload = () => resolve(global.mqtt);
      s.onerror = () => reject(new Error("mqtt.js load failed"));
      document.head.appendChild(s);
    });
  }

  function createTransport(cfg) {
    let client = null;
    let mode = "http";
    let pollTimer = null;
    let staleTimer = null;
    let onPayload = null;
    let onStatus = null;

    function setStatus(label, stale) {
      if (onStatus) onStatus({ label, stale, mode });
    }

    function deliver(envelope) {
      if (!envelope || !onPayload) return;
      const data = envelope.data != null ? envelope.data : envelope;
      const stale = envelope.stale === true;
      onPayload(data, { stale, mode });
    }

    async function startHttpPoll(pollFn, intervalMs) {
      mode = "http";
      setStatus("HTTP", false);
      async function tick() {
        try {
          const json = await pollFn();
          if (!json) return;
          deliver({ data: json.data, stale: json.stale });
          setStatus(json.stale || !json.data ? "Waiting" : "Live", json.stale || !json.data);
        } catch {
          setStatus("Offline", true);
        }
      }
      await tick();
      pollTimer = setInterval(tick, intervalMs);
    }

    async function startMqtt(mqttCfg, pollFn, intervalMs) {
      if (!mqttCfg.enabled || !mqttCfg.wsUrl) {
        return startHttpPoll(pollFn, intervalMs);
      }
      try {
        await loadScript(MQTT_CDN);
      } catch {
        return startHttpPoll(pollFn, intervalMs);
      }

      const topic = mqttCfg.topics && mqttCfg.topics.state;
      if (!topic) return startHttpPoll(pollFn, intervalMs);

      return new Promise((resolve) => {
        let settled = false;
        const fallback = () => {
          if (settled) return;
          settled = true;
          if (client) {
            try { client.end(true); } catch { /* ignore */ }
            client = null;
          }
          startHttpPoll(pollFn, intervalMs).then(resolve);
        };

        const connectTimer = setTimeout(fallback, 6000);

        try {
          client = global.mqtt.connect(mqttCfg.wsUrl, {
            reconnectPeriod: 4000,
            connectTimeout: 5000,
            keepalive: 30,
          });
        } catch {
          clearTimeout(connectTimer);
          fallback();
          return;
        }

        client.on("connect", () => {
          clearTimeout(connectTimer);
          if (settled) return;
          settled = true;
          mode = "mqtt";
          setStatus("MQTT Live", false);
          client.subscribe(topic, { qos: 0 }, (err) => {
            if (err) fallback();
          });
          // Slow HTTP fallback if MQTT goes quiet
          pollTimer = setInterval(async () => {
            try {
              const json = await pollFn();
              if (json && json.data) deliver({ data: json.data, stale: json.stale });
            } catch { /* ignore */ }
          }, Math.max(intervalMs * 4, 2000));
          resolve();
        });

        client.on("message", (_topic, buf) => {
          try {
            const envelope = JSON.parse(buf.toString());
            deliver(envelope);
            setStatus("MQTT Live", envelope.stale === true);
            if (staleTimer) clearTimeout(staleTimer);
            staleTimer = setTimeout(() => setStatus("MQTT Stale", true), 3500);
          } catch { /* ignore bad payload */ }
        });

        client.on("error", () => {
          if (!settled) {
            clearTimeout(connectTimer);
            fallback();
          }
        });

        client.on("offline", () => {
          if (mode === "mqtt") setStatus("MQTT Offline", true);
        });

        client.on("reconnect", () => {
          if (mode === "mqtt") setStatus("MQTT …", true);
        });
      });
    }

    return {
      onPayload(fn) { onPayload = fn; },
      onStatus(fn) { onStatus = fn; },
      async start(cfg, pollFn, intervalMs) {
        const mqttCfg = (cfg && cfg.mqtt) || {};
        if (mqttCfg.enabled && mqttCfg.wsUrl) {
          await startMqtt(mqttCfg, pollFn, intervalMs);
        } else {
          await startHttpPoll(pollFn, intervalMs);
        }
      },
      stop() {
        if (pollTimer) clearInterval(pollTimer);
        if (staleTimer) clearTimeout(staleTimer);
        if (client) {
          try { client.end(true); } catch { /* ignore */ }
          client = null;
        }
      },
    };
  }

  global.FootballMqttSpectator = { createTransport, loadScript };
})(typeof window !== "undefined" ? window : global);
