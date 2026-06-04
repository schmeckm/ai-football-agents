"""
MAKE Football Team - FastAPI Backend
Endpoints:
  POST /api/move        -> game move decisions
  POST /api/commentary  -> live match commentary
"""
import os
import re
import sys
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


# =====================================================================
# /api/move
# =====================================================================
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


def zero_moves(players: Dict[str, Player]) -> Dict[str, Dict]:
    return {n: {"x": 0, "y": 0, "k": False} for n in players.keys()}


def clamp_move(mv: Dict) -> Dict:
    try:
        x = float(mv.get("x", 0) or 0)
        y = float(mv.get("y", 0) or 0)
    except (TypeError, ValueError):
        x, y = 0.0, 0.0
    return {
        "x": max(-5.0, min(5.0, x)),
        "y": max(-5.0, min(5.0, y)),
        "k": bool(mv.get("k", False)),
    }


def extract_json(raw: str) -> Dict:
    cleaned = re.sub(r"```(?:json)?\s*", "", raw)
    cleaned = re.sub(r"```", "", cleaned)
    m = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not m:
        raise ValueError("no JSON object found")
    return json.loads(m.group(0))


@app.post("/api/move", response_model=MoveResponse)
async def get_moves(req: MoveRequest):
    active = {n: p for n, p in req.players.items() if p.prompt.strip()}
    if not active:
        return MoveResponse(moves=zero_moves(req.players), debug="no active players")

    strategies = "\n".join(
        f"- {name} (team {p.team}): {p.prompt}" for name, p in active.items()
    )
    positions = ", ".join(
        f"{n}=({int(p.x)},{int(p.y)})" for n, p in active.items()
    )
    ball_pos = f"({int(req.ball.get('x', 0))},{int(req.ball.get('y', 0))})"

    system = (
        "You control football players. Output ONE JSON object only, no prose, no markdown.\n\n"
        'FORMAT: {"player_name":{"x":<dx>,"y":<dy>,"k":<bool>}}\n\n'
        "CRITICAL — read carefully:\n"
        "* 'x' is a movement STEP, a small integer between -5 and +5. NOT a field coordinate.\n"
        "* 'y' is a movement STEP, a small integer between -5 and +5. NOT a field coordinate.\n"
        "* Positive x means move RIGHT. Negative x means move LEFT.\n"
        "* Positive y means move DOWN. Negative y means move UP.\n"
        "* 'k' = true only if the player is right next to the ball and should kick this tick.\n"
        "* NEVER output numbers like 200, 400, 780. ALWAYS small numbers between -5 and +5.\n\n"
        f"FIELD: {req.field_w} wide, {req.field_h} tall. "
        f"Red team ('{req.team_red_name}') attacks the RIGHT goal at x={req.field_w}. "
        f"Blue team ('{req.team_blue_name}') attacks the LEFT goal at x=0.\n\n"
        "EXAMPLES:\n"
        '* Striker at (200,250), ball at (300,200) -> {"x":5,"y":-2,"k":false}   (run toward ball)\n'
        '* Striker at (350,200), ball at (355,205) -> {"x":1,"y":1,"k":true}     (touching ball, kick!)\n'
        '* Midfielder at (200,300), ball at (400,200) -> {"x":4,"y":-3,"k":false}  (chase the ball)\n'
        '* Defender at (100,250), ball at (600,250) -> {"x":-1,"y":0,"k":false}  (ball far away, hold)\n\n'
        "RULE OF THUMB: if ball.x > player.x set x positive; if ball.x < player.x set x negative. Same for y.\n\n"
        "PLAYER STRATEGIES:\n" + strategies
    )
    user = f"State: ball at {ball_pos}, players at {positions}. Output JSON now."

    payload = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.2,
        "max_tokens": 180,
    }

    raw = ""
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
            parsed = extract_json(raw)

            cleaned = {}
            for n in req.players.keys():
                if n in parsed and isinstance(parsed[n], dict):
                    cleaned[n] = clamp_move(parsed[n])
                else:
                    cleaned[n] = {"x": 0, "y": 0, "k": False}

            sample = next(iter(cleaned.values()))
            log(f"[move] OK active={len(active)} sample={sample}")
            return MoveResponse(moves=cleaned, debug=raw[:500])

    except httpx.HTTPStatusError as e:
        err = f"HTTP {e.response.status_code}: {e.response.text[:160]}"
        log(f"[move] {err}")
        return MoveResponse(moves=zero_moves(req.players), debug=f"ERROR: {err}")
    except Exception as e:
        err = f"{type(e).__name__}: {str(e)[:160]}"
        log(f"[move] ERROR: {err} | raw={raw[:200]}")
        return MoveResponse(moves=zero_moves(req.players), debug=f"ERROR: {err}")


# =====================================================================
# /api/commentary
# =====================================================================
class CommentaryRequest(BaseModel):
    event: str = "ambient"
    team_red_name: str = "Red"
    team_blue_name: str = "Blue"
    score_red: int = 0
    score_blue: int = 0
    time_left: float = 90.0
    extra: str = ""


class CommentaryResponse(BaseModel):
    text: str
    debug: str = ""


CANNED_COMMENTARY = {
    "kickoff":     "And the match is underway!",
    "goal_red":    "GOAL! What a finish!",
    "goal_blue":   "GOAL! Stunning play!",
    "halftime":    "The halftime whistle blows.",
    "fulltime":    "And that is full time!",
    "ambient":     "End-to-end stuff here.",
}


@app.post("/api/commentary", response_model=CommentaryResponse)
async def get_commentary(req: CommentaryRequest):
    event_desc = {
        "kickoff":   "The match has just kicked off.",
        "goal_red":  f"{req.team_red_name} just scored.",
        "goal_blue": f"{req.team_blue_name} just scored.",
        "halftime":  "It is halftime.",
        "fulltime":  "The match is over.",
        "ambient":   "The match is in play.",
    }.get(req.event, req.event)

    system = (
        "You are an excited football match commentator on live TV. "
        "Reply with ONE short, energetic sentence — maximum 14 words. "
        "No quotes, no asterisks, no markdown formatting. Just the sentence."
    )
    user = (
        f"Score: {req.team_red_name} {req.score_red} - {req.score_blue} {req.team_blue_name}. "
        f"Time left: {int(req.time_left)}s. "
        f"Event: {event_desc} "
        f"{req.extra}\n"
        f"Commentary now:"
    )

    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            r = await client.post(
                NVIDIA_URL,
                headers={
                    "Authorization": f"Bearer {NVIDIA_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": MODEL_ID,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    "temperature": 0.9,
                    "max_tokens": 50,
                },
            )
            r.raise_for_status()
            data = r.json()
            text = data["choices"][0]["message"]["content"].strip()
            text = text.strip('"\'`*').split("\n")[0].strip()
            if len(text) > 160:
                text = text[:157] + "..."
            log(f"[commentary] {req.event} -> {text}")
            return CommentaryResponse(text=text)

    except Exception as e:
        log(f"[commentary] ERROR: {e}")
        fallback = CANNED_COMMENTARY.get(req.event, "The match continues...")
        if req.event == "goal_red":
            fallback = f"GOAL for {req.team_red_name}!"
        elif req.event == "goal_blue":
            fallback = f"GOAL for {req.team_blue_name}!"
        elif req.event == "halftime":
            fallback = f"Halftime. {req.team_red_name} {req.score_red}, {req.team_blue_name} {req.score_blue}."
        return CommentaryResponse(text=fallback, debug=f"fallback: {e}")


# =====================================================================
# static + health
# =====================================================================
@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL_ID}


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse("static/index.html")
