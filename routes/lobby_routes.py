# routes/lobby_routes.py
"""
Lobby routes for Chess and Checkers web app.
Handles:
- Listing active game rooms
- Creating and joining rooms
- Returning connected users
"""

from flask import Blueprint, jsonify, request, render_template, session
from utils.game_logic import GameLogic

# Blueprint setup
lobby_bp = Blueprint("lobby_bp", __name__)

# Temporary in-memory storage
active_rooms = {}
connected_users = set()


@lobby_bp.route("/", methods=["GET"])
def lobby_page():
    """Render the lobby page."""
    username = session.get("username", "Player")
    return render_template("lobby.html", username=username)


@lobby_bp.route("/rooms", methods=["GET"])
def get_rooms():
    """Return all active rooms."""
    return jsonify({"active_rooms": list(active_rooms.keys())})


@lobby_bp.route("/create-room", methods=["POST"])
def create_room():
    """Create a new game room."""
    data = request.get_json()
    room_name = data.get("room_name")
    game_type = data.get("game_type", "checkers")

    if room_name in active_rooms:
        return jsonify({"error": "Room already exists"}), 400

    active_rooms[room_name] = {
        "game": GameLogic(game_type),
        "players": []
    }

    return jsonify({"message": f"Room '{room_name}' created successfully!", "game_type": game_type}), 201


@lobby_bp.route("/join-room", methods=["POST"])
def join_room():
    """Add a player to an existing room."""
    data = request.get_json()
    username = data.get("username")
    room_name = data.get("room_name")

    if room_name not in active_rooms:
        return jsonify({"error": "Room not found"}), 404

    if username not in active_rooms[room_name]["players"]:
        active_rooms[room_name]["players"].append(username)
        connected_users.add(username)

    return jsonify({
        "message": f"{username} joined room '{room_name}'",
        "room": room_name,
        "players": active_rooms[room_name]["players"]
    }), 200


@lobby_bp.route("/users", methods=["GET"])
def get_users():
    """Return all connected users."""
    return jsonify({"connected_users": list(connected_users)})
