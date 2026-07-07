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
CELL_SIZE = 30             # nominal cell size; the play viewport auto-scales per maze
HUD_HEIGHT = 56            # reserved bar at the top of the play screen
FPS = 60
CAPTION = "Memory Maze"

# --------------------------------------------------------------------------- #
# Gameplay tunables
# --------------------------------------------------------------------------- #
PLAYER_MOVE_DELAY = 6      # frames the player must wait between moves
DEAD_END_PENALTY = 2       # seconds added when the player walks into a dead-end
MEMORY_HIDE_RATIO = 0.6    # fraction of cells hidden during the HIDDEN phase
POWERUP_COUNT = 7          # power-ups spawned per game
FREEZE_DURATION = 60       # frames the AI stays frozen after a FREEZE pickup
SPEED_BOOST = 2            # amount the player's move delay is reduced by
SLOW_AI_AMOUNT = 3         # amount added to the AI's move delay
REVEAL_FRAMES = FPS * 3    # frames REVEAL keeps the whole maze visible
TELEPORT_JUMP = 4          # cells TELEPORT moves you along your route to the exit
COUNTDOWN_SECONDS = 3      # "3-2-1-GO" before a round begins
MAX_USERNAME_LEN = 12
LEADERBOARD_LIMIT = 10     # rows shown on the leaderboard screen


@dataclass(frozen=True)
class Difficulty:
    """A single difficulty preset."""

    name: str
    size: int              # maze is size x size cells
    ai_move_delay: int     # lower is faster
    reveal_seconds: int    # length of each memory (visible/hidden) phase
    score_base: int        # starting points before time/penalty deductions


DIFFICULTIES = {
    "EASY": Difficulty("EASY", size=12, ai_move_delay=12, reveal_seconds=8, score_base=500),
    "MEDIUM": Difficulty("MEDIUM", size=18, ai_move_delay=9, reveal_seconds=6, score_base=800),
    "HARD": Difficulty("HARD", size=25, ai_move_delay=7, reveal_seconds=4, score_base=1200),
}
DEFAULT_DIFFICULTY = "MEDIUM"


# --------------------------------------------------------------------------- #
# Colors
# --------------------------------------------------------------------------- #
class Color:
    BG = (10, 10, 25)
    BG_TOP = (18, 20, 44)         # background gradient (top)
    BG_BOTTOM = (6, 6, 16)        # background gradient (bottom)
    WHITE = (245, 248, 255)
    STAR = (190, 205, 255)

    WALL = (150, 175, 230)
    FLOOR = (17, 19, 36)
    FLOOR_BORDER = (44, 60, 120)
    HIDDEN_CELL = (11, 12, 26)
    FOG = (26, 30, 62)

    ACCENT = (0, 220, 255)
    ACCENT_SOFT = (120, 235, 255)
    TITLE_GOLD = (255, 215, 0)
    HINT = (165, 178, 210)

    START = (60, 230, 130)
    EXIT = (255, 90, 90)
    PLAYER = (70, 195, 255)
    PLAYER_GLOW = (30, 140, 240)
    AI_BODY = (255, 95, 95)
    AI_GLOW = (255, 70, 70)
    FREEZE_TINT = (120, 210, 255)

    INPUT_BOX = (30, 32, 60)
    INPUT_BORDER = (0, 185, 240)
    BTN = (44, 48, 96)
    BTN_HOVER = (0, 150, 240)
    BTN_BORDER = (92, 130, 230)

    PANEL = (18, 20, 42)
    PANEL_BORDER = (62, 82, 165)

    POWERUP = {
        "SPEED": (60, 235, 120),
        "SLOW_AI": (255, 170, 40),
        "FREEZE": (0, 205, 255),
        "REVEAL": (190, 120, 255),
        "TELEPORT": (255, 110, 200),
    }
    POWERUP_ICON = {
        "SPEED": "S",
        "SLOW_AI": "A",
        "FREEZE": "F",
        "REVEAL": "R",
        "TELEPORT": "T",
    }

    CONFETTI = [
        (255, 90, 90), (60, 230, 130), (0, 205, 255),
        (255, 215, 0), (190, 120, 255), (255, 110, 200),
    ]
