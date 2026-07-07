"""The human-controlled player."""

from collections import deque

import pygame

from . import config, effects
from .maze import TOP, RIGHT, BOTTOM, LEFT

# Each scheme maps a key -> (wall that must be open, row delta, col delta).
CONTROL_SCHEMES = {
    "ARROWS": {
        pygame.K_LEFT: (LEFT, 0, -1),
        pygame.K_RIGHT: (RIGHT, 0, 1),
        pygame.K_UP: (TOP, -1, 0),
        pygame.K_DOWN: (BOTTOM, 1, 0),
    },
    "WASD": {
        pygame.K_a: (LEFT, 0, -1),
        pygame.K_d: (RIGHT, 0, 1),
        pygame.K_w: (TOP, -1, 0),
        pygame.K_s: (BOTTOM, 1, 0),
    },
}


class Player:
    def __init__(self, start, controls="ARROWS"):
        self.row, self.col = start
        self.move_delay = 0        # frames remaining before the next move is allowed
        self.penalty_time = 0      # seconds added for entering dead-ends
        self.moves = CONTROL_SCHEMES.get(controls, CONTROL_SCHEMES["ARROWS"])

        self.render_x = None       # pixel position (lazily set on first draw)
        self.render_y = None
        self.trail = deque(maxlen=9)

    def handle_input(self, keys, maze):
        """Move at most one cell. Returns True if the player actually moved."""
        if self.move_delay > 0:
            self.move_delay -= 1
            return False

        cell = maze.cell(self.row, self.col)
        if cell is None:
            return False

        for key, (wall, dr, dc) in self.moves.items():
            if keys[key] and not cell.walls[wall]:
                self.row += dr
                self.col += dc
                self.move_delay = config.PLAYER_MOVE_DELAY
                self._apply_dead_end_penalty(maze)
                return True
        return False

    def teleport_along(self, path, jump):
        """Jump forward up to ``jump`` cells along a precomputed route."""
        if not path:
            return
        target = path[min(jump, len(path)) - 1]
        self.row, self.col = target

    def _apply_dead_end_penalty(self, maze):
        cell = maze.cell(self.row, self.col)
        open_paths = sum(not wall for wall in cell.walls)
        if open_paths <= 1:
            self.penalty_time += config.DEAD_END_PENALTY

    def draw(self, screen, viewport, t=0.0):
        size = viewport.cell_size
        target_x, target_y = viewport.center(self.row, self.col)
        if self.render_x is None:
            self.render_x, self.render_y = target_x, target_y
        self.render_x = effects.ease(self.render_x, target_x, 0.25)
        self.render_y = effects.ease(self.render_y, target_y, 0.25)
        center = (self.render_x, self.render_y)

        if effects.enabled():
            self.trail.append(center)
            for i, (tx, ty) in enumerate(self.trail):
                f = (i + 1) / len(self.trail)
                effects.draw_alpha_circle(screen, config.Color.PLAYER, (tx, ty),
                                          size * 0.16 * f, int(70 * f))

        effects.draw_glow(screen, config.Color.PLAYER_GLOW, center, size * 0.55)
        pygame.draw.circle(screen, config.Color.PLAYER, center, int(size * 0.28))
        pygame.draw.circle(screen, config.Color.WHITE, center, int(size * 0.10))
