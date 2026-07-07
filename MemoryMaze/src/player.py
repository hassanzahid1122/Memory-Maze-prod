import pygame
from src.settings import *

class Player:
    def __init__(self, start):
        self.row, self.col = start
        self.move_delay = 0
        self.penalty_time = 0

    def handle_input(self, keys, maze):

        if self.move_delay > 0:
            self.move_delay -= 1
            return

        cell = maze.cell(self.row, self.col)
        r, c = self.row, self.col

        moved = False

        # LEFT
        if keys[pygame.K_LEFT] and not cell.walls[3]:
            self.col -= 1
            moved = True

        # RIGHT
        elif keys[pygame.K_RIGHT] and not cell.walls[1]:
            self.col += 1
            moved = True

        # UP
        elif keys[pygame.K_UP] and not cell.walls[0]:
            self.row -= 1
            moved = True

        # DOWN
        elif keys[pygame.K_DOWN] and not cell.walls[2]:
            self.row += 1
            moved = True

        if moved:
            self.move_delay = 6
            self.check_dead_end(maze)

    def check_dead_end(self, maze):
        cell = maze.cell(self.row, self.col)
        open_paths = sum([not w for w in cell.walls])

        if open_paths <= 1:
            self.penalty_time += 2

    def draw(self, screen):
        x = self.col * CELL_SIZE + CELL_SIZE//4
        y = self.row * CELL_SIZE + CELL_SIZE//4

        pygame.draw.rect(screen, (0, 180, 255),
                         (x, y, CELL_SIZE//2, CELL_SIZE//2))