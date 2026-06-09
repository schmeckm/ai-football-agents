/* Shared helpers: i18n labels, offline QR, state API headers */
(function (global) {
  const LANG_KEY = "make-football-lang-v1";

  const I18N = {
    de: {
      title: "⚽ Football Soccer — KI-gesteuert",
      subtitle: "🇺🇸 FIFA WM 2026 · USA · Kanada · Mexiko",
      match_setup: "🏆 Match-Setup",
      setup_cap: "Teams, Nationen und Spielzeit einstellen. Übernehmen startet ein frisches Match.",
      team_a: "Team A (links, greift rechts an)",
      team_b: "Team B (rechts, greift links an)",
      name: "Name", nation: "Nation", color: "Farbe",
      dynamics: "Dynamik",
      preview_anthem: "🎵 Hymne testen",
      anthems_hdr: "🎵 Nationalhymnen",
      anthems_cap: "Anpfiff: beide Teams. Spielende: nur Sieger. MP3s in static/anthems/",
      anthem_kickoff: "Hymne Anpfiff (je Team)",
      anthem_winner: "Siegerhymne",
      draw_anthem: "Hymne bei Unentschieden",
      draw_none: "Keine", draw_host: "Gastgeber-Nation", draw_both: "Beide Teams (kurz)", draw_fanfare: "Fanfare",
      host_nation: "Gastgeber-Nation",
      llm_interval: "KI-Reaktionszeit",
      match_duration: "Spielzeit",
      sfx_vol: "🔊 Stadion-SFX",
      anthem_vol: "🎵 Hymnen-Lautstärke",
      state_token: "🔒 Spectator-Token (optional)",
      state_token_cap: "Muss mit STATE_TOKEN auf dem Server übereinstimmen",
      spectator_phone: "📱 Zuschauer-Handy",
      spectator_cap: "QR scannen — gleiches WLAN. URL unten kopieren.",
      apply: "✅ Übernehmen & neues Match",
      start: "▶️ Spiel starten", pause: "⏸️ Pause", resume: "▶️ Weiter", new_match: "▶️ Neues Match",
      end_match: "🏁 Spiel beenden",
      coach: "Team coachen",
      coach_cap: "4 Rollen pro Team. Leerer Prompt = Spieler inaktiv.",
      tactical_ai: "✨ Taktik-Coach KI",
      generate: "✨ Generieren",
      reset_ball: "🔄 Ball zurücksetzen",
      reset_match: "⏮️ Match zurücksetzen",
      skip_ceremony: "⏭ Ceremony überspringen",
      fulltime: "🏁 Spielende",
      halftime: "⏸️ HALBZEIT",
      ht_resume: "▶️ Zweite Halbzeit",
      ft_new: "▶️ Neues Match",
      ft_highlights: "🎬 Highlights",
      ft_penalty: "🎯 Elfmeterschießen",
      ft_heatmap: "🔥 Heatmap",
      ft_close: "Schließen",
      pen_close: "🏁 Ergebnis anzeigen",
      pen_take: "⚽ Elfmeter",
      hint: "Tasten: F Vollbild · M Stumm · Leertaste Start · E Beenden",
      lang_label: "🌐 Sprache",
      help_title: "❓ Hilfe & Features",
      help_cap: "Überblick über alle Funktionen des Programms.",
      help_cat_sim: "⚽ Simulation",
      help_sim_1: "8 KI-Spieler (4 Rollen × 2 Teams) steuern Laufwege und Schüsse per LLM.",
      help_sim_2: "60-FPS-Physik: Ball, Tackling, Torwartzonen, Live-Schiedsrichter.",
      help_sim_3: "Cartoon-Köpfe oder Basler Fasnacht-Larven — pro Spieler deterministisch.",
      help_sim_4: "22 Nationen mit Flaggen, Teamfarben und Dynamik-Slider pro Seite.",
      help_cat_tactics: "🧠 Taktik & Coaching",
      help_tac_1: "16 Strategie-Presets (4 pro Rolle) — z. B. Pressing, Sweeper, Line Goalie.",
      help_tac_2: "Taktik-Coach KI: Idee eingeben → 4 Prompts für das aktive Team generieren.",
      help_tac_3: "Prompts live während des Spiels ändern — wirksam ab dem nächsten KI-Tick.",
      help_tac_4: "Leerer Prompt = Spieler inaktiv (gestrichelter Kreis auf dem Platz).",
      help_tac_5: "Strategie-Bibliothek: Speichern, Laden, JSON Export/Import.",
      help_cat_flow: "🏟️ Spielablauf",
      help_flow_1: "Anpfiff-Ceremony mit Nationalhymnen (MP3 oder Synth-Fallback).",
      help_flow_2: "Halbzeit-Pause: Taktik anpassen, dann zweite Halbzeit.",
      help_flow_3: "Tore: Flash, Konfetti, Bildschirmshake, Slow-Motion-Replay.",
      help_flow_4: "Spielende: Highlights, Heatmap, Elfmeterschießen bei Unentschieden.",
      help_flow_5: "Spiel früh beenden — Sieger- oder Unentschieden-Hymne.",
      help_cat_audio: "🔊 Audio & Kommentar",
      help_aud_1: "Stadion-SFX: Pfiff, Schuss, Tor, Jubel (Web Audio).",
      help_aud_2: "KI-Kommentator mit optionalem Browser-TTS und Stimmen-Auswahl.",
      help_aud_3: "Getrennte Lautstärke für SFX und Hymnen.",
      help_cat_stats: "📊 Statistik & Zuschauer",
      help_stat_1: "Live: Ballbesitz, Kicks, Schüsse pro Team.",
      help_stat_2: "Turnier-Rangliste im Browser (Siege/Niederlagen/Punkte).",
      help_stat_3: "QR-Code & /spectator — Handy-Ansicht im gleichen WLAN.",
      help_stat_4: "LED-Banner, Flugzeug-Werbebanner, Beat-Mörker Easter Egg.",
      help_cat_keys: "⌨️ Tastenkürzel",
      help_key_f: "Vollbild",
      help_key_m: "Stumm",
      help_key_space: "Start/Pause",
      help_key_e: "Beenden",
      help_key_esc: "Schließen",
      help_cat_mqtt: "📡 MQTT / Unified Namespace",
      help_mqtt_cap: "Optional: Live-Spielzustand wird an einen MQTT-Broker publiziert (UNS-Topics, Industrie-Demo).",
      help_mqtt_1: "Aktivierung: MQTT_ENABLED=1 in .env — Broker z. B. Mosquitto auf Port 1883.",
      help_mqtt_2: "Topics erscheinen beim Serverstart (retained meta + match/state).",
      help_mqtt_3: "MQTT Explorer oder MQTTX: Host localhost, Port 1883, Subscribe {prefix}/#",
      help_mqtt_4: "KI-Bewegungen bleiben HTTP (/api/move) — nur State & Events über MQTT.",
      help_mqtt_5: "Handy-Spectator: MQTT-WebSocket wenn MQTT_WS_URL gesetzt, sonst HTTP-Polling.",
      help_mqtt_6: "Status: GET /api/mqtt/status · Konfiguration: GET /api/config",
      help_mqtt_7: "Sparkplug B (optional): SPARKPLUG_ENABLED=1 — Protobuf auf spBv1.0/{group}/DDATA/…",
      help_mqtt_topics_loading: "MQTT-Topics werden geladen…",
      help_mqtt_sparkplug: "Sparkplug B",
      help_mqtt_topics_off: "MQTT deaktiviert (MQTT_ENABLED=0). HTTP-Sync aktiv.",
      help_mqtt_topics_connected: "Verbunden",
      help_mqtt_topics_disconnected: "Nicht verbunden",
    },
    en: {
      title: "⚽ Football Soccer — LLM Driven",
      subtitle: "🇺🇸 FIFA World Cup 2026 · USA · Canada · Mexico",
      match_setup: "🏆 Match setup",
      setup_cap: "Name your sides, pick nations, set the clock. Apply starts a fresh match.",
      team_a: "Team A (left, attacks right goal)",
      team_b: "Team B (right, attacks left goal)",
      name: "Name", nation: "Nation", color: "Color",
      dynamics: "Dynamics",
      preview_anthem: "🎵 Preview anthem",
      anthems_hdr: "🎵 National anthems",
      anthems_cap: "Kickoff plays both teams; full time plays the winner. MP3s in static/anthems/",
      anthem_kickoff: "Kickoff anthem (each team)",
      anthem_winner: "Winner anthem",
      draw_anthem: "Draw anthem",
      draw_none: "None", draw_host: "Host nation", draw_both: "Both teams (short)", draw_fanfare: "Fanfare",
      host_nation: "Host nation",
      llm_interval: "AI reaction interval",
      match_duration: "Match duration",
      sfx_vol: "🔊 Stadium SFX volume",
      anthem_vol: "🎵 Anthem volume",
      state_token: "🔒 Spectator token (optional)",
      state_token_cap: "Must match server STATE_TOKEN env var",
      spectator_phone: "📱 Phone spectator",
      spectator_cap: "Scan QR on same network. Copy URL below.",
      apply: "✅ Apply & new match",
      start: "▶️ Start match", pause: "⏸️ Pause match", resume: "▶️ Resume match", new_match: "▶️ New match",
      end_match: "🏁 End match",
      coach: "Coach your team",
      coach_cap: "Four roles per side. Empty prompt = player inactive.",
      tactical_ai: "✨ Tactical Coach AI",
      generate: "✨ Generate",
      reset_ball: "🔄 Reset ball",
      reset_match: "⏮️ Reset match",
      skip_ceremony: "⏭ Skip ceremony",
      fulltime: "🏁 Full Time",
      halftime: "⏸️ HALF TIME",
      ht_resume: "▶️ Out for the second half",
      ft_new: "▶️ New match",
      ft_highlights: "🎬 Highlights",
      ft_penalty: "🎯 Penalty Shootout",
      ft_heatmap: "🔥 Heat Map",
      ft_close: "Close",
      pen_close: "🏁 Show result",
      pen_take: "⚽ Take Penalty",
      hint: "Keys: F fullscreen · M mute · Space kick off · E end match",
      lang_label: "🌐 Language",
      help_title: "❓ Help & Features",
      help_cap: "Overview of everything this app can do.",
      help_cat_sim: "⚽ Simulation",
      help_sim_1: "8 AI players (4 roles × 2 teams) — LLM decides movement and shots.",
      help_sim_2: "60 FPS physics: ball, tackling, keeper zones, live referee.",
      help_sim_3: "Cartoon faces or Basel carnival Larven masks — deterministic per player.",
      help_sim_4: "22 nations with flags, team colours, and per-side dynamics slider.",
      help_cat_tactics: "🧠 Tactics & Coaching",
      help_tac_1: "16 strategy presets (4 per role) — e.g. pressing, sweeper, line goalie.",
      help_tac_2: "Tactical Coach AI: type an idea → generates 4 prompts for the active team.",
      help_tac_3: "Edit prompts live mid-match — takes effect on the next AI tick.",
      help_tac_4: "Empty prompt = inactive player (dashed circle on the pitch).",
      help_tac_5: "Strategy library: save, load, JSON export/import.",
      help_cat_flow: "🏟️ Match Flow",
      help_flow_1: "Kickoff ceremony with national anthems (MP3 or synth fallback).",
      help_flow_2: "Halftime pause: tweak tactics, then resume for the second half.",
      help_flow_3: "Goals: flash, confetti, screen shake, slow-motion replay.",
      help_flow_4: "Full time: highlights, heat map, penalty shootout on draws.",
      help_flow_5: "End match early — winner or draw anthem plays.",
      help_cat_audio: "🔊 Audio & Commentary",
      help_aud_1: "Stadium SFX: whistle, kick, goal, crowd cheer (Web Audio).",
      help_aud_2: "AI commentator with optional browser TTS and voice picker.",
      help_aud_3: "Separate volume sliders for SFX and anthems.",
      help_cat_stats: "📊 Stats & Spectator",
      help_stat_1: "Live possession, kicks, and shots per team.",
      help_stat_2: "Tournament leaderboard in the browser (W/D/L/points).",
      help_stat_3: "QR code & /spectator — phone view on the same LAN.",
      help_stat_4: "LED banners, flying plane ad, Beat Mörker easter egg.",
      help_cat_keys: "⌨️ Keyboard Shortcuts",
      help_key_f: "Fullscreen",
      help_key_m: "Mute",
      help_key_space: "Start/Pause",
      help_key_e: "End match",
      help_key_esc: "Close modal",
      help_cat_mqtt: "📡 MQTT / Unified Namespace",
      help_mqtt_cap: "Optional: live match state is published to an MQTT broker (UNS-style topics, industrial demo).",
      help_mqtt_1: "Enable MQTT_ENABLED=1 in .env — broker e.g. Mosquitto on port 1883.",
      help_mqtt_2: "Topics appear on server start (retained meta + match/state).",
      help_mqtt_3: "MQTT Explorer or MQTTX: host localhost, port 1883, subscribe {prefix}/#",
      help_mqtt_4: "LLM moves stay on HTTP (/api/move) — only state & events use MQTT.",
      help_mqtt_5: "Phone spectator: MQTT WebSocket if MQTT_WS_URL is set; else HTTP polling.",
      help_mqtt_6: "Status: GET /api/mqtt/status · config: GET /api/config",
      help_mqtt_7: "Sparkplug B (optional): SPARKPLUG_ENABLED=1 — protobuf on spBv1.0/{group}/DDATA/…",
      help_mqtt_topics_loading: "Loading MQTT topics…",
      help_mqtt_sparkplug: "Sparkplug B",
      help_mqtt_topics_off: "MQTT disabled (MQTT_ENABLED=0). HTTP sync active.",
      help_mqtt_topics_connected: "Connected",
      help_mqtt_topics_disconnected: "Not connected",
    },
  };

  function getLang() {
    return localStorage.getItem(LANG_KEY) || "de";
  }
  function setLang(lang) {
    localStorage.setItem(LANG_KEY, lang);
  }
  function t(key) {
    const lang = getLang();
    return (I18N[lang] && I18N[lang][key]) || I18N.en[key] || key;
  }

  function applyI18n() {
    const map = {
      "page-title": "title",
      "ui-subtitle": "subtitle",
      "ui-match-setup": "match_setup",
      "ui-setup-cap": "setup_cap",
      "ui-team-a": "team_a",
      "ui-team-b": "team_b",
      "ui-anthems-hdr": "anthems_hdr",
      "ui-anthems-cap": "anthems_cap",
      "ui-spectator-hdr": "spectator_phone",
      "ui-spectator-cap": "spectator_cap",
      "ui-coach": "coach",
      "ui-coach-cap": "coach_cap",
      "ui-tactical": "tactical_ai",
      "ceremony-skip": "skip_ceremony",
      "ft-h1": "fulltime",
      "ht-h1": "halftime",
      "ht-resume": "ht_resume",
      "ft-new": "ft_new",
      "ft-highlights": "ft_highlights",
      "ft-penalty": "ft_penalty",
      "ft-heatmap": "ft_heatmap",
      "ft-close": "ft_close",
      "pen-close": "pen_close",
      "pen-take": "pen_take",
      "spectator-hint": "hint",
      "ui-lang-label": "lang_label",
      "help-title": "help_title",
      "help-cap": "help_cap",
      "help-cat-sim": "help_cat_sim",
      "help-sim-1": "help_sim_1",
      "help-sim-2": "help_sim_2",
      "help-sim-3": "help_sim_3",
      "help-sim-4": "help_sim_4",
      "help-cat-tactics": "help_cat_tactics",
      "help-tac-1": "help_tac_1",
      "help-tac-2": "help_tac_2",
      "help-tac-3": "help_tac_3",
      "help-tac-4": "help_tac_4",
      "help-tac-5": "help_tac_5",
      "help-cat-flow": "help_cat_flow",
      "help-flow-1": "help_flow_1",
      "help-flow-2": "help_flow_2",
      "help-flow-3": "help_flow_3",
      "help-flow-4": "help_flow_4",
      "help-flow-5": "help_flow_5",
      "help-cat-audio": "help_cat_audio",
      "help-aud-1": "help_aud_1",
      "help-aud-2": "help_aud_2",
      "help-aud-3": "help_aud_3",
      "help-cat-stats": "help_cat_stats",
      "help-stat-1": "help_stat_1",
      "help-stat-2": "help_stat_2",
      "help-stat-3": "help_stat_3",
      "help-stat-4": "help_stat_4",
      "help-cat-keys": "help_cat_keys",
      "help-key-f": "help_key_f",
      "help-key-m": "help_key_m",
      "help-key-space": "help_key_space",
      "help-key-e": "help_key_e",
      "help-key-esc": "help_key_esc",
      "help-cat-mqtt": "help_cat_mqtt",
      "help-mqtt-cap": "help_mqtt_cap",
      "help-mqtt-1": "help_mqtt_1",
      "help-mqtt-2": "help_mqtt_2",
      "help-mqtt-3": "help_mqtt_3",
      "help-mqtt-4": "help_mqtt_4",
      "help-mqtt-5": "help_mqtt_5",
      "help-mqtt-6": "help_mqtt_6",
      "help-mqtt-7": "help_mqtt_7",
      "ui-state-token-lbl": "state_token",
      "ui-host-nation-lbl": "host_nation",
      "ui-token-cap": "state_token_cap",
      "btn_apply": "apply",
      "btn_generate": "generate",
      "btn_reset": "reset_ball",
      "btn_reset_match": "reset_match",
      "btn_end_match": "end_match",
    };
    for (const [id, key] of Object.entries(map)) {
      const el = document.getElementById(id);
      if (!el) continue;
      let text = t(key);
      if (key === "help_mqtt_3" && global.__mqttTopicPrefix) {
        text = text.replace("{prefix}", global.__mqttTopicPrefix);
      }
      el.textContent = text;
    }
    const llmLbl = document.getElementById("ui-llm-label");
    if (llmLbl) llmLbl.childNodes[0].textContent = t("llm_interval") + ": ";
    const drawSel = document.getElementById("su_draw_anthem");
    if (drawSel && drawSel.options.length >= 4) {
      drawSel.options[0].textContent = t("draw_none");
      drawSel.options[1].textContent = t("draw_host");
      drawSel.options[2].textContent = t("draw_both");
      drawSel.options[3].textContent = t("draw_fanfare");
    }
  }

  function stateFetchHeaders(extra) {
    const h = Object.assign({ "Content-Type": "application/json" }, extra || {});
    const tok = localStorage.getItem("make-football-state-token-v1") || "";
    if (tok) h["X-State-Token"] = tok;
    return h;
  }

  function spectatorUrl() {
    const base = window.location.origin + "/spectator";
    const tok = localStorage.getItem("make-football-state-token-v1") || "";
    return tok ? base + "?token=" + encodeURIComponent(tok) : base;
  }

  const QR_DISPLAY_PX = 80;

  function drawOfflineQR(canvas, text, sizePx) {
    if (typeof qrcode === "undefined") return false;
    try {
      const qr = qrcode(0, "M");
      qr.addData(text);
      qr.make();
      const n = qr.getModuleCount();
      const size = sizePx || QR_DISPLAY_PX;
      const cell = Math.floor(size / n);
      const pad = Math.floor((size - cell * n) / 2);
      canvas.width = size;
      canvas.height = size;
      const ctx = canvas.getContext("2d");
      ctx.fillStyle = "#fff";
      ctx.fillRect(0, 0, size, size);
      ctx.fillStyle = "#000";
      for (let r = 0; r < n; r++) {
        for (let c = 0; c < n; c++) {
          if (qr.isDark(r, c)) ctx.fillRect(pad + c * cell, pad + r * cell, cell, cell);
        }
      }
      return true;
    } catch (e) {
      console.warn("[QR]", e);
      return false;
    }
  }

  function refreshMqttHelpTopics(cfg) {
    const el = document.getElementById("help-mqtt-topics");
    if (!el) return;
    const mqtt = (cfg && cfg.mqtt) || {};
    if (!mqtt.enabled) {
      el.innerHTML = `<span class="off">${t("help_mqtt_topics_off")}</span>`;
      global.__mqttTopicPrefix = "";
      return;
    }
    const prefix = mqtt.topicPrefix || "aspire/basel/demo/football";
    global.__mqttTopicPrefix = prefix;
    const topics = mqtt.topics || {};
    const conn = mqtt.connected
      ? `<span class="ok">${t("help_mqtt_topics_connected")}</span>`
      : `<span class="off">${t("help_mqtt_topics_disconnected")}</span>`;
    const lines = [
      `${conn} · ${mqtt.broker || "localhost:1883"}`,
      topics.meta || `${prefix}/meta`,
      topics.state || `${prefix}/match/state`,
      topics.events || `${prefix}/match/event/#`,
      topics.agents || `${prefix}/agent/+/telemetry`,
    ];
    if (mqtt.wsUrl) lines.push(`WS: ${mqtt.wsUrl}`);
    const sp = mqtt.sparkplug || {};
    if (sp.enabled && sp.topics) {
      lines.push("");
      lines.push(`${t("help_mqtt_sparkplug")}:`);
      lines.push(sp.topics.nbirth || "");
      lines.push(sp.topics.dbirth || "");
      lines.push(sp.topics.ddata || "");
    }
    el.textContent = lines.join("\n");
    const m3 = document.getElementById("help-mqtt-3");
    if (m3) m3.textContent = t("help_mqtt_3").replace("{prefix}", prefix);
  }

  async function loadMqttHelp() {
    const el = document.getElementById("help-mqtt-topics");
    if (el) el.textContent = t("help_mqtt_topics_loading");
    try {
      const r = await fetch("/api/mqtt/status");
      if (r.ok) refreshMqttHelpTopics({ mqtt: await r.json() });
      else refreshMqttHelpTopics({ mqtt: { enabled: false } });
    } catch {
      refreshMqttHelpTopics({ mqtt: { enabled: false } });
    }
  }

  global.PTEFeatures = { I18N, t, getLang, setLang, applyI18n, loadMqttHelp, refreshMqttHelpTopics, stateFetchHeaders, spectatorUrl, drawOfflineQR };
})(window);
