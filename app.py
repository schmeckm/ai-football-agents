import streamlit as st
import streamlit.components.v1 as components
import asyncio
import json
import time
from openai import AsyncOpenAI

# =====================================================================
# 1. API CONFIGURATION & GLOBAL SETTINGS
# =====================================================================
NVIDIA_API_KEY = st.secrets["NVIDIA_API_KEY"]

ai_client = AsyncOpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY
)

st.set_page_config(layout="wide", page_title="Multiplayer AI Football", page_icon="⚽")

# =====================================================================
# 2. MULTI-LANGUAGE DICTIONARY (EN, DE, FR, ES, PL)
# =====================================================================
TRANSLATIONS = {
    "English": {
        "panel_title": "⚽ Agent Control Panel",
        "btn_stop": "⏹️ Stop Match (Auto-Play)",
        "btn_start": "▶️ Start Match (Auto-Play)",
        "prompt_hdr": "📝 Live Prompt Engineering",
        "prompt_cap": "Changes here affect players live on the next game tick! You can type in ANY language.",
        "bob_lbl": "🔴 BOB (Red Striker) Strategy:",
        "mel_lbl": "🔵 MEL (Blue Defender) Strategy:",
        "btn_reset": "🔄 Reset Ball",
        "debug_hdr": "🖥️ Debug Console (Live JSON Output)",
        "sim_title": "🏟️ Live Simulation",
        "time": "Time",
        "live": "Live Match",
        "score_red": "RED",
        "score_blue": "BLUE"
    },
    "Deutsch": {
        "panel_title": "⚽ Agenten-Kontrollzentrum",
        "btn_stop": "⏹️ Spiel stoppen (Auto-Play)",
        "btn_start": "▶️ Spiel starten (Auto-Play)",
        "prompt_hdr": "📝 Live Prompt Engineering",
        "prompt_cap": "Änderungen hier beeinflussen die Spieler live beim nächsten Takt! Eingabe in JEDER Sprache möglich.",
        "bob_lbl": "🔴 BOB (Roter Stürmer) Strategie:",
        "mel_lbl": "🔵 MEL (Blaue Verteidigerin) Strategie:",
        "btn_reset": "🔄 Ball zurücksetzen",
        "debug_hdr": "🖥️ Debug-Konsole (Live JSON Output)",
        "sim_title": "🏟️ Live Simulation",
        "time": "Zeit",
        "live": "Live-Match",
        "score_red": "ROT",
        "score_blue": "BLAU"
    },
    "Français": {
        "panel_title": "⚽ Panneau de Contrôle des Agents",
        "btn_stop": "⏹️ Arrêter le Match (Auto-Play)",
        "btn_start": "▶️ Démarrer le Match (Auto-Play)",
        "prompt_hdr": "📝 Ingénierie des Prompts en Direct",
        "prompt_cap": "Les modifications ici affectent les joueurs en direct au prochain tour! Vous pouvez écrire dans N'IMPORTE QUELLE langue.",
        "bob_lbl": "🔴 Stratégie de BOB (Attaquant Rouge) :",
        "mel_lbl": "🔵 Stratégie de MEL (Défenseuse Bleue) :",
        "btn_reset": "🔄 Réinitialiser le Ballon",
        "debug_hdr": "🖥️ Console de Débogage (Sortie JSON)",
        "sim_title": "🏟️ Simulation en Direct",
        "time": "Temps",
        "live": "Match en Direct",
        "score_red": "ROUGE",
        "score_blue": "BLEU"
    },
    "Español": {
        "panel_title": "⚽ Panel de Control de Agentes",
        "btn_stop": "⏹️ Detener Partido (Auto-Play)",
        "btn_start": "▶️ Iniciar Partido (Auto-Play)",
        "prompt_hdr": "📝 Ingeniería de Prompts en Vivo",
        "prompt_cap": "¡Los cambios aquí afectan a los jugadores en vivo en el próximo segundo! Puedes escribir en CUALQUIER idioma.",
        "bob_lbl": "🔴 Estrategia de BOB (Delantero Rojo):",
        "mel_lbl": "🔵 Estrategia de MEL (Defensora Azul):",
        "btn_reset": "🔄 Reiniciar Balón",
        "debug_hdr": "🖥️ Consola de Depuración (JSON en Vivo)",
        "sim_title": "🏟️ Simulación en Vivo",
        "time": "Tiempo",
        "live": "Partido en Vivo",
        "score_red": "ROJO",
        "score_blue": "AZUL"
    },
    "Polski": {
        "panel_title": "⚽ Panel Sterowania Agentami",
        "btn_stop": "⏹️ Zatrzymaj Mecz (Auto-Play)",
        "btn_start": "▶️ Uruchom Mecz (Auto-Play)",
        "prompt_hdr": "📝 Inżynieria Promptów na Żywo",
        "prompt_cap": "Zmiany tutaj wpływają na graczy na żywo przy następnym ruchu! Możesz pisać w DOWOLNYM języku.",
        "bob_lbl": "🔴 Strategia BOBA (Czerwony Napastnik):",
        "mel_lbl": "🔵 Strategia MEL (Niebieski Obrońca):",
        "btn_reset": "🔄 Resetuj Piłkę",
        "debug_hdr": "🖥️ Konsola Debugowania (Format JSON)",
        "sim_title": "🏟️ Symulacja na Żywo",
        "time": "Czas",
        "live": "Mecz na Żywo",
        "score_red": "CZERWONI",
        "score_blue": "NIEBIESCY"
    }
}

