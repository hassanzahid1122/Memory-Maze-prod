"""Persistent leaderboard: storage, scoring formula and ranking helpers."""

from . import config, storage

SCORES_FILE = "scores.json"


def compute_score(difficulty_key, winner, time_taken, penalty):
    """Points reward finishing fast; losing to the AI still earns a fraction."""
    base = config.DIFFICULTIES[difficulty_key].score_base
    points = base - time_taken * 8 - penalty * 20
    if winner != "PLAYER":
        points //= 3
    return max(50, int(points))


def load_scores():
    """Return the raw list of recorded games (oldest first)."""
    data = storage.load_json(SCORES_FILE, [])
    return data if isinstance(data, list) else []


def save_score(player, winner, time_taken, penalty, difficulty="MEDIUM"):
    scores = load_scores()
    scores.append({
        "player": player,
        "winner": winner,
        "time": time_taken,
        "penalty": penalty,
        "difficulty": difficulty,
        "score": compute_score(difficulty, winner, time_taken, penalty),
    })
    storage.save_json(SCORES_FILE, scores)


def _score_of(entry):
    return entry.get("score", 0)


def top_scores(limit=config.LEADERBOARD_LIMIT):
    """Highest-scoring games first."""
    return sorted(load_scores(), key=_score_of, reverse=True)[:limit]


def best_score(difficulty_key=None):
    """The single best score overall, or for one difficulty."""
    scores = load_scores()
    if difficulty_key:
        scores = [s for s in scores if s.get("difficulty") == difficulty_key]
    return max((_score_of(s) for s in scores), default=0)
