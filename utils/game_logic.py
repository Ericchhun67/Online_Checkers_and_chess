""" 
Game logic utilities for Chess and Checkers app.
Handles the core game logic for Chess and Checkers.
- Board setup
- Move validation
- Turn management
- Win condition detection
"""

import random


class GameLogic:
    """ 
        psudo code:
            - Initialize game state (board, turn, winner)
            - Method to set up initial board based on game type
            - Method to get legal moves for a piece
            - Method to move a piece with validation
            - Method to check for win conditions
            - Method to handle AI moves
    
    """
    # Function to initialize the game logic with a specified game type
    def __init__(self, game_type="checkers"):
        # store the game type (checkers or chess)
        self.game_type = game_type
        # initialize the board based on the game type and set the turn to white
        # and black and winner to none
        self.board = self.initialize_board()
        self.turn = "white" # white starts first 
        self.winner = None
        
    # function to initialize the board based on the game type
    def initialize_board(self):
        if self.game_type == "checkers":
            return self._init_checkers_board()
        elif self.game_type == "chess":
            return self._init_chess_board()
        else:
            raise ValueError("invalid game type")
    
    
    def _init_checkers_board(self):
        """ 
            Set up a standard 8x8 checkers board with pieces in starting positions.
        """
        # Create an 8x8 board with empty strings
        board = [["" for _ in range(8)] for _ in range(8)]
        # loop to place black and white pieces
        for row in range(3):
            # loop through columns to place pieces on dark squares
            for col in range(8):
                # if the sum of row and col is odd, its a dark square
                if (row + col) % 2 == 1:
                    # create a board in a 2d list because its easier to manage
                    board[row][col] = "B"
        # loop through rows 
        for row in range(5, 8):
            for col in range(8):
                if (row + col) % 2 == 1:
                    board[row][col] = "W"
        # return the initialized board
        return board
    
    def _init_chess_board(self):
        """Set up standard chess layout."""
        pieces = ["R", "N", "B", "Q", "K", "B", "N", "R"]
        board = [] # create an empty board and then append the pieces in the correct positions
        board.append(["B" + p for p in pieces])
        board.append(["BP" for _ in range(8)])
        board.extend([["" for _ in range(8)] for _ in range(4)])
        board.append(["WP" for _ in range(8)])
        board.append(["W" + p for p in pieces])
        # return the initialized chess board
        return board
    
    def _in_bounds(self, row, col):
        return 0 <= row < 8 and 0 <= col < 8

    def _piece_color(self, piece):
        # if the piece is empty, return none
        if not piece:
            return None
        if piece.startswith("W"):
            return "white"
        if piece.startswith("B"):
            return "black"
        return None

    def _opponent(self, color):
        # return the opposite color
        return "black" if color == "white" else "white"

    def _clone(self):
        """" 
            psudo code:
                - Create a new GameLogic instance with the same game type
                - Deep copy the board state to the new instance
                - Copy the current turn and winner status to the new instance
                - Return the new instance as a clone of the current game state
        """
        clone = GameLogic(self.game_type)
        clone.board = [row[:] for row in self.board]
        clone.turn = self.turn
        clone.winner = self.winner
        return clone

    def _checkers_moves_for_piece(self, start, piece):
        """ 
            - Get legal moves for a checkers piece at a given position.
            - Handles normal moves and captures.
            - For kings, allows backward moves and forward moves
            - for regular pieces, only allows forward moves based on color
            - Returns a list of legal moves in the format 
        """
        # Get the row and column from the start position
        r, c = start
        # Determine the color of the piece and if it's a king or not
        color = self._piece_color(piece)
        # check the length og the piece string to determine if its a king
        is_king = len(piece) > 1 and piece[1] == "K"
        # if its a king, it can move in both directions, otherwise normal pieces
        # can only move forward (up down poosition based on color)
        if is_king:
            directions = (-1, 1)
        else:
            directions = (-1,) if color == "white" else (1,)
        moves = [] # set up an empty list to store legal moves
        # nested loop through possible move directions
        for dr in directions:
            for dc in (-1, 1):
                # Calculate the target position for a normal move
                r1, c1 = r + dr, c + dc
                if self._in_bounds(r1, c1) and not self.board[r1][c1]:
                    moves.append((start, (r1, c1)))

                r2, c2 = r + (2 * dr), c + (2 * dc)
                if not self._in_bounds(r2, c2):
                    continue
                middle = self.board[r + dr][c + dc]
                if middle and self._piece_color(middle) == self._opponent(color) and not self.board[r2][c2]:
                    moves.append((start, (r2, c2)))

        return moves

    def _add_slide_moves(self, start, color, deltas, moves):
        r, c = start
        for dr, dc in deltas:
            r1, c1 = r + dr, c + dc
            while self._in_bounds(r1, c1):
                target = self.board[r1][c1]
                if not target:
                    moves.append((start, (r1, c1)))
                else:
                    if self._piece_color(target) != color:
                        moves.append((start, (r1, c1)))
                    break
                r1 += dr
                c1 += dc

    def _chess_moves_for_piece(self, start, piece):
        r, c = start
        color = self._piece_color(piece)
        piece_type = piece[1]
        moves = []

        if piece_type == "P":
            direction = -1 if color == "white" else 1
            start_row = 6 if color == "white" else 1
            r1 = r + direction
            if self._in_bounds(r1, c) and not self.board[r1][c]:
                moves.append((start, (r1, c)))
                r2 = r + (2 * direction)
                if r == start_row and self._in_bounds(r2, c) and not self.board[r2][c]:
                    moves.append((start, (r2, c)))
            for dc in (-1, 1):
                rc, cc = r + direction, c + dc
                if not self._in_bounds(rc, cc):
                    continue
                target = self.board[rc][cc]
                if target and self._piece_color(target) == self._opponent(color):
                    moves.append((start, (rc, cc)))

        elif piece_type == "N":
            jumps = [
                (-2, -1), (-2, 1),
                (-1, -2), (-1, 2),
                (1, -2), (1, 2),
                (2, -1), (2, 1),
            ]
            for dr, dc in jumps:
                r1, c1 = r + dr, c + dc
                if not self._in_bounds(r1, c1):
                    continue
                target = self.board[r1][c1]
                if not target or self._piece_color(target) != color:
                    moves.append((start, (r1, c1)))

        elif piece_type == "B":
            self._add_slide_moves(start, color, [(-1, -1), (-1, 1), (1, -1), (1, 1)], moves)

        elif piece_type == "R":
            self._add_slide_moves(start, color, [(-1, 0), (1, 0), (0, -1), (0, 1)], moves)

        elif piece_type == "Q":
            self._add_slide_moves(
                start,
                color,
                [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)],
                moves
            )

        elif piece_type == "K":
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    r1, c1 = r + dr, c + dc
                    if not self._in_bounds(r1, c1):
                        continue
                    target = self.board[r1][c1]
                    if not target or self._piece_color(target) != color:
                        moves.append((start, (r1, c1)))

        return moves

    def _legal_moves_for_piece(self, start):
        r, c = start
        if not self._in_bounds(r, c):
            return []
        piece = self.board[r][c]
        if not piece:
            return []
        if self.game_type == "checkers":
            return self._checkers_moves_for_piece(start, piece)
        if self.game_type == "chess":
            return self._chess_moves_for_piece(start, piece)
        return []

    def get_legal_moves(self, color=None):
        color = color or self.turn
        moves = []
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if not piece:
                    continue
                if self._piece_color(piece) != color:
                    continue
                moves.extend(self._legal_moves_for_piece((r, c)))
        return moves

    def _is_capture_move(self, board, start, end, piece):
        r1, c1 = start
        r2, c2 = end
        color = self._piece_color(piece)
        if self.game_type == "checkers":
            if abs(r2 - r1) == 2 and abs(c2 - c1) == 2:
                mid_r = (r1 + r2) // 2
                mid_c = (c1 + c2) // 2
                middle = board[mid_r][mid_c]
                return middle and self._piece_color(middle) == self._opponent(color)
            return False
        target = board[r2][c2]
        return bool(target) and self._piece_color(target) == self._opponent(color)

    def _evaluate_board(self, board, perspective):
        if self.game_type == "checkers":
            weights = {"P": 1, "K": 2}
        else:
            weights = {"P": 1, "N": 3, "B": 3, "R": 5, "Q": 9, "K": 200}

        score = 0
        for row in board:
            for piece in row:
                if not piece:
                    continue
                color = self._piece_color(piece)
                piece_type = piece[1] if len(piece) > 1 else "P"
                value = weights.get(piece_type, 1)
                score += value if color == perspective else -value
        return score

    def _minimax(self, depth, maximizing_color, alpha, beta):
        INF = 10**9
        if self.winner:
            return INF if self.winner == maximizing_color else -INF
        if depth == 0:
            return self._evaluate_board(self.board, maximizing_color)

        legal_moves = self.get_legal_moves(self.turn)
        if not legal_moves:
            return -INF if self.turn == maximizing_color else INF

        is_maximizing = self.turn == maximizing_color
        if is_maximizing:
            best = -INF
            for start, end in legal_moves:
                sim = self._clone()
                sim.move_piece(start, end, enforce_turn=True)
                best = max(best, sim._minimax(depth - 1, maximizing_color, alpha, beta))
                alpha = max(alpha, best)
                if beta <= alpha:
                    break
            return best

        best = INF
        for start, end in legal_moves:
            sim = self._clone()
            sim.move_piece(start, end, enforce_turn=True)
            best = min(best, sim._minimax(depth - 1, maximizing_color, alpha, beta))
            beta = min(beta, best)
            if beta <= alpha:
                break
        return best

    def _select_ai_move(self, difficulty="random", depth=2):
        legal_moves = self.get_legal_moves(self.turn)
        if not legal_moves:
            return None

        if difficulty == "greedy":
            capture_moves = []
            for start, end in legal_moves:
                piece = self.board[start[0]][start[1]]
                if self._is_capture_move(self.board, start, end, piece):
                    capture_moves.append((start, end))
            return random.choice(capture_moves or legal_moves)

        if difficulty == "minimax":
            best_score = -10**9
            best_moves = []
            for start, end in legal_moves:
                sim = self._clone()
                sim.move_piece(start, end, enforce_turn=True)
                score = sim._minimax(depth - 1, self.turn, -10**9, 10**9)
                if score > best_score:
                    best_score = score
                    best_moves = [(start, end)]
                elif score == best_score:
                    best_moves.append((start, end))
            return random.choice(best_moves or legal_moves)

        return random.choice(legal_moves)

    def move_piece(self, start, end, enforce_turn=True):
        """Move a piece and handle basic validation."""
        r1, c1 = start
        r2, c2 = end

        if not self._in_bounds(r1, c1) or not self._in_bounds(r2, c2):
            return {"error": "Move out of bounds"}

        piece = self.board[r1][c1]
        if not piece:
            return {"error": "No piece at start"}
        if self.winner:
            return {"error": "Game already over"}

        color = self._piece_color(piece)
        if enforce_turn and color != self.turn:
            return {"error": f"It is {self.turn}'s turn"}

        legal_moves = self._legal_moves_for_piece((r1, c1))
        if (start, end) not in legal_moves:
            return {"error": "Illegal move"}

        captured = False
        if self.game_type == "checkers" and abs(r2 - r1) == 2 and abs(c2 - c1) == 2:
            mid_r = (r1 + r2) // 2
            mid_c = (c1 + c2) // 2
            if self.board[mid_r][mid_c]:
                self.board[mid_r][mid_c] = ""
                captured = True

        self.board[r2][c2], self.board[r1][c1] = piece, ""

        promoted = False
        if self.game_type == "checkers":
            moved_piece = self.board[r2][c2]
            if moved_piece == "W" and r2 == 0:
                self.board[r2][c2] = "WK"
                promoted = True
            elif moved_piece == "B" and r2 == 7:
                self.board[r2][c2] = "BK"
                promoted = True

        moved_piece = self.board[r2][c2]
        winner = self.check_winner()
        if not winner:
            self.turn = "black" if self.turn == "white" else "white"

        return {
            "message": "Move successful",
            "piece": moved_piece,
            "start": start,
            "end": end,
            "captured": captured,
            "promoted": promoted,
            "next_turn": self.turn,
            "winner": winner
        }

    def timeout_turn(self):
        """Skip the current side's turn because its timer expired."""
        if self.winner:
            return {"error": "Game already over"}

        skipped_color = self.turn
        self.turn = self._opponent(self.turn)

        return {
            "message": "Turn skipped due to timeout",
            "skipped_color": skipped_color,
            "next_turn": self.turn,
            "winner": self.winner
        }

    def make_ai_move(self, difficulty="random", depth=2):
        """Pick a legal move for the current side to move."""
        if self.winner:
            return {"error": "Game already over"}

        if depth < 1:
            depth = 1
        if self.game_type == "chess":
            depth = min(depth, 2)
        else:
            depth = min(depth, 4)

        move = self._select_ai_move(difficulty=difficulty, depth=depth)
        if not move:
            self.winner = self._opponent(self.turn)
            return {"error": "No legal moves", "winner": self.winner}

        start, end = move
        result = self.move_piece(start, end, enforce_turn=True)
        result["ai_difficulty"] = difficulty
        return result

    def check_winner(self):
        """Basic win condition (simplified)."""
        white_pieces = sum(piece.startswith("W") for row in self.board for piece in row if piece)
        black_pieces = sum(piece.startswith("B") for row in self.board for piece in row if piece)
        if white_pieces == 0:
            self.winner = "black"
        elif black_pieces == 0:
            self.winner = "white"
        return self.winner

if __name__ == '__main__':
    game = GameLogic("checkers")
    for row in game.board:
        print(row)
