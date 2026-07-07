"""Central configuration: display, colors, gameplay tunables and difficulty presets.

Every magic number that used to be scattered across the codebase lives here so the
game can be re-balanced or re-skinned from a single file.
"""

from dataclasses import dataclass

# --------------------------------------------------------------------------- #
# Display
# --------------------------------------------------------------------------- #
WIDTH = 900
HEIGHT = 700
CELL_SIZE = 30
FPS = 60
CAPTION = "Memory Maze"

# --------------------------------------------------------------------------- #
# Gameplay tunables
# --------------------------------------------------------------------------- #
PLAYER_MOVE_DELAY = 6      # frames the player must wait between moves
DEAD_END_PENALTY = 2       # seconds added when the player walks into a dead-end
MEMORY_HIDE_RATIO = 0.6    # fraction of cells hidden during the HIDDEN phase
POWERUP_COUNT = 6          # power-ups spawned per game
FREEZE_DURATION = 60       # frames the AI stays frozen after a FREEZE pickup
SPEED_BOOST = 2            # amount the player's move delay is reduced by
SLOW_AI_AMOUNT = 3         # amount added to the AI's move delay
MAX_USERNAME_LEN = 12
LEADERBOARD_LIMIT = 10     # rows shown on the leaderboard screen


@dataclass(frozen=True)
class Difficulty:
    """A single difficulty preset."""

    name: str
    size: int              # maze is size x size cells
    ai_move_delay: int     # lower is faster
    reveal_seconds: int    # length of each memory (visible/hidden) phase


DIFFICULTIES = {
    "EASY": Difficulty("EASY", size=12, ai_move_delay=12, reveal_seconds=8),
    "MEDIUM": Difficulty("MEDIUM", size=18, ai_move_delay=9, reveal_seconds=6),
    "HARD": Difficulty("HARD", size=25, ai_move_delay=7, reveal_seconds=4),
}
DEFAULT_DIFFICULTY = "MEDIUM"


# --------------------------------------------------------------------------- #
# Colors
# --------------------------------------------------------------------------- #
class Color:
    BG = (10, 10, 25)
    WHITE = (255, 255, 255)
    WALL = (200, 200, 200)
    HIDDEN_CELL = (12, 12, 20)

    ACCENT = (0, 220, 255)
    TITLE_GOLD = (255, 215, 0)
    HINT = (180, 180, 180)

    START = (0, 255, 0)
    EXIT = (255, 0, 0)
    PLAYER = (0, 180, 255)
    AI_BODY = (255, 80, 80)
    AI_GLOW = (255, 160, 160)

    INPUT_BOX = (40, 40, 70)
    BTN = (60, 60, 120)
    BTN_HOVER = (0, 160, 255)

    POWERUP = {
        "SPEED": (0, 255, 0),
        "SLOW_AI": (255, 165, 0),
        "FREEZE": (0, 200, 255),
    }
