"""Collectable power-ups that alter the player's or the AI's speed."""

import math
import random

import pygame

from . import ai as ai_module
from . import audio, config, effects

SPEED = "SPEED"
SLOW_AI = "SLOW_AI"
FREEZE = "FREEZE"
REVEAL = "REVEAL"
TELEPORT = "TELEPORT"
# Common speed power-ups are weighted more heavily than the rarer utilities.
SPAWN_POOL = [SPEED, SPEED, SLOW_AI, SLOW_AI, FREEZE, FREEZE, REVEAL, TELEPORT]


class PowerUp:
    __slots__ = ("row", "col", "type", "active")

    def __init__(self, row, col, type_):
        self.row = row
        self.col = col
        self.type = type_
        self.active = True


_icon_fonts = {}


def _get_icon_font(cell_size):
    size = max(10, cell_size // 2)
    font = _icon_fonts.get(size)
    if font is None:
        font = pygame.font.SysFont("arial", size, bold=True)
        _icon_fonts[size] = font
    return font


class PowerUpManager:
    def __init__(self, maze):
        self.maze = maze
        self.powerups = self._spawn()

    def _spawn(self):
        """Scatter power-ups on random interior cells."""
        powerups = []
        for _ in range(config.POWERUP_COUNT):
            r = random.randint(1, self.maze.rows - 2)
            c = random.randint(1, self.maze.cols - 2)
            powerups.append(PowerUp(r, c, random.choice(SPAWN_POOL)))
        return powerups

    def update(self, player, ai):
        """Apply the effect of any power-up the player is standing on."""
        for p in self.powerups:
            if not p.active or (player.row, player.col) != (p.row, p.col):
                continue

            if p.type == SPEED:
                player.move_delay = max(1, player.move_delay - config.SPEED_BOOST)
            elif p.type == SLOW_AI:
                ai.move_delay += config.SLOW_AI_AMOUNT
            elif p.type == FREEZE:
                ai.freeze_time = config.FREEZE_DURATION
            elif p.type == REVEAL:
                self.maze.reveal_time = config.REVEAL_FRAMES
            elif p.type == TELEPORT:
                path = ai_module.shortest_path(self.maze, (player.row, player.col), self.maze.exit)
                player.teleport_along(path, config.TELEPORT_JUMP)

            p.active = False
            audio.play("pickup")

    def draw(self, screen, viewport, t=0.0):
        size = viewport.cell_size
        font = _get_icon_font(size)
        for p in self.powerups:
            if not p.active:
                continue

            color = config.Color.POWERUP[p.type]
            bob = math.sin(t * 3 + p.row + p.col) * size * 0.08
            base_x, base_y = viewport.center(p.row, p.col)
            cx = base_x
            cy = base_y + bob

            radius = size * 0.24 * (0.85 + 0.15 * effects.pulse(t, speed=4))
            effects.draw_glow(screen, color, (cx, cy), radius * 2.1)
            pygame.draw.circle(screen, color, (cx, cy), int(radius))

            icon = font.render(config.Color.POWERUP_ICON[p.type], True, (10, 12, 24))
            screen.blit(icon, (cx - icon.get_width() / 2, cy - icon.get_height() / 2))
