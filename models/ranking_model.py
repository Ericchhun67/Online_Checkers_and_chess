"""
Ranking/leaderboard model for the Chess and Checkers app.
Stores per-user stats for each game type (chess/checkers).
"""

from datetime import datetime

from utils.db_handler import db


class Ranking(db.Model):
    """Leaderboard stats for a user in a specific game type."""

    __tablename__ = "rankings"
    __table_args__ = (
        db.UniqueConstraint("user_id", "game_type", name="uq_rankings_user_game"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    game_type = db.Column(db.String(20), nullable=False)  # chess or checkers
    wins = db.Column(db.Integer, nullable=False, default=0)
    losses = db.Column(db.Integer, nullable=False, default=0)
    draws = db.Column(db.Integer, nullable=False, default=0)
    rating = db.Column(db.Integer, nullable=False, default=1200)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("rankings", lazy=True))

    @property
    def games_played(self):
        return self.wins + self.losses + self.draws

    def to_dict(self):
        """Return dictionary representation of the ranking."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "game_type": self.game_type,
            "wins": self.wins,
            "losses": self.losses,
            "draws": self.draws,
            "rating": self.rating,
            "games_played": self.games_played,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }

    def record_result(self, result, rating_delta=0):
        """Update stats for a game outcome and persist the change."""
        normalized = (result or "").strip().lower()
        if normalized not in {"win", "loss", "draw"}:
            raise ValueError("result must be 'win', 'loss', or 'draw'")

        if normalized == "win":
            self.wins += 1
        elif normalized == "loss":
            self.losses += 1
        else:
            self.draws += 1

        if rating_delta:
            self.rating = max(0, self.rating + int(rating_delta))

        self.last_updated = datetime.utcnow()
        db.session.commit()
        return self

    @staticmethod
    def get_or_create(user_id, game_type, default_rating=1200):
        """Fetch a ranking row or create a new one for the user + game type."""
        ranking = Ranking.query.filter_by(user_id=user_id, game_type=game_type).first()
        if ranking:
            return ranking

        ranking = Ranking(user_id=user_id, game_type=game_type, rating=default_rating)
        db.session.add(ranking)
        db.session.commit()
        return ranking

    def __repr__(self):
        return (
            f"<Ranking user_id={self.user_id} game_type={self.game_type} "
            f"wins={self.wins} losses={self.losses} draws={self.draws} rating={self.rating}>"
        )
