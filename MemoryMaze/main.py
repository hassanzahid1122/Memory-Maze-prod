import pygame
import sys
import time

from src.settings import *
from src.maze import Maze
from src.player import Player
from src.ai import AIPlayer
from src.powerups import PowerUpManager
from src.scores import save_score, load_scores

pygame.init()


# SCREEN
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Memory Maze")
clock = pygame.time.Clock()


# FONTS
font_big = pygame.font.SysFont("arial", 64, bold=True)
font_med = pygame.font.SysFont("arial", 32)
font_small = pygame.font.SysFont("arial", 22)

# STATES

LOGIN = "login"
MENU = "menu"
DIFFICULTY = "difficulty"
PLAYING = "playing"
PAUSE = "pause"
GAME_OVER = "game_over"
LEADERBOARD = "leaderboard"

state = LOGIN

# VARIABLES

player_name = ""
user_text = ""
winner = ""

maze = None
player = None
ai = None
powerups = None

start_time = 0
difficulty = "MEDIUM"

# START GAME

def start_game():
    global maze, player, ai, powerups, start_time, state, winner

    winner = ""

    if difficulty == "EASY":
        size, ai_speed, reveal = 12, 12, 8
    elif difficulty == "MEDIUM":
        size, ai_speed, reveal = 18, 9, 6
    else:
        size, ai_speed, reveal = 25, 7, 4

    maze = Maze(size)

    maze.memory_state = "VISIBLE"
    maze.visible_cells = set()
    maze.last_switch_time = time.time()
    maze.cycle_duration = reveal

    player = Player(maze.start)
    ai = AIPlayer(maze.start)
    ai.move_delay = ai_speed

    powerups = PowerUpManager(maze)

    start_time = time.time()
    state = PLAYING



# BUTTON UI
def button(x, y, w, h, text):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    rect = pygame.Rect(x, y, w, h)
    hover = rect.collidepoint(mouse)

    color = (60, 60, 120)
    if hover:
        color = (0, 160, 255)

    pygame.draw.rect(screen, color, rect, border_radius=12)

    label = font_med.render(text, True, (255, 255, 255))
    screen.blit(label, (
        x + (w - label.get_width()) // 2,
        y + (h - label.get_height()) // 2
    ))

    return hover and click[0]



# MAIN LOOP
running = True