# Local Session State for individual language selection per browser tab
if "ui_lang" not in st.session_state:
    st.session_state.ui_lang = "English"

lang = TRANSLATIONS[st.session_state.ui_lang]

# =====================================================================
# 3. GLOBAL MULTIPLAYER MATCH STATE (Shared by everyone)
# =====================================================================
@st.cache_resource
def get_shared_match():
    return {
        "time_left": 90.0,
        "score": {"Red": 0, "Blue": 0},
        "autoplay": False,
        "last_tick": 0.0,
        "ball": {"x": 300, "y": 200, "vx": 0, "vy": 0},
        "players": {
            "bob_striker": {"team": "Red", "role": "Striker", "x": 200, "y": 200, "prompt": "You are Bob (Striker Red Team). Run to the ball and score into the right goal!"},
            "red_defender": {"team": "Red", "role": "Defender", "x": 100, "y": 200, "prompt": "You are the red defender. Stay on the left side and protect your goal."},
            "mel_defender": {"team": "Blue", "role": "Defender", "x": 400, "y": 200, "prompt": "You are Mel (Defender Blue Team). Block the red striker and push him away."},
            "blue_striker": {"team": "Blue", "role": "Striker", "x": 500, "y": 200, "prompt": "You are the blue striker. Get the ball and score into the left goal!"}
        },
        "last_llm_response": "{}"
    }

shared_state = get_shared_match()

# =====================================================================
# 4. ARTIFICIAL INTELLIGENCE (Asynchronous & Multilingual API requests)
# =====================================================================
async def fetch_agent_move(player_name, player_data, current_state):
    """Queries the NVIDIA LLM for the next step, supporting any prompt language."""
    clean_state = {
        "time_left": current_state["time_left"],
        "ball": current_state["ball"],
        "players": {name: {"x": p["x"], "y": p["y"], "team": p["team"]} for name, p in current_state["players"].items()}
    }
    
    user_message = f"Current game state: {json.dumps(clean_state)}. Generate your next move based on your strategy."

    try:
        response = await ai_client.chat.completions.create(
            model="meta/llama-3.1-8b-instruct",
            messages=[
                {"role": "system", "content": player_data["prompt"] + " Respond EXCLUSIVELY as a valid JSON object with keys 'dx' (number -5 to 5), 'dy' (number -5 to 5), and 'kick' (true/false). Do NOT write any markdown, thinking, or extra text before or after the JSON!"},
                {"role": "user", "content": user_message}
            ],
            temperature=0.1,
            max_tokens=60
        )
        
        raw_content = response.choices[0].message.content.strip()
        if raw_content.startswith("```"):
            lines = raw_content.splitlines()
            if lines[0].startswith("```"): lines = lines[1:]
            if lines[-1].startswith("```"): lines = lines[:-1]
            raw_content = "\n".join(lines).strip()
            
        return player_name, json.loads(raw_content)
    except Exception as e:
        print(f"❌ API Error for {player_name}: {e}")
        return player_name, {"dx": 0, "dy": 0, "kick": False}

