"""
Eric Chhun
Game routes for Chess and Checkers web app.
Handles:
- Board state retrieval
- Player moves
- Optional AI response moves
"""

from flask import Blueprint, jsonify, request, render_template, session
from utils.game_logic import GameLogic

game_bp = Blueprint("game_bp", __name__)

# In-memory game instances (single shared game per type for now)
games = {
    "checkers": GameLogic("checkers"),
    "chess": GameLogic("chess"),
}


def _parse_int(raw_value, default=0):
    try:
        return int(raw_value)
    except (TypeError, ValueError):
        return default

# A function to format duration in seconds into a MM:SS string for display on the results page
def _format_duration(seconds):
    """"
        Convert a duration in seconds to a MM:SS format string.
        This is used to display the total game duration on the results page
        return a string in the format of minutes and seconds, ensuring that seconds 
        is always non-negative and properly formatted with leading zeros if needed.
        
    """
    # Ensure seconds is non-negative before formatting and 
    # calculate minutes and remaining seconds for display
    seconds = max(0, seconds)
    minutes = seconds // 60
    remaining = seconds % 60
    return f"{minutes:02d}:{remaining:02d}"


@game_bp.route("/ai", methods=["GET"])
def ai_game():
    """Render the Player vs AI game screen."""
    username = session.get("username", "Player")
    game_type = request.args.get("game", "checkers").lower()
    if game_type not in ["checkers", "chess"]:
        game_type = "checkers"
    # Start each AI page load with a fresh in-memory game state.
    games[game_type] = GameLogic(game_type)
    return render_template("game_ai.html", username=username, game_type=game_type)


@game_bp.route("/pvp", methods=["GET"])
def pvp_game():
    """Render the local Player vs Player game screen."""
    username = session.get("username", "Player")
    game_type = request.args.get("game", "checkers").lower()
    if game_type not in ["checkers", "chess"]:
        game_type = "checkers"
    # Start each PvP page load with a fresh in-memory game state.
    games[game_type] = GameLogic(game_type)
    return render_template("game_pvp.html", username=username, game_type=game_type)


@game_bp.route("/win", methods=["GET"])
def win_page():
    """Render post-game results page for AI and PvP games."""
    username = session.get("username", "Player")
    game_type = request.args.get("game", "checkers").lower()
    if game_type not in ["checkers", "chess"]:
        game_type = "checkers"

    mode = request.args.get("mode", "ai").lower()
    if mode not in ["ai", "pvp"]:
        mode = "ai"

    winner = request.args.get("winner", "white").lower()
    if winner not in ["white", "black"]:
        winner = "white"

    winner_label = "White" if winner == "white" else "Black"
    winner_name = username if (mode == "ai" and winner == "white") else ("AI" if mode == "ai" else f"{winner_label} Player")

    outcome = request.args.get("outcome", "").lower()
    if outcome not in ["victory", "defeat"]:
        if mode == "ai":
            outcome = "victory" if winner == "white" else "defeat"
        else:
            outcome = "victory"

    reason = request.args.get("reason")
    if not reason:
        reason = "by checkmate" if game_type == "chess" else "by capturing all opponent pieces"

    moves = max(0, _parse_int(request.args.get("moves"), 0))
    duration_seconds = max(0, _parse_int(request.args.get("duration"), 0))
    duration_display = _format_duration(duration_seconds)

    rating_delta_raw = request.args.get("rating")
    if rating_delta_raw is None:
        rating_delta = "+34" if outcome == "victory" else "-20"
    else:
        rating_delta = str(rating_delta_raw)

    if outcome == "defeat":
        title = "Defeat"
        subtitle = f"{winner_name} won the match {reason}"
    elif mode == "pvp":
        title = f"{winner_label} Wins!"
        subtitle = f"{winner_name} won the match {reason}"
    else:
        title = "Victory!"
        subtitle = f"Congratulations, you won the match {reason}"

    return render_template(
        "win.html",
        username=username,
        game_type=game_type,
        mode=mode,
        winner=winner,
        winner_label=winner_label,
        winner_name=winner_name,
        outcome=outcome,
        title=title,
        subtitle=subtitle,
        moves=moves,
        duration_seconds=duration_seconds,
        duration_display=duration_display,
        rating_delta=rating_delta
    )


