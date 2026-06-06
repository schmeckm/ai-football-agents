# ⚽ PTE - Football Soccer · LLM Driven

AI-driven football simulation where every player on the pitch is controlled by `llama-3.1-8b-instruct`. Each player gets a natural-language tactical prompt; the LLM decides where they move and when they shoot. Built as a team-event tool — 🇺🇸 ready for the **FIFA World Cup 2026 (USA · Canada · Mexico)** vibes.

```
🇨🇭 PTE Digital                vs                PTE - Aspire 🇩🇪
   ▼                                                     ▼
[STR][MID][DEF][GK]                          [STR][MID][DEF][GK]
                            ⚽
                  ─── 800 × 500 pitch ───
```

---

## 🏟️ Features

### Match
- **4 roles per team** — Striker, Midfielder, Defender, Goalkeeper (8 players total)
- **Goalkeeper movement constraint** — stays in own penalty area (x ∈ [25,110] or [690,775], y ∈ [150,350])
- **Live referee** — yellow-and-black striped figure that follows the ball with a diagonal offset, raises an arm on goals
- **Cartoon avatars** — deterministic per player name: 6 skin tones × 7 hairstyles × 7 hair colours × 3 mouth styles
- **22 nations with flags** (Switzerland, Germany, Brazil, USA, Singapore, …) + custom colour picker

### Audio & Voice
- **National anthems** — MP3s in `static/anthems/` (kickoff, winner, draw options) with synth fallback; duration sliders; skip ceremony
- **Separate volume sliders** — stadium SFX vs anthem volume
- **Synthesised sound FX** — whistle, kick, goal fanfare + crowd cheer (Web Audio API, no external assets)
- **AI Commentator** with backend LLM endpoint, opt-in, polls every ~14 s during play, fires on kickoff/goal/halftime/fulltime
- **Voice picker** — dropdown of every English voice the browser has, auto-selects male British voices first (Daniel, Microsoft Ryan), then US male, with a 🇬🇧🇺🇸🇦🇺 flag prefix
- **Test button** — sample utterance to compare voices

### Tactics
- **16 strategy presets** — 4 per role, written in coach voice ("First to every ball, no hesitation, no waiting")
- **Tactical Coach AI** — type a tactical idea ("tiki-taka", "park the bus", "gegenpressing") → backend writes all 4 prompts for the active team
- **Strategy library** — save / load / delete named setups (teams + 8 prompts + duration), export/import as JSON

### Match flow
- **Halftime pause** at `duration/2` — modal overlay, ball returns to centre spot, edit tactics, then resume with whistle
- **Slow-motion replay** after every goal — 3-second buffer captured at 30 FPS, plays back at 0.35× with progress bar
- **Confetti burst** + **screen shake** + **goal flash** with team colour
- **Full-time overlay** with winner, "new match" + "🔥 heat map" buttons

### Stats & analytics
- **Live possession bar** — closest active player to ball wins the tick
- **Live kick / shot counters** — shot = kick taken in opponent's half
- **Heat map** — position sampled every 250 ms, rendered as radial-gradient blobs per player after full-time
- **Tournament leaderboard** in localStorage — P/W/D/L/GF/GA/Pts with 3-1-0 scoring, gold/silver/bronze top 3, recent matches list

### Spectator mode (QR-code)
- **Mobile read-only view** at `/spectator` — minimal UI, score, timer, pitch, stats, commentary
- **Auto-polling** every 250 ms, ● LIVE / Waiting / Offline tag
- **Goal flash** + score pulse on the phone too
- **Ceremony overlay** + optional anthem audio synced from the main client
- **Referee** rendered on the spectator pitch
- **Offline QR code** (no external API) — URL includes `?token=` when `STATE_TOKEN` is set
- **Optional `STATE_TOKEN`** — protects `/api/state` from spoofing on the LAN

### Interaction
- **German / English UI** — language switcher (DE default), persisted in localStorage
- **LLM interval slider** — 1.2–4.0 s reaction time (saved in setup prefs)
- **End match** button + **`E` key** — blow the final whistle early; winner or draw anthem plays
- **Draw anthem options** — none, host nation, both teams (short), or fanfare
- **Live prompt editing** — change any player's strategy mid-match, takes effect on next LLM call
- **Empty prompt = inactive** — player rendered as dashed transparent circle, sits the match out
- **Spectator (fullscreen) mode** — `F` key hides the control panel
- **Keyboard shortcuts** — `F` fullscreen · `M` mute · `Space` start/stop · `E` end match · `Esc` close modal

---

## 🚀 Quickstart

