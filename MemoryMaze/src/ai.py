"""The AI opponent: it solves the maze with A* and steps along the path."""

import heapq

import pygame

from . import config
from .maze import DIRECTIONS


class AIPlayer:
    def __init__(self, start, move_delay=config.DIFFICULTIES[config.DEFAULT_DIFFICULTY].ai_move_delay):
        self.row, self.col = start
        self.move_delay = move_delay
        self.tick = 0
        self.freeze_time = 0       # frames remaining frozen (from a FREEZE pickup)

        self.path = []
        self.index = 0

    def update(self, maze):
        if self.freeze_time > 0:
            self.freeze_time -= 1
            return

        if not self.path or self.index >= len(self.path):
            self.path = self._a_star(maze, (self.row, self.col), maze.exit)
            self.index = 0

        if not self.path:
            return

        self.tick += 1
        if self.tick < self.move_delay:
            return

        self.tick = 0
        self.row, self.col = self.path[self.index]
        self.index += 1

    @staticmethod
    def _a_star(maze, start, goal):
        """Return the shortest path from ``start`` to ``goal`` (excluding start)."""

        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                return _reconstruct(came_from, current)

            cell = maze.cell(*current)
            if not cell:
                continue

            for dr, dc, wall, _ in DIRECTIONS:
                if cell.walls[wall]:
                    continue

                neighbour = (current[0] + dr, current[1] + dc)
                if not maze.in_bounds(*neighbour):
                    continue

                tentative_g = g_score[current] + 1
                if tentative_g < g_score.get(neighbour, float("inf")):
                    g_score[neighbour] = tentative_g
                    came_from[neighbour] = current
                    heapq.heappush(open_set, (tentative_g + heuristic(neighbour, goal), neighbour))

        return []

    def draw(self, screen):
        size = config.CELL_SIZE
        x = self.col * size + size // 4
        y = self.row * size + size // 4
        pygame.draw.rect(screen, config.Color.AI_BODY, (x, y, size // 2, size // 2))

        center = (self.col * size + size // 2, self.row * size + size // 2)
        pygame.draw.circle(screen, config.Color.AI_GLOW, center, size // 6)


def _reconstruct(came_from, current):
    path = []
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path
