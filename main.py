"""
MAKE Football Team - FastAPI Backend
Single endpoint /api/move forwards game state to NVIDIA llama-3.1-8b-instruct.
"""
import os
import re
import json
from typing import Dict
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY")
if not NVIDIA_API_KEY:
    raise RuntimeError("NVIDIA_API_KEY environment variable is required")

NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL_ID = os.environ.get("MODEL_ID", "meta/llama-3.1-8b-instruct")

app = FastAPI(title="MAKE Football Team")

# Same-origin in production, * for local dev/preview
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Player(BaseModel):
    team: str
    x: float
    y: float
    prompt: str


class MoveRequest(BaseModel):
    ball: Dict[str, float]
    players: Dict[str, Player]
    team_red_name: str = "Make Red"
    team_blue_name: str = "Make Blue"
    field_w: int = 800
    field_h: int = 500


class MoveResponse(BaseModel):
    moves: Dict[str, Dict]
    debug: str = ""


def fallback_moves(players: Dict[str, Player]) -> Dict[str, Dict]:
    return {n: {"x": 0, "y": 0, "k": False} for n in players.keys()}


@app.post("/api/move", response_model=MoveResponse)
async def get_moves(req: MoveRequest):
    # Filter inactive players (empty prompt) – saves tokens, keeps player idle
    active = {n: p for n, p in req.players.items() if p.prompt.strip()}
    if not active:
        return MoveResponse(moves=fallback_moves(req.players), debug="no active players")

    strategies = "\n".join(
        f"{name}({p.team}): {p.prompt}" for name, p in active.items()
    )
    positions = " | ".join(
        f"{n}={int(p.x)},{int(p.y)}" for n, p in active.items()
    )

    system = (
        "You control football players. Return ONLY one JSON object, no prose.\n"
        "Schema: {\"player_name\":{\"x\":<dx -5..5>,\"y\":<dy -5..5>,\"k\":<bool>}}\n"
        f"Field {req.field_w}x{req.field_h}. Red team = '{req.team_red_name}' attacks RIGHT goal (x={req.field_w}). "
        f"Blue team = '{req.team_blue_name}' attacks LEFT goal (x=0).\n"
        "Strategies:\n" + strategies
    )
    user = f"Ball={int(req.ball.get('x', 0))},{int(req.ball.get('y', 0))} | {positions}\nReturn moves now."

    payload = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.2,
        "max_tokens": 140,
    }

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            r = await client.post(
                NVIDIA_URL,
                headers={
                    "Authorization": f"Bearer {NVIDIA_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            r.raise_for_status()
            data = r.json()
            raw = data["choices"][0]["message"]["content"].strip()

            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if not match:
                raise ValueError(f"no JSON in response: {raw[:140]}")

            parsed = json.loads(match.group(0))
            for n in req.players.keys():
                if n not in parsed:
                    parsed[n] = {"x": 0, "y": 0, "k": False}

            return MoveResponse(moves=parsed, debug=raw[:500])

    except Exception as e:
        return MoveResponse(
            moves=fallback_moves(req.players),
            debug=f"ERROR: {str(e)[:200]}",
        )


@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL_ID}


# Serve frontend
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse("static/index.html")

