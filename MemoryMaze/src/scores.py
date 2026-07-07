import json
import os

FILE = "scores.json"


def load_scores():
    if not os.path.exists(FILE):
        return []

    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_score(player, winner, time_taken, penalty):

    data = load_scores()

    data.append({
        "player": player,
        "winner": winner,
        "time": time_taken,
        "penalty": penalty
    })

    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)