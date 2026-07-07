"""Collectable power-ups that alter the player's or the AI's speed."""

import random

import pygame

from . import config

SPEED = "SPEED"
SLOW_AI = "SLOW_AI"
FREEZE = "FREEZE"
TYPES = (SPEED, SLOW_AI, FREEZE)


class PowerUp:
    __slots__ = ("row", "col", "type", "active")

    def __init__(self, row, col, type_):
        self.row = row
        self.col = col
        self.type = type_
        self.active = True


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
            powerups.append(PowerUp(r, c, random.choice(TYPES)))
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

            p.active = False

    def draw(self, screen):
        size = config.CELL_SIZE
        for p in self.powerups:
            if not p.active:
                continue
            x = p.col * size + size // 2
            y = p.row * size + size // 2
            pygame.draw.circle(screen, config.Color.POWERUP[p.type], (x, y), size // 4)