async def run_game_tick():
    """Calculates all player movements and ball physics."""
    tasks = [fetch_agent_move(name, data, shared_state) for name, data in shared_state["players"].items()]
    results = await asyncio.gather(*tasks)
    
    shared_state["last_llm_response"] = json.dumps(dict(results), indent=2)

    for name, move in results:
        p = shared_state["players"][name]
        p["x"] = max(20, min(580, p["x"] + move.get("dx", 0)))
        p["y"] = max(20, min(380, p["y"] + move.get("dy", 0)))
        
        dist = ((p["x"] - shared_state["ball"]["x"])**2 + (p["y"] - shared_state["ball"]["y"])**2)**0.5
        if dist < 25 and move.get("kick", False):
            direction = 11 if p["team"] == "Red" else -11
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
# 5. GRAPHICS ENGINE (HTML5 Canvas via JavaScript)
# =====================================================================
def generate_pitch_html(state, t):
    players_json = json.dumps(state["players"])
    ball_json = json.dumps(state["ball"])
    score_text = f"{t['score_red']}: {state['score']['Red']} | {t['score_blue']}: {state['score']['Blue']}"
    
    return f"""
    <div style="background: #1e1e1e; padding: 15px; border-radius: 10px; color: white; font-family: sans-serif;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 10px; font-weight: bold; font-size: 16px;">
            <span>⏱️ {t['time']}: {state['time_left']:.1f}s</span>
            <span style="color: #ffcc00; font-size: 18px;">{score_text}</span>
            <span style="color: #4caf50;">{t['live']}</span>
        </div>
        <canvas id="field" width="600" height="400" style="background: #2e7d32; border: 4px solid #fff; border-radius: 5px; width: 100%; height: auto;"></canvas>
    </div>
    <script>
        const canvas = document.getElementById('field');
        const ctx = canvas.getContext('2d');
        const players = {players_json};
        const ball = {ball_json};

        ctx.strokeStyle = "rgba(255,255,255,0.7)"; ctx.lineWidth = 3;
        ctx.beginPath(); ctx.moveTo(300, 0); ctx.lineTo(300, 400); ctx.stroke();
        ctx.beginPath(); ctx.arc(300, 200, 50, 0, 2*Math.PI); ctx.stroke();
        
        ctx.strokeRect(0, 100, 60, 200); ctx.strokeRect(540, 100, 60, 200); 
        ctx.fillStyle = "rgba(255,255,255,0.2)";
        ctx.fillRect(0, 120, 10, 160); ctx.fillRect(590, 120, 10, 160);

        ctx.beginPath(); ctx.arc(ball.x, ball.y, 7, 0, 2*Math.PI);
        ctx.fillStyle = "white"; ctx.fill(); ctx.strokeStyle = "black"; ctx.lineWidth = 1.5; ctx.stroke();

        for (let name in players) {{
            let p = players[name];
            ctx.beginPath(); ctx.arc(p.x, p.y, 13, 0, 2*Math.PI);
            ctx.fillStyle = p.team === "Red" ? "#dc3545" : "#007bff";
            ctx.fill(); ctx.strokeStyle = "#fff"; ctx.lineWidth = 2; ctx.stroke();
            
            ctx.fillStyle = "white"; ctx.font = "bold 11px sans-serif"; ctx.textAlign = "center";
            ctx.fillText(name.split('_')[0].toUpperCase(), p.x, p.y - 18);
        }}
    </script>
    """

# =====================================================================
# 6. STREAMLIT FRONTEND LAYOUT
# =====================================================================
col_left, col_right = st.columns([1, 1.2])

with col_left:
    # Language Picker (only changes the UI locally for this specific user tab!)
    st.session_state.ui_lang = st.selectbox(
        "🌐 Interface Language / Langue / Sprache", 
        ["English", "Deutsch", "Français", "Español", "Polski"]
    )
    
    st.title(lang["panel_title"])
    
    btn_label = lang["btn_stop"] if shared_state["autoplay"] else lang["btn_start"]
    if st.button(btn_label, use_container_width=True, type="primary" if not shared_state["autoplay"] else "secondary"):
        shared_state["autoplay"] = not shared_state["autoplay"]
        st.rerun()

    st.subheader(lang["prompt_hdr"])
    st.caption(lang["prompt_cap"])
    
    shared_state["players"]["bob_striker"]["prompt"] = st.text_area(
        lang["bob_lbl"], shared_state["players"]["bob_striker"]["prompt"], height=65
    )
    shared_state["players"]["mel_defender"]["prompt"] = st.text_area(
        lang["mel_lbl"], shared_state["players"]["mel_defender"]["prompt"], height=65
    )

    if st.button(lang["btn_reset"], use_container_width=True):
        reset_ball()
        st.rerun()

    st.subheader(lang["debug_hdr"])
    st.code(shared_state["last_llm_response"], language="json")

with col_right:
    st.title(lang["sim_title"])
    html_pitch = generate_pitch_html(shared_state, lang)
    components.html(html_pitch, height=490)

# =====================================================================
# 7. SERVER GAME LOOP
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