while running:

    clock.tick(FPS)
    screen.fill((10, 10, 25))
    keys = pygame.key.get_pressed()


    # EVENTS
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # LOGIN
        if state == LOGIN:
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN and user_text != "":
                    player_name = user_text
                    state = MENU

                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]

                else:
                    if len(user_text) < 12:
                        user_text += event.unicode

        # PLAYING
        elif state == PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state = PAUSE

        # PAUSE
        elif state == PAUSE:
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    state = PLAYING

                elif event.key == pygame.K_r:
                    start_game()

                elif event.key == pygame.K_m:
                    state = MENU

        # GAME OVER
        elif state == GAME_OVER:
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_r:
                    start_game()

                elif event.key == pygame.K_m:
                    state = MENU

        # LEADERBOARD
        elif state == LEADERBOARD:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state = MENU


    # LOGIN SCREEN
    if state == LOGIN:

        title = font_big.render("MEMORY MAZE", True, (0, 220, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))

        box = pygame.Rect(WIDTH//2 - 220, 300, 440, 65)
        pygame.draw.rect(screen, (40, 40, 70), box, border_radius=12)

        text = font_med.render(user_text, True, (255, 255, 255))
        screen.blit(text, (box.x + 20, box.y + 18))

        hint = font_small.render("Enter Username & Press ENTER", True, (180,180,180))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, 400))

  
    # MENU
    elif state == MENU:

        title = font_big.render("MEMORY MAZE", True, (0, 220, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))

        welcome = font_small.render(f"Welcome {player_name}", True, (255,255,0))
        screen.blit(welcome, (WIDTH//2 - welcome.get_width()//2, 180))

        if button(WIDTH//2 - 150, 270, 300, 60, "START GAME"):
            state = DIFFICULTY

        if button(WIDTH//2 - 150, 350, 300, 60, "LEADERBOARD"):
            state = LEADERBOARD

        if button(WIDTH//2 - 150, 430, 300, 60, "EXIT"):
            pygame.quit()
            sys.exit()

    #ui 
    elif state == DIFFICULTY:

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        title = font_big.render("SELECT DIFFICULTY", True, (255, 215, 0))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 70))

        sub = font_small.render("Choose your challenge level", True, (220,220,220))
        screen.blit(sub, (WIDTH//2 - sub.get_width()//2, 145))

        if button(WIDTH//2 - 180, 220, 360, 70, "EASY"):
            difficulty = "EASY"
            start_game()

        easy = font_small.render("Small Maze | Slow AI | 8s Reveal", True, (180,255,180))
        screen.blit(easy, (WIDTH//2 - easy.get_width()//2, 295))

        if button(WIDTH//2 - 180, 340, 360, 70, "MEDIUM"):
            difficulty = "MEDIUM"
            start_game()

        med = font_small.render("Balanced Maze | Normal AI | 6s Reveal", True, (255,255,180))
        screen.blit(med, (WIDTH//2 - med.get_width()//2, 415))

        if button(WIDTH//2 - 180, 460, 360, 70, "HARD"):
            difficulty = "HARD"
            start_game()

        hard = font_small.render("Large Maze | Fast AI | 4s Reveal", True, (255,180,180))
        screen.blit(hard, (WIDTH//2 - hard.get_width()//2, 535))

        if button(WIDTH//2 - 120, 610, 240, 55, "BACK"):
            state = MENU

  
    # PLAYING
    elif state == PLAYING:

        maze.update_memory_cycle()

        player.handle_input(keys, maze)
        ai.update(maze)
        powerups.update(player, ai)

        maze.draw(screen)
        player.draw(screen)
        ai.draw(screen)
        powerups.draw(screen)

        elapsed = int(time.time() - start_time)

        screen.blit(font_small.render(f"Time: {elapsed}s", True, (255,255,255)), (20,20))

        if (player.row, player.col) == maze.exit:
            winner = "PLAYER"
            save_score(player_name, "PLAYER", elapsed, player.penalty_time)
            state = GAME_OVER

        if (ai.row, ai.col) == maze.exit:
            winner = "AI"
            save_score(player_name, "AI", elapsed, player.penalty_time)
            state = GAME_OVER

    # PAUSE
    elif state == PAUSE:

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0,0,0))
        screen.blit(overlay, (0,0))

        title = font_big.render("PAUSED", True, (255,255,0))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))

        if button(WIDTH//2 - 150, 260, 300, 60, "RESUME"):
            state = PLAYING

        if button(WIDTH//2 - 150, 340, 300, 60, "RESTART"):
            start_game()

        if button(WIDTH//2 - 150, 420, 300, 60, "MAIN MENU"):
            state = MENU

    # GAME OVER
    elif state == GAME_OVER:

        result = "PLAYER WINS!" if winner == "PLAYER" else "AI WINS!"

        screen.blit(font_big.render("GAME OVER", True, (0,255,120)),
                    (WIDTH//2 - 220, 120))

        screen.blit(font_big.render(result, True, (255,255,0)),
                    (WIDTH//2 - 250, 220))

        screen.blit(font_med.render("R - Restart | M - Menu", True, (255,255,255)),
                    (WIDTH//2 - 180, 340))

    # LEADERBOARD
    elif state == LEADERBOARD:

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0,0,0))
        screen.blit(overlay, (0,0))

        title = font_big.render("LEADERBOARD", True, (0,200,255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))

        scores = load_scores()

        y = 160

        if not scores:
            msg = font_med.render("No scores yet", True, (255,255,255))
            screen.blit(msg, (WIDTH//2 - msg.get_width()//2, y))
        else:
            for s in scores[-10:][::-1]:
                text = f"{s['player']} | {s['winner']} | {s['time']}s"
                row = font_small.render(text, True, (255,255,255))
                screen.blit(row, (WIDTH//2 - 160, y))
                y += 40

        if button(WIDTH//2 - 150, HEIGHT - 90, 300, 60, "BACK TO MENU"):
            state = MENU

    pygame.display.flip()

pygame.quit()
sys.exit()