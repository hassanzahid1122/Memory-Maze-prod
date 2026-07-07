"""The game application: window, main loop and the screen state machine."""

import enum
import sys
import time

import pygame

from . import config, effects, ui
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

        self.background = effects.make_gradient(
            config.WIDTH, config.HEIGHT, config.Color.BG_TOP, config.Color.BG_BOTTOM)
        self.starfield = effects.Starfield()
        self.time = 0.0

        self.state = State.LOGIN
        self.player_name = ""
        self.user_text = ""
        self.winner = ""
        self.difficulty_key = config.DEFAULT_DIFFICULTY

        self.maze = None
        self.player = None
        self.ai = None
        self.powerups = None
        self.viewport = None
        self.start_time = 0.0

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #
    def run(self):
        running = True
        while running:
            self.clock.tick(config.FPS)
            self.time = pygame.time.get_ticks() / 1000.0
            self.screen.blit(self.background, (0, 0))
            if self.state != State.PLAYING:
                self.starfield.draw(self.screen, self.time)
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

        play_area = (0, config.HUD_HEIGHT, config.WIDTH, config.HEIGHT - config.HUD_HEIGHT)
        self.viewport = effects.Viewport(self.maze.rows, self.maze.cols, play_area)

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
        ui.title(self.screen, self.font_big, "MEMORY MAZE", config.Color.ACCENT, 130)
        ui.blit_centered(self.screen, self.font_small,
                         "Race the AI out of the maze — before it fades from memory",
                         config.Color.HINT, 210)

        box = pygame.Rect(config.WIDTH // 2 - 220, 300, 440, 65)
        pygame.draw.rect(self.screen, config.Color.INPUT_BOX, box, border_radius=12)
        pygame.draw.rect(self.screen, config.Color.INPUT_BORDER, box, width=2, border_radius=12)

        caret = "|" if int(self.time * 2) % 2 == 0 else " "
        shown = self.font_med.render(self.user_text + caret, True, config.Color.WHITE)
        self.screen.blit(shown, (box.x + 20, box.y + 18))

        ui.blit_centered(self.screen, self.font_small,
                         "Enter Username & Press ENTER", config.Color.HINT, 400)

    def _screen_menu(self):
        ui.title(self.screen, self.font_big, "MEMORY MAZE", config.Color.ACCENT, 100)
        ui.blit_centered(self.screen, self.font_small,
                         f"Welcome, {self.player_name}", config.Color.TITLE_GOLD, 190)

        cx = config.WIDTH // 2 - 150
        if ui.button(self.screen, self.font_med, cx, 270, 300, 60, "START GAME"):
            self.state = State.DIFFICULTY
        if ui.button(self.screen, self.font_med, cx, 350, 300, 60, "LEADERBOARD"):
            self.state = State.LEADERBOARD
        if ui.button(self.screen, self.font_med, cx, 430, 300, 60, "EXIT"):
            self._quit()

    def _screen_difficulty(self):
        ui.title(self.screen, self.font_big, "SELECT DIFFICULTY", config.Color.TITLE_GOLD, 70,
                 glow_color=config.Color.TITLE_GOLD)
        ui.blit_centered(self.screen, self.font_small,
                         "Choose your challenge level", config.Color.HINT, 145)

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

        self.maze.draw(self.screen, self.viewport, self.time)
        self.powerups.draw(self.screen, self.viewport, self.time)
        self.player.draw(self.screen, self.viewport, self.time)
        self.ai.draw(self.screen, self.viewport, self.time)

        elapsed = int(time.time() - self.start_time)
        self._draw_hud(elapsed)

        if (self.player.row, self.player.col) == self.maze.exit:
            self._finish("PLAYER", elapsed)
        elif (self.ai.row, self.ai.col) == self.maze.exit:
            self._finish("AI", elapsed)

    def _draw_hud(self, elapsed):
        bar = pygame.Rect(0, 0, config.WIDTH, config.HUD_HEIGHT)
        strip = pygame.Surface(bar.size, pygame.SRCALPHA)
        strip.fill((14, 16, 34, 220))
        self.screen.blit(strip, (0, 0))
        pygame.draw.line(self.screen, config.Color.PANEL_BORDER,
                         (0, config.HUD_HEIGHT), (config.WIDTH, config.HUD_HEIGHT), 2)

        y = 16
        self.screen.blit(self.font_small.render(f"TIME  {elapsed}s", True, config.Color.WHITE),
                         (24, y))
        self.screen.blit(self.font_small.render(f"{self.difficulty_key}", True, config.Color.ACCENT_SOFT),
                         (200, y))
        self.screen.blit(self.font_small.render(f"PENALTY  +{self.player.penalty_time}s", True,
                                                config.Color.TITLE_GOLD), (330, y))

        phase = "REMEMBER!" if self.maze.memory_state == "HIDDEN" else "LOOK"
        phase_color = config.Color.EXIT if self.maze.memory_state == "HIDDEN" else config.Color.START
        self.screen.blit(self.font_small.render(phase, True, phase_color), (560, y))

        if self.ai.freeze_time > 0:
            self.screen.blit(self.font_small.render("AI FROZEN", True, config.Color.FREEZE_TINT),
                             (config.WIDTH - 140, y))

    def _finish(self, winner, elapsed):
        self.winner = winner
        save_score(self.player_name, winner, elapsed, self.player.penalty_time)
        self.state = State.GAME_OVER

    def _screen_pause(self):
        ui.draw_overlay(self.screen, 170)
        ui.panel(self.screen, pygame.Rect(config.WIDTH // 2 - 200, 90, 400, 430))
        ui.title(self.screen, self.font_big, "PAUSED", config.Color.TITLE_GOLD, 120,
                 glow_color=config.Color.TITLE_GOLD)

        cx = config.WIDTH // 2 - 150
        if ui.button(self.screen, self.font_med, cx, 260, 300, 60, "RESUME"):
            self.state = State.PLAYING
        if ui.button(self.screen, self.font_med, cx, 340, 300, 60, "RESTART"):
            self.start_game(self.difficulty_key)
        if ui.button(self.screen, self.font_med, cx, 420, 300, 60, "MAIN MENU"):
            self.state = State.MENU

    def _screen_game_over(self):
        player_won = self.winner == "PLAYER"
        result = "YOU WIN!" if player_won else "AI WINS!"
        result_color = config.Color.START if player_won else config.Color.EXIT

        ui.panel(self.screen, pygame.Rect(config.WIDTH // 2 - 260, 150, 520, 300))
        ui.title(self.screen, self.font_med, "GAME OVER", config.Color.HINT, 190,
                 glow_color=config.Color.HINT)
        ui.title(self.screen, self.font_big, result, result_color, 250, glow_color=result_color)
        ui.blit_centered(self.screen, self.font_small,
                         "R  -  Restart      M  -  Menu", config.Color.WHITE, 380)

    def _screen_leaderboard(self):
        ui.title(self.screen, self.font_big, "LEADERBOARD", config.Color.ACCENT, 60)

        panel_rect = pygame.Rect(config.WIDTH // 2 - 280, 150, 560, config.HEIGHT - 260)
        ui.panel(self.screen, panel_rect)

        scores = load_scores()
        y = panel_rect.y + 24
        if not scores:
            ui.blit_centered(self.screen, self.font_med, "No scores yet", config.Color.HINT, y + 40)
        else:
            header = self.font_small.render("PLAYER            RESULT        TIME",
                                            True, config.Color.ACCENT_SOFT)
            self.screen.blit(header, (panel_rect.x + 30, y))
            y += 40
            for s in scores[-config.LEADERBOARD_LIMIT:][::-1]:
                win = s["winner"] == "PLAYER"
                row_color = config.Color.START if win else config.Color.EXIT
                name = self.font_small.render(f"{s['player']:<14}", True, config.Color.WHITE)
                res = self.font_small.render(f"{'WIN' if win else 'LOSS':<10}", True, row_color)
                tm = self.font_small.render(f"{s['time']}s", True, config.Color.WHITE)
                self.screen.blit(name, (panel_rect.x + 30, y))
                self.screen.blit(res, (panel_rect.x + 250, y))
                self.screen.blit(tm, (panel_rect.x + 430, y))
                y += 34

        if ui.button(self.screen, self.font_med,
                     config.WIDTH // 2 - 150, config.HEIGHT - 80, 300, 55, "BACK TO MENU"):
            self.state = State.MENU
