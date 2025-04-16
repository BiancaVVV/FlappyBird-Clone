import pygame
import random
import os
import sys

pygame.init()

WIDTH, HEIGHT = 400, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird Clone")

if getattr(sys, 'frozen', False):
    resource_path = sys._MEIPASS
else:
    resource_path = os.path.dirname(__file__)

BACKGROUND_DAY = pygame.image.load(os.path.join(resource_path, "flappy_assets", "background_day.png"))
BACKGROUND_NIGHT = pygame.image.load(os.path.join(resource_path, "flappy_assets", "background_night.png"))
BIRD = pygame.image.load(os.path.join(resource_path, "flappy_assets", "bird.png"))
PIPE = pygame.image.load(os.path.join(resource_path, "flappy_assets", "pipe.png"))
PIPE_FLIPPED = pygame.transform.flip(PIPE, False, True)

font = pygame.font.Font(None, 36)
menu_font = pygame.font.Font(None, 48)
return_font = pygame.font.Font(None, 24)

flap_sound = pygame.mixer.Sound(os.path.join(resource_path, "flappy_assets", "flap.wav"))

SCORE_FILE = os.path.join(resource_path, "scores.txt")

def initialize_score_file():
    if not os.path.exists(SCORE_FILE):
        with open(SCORE_FILE, 'w') as file:
            file.write("")

initialize_score_file()

def save_score(score):
    scores = load_scores()
    scores.append(score)
    scores.sort(reverse=True)
    scores = scores[:5]
    with open(SCORE_FILE, "w") as file:
        for score in scores:
            file.write(str(score) + "\n")

def load_scores():
    if not os.path.exists(SCORE_FILE):
        return []
    with open(SCORE_FILE, "r") as file:
        return [int(line.strip()) for line in file.readlines()]

controller_connected = False
joystick = None
using_controller = False

pygame.joystick.init()

def check_controller():
    global controller_connected, joystick
    if pygame.joystick.get_count() > 0:
        if joystick is None:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
        controller_connected = True
    else:
        controller_connected = False
        joystick = None

def is_using_controller():
    return using_controller and controller_connected

check_controller()

def show_menu():
    global using_controller
    while True:
        check_controller()
        SCREEN.fill((30, 30, 30))
        title = font.render("Flappy Bird", True, (255, 255, 0))

        if is_using_controller():
            start = menu_font.render("X - Start", True, (255, 255, 255))
            scores = menu_font.render("O - Scores", True, (255, 255, 255))
            quit_game = menu_font.render(" - Quit", True, (255, 255, 255))
            # Draw a larger square around the Quit button
            pygame.draw.rect(SCREEN, (255, 255, 255), (WIDTH // 2 - 80, 320, 30, 30), 2)
        else:
            start = menu_font.render("1. Start", True, (255, 255, 255))
            scores = menu_font.render("2. Scores", True, (255, 255, 255))
            quit_game = menu_font.render("3. Quit", True, (255, 255, 255))

        SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        SCREEN.blit(start, (WIDTH // 2 - start.get_width() // 2, 200))
        SCREEN.blit(scores, (WIDTH // 2 - scores.get_width() // 2, 260))
        SCREEN.blit(quit_game, (WIDTH // 2 - quit_game.get_width() // 2, 320))

        control_text = font.render("Controller" if is_using_controller() else "Tastatura", True, (0, 255, 0))
        SCREEN.blit(control_text, (WIDTH - control_text.get_width() - 10, 10))

        if controller_connected:
            switch_text = return_font.render("Triangle - Switch to Keyboard" if is_using_controller() else "Press T to switch to Controller", True, (200, 200, 200))
            SCREEN.blit(switch_text, (WIDTH // 2 - switch_text.get_width() // 2, 380))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if is_using_controller() and controller_connected and event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:  # X button pressed
                    return
                elif event.button == 1:  # O button pressed
                    show_scores()
                elif event.button == 2:  # Square (Quit)
                    pygame.quit()
                    exit()
                elif event.button == 3:  # Triangle (Switch to Keyboard)
                    using_controller = False

            elif not is_using_controller() and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:  # Keyboard start
                    return
                elif event.key == pygame.K_2:  # Keyboard scores
                    show_scores()
                elif event.key == pygame.K_3:  # Keyboard quit
                    pygame.quit()
                    exit()
                elif event.key == pygame.K_t and controller_connected:  # Switch to controller (T key)
                    using_controller = True

def show_scores():
    scores = load_scores()
    while True:
        SCREEN.fill((30, 30, 30))
        title = font.render("High Scores", True, (255, 255, 0))
        SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        for i, score in enumerate(scores):
            score_text = menu_font.render(f"{i+1}. {score}", True, (255, 255, 255))
            SCREEN.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 120 + i * 40))

        exit_text = return_font.render("Press any key to return", True, (200, 200, 200))
        SCREEN.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, 400))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                return

def game_over(score):
    save_score(score)
    if is_using_controller():
        joystick.rumble(1, 1, 500)
    while True:
        SCREEN.fill((30, 30, 30))
        game_over_text = font.render("Game Over!", True, (255, 0, 0))
        score_text = font.render(f"Score: {score}", True, (255, 255, 0))
        SCREEN.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, 150))
        SCREEN.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 220))

        restart_text = return_font.render("Press any key to return to menu", True, (255, 255, 255))
        SCREEN.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, 300))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                return
            if event.type == pygame.JOYBUTTONDOWN:
                return

