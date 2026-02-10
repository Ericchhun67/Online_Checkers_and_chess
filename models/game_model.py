"""
    Game info + moves + results

"""


from utils.db_handler import db
from datetime import datetime
import json


class GameModel(db.Model):
    __tablename__ = "Games"
    # columns to store game information and set state to the database
    id = db.Column(db.Integer, primary_key=True)
    # unique room name for each game session
    room_name = db.Column(db.String(80), unique=True, nullable=False)
    game_type = db.Column(db.String(20), nullable=False)  # chess or checkers
    board_state = db.Column(db.Text, nullable=False)  # serialized JSON board
    turn = db.Column(db.String(10), nullable=False)
    last_move = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    
    def to_dict(self):
        """Return dictionary representation of a game."""
        return {
            "id": self.id,
            "room_name": self.room_name,
            "game_type": self.game_type,
            "board_state": json.loads(self.board_state),
            "turn": self.turn,
            "last_move": self.last_move,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    def update_state(self, new_board, turn, last_move=None):
        """Update the board and save new move."""
        self.board_state = json.dumps(new_board)
        self.turn = turn
        if last_move:
            self.last_move = last_move
        db.session.commit()

    @staticmethod
    def create_new(room_name, game_type, initial_board, turn="white"):
        """Create a new game instance and store in the database."""
        game = GameModel(
            room_name=room_name,
            game_type=game_type,
            board_state=json.dumps(initial_board),
            turn=turn
        )
        db.session.add(game)
        db.session.commit()
        return game
    
    
