"""
Utilities for updating player rankings using a simple Elo system.
"""

from datetime import datetime

from utils.db_handler import db
from models.ranking_model import Ranking


DEFAULT_RATING = 1200


def normalize_result(result):
    """Normalize a result string into a score for player A."""
    normalized = (result or "").strip().lower()
    if normalized == "win":
        return 1.0
    if normalized == "loss":
        return 0.0
    if normalized == "draw":
        return 0.5
    raise ValueError("result must be 'win', 'loss', or 'draw'")


def expected_score(rating_a, rating_b):
    """Expected score for player A against player B."""
    return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))


def k_factor_for(games_played):
    """Determine K-factor based on number of games played."""
    if games_played < 30:
        return 40
    if games_played < 100:
        return 20
    return 10


def calculate_elo(rating_a, rating_b, score_a, k_factor):
    """Return new ratings for A and B using Elo."""
    expected_a = expected_score(rating_a, rating_b)
    expected_b = 1.0 - expected_a
    score_b = 1.0 - score_a

    new_rating_a = rating_a + k_factor * (score_a - expected_a)
    new_rating_b = rating_b + k_factor * (score_b - expected_b)

    return round(new_rating_a), round(new_rating_b)


def update_ranking_pair(player_ranking, opponent_ranking, result, k_factor=None):
    """Update two Ranking rows for a head-to-head result."""
    score_a = normalize_result(result)

    if k_factor is None:
        player_k = k_factor_for(player_ranking.games_played)
        opponent_k = k_factor_for(opponent_ranking.games_played)
        k_factor = max(player_k, opponent_k)

    new_rating_a, new_rating_b = calculate_elo(
        player_ranking.rating,
        opponent_ranking.rating,
        score_a,
        k_factor,
    )

    if score_a == 1.0:
        player_ranking.wins += 1
        opponent_ranking.losses += 1
    elif score_a == 0.0:
        player_ranking.losses += 1
        opponent_ranking.wins += 1
    else:
        player_ranking.draws += 1
        opponent_ranking.draws += 1

    player_ranking.rating = max(0, new_rating_a)
    opponent_ranking.rating = max(0, new_rating_b)

    now = datetime.utcnow()
    player_ranking.last_updated = now
    opponent_ranking.last_updated = now

    db.session.commit()

    return {
        "player_rating": player_ranking.rating,
        "opponent_rating": opponent_ranking.rating,
        "k_factor": k_factor,
        "score": score_a,
    }


def record_match(user_id, opponent_id, game_type, result, default_rating=DEFAULT_RATING, k_factor=None):
    """Get/create rankings and record a match result for two users."""
    player_ranking = Ranking.get_or_create(user_id, game_type, default_rating=default_rating)
    opponent_ranking = Ranking.get_or_create(opponent_id, game_type, default_rating=default_rating)
    return update_ranking_pair(player_ranking, opponent_ranking, result, k_factor=k_factor)
