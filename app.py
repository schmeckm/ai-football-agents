import streamlit as st
import streamlit.components.v1 as components
import asyncio
import json
import time
from openai import AsyncOpenAI

# =====================================================================
# 1. API-KONFIGURATION & GLOBALE EINSTELLUNGEN
# =====================================================================
# WICHTIG: Der Key wird hier sicher aus den Streamlit Secrets geladen.
# Du musst ihn NICHT mehr fest in diesen Code schreiben!
NVIDIA_API_KEY = st.secrets["NVIDIA_API_KEY"]

ai_client = AsyncOpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY
)

st.set_page_config(layout="wide", page_title="Multiplayer AI Football", page_icon="⚽")

# =====================================================================
# 2. DER GLOBALE MULTIPLAYER-SPEICHER (Für alle User identisch)
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
            # --- TEAM ROT ---
            "bob_striker": {"team": "Red", "role": "Striker", "x": 200, "y": 200, "prompt": "Du bist Bob (Stürmer Team Rot). Lauf zum Ball und schieße nach rechts ins gegnerische Tor!"},
            "red_defender": {"team": "Red", "role": "Defender", "x": 100, "y": 200, "prompt": "Du bist der rote Verteidiger. Bleibe links und sichere dein Tor ab."},
            # --- TEAM BLAU ---
            "mel_defender": {"team": "Blue", "role": "Defender", "x": 400, "y": 200, "prompt": "Du bist Mel (Verteidigerin Team Blau). Blockiere die roten Stürmer und dränge sie nach links ab."},
            "blue_striker": {"team": "Blue", "role": "Striker", "x": 500, "y": 200, "prompt": "Du bist der blaue Stürmer. Hol dir den Ball und schieße nach links ins rote Tor!"}
        },
        "last_llm_response": "{}"
    }

# Alle Browser-Tabs teilen sich ab hier diese Variable:
shared_state = get_shared_match()

