import pygame
import heapq
from src.settings import *

class AIPlayer:

    def __init__(self, start):
        self.row, self.col = start

        self.path = []
        self.index = 0

        self.move_delay = 8
        self.tick = 0

        self.freeze_time = 0


    # UPDATE AI (MOVEMENT LOGIC)
    def update(self, maze):

        # freeze effect (powerup)
        if self.freeze_time > 0:
            self.freeze_time -= 1
            return

        # recalc path if needed
        if not self.path or self.index >= len(self.path):
            self.path = self.a_star(maze, (self.row, self.col), maze.exit)
            self.index = 0

        if not self.path:
            return

        self.tick += 1

        if self.tick < self.move_delay:
            return

        self.tick = 0

        # move AI step-by-step
        self.row, self.col = self.path[self.index]
        self.index += 1

    def a_star(self, maze, start, goal):

        def h(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        open_set = []
        heapq.heappush(open_set, (0, start))

        came_from = {}
        g_score = {start: 0}

        while open_set:

            _, current = heapq.heappop(open_set)

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path

            r, c = current
            cell = maze.cell(r, c)

            if not cell:
                continue

   
            directions = [
                (-1, 0, 0),  # up
                (0, 1, 1),   # right
                (1, 0, 2),   # down
                (0, -1, 3)   # left
            ]

            for dr, dc, wall in directions:

            
                if cell.walls[wall]:
                    continue

                nr, nc = r + dr, c + dc

        
                if nr < 0 or nc < 0 or nr >= maze.rows or nc >= maze.cols:
                    continue

                neighbor = (nr, nc)

                temp_g = g_score[current] + 1

                if neighbor not in g_score or temp_g < g_score[neighbor]:

                    g_score[neighbor] = temp_g
                    f_score = temp_g + h(neighbor, goal)

                    heapq.heappush(open_set, (f_score, neighbor))
                    came_from[neighbor] = current

        return []


    # DRAW AI 
    def draw(self, screen):

        x = self.col * CELL_SIZE + CELL_SIZE // 4
        y = self.row * CELL_SIZE + CELL_SIZE // 4

        # AI BODY
        pygame.draw.rect(
            screen,
            (255, 80, 80),
            (x, y, CELL_SIZE // 2, CELL_SIZE // 2)
        )

        # AI INNER GLOW
        pygame.draw.circle(
            screen,
            (255, 160, 160),
            (self.col * CELL_SIZE + CELL_SIZE // 2,
             self.row * CELL_SIZE + CELL_SIZE // 2),
            CELL_SIZE // 6
        )