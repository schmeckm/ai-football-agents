import streamlit as st
import streamlit.components.v1 as components
import time
import json
import re
from openai import OpenAI
 
# =====================================================================
# 1. API-KONFIGURATION
# =====================================================================
NVIDIA_API_KEY = st.secrets["NVIDIA_API_KEY"]
 
ai_client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY,
    timeout=8.0,  # SPEED: harter Timeout verhindert hängende Calls
)
 
st.set_page_config(layout="wide", page_title="MAKE Football Team - AI Match", page_icon="⚽")
 
# =====================================================================
# 2. CSS – geputzt, ohne invalide :contains-Selektoren
# =====================================================================
st.markdown("""
<style>
.stApp {
    background-color: #0b0c10 !important;
    color: #f5f5f7 !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}
h1, h2, h3, h4, h5, h6 {
    color: #ffffff !important;
    font-weight: 800 !important;
    letter-spacing: -0.7px;
}
div[data-testid="column"] {
    background-color: #12131a;
    padding: 20px !important;
    border-radius: 12px;
    border: 1px solid #1f222e;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    margin-bottom: 20px;
}
.stSelectbox div[data-baseweb="select"] {
    background-color: #1a1c23 !important;
    color: #ffffff !important;
    border: 1px solid #2f3346 !important;
    border-radius: 8px !important;
}
.stTextArea textarea {
    background-color: #090a0f !important;
    color: #e4e6eb !important;
    border: 1px solid #2f3346 !important;
    border-radius: 6px !important;
    font-size: 13.5px !important;
    padding: 10px !important;
    transition: all 0.25s ease;
}
.stTextArea textarea:focus {
    border-color: #00e676 !important;
    box-shadow: 0 0 8px rgba(0, 230, 118, 0.2) !important;
}
label[data-testid="stWidgetLabel"] {
    color: #8a90a6 !important;
    font-weight: 600 !important;
    font-size: 13.5px !important;
    margin-bottom: 4px !important;
}
 
/* Expander komplett dunkel */
div[data-testid="stExpander"] {
    background-color: #12131a !important;
    border: 1px solid #252836 !important;
    border-radius: 8px !important;
    margin-bottom: 10px !important;
    overflow: hidden !important;
}
div[data-testid="stExpander"] details summary {
    background-color: #1a1c23 !important;
    color: #ffffff !important;
    border-bottom: 1px solid #252836 !important;
    padding: 12px 15px !important;
}
div[data-testid="stExpander"] details summary:focus,
div[data-testid="stExpander"] details summary:active {
    background-color: #1a1c23 !important;
    color: #00e676 !important;
    outline: none !important;
}
div[data-testid="stExpander"] details summary span { color: #ffffff !important; font-weight: 700 !important; }
div[data-testid="stExpander"] details summary:hover span { color: #00e676 !important; }
div[data-testid="stExpander"] [role="transition-container"] {
    background-color: #12131a !important;
    padding: 15px !important;
}
div[data-testid="stExpander"] svg { fill: #00e676 !important; color: #00e676 !important; }
 
/* Tabs */
button[data-baseweb="tab"] {
    color: #8a90a6 !important;
    font-size: 14.5px !important;
    font-weight: 800 !important;
    padding: 12px 18px !important;
    background-color: transparent !important;
    border: none !important;
    transition: all 0.25s ease;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #00e676 !important;
    border-bottom: 3px solid #00e676 !important;
}
 
/* Standard-Buttons (secondary) */
div.stButton > button[kind="secondary"], div.stButton > button:not([kind]) {
    background: linear-gradient(135deg, #16171e 0%, #1d1f2a 100%) !important;
    color: #ffffff !important;
    border: 1px solid #3a3f58 !important;
    border-radius: 8px !important;
    padding: 12px 24px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    width: 100%;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
div.stButton > button[kind="secondary"]:hover, div.stButton > button:not([kind]):hover {
    border-color: #00e676 !important;
    color: #00e676 !important;
    box-shadow: 0 0 20px rgba(0, 230, 118, 0.3) !important;
    transform: translateY(-1.5px);
}
 
/* Primary = Stop-Button (rot) – ersetzt den kaputten :contains-Hack */
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2a0d12 0%, #3a1218 100%) !important;
    color: #ff5a6c !important;
    border: 1px solid #ff1744 !important;
    border-radius: 8px !important;
    padding: 12px 24px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    width: 100%;
    transition: all 0.2s ease !important;
}
div.stButton > button[kind="primary"]:hover {
    color: #ff1744 !important;
    box-shadow: 0 0 20px rgba(255, 23, 68, 0.35) !important;
    transform: translateY(-1.5px);
}
 
div[data-testid="stCodeBlock"] {
    background-color: #07080a !important;
    border: 1px solid #1a1c23 !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)
 
# =====================================================================
# 3. ÜBERSETZUNGEN
# =====================================================================
TRANSLATIONS = {
    "English": {
        "panel_title": "MAKE Football Team - Control Panel",
        "btn_stop": "⏹️ STOP MATCH", "btn_start": "▶️ START MATCH",
        "prompt_hdr": "Live Prompt Engineering",
        "prompt_cap": "Changes here affect players live on the next LLM tick.",
        "btn_reset": "🔄 RESET BALL TO CENTER",
        "debug_hdr": "Debug Console (Single-Query JSON)",
        "sim_title": "MAKE Live Simulation",
        "time": "Time", "live": "Live Match",
        "score_red": "MAKE RED", "score_blue": "MAKE BLUE",
        "strat_hdr": "Live Synced Strategies (All Players)"
    },
    "Deutsch": {
        "panel_title": "MAKE Football Team - Kontrollzentrum",
        "btn_stop": "⏹️ SPIEL STOPPEN", "btn_start": "▶️ SPIEL STARTEN",
        "prompt_hdr": "Live Prompt Engineering",
        "prompt_cap": "Änderungen wirken beim nächsten LLM-Tick auf die Spieler.",
        "btn_reset": "🔄 BALL ZURÜCKSETZEN",
        "debug_hdr": "Debug-Konsole (Sammel-Abfrage JSON)",
        "sim_title": "MAKE Live Simulation",
        "time": "Zeit", "live": "Live-Match",
        "score_red": "MAKE ROT", "score_blue": "MAKE BLAU",
        "strat_hdr": "Aktive Strategien aller Spieler"
    },
    "Français": {
        "panel_title": "MAKE Football Team - Panneau de Contrôle",
        "btn_stop": "⏹️ ARRÊTER LE MATCH", "btn_start": "▶️ DÉMARRER LE MATCH",
        "prompt_hdr": "Ingénierie des Prompts en Direct",
        "prompt_cap": "Les modifications s'appliquent au prochain tick du LLM.",
        "btn_reset": "🔄 RÉINITIALISER LE BALLON",
        "debug_hdr": "Console de Débogage (Sortie JSON unique)",
        "sim_title": "Simulation en Direct MAKE",
        "time": "Temps", "live": "Match en Direct",
        "score_red": "MAKE ROUGE", "score_blue": "MAKE BLEU",
        "strat_hdr": "Stratégies actives des joueurs"
    },
    "Español": {
        "panel_title": "MAKE Football Team - Panel de Control",
        "btn_stop": "⏹️ DETENER PARTIDO", "btn_start": "▶️ INICIAR PARTIDO",
        "prompt_hdr": "Ingeniería de Prompts en Vivo",
        "prompt_cap": "Los cambios se aplican en el próximo tick del LLM.",
        "btn_reset": "🔄 REINICIAR BALÓN",
        "debug_hdr": "Consola de Depuración (Consulta Única JSON)",
        "sim_title": "Simulación en Vivo MAKE",
        "time": "Tiempo", "live": "Partido en Vivo",
        "score_red": "MAKE ROJO", "score_blue": "MAKE AZUL",
        "strat_hdr": "Estrategias activas de jugadores"
    },
    "Polski": {
        "panel_title": "MAKE Football Team - Panel Sterowania",
        "btn_stop": "⏹️ ZATRZYMAJ MECZ", "btn_start": "▶️ URUCHOM MECZ",
        "prompt_hdr": "Inżynieria Promptów na Żywo",
        "prompt_cap": "Zmiany zostaną zastosowane przy następnym tickcie LLM.",
        "btn_reset": "🔄 RESETUJ PIŁKĘ",
        "debug_hdr": "Konsola Debugowania (Zbiór danych JSON)",
        "sim_title": "Symulacja na Żywo MAKE",
        "time": "Czas", "live": "Mecz na Żywo",
        "score_red": "MAKE CZERWONI", "score_blue": "MAKE NIEBIESCY",
        "strat_hdr": "Aktywne strategie graczy"
    }
}
 
if "ui_lang" not in st.session_state:
    st.session_state.ui_lang = "English"
 
# =====================================================================
# 4. SHARED MATCH STATE
# =====================================================================
@st.cache_resource
def get_shared_match():
    return {
        "time_left": 90.0,
        "score": {"Red": 0, "Blue": 0},
        "autoplay": False,
        "last_tick": 0.0,
        "last_llm_call": 0.0,
        "api_error": None,
        "ball": {"x": 300, "y": 200, "vx": 0, "vy": 0},
        "ball_trail": [],  # FORMAT: visueller Speed-Trail
        "players": {
            "red_striker":    {"team": "Red",  "role": "Striker",    "x": 200, "y": 150, "prompt": "You are the Red Striker. Sprint to the ball and shoot right into the blue goal!", "dx": 0.0, "dy": 0.0, "kick": False},
            "red_midfielder": {"team": "Red",  "role": "Midfielder", "x": 180, "y": 250, "prompt": "You are the Red Midfielder. Distribute the ball to strikers and support from behind.", "dx": 0.0, "dy": 0.0, "kick": False},
            "red_winger":     {"team": "Red",  "role": "Winger",     "x": 150, "y":  80, "prompt": "You are the Red Winger. Run along the upper wing and cross the ball forward.", "dx": 0.0, "dy": 0.0, "kick": False},
            "red_defender":   {"team": "Red",  "role": "Defender",   "x": 100, "y": 200, "prompt": "You are the Red Defender. Stay on your half and clear the ball away from the red goal.", "dx": 0.0, "dy": 0.0, "kick": False},
            "blue_striker":   {"team": "Blue", "role": "Striker",    "x": 400, "y": 250, "prompt": "You are the Blue Striker. Chase the ball and shoot left into the red goal!", "dx": 0.0, "dy": 0.0, "kick": False},
            "blue_midfielder":{"team": "Blue", "role": "Midfielder", "x": 420, "y": 150, "prompt": "You are the Blue Midfielder. Stop red attacks and pass the ball to blue strikers.", "dx": 0.0, "dy": 0.0, "kick": False},
            "blue_winger":    {"team": "Blue", "role": "Winger",     "x": 450, "y": 320, "prompt": "You are the Blue Winger. Intercept red passes along the lower wing.", "dx": 0.0, "dy": 0.0, "kick": False},
            "blue_defender":  {"team": "Blue", "role": "Defender",   "x": 500, "y": 200, "prompt": "You are the Blue Defender. Guard the right goal area and block red strikers.", "dx": 0.0, "dy": 0.0, "kick": False},
        },
        "last_llm_response": "{}"
    }
 
shared_state = get_shared_match()
lang = TRANSLATIONS[st.session_state.ui_lang]
 
# =====================================================================
# 5. KI – SPEED-OPTIMIERT
#    - Kürzere System-Message
#    - Kompakte Position-Repräsentation
#    - JSON-Keys auf 1 Zeichen reduziert (x/y/k)
#    - max_tokens halbiert (400 -> 220)
#    - Throttle 1.2 s (statt 1.5 s) -> ~50 req/min, weiter unter Limit
# =====================================================================
def fetch_all_agent_moves(current_state):
    strategies = "\n".join(
        f"{name}({p['team']}): {p['prompt']}"
        for name, p in current_state["players"].items()
    )
    ball = current_state["ball"]
    positions = " | ".join(
        f"{n}={int(p['x'])},{int(p['y'])}"
        for n, p in current_state["players"].items()
    )
 
    system = (
        "You control 8 football players. Return ONLY one JSON object, no prose.\n"
        "Schema: {\"player_name\":{\"x\":<dx -5..5>,\"y\":<dy -5..5>,\"k\":<bool>}}\n"
        "Field 600x400. Red attacks RIGHT goal (x=600). Blue attacks LEFT goal (x=0).\n"
        "Strategies:\n" + strategies
    )
    user = f"Ball={int(ball['x'])},{int(ball['y'])} | {positions}\nReturn moves now."
 
    try:
        response = ai_client.chat.completions.create(
            model="meta/llama-3.1-8b-instruct",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
            max_tokens=220,
        )
        raw = response.choices[0].message.content.strip()
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if not match:
            raise ValueError(f"No JSON in: {raw[:140]}")
        parsed = json.loads(match.group(0))
        shared_state["api_error"] = None
        return parsed
    except Exception as e:
        shared_state["api_error"] = str(e)[:160]
        return {n: {"x": 0, "y": 0, "k": False} for n in current_state["players"].keys()}
 
# =====================================================================
# 6. GAME TICK – 100 ms statt 150 ms = smoother
# =====================================================================
LLM_THROTTLE = 1.2     # Sekunden zwischen LLM-Calls
TICK_INTERVAL = 0.10   # Sekunden zwischen Physik-Ticks
 
def run_game_tick():
    now = time.time()
 
    # LLM nur alle LLM_THROTTLE Sekunden -> bleibt unter Rate-Limit
    if now - shared_state["last_llm_call"] > LLM_THROTTLE:
        shared_state["last_llm_call"] = now
        moves = fetch_all_agent_moves(shared_state)
        shared_state["last_llm_response"] = json.dumps(moves, indent=2)
        for name, p in shared_state["players"].items():
            mv = moves.get(name, {})
            p["dx"]   = float(mv.get("x", mv.get("dx", 0.0)))
            p["dy"]   = float(mv.get("y", mv.get("dy", 0.0)))
            p["kick"] = bool(mv.get("k", mv.get("kick", False)))
 
    # Physik – läuft jeden Tick, nutzt zwischengespeicherte dx/dy
    for p in shared_state["players"].values():
        p["x"] = max(20, min(580, p["x"] + p["dx"]))
        p["y"] = max(20, min(380, p["y"] + p["dy"]))
 
        dx = p["x"] - shared_state["ball"]["x"]
        dy = p["y"] - shared_state["ball"]["y"]
        dist2 = dx*dx + dy*dy
        if dist2 < 625 and p["kick"]:  # 25^2
            direction = 12 if p["team"] == "Red" else -12
            shared_state["ball"]["vx"] = direction
            shared_state["ball"]["vy"] = (shared_state["ball"]["y"] - p["y"]) * 0.35
 
    # Ball-Bewegung + Reibung
    b = shared_state["ball"]
    b["x"] += b["vx"]
    b["y"] += b["vy"]
    b["vx"] *= 0.88
    b["vy"] *= 0.88
 
    # Trail aufzeichnen (Format: visueller Speed-Indikator)
    shared_state["ball_trail"].append([round(b["x"], 1), round(b["y"], 1)])
    if len(shared_state["ball_trail"]) > 12:
        shared_state["ball_trail"].pop(0)
 
    # Tor-Check + Bandenabprall (verhindert Ball-Stuck am Rand)
    if b["x"] > 580 and 120 < b["y"] < 280:
        shared_state["score"]["Red"] += 1
        reset_ball()
    elif b["x"] < 20 and 120 < b["y"] < 280:
        shared_state["score"]["Blue"] += 1
        reset_ball()
    else:
        if b["x"] < 8 or b["x"] > 592:
            b["vx"] *= -0.5
            b["x"] = max(8, min(592, b["x"]))
        if b["y"] < 8 or b["y"] > 392:
            b["vy"] *= -0.5
            b["y"] = max(8, min(392, b["y"]))
 
    shared_state["time_left"] = max(0.0, shared_state["time_left"] - TICK_INTERVAL)
 
def reset_ball():
    shared_state["ball"] = {"x": 300, "y": 200, "vx": 0, "vy": 0}
    shared_state["ball_trail"] = []
 
# =====================================================================
# 7. PITCH-RENDERER (HTML/Canvas)
# =====================================================================
def generate_pitch_html(state, t):
    players_json = json.dumps(state["players"])
    ball_json    = json.dumps(state["ball"])
    trail_json   = json.dumps(state["ball_trail"])
    score_text   = f"{t['score_red']}: {state['score']['Red']}  |  {t['score_blue']}: {state['score']['Blue']}"
 
    return f"""<!DOCTYPE html>
<html><head><style>
body {{ margin:0; padding:0; overflow:hidden; background-color:#0b0c10; }}
.container {{
  background:#111215; padding:12px; border-radius:10px;
  color:white; font-family:'Inter',sans-serif; box-sizing:border-box;
}}
</style></head><body>
<div class="container">
  <div style="display:flex;justify-content:space-between;margin-bottom:8px;font-weight:bold;font-size:15px;">
    <span>⏱️ {t['time']}: {state['time_left']:.1f}s</span>
    <span style="color:#00e676;font-size:17px;font-family:monospace;letter-spacing:1px;">{score_text}</span>
    <span style="color:#ff9100;">{t['live']}</span>
  </div>
  <canvas id="field" width="600" height="400"
    style="background:#235e29;border:3px solid #fff;border-radius:6px;width:100%;height:auto;display:block;"></canvas>
</div>
<script>
const canvas = document.getElementById('field');
const ctx = canvas.getContext('2d');
const players = {players_json};
const ball    = {ball_json};
const trail   = {trail_json};
 
// Mittellinie + Mittelkreis
ctx.strokeStyle = "rgba(255,255,255,0.8)"; ctx.lineWidth = 2.5;
ctx.beginPath(); ctx.moveTo(300, 0); ctx.lineTo(300, 400); ctx.stroke();
ctx.beginPath(); ctx.arc(300, 200, 50, 0, 2*Math.PI); ctx.stroke();
// Strafraum
ctx.strokeRect(0, 100, 60, 200); ctx.strokeRect(540, 100, 60, 200);
// Tor-Visualisierung
ctx.fillStyle = "rgba(255,255,255,0.18)";
ctx.fillRect(0, 120, 10, 160); ctx.fillRect(590, 120, 10, 160);
 
// Watermark
ctx.fillStyle = "rgba(255,255,255,0.15)";
ctx.font = "bold 24px 'Impact',sans-serif"; ctx.textAlign = "center";
ctx.fillText("MAKE FOOTBALL TEAM", 300, 210);
 
// Ball-Trail (Speed-Indikator)
for (let i = 0; i < trail.length; i++) {{
  const alpha = (i + 1) / trail.length * 0.5;
  ctx.beginPath();
  ctx.arc(trail[i][0], trail[i][1], 3 + i * 0.3, 0, 2*Math.PI);
  ctx.fillStyle = `rgba(255,255,255,${{alpha}})`;
  ctx.fill();
}}
 
// Ball
ctx.beginPath(); ctx.arc(ball.x, ball.y, 7, 0, 2*Math.PI);
ctx.fillStyle = "#ffffff"; ctx.fill();
ctx.strokeStyle = "#000"; ctx.lineWidth = 1.5; ctx.stroke();
 
// Spieler
for (let name in players) {{
  const p = players[name];
  ctx.beginPath(); ctx.arc(p.x, p.y, 12, 0, 2*Math.PI);
  ctx.fillStyle = p.team === "Red" ? "#ff1744" : "#00b0ff";
  ctx.fill();
  ctx.strokeStyle = "#ffffff"; ctx.lineWidth = 1.5; ctx.stroke();
 
  ctx.fillStyle = "rgba(255,255,255,0.95)";
  ctx.font = "bold 9px sans-serif"; ctx.textAlign = "center";
  const role = name.split('_')[1].slice(0,2).toUpperCase();
  ctx.fillText(role, p.x, p.y + 3);
}}
</script></body></html>"""
 
# =====================================================================
# 8. STREAMLIT LAYOUT
# =====================================================================
col_left, col_right = st.columns([1, 1.25])
 
with col_left:
    st.session_state.ui_lang = st.selectbox(
        "🌐 Interface Language / Langue / Sprache",
        ["English", "Deutsch", "Français", "Español", "Polski"]
    )
    lang = TRANSLATIONS[st.session_state.ui_lang]
 
    st.title(lang["panel_title"])
 
    if shared_state.get("api_error"):
        st.error(f"⚠️ API Error: {shared_state['api_error']}")
        st.info("💡 Check your NVIDIA API Key in Streamlit Cloud Secrets.")
 
    # Stop = primary (rot), Start = secondary – ersetzt :contains-Hack
    btn_type  = "primary" if shared_state["autoplay"] else "secondary"
    btn_label = lang["btn_stop"] if shared_state["autoplay"] else lang["btn_start"]
    if st.button(btn_label, use_container_width=True, type=btn_type):
        shared_state["autoplay"] = not shared_state["autoplay"]
        st.rerun()
 
    st.subheader(lang["prompt_hdr"])
    st.caption(lang["prompt_cap"])
 
    tab_red, tab_blue = st.tabs(["🔴 MAKE RED Team", "🔵 MAKE BLUE Team"])
 
    with tab_red:
        for name, p in shared_state["players"].items():
            if p["team"] == "Red":
                role_display = name.split('_')[1].upper()
                with st.expander(f"🔴 RED {role_display} - Prompt", expanded=(role_display == "STRIKER")):
                    shared_state["players"][name]["prompt"] = st.text_area(
                        "Prompt String:", value=p["prompt"],
                        key=f"input_{name}", height=70, label_visibility="collapsed"
                    )
 
    with tab_blue:
        for name, p in shared_state["players"].items():
            if p["team"] == "Blue":
                role_display = name.split('_')[1].upper()
                with st.expander(f"🔵 BLUE {role_display} - Prompt", expanded=(role_display == "STRIKER")):
                    shared_state["players"][name]["prompt"] = st.text_area(
                        "Prompt String:", value=p["prompt"],
                        key=f"input_{name}", height=70, label_visibility="collapsed"
                    )
 
    if st.button(lang["btn_reset"], use_container_width=True):
        reset_ball()
        st.rerun()
 
    with st.expander("📋 " + lang["strat_hdr"], expanded=False):
        st.json({
            name.upper(): {
                "Team": "🔴 RED (MAKE)" if data["team"] == "Red" else "🔵 BLUE (MAKE)",
                "Role": data["role"].upper(),
                "Strategy": data["prompt"],
            }
            for name, data in shared_state["players"].items()
        })
 
    st.subheader(lang["debug_hdr"])
    st.code(shared_state["last_llm_response"], language="json")
 
with col_right:
    st.title(lang["sim_title"])
    html_pitch = generate_pitch_html(shared_state, lang)
    # FIX: st.iframe existiert nicht in Streamlit -> components.html
    components.html(html_pitch, height=485, scrolling=False)
 
# =====================================================================
# 9. SERVER GAME LOOP
# =====================================================================
if shared_state["autoplay"] and shared_state["time_left"] > 0:
    now = time.time()
    if now - shared_state["last_tick"] > TICK_INTERVAL:
        shared_state["last_tick"] = now
        run_game_tick()
    time.sleep(0.04)  # SPEED: kürzerer Sleep -> snappere rerun-Loop
    st.rerun()
elif not shared_state["autoplay"]:
    time.sleep(1.0)
    st.rerun()
