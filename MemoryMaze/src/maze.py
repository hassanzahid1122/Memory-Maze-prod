import pygame
import random
import time
from src.settings import *

class Cell:
    def __init__(self, r, c):
        self.row = r
        self.col = c
        self.walls = [True, True, True, True]
        self.visited = False


class Maze:

    def __init__(self, size):

        self.rows = size
        self.cols = size

        self.grid = [
            [Cell(r, c) for c in range(size)]
            for r in range(size)
        ]

        self.start = (0, 0)
        self.exit = (size - 1, size - 1)

        # ================= MEMORY CYCLE =================
        self.memory_state = "VISIBLE"
        self.last_switch_time = time.time()
        self.cycle_duration = 5  # seconds

        self.visible_cells = set()

        self.generate_maze()

    # SAFE CELL ACCESS
    def cell(self, r, c):

        if r < 0 or c < 0 or r >= self.rows or c >= self.cols:
            return None

        return self.grid[r][c]

    # MAZE GENERATION
    def generate_maze(self):

        stack = []
        start = self.grid[0][0]
        start.visited = True
        stack.append(start)

        while stack:

            current = stack[-1]
            r, c = current.row, current.col

            neighbors = []

            def check(nr, nc):
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    n = self.grid[nr][nc]
                    if not n.visited:
                        neighbors.append(n)

            check(r-1, c)
            check(r, c+1)
            check(r+1, c)
            check(r, c-1)

            if neighbors:

                nxt = random.choice(neighbors)
                nxt.visited = True
                stack.append(nxt)

                dr = nxt.row - r
                dc = nxt.col - c

                if dr == -1:
                    current.walls[0] = False
                    nxt.walls[2] = False
                elif dr == 1:
                    current.walls[2] = False
                    nxt.walls[0] = False
                elif dc == 1:
                    current.walls[1] = False
                    nxt.walls[3] = False
                elif dc == -1:
                    current.walls[3] = False
                    nxt.walls[1] = False

            else:
                stack.pop()

    # MEMORY CYCLE UPDATE (IMPORTANT)
    def update_memory_cycle(self):

        now = time.time()

        if now - self.last_switch_time >= self.cycle_duration:

            self.last_switch_time = now

            if self.memory_state == "VISIBLE":
                self.memory_state = "HIDDEN"
                self.generate_memory_view(0.6)

            else:
                self.memory_state = "VISIBLE"
                self.visible_cells = set()

    # MEMORY VIEW (60% HIDE)
    def generate_memory_view(self, hide_ratio=0.6):

        self.visible_cells = set()

        total = self.rows * self.cols

        # Always keep start & exit
        self.visible_cells.add(self.start)
        self.visible_cells.add(self.exit)

        all_cells = [
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
        ]

        random.shuffle(all_cells)

        keep = int(total * (1 - hide_ratio))

        for cell in all_cells[:keep]:
            self.visible_cells.add(cell)

    # DRAW
    def draw(self, screen):

        for row in self.grid:
            for cell in row:

                x = cell.col * CELL_SIZE
                y = cell.row * CELL_SIZE

                pos = (cell.row, cell.col)

                # START
                if pos == self.start:
                    pygame.draw.rect(screen, (0, 255, 0),
                                     (x, y, CELL_SIZE, CELL_SIZE))
                    continue

                # EXIT
                if pos == self.exit:
                    pygame.draw.rect(screen, (255, 0, 0),
                                     (x, y, CELL_SIZE, CELL_SIZE))
                    continue

                # MEMORY HIDE LOGIC
                if self.memory_state == "HIDDEN" and pos not in self.visible_cells:
                    pygame.draw.rect(screen, (12, 12, 20),
                                     (x, y, CELL_SIZE, CELL_SIZE))
                    continue

                # WALLS
                if cell.walls[0]:
                    pygame.draw.line(screen, (200,200,200), (x,y), (x+CELL_SIZE,y))
                if cell.walls[1]:
                    pygame.draw.line(screen, (200,200,200), (x+CELL_SIZE,y), (x+CELL_SIZE,y+CELL_SIZE))
                if cell.walls[2]:
                    pygame.draw.line(screen, (200,200,200), (x,y+CELL_SIZE), (x+CELL_SIZE,y+CELL_SIZE))
                if cell.walls[3]:
                    pygame.draw.line(screen, (200,200,200), (x,y), (x,y+CELL_SIZE))