import streamlit as st
import streamlit.components.v1 as components
import time
import json
import re
from openai import OpenAI

# =====================================================================
# 1. API
# =====================================================================
NVIDIA_API_KEY = st.secrets["NVIDIA_API_KEY"]

ai_client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY,
    timeout=8.0,
)

st.set_page_config(layout="wide", page_title="MAKE Football Team - AI Match", page_icon="⚽")

# =====================================================================
# 2. CSS
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
.stSelectbox div[data-baseweb="select"],
.stTextInput input, .stNumberInput input {
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
div[data-testid="stExpander"] details summary span { color: #ffffff !important; font-weight: 700 !important; }
div[data-testid="stExpander"] details summary:hover span { color: #00e676 !important; }
div[data-testid="stExpander"] [role="transition-container"] {
    background-color: #12131a !important;
    padding: 15px !important;
}
div[data-testid="stExpander"] svg { fill: #00e676 !important; color: #00e676 !important; }
button[data-baseweb="tab"] {
    color: #8a90a6 !important;
    font-size: 14.5px !important;
    font-weight: 800 !important;
    padding: 12px 18px !important;
    background-color: transparent !important;
    border: none !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #00e676 !important;
    border-bottom: 3px solid #00e676 !important;
}
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
}
div.stButton > button[kind="secondary"]:hover, div.stButton > button:not([kind]):hover {
    border-color: #00e676 !important;
    color: #00e676 !important;
    box-shadow: 0 0 20px rgba(0, 230, 118, 0.3) !important;
    transform: translateY(-1.5px);
}
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2a0d12 0%, #3a1218 100%) !important;
    color: #ff5a6c !important;
    border: 1px solid #ff1744 !important;
    border-radius: 8px !important;
    padding: 12px 24px !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    width: 100%;
}
div.stButton > button[kind="primary"]:hover {
    color: #ff1744 !important;
    box-shadow: 0 0 20px rgba(255, 23, 68, 0.35) !important;
}
div[data-testid="stCodeBlock"] {
    background-color: #07080a !important;
    border: 1px solid #1a1c23 !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 3. NATIONEN
# =====================================================================
NATIONS = {
    "Argentina":   {"flag": "🇦🇷", "color": "#75aadb"},
    "Austria":     {"flag": "🇦🇹", "color": "#ed2939"},
    "Belgium":     {"flag": "🇧🇪", "color": "#e30613"},
    "Brazil":      {"flag": "🇧🇷", "color": "#ffdf00"},
    "Croatia":     {"flag": "🇭🇷", "color": "#171796"},
    "Denmark":     {"flag": "🇩🇰", "color": "#c8102e"},
    "England":     {"flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "color": "#ffffff"},
    "France":      {"flag": "🇫🇷", "color": "#0055a4"},
    "Germany":     {"flag": "🇩🇪", "color": "#1c1c1c"},
    "Italy":       {"flag": "🇮🇹", "color": "#0066cc"},
    "Japan":       {"flag": "🇯🇵", "color": "#003580"},
    "Mexico":      {"flag": "🇲🇽", "color": "#006847"},
    "Netherlands": {"flag": "🇳🇱", "color": "#ff6c00"},
    "Norway":      {"flag": "🇳🇴", "color": "#ba0c2f"},
    "Poland":      {"flag": "🇵🇱", "color": "#dc143c"},
    "Portugal":    {"flag": "🇵🇹", "color": "#d62828"},
    "Singapore":   {"flag": "🇸🇬", "color": "#ed2939"},
    "South Korea": {"flag": "🇰🇷", "color": "#cd2e3a"},
    "Spain":       {"flag": "🇪🇸", "color": "#aa151b"},
    "Sweden":      {"flag": "🇸🇪", "color": "#fecc00"},
    "Switzerland": {"flag": "🇨🇭", "color": "#ff0000"},
    "USA":         {"flag": "🇺🇸", "color": "#3c3b6e"},
}
NATION_NAMES = list(NATIONS.keys())

# =====================================================================
# 4. ÜBERSETZUNGEN
# =====================================================================
TRANSLATIONS = {
    "English": {
        "panel_title": "MAKE Football Team - Control Panel",
        "btn_stop": "⏹️ STOP MATCH", "btn_start": "▶️ START MATCH",
        "prompt_hdr": "Live Prompt Engineering",
        "prompt_cap": "Changes here affect players live on the next LLM tick.",
        "btn_reset": "🔄 RESET BALL TO CENTER",
        "debug_hdr": "Debug Console",
        "sim_title": "Live Simulation",
        "time": "Time", "live": "Live Match",
        "strat_hdr": "Live Synced Strategies",
        "setup_hdr": "🏆 Match Setup",
        "setup_cap": "Configure teams, nations and match duration. 'Apply' starts a fresh match.",
        "team_a": "Team A (left side, attacks right goal)",
        "team_b": "Team B (right side, attacks left goal)",
        "f_name": "Team name", "f_nation": "Nation", "f_color": "Jersey color",
        "f_duration": "Match duration (seconds)",
        "btn_apply": "✅ APPLY & KICKOFF NEW MATCH",
        "applied": "Match setup applied. Press START MATCH to kickoff.",
    },
    "Deutsch": {
        "panel_title": "MAKE Football Team - Kontrollzentrum",
        "btn_stop": "⏹️ SPIEL STOPPEN", "btn_start": "▶️ SPIEL STARTEN",
        "prompt_hdr": "Live Prompt Engineering",
        "prompt_cap": "Änderungen wirken beim nächsten LLM-Tick auf die Spieler.",
        "btn_reset": "🔄 BALL ZURÜCKSETZEN",
        "debug_hdr": "Debug-Konsole",
        "sim_title": "Live-Simulation",
        "time": "Zeit", "live": "Live-Match",
        "strat_hdr": "Aktive Strategien",
        "setup_hdr": "🏆 Match-Setup",
        "setup_cap": "Teams, Nationen und Spielzeit konfigurieren. 'Übernehmen' startet ein frisches Match.",
        "team_a": "Team A (links, greift rechtes Tor an)",
        "team_b": "Team B (rechts, greift linkes Tor an)",
        "f_name": "Teamname", "f_nation": "Nation", "f_color": "Trikotfarbe",
        "f_duration": "Spielzeit (Sekunden)",
        "btn_apply": "✅ ÜBERNEHMEN & ANSTOSS",
        "applied": "Setup übernommen. SPIEL STARTEN klicken zum Anstoss.",
    },
    "Français": {
        "panel_title": "MAKE Football Team - Panneau de Contrôle",
        "btn_stop": "⏹️ ARRÊTER LE MATCH", "btn_start": "▶️ DÉMARRER LE MATCH",
        "prompt_hdr": "Ingénierie des Prompts en Direct",
        "prompt_cap": "Les modifications s'appliquent au prochain tick du LLM.",
        "btn_reset": "🔄 RÉINITIALISER LE BALLON",
        "debug_hdr": "Console de Débogage",
        "sim_title": "Simulation en Direct",
        "time": "Temps", "live": "Match en Direct",
        "strat_hdr": "Stratégies actives",
        "setup_hdr": "🏆 Configuration du Match",
        "setup_cap": "Configurez équipes, nations et durée. 'Appliquer' démarre un nouveau match.",
        "team_a": "Équipe A (gauche, attaque le but droit)",
        "team_b": "Équipe B (droite, attaque le but gauche)",
        "f_name": "Nom de l'équipe", "f_nation": "Nation", "f_color": "Couleur du maillot",
        "f_duration": "Durée du match (secondes)",
        "btn_apply": "✅ APPLIQUER & COUP D'ENVOI",
        "applied": "Configuration appliquée. Appuyez sur DÉMARRER LE MATCH.",
    },
    "Español": {
        "panel_title": "MAKE Football Team - Panel de Control",
        "btn_stop": "⏹️ DETENER PARTIDO", "btn_start": "▶️ INICIAR PARTIDO",
        "prompt_hdr": "Ingeniería de Prompts en Vivo",
        "prompt_cap": "Los cambios se aplican en el próximo tick del LLM.",
        "btn_reset": "🔄 REINICIAR BALÓN",
        "debug_hdr": "Consola de Depuración",
        "sim_title": "Simulación en Vivo",
        "time": "Tiempo", "live": "Partido en Vivo",
        "strat_hdr": "Estrategias activas",
        "setup_hdr": "🏆 Configuración del Partido",
        "setup_cap": "Configura equipos, naciones y duración. 'Aplicar' inicia un nuevo partido.",
        "team_a": "Equipo A (izquierda, ataca portería derecha)",
        "team_b": "Equipo B (derecha, ataca portería izquierda)",
        "f_name": "Nombre del equipo", "f_nation": "Nación", "f_color": "Color de camiseta",
        "f_duration": "Duración del partido (segundos)",
        "btn_apply": "✅ APLICAR & SAQUE INICIAL",
        "applied": "Configuración aplicada. Pulsa INICIAR PARTIDO.",
    },
    "Polski": {
        "panel_title": "MAKE Football Team - Panel Sterowania",
        "btn_stop": "⏹️ ZATRZYMAJ MECZ", "btn_start": "▶️ URUCHOM MECZ",
        "prompt_hdr": "Inżynieria Promptów na Żywo",
        "prompt_cap": "Zmiany zostaną zastosowane przy następnym ticku LLM.",
        "btn_reset": "🔄 RESETUJ PIŁKĘ",
        "debug_hdr": "Konsola Debugowania",
        "sim_title": "Symulacja na Żywo",
        "time": "Czas", "live": "Mecz na Żywo",
        "strat_hdr": "Aktywne strategie",
        "setup_hdr": "🏆 Ustawienia Meczu",
        "setup_cap": "Skonfiguruj drużyny, narody i czas. 'Zastosuj' uruchamia nowy mecz.",
        "team_a": "Drużyna A (lewa, atakuje prawą bramkę)",
        "team_b": "Drużyna B (prawa, atakuje lewą bramkę)",
        "f_name": "Nazwa drużyny", "f_nation": "Narodowość", "f_color": "Kolor koszulki",
        "f_duration": "Czas meczu (sekundy)",
        "btn_apply": "✅ ZASTOSUJ I ROZPOCZNIJ",
        "applied": "Ustawienia zastosowane. Naciśnij URUCHOM MECZ.",
    }
}

if "ui_lang" not in st.session_state:
    st.session_state.ui_lang = "English"

# =====================================================================
# 5. SPIELER-LAYOUT & PROMPT-GENERATOR
# =====================================================================
INITIAL_POSITIONS = {
    "red_striker":     {"team": "Red",  "role": "Striker",    "x": 200, "y": 150},
    "red_midfielder":  {"team": "Red",  "role": "Midfielder", "x": 180, "y": 250},
    "red_winger":      {"team": "Red",  "role": "Winger",     "x": 150, "y":  80},
    "red_defender":    {"team": "Red",  "role": "Defender",   "x": 100, "y": 200},
    "blue_striker":    {"team": "Blue", "role": "Striker",    "x": 400, "y": 250},
    "blue_midfielder": {"team": "Blue", "role": "Midfielder", "x": 420, "y": 150},
    "blue_winger":     {"team": "Blue", "role": "Winger",     "x": 450, "y": 320},
    "blue_defender":   {"team": "Blue", "role": "Defender",   "x": 500, "y": 200},
}

def make_default_prompts(name_red, name_blue):
    return {
        "red_striker":     f"You are the {name_red} Striker. Sprint to the ball and shoot right into the {name_blue} goal.",
        "red_midfielder":  f"You are the {name_red} Midfielder. Distribute the ball to strikers and support from behind.",
        "red_winger":      f"You are the {name_red} Winger. Run along the upper wing and cross the ball forward.",
        "red_defender":    f"You are the {name_red} Defender. Stay on your half and clear the ball away from the {name_red} goal.",
        "blue_striker":    f"You are the {name_blue} Striker. Chase the ball and shoot left into the {name_red} goal.",
        "blue_midfielder": f"You are the {name_blue} Midfielder. Stop {name_red} attacks and pass the ball to {name_blue} strikers.",
        "blue_winger":     f"You are the {name_blue} Winger. Intercept {name_red} passes along the lower wing.",
        "blue_defender":   f"You are the {name_blue} Defender. Guard the right goal area and block {name_red} strikers.",
    }

def build_players(name_red, name_blue):
    prompts = make_default_prompts(name_red, name_blue)
    return {
        n: {**INITIAL_POSITIONS[n], "prompt": prompts[n], "dx": 0.0, "dy": 0.0, "kick": False}
        for n in INITIAL_POSITIONS
    }

# =====================================================================
# 6. SHARED STATE
# =====================================================================
@st.cache_resource
def get_shared_match():
    name_red, name_blue = "Make Red", "Make Blue"
    return {
        "time_left": 90.0,
        "match_duration": 90.0,
        "score": {"Red": 0, "Blue": 0},
        "autoplay": False,
        "last_tick": 0.0,
        "last_llm_call": 0.0,
        "api_error": None,
        "ball": {"x": 300, "y": 200, "vx": 0, "vy": 0},
        "ball_trail": [],
        "team_red_name":    name_red,
        "team_red_nation":  "Switzerland",
        "team_red_color":   "#ff1744",
        "team_blue_name":   name_blue,
        "team_blue_nation": "Germany",
        "team_blue_color":  "#00b0ff",
        "players": build_players(name_red, name_blue),
        "last_llm_response": "{}",
        "info_message": "",
    }

shared_state = get_shared_match()
lang = TRANSLATIONS[st.session_state.ui_lang]

# =====================================================================
# 7. SETUP ANWENDEN
# =====================================================================
def apply_match_setup(name_red, nation_red, color_red, name_blue, nation_blue, color_blue, duration):
    shared_state["team_red_name"]    = (name_red.strip() or "Team A")
    shared_state["team_red_nation"]  = nation_red
    shared_state["team_red_color"]   = color_red
    shared_state["team_blue_name"]   = (name_blue.strip() or "Team B")
    shared_state["team_blue_nation"] = nation_blue
    shared_state["team_blue_color"]  = color_blue
    shared_state["match_duration"]   = float(duration)
    shared_state["time_left"]        = float(duration)
    shared_state["score"]            = {"Red": 0, "Blue": 0}
    shared_state["autoplay"]         = False
    shared_state["ball"]             = {"x": 300, "y": 200, "vx": 0, "vy": 0}
    shared_state["ball_trail"]       = []
    shared_state["players"]          = build_players(
        shared_state["team_red_name"], shared_state["team_blue_name"]
    )
    shared_state["last_llm_response"] = "{}"
    shared_state["api_error"]         = None
    shared_state["info_message"]      = "applied"

def reset_ball():
    shared_state["ball"] = {"x": 300, "y": 200, "vx": 0, "vy": 0}
    shared_state["ball_trail"] = []

# =====================================================================
# 8. LLM
# =====================================================================
def fetch_all_agent_moves(current_state):
    name_red  = current_state["team_red_name"]
    name_blue = current_state["team_blue_name"]
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
        f"Field 600x400. Red team = '{name_red}' attacks RIGHT goal (x=600). "
        f"Blue team = '{name_blue}' attacks LEFT goal (x=0).\n"
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
# 9. PHYSIK
# =====================================================================
LLM_THROTTLE  = 1.2
TICK_INTERVAL = 0.10

def run_game_tick():
    now = time.time()

    if now - shared_state["last_llm_call"] > LLM_THROTTLE:
        shared_state["last_llm_call"] = now
        moves = fetch_all_agent_moves(shared_state)
        shared_state["last_llm_response"] = json.dumps(moves, indent=2)
        for name, p in shared_state["players"].items():
            mv = moves.get(name, {})
            p["dx"]   = float(mv.get("x", mv.get("dx", 0.0)))
            p["dy"]   = float(mv.get("y", mv.get("dy", 0.0)))
            p["kick"] = bool(mv.get("k", mv.get("kick", False)))

    for p in shared_state["players"].values():
        p["x"] = max(20, min(580, p["x"] + p["dx"]))
        p["y"] = max(20, min(380, p["y"] + p["dy"]))

        dx = p["x"] - shared_state["ball"]["x"]
        dy = p["y"] - shared_state["ball"]["y"]
        if dx*dx + dy*dy < 625 and p["kick"]:
            direction = 12 if p["team"] == "Red" else -12
            shared_state["ball"]["vx"] = direction
            shared_state["ball"]["vy"] = (shared_state["ball"]["y"] - p["y"]) * 0.35

    b = shared_state["ball"]
    b["x"] += b["vx"]; b["y"] += b["vy"]
    b["vx"] *= 0.88;   b["vy"] *= 0.88

    shared_state["ball_trail"].append([round(b["x"], 1), round(b["y"], 1)])
    if len(shared_state["ball_trail"]) > 12:
        shared_state["ball_trail"].pop(0)

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

# =====================================================================
# 10. PITCH RENDER
# =====================================================================
def generate_pitch_html(state, t):
    players_json = json.dumps(state["players"])
    ball_json    = json.dumps(state["ball"])
    trail_json   = json.dumps(state["ball_trail"])
    red_color    = state["team_red_color"]
    blue_color   = state["team_blue_color"]
    red_flag     = NATIONS.get(state["team_red_nation"], {}).get("flag", "")
    blue_flag    = NATIONS.get(state["team_blue_nation"], {}).get("flag", "")
    score_text   = (
        f"{red_flag} {state['team_red_name']}: {state['score']['Red']}  |  "
        f"{state['team_blue_name']} {blue_flag}: {state['score']['Blue']}"
    )

    return f"""<!DOCTYPE html>
<html><head><style>
body {{ margin:0; padding:0; overflow:hidden; background-color:#0b0c10; }}
.container {{
  background:#111215; padding:12px; border-radius:10px;
  color:white; font-family:'Inter',sans-serif; box-sizing:border-box;
}}
</style></head><body>
<div class="container">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;font-weight:bold;font-size:15px;">
    <span>⏱️ {t['time']}: {state['time_left']:.1f}s</span>
    <span style="color:#00e676;font-size:16px;font-family:monospace;letter-spacing:1px;">{score_text}</span>
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
const RED_COLOR  = "{red_color}";
const BLUE_COLOR = "{blue_color}";

ctx.strokeStyle = "rgba(255,255,255,0.8)"; ctx.lineWidth = 2.5;
ctx.beginPath(); ctx.moveTo(300, 0); ctx.lineTo(300, 400); ctx.stroke();
ctx.beginPath(); ctx.arc(300, 200, 50, 0, 2*Math.PI); ctx.stroke();
ctx.strokeRect(0, 100, 60, 200); ctx.strokeRect(540, 100, 60, 200);
ctx.fillStyle = "rgba(255,255,255,0.18)";
ctx.fillRect(0, 120, 10, 160); ctx.fillRect(590, 120, 10, 160);

ctx.fillStyle = "rgba(255,255,255,0.15)";
ctx.font = "bold 24px 'Impact',sans-serif"; ctx.textAlign = "center";
ctx.fillText("MAKE FOOTBALL TEAM", 300, 210);

for (let i = 0; i < trail.length; i++) {{
  const alpha = (i + 1) / trail.length * 0.5;
  ctx.beginPath();
  ctx.arc(trail[i][0], trail[i][1], 3 + i * 0.3, 0, 2*Math.PI);
  ctx.fillStyle = `rgba(255,255,255,${{alpha}})`;
  ctx.fill();
}}

ctx.beginPath(); ctx.arc(ball.x, ball.y, 7, 0, 2*Math.PI);
ctx.fillStyle = "#ffffff"; ctx.fill();
ctx.strokeStyle = "#000"; ctx.lineWidth = 1.5; ctx.stroke();

for (let name in players) {{
  const p = players[name];
  ctx.beginPath(); ctx.arc(p.x, p.y, 12, 0, 2*Math.PI);
  ctx.fillStyle = p.team === "Red" ? RED_COLOR : BLUE_COLOR;
  ctx.fill();
  ctx.strokeStyle = "#ffffff"; ctx.lineWidth = 1.5; ctx.stroke();

  ctx.fillStyle = "rgba(255,255,255,0.95)";
  ctx.font = "bold 9px sans-serif"; ctx.textAlign = "center";
  const role = name.split('_')[1].slice(0,2).toUpperCase();
  ctx.fillText(role, p.x, p.y + 3);
}}
</script></body></html>"""

# =====================================================================
# 11. LAYOUT
# =====================================================================
col_left, col_right = st.columns([1, 1.25])

with col_left:
    st.session_state.ui_lang = st.selectbox(
        "🌐 Interface Language / Sprache",
        ["English", "Deutsch", "Français", "Español", "Polski"]
    )
    lang = TRANSLATIONS[st.session_state.ui_lang]

    st.title(lang["panel_title"])

    # --- MATCH SETUP --------------------------------------------------
    with st.expander(lang["setup_hdr"], expanded=False):
        st.caption(lang["setup_cap"])

        st.markdown(f"**{lang['team_a']}**")
        c1, c2, c3 = st.columns([1.3, 1, 0.6])
        with c1:
            in_name_red = st.text_input(
                lang["f_name"], value=shared_state["team_red_name"], key="su_name_red"
            )
        with c2:
            in_nation_red = st.selectbox(
                lang["f_nation"], NATION_NAMES,
                index=NATION_NAMES.index(shared_state["team_red_nation"]),
                format_func=lambda n: f"{NATIONS[n]['flag']} {n}",
                key="su_nation_red"
            )
        with c3:
            in_color_red = st.color_picker(
                lang["f_color"], value=shared_state["team_red_color"], key="su_color_red"
            )

        st.markdown(f"**{lang['team_b']}**")
        c4, c5, c6 = st.columns([1.3, 1, 0.6])
        with c4:
            in_name_blue = st.text_input(
                lang["f_name"], value=shared_state["team_blue_name"], key="su_name_blue"
            )
        with c5:
            in_nation_blue = st.selectbox(
                lang["f_nation"], NATION_NAMES,
                index=NATION_NAMES.index(shared_state["team_blue_nation"]),
                format_func=lambda n: f"{NATIONS[n]['flag']} {n}",
                key="su_nation_blue"
            )
        with c6:
            in_color_blue = st.color_picker(
                lang["f_color"], value=shared_state["team_blue_color"], key="su_color_blue"
            )

        in_duration = st.slider(
            lang["f_duration"], min_value=30, max_value=300,
            value=int(shared_state["match_duration"]),
            step=10, key="su_duration"
        )

        if st.button(lang["btn_apply"], use_container_width=True, key="btn_apply"):
            apply_match_setup(
                in_name_red, in_nation_red, in_color_red,
                in_name_blue, in_nation_blue, in_color_blue,
                in_duration
            )
            st.rerun()

        if shared_state.get("info_message") == "applied":
            st.success(lang["applied"])
            shared_state["info_message"] = ""

    if shared_state.get("api_error"):
        st.error(f"⚠️ API Error: {shared_state['api_error']}")
        st.info("💡 Check your NVIDIA API Key in Streamlit Cloud Secrets.")

    # --- START / STOP -------------------------------------------------
    btn_type  = "primary" if shared_state["autoplay"] else "secondary"
    btn_label = lang["btn_stop"] if shared_state["autoplay"] else lang["btn_start"]
    if st.button(btn_label, use_container_width=True, type=btn_type):
        shared_state["autoplay"] = not shared_state["autoplay"]
        st.rerun()

    # --- PROMPTS ------------------------------------------------------
    st.subheader(lang["prompt_hdr"])
    st.caption(lang["prompt_cap"])

    red_flag  = NATIONS.get(shared_state["team_red_nation"],  {}).get("flag", "🔴")
    blue_flag = NATIONS.get(shared_state["team_blue_nation"], {}).get("flag", "🔵")
    tab_red, tab_blue = st.tabs([
        f"{red_flag} {shared_state['team_red_name']}",
        f"{blue_flag} {shared_state['team_blue_name']}"
    ])

    with tab_red:
        for name, p in shared_state["players"].items():
            if p["team"] == "Red":
                role_display = name.split('_')[1].upper()
                with st.expander(f"{red_flag} {role_display}", expanded=(role_display == "STRIKER")):
                    shared_state["players"][name]["prompt"] = st.text_area(
                        "Prompt", value=p["prompt"],
                        key=f"input_{name}", height=70, label_visibility="collapsed"
                    )

    with tab_blue:
        for name, p in shared_state["players"].items():
            if p["team"] == "Blue":
                role_display = name.split('_')[1].upper()
                with st.expander(f"{blue_flag} {role_display}", expanded=(role_display == "STRIKER")):
                    shared_state["players"][name]["prompt"] = st.text_area(
                        "Prompt", value=p["prompt"],
                        key=f"input_{name}", height=70, label_visibility="collapsed"
                    )

    if st.button(lang["btn_reset"], use_container_width=True):
        reset_ball()
        st.rerun()

    with st.expander("📋 " + lang["strat_hdr"], expanded=False):
        st.json({
            name.upper(): {
                "Team": (
                    f"{red_flag} {shared_state['team_red_name']}"
                    if data["team"] == "Red"
                    else f"{blue_flag} {shared_state['team_blue_name']}"
                ),
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
    components.html(html_pitch, height=485, scrolling=False)

# =====================================================================
# 12. GAME LOOP
# =====================================================================
if shared_state["autoplay"] and shared_state["time_left"] > 0:
    now = time.time()
    if now - shared_state["last_tick"] > TICK_INTERVAL:
        shared_state["last_tick"] = now
        run_game_tick()
    time.sleep(0.04)
    st.rerun()
elif not shared_state["autoplay"]:
    time.sleep(1.0)
    st.rerun()