# =====================================================================
# 3. KÜNSTLICHE INTELLIGENZ (Asynchron & Parallel)
# =====================================================================
async def fetch_agent_move(player_name, player_data, current_state):
    """Fragt das LLM über die NVIDIA API nach dem nächsten Schritt."""
    # Zustand komprimieren, um API-Kosten/Dauer zu sparen
    clean_state = {
        "time_left": current_state["time_left"],
        "ball": current_state["ball"],
        "players": {name: {"x": p["x"], "y": p["y"], "team": p["team"]} for name, p in current_state["players"].items()}
    }
    
    user_message = f"Aktueller Spielzustand: {json.dumps(clean_state)}. Generiere deinen nächsten Schritt."

    try:
        response = await ai_client.chat.completions.create(
            model="meta/llama-3.1-8b-instruct",
            messages=[
                {"role": "system", "content": player_data["prompt"] + " Antworte NUR als JSON mit: 'dx' (-5 bis 5), 'dy' (-5 bis 5) und 'kick' (true/false)."},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=50
        )
        return player_name, json.loads(response.choices[0].message.content)
    except Exception:
        # Fallback bei API-Fehlern
        return player_name, {"dx": 0, "dy": 0, "kick": False}

async def run_game_tick():
    """Berechnet die Bewegungen allen Spieler und die Ballphysik."""
    # 1. Alle KI-Agenten parallel "denken" lassen
    tasks = [fetch_agent_move(name, data, shared_state) for name, data in shared_state["players"].items()]
    results = await asyncio.gather(*tasks)
    
    # In der Debug-Konsole anzeigen
    shared_state["last_llm_response"] = json.dumps(dict(results), indent=2)

    # 2. Spieler bewegen & Kicks ausführen
    for name, move in results:
        p = shared_state["players"][name]
        p["x"] = max(20, min(580, p["x"] + move.get("dx", 0)))
        p["y"] = max(20, min(380, p["y"] + move.get("dy", 0)))
        
        # Schuss-Logik, wenn ein Spieler nah am Ball ist
        dist = ((p["x"] - shared_state["ball"]["x"])**2 + (p["y"] - shared_state["ball"]["y"])**2)**0.5
        if dist < 25 and move.get("kick", False):
            direction = 10 if p["team"] == "Red" else -10
            shared_state["ball"]["vx"] = direction
            shared_state["ball"]["vy"] = (shared_state["ball"]["y"] - p["y"]) * 0.3

    # 3. Ballphysik (Bewegung und Verlangsamung durch Reibung)
    shared_state["ball"]["x"] += shared_state["ball"]["vx"]
    shared_state["ball"]["y"] += shared_state["ball"]["vy"]
    shared_state["ball"]["vx"] *= 0.85
    shared_state["ball"]["vy"] *= 0.85
    
    # 4. Tor-Erkennung (Tore liegen zwischen Y: 120 und 280)
    if shared_state["ball"]["x"] > 580 and 120 < shared_state["ball"]["y"] < 280:
        shared_state["score"]["Red"] += 1
        reset_ball()
    elif shared_state["ball"]["x"] < 20 and 120 < shared_state["ball"]["y"] < 280:
        shared_state["score"]["Blue"] += 1
        reset_ball()

    # Zeit herunterzählen
    shared_state["time_left"] = max(0.0, shared_state["time_left"] - 0.2)

def reset_ball():
    shared_state["ball"] = {"x": 300, "y": 200, "vx": 0, "vy": 0}

# =====================================================================
# 4. GRAFIK-ENGINE (HTML5 Canvas via JavaScript)
# =====================================================================
def generate_pitch_html(state):
    players_json = json.dumps(state["players"])
    ball_json = json.dumps(state["ball"])
    score_text = f"ROT: {state['score']['Red']} | BLAU: {state['score']['Blue']}"
    
    return f"""
    <div style="background: #1e1e1e; padding: 15px; border-radius: 10px; color: white; font-family: sans-serif;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 10px; font-weight: bold; font-size: 16px;">
            <span>⏱️ Zeit: {state['time_left']:.1f}s</span>
            <span style="color: #ffcc00; font-size: 18px;">{score_text}</span>
            <span style="color: #4caf50;">● Live-Match</span>
        </div>
        <canvas id="field" width="600" height="400" style="background: #2e7d32; border: 4px solid #fff; border-radius: 5px; width: 100%; height: auto;"></canvas>
    </div>
    <script>
        const canvas = document.getElementById('field');
        const ctx = canvas.getContext('2d');
        const players = {players_json};
        const ball = {ball_json};

        // Spielfeld-Linien zeichnen
        ctx.strokeStyle = "rgba(255,255,255,0.7)"; ctx.lineWidth = 3;
        ctx.beginPath(); ctx.moveTo(300, 0); ctx.lineTo(300, 400); ctx.stroke(); // Mittellinie
        ctx.beginPath(); ctx.arc(300, 200, 50, 0, 2*Math.PI); ctx.stroke(); // Mittelkreis
        
        // Strafräume & Tore
        ctx.strokeRect(0, 100, 60, 200); ctx.strokeRect(540, 100, 60, 200); 
        ctx.fillStyle = "rgba(255,255,255,0.2)";
        ctx.fillRect(0, 120, 10, 160); ctx.fillRect(590, 120, 10, 160); // Tornetze

        // Ball zeichnen
        ctx.beginPath(); ctx.arc(ball.x, ball.y, 7, 0, 2*Math.PI);
        ctx.fillStyle = "white"; ctx.fill(); ctx.strokeStyle = "black"; ctx.lineWidth = 1.5; ctx.stroke();

        // Spieler zeichnen
        for (let name in players) {{
            let p = players[name];
            ctx.beginPath(); ctx.arc(p.x, p.y, 13, 0, 2*Math.PI);
            ctx.fillStyle = p.team === "Red" ? "#dc3545" : "#007bff";
            ctx.fill(); ctx.strokeStyle = "#fff"; ctx.lineWidth = 2; ctx.stroke();
            
            // Text-Schilder über den Spielern
            ctx.fillStyle = "white"; ctx.font = "bold 11px sans-serif"; ctx.textAlign = "center";
            ctx.fillText(name.split('_')[0].toUpperCase(), p.x, p.y - 18);
        }}
    </script>
    """

# =====================================================================
# 5. STREAMLIT FRONTEND-LAYOUT
# =====================================================================
col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.title("⚽ Agent Control Panel")
    
    # Der Start/Stop Knopf schaltet das Spiel für ALLE um
    btn_label = "⏹️ Stop Match (Auto-Play)" if shared_state["autoplay"] else "▶️ Start Match (Auto-Play)"
    if st.button(btn_label, use_container_width=True, type="primary" if not shared_state["autoplay"] else "secondary"):
        shared_state["autoplay"] = not shared_state["autoplay"]
        st.rerun()

    st.subheader("📝 Live Prompt Engineering")
    st.caption("Änderungen hier beeinflussen die Spieler beim nächsten Spieltakt live!")
    
    # Eingabefelder überschreiben direkt den globalen Zustand
    shared_state["players"]["bob_striker"]["prompt"] = st.text_area(
        "🔴 BOB (Roter Stürmer) Strategie:", shared_state["players"]["bob_striker"]["prompt"], height=65
    )
    shared_state["players"]["mel_defender"]["prompt"] = st.text_area(
        "🔵 MEL (Blaue Verteidigerin) Strategie:", shared_state["players"]["mel_defender"]["prompt"], height=65
    )

    # Schiedsrichter-Notfallknopf
    if st.button("🔄 Ball zurücksetzen", use_container_width=True):
        reset_ball()
        st.rerun()

    st.subheader("🖥️ Debug Console (Live JSON Output)")
    st.code(shared_state["last_llm_response"], language="json")

with col_right:
    st.title("🏟️ Live Simulation")
    # HTML-Spielfeld rendern
    html_pitch = generate_pitch_html(shared_state)
    components.html(html_pitch, height=490)

# =====================================================================
# 6. SERVER GAME LOOP (Echtzeit-Aktualisierung)
# =====================================================================
if shared_state["autoplay"] and shared_state["time_left"] > 0:
    current_time = time.time()
    
    # Zeitsperre: Nur alle 0.15 Sekunden darf EIN Tab die KI berechnen.
    # Das verhindert Chaos bei mehreren verbundenen Usern.
    if current_time - shared_state["last_tick"] > 0.15:
        shared_state["last_tick"] = current_time
        asyncio.run(run_game_tick())
    
    # Kurze Atempause für die CPU und sofort neu rendern
    time.sleep(0.05)
    st.rerun()
elif shared_state["autoplay"] is False:
    # Wenn das Spiel pausiert ist, lauschen alle Tabs im Hintergrund (jede Sekunde),
    # ob ein anderer User den "Start"-Knopf drückt.
    time.sleep(1.0)
    st.rerun()
