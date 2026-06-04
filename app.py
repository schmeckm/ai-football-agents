import streamlit as st
import asyncio
import json
import time
import re
from openai import AsyncOpenAI

# =====================================================================
# 1. API-KONFIGURATION & GLOBALE EINSTELLUNGEN
# =====================================================================
# Sicherer Abruf des Keys aus den Streamlit Secrets
NVIDIA_API_KEY = st.secrets["NVIDIA_API_KEY"]

ai_client = AsyncOpenAI(
    base_url="https://integrate.api.google.com/v1" if not NVIDIA_API_KEY else "https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY
)

st.set_page_config(layout="wide", page_title="MAKE Football Team - AI Match", page_icon="⚽")

# Custom CSS, um die linke Benutzeroberfläche edel dunkel/schwarz zu färben
st.markdown("""
    <style>
        /* Hintergrund der gesamten App auf edles Dunkel setzen */
        .stApp {
            background-color: #0d0e11;
            color: #ffffff;
        }
        /* Style für Eingabefelder und Buttons anpassen */
        .stTextArea textarea {
            background-color: #1a1c23 !important;
            color: #ffffff !important;
            border: 1px solid #3f4456 !important;
        }
        .stSelectbox div[data-baseweb="select"] {
            background-color: #1a1c23 !important;
            color: #ffffff !important;
        }
        div[data-testid="stExpander"] {
            background-color: #1a1c23 !important;
            border: 1px solid #2d313f !important;
        }
        /* Tabs farblich hervorheben */
        button[data-baseweb="tab"] {
            color: #8a90a6 !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #00e676 !important;
            border-bottom-color: #00e676 !important;
        }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. MEHRSPRACHIGES WÖRTERBUCH (EN, DE, FR, ES, PL)
# =====================================================================
TRANSLATIONS = {
    "English": {
        "panel_title": "⚽ MAKE Football Team - Control Panel",
        "btn_stop": "⏹️ Stop Match (Auto-Play)",
        "btn_start": "▶️ Start Match (Auto-Play)",
        "prompt_hdr": "📝 Live Prompt Engineering",
        "prompt_cap": "Changes here affect players live on the next game tick! You can type in ANY language.",
        "btn_reset": "🔄 Reset Ball",
        "debug_hdr": "🖥️ Debug Console (Live Single-Query JSON)",
        "sim_title": "🏟️ MAKE Live Simulation",
        "time": "Time",
        "live": "Live Match",
        "score_red": "MAKE RED",
        "score_blue": "MAKE BLUE"
    },
    "Deutsch": {
        "panel_title": "⚽ MAKE Football Team - Kontrollzentrum",
        "btn_stop": "⏹️ Spiel stoppen (Auto-Play)",
        "btn_start": "▶️ Spiel starten (Auto-Play)",
        "prompt_hdr": "📝 Live Prompt Engineering",
        "prompt_cap": "Änderungen hier beeinflussen die Spieler live beim nächsten Takt! Eingabe in JEDER Sprache möglich.",
        "btn_reset": "🔄 Ball zurücksetzen",
        "debug_hdr": "🖥️ Debug-Konsole (Sammel-Abfrage JSON)",
        "sim_title": "🏟️ MAKE Live Simulation",
        "time": "Zeit",
        "live": "Live-Match",
        "score_red": "MAKE ROT",
        "score_blue": "MAKE BLAU"
    },
    "Français": {
        "panel_title": "⚽ MAKE Football Team - Panneau de Contrôle",
        "btn_stop": "⏹️ Arrêter le Match (Auto-Play)",
        "btn_start": "▶️ Démarrer le Match (Auto-Play)",
        "prompt_hdr": "📝 Ingénierie des Prompts en Direct",
        "prompt_cap": "Les modifications ici affectent les joueurs en direct au prochain tour! Écrivez dans n'importe quelle langue.",
        "btn_reset": "🔄 Réinitialiser le Ballon",
        "debug_hdr": "🖥️ Console de Débogage (Sortie JSON unique)",
        "sim_title": "🏟️ Simulation en Direct MAKE",
        "time": "Temps",
        "live": "Match en Direct",
        "score_red": "MAKE ROUGE",
        "score_blue": "MAKE BLEU"
    },
    "Español": {
        "panel_title": "⚽ MAKE Football Team - Panel de Control",
        "btn_stop": "⏹️ Detener Partido (Auto-Play)",
        "btn_start": "▶️ Iniciar Partido (Auto-Play)",
        "prompt_hdr": "📝 Ingeniería de Prompts en Vivo",
        "prompt_cap": "¡Los cambios aquí afectan a los jugadores en vivo! Puedes escribir en cualquier idioma.",
        "btn_reset": "🔄 Reiniciar Balón",
        "debug_hdr": "🖥️ Consola de Depuración (Consulta Única JSON)",
        "sim_title": "🏟️ Simulación en Vivo MAKE",
        "time": "Tiempo",
        "live": "Partido en Vivo",
        "score_red": "MAKE ROJO",
        "score_blue": "MAKE AZUL"
    },
    "Polski": {
        "panel_title": "⚽ MAKE Football Team - Panel Sterowania",
        "btn_stop": "⏹️ Zatrzymaj Mecz (Auto-Play)",
        "btn_start": "▶️ Uruchom Mecz (Auto-Play)",
        "prompt_hdr": "📝 Inżynieria Promptów na Żywo",
        "prompt_cap": "Zmiany tutaj wpływają na graczy na żywo! Możesz pisać w dowolnym języku.",
        "btn_reset": "🔄 Resetuj Piłkę",
        "debug_hdr": "🖥️ Konsola Debugowania (Zbiór danych JSON)",
        "sim_title": "🏟️ Symulacja na Żywo MAKE",
        "time": "Czas",
        "live": "Mecz na Żywo",
        "score_red": "MAKE CZERWONI",
        "score_blue": "MAKE NIEBIESCY"
    }
}

if "ui_lang" not in st.session_state:
    st.session_state.ui_lang = "English"

lang = TRANSLATIONS[st.session_state.ui_lang]

# =====================================================================
# 3. GLOBALE SPIELZUSTANDS-DATENBANK (Für alle User synchronisiert)
# =====================================================================
@st.cache_resource
def get_shared_match():
    return {
        "time_left": 90.0,
        "score": {"Red": 0, "Blue": 0},
        "autoplay": False,
        "last_tick": 0.0,
        "api_error": None,
        "ball": {"x": 300, "y": 200, "vx": 0, "vy": 0},
        "players": {
            # --- TEAM RED (MAKE RED) ---
            "red_striker": {"team": "Red", "role": "Striker", "x": 200, "y": 150, "prompt": "You are the Red Striker. Sprint to the ball and shoot right into the blue goal!"},
            "red_midfielder": {"team": "Red", "role": "Midfielder", "x": 180, "y": 250, "prompt": "You are the Red Midfielder. Distribute the ball to strikers and support from behind."},
            "red_winger": {"team": "Red", "role": "Winger", "x": 150, "y": 80, "prompt": "You are the Red Winger. Run along the upper wing and cross the ball forward."},
            "red_defender": {"team": "Red", "role": "Defender", "x": 100, "y": 200, "prompt": "You are the Red Defender. Stay on your half and clear the ball away from the red goal."},
            
            # --- TEAM BLUE (MAKE BLUE) ---
            "blue_striker": {"team": "Blue", "role": "Striker", "x": 400, "y": 250, "prompt": "You are the Blue Striker. Chase the ball and shoot left into the red goal!"},
            "blue_midfielder": {"team": "Blue", "role": "Midfielder", "x": 420, "y": 150, "prompt": "You are the Blue Midfielder. Stop red attacks and pass the ball to blue strikers."},
            "blue_winger": {"team": "Blue", "role": "Winger", "x": 450, "y": 320, "prompt": "You are the Blue Winger. Intercept red passes along the lower wing."},
            "blue_defender": {"team": "Blue", "role": "Defender", "x": 500, "y": 200, "prompt": "You are the Blue Defender. Guard the right goal area and block red strikers."}
        },
        "last_llm_response": "{}"
    }

shared_state = get_shared_match()

# =====================================================================
# 4. KÜNSTLICHE INTELLIGENZ (Sammel-Abfrage zur Vermeidung von 429)
# =====================================================================
async def fetch_all_agent_moves(current_state):
    """Sucht die Spielzüge ALLER 8 Spieler in einer einzigen, sicheren API-Abfrage."""
    clean_state = {
        "time_left": current_state["time_left"],
        "ball": current_state["ball"],
        "players": {name: {"x": p["x"], "y": p["y"], "team": p["team"]} for name, p in current_state["players"].items()}
    }
    
    # Wir erstellen eine Liste aller Spieler-Prompts für das KI-Modell
    strategies_info = ""
    for name, p in current_state["players"].items():
        strategies_info += f"- {name} (Team: {p['team']}): \"{p['prompt']}\"\n"

    system_instruction = f"""You are the central game brain for 'MAKE Football Team'.
Your task is to compute the next movement ('dx', 'dy' from -5 to 5) and shot decision ('kick' true/false) for ALL 8 players simultaneously.
You must read the individual instructions for each player carefully and apply them:

{strategies_info}

You MUST return strictly a single valid JSON object mapping each player's name to their move decision. Do not write any explanations, markdown, or text outside the JSON.
Example Format:
{{
  "red_striker": {{"dx": 3.2, "dy": -1.5, "kick": false}},
  "red_midfielder": {{"dx": 1.0, "dy": 0.5, "kick": false}},
  "red_winger": {{"dx": 0.0, "dy": -2.0, "kick": false}},
  "red_defender": {{"dx": -0.5, "dy": 0.0, "kick": false}},
  "blue_striker": {{"dx": -2.5, "dy": 1.2, "kick": true}},
  "blue_midfielder": {{"dx": -1.0, "dy": -0.5, "kick": false}},
  "blue_winger": {{"dx": 0.5, "dy": 1.0, "kick": false}},
  "blue_defender": {{"dx": 0.5, "dy": 0.0, "kick": false}}
}}"""

    user_message = f"Current pitch coordinate state: {json.dumps(clean_state)}. Calculate the moves for all players now!"

    try:
        response = await ai_client.chat.completions.create(
            model="meta/llama-3.1-8b-instruct",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_message}
            ],
            temperature=0.1,
            max_tokens=400
        )
        
        raw_content = response.choices[0].message.content.strip()
        
        # Robustes JSON-Parsing per Regex (falls die KI Text herum baut)
        match = re.search(r'\{.*\}', raw_content, re.DOTALL)
        if match:
            parsed_moves = json.loads(match.group(0))
            shared_state["api_error"] = None
            return parsed_moves
        else:
            raise ValueError(f"Could not parse single-query JSON. Response was: '{raw_content}'")
            
    except Exception as e:
        shared_state["api_error"] = str(e)
        # Fallback: Alle Spieler bleiben stehen
        return {name: {"dx": 0, "dy": 0, "kick": False} for name in current_state["players"].keys()}

async def run_game_tick():
    """Berechnet das Spielfeld basierend auf der Sammel-Abfrage."""
    moves = await fetch_all_agent_moves(shared_state)
    
    # Speichern für die Debug-Konsole links
    shared_state["last_llm_response"] = json.dumps(moves, indent=2)

    # Positionen & Kicks berechnen
    for name, p in shared_state["players"].items():
        move = moves.get(name, {"dx": 0, "dy": 0, "kick": False})
        
        # Neue Koordinaten begrenzen, damit niemand das Spielfeld verlässt
        p["x"] = max(20, min(580, p["x"] + float(move.get("dx", 0))))
        p["y"] = max(20, min(380, p["y"] + float(move.get("dy", 0))))
        
        # Schussprüfung
        dist = ((p["x"] - shared_state["ball"]["x"])**2 + (p["y"] - shared_state["ball"]["y"])**2)**0.5
        if dist < 25 and move.get("kick", False):
            direction = 12 if p["team"] == "Red" else -12
            shared_state["ball"]["vx"] = direction
            shared_state["ball"]["vy"] = (shared_state["ball"]["y"] - p["y"]) * 0.35

    # Ballphysik und Reibung
    shared_state["ball"]["x"] += shared_state["ball"]["vx"]
    shared_state["ball"]["y"] += shared_state["ball"]["vy"]
    shared_state["ball"]["vx"] *= 0.85
    shared_state["ball"]["vy"] *= 0.85
    
    # Torerfassung (Tore liegen zwischen Y: 120 und 280)
    if shared_state["ball"]["x"] > 580 and 120 < shared_state["ball"]["y"] < 280:
        shared_state["score"]["Red"] += 1
        reset_ball()
    elif shared_state["ball"]["x"] < 20 and 120 < shared_state["ball"]["y"] < 280:
        shared_state["score"]["Blue"] += 1
        reset_ball()

    shared_state["time_left"] = max(0.0, shared_state["time_left"] - 0.2)

def reset_ball():
    shared_state["ball"] = {"x": 300, "y": 200, "vx": 0, "vy": 0}

# =====================================================================
# 5. GRAFIK-ENGINE (Klassisch grünes HTML5-Spielfeld)
# =====================================================================
def generate_pitch_html(state, t):
    players_json = json.dumps(state["players"])
    ball_json = json.dumps(state["ball"])
    score_text = f"{t['score_red']}: {state['score']['Red']} | {t['score_blue']}: {state['score']['Blue']}"
    
    return f"""
    <div style="background: #111215; padding: 15px; border-radius: 10px; color: white; font-family: sans-serif;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 10px; font-weight: bold; font-size: 16px;">
            <span>⏱️ {t['time']}: {state['time_left']:.1f}s</span>
            <span style="color: #00e676; font-size: 18px; font-family: monospace; letter-spacing: 1px;">{score_text}</span>
            <span style="color: #ff9100;">{t['live']}</span>
        </div>
        <canvas id="field" width="600" height="400" style="background: #235e29; border: 4px solid #fff; border-radius: 8px; width: 100%; height: auto;"></canvas>
    </div>
    <script>
        const canvas = document.getElementById('field');
        const ctx = canvas.getContext('2d');
        const players = {players_json};
        const ball = {ball_json};

        // Weiße Spielfeldlinien auf sattem Grün
        ctx.strokeStyle = "rgba(255,255,255,0.8)"; ctx.lineWidth = 2.5;
        ctx.beginPath(); ctx.moveTo(300, 0); ctx.lineTo(300, 400); ctx.stroke();
        ctx.beginPath(); ctx.arc(300, 200, 50, 0, 2*Math.PI); ctx.stroke();
        
        ctx.strokeRect(0, 100, 60, 200); ctx.strokeRect(540, 100, 60, 200); 
        ctx.fillStyle = "rgba(255,255,255,0.1)";
        ctx.fillRect(0, 120, 10, 160); ctx.fillRect(590, 120, 10, 160);

        // Dezent integriertes "MAKE FOOTBALL TEAM" Wasserzeichen im Center
        ctx.fillStyle = "rgba(255, 255, 255, 0.15)";
        ctx.font = "bold 24px 'Impact', sans-serif";
        ctx.textAlign = "center";
        ctx.fillText("MAKE FOOTBALL TEAM", 300, 210);

        // Weißer Ball mit Kontur
        ctx.beginPath(); ctx.arc(ball.x, ball.y, 7, 0, 2*Math.PI);
        ctx.fillStyle = "#ffffff"; ctx.fill(); 
        ctx.strokeStyle = "#000"; ctx.lineWidth = 1.5; ctx.stroke();

        // Neon Spieler-Punkte
        for (let name in players) {{
            let p = players[name];
            ctx.beginPath(); ctx.arc(p.x, p.y, 12, 0, 2*Math.PI);
            
            // Neon Rot vs Neon Cyber Blau
            ctx.fillStyle = p.team === "Red" ? "#ff1744" : "#00b0ff";
            ctx.fill(); 
            ctx.strokeStyle = "#ffffff"; ctx.lineWidth = 1.5; ctx.stroke();
            
            // Text-Label über dem Spieler
            ctx.fillStyle = "rgba(255,255,255,0.95)"; 
            ctx.font = "bold 9px sans-serif"; 
            ctx.textAlign = "center";
            
            let displayRole = name.split('_')[1].toUpperCase();
            ctx.fillText(displayRole, p.x, p.y - 16);
        }}
    </script>
    """

# =====================================================================
# 6. STREAMLIT BENUTZEROBERFLÄCHE (Steuerung)
# =====================================================================
col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.session_state.ui_lang = st.selectbox(
        "🌐 Interface Language / Langue / Sprache", 
        ["English", "Deutsch", "Français", "Español", "Polski"]
    )
    
    st.title(lang["panel_title"])
    
    # Echtzeit-Fehlermeldung bei API-Problemen direkt auf dem Bildschirm anzeigen
    if "api_error" in shared_state and shared_state["api_error"]:
        st.error(f"⚠️ API Error: {shared_state['api_error']}")
        st.info("💡 Please verify your NVIDIA API Key in your Streamlit Cloud Secrets!")
    
    btn_label = lang["btn_stop"] if shared_state["autoplay"] else lang["btn_start"]
    if st.button(btn_label, use_container_width=True, type="primary" if not shared_state["autoplay"] else "secondary"):
        shared_state["autoplay"] = not shared_state["autoplay"]
        st.rerun()

    st.subheader(lang["prompt_hdr"])
    st.caption(lang["prompt_cap"])
    
    # Aufteilung der Eingabefelder in 2 Teams (Tabs) für ein sauberes Layout
    tab_red, tab_blue = st.tabs(["🔴 MAKE RED Team", "🔵 MAKE BLUE Team"])
    
    with tab_red:
        for name, p in list(shared_state["players"].items()):
            if p["team"] == "Red":
                role_display = name.split('_')[1].upper()
                shared_state["players"][name]["prompt"] = st.text_area(
                    f"🔴 Red {role_display} Strategy:",
                    value=p["prompt"],
                    key=f"input_{name}",
                    height=65
                )
                
    with tab_blue:
        for name, p in list(shared_state["players"].items()):
            if p["team"] == "Blue":
                role_display = name.split('_')[1].upper()
                shared_state["players"][name]["prompt"] = st.text_area(
                    f"🔵 Blue {role_display} Strategy:",
                    value=p["prompt"],
                    key=f"input_{name}",
                    height=65
                )

    if st.button(lang["btn_reset"], use_container_width=True):
        reset_ball()
        st.rerun()

    st.subheader(lang["debug_hdr"])
    st.code(shared_state["last_llm_response"], language="json")

with col_right:
    st.title(lang["sim_title"])
    html_pitch = generate_pitch_html(shared_state, lang)
    st.iframe(html_pitch, height=490)

# =====================================================================
# 7. SERVER SPIEL-SCHLEIFE
# =====================================================================
if shared_state["autoplay"] and shared_state["time_left"] > 0:
    current_time = time.time()
    if current_time - shared_state["last_tick"] > 0.15:
        shared_state["last_tick"] = current_time
        asyncio.run(run_game_tick())
    time.sleep(0.05)
    st.rerun()
elif shared_state["autoplay"] is False:
    time.sleep(1.0)
    st.rerun()