@game_bp.route("/game", methods=["GET"])
def get_board():
    """Return current board state. Use ?type=chess or ?type=checkers"""
    game_type = request.args.get("type", "checkers").lower()

    if game_type not in games:
        return jsonify({"error": "Invalid game type. Use 'chess' or 'checkers'."}), 400

    game = games[game_type]
    return jsonify({
        "game_type": game_type,
        "board": game.board,
        "turn": game.turn,
        "winner": game.winner
    })

# Route to handle player moves in both AI and PVP modes.
@game_bp.route("/move", methods=["POST"])
def move_piece():
    """
        Move a piece in the specified game type.
        Expects JSON body with:
        - game_type: "chess" or "checkers"
        - start: [row, col]
        - end: [row, col]
        - ai (optional): true to enable AI response in PvE mode
        - ai_difficulty (optional): "minimax" or "random" for AI move
        - ai_depth (optional): integer depth for minimax AI

    """
    data = request.get_json() or {}
    game_type = data.get("game_type", "checkers").lower()
    ai_enabled = bool(data.get("ai"))
    ai_difficulty = str(data.get("ai_difficulty", "minimax")).lower()
    ai_depth_raw = data.get("ai_depth", 2)
    try:
        ai_depth = int(ai_depth_raw)
    except (TypeError, ValueError):
        ai_depth = 2

    if game_type not in games:
        return jsonify({"error": "Invalid game type."}), 400

    if "start" not in data or "end" not in data:
        return jsonify({"error": "Missing start or end positions."}), 400

    start = tuple(data.get("start"))
    end = tuple(data.get("end"))

    game = games[game_type]
    result = game.move_piece(start, end)
    if "error" in result:
        return jsonify(result), 400

    response = {
        "player_move": result,
        "board": game.board,
        "turn": game.turn,
        "winner": game.winner
    }

    if ai_enabled and not game.winner:
        ai_result = game.make_ai_move(difficulty=ai_difficulty, depth=ai_depth)
        response["ai_move"] = ai_result
        response["ai_difficulty"] = ai_result.get("ai_difficulty", ai_difficulty)
        response["board"] = game.board
        response["turn"] = game.turn
        response["winner"] = game.winner

    return jsonify(response)


@game_bp.route("/timeout-turn", methods=["POST"])
def timeout_turn():
    """Skip the current turn when a player's timer expires."""
    data = request.get_json() or {}
    game_type = data.get("game_type", "checkers").lower()
    ai_enabled = bool(data.get("ai"))
    ai_difficulty = str(data.get("ai_difficulty", "minimax")).lower()
    ai_depth_raw = data.get("ai_depth", 2)
    try:
        ai_depth = int(ai_depth_raw)
    except (TypeError, ValueError):
        ai_depth = 2

    if game_type not in games:
        return jsonify({"error": "Invalid game type."}), 400

    game = games[game_type]
    timeout_result = game.timeout_turn()
    if "error" in timeout_result:
        return jsonify(timeout_result), 400

    response = {
        "timeout_move": timeout_result,
        "board": game.board,
        "turn": game.turn,
        "winner": game.winner
    }

    # In PvE mode, if timeout hands turn to black (AI), let AI respond immediately.
    if ai_enabled and game.turn == "black" and not game.winner:
        ai_result = game.make_ai_move(difficulty=ai_difficulty, depth=ai_depth)
        response["ai_move"] = ai_result
        response["ai_difficulty"] = ai_result.get("ai_difficulty", ai_difficulty)
        response["board"] = game.board
        response["turn"] = game.turn
        response["winner"] = game.winner

    return jsonify(response)
