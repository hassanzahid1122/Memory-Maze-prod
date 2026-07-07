"""The AI opponent: it solves the maze with A* and steps along the path."""

import heapq
from collections import deque

import pygame

from . import config, effects
from .maze import DIRECTIONS


class AIPlayer:
    def __init__(self, start, move_delay=config.DIFFICULTIES[config.DEFAULT_DIFFICULTY].ai_move_delay):
        self.row, self.col = start
        self.move_delay = move_delay
        self.tick = 0
        self.freeze_time = 0       # frames remaining frozen (from a FREEZE pickup)

        self.path = []
        self.index = 0

        self.render_x = None       # pixel position (lazily set on first draw)
        self.render_y = None
        self.trail = deque(maxlen=9)

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

    def draw(self, screen, viewport, t=0.0):
        size = viewport.cell_size
        target_x, target_y = viewport.center(self.row, self.col)
        if self.render_x is None:
            self.render_x, self.render_y = target_x, target_y
        self.render_x = effects.ease(self.render_x, target_x, 0.25)
        self.render_y = effects.ease(self.render_y, target_y, 0.25)
        center = (self.render_x, self.render_y)

        frozen = self.freeze_time > 0
        body = config.Color.FREEZE_TINT if frozen else config.Color.AI_BODY
        glow = config.Color.FREEZE_TINT if frozen else config.Color.AI_GLOW

        self.trail.append(center)
        for i, (tx, ty) in enumerate(self.trail):
            f = (i + 1) / len(self.trail)
            effects.draw_alpha_circle(screen, body, (tx, ty), size * 0.16 * f, int(60 * f))

        glow_r = size * (0.5 + 0.12 * effects.pulse(t, speed=5))
        effects.draw_glow(screen, glow, center, glow_r)
        pygame.draw.circle(screen, body, center, int(size * 0.28))
        pygame.draw.circle(screen, config.Color.WHITE, center, int(size * 0.09))


def _reconstruct(came_from, current):
    path = []
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path
