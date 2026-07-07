"""Persistent leaderboard storage.

The scores file is resolved to a fixed, absolute location so results land in the
same place regardless of the current working directory (and next to the binary
when the game is frozen into an executable).
"""

import json
import sys
from pathlib import Path


def _scores_path():
    if getattr(sys, "frozen", False):  # running from a PyInstaller bundle
        base = Path(sys.executable).resolve().parent
    else:
        base = Path(__file__).resolve().parent.parent  # the MemoryMaze/ folder
    return base / "scores.json"


SCORES_FILE = _scores_path()


def load_scores():
    """Return the list of recorded games, or an empty list if none/corrupt."""
    if not SCORES_FILE.exists():
        return []
    try:
        with open(SCORES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_score(player, winner, time_taken, penalty):
    scores = load_scores()
    scores.append({
        "player": player,
        "winner": winner,
        "time": time_taken,
        "penalty": penalty,
    })
    with open(SCORES_FILE, "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=4)
