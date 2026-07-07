"""The game application: window, main loop and the screen state machine."""

import enum
import math
import random
import sys
import time

import pygame

from . import audio, config, effects, theme, ui
from .ai import AIPlayer
from .maze import Maze
from .player import Player
from .powerups import PowerUpManager
from .scores import best_score, compute_score, save_score, top_scores
from .settings import CONTROL_OPTIONS, THEME_OPTIONS, Settings


class State(enum.Enum):
    LOGIN = "login"
    MENU = "menu"
    DIFFICULTY = "difficulty"
    SETTINGS = "settings"
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
        self.display = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
        pygame.display.set_caption(config.CAPTION)
        self.screen = pygame.Surface((config.WIDTH, config.HEIGHT))  # draw target (shakeable)
        self.clock = pygame.time.Clock()

        self.font_big = pygame.font.SysFont("arial", 64, bold=True)
        self.font_med = pygame.font.SysFont("arial", 32)
        self.font_small = pygame.font.SysFont("arial", 22)

        # Preferences: theme, effects and audio are applied before anything draws.
        self.settings = Settings()
        theme.apply(self.settings["theme"])
        effects.set_enabled(self.settings["effects"])
        audio.init(self.settings["sound"])

        self.background = self._make_background()
        self.starfield = effects.Starfield()
        self.confetti = effects.Confetti()
        self.time = 0.0

        self.state = State.LOGIN
        self.player_name = ""
        self.user_text = ""
        self.winner = ""
        self.difficulty_key = config.DEFAULT_DIFFICULTY
        self.last_score = 0

        self.maze = None
        self.player = None
        self.ai = None
        self.powerups = None
        self.viewport = None
        self.start_time = 0.0
        self.round_start = 0.0
        self._count_shown = None
        self._go_played = False
        self.shake_frames = 0

    def _make_background(self):
        return effects.make_gradient(
            config.WIDTH, config.HEIGHT, config.Color.BG_TOP, config.Color.BG_BOTTOM)

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #
    def run(self):
        running = True
        while running:
            self.clock.tick(config.FPS)
            self.time = pygame.time.get_ticks() / 1000.0
            ui.begin_frame()

            self.screen.blit(self.background, (0, 0))
            if self.state != State.PLAYING:
                self.starfield.draw(self.screen, self.time)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self._handle_keydown(event)

            self._draw_current_screen(pygame.key.get_pressed())
            self._manage_music()
            self._present()

        pygame.quit()
        sys.exit()

    def _present(self):
        """Blit the draw surface to the window, applying any screen shake."""
        ox = oy = 0
        if self.shake_frames > 0:
            self.shake_frames -= 1
            mag = self.shake_frames * 0.5
            ox = random.uniform(-mag, mag)
            oy = random.uniform(-mag, mag)
        self.display.fill((0, 0, 0))
        self.display.blit(self.screen, (ox, oy))
        pygame.display.flip()

    def _manage_music(self):
        if self.state in (State.PLAYING, State.PAUSE):
            audio.start_music()
        else:
            audio.stop_music()

    def _quit(self):
        pygame.quit()
        sys.exit()

    def start_game(self, difficulty_key):
        self.difficulty_key = difficulty_key
        preset = config.DIFFICULTIES[difficulty_key]
        self.winner = ""

        self.maze = Maze(preset.size, cycle_duration=preset.reveal_seconds)
        self.player = Player(self.maze.start, controls=self.settings["controls"])
        self.ai = AIPlayer(self.maze.start, move_delay=preset.ai_move_delay)
        self.powerups = PowerUpManager(self.maze)

        play_area = (0, config.HUD_HEIGHT, config.WIDTH, config.HEIGHT - config.HUD_HEIGHT)
        self.viewport = effects.Viewport(self.maze.rows, self.maze.cols, play_area)

        self.round_start = time.time()
        self.start_time = self.round_start + config.COUNTDOWN_SECONDS
        self._count_shown = None
        self._go_played = False
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
        elif self.state in (State.LEADERBOARD, State.SETTINGS) and event.key == pygame.K_ESCAPE:
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
            State.SETTINGS: self._screen_settings,
            State.PLAYING: lambda: self._screen_playing(keys),
            State.PAUSE: self._screen_pause,
            State.GAME_OVER: self._screen_game_over,
            State.LEADERBOARD: self._screen_leaderboard,
        }[self.state]()

    # ------------------------------------------------------------------ #
    # Screens: menus
    # ------------------------------------------------------------------ #
    def _screen_login(self):
        ui.title(self.screen, self.font_big, "MEMORY MAZE", config.Color.ACCENT, 120)
        ui.blit_centered(self.screen, self.font_small,
                         "Race the AI out of the maze — before it fades from memory",
                         config.Color.HINT, 200)

        box = pygame.Rect(config.WIDTH // 2 - 220, 300, 440, 65)
        pygame.draw.rect(self.screen, config.Color.INPUT_BOX, box, border_radius=12)
        pygame.draw.rect(self.screen, config.Color.INPUT_BORDER, box, width=2, border_radius=12)

        caret = "|" if int(self.time * 2) % 2 == 0 else " "
        shown = self.font_med.render(self.user_text + caret, True, config.Color.WHITE)
        self.screen.blit(shown, (box.x + 20, box.y + 18))

        ui.blit_centered(self.screen, self.font_small,
                         "Enter Username & Press ENTER", config.Color.HINT, 400)

    def _screen_menu(self):
        ui.title(self.screen, self.font_big, "MEMORY MAZE", config.Color.ACCENT, 90)
        ui.blit_centered(self.screen, self.font_small,
                         f"Welcome, {self.player_name}", config.Color.TITLE_GOLD, 178)

        cx = config.WIDTH // 2 - 150
        if ui.button(self.screen, self.font_med, cx, 240, 300, 58, "START GAME"):
            self.state = State.DIFFICULTY
        if ui.button(self.screen, self.font_med, cx, 312, 300, 58, "LEADERBOARD"):
            self.state = State.LEADERBOARD
        if ui.button(self.screen, self.font_med, cx, 384, 300, 58, "SETTINGS"):
            self.state = State.SETTINGS
        if ui.button(self.screen, self.font_med, cx, 456, 300, 58, "EXIT"):
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

    def _screen_settings(self):
        ui.title(self.screen, self.font_big, "SETTINGS", config.Color.TITLE_GOLD, 60,
                 glow_color=config.Color.TITLE_GOLD)
        ui.panel(self.screen, pygame.Rect(config.WIDTH // 2 - 260, 160, 520, 340))

        self._setting_row("Controls", self.settings["controls"], 200, self._cycle_controls)
        self._setting_row("Theme", self.settings["theme"], 275, self._cycle_theme)
        self._setting_row("Effects", "ON" if self.settings["effects"] else "OFF", 350,
                          lambda: self._toggle("effects", effects.set_enabled))
        self._setting_row("Sound", "ON" if self.settings["sound"] else "OFF", 425,
                          lambda: self._toggle("sound", audio.set_enabled))

        if ui.button(self.screen, self.font_med, config.WIDTH // 2 - 120, 540, 240, 55, "BACK"):
            self.state = State.MENU

    def _setting_row(self, label, value, y, on_click):
        x = config.WIDTH // 2 - 220
        self.screen.blit(self.font_med.render(label, True, config.Color.WHITE), (x, y + 10))
        if ui.button(self.screen, self.font_med, x + 210, y, 230, 54, str(value)):
            on_click()

    def _cycle_controls(self):
        self.settings.cycle("controls", CONTROL_OPTIONS)

    def _cycle_theme(self):
        self.settings.cycle("theme", THEME_OPTIONS)
        theme.apply(self.settings["theme"])
        effects.clear_caches()
        self.background = self._make_background()

    def _toggle(self, key, apply_fn):
        self.settings.toggle(key)
        apply_fn(self.settings[key])

    # ------------------------------------------------------------------ #
    # Screens: gameplay
    # ------------------------------------------------------------------ #
    def _screen_playing(self, keys):
        now = time.time()
        counting = (now - self.round_start) < config.COUNTDOWN_SECONDS

        if not counting:
            if not self._go_played:
                self._go_played = True
                audio.play("go")
            self.maze.update_memory_cycle()
            if self.player.handle_input(keys, self.maze):
                audio.play("move")
            self.ai.update(self.maze)
            self.powerups.update(self.player, self.ai)

        self.maze.draw(self.screen, self.viewport, self.time)
        self.powerups.draw(self.screen, self.viewport, self.time)
        self.player.draw(self.screen, self.viewport, self.time)
        self.ai.draw(self.screen, self.viewport, self.time)

        elapsed = max(0, int(now - self.start_time))
        self._draw_hud(elapsed)

        if counting:
            self._draw_countdown(config.COUNTDOWN_SECONDS - (now - self.round_start))
            return

        if (self.player.row, self.player.col) == self.maze.exit:
            self._finish("PLAYER", elapsed)
        elif (self.ai.row, self.ai.col) == self.maze.exit:
            self._finish("AI", elapsed)

    def _draw_countdown(self, remaining):
        n = int(math.ceil(remaining))
        if n != self._count_shown:
            self._count_shown = n
            audio.play("tick")
        label = str(n) if n > 0 else "GO!"
        scale = 1.0 + (remaining - int(remaining)) * 0.4  # gentle grow between ticks
        surf = self.font_big.render(label, True, config.Color.ACCENT)
        surf = pygame.transform.rotozoom(surf, 0, scale)
        effects.draw_glow(self.screen, config.Color.ACCENT,
                          (config.WIDTH // 2, config.HEIGHT // 2), 90)
        self.screen.blit(surf, (config.WIDTH // 2 - surf.get_width() // 2,
                                config.HEIGHT // 2 - surf.get_height() // 2))

    def _draw_hud(self, elapsed):
        strip = pygame.Surface((config.WIDTH, config.HUD_HEIGHT), pygame.SRCALPHA)
        strip.fill((14, 16, 34, 220))
        self.screen.blit(strip, (0, 0))
        pygame.draw.line(self.screen, config.Color.PANEL_BORDER,
                         (0, config.HUD_HEIGHT), (config.WIDTH, config.HUD_HEIGHT), 2)

        y = 16
        self.screen.blit(self.font_small.render(f"TIME  {elapsed}s", True, config.Color.WHITE), (24, y))
        self.screen.blit(self.font_small.render(self.difficulty_key, True, config.Color.ACCENT_SOFT),
                         (180, y))
        self.screen.blit(self.font_small.render(f"PENALTY  +{self.player.penalty_time}s", True,
                                                config.Color.TITLE_GOLD), (300, y))

        if self.maze.revealed:
            phase, color = "REVEALED", config.Color.POWERUP["REVEAL"]
        elif self.maze.memory_state == "HIDDEN":
            phase, color = "REMEMBER!", config.Color.EXIT
        else:
            phase, color = "LOOK", config.Color.START
        self.screen.blit(self.font_small.render(phase, True, color), (520, y))

        if self.ai.freeze_time > 0:
            self.screen.blit(self.font_small.render("AI FROZEN", True, config.Color.FREEZE_TINT),
                             (config.WIDTH - 140, y))

    def _finish(self, winner, elapsed):
        self.winner = winner
        self.last_score = compute_score(self.difficulty_key, winner, elapsed, self.player.penalty_time)
        save_score(self.player_name, winner, elapsed, self.player.penalty_time, self.difficulty_key)
        self.state = State.GAME_OVER
        if winner == "PLAYER":
            audio.play("win")
            self.confetti.burst()
        else:
            audio.play("lose")
            self.shake_frames = 26

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

        ui.panel(self.screen, pygame.Rect(config.WIDTH // 2 - 260, 140, 520, 340))
        ui.title(self.screen, self.font_med, "GAME OVER", config.Color.HINT, 175,
                 glow_color=config.Color.HINT)
        ui.title(self.screen, self.font_big, result, result_color, 230, glow_color=result_color)

        best = best_score(self.difficulty_key)
        ui.blit_centered(self.screen, self.font_med,
                         f"Score  {self.last_score}", config.Color.WHITE, 330)
        ui.blit_centered(self.screen, self.font_small,
                         f"Best ({self.difficulty_key})  {best}", config.Color.ACCENT_SOFT, 375)
        ui.blit_centered(self.screen, self.font_small,
                         "R  -  Restart      M  -  Menu", config.Color.HINT, 420)

        if player_won:
            self.confetti.update_and_draw(self.screen)

    def _screen_leaderboard(self):
        ui.title(self.screen, self.font_big, "LEADERBOARD", config.Color.ACCENT, 50)

        panel_rect = pygame.Rect(config.WIDTH // 2 - 300, 140, 600, config.HEIGHT - 240)
        ui.panel(self.screen, panel_rect)

        scores = top_scores()
        x = panel_rect.x + 28
        y = panel_rect.y + 22
        if not scores:
            ui.blit_centered(self.screen, self.font_med, "No scores yet", config.Color.HINT, y + 40)
        else:
            header = self.font_small.render("#   PLAYER          DIFF       TIME     SCORE",
                                            True, config.Color.ACCENT_SOFT)
            self.screen.blit(header, (x, y))
            y += 38
            for i, s in enumerate(scores, 1):
                win = s.get("winner") == "PLAYER"
                mark = config.Color.START if win else config.Color.EXIT
                row = f"{i:<3} {s.get('player', '?'):<14} {s.get('difficulty', '-'):<8} " \
                      f"{s.get('time', 0)}s"
                self.screen.blit(self.font_small.render(row, True, config.Color.WHITE), (x, y))
                self.screen.blit(self.font_small.render(str(s.get('score', 0)), True, mark),
                                 (panel_rect.right - 90, y))
                y += 32

        if ui.button(self.screen, self.font_med,
                     config.WIDTH // 2 - 150, config.HEIGHT - 78, 300, 52, "BACK TO MENU"):
            self.state = State.MENU
