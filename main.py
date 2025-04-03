import pygame
import random
import os
import sys

# Inițializare pygame
pygame.init()

# Setări ecran
WIDTH, HEIGHT = 400, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird Clone")

# Calea către fișierele de resurse
if getattr(sys, 'frozen', False):
    # Dacă aplicația este rulată dintr-un executabil PyInstaller
    resource_path = sys._MEIPASS  # Calea temporară unde sunt stocate fișierele la rulare
else:
    # Dacă aplicația este rulată din sursa Python
    resource_path = os.path.dirname(__file__)

# Încărcare imagini
BACKGROUND_DAY = pygame.image.load(os.path.join(resource_path, "flappy_assets", "background_day.png"))  # Fundal zi
BACKGROUND_NIGHT = pygame.image.load(os.path.join(resource_path, "flappy_assets", "background_night.png"))  # Fundal seară
BIRD = pygame.image.load(os.path.join(resource_path, "flappy_assets", "bird.png"))
PIPE = pygame.image.load(os.path.join(resource_path, "flappy_assets", "pipe.png"))
PIPE_FLIPPED = pygame.transform.flip(PIPE, False, True)

# Fonturi
font = pygame.font.Font(None, 36)
menu_font = pygame.font.Font(None, 48)  # Adăugarea fontului pentru meniuri
return_font = pygame.font.Font(None, 24)  # Font mai mic pentru textul de revenire

# Sunete
flap_sound = pygame.mixer.Sound(os.path.join(resource_path, "flappy_assets", "flap.wav"))

# Fișier scoruri
SCORE_FILE = os.path.join(resource_path, "scores.txt")

# Verificare și crearea fișierului de scoruri dacă nu există
def initialize_score_file():
    if not os.path.exists(SCORE_FILE):
        with open(SCORE_FILE, 'w') as file:
            file.write("")  # Crează fișierul gol dacă nu există

initialize_score_file()

def save_score(score):
    scores = load_scores()  # Încărcăm scorurile existente
    scores.append(score)  # Adăugăm scorul nou la lista de scoruri
    scores.sort(reverse=True)  # Sortăm scorurile în ordine descrescătoare
    # Păstrăm doar primele 5 scoruri, dacă sunt mai multe
    scores = scores[:5]
    
    with open(SCORE_FILE, "w") as file:
        for score in scores:
            file.write(str(score) + "\n")

def load_scores():
    if not os.path.exists(SCORE_FILE):
        return []
    with open(SCORE_FILE, "r") as file:
        return [int(line.strip()) for line in file.readlines()]

def show_menu():
    while True:
        SCREEN.fill((30, 30, 30))  # Fundal gri închis
        title = font.render("Flappy Bird", True, (255, 255, 0))
        start = menu_font.render("1. Start", True, (255, 255, 255))
        scores = menu_font.render("2. Scores", True, (255, 255, 255))
        quit_game = menu_font.render("3. Quit", True, (255, 255, 255))
        
        SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        SCREEN.blit(start, (WIDTH // 2 - start.get_width() // 2, 200))
        SCREEN.blit(scores, (WIDTH // 2 - scores.get_width() // 2, 260))
        SCREEN.blit(quit_game, (WIDTH // 2 - quit_game.get_width() // 2, 320))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return  # Start joc
                elif event.key == pygame.K_2:
                    show_scores()
                elif event.key == pygame.K_3:
                    pygame.quit()
                    exit()

def show_scores():
    scores = load_scores()
    while True:
        SCREEN.fill((30, 30, 30))
        title = font.render("High Scores", True, (255, 255, 0))
        SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
        
        for i, score in enumerate(scores):
            score_text = menu_font.render(f"{i+1}. {score}", True, (255, 255, 255))
            SCREEN.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 120 + i * 40))
        
        # Folosim textul cu fontul mai mic
        exit_text = return_font.render("Press any key to return", True, (200, 200, 200))
        SCREEN.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, 400))  # Ajustăm poziția pe axa Y
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                return  # Revenire la meniu

def game_over(score):
    save_score(score)  # Salvează scorul la final
    while True:
        SCREEN.fill((30, 30, 30))
        game_over_text = font.render("Game Over!", True, (255, 0, 0))
        score_text = font.render(f"Score: {score}", True, (255, 255, 0))
        SCREEN.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, 150))
        SCREEN.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 220))
        
        # Schimbăm textul "Press any key to return" folosind fontul mic și îl centrăm
        restart_text = return_font.render("Press any key to return to menu", True, (255, 255, 255))
        SCREEN.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, 300))  # Ajustăm poziția pe axa Y
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                return  # Revenire la meniu

def game_loop():
    # Variabile pentru joc
    bird_x, bird_y = 100, HEIGHT // 2
    bird_vel_y = 0
    gravity = 0.5
    flap_strength = -8
    pipes = []
    score = 0
    bird_rect = pygame.Rect(bird_x, bird_y, BIRD.get_width(), BIRD.get_height())

    # Temporizator pentru apariția pipe-urilor
    pipe_timer = pygame.time.get_ticks()

    # Viteza pipe-urilor (mai lent la început)
    pipe_speed = 3

    # Timpul de început al jocului
    start_time = pygame.time.get_ticks()

    while True:
        # Verificăm dacă a trecut 10 secunde
        elapsed_time = pygame.time.get_ticks() - start_time
        if elapsed_time >= 10000:  # 10 secunde = 10000 ms
            SCREEN.blit(BACKGROUND_NIGHT, (0, 0))  # Schimbăm fundalul cu cel de seară
        else:
            SCREEN.blit(BACKGROUND_DAY, (0, 0))  # Fundal zi

        # Evenimente de input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird_vel_y = flap_strength  # Bird flap
                    flap_sound.play()

        # Muta bird-ul cu gravitație
        bird_vel_y += gravity
        bird_y += bird_vel_y
        bird_rect.y = bird_y

        # Coliziune cu solul
        if bird_rect.bottom >= HEIGHT:
            game_over(score)
            return

        # Adăugare pipe-uri noi
        if pygame.time.get_ticks() - pipe_timer > 2000:  # Pipe-uri la fiecare 2s (distanta mai mică între pipe-uri)
            pipe_height = random.randint(150, HEIGHT - 200)  # Creăm un spațiu normal între pipe-uri
            top_pipe = pygame.Rect(WIDTH, 0, PIPE.get_width(), pipe_height)
            bottom_pipe = pygame.Rect(WIDTH, pipe_height + 200, PIPE.get_width(), HEIGHT - pipe_height - 200)
            pipes.append((top_pipe, bottom_pipe))
            pipe_timer = pygame.time.get_ticks()

        # Muta pipe-urile și detectează coliziuni
        for top_pipe, bottom_pipe in pipes[:]:
            top_pipe.x -= pipe_speed
            bottom_pipe.x -= pipe_speed
            if top_pipe.right < 0:
                pipes.remove((top_pipe, bottom_pipe))
                score += 1  # Crește scorul dacă pipe-ul este depășit

            # Verificare coliziune directă între pasăre și pipe
            if bird_rect.colliderect(top_pipe) or bird_rect.colliderect(bottom_pipe):
                game_over(score)
                return

            SCREEN.blit(PIPE_FLIPPED, top_pipe)  # Pipe-ul de sus
            SCREEN.blit(PIPE, bottom_pipe)  # Pipe-ul de jos

        # Creșterea vitezei păsării și a dificultății pe măsură ce scorul crește
        flap_strength = -8 - (score // 10)  # Pasărea zboară mai sus pe măsură ce scorul crește
        gravity = 0.5 + (score // 10) * 0.1  # Crește gravitația pe măsură ce scorul crește

        # Creșterea vitezei pipe-urilor
        pipe_speed = 3 + (score // 5)  # Pipe-urile devin mai rapide pe măsură ce scorul crește

        # Desenează pasărea
        SCREEN.blit(BIRD, bird_rect)

        # Afisează scorul
        score_text = font.render(f"Score: {score}", True, (255, 255, 0))
        SCREEN.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))

        pygame.display.update()

        # Limitează frame rate-ul
        pygame.time.Clock().tick(60)

# Începe jocul
while True:
    show_menu()
    game_loop()

pygame.quit()
