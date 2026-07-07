import random
import pygame

class PowerUp:
    def __init__(self, r, c, t):
        self.row = r
        self.col = c
        self.type = t
        self.active = True


class PowerUpManager:
    def __init__(self, maze):
        self.maze = maze
        self.powerups = []
        self.spawn()

    # FR6.1 — RANDOM SPAWN
    def spawn(self):
        types = ["SPEED", "SLOW_AI", "FREEZE"]

        for _ in range(6):
            r = random.randint(1, self.maze.rows-2)
            c = random.randint(1, self.maze.cols-2)

            self.powerups.append(PowerUp(r, c, random.choice(types)))

    # FR6.3 — APPLY EFFECTS
    def update(self, player, ai):

        for p in self.powerups:
            if not p.active:
                continue

            # PLAYER PICKUP
            if (player.row, player.col) == (p.row, p.col):

                if p.type == "SPEED":
                    player.move_delay = max(1, player.move_delay - 2)

                elif p.type == "SLOW_AI":
                    ai.move_delay += 3

                elif p.type == "FREEZE":
                    ai.freeze_time = 60

                p.active = False

    # DRAW
    def draw(self, screen):

        for p in self.powerups:
            if not p.active:
                continue

            x = p.col * 30 + 15
            y = p.row * 30 + 15

            color = {
                "SPEED": (0,255,0),
                "SLOW_AI": (255,165,0),
                "FREEZE": (0,200,255)
            }[p.type]

            pygame.draw.circle(screen, color, (x,y), 8)
            