"""Selectable color themes.

A theme is just a set of overrides applied onto ``config.Color`` at runtime, so
the rest of the code keeps reading ``config.Color.X`` and never needs to know a
theme system exists.
"""

from . import config

THEMES = {
    "NEON": {
        "BG_TOP": (18, 20, 44), "BG_BOTTOM": (6, 6, 16),
        "WALL": (150, 175, 230), "FLOOR_BORDER": (44, 60, 120), "FOG": (26, 30, 62),
        "ACCENT": (0, 220, 255), "ACCENT_SOFT": (120, 235, 255), "TITLE_GOLD": (255, 215, 0),
        "START": (60, 230, 130), "EXIT": (255, 90, 90),
        "PLAYER": (70, 195, 255), "PLAYER_GLOW": (30, 140, 240),
        "AI_BODY": (255, 95, 95), "AI_GLOW": (255, 70, 70),
        "INPUT_BORDER": (0, 185, 240), "BTN": (44, 48, 96),
        "BTN_HOVER": (0, 150, 240), "BTN_BORDER": (92, 130, 230), "PANEL_BORDER": (62, 82, 165),
    },
    "AMBER": {
        "BG_TOP": (40, 26, 14), "BG_BOTTOM": (16, 9, 4),
        "WALL": (235, 195, 140), "FLOOR_BORDER": (120, 78, 34), "FOG": (58, 40, 22),
        "ACCENT": (255, 175, 45), "ACCENT_SOFT": (255, 205, 120), "TITLE_GOLD": (255, 225, 130),
        "START": (150, 220, 90), "EXIT": (255, 80, 60),
        "PLAYER": (255, 190, 70), "PLAYER_GLOW": (220, 130, 30),
        "AI_BODY": (235, 70, 60), "AI_GLOW": (220, 50, 40),
        "INPUT_BORDER": (255, 170, 60), "BTN": (92, 60, 30),
        "BTN_HOVER": (210, 130, 40), "BTN_BORDER": (230, 160, 80), "PANEL_BORDER": (150, 95, 45),
    },
    "MONO": {
        "BG_TOP": (30, 32, 38), "BG_BOTTOM": (10, 11, 14),
        "WALL": (205, 210, 220), "FLOOR_BORDER": (80, 84, 96), "FOG": (40, 42, 50),
        "ACCENT": (225, 230, 240), "ACCENT_SOFT": (180, 186, 200), "TITLE_GOLD": (235, 238, 245),
        "START": (170, 220, 180), "EXIT": (230, 130, 130),
        "PLAYER": (235, 240, 250), "PLAYER_GLOW": (150, 156, 170),
        "AI_BODY": (150, 156, 170), "AI_GLOW": (110, 116, 130),
        "INPUT_BORDER": (170, 176, 190), "BTN": (54, 58, 68),
        "BTN_HOVER": (120, 126, 140), "BTN_BORDER": (140, 146, 160), "PANEL_BORDER": (90, 96, 110),
    },
}


def apply(name):
    """Apply a theme onto ``config.Color`` (falls back to NEON if unknown)."""
    palette = THEMES.get(name, THEMES["NEON"])
    for key, value in palette.items():
        setattr(config.Color, key, value)
