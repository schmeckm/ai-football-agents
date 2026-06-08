/* Player avatars: cartoon + Basler Fasnacht Larven (canvas) */
(function (global) {
  function hashString(s) {
    let h = 2166136261;
    for (let i = 0; i < s.length; i++) h = ((h ^ s.charCodeAt(i)) * 16777619) >>> 0;
    return h;
  }

  const SKIN_TONES = ["#fcd9b8", "#f0c098", "#d6a17a", "#b8804a", "#8a5a32", "#5d3a1c"];
  const HAIR_COLORS = ["#1a0e08", "#3a200e", "#6b4523", "#a87436", "#c69a4f", "#d4d4d4", "#b03020"];
  const HAIR_STYLES = ["short", "spiky", "curly", "bald", "buzz", "mohawk", "long"];
  const MOUTH_STYLES = ["neutral", "smile", "smirk"];
  const LARVE_TYPES = ["waggis", "alti_dante", "vogel_gryff", "fratze", "holzlarve"];
  const LARVE_ACCENTS = ["#c62828", "#1565c0", "#f9a825", "#6a1b9a", "#2e7d32", "#ff6f00"];

  const ROLE_NUMBERS = {
    Striker: 9, Midfielder: 10, Defender: 4, Goalkeeper: 1,
  };

  function generateAppearance(playerName, style) {
    const h = hashString(playerName);
    if (style === "larve") {
      return {
        mode: "larve",
        larve: LARVE_TYPES[h % LARVE_TYPES.length],
        accent: LARVE_ACCENTS[Math.floor(h / 11) % LARVE_ACCENTS.length],
      };
    }
    return {
      mode: "cartoon",
      skin: SKIN_TONES[h % SKIN_TONES.length],
      hair: HAIR_COLORS[Math.floor(h / 7) % HAIR_COLORS.length],
      style: HAIR_STYLES[Math.floor(h / 13) % HAIR_STYLES.length],
      mouth: MOUTH_STYLES[Math.floor(h / 23) % MOUTH_STYLES.length],
    };
  }

  function drawHair(ctx, cx, cy, head_r, app) {
    ctx.fillStyle = app.hair;
    switch (app.style) {
      case "short":
        ctx.beginPath();
        ctx.arc(cx, cy, head_r * 1.02, Math.PI, Math.PI * 2);
        ctx.lineTo(cx + head_r * 0.95, cy + 1);
        ctx.lineTo(cx - head_r * 0.95, cy + 1);
        ctx.closePath();
        ctx.fill();
        break;
      case "spiky":
        ctx.beginPath();
        ctx.arc(cx, cy, head_r * 1.02, Math.PI * 1.05, Math.PI * 1.95);
        ctx.closePath();
        ctx.fill();
        for (const off of [-3.5, -1, 1.5, 4]) {
          ctx.beginPath();
          ctx.moveTo(cx + off, cy - head_r);
          ctx.lineTo(cx + off + 1, cy - head_r - 3.2);
          ctx.lineTo(cx + off + 2, cy - head_r);
          ctx.closePath();
          ctx.fill();
        }
        break;
      case "curly":
        for (const [dx, dy] of [[-4.5, -head_r], [-1.5, -head_r - 1.5], [1.5, -head_r - 1.5], [4.5, -head_r], [-5.5, -head_r + 1.5], [5.5, -head_r + 1.5]]) {
          ctx.beginPath();
          ctx.arc(cx + dx, cy + dy, 1.9, 0, Math.PI * 2);
          ctx.fill();
        }
        break;
      case "bald":
        break;
      case "buzz":
        ctx.globalAlpha = 0.55;
        ctx.beginPath();
        ctx.arc(cx, cy, head_r * 0.98, Math.PI * 1.1, Math.PI * 1.9);
        ctx.closePath();
        ctx.fill();
        ctx.globalAlpha = 1;
        break;
      case "mohawk":
        ctx.fillRect(cx - 1.4, cy - head_r - 2.5, 2.8, 4);
        ctx.beginPath();
        ctx.arc(cx, cy, head_r, Math.PI * 1.1, Math.PI * 1.9);
        ctx.closePath();
        ctx.fill();
        break;
      case "long":
        ctx.beginPath();
        ctx.arc(cx, cy, head_r * 1.05, Math.PI * 0.9, Math.PI * 2.1);
        ctx.lineTo(cx + head_r * 1.05, cy + head_r * 0.5);
        ctx.lineTo(cx - head_r * 1.05, cy + head_r * 0.5);
        ctx.closePath();
        ctx.fill();
        break;
    }
  }

  function drawMouth(ctx, cx, head_cy, head_r, mouthStyle) {
    ctx.strokeStyle = "#3a1810";
    ctx.lineWidth = 0.9;
    const my = head_cy + head_r * 0.42;
    ctx.beginPath();
    if (mouthStyle === "smile") ctx.arc(cx, my - 1, 2, 0.1 * Math.PI, 0.9 * Math.PI);
    else if (mouthStyle === "smirk") {
      ctx.moveTo(cx - 1.5, my);
      ctx.quadraticCurveTo(cx, my - 1, cx + 2, my - 0.6);
    } else {
      ctx.moveTo(cx - 1.7, my);
      ctx.lineTo(cx + 1.7, my);
    }
    ctx.stroke();
  }

  function drawWaggisWig(ctx, cx, head_cy, head_r) {
    const strands = 28;
    const baseY = head_cy - head_r * 0.55;
    for (let i = 0; i < strands; i++) {
      const t = i / (strands - 1);
      const ang = Math.PI * 0.15 + t * Math.PI * 0.7;
      const len = head_r * (1.1 + (i % 3) * 0.12);
      const sx = cx + Math.cos(ang - Math.PI / 2) * head_r * 0.55;
      const sy = baseY;
      const ex = sx + Math.cos(ang) * len * 0.35;
      const ey = sy - Math.sin(ang) * len;
      ctx.strokeStyle = i % 2 === 0 ? "#d50000" : "#ff1744";
      ctx.lineWidth = 1.1 + (i % 2) * 0.3;
      ctx.beginPath();
      ctx.moveTo(sx, sy);
      ctx.quadraticCurveTo(sx + (ex - sx) * 0.4, sy - len * 0.55, ex, ey);
      ctx.stroke();
    }
    ctx.fillStyle = "#c62828";
    ctx.beginPath();
    ctx.ellipse(cx, baseY + head_r * 0.08, head_r * 0.95, head_r * 0.35, 0, 0, Math.PI * 2);
    ctx.fill();
  }

  function drawWaggisFace(ctx, cx, head_cy, head_r) {
    ctx.fillStyle = "#f3f0e8";
    ctx.beginPath();
    ctx.ellipse(cx, head_cy + head_r * 0.05, head_r * 1.05, head_r * 1.0, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = "rgba(40,30,20,0.45)";
    ctx.lineWidth = 0.9;
    ctx.stroke();

    ctx.fillStyle = "#e53935";
    ctx.beginPath();
    ctx.arc(cx, head_cy + head_r * 0.12, head_r * 0.32, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = "#b71c1c";
    ctx.lineWidth = 0.6;
    ctx.stroke();

    const ey = head_cy - head_r * 0.05;
    ctx.fillStyle = "#1a1020";
    ctx.beginPath();
    ctx.ellipse(cx + head_r * 0.38, ey, head_r * 0.14, head_r * 0.2, 0.1, 0, Math.PI * 2);
    ctx.fill();

    const lx = cx - head_r * 0.36;
    ctx.fillStyle = "#ff6f00";
    ctx.beginPath(); ctx.arc(lx, ey, head_r * 0.22, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = "#d32f2f";
    ctx.beginPath(); ctx.arc(lx, ey, head_r * 0.16, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = "#fff";
    ctx.beginPath(); ctx.arc(lx, ey, head_r * 0.1, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = "#1565c0";
    ctx.beginPath(); ctx.arc(lx, ey, head_r * 0.06, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = "#1a1a1a";
    ctx.beginPath(); ctx.arc(lx, ey, head_r * 0.03, 0, Math.PI * 2); ctx.fill();

    const my = head_cy + head_r * 0.48;
    const mw = head_r * 0.72;
    ctx.fillStyle = "#4a148c";
    ctx.beginPath();
    ctx.ellipse(cx, my, mw * 0.55, head_r * 0.22, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "#fff";
    const tw = mw * 0.9;
    const th = head_r * 0.14;
    ctx.fillRect(cx - tw / 2, my - th * 0.35, tw, th);
    ctx.strokeStyle = "#2a1030";
    ctx.lineWidth = 0.5;
    for (let i = -2; i <= 2; i++) {
      ctx.beginPath();
      ctx.moveTo(cx + i * (tw / 5), my - th * 0.35);
      ctx.lineTo(cx + i * (tw / 5), my + th * 0.65);
      ctx.stroke();
    }
    ctx.beginPath();
    ctx.moveTo(cx - tw / 2, my + th * 0.15);
    ctx.lineTo(cx + tw / 2, my + th * 0.15);
    ctx.stroke();
    ctx.strokeStyle = "#1a1020";
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    ctx.arc(cx, my - head_r * 0.02, mw * 0.58, 0.12 * Math.PI, 0.88 * Math.PI);
    ctx.stroke();
  }

  function drawLarveHood(ctx, cx, head_cy, head_r, accent) {
    ctx.fillStyle = accent;
    ctx.beginPath();
    ctx.moveTo(cx - head_r * 1.15, head_cy + head_r * 0.3);
    ctx.lineTo(cx, head_cy - head_r * 1.35);
    ctx.lineTo(cx + head_r * 1.15, head_cy + head_r * 0.3);
    ctx.closePath();
    ctx.fill();
    ctx.strokeStyle = "rgba(0,0,0,0.35)";
    ctx.lineWidth = 0.6;
    ctx.stroke();
  }

  function drawLarveEyes(ctx, cx, head_cy, head_r, style) {
    const ey = head_cy - head_r * 0.08;
    if (style === "slit") {
      ctx.fillStyle = "#1a1a1a";
      ctx.fillRect(cx - head_r * 0.55, ey - 0.8, head_r * 0.35, 1.6);
      ctx.fillRect(cx + head_r * 0.2, ey - 0.8, head_r * 0.35, 1.6);
      return;
    }
    if (style === "squint") {
      ctx.strokeStyle = "#1a1a1a"; ctx.lineWidth = 1.2;
      ctx.beginPath(); ctx.arc(cx - head_r * 0.42, ey, 1.8, 0.15 * Math.PI, 0.85 * Math.PI); ctx.stroke();
      ctx.beginPath(); ctx.arc(cx + head_r * 0.42, ey, 1.8, 0.15 * Math.PI, 0.85 * Math.PI); ctx.stroke();
      return;
    }
    if (style === "wide") {
      ctx.fillStyle = "#fff";
      ctx.beginPath(); ctx.ellipse(cx - head_r * 0.38, ey, 2.8, 3.4, 0, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.ellipse(cx + head_r * 0.38, ey, 2.8, 3.4, 0, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = "#1a1a1a"; ctx.lineWidth = 1.2;
      ctx.beginPath(); ctx.arc(cx - head_r * 0.38, ey, 2.8, 0, Math.PI * 2); ctx.stroke();
      ctx.beginPath(); ctx.arc(cx + head_r * 0.38, ey, 2.8, 0, Math.PI * 2); ctx.stroke();
      ctx.fillStyle = "#1a1a1a";
      ctx.beginPath(); ctx.arc(cx - head_r * 0.38, ey, 1.2, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.arc(cx + head_r * 0.38, ey, 1.2, 0, Math.PI * 2); ctx.fill();
      return;
    }
    ctx.fillStyle = "#1a1a1a";
    ctx.beginPath(); ctx.arc(cx - head_r * 0.4, ey, 1.1, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.arc(cx + head_r * 0.4, ey, 1.1, 0, Math.PI * 2); ctx.fill();
  }

  function drawLarve(ctx, cx, head_cy, head_r, app, isGK) {
    const type = app.larve || "waggis";
    const accent = app.accent || "#c62828";

    if (type === "waggis") {
      drawWaggisWig(ctx, cx, head_cy, head_r);
      drawWaggisFace(ctx, cx, head_cy, head_r);
      return;
    }

    if (type !== "vogel_gryff") drawLarveHood(ctx, cx, head_cy, head_r, isGK ? "#ffd700" : accent);

    let base = "#f4c4a8";
    if (type === "holzlarve") base = "#c9a86c";
    else if (type === "vogel_gryff") base = "#ffd54f";
    else if (type === "alti_dante") base = "#e8c9a0";

    ctx.fillStyle = base;
    ctx.beginPath();
    ctx.arc(cx, head_cy, head_r * 1.02, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = "rgba(0,0,0,0.35)";
    ctx.lineWidth = 0.8;
    ctx.stroke();

    if (type === "alti_dante") {
      ctx.strokeStyle = "rgba(90,60,40,0.5)"; ctx.lineWidth = 0.6;
      for (const off of [-0.3, 0, 0.25]) {
        ctx.beginPath();
        ctx.moveTo(cx - head_r * 0.5, head_cy + head_r * off);
        ctx.quadraticCurveTo(cx, head_cy + head_r * (off + 0.15), cx + head_r * 0.5, head_cy + head_r * off);
        ctx.stroke();
      }
      ctx.fillStyle = "#eceff1";
      ctx.fillRect(cx - head_r * 0.75, head_cy - head_r * 0.55, head_r * 0.35, head_r * 0.22);
      ctx.fillRect(cx + head_r * 0.4, head_cy - head_r * 0.55, head_r * 0.35, head_r * 0.22);
      drawLarveEyes(ctx, cx, head_cy, head_r, "normal");
      ctx.fillStyle = "#bcaaa4";
      ctx.beginPath(); ctx.ellipse(cx, head_cy + head_r * 0.25, head_r * 0.18, head_r * 0.28, 0, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = "#3a1810"; ctx.lineWidth = 0.8;
      ctx.beginPath(); ctx.moveTo(cx - head_r * 0.2, head_cy + head_r * 0.48); ctx.lineTo(cx + head_r * 0.2, head_cy + head_r * 0.48); ctx.stroke();
      return;
    }

    if (type === "vogel_gryff") {
      ctx.fillStyle = "#c62828";
      ctx.beginPath();
      ctx.moveTo(cx, head_cy - head_r * 1.2);
      ctx.lineTo(cx - head_r * 0.35, head_cy - head_r * 0.55);
      ctx.lineTo(cx + head_r * 0.35, head_cy - head_r * 0.55);
      ctx.closePath();
      ctx.fill();
      drawLarveEyes(ctx, cx, head_cy, head_r, "slit");
      ctx.fillStyle = "#e65100";
      ctx.beginPath();
      ctx.moveTo(cx, head_cy + head_r * 0.05);
      ctx.lineTo(cx - head_r * 0.12, head_cy + head_r * 0.45);
      ctx.lineTo(cx + head_r * 0.12, head_cy + head_r * 0.45);
      ctx.closePath();
      ctx.fill();
      return;
    }

    if (type === "fratze") {
      drawLarveEyes(ctx, cx, head_cy, head_r, "wide");
      ctx.fillStyle = "#1a1a1a";
      ctx.beginPath(); ctx.ellipse(cx, head_cy + head_r * 0.45, head_r * 0.22, head_r * 0.3, 0, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = "#5d4037"; ctx.lineWidth = 1.2;
      ctx.beginPath();
      ctx.moveTo(cx - head_r * 0.55, head_cy - head_r * 0.35);
      ctx.quadraticCurveTo(cx - head_r * 0.2, head_cy - head_r * 0.55, cx + head_r * 0.05, head_cy - head_r * 0.4);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(cx + head_r * 0.55, head_cy - head_r * 0.35);
      ctx.quadraticCurveTo(cx + head_r * 0.2, head_cy - head_r * 0.55, cx - head_r * 0.05, head_cy - head_r * 0.4);
      ctx.stroke();
      return;
    }

    if (type === "holzlarve") {
      drawLarveEyes(ctx, cx, head_cy, head_r, "slit");
      ctx.fillStyle = "rgba(60,40,20,0.25)";
      ctx.fillRect(cx - head_r * 0.15, head_cy + head_r * 0.05, head_r * 0.3, head_r * 0.35);
      ctx.strokeStyle = "#4e342e"; ctx.lineWidth = 0.7;
      ctx.beginPath();
      ctx.moveTo(cx, head_cy - head_r * 0.2);
      ctx.lineTo(cx, head_cy + head_r * 0.55);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(cx - head_r * 0.25, head_cy + head_r * 0.52);
      ctx.quadraticCurveTo(cx, head_cy + head_r * 0.62, cx + head_r * 0.25, head_cy + head_r * 0.52);
      ctx.stroke();
    }
  }

  function drawAvatar(ctx, cx, cy, teamColor, role, appearance, active, playerRadius) {
    const R = playerRadius || 14;
    const isGK = role === "Goalkeeper";
    const r = isGK ? R + 2 : R;
    const app = appearance || { mode: "cartoon" };

    if (!active) {
      ctx.globalAlpha = 0.32;
      ctx.fillStyle = teamColor;
      ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = "rgba(255,255,255,0.7)"; ctx.lineWidth = 1.5;
      ctx.setLineDash([4, 4]); ctx.stroke(); ctx.setLineDash([]);
      ctx.globalAlpha = 1;
      ctx.fillStyle = "rgba(255,255,255,0.55)";
      ctx.font = "bold 9px 'Inter', sans-serif"; ctx.textAlign = "center";
      ctx.fillText(isGK ? "GK" : role.slice(0, 3).toUpperCase(), cx, cy + 3);
      return;
    }

    ctx.globalAlpha = 0.22;
    ctx.fillStyle = teamColor;
    ctx.beginPath(); ctx.arc(cx, cy, r + 5, 0, Math.PI * 2); ctx.fill();
    ctx.globalAlpha = 1;

    const jerseyColor = isGK ? "#ffd54f" : teamColor;
    ctx.fillStyle = jerseyColor;
    ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = "rgba(0,0,0,0.55)"; ctx.lineWidth = 1; ctx.stroke();

    const head_r = r * 0.62;
    const head_cy = cy - r * 0.18;

    if (app.mode === "larve") {
      drawLarve(ctx, cx, head_cy, head_r, app, isGK);
    } else {
      ctx.fillStyle = app.skin;
      ctx.beginPath(); ctx.arc(cx, head_cy, head_r, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = "rgba(0,0,0,0.3)"; ctx.lineWidth = 0.6; ctx.stroke();
      drawHair(ctx, cx, head_cy, head_r, app);
      ctx.fillStyle = "#1a1a1a";
      ctx.beginPath(); ctx.arc(cx - head_r * 0.42, head_cy - head_r * 0.1, 0.95, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.arc(cx + head_r * 0.42, head_cy - head_r * 0.1, 0.95, 0, Math.PI * 2); ctx.fill();
      drawMouth(ctx, cx, head_cy, head_r, app.mouth);
    }

    const num = ROLE_NUMBERS[role];
    if (num != null) {
      ctx.fillStyle = isGK ? "#1a1a1a" : "rgba(255,255,255,0.95)";
      ctx.font = "bold 7px 'Inter', sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(String(num), cx, cy + r * 0.78);
    }

    if (isGK) {
      ctx.strokeStyle = teamColor; ctx.lineWidth = 2.6;
      ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.stroke();
    }
  }

  global.FootballAvatars = {
    generateAppearance,
    drawAvatar,
    ROLE_NUMBERS,
    LARVE_TYPES,
  };
})(typeof window !== "undefined" ? window : global);
