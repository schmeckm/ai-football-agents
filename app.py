import streamlit as st
import time
import json
import re
from openai import OpenAI  # Synchroner Client für maximale Stabilität!

# =====================================================================
# 1. API-KONFIGURATION & GLOBALE EINSTELLUNGEN
# =====================================================================
NVIDIA_API_KEY = st.secrets["NVIDIA_API_KEY"]

# Synchroner Client verhindert jegliche Streamlit-Event-Loop-Konflikte
ai_client = OpenAI(
    base_url="https://integrate.api.google.com/v1" if not NVIDIA_API_KEY else "https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY
)

st.set_page_config(layout="wide", page_title="MAKE Football Team - AI Match", page_icon="⚽")

# =====================================================================
# CUSTOM CSS FÜR EIN HOCHWERTIGES GAMING-DASHBOARD (LEFT PANEL)
# =====================================================================
st.markdown("""
    <style>
        /* Globaler Hintergrund & edle Typografie */
        .stApp {
            background-color: #0b0c10 !important;
            color: #f5f5f7 !important;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }
        
        /* Titel & Überschriften Kontrast */
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff !important;
            font-weight: 800 !important;
            letter-spacing: -0.7px;
        }
        
        /* Edle Rahmen für das Gaming-Dashboard */
        div[data-testid="column"] {
            background-color: #12131a;
            padding: 20px !important;
            border-radius: 12px;
            border: 1px solid #1f222e;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
            margin-bottom: 20px;
        }
        
        /* Dropdowns, Selectboxen & Eingabefelder */
        .stSelectbox div[data-baseweb="select"] {
            background-color: #1a1c23 !important;
            color: #ffffff !important;
            border: 1px solid #2f3346 !important;
            border-radius: 8px !important;
        }
        
        /* Textareas für die Prompts */
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
        
        /* Labels über den Widgets */
        label[data-testid="stWidgetLabel"] {
            color: #8a90a6 !important;
            font-weight: 600 !important;
            font-size: 13.5px !important;
            margin-bottom: 4px !important;
        }
        
        /* Modernisiertes Expander/Akkordeon Design für die Spieler */
        div[data-testid="stExpander"] {
            background-color: #16171f !important;
            border: 1px solid #252836 !important;
            border-radius: 8px !important;
            margin-bottom: 8px !important;
            overflow: hidden;
            transition: all 0.2s ease;
        }
        div[data-testid="stExpander"]:hover {
            border-color: #3e445b !important;
        }
        div[data-testid="stExpander"] [data-testid="stExpanderHeader"] {
            font-weight: bold !important;
            color: #ffffff !important;
            padding: 10px 15px !important;
        }
        
        /* Tabs (Team-Reiter) */
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
        
        /* Custom Button Styling (Hochwertige e-sports Buttons) */
        div.stButton > button {
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
        div.stButton > button:hover {
            border-color: #00e676 !important;
            color: #00e676 !important;
            box-shadow: 0 0 20px rgba(0, 230, 118, 0.3) !important;
            transform: translateY(-1.5px);
        }
        div.stButton > button:active {
            transform: translateY(0.5px);
        }
        
        /* Stopp-Button farbliche Anpassung */
        div.stButton > button:contains("⏹") {
            border-color: #ff1744 !important;
        }
        div.stButton > button:contains("⏹"):hover {
            color: #ff1744 !important;
            box-shadow: 0 0 20px rgba(255, 23, 68, 0.3) !important;
        }
        
        /* Debug Console Box */
        div[data-testid="stCodeBlock"] {
            background-color: #07080a !important;
            border: 1px solid #1a1c23 !important;
            border-radius: 8px !important;
        }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. MEHRSPRACHIGES WÖRTERBUCH (EN, DE, FR, ES, PL)
# =====================================================================
TRANSLATIONS = {
    "English": {
        "panel_title": "MAKE Football Team - Control Panel",
        "btn_stop": "⏹️ STOP MATCH",
        "btn_start": "▶️ START MATCH",
        "prompt_hdr": "Live Prompt Engineering",
        "prompt_cap": "Changes here affect players live on the next game tick! Make edits, then click outside or press Ctrl+Enter to apply.",
        "btn_reset": "🔄 RESET BALL TO CENTER",
        "debug_hdr": "Debug Console (Live Single-Query JSON)",
        "sim_title": "MAKE Live Simulation",
        "time": "Time",
        "live": "Live Match",
        "score_red": "MAKE RED",
        "score_blue": "MAKE BLUE"
    },
    "Deutsch": {
        "panel_title": "MAKE Football Team - Kontrollzentrum",
        "btn_stop": "⏹️ SPIEL STOPPEN",
        "btn_start": "▶️ SPIEL STARTEN",
        "prompt_hdr": "Live Prompt Engineering",
        "prompt_cap": "Änderungen hier beeinflussen die Spieler live! Text anpassen, dann außerhalb klicken oder Strg+Enter drücken zum Bestätigen.",
        "btn_reset": "🔄 BALL ZURÜCKSETZEN",
        "debug_hdr": "Debug-Konsole (Sammel-Abfrage JSON)",
        "sim_title": "MAKE Live Simulation",
        "time": "Zeit",
        "live": "Live-Match",
        "score_red": "MAKE ROT",
        "score_blue": "MAKE BLAU"
    },
    "Français": {
        "panel_title": "MAKE Football Team - Panneau de Contrôle",
        "btn_stop": "⏹️ ARRÊTER LE MATCH",
        "btn_start": "▶️ Démarrer Le Match",
        "prompt_hdr": "Ingénierie des Prompts en Direct",
        "prompt_cap": "Les modifications ici affectent les joueurs en direct au prochain tour! Modifiez, puis cliquez à l'extérieur ou appuyez sur Ctrl+Entrée.",
        "btn_reset": "🔄 RÉINITIALISER LE BALLON",
        "debug_hdr": "Console de Débogage (Sortie JSON unique)",
        "sim_title": "Simulation en Direct MAKE",
        "time": "Temps",
        "live": "Match en Direct",
        "score_red": "MAKE ROUGE",
        "score_blue": "MAKE BLEU"
    },
    "Español": {
        "panel_title": "MAKE Football Team - Panel de Control",
        "btn_stop": "⏹️ DETENER PARTIDO",
        "btn_start": "▶️ INICIAR PARTIDO",
        "prompt_hdr": "Ingeniería de Prompts en Vivo",
        "prompt_cap": "¡Los cambios aquí afectan a los jugadores en vivo! Edita el texto, luego haz clic fuera o presiona Ctrl+Enter para aplicar.",
        "btn_reset": "🔄 REINICIAR BALÓN",
        "debug_hdr": "Consola de Depuración (Consulta Única JSON)",
        "sim_title": "Simulación en Vivo MAKE",
        "time": "Tiempo",
        "live": "Partido en Vivo",
        "score_red": "MAKE ROJO",
        "score_blue": "MAKE AZUL"
    },
    "Polski": {
        "panel_title": "MAKE Football Team - Panel Sterowania",
        "btn_stop": "⏹️ ZATRZYMAJ MECZ",
        "btn_start": "▶️ URUCHOM MECZ",
        "prompt_hdr": "Inżynieria Promptów na Żywo",
        "prompt_cap": "Zmiany tutaj wpływają na graczy na żywo! Po edycji kliknij poza polem lub naciśnij Ctrl+Enter, aby zastosować.",
        "btn_reset": "🔄 RESETUJ PIĘKĘ",
        "debug_hdr": "Konsola Debugowania (Zbiór danych JSON)",
        "sim_title": "Symulacja na Żywo MAKE",
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
def fetch_all_agent_moves(current_state):
    """Sucht die Spielzüge ALLER 8 Spieler in einer einzigen, sicheren und synchronen API-Abfrage."""
    clean_state = {
        "time_left": current_state["time_left"],
        "ball": current_state["ball"],
        "players": {name: {"x": p["x"], "y": p["y"], "team": p["team"]} for name, p in current_state["players"].items()}
    }
    
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
        response = ai_client.chat.completions.create(
            model="meta/llama-3.1-8b-instruct",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_message}
            ],
            temperature=0.1,
            max_tokens=400
        )
        
        raw_content = response.choices[0].message.content.strip()
        
        match = re.search(r'\{.*\}', raw_content, re.DOTALL)
        if match:
            parsed_moves = json.loads(match.group(0))
            shared_state["api_error"] = None
            return parsed_moves
        else:
            raise ValueError(f"Could not parse single-query JSON. Response was: '{raw_content}'")
            
    except Exception as e:
        shared_state["api_error"] = str(e)
        return {name: {"dx": 0, "dy": 0, "kick": False} for name in current_state["players"].keys()}

def run_game_tick():
    """Berechnet das Spielfeld basierend auf der Sammel-Abfrage."""
    moves = fetch_all_agent_moves(shared_state)
    shared_state["last_llm_response"] = json.dumps(moves, indent=2)

    for name, p in shared_state["players"].items():
        move = moves.get(name, {"dx": 0, "dy": 0, "kick": False})
        
        p["x"] = max(20, min(580, p["x"] + float(move.get("dx", 0))))
        p["y"] = max(20, min(380, p["y"] + float(move.get("dy", 0))))
        
        dist = ((p["x"] - shared_state["ball"]["x"])**2 + (p["y"] - shared_state["ball"]["y"])**2)**0.5
        if dist < 25 and move.get("kick", False):
            direction = 12 if p["team"] == "Red" else -12
            shared_state["ball"]["vx"] = direction
            shared_state["ball"]["vy"] = (shared_state["ball"]["y"] - p["y"]) * 0.35

    shared_state["ball"]["x"] += shared_state["ball"]["vx"]
    shared_state["ball"]["y"] += shared_state["ball"]["vy"]
    shared_state["ball"]["vx"] *= 0.85
    shared_state["ball"]["vy"] *= 0.85
    
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
# 5. GRAFIK-ENGINE (Sattes grünes Spielfeld mit CSS-Reset gegen Scrollbars)
# =====================================================================
def generate_pitch_html(state, t):
    players_json = json.dumps(state["players"])
    ball_json = json.dumps(state["ball"])
    score_text = f"{t['score_red']}: {state['score']['Red']} | {t['score_blue']}: {state['score']['Blue']}"
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            /* WICHTIG: Verhindert die Scrollbalken im iframe vollständig */
            body {{
                margin: 0;
                padding: 0;
                overflow: hidden;
                background-color: #0b0c10;
            }}
            .container {{
                background: #111215;
                padding: 12px;
                border-radius: 10px;
                color: white;
                font-family: 'Inter', sans-serif;
                box-sizing: border-box;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-weight: bold; font-size: 15px;">
                <span>⏱️ {t['time']}: {state['time_left']:.1f}s</span>
                <span style="color: #00e676; font-size: 17px; font-family: monospace; letter-spacing: 1px;">{score_text}</span>
                <span style="color: #ff9100;">{t['live']}</span>
            </div>
            <canvas id="field" width="600" height="400" style="background: #235e29; border: 3px solid #fff; border-radius: 6px; width: 100%; height: auto; display: block;"></canvas>
        </div>
        <script>
            const canvas = document.getElementById('field');
            const ctx = canvas.getContext('2d');
            const players = {players_json};
            const ball = {ball_json};

            // Linien auf sattem Grün zeichnen
            ctx.strokeStyle = "rgba(255,255,255,0.8)"; ctx.lineWidth = 2.5;
            ctx.beginPath(); ctx.moveTo(300, 0); ctx.lineTo(300, 400); ctx.stroke();
            ctx.beginPath(); ctx.arc(300, 200, 50, 0, 2*Math.PI); ctx.stroke();
            
            ctx.strokeRect(0, 100, 60, 200); ctx.strokeRect(540, 100, 60, 200); 
            ctx.fillStyle = "rgba(255,255,255,0.1)";
            ctx.fillRect(0, 120, 10, 160); ctx.fillRect(590, 120, 10, 160);

            // "MAKE FOOTBALL TEAM" Wasserzeichen im Center
            ctx.fillStyle = "rgba(255, 255, 255, 0.15)";
            ctx.font = "bold 24px 'Impact', sans-serif";
            ctx.textAlign = "center";
            ctx.fillText("MAKE FOOTBALL TEAM", 300, 210);

            // Weißer Ball mit Kontur
            ctx.beginPath(); ctx.arc(ball.x, ball.y, 7, 0, 2*Math.PI);
            ctx.fillStyle = "#ffffff"; ctx.fill(); 
            ctx.strokeStyle = "#000"; ctx.lineWidth = 1.5; ctx.stroke();

            // Spieler zeichnen (Neon-Farben)
            for (let name in players) {{
                let p = players[name];
                ctx.beginPath(); ctx.arc(p.x, p.y, 12, 0, 2*Math.PI);
                
                // Neon Rot vs Neon Cyber Blau
                ctx.fillStyle = p.team === "Red" ? "#ff1744" : "#00b0ff";
                ctx.fill(); 
                ctx.strokeStyle = "#ffffff"; ctx.lineWidth = 1.5; ctx.stroke();
                
                // Labels über Spielern
                ctx.fillStyle = "rgba(255,255,255,0.95)"; 
                ctx.font = "bold 9px sans-serif"; 
                ctx.textAlign = "center";
                
                let displayRole = name.split('_')[1].toUpperCase();
                ctx.fillText(displayRole, p.x, p.y - 16);
            }}
        </script>
    </body>
    </html>
    """

# =====================================================================
# 6. STREAMLIT FRONTEND-LAYOUT
# =====================================================================
col_left, col_right = st.columns([1, 1.25])

with col_left:
    st.session_state.ui_lang = st.selectbox(
        "🌐 Interface Language / Langue / Sprache", 
        ["English", "Deutsch", "Français", "Español", "Polski"]
    )
    
    st.title(lang["panel_title"])
    
    if "api_error" in shared_state and shared_state["api_error"]:
        st.error(f"⚠️ API Error: {shared_state['api_error']}")
        st.info("💡 Please verify your NVIDIA API Key in your Streamlit Cloud Secrets!")
    
    btn_label = lang["btn_stop"] if shared_state["autoplay"] else lang["btn_start"]
    if st.button(btn_label, use_container_width=True):
        shared_state["autoplay"] = not shared_state["autoplay"]
        st.rerun()

    st.subheader(lang["prompt_hdr"])
    st.caption(lang["prompt_cap"])
    
    # Aufteilung in Teams (Tabs)
    tab_red, tab_blue = st.tabs(["🔴 MAKE RED Team", "🔵 MAKE BLUE Team"])
    
    with tab_red:
        for name, p in list(shared_state["players"].items()):
            if p["team"] == "Red":
                role_display = name.split('_')[1].upper()
                # Verwende einen Expander, um Vertikal-Platz zu sparen!
                with st.expander(f"🔴 RED {role_display} - Prompt", expanded=(role_display == "STRIKER")):
                    shared_state["players"][name]["prompt"] = st.text_area(
                        "Prompt String:",
                        value=p["prompt"],
                        key=f"input_{name}",
                        height=70,
                        label_visibility="collapsed"
                    )
                
    with tab_blue:
        for name, p in list(shared_state["players"].items()):
            if p["team"] == "Blue":
                role_display = name.split('_')[1].upper()
                # Verwende einen Expander, um Vertikal-Platz zu sparen!
                with st.expander(f"🔵 BLUE {role_display} - Prompt", expanded=(role_display == "STRIKER")):
                    shared_state["players"][name]["prompt"] = st.text_area(
                        "Prompt String:",
                        value=p["prompt"],
                        key=f"input_{name}",
                        height=70,
                        label_visibility="collapsed"
                    )

    if st.button(lang["btn_reset"], use_container_width=True):
        reset_ball()
        st.rerun()

    st.subheader(lang["debug_hdr"])
    st.code(shared_state["last_llm_response"], language="json")

with col_right:
    st.title(lang["sim_title"])
    html_pitch = generate_pitch_html(shared_state, lang)
    # Nutzt st.iframe mit exzellenter Anpassung
    st.iframe(html_pitch, height=485)

# =====================================================================
# 7. SERVER SPIEL-SCHLEIFE
# =====================================================================
if shared_state["autoplay"] and shared_state["time_left"] > 0:
    current_time = time.time()
    if current_time - shared_state["last_tick"] > 0.15:
        shared_state["last_tick"] = current_time
        run_game_tick()  # Jetzt absolut synchron und stabil!
    time.sleep(0.05)
    st.rerun()
elif shared_state["autoplay"] is False:
    time.sleep(1.0)
    st.rerun()
