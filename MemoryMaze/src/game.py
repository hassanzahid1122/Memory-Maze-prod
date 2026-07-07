"""The game application: window, main loop and the screen state machine."""

import enum
import sys
import time

import pygame

from . import config, ui
from .ai import AIPlayer
from .maze import Maze
from .player import Player
from .powerups import PowerUpManager
from .scores import load_scores, save_score


class State(enum.Enum):
    LOGIN = "login"
    MENU = "menu"
    DIFFICULTY = "difficulty"
    PLAYING = "playing"
    PAUSE = "pause"
    GAME_OVER = "game_over"
    LEADERBOARD = "leaderboard"


_DIFFICULTY_BLURB = {
    "EASY": ("Small Maze | Slow AI | 8s Reveal", (180, 255, 180)),
    "MEDIUM": ("Balanced Maze | Normal AI | 6s Reveal", (255, 255, 180)),
    "HARD": ("Large Maze | Fast AI | 4s Reveal", (255, 180, 180)),
}


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
        pygame.display.set_caption(config.CAPTION)
        self.clock = pygame.time.Clock()

        self.font_big = pygame.font.SysFont("arial", 64, bold=True)
        self.font_med = pygame.font.SysFont("arial", 32)
        self.font_small = pygame.font.SysFont("arial", 22)

        self.state = State.LOGIN
        self.player_name = ""
        self.user_text = ""
        self.winner = ""
        self.difficulty_key = config.DEFAULT_DIFFICULTY

        self.maze = None
        self.player = None
        self.ai = None
        self.powerups = None
        self.start_time = 0.0

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #
    def run(self):
        running = True
        while running:
            self.clock.tick(config.FPS)
            self.screen.fill(config.Color.BG)
            keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self._handle_keydown(event)

            self._draw_current_screen(keys)
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _quit(self):
        pygame.quit()
        sys.exit()

    def start_game(self, difficulty_key):
        self.difficulty_key = difficulty_key
        preset = config.DIFFICULTIES[difficulty_key]
        self.winner = ""

        self.maze = Maze(preset.size, cycle_duration=preset.reveal_seconds)
        self.player = Player(self.maze.start)
        self.ai = AIPlayer(self.maze.start, move_delay=preset.ai_move_delay)
        self.powerups = PowerUpManager(self.maze)

        self.start_time = time.time()
        self.state = State.PLAYING

    # ------------------------------------------------------------------ #
    # Event handling (keyboard)
    # ------------------------------------------------------------------ #
    def _handle_keydown(self, event):
        if self.state == State.LOGIN:
            self._handle_login_key(event)
        elif self.state == State.PLAYING and event.key == pygame.K_ESCAPE:
            self.state = State.PAUSE
        elif self.state == State.PAUSE:
            if event.key == pygame.K_ESCAPE:
                self.state = State.PLAYING
            elif event.key == pygame.K_r:
                self.start_game(self.difficulty_key)
            elif event.key == pygame.K_m:
                self.state = State.MENU
        elif self.state == State.GAME_OVER:
            if event.key == pygame.K_r:
                self.start_game(self.difficulty_key)
            elif event.key == pygame.K_m:
                self.state = State.MENU
        elif self.state == State.LEADERBOARD and event.key == pygame.K_ESCAPE:
            self.state = State.MENU

    def _handle_login_key(self, event):
        if event.key == pygame.K_RETURN and self.user_text:
            self.player_name = self.user_text
            self.state = State.MENU
        elif event.key == pygame.K_BACKSPACE:
            self.user_text = self.user_text[:-1]
        elif len(self.user_text) < config.MAX_USERNAME_LEN:
            self.user_text += event.unicode

    # ------------------------------------------------------------------ #
    # Screen dispatch
    # ------------------------------------------------------------------ #
    def _draw_current_screen(self, keys):
        {
            State.LOGIN: self._screen_login,
            State.MENU: self._screen_menu,
            State.DIFFICULTY: self._screen_difficulty,
            State.PLAYING: lambda: self._screen_playing(keys),
            State.PAUSE: self._screen_pause,
            State.GAME_OVER: self._screen_game_over,
            State.LEADERBOARD: self._screen_leaderboard,
        }[self.state]()

    # ------------------------------------------------------------------ #
    # Screens
    # ------------------------------------------------------------------ #
    def _screen_login(self):
        ui.blit_centered(self.screen, self.font_big, "MEMORY MAZE", config.Color.ACCENT, 120)

        box = pygame.Rect(config.WIDTH // 2 - 220, 300, 440, 65)
        pygame.draw.rect(self.screen, config.Color.INPUT_BOX, box, border_radius=12)
        self.screen.blit(self.font_med.render(self.user_text, True, config.Color.WHITE),
                         (box.x + 20, box.y + 18))

        ui.blit_centered(self.screen, self.font_small,
                         "Enter Username & Press ENTER", config.Color.HINT, 400)

    def _screen_menu(self):
        ui.blit_centered(self.screen, self.font_big, "MEMORY MAZE", config.Color.ACCENT, 100)
        ui.blit_centered(self.screen, self.font_small,
                         f"Welcome {self.player_name}", (255, 255, 0), 180)

        cx = config.WIDTH // 2 - 150
        if ui.button(self.screen, self.font_med, cx, 270, 300, 60, "START GAME"):
            self.state = State.DIFFICULTY
        if ui.button(self.screen, self.font_med, cx, 350, 300, 60, "LEADERBOARD"):
            self.state = State.LEADERBOARD
        if ui.button(self.screen, self.font_med, cx, 430, 300, 60, "EXIT"):
            self._quit()

    def _screen_difficulty(self):
        ui.draw_overlay(self.screen, 180)
        ui.blit_centered(self.screen, self.font_big, "SELECT DIFFICULTY", config.Color.TITLE_GOLD, 70)
        ui.blit_centered(self.screen, self.font_small,
                         "Choose your challenge level", (220, 220, 220), 145)

        cx = config.WIDTH // 2 - 180
        rows = [("EASY", 220, 295), ("MEDIUM", 340, 415), ("HARD", 460, 535)]
        for key, btn_y, blurb_y in rows:
            if ui.button(self.screen, self.font_med, cx, btn_y, 360, 70, key):
                self.start_game(key)
                return
            text, color = _DIFFICULTY_BLURB[key]
            ui.blit_centered(self.screen, self.font_small, text, color, blurb_y)

        if ui.button(self.screen, self.font_med, config.WIDTH // 2 - 120, 610, 240, 55, "BACK"):
            self.state = State.MENU

    def _screen_playing(self, keys):
        self.maze.update_memory_cycle()
        self.player.handle_input(keys, self.maze)
        self.ai.update(self.maze)
        self.powerups.update(self.player, self.ai)

        self.maze.draw(self.screen)
        self.player.draw(self.screen)
        self.ai.draw(self.screen)
        self.powerups.draw(self.screen)

        elapsed = int(time.time() - self.start_time)
        self.screen.blit(self.font_small.render(f"Time: {elapsed}s", True, config.Color.WHITE), (20, 20))

        if (self.player.row, self.player.col) == self.maze.exit:
            self._finish("PLAYER", elapsed)
        elif (self.ai.row, self.ai.col) == self.maze.exit:
            self._finish("AI", elapsed)

    def _finish(self, winner, elapsed):
        self.winner = winner
        save_score(self.player_name, winner, elapsed, self.player.penalty_time)
        self.state = State.GAME_OVER

    def _screen_pause(self):
        ui.draw_overlay(self.screen, 180)
        ui.blit_centered(self.screen, self.font_big, "PAUSED", (255, 255, 0), 120)

        cx = config.WIDTH // 2 - 150
        if ui.button(self.screen, self.font_med, cx, 260, 300, 60, "RESUME"):
            self.state = State.PLAYING
        if ui.button(self.screen, self.font_med, cx, 340, 300, 60, "RESTART"):
            self.start_game(self.difficulty_key)
        if ui.button(self.screen, self.font_med, cx, 420, 300, 60, "MAIN MENU"):
            self.state = State.MENU

    def _screen_game_over(self):
        result = "PLAYER WINS!" if self.winner == "PLAYER" else "AI WINS!"
        self.screen.blit(self.font_big.render("GAME OVER", True, (0, 255, 120)),
                         (config.WIDTH // 2 - 220, 120))
        self.screen.blit(self.font_big.render(result, True, (255, 255, 0)),
                         (config.WIDTH // 2 - 250, 220))
        self.screen.blit(self.font_med.render("R - Restart | M - Menu", True, config.Color.WHITE),
                         (config.WIDTH // 2 - 180, 340))

    def _screen_leaderboard(self):
        ui.draw_overlay(self.screen, 200)
        ui.blit_centered(self.screen, self.font_big, "LEADERBOARD", config.Color.ACCENT, 80)

        scores = load_scores()
        y = 160
        if not scores:
            ui.blit_centered(self.screen, self.font_med, "No scores yet", config.Color.WHITE, y)
        else:
            for s in scores[-config.LEADERBOARD_LIMIT:][::-1]:
                row = f"{s['player']} | {s['winner']} | {s['time']}s"
                self.screen.blit(self.font_small.render(row, True, config.Color.WHITE),
                                 (config.WIDTH // 2 - 160, y))
                y += 40

        if ui.button(self.screen, self.font_med,
                     config.WIDTH // 2 - 150, config.HEIGHT - 90, 300, 60, "BACK TO MENU"):
            self.state = State.MENU