```bash
cp .env.example .env   # add NVIDIA_API_KEY (and optional STATE_TOKEN)
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
# open http://localhost:8000
# phone spectator: http://<your-ip>:8000/spectator
```

Copy the same `STATE_TOKEN` into **Match setup → Spectator token** so the QR URL and state push stay in sync.

## 🐳 Docker

```bash
docker build -t pte-football .
docker run -p 8000:8000 -e NVIDIA_API_KEY=nvapi-... pte-football
```

## 📦 Portainer deployment via GitHub

1. **Push this repo to GitHub** (private is fine, just authenticate Portainer)
2. In Portainer:
   - **Stacks → Add stack**
   - Build method: **Repository**
   - Repository URL: `https://github.com/<your-user>/ai-football-agents`
   - Repository reference: `refs/heads/main`
   - Compose path: `docker-compose.yml`
   - Private repo? tick *Authentication* and add a GitHub PAT with `repo` scope
   - **Environment variables**:
     - `NVIDIA_API_KEY` = `nvapi-xxxxxxxx`
     - `MODEL_ID` = `meta/llama-3.1-8b-instruct` (optional)
   - **Deploy the stack**
3. On code update: **Pull and redeploy** with ☑ **Re-pull image** checkbox (without this checkbox, the cached image is reused)
4. Optional: enable **GitOps updates** (Portainer polls the repo every N minutes and auto-redeploys)

Stack ends up at `http://<portainer-host>:8000` (main) and `/spectator` (mobile view).

## 🔒 Nginx HTTPS reverse proxy

```nginx
server {
    listen 443 ssl http2;
    server_name football.example.ch;

    ssl_certificate     /etc/letsencrypt/live/football.example.ch/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/football.example.ch/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 30s;
    }
}
```

---

## 🧠 How it works

1. **Game state lives in the browser.** Ball, players, score, timer — all in a JS object running at 60 FPS via `requestAnimationFrame`.
2. **Every ~1.8 s** (configurable slider) the browser POSTs current positions + tactical prompts to `/api/move`.
3. **Backend** assembles a compact system prompt explaining the field, roles, and active strategies, calls NVIDIA, parses the returned JSON, returns `{x, y, k}` deltas per player (clamped to ±5 each).
4. **Browser applies** the deltas — players keep moving in those directions, kicking when in range, until the next LLM update.
5. **Empty prompts** → player skipped in the LLM request payload, stays idle (transparent + dashed border).
6. **Main page pushes state every 200 ms** to `/api/state`. The spectator page polls the same endpoint at 250 ms intervals.

```
                                         ┌──────────────────┐
                                         │ NVIDIA Build API │
                                         │  llama-3.1-8b    │
                                         └─────┬──────▲─────┘
                                               │      │ JSON
                                               ▼      │
┌─────────────────────────┐         ┌──────────────────────────┐
│ Browser (Operator)      │   POST  │ FastAPI (this container) │
│ • 60 FPS canvas         │ ──────► │ /api/move                │
│ • physics + render      │ ◄────── │ /api/commentary          │
│ • prompt editors        │   JSON  │ /api/generate_strategy   │
│ • LLM call every 1.8 s  │         │ /api/state ◄─────┐       │
└────────────┬────────────┘         │ /spectator       │       │
             │                      └──────────────────┼───────┘
             │ POST state every 200 ms                 │
             └─────────────────────────────────────────┘
                                                       │
                              GET /api/state every 250 ms
                                                       ▼
                                          ┌──────────────────┐
                                          │ Phone (Spectator)│
                                          │ • read-only view │
                                          │ • QR-coded URL   │
                                          └──────────────────┘
```

---

