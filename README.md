MAKE Football Team
AI-driven football simulation. Two teams of three LLM-controlled players square off on an 800×500 pitch. Each player gets a natural-language prompt that determines their behaviour. Empty prompt → player is inactive.
Backend: FastAPI + httpx, forwards game state to NVIDIA `llama-3.1-8b-instruct`
Frontend: vanilla HTML/JS/Canvas, 60 FPS via `requestAnimationFrame`, smooth player motion between LLM updates
Architecture: game state lives in the browser; backend is a thin LLM proxy
Local quickstart
```bash
export NVIDIA_API_KEY=nvapi-...
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
# open http://localhost:8000
```
Docker
```bash
docker build -t make-football .
docker run -p 8000:8000 -e NVIDIA_API_KEY=nvapi-... make-football
```
Portainer deployment via GitHub
Push this repo to GitHub (private is fine)
In Portainer:
Stacks → Add stack
Build method: Repository
Repository URL: `https://github.com/your-user/make-football`
Repository reference: `refs/heads/main` (or your branch)
Compose path: `docker-compose.yml`
If repo is private: tick Authentication and add a GitHub Personal Access Token (`repo` scope)
Environment variables section:
`NVIDIA_API_KEY` = `nvapi-xxxxxxxx`
`MODEL_ID` = `meta/llama-3.1-8b-instruct` (optional)
Deploy the stack
On code update: in Portainer open the stack → Pull and redeploy
Optional: enable GitOps updates (Portainer polls the repo every N minutes)
Stack ends up at `http://<portainer-host>:8000`.
Nginx reverse proxy snippet
If you want to expose it under a subdomain (e.g. `football.example.ch`) with HTTPS, add to your Nginx config:
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
How it works
Browser keeps the game state and runs physics + rendering at 60 FPS
Every ~900 ms the browser POSTs `/api/move` with current ball + player positions and prompts
Backend builds a compact system prompt, calls NVIDIA, parses the returned JSON, returns it
Browser applies the new `dx`/`dy`/`kick` decisions; players keep moving in those directions until the next update
Empty prompts → player filtered out of the LLM request, stays idle on the pitch (transparent + dashed border)
Architecture overview
```
┌─────────────────────────┐         ┌──────────────────────────┐         ┌──────────────────┐
│ Browser                 │ POST    │ FastAPI (this container) │  POST   │ NVIDIA Build API │
│ - game loop @ 60 FPS    │ ──────► │ /api/move                │ ──────► │ llama-3.1-8b     │
│ - canvas render         │         │ - compose prompt         │         │                  │
│ - prompt editors        │ ◄────── │ - call NVIDIA            │ ◄────── │                  │
│ - LLM call every 900 ms │  JSON   │ - parse JSON             │  JSON   │                  │
└─────────────────────────┘         └──────────────────────────┘         └──────────────────┘
```
Tuning
`LLM_INTERVAL_MS` in `index.html` — how often to call the LLM (lower = more reactive, more requests)
`PLAYER_SPEED_SCALE` in `index.html` — overall player movement speed
`max_tokens` in `main.py` — LLM response budget (currently 140, enough for 6 players)
`MODEL_ID` env var — swap to a different model without code change
Troubleshooting
`NVIDIA_API_KEY environment variable is required` → env var not set on the container
`API error: HTTP 429` → rate limit. Increase `LLM_INTERVAL_MS` or upgrade tier
Players don't move → check `/health` endpoint, then watch the debug console in the UI for parse errors
No moves coming back → some Llama responses occasionally miss a player. They get a zero-move fallback so the game keeps running
