/* Shared helpers: i18n labels, offline QR, state API headers */
(function (global) {
  const LANG_KEY = "make-football-lang-v1";

  const I18N = {
    de: {
      title: "⚽ PTE Football Soccer — KI-gesteuert",
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
    },
    en: {
      title: "⚽ PTE Football Soccer — LLM Driven",
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
      if (el) el.textContent = t(key);
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

  global.PTEFeatures = { I18N, t, getLang, setLang, applyI18n, stateFetchHeaders, spectatorUrl, drawOfflineQR };
})(window);