def game_loop():
    bird_x, bird_y = 100, HEIGHT // 2
    bird_vel_y = 0
    gravity = 0.5
    flap_strength = -8
    pipes = []
    score = 0
    bird_rect = pygame.Rect(bird_x, bird_y, BIRD.get_width(), BIRD.get_height())
    pipe_timer = pygame.time.get_ticks()
    pipe_speed = 3
    start_time = pygame.time.get_ticks()

    while True:
        elapsed_time = pygame.time.get_ticks() - start_time
        if elapsed_time >= 10000:
            SCREEN.blit(BACKGROUND_NIGHT, (0, 0))
        else:
            SCREEN.blit(BACKGROUND_DAY, (0, 0))

        check_controller()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if is_using_controller() and controller_connected and event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:  # A button pressed
                    bird_vel_y = flap_strength
                    flap_sound.play()

            elif not is_using_controller() and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # Space key pressed for flap
                    bird_vel_y = flap_strength
                    flap_sound.play()

        bird_vel_y += gravity
        bird_y += bird_vel_y
        bird_rect.y = bird_y

        if bird_rect.bottom >= HEIGHT:
            game_over(score)
            return

        if pygame.time.get_ticks() - pipe_timer > 2000:
            pipe_height = random.randint(150, HEIGHT - 200)
            top_pipe = pygame.Rect(WIDTH, 0, PIPE.get_width(), pipe_height)
            bottom_pipe = pygame.Rect(WIDTH, pipe_height + 200, PIPE.get_width(), HEIGHT - pipe_height - 200)
            pipes.append((top_pipe, bottom_pipe))
            pipe_timer = pygame.time.get_ticks()

        for top_pipe, bottom_pipe in pipes[:]:
            top_pipe.x -= pipe_speed
            bottom_pipe.x -= pipe_speed
            if top_pipe.right < 0:
                pipes.remove((top_pipe, bottom_pipe))
                score += 1

            if bird_rect.colliderect(top_pipe) or bird_rect.colliderect(bottom_pipe):
                game_over(score)
                return

            SCREEN.blit(PIPE_FLIPPED, top_pipe)
            SCREEN.blit(PIPE, bottom_pipe)

        flap_strength = -8 - (score // 10)
        gravity = 0.5 + (score // 10) * 0.1
        pipe_speed = 3 + (score // 5)

        SCREEN.blit(BIRD, bird_rect)
        score_text = font.render(f"Score: {score}", True, (255, 255, 0))
        SCREEN.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))

        control_text = font.render("Controller" if is_using_controller() else "Tastatura", True, (0, 255, 0))
        SCREEN.blit(control_text, (WIDTH - control_text.get_width() - 10, 10))

        pygame.display.update()
        pygame.time.Clock().tick(60)

using_controller = False

while True:
    show_menu()
    game_loop()

pygame.quit()