## 🔌 Backend endpoints

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/move` | Per-tick player decisions. Returns `{moves: {player_name: {x,y,k}}}` with deltas clamped to ±5 |
| `POST` | `/api/commentary` | One-sentence live call. Events: `kickoff`, `goal_red`, `goal_blue`, `halftime`, `fulltime`, `ambient` |
| `POST` | `/api/generate_strategy` | Tactical Coach AI. Input: `{intent, team_name}`. Returns 4 role briefings as JSON |
| `GET` | `/api/config` | Public config: `{model, stateAuthRequired}` |
| `POST` | `/api/state` | Main client pushes state. Optional header `X-State-Token` if `STATE_TOKEN` is set |
| `GET` | `/api/state` | Spectator polls. Optional `?token=`. Returns `{data, ts, stale}` |
| `GET` | `/spectator` | Serves `static/spectator.html` |
| `GET` | `/health` | `{status: "ok", model: ...}` for healthchecks |
| `GET` | `/` | Serves `static/index.html` (main page) |

---

## 🎛️ Tuning constants

### Frontend (`static/index.html`)
| Constant | Default | What it does |
|---|---|---|
| `state.llmIntervalMs` | 1800 | How often to call `/api/move` (slider 1200–4000 ms). NVIDIA free tier ≈ 40/min |
| `COMMENTARY_INTERVAL_MS` | 14000 | Ambient commentary cadence |
| `STATE_PUSH_MS` | 200 | How often the main page pushes state to backend |
| `HEATMAP_SAMPLE_MS` | 250 | How often to record positions for the heat map |
| `PLAYER_SPEED_SCALE` | 20 | Overall player movement speed multiplier |
| `KICK_POWER` | 520 | Ball velocity (px/sec) on a kick |
| `BALL_FRICTION_PER_SEC` | 0.55 | Ball decay factor per second |
| `REPLAY_DURATION_SEC` | 3 | Length of slow-mo buffer |
| `REPLAY_SPEED` | 0.35 | Playback speed multiplier (slower than 1.0 = slow-mo) |
| `REF_SPEED` | 130 | Referee movement (px/sec) |
| `GK_RED_X_MIN/MAX`, `GK_BLUE_X_MIN/MAX`, `GK_Y_MIN/MAX` | — | Goalkeeper movement bounds |

### Backend (`main.py`)
| Constant | Default | What it does |
|---|---|---|
| `MODEL_ID` env var | `meta/llama-3.1-8b-instruct` | Swap to a different NVIDIA-hosted model without code change |
| `max_tokens` (move) | 220 | LLM response budget for movements |
| `max_tokens` (commentary) | 50 | LLM response budget for commentary |
| `max_tokens` (gen_strategy) | 600 | LLM response budget for 4-role briefings |

---

## 🧪 Local development tips

- **Hot-reload:** `uvicorn main:app --reload`
- **Test endpoints from CLI:**
  ```bash
  curl http://localhost:8000/health
  curl -X POST http://localhost:8000/api/commentary -H "Content-Type: application/json" \
       -d '{"event":"goal_red","team_red_name":"PTE Digital","score_red":1,"score_blue":0}'
  ```
- **Test the spectator without a phone:** open `http://localhost:8000/spectator` in a second browser tab while a match is running on the main tab

---

## 🩺 Troubleshooting

| Symptom | Cause / Fix |
|---|---|
| Container won't start: `NVIDIA_API_KEY environment variable is required` | Env var missing on the container. Set it in Portainer Stack → Environment variables |
| `API error: HTTP 429` in debug console | NVIDIA rate limit hit. Increase the LLM interval slider to 2.5 s+ or upgrade tier |
| Players don't move | Check `/health` returns OK; watch the debug console at the bottom for parse errors |
| Some player stays still while others move | Llama sometimes drops a player from JSON. The frontend applies a zero-move fallback — the game keeps running |
| **Spectator shows "Waiting" forever** | Main page must be open and a match playing (or just started). State is pushed only when the main page is alive |
| QR code doesn't load | `api.qrserver.com` blocked by firewall. Spectator URL is still shown as text below the QR — copy/paste into phone |
| Goalkeeper isn't visible after deploy | You pulled the old image. Portainer Stack → ☑ **Re-pull image** → Pull and redeploy. Then `Ctrl+Shift+R` in browser |
| Heat map empty after match | No active players + no autoplay = no samples. Make sure at least one team had active prompts during play |
| TTS reads in wrong voice or robotic | Pick a different voice from the dropdown under 🎙️ AI Commentator. On Windows install Microsoft Edge to get the neural voices (Aria/Davis/Guy) |

---

## 📚 Tech stack

- **Backend:** Python 3.11, FastAPI, httpx, Pydantic, uvicorn
- **Frontend:** vanilla HTML / JS / Canvas 2D — no framework, no build step
- **LLM:** NVIDIA Build API (`meta/llama-3.1-8b-instruct`)
- **TTS:** Browser `SpeechSynthesis` (no API calls, runs locally in the browser)
- **Audio FX:** Web Audio API synthesis (no audio files shipped)
- **QR generation:** external `api.qrserver.com` with text fallback
- **Persistence:** browser `localStorage` for history, strategies, mute, voice, commentary preferences
- **Containerisation:** Docker (python:3.11-slim base), Portainer-ready compose

---

## 🎯 Default teams

| Team | Nation | Colour | Plays |
|---|---|---|---|
| 🇨🇭 PTE Digital | Switzerland | `#ff1744` (red) | Left side, attacks right goal |
| 🇩🇪 PTE - Aspire | Germany | `#00b0ff` (blue) | Right side, attacks left goal |

Both editable in the Match Setup accordion — change name, nation flag, jersey colour, duration (30–300 s), then **Apply & Kickoff**.
