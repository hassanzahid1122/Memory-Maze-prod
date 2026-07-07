"""Maze generation, the memory (visible/hidden) cycle, and rendering."""

import random
import time

import pygame

from . import config, effects

# Wall indices, shared by every module that inspects a cell's walls.
TOP, RIGHT, BOTTOM, LEFT = 0, 1, 2, 3

# (row delta, col delta, wall on current cell, opposite wall on neighbour)
DIRECTIONS = [
    (-1, 0, TOP, BOTTOM),
    (0, 1, RIGHT, LEFT),
    (1, 0, BOTTOM, TOP),
    (0, -1, LEFT, RIGHT),
]

VISIBLE = "VISIBLE"
HIDDEN = "HIDDEN"


class Cell:
    """A single maze cell. ``walls`` is indexed by TOP/RIGHT/BOTTOM/LEFT."""

    __slots__ = ("row", "col", "walls", "visited")

    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.walls = [True, True, True, True]
        self.visited = False


class Maze:
    """A perfect maze generated with randomised depth-first search.

    The "memory" mechanic periodically hides a fraction of the cells so the
    player has to remember the layout, alternating between VISIBLE and HIDDEN
    phases every ``cycle_duration`` seconds.
    """

    def __init__(self, size, cycle_duration=config.DIFFICULTIES[config.DEFAULT_DIFFICULTY].reveal_seconds):
        self.rows = size
        self.cols = size
        self.grid = [[Cell(r, c) for c in range(size)] for r in range(size)]

        self.start = (0, 0)
        self.exit = (size - 1, size - 1)

        self.memory_state = VISIBLE
        self.cycle_duration = cycle_duration
        self.last_switch_time = time.time()
        self.visible_cells = set()

        self._generate()

    # ------------------------------------------------------------------ #
    # Access
    # ------------------------------------------------------------------ #
    def cell(self, row, col):
        """Return the cell at (row, col), or None when out of bounds."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col]
        return None

    def in_bounds(self, row, col):
        return 0 <= row < self.rows and 0 <= col < self.cols

    # ------------------------------------------------------------------ #
    # Generation
    # ------------------------------------------------------------------ #
    def _generate(self):
        start = self.grid[0][0]
        start.visited = True
        stack = [start]

        while stack:
            current = stack[-1]
            neighbours = self._unvisited_neighbours(current)

            if not neighbours:
                stack.pop()
                continue

            nxt = random.choice(neighbours)
            nxt.visited = True
            self._open_wall(current, nxt)
            stack.append(nxt)

    def _unvisited_neighbours(self, cell):
        neighbours = []
        for dr, dc, _, _ in DIRECTIONS:
            neighbour = self.cell(cell.row + dr, cell.col + dc)
            if neighbour and not neighbour.visited:
                neighbours.append(neighbour)
        return neighbours

    @staticmethod
    def _open_wall(current, nxt):
        dr = nxt.row - current.row
        dc = nxt.col - current.col
        for ddr, ddc, wall, opposite in DIRECTIONS:
            if (ddr, ddc) == (dr, dc):
                current.walls[wall] = False
                nxt.walls[opposite] = False
                return

    # ------------------------------------------------------------------ #
    # Memory cycle
    # ------------------------------------------------------------------ #
    def update_memory_cycle(self):
        """Flip between VISIBLE and HIDDEN once ``cycle_duration`` has elapsed."""
        now = time.time()
        if now - self.last_switch_time < self.cycle_duration:
            return

        self.last_switch_time = now
        if self.memory_state == VISIBLE:
            self.memory_state = HIDDEN
            self._build_memory_view(config.MEMORY_HIDE_RATIO)
        else:
            self.memory_state = VISIBLE
            self.visible_cells = set()

    def _build_memory_view(self, hide_ratio):
        """Pick which cells stay visible while HIDDEN (start & exit always show)."""
        all_cells = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        random.shuffle(all_cells)

        keep = int(len(all_cells) * (1 - hide_ratio))
        self.visible_cells = set(all_cells[:keep])
        self.visible_cells.add(self.start)
        self.visible_cells.add(self.exit)

    # ------------------------------------------------------------------ #
    # Rendering
    # ------------------------------------------------------------------ #
    def draw(self, screen, viewport, t=0.0):
        size = viewport.cell_size

        # Floor beneath the whole maze so the walls read clearly.
        field = pygame.Rect(viewport.ox, viewport.oy, viewport.width, viewport.height)
        pygame.draw.rect(screen, config.Color.FLOOR, field.inflate(10, 10), border_radius=10)
        pygame.draw.rect(screen, config.Color.FLOOR_BORDER, field.inflate(10, 10),
                         width=2, border_radius=10)

        for row in self.grid:
            for cell in row:
                x, y = viewport.origin(cell.row, cell.col)
                pos = (cell.row, cell.col)

                if pos == self.start:
                    self._draw_marker(screen, x, y, size, config.Color.START, t)
                    continue
                if pos == self.exit:
                    self._draw_marker(screen, x, y, size, config.Color.EXIT, t, offset=0.9)
                    continue

                if self.memory_state == HIDDEN and pos not in self.visible_cells:
                    pygame.draw.rect(screen, config.Color.FOG, (x + 1, y + 1, size - 2, size - 2),
                                     border_radius=4)
                    continue

                self._draw_walls(screen, cell, x, y, size)

    @staticmethod
    def _draw_marker(screen, x, y, size, color, t, offset=0.0):
        """A glowing, gently pulsing start/exit tile."""
        cx, cy = x + size / 2, y + size / 2
        glow_r = size * (0.7 + 0.18 * effects.pulse(t + offset, speed=3))
        effects.draw_glow(screen, color, (cx, cy), glow_r)
        inset = max(2, size // 8)
        pygame.draw.rect(screen, color, (x + inset, y + inset, size - 2 * inset, size - 2 * inset),
                         border_radius=6)

    @staticmethod
    def _draw_walls(screen, cell, x, y, size):
        color = config.Color.WALL
        w = 2
        if cell.walls[TOP]:
            pygame.draw.line(screen, color, (x, y), (x + size, y), w)
        if cell.walls[RIGHT]:
            pygame.draw.line(screen, color, (x + size, y), (x + size, y + size), w)
        if cell.walls[BOTTOM]:
            pygame.draw.line(screen, color, (x, y + size), (x + size, y + size), w)
        if cell.walls[LEFT]:
            pygame.draw.line(screen, color, (x, y), (x, y + size), w)
