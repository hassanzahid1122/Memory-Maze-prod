"""The human-controlled player."""

import pygame

from . import config
from .maze import TOP, RIGHT, BOTTOM, LEFT

# Arrow key -> (wall that must be open, row delta, col delta)
_MOVES = {
    pygame.K_LEFT: (LEFT, 0, -1),
    pygame.K_RIGHT: (RIGHT, 0, 1),
    pygame.K_UP: (TOP, -1, 0),
    pygame.K_DOWN: (BOTTOM, 1, 0),
}


class Player:
    def __init__(self, start):
        self.row, self.col = start
        self.move_delay = 0        # frames remaining before the next move is allowed
        self.penalty_time = 0      # seconds added for entering dead-ends

    def handle_input(self, keys, maze):
        if self.move_delay > 0:
            self.move_delay -= 1
            return

        cell = maze.cell(self.row, self.col)
        if cell is None:
            return

        for key, (wall, dr, dc) in _MOVES.items():
            if keys[key] and not cell.walls[wall]:
                self.row += dr
                self.col += dc
                self.move_delay = config.PLAYER_MOVE_DELAY
                self._apply_dead_end_penalty(maze)
                return

    def _apply_dead_end_penalty(self, maze):
        cell = maze.cell(self.row, self.col)
        open_paths = sum(not wall for wall in cell.walls)
        if open_paths <= 1:
            self.penalty_time += config.DEAD_END_PENALTY

    def draw(self, screen):
        size = config.CELL_SIZE
        x = self.col * size + size // 4
        y = self.row * size + size // 4
        pygame.draw.rect(screen, config.Color.PLAYER, (x, y, size // 2, size // 2))
