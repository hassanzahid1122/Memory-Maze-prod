"""Shared JSON persistence helpers with a deterministic data location.

Data lands next to the package during development, or next to the executable
when the game is frozen with PyInstaller — never in a random working directory.
"""

import json
import sys
from pathlib import Path


def base_dir():
    if getattr(sys, "frozen", False):  # running from a PyInstaller bundle
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent  # the MemoryMaze/ folder


def path_for(filename):
    return base_dir() / filename


def load_json(filename, default):
    p = path_for(filename)
    if not p.exists():
        return default
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def save_json(filename, data):
    try:
        with open(path_for(filename), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except OSError:
        pass  # persistence is best-effort; never crash the game over it
