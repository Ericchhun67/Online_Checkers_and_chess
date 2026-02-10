""" 
    Unit tests for the game logic of the Chess and Checkers application.
    tests include:
        - Board initialization for both checkers and chess game
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.game_logic import GameLogic


def test_checkers_initialization():
    game = GameLogic("checkers")
    assert game.board[0][1] == "B"
    assert game.board[7][0] == "W"
    assert game.turn == "white"

def test_move_piece():
    game = GameLogic("checkers")
    result = game.move_piece((5, 0), (4, 1))
    assert result["message"] == "Move successful"
    assert game.turn == "black"

def test_chess_initialization():
    game = GameLogic("chess")
    assert game.board[0][0] == "BR"
    assert game.board[7][4] == "WK"

def test_checkers_promotion_to_king():
    game = GameLogic("checkers")
    game.board = [["" for _ in range(8)] for _ in range(8)]
    game.board[1][2] = "W"
    game.turn = "white"

    result = game.move_piece((1, 2), (0, 1))
    assert result["message"] == "Move successful"
    assert result["promoted"] is True
    assert game.board[0][1] == "WK"
    assert result["piece"] == "WK"

def test_checkers_king_can_move_backward():
    game = GameLogic("checkers")
    game.board = [["" for _ in range(8)] for _ in range(8)]
    game.board[3][2] = "WK"
    game.turn = "white"

    result = game.move_piece((3, 2), (4, 3))
    assert result["message"] == "Move successful"
    assert game.board[4][3] == "WK"

def test_checkers_ai_minimax_makes_move():
    game = GameLogic("checkers")
    result = game.make_ai_move(difficulty="minimax", depth=2)
    assert result["message"] == "Move successful"
    assert game.turn == "black"

def test_chess_ai_minimax_makes_move():
    game = GameLogic("chess")
    result = game.make_ai_move(difficulty="minimax", depth=2)
    assert result["message"] == "Move successful"
    assert game.turn == "black"

def test_timeout_turn_switches_turn():
    game = GameLogic("checkers")
    assert game.turn == "white"
    result = game.timeout_turn()
    assert result["message"] == "Turn skipped due to timeout"
    assert result["skipped_color"] == "white"
    assert game.turn == "black"

def test_check_winner():
    game = GameLogic("checkers")
    # Simulate all white pieces gone
    for r in range(8):
        for c in range(8):
            if "W" in game.board[r][c]:
                game.board[r][c] = ""
    assert game.check_winner() == "black"

if __name__ == '__main__':
    test_checkers_initialization()
    test_move_piece()
    test_chess_initialization()
    test_checkers_promotion_to_king()
    test_checkers_king_can_move_backward()
    test_checkers_ai_minimax_makes_move()
    test_chess_ai_minimax_makes_move()
    test_timeout_turn_switches_turn()
    test_check_winner()
    print("all tests passed!")
