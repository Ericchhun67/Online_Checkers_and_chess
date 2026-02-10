"""
Simple test script for game routes.
tests:
    - GET /game and /pvp pages
    - POST /move (valid and invalid, PvP turn alternation)
    - AI response payload shape
"""

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from routes.game_routes import games
from utils.game_logic import GameLogic


def reset_games():
    games["checkers"] = GameLogic("checkers")
    games["chess"] = GameLogic("chess")


client = app.test_client()

# Reset shared in-memory games for deterministic results
reset_games()

# ✅ GET /game/game
response = client.get("/game/game?type=checkers")
print("GET /game/game", response.status_code, response.json)
assert response.status_code == 200
assert "board" in response.json
assert response.json["turn"] == "white"

# ✅ GET /game/game invalid
response = client.get("/game/game?type=invalid")
print("GET /game/game invalid", response.status_code, response.json)
assert response.status_code == 400

# ✅ GET /game/pvp page
response = client.get("/game/pvp?game=chess")
print("GET /game/pvp", response.status_code)
assert response.status_code == 200

# ✅ GET /game/win page
response = client.get("/game/win?mode=ai&game=chess&winner=white&moves=20&duration=135")
print("GET /game/win", response.status_code)
assert response.status_code == 200

# ✅ POST /game/move invalid payload
response = client.post("/game/move", json={"game_type": "checkers"})
print("POST /game/move missing", response.status_code, response.json)
assert response.status_code == 400

# ✅ POST /game/move valid move (white starts)
reset_games()
response = client.post("/game/move", json={
    "game_type": "checkers",
    "start": [5, 0],
    "end": [4, 1]
})
print("POST /game/move", response.status_code, response.json)
assert response.status_code == 200
assert response.json["player_move"]["message"] == "Move successful"
assert response.json["turn"] == "black"

# ✅ PvP alternation: black can move after white
response = client.post("/game/move", json={
    "game_type": "checkers",
    "start": [2, 1],
    "end": [3, 0]
})
print("POST /game/move black turn", response.status_code, response.json)
assert response.status_code == 200
assert response.json["turn"] == "white"

# ✅ PvP alternation: wrong color move rejected
response = client.post("/game/move", json={
    "game_type": "checkers",
    "start": [2, 3],
    "end": [3, 2]
})
print("POST /game/move wrong turn", response.status_code, response.json)
assert response.status_code == 400
assert "error" in response.json

# ✅ POST /game/timeout-turn PvP timeout switches to black
reset_games()
response = client.post("/game/timeout-turn", json={
    "game_type": "checkers",
    "ai": False
})
print("POST /game/timeout-turn pvp", response.status_code, response.json)
assert response.status_code == 200
assert response.json["turn"] == "black"
assert "timeout_move" in response.json

# ✅ POST /game/timeout-turn with AI should include AI move and return to white
reset_games()
response = client.post("/game/timeout-turn", json={
    "game_type": "checkers",
    "ai": True,
    "ai_difficulty": "greedy"
})
print("POST /game/timeout-turn + ai", response.status_code, response.json)
assert response.status_code == 200
assert "timeout_move" in response.json
assert "ai_move" in response.json
assert response.json["turn"] == "white"

# ✅ POST /game/move with AI
reset_games()
response = client.post("/game/move", json={
    "game_type": "checkers",
    "start": [5, 0],
    "end": [4, 1],
    "ai": True,
    "ai_difficulty": "greedy"
})
print("POST /game/move + ai", response.status_code, response.json)
assert response.status_code == 200
assert "ai_move" in response.json

print("all route tests passed!")
