import pygame
import sys
import csv
import tkinter as tk
from tkinter import simpledialog
pygame.init()
font = pygame.font.SysFont(None, 36)

# Näytön asetukset
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pepen mahtava seikkailu")

current_level = 1 

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
Red = (255, 0, 0)
Green = (0, 255, 0)
GRAY = (200, 200, 200)

STATE_MENU = "menu"
STATE_GAME = "game"
STATE_LEADERBOARD = "leaderboard"
state = STATE_MENU

# Placeholder background for menu and leaderboard
menu_bg = pygame.image.load("Images/pixil-frame-0_8.png")

leaderboard_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
leaderboard_bg.fill(WHITE)

# button koot
button_width, button_height = 150, 50
start_button = pygame.Rect((10, 500), (button_width, button_height))
quit_button = pygame.Rect((225, 500), (button_width, button_height))
leaderboard_button = pygame.Rect((440, 500), (button_width, button_height))

# aika data
leaderboard_results = []

def draw_menu():
    screen.blit(menu_bg, (0, 0))
    title_text = font.render("Pepen mahtava seikkailu", True, BLACK)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
    pygame.draw.rect(screen, BLACK, start_button)
    pygame.draw.rect(screen, BLACK, quit_button)
    pygame.draw.rect(screen, BLACK, leaderboard_button)
    start_text = font.render("Aloita peli", True, WHITE)
    quit_text = font.render("Lopeta", True, WHITE)
    leaderboard_text = font.render("Tulostaulu", True, WHITE)
    screen.blit(start_text, (start_button.centerx - start_text.get_width() // 2, start_button.centery - start_text.get_height() // 2))
    screen.blit(quit_text, (quit_button.centerx - quit_text.get_width() // 2, quit_button.centery - quit_text.get_height() // 2))
    screen.blit(leaderboard_text, (leaderboard_button.centerx - leaderboard_text.get_width() // 2, leaderboard_button.centery - leaderboard_text.get_height() // 2))

def draw_leaderboard():
    screen.blit(leaderboard_bg, (0, 0))
    title_text = font.render("Tulostaulu", True, BLACK)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
    
    # näytä ajat
    y_offset = 120
    if leaderboard_results:
        for i, (player, time) in enumerate(leaderboard_results[:10], start=1):
            entry_text = font.render(f"{i}. {player}: {time}s", True, BLACK)
            screen.blit(entry_text, (50, y_offset))
            y_offset += 30
    else:
        no_results_text = font.render("Ei tuloksia tallennettu.", True, BLACK)
        screen.blit(no_results_text, (SCREEN_WIDTH // 2 - no_results_text.get_width() // 2, 120))
    
    back_text = font.render("Palaa valikkoon (B)", True, BLACK)
    screen.blit(back_text, (10, SCREEN_HEIGHT - 40))

def load_leaderboard():
    global leaderboard_results
    try:
        with open("game_results.csv", "r") as csvfile:
            csv_reader = csv.reader(csvfile)
            leaderboard_results = list(csv_reader)[1:]  # ohita row 1
            leaderboard_results.sort(key=lambda x: float(x[1]))  # sort ajalla
    except FileNotFoundError:
        leaderboard_results = []

def get_player_name():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    name = simpledialog.askstring("Player Name", "Enter your player name:")
    root.destroy()
    return name if name else "Anonymous"

player_name = get_player_name()

def save_score(name, time):
    global leaderboard_results
    updated = False
    
    # Load existing results
    load_leaderboard()
    
    # Check if the player already has a score
    for entry in leaderboard_results:
        if entry[0] == name:
            if float(entry[1]) > time:  # Update if the new time is faster
                entry[1] = str(time)
            updated = True
            break

    # If not found, add a new entry
    if not updated:
        leaderboard_results.append([name, str(time)])

    # Save back to CSV
    with open("game_results.csv", "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["Player", "Time (s)"])
        csv_writer.writerows(leaderboard_results)


ground_img = pygame.Surface((200, 20))
ground_img.fill(BLACK)
# pelaajan asetukset
player_width = 40
player_height = 60
player_x = 0
player_y = SCREEN_HEIGHT - player_height - 100
player_speed = 5
player_jump_power = 15
player_gravity = 0.8
player_velocity_y = 0
on_ground = False

# ryhmät
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
stars = pygame.sprite.Group()

# pelaaja
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((player_width, player_height))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocity_y = 0
        self.on_ground = False

    def update(self, keys):
        # liikkuminen
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rect.x -= player_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rect.x += player_speed
        if keys[pygame.K_LSHIFT] and keys[pygame.K_d] or keys[pygame.K_LSHIFT] and keys[pygame.K_RIGHT]:
            self.rect.x += player_speed * 1.145
        if keys[pygame.K_LSHIFT] and keys[pygame.K_a] or keys[pygame.K_LSHIFT] and keys[pygame.K_LEFT]:
            self.rect.x -= player_speed * 1.145
        
        # hyppy
        if keys[pygame.K_SPACE] and self.on_ground or keys[pygame.K_w] and self.on_ground:
            self.velocity_y = -player_jump_power
            self.on_ground = False

        # apply gravity
        self.velocity_y += player_gravity
        self.rect.y += self.velocity_y

        # tarkista osuminen
        self.check_platform_collision()

    def check_platform_collision(self):
        self.on_ground = False  # pelaaja ei ole maassa
        for platform in platforms:
            # kuole platformin logiikka
            if platform.rect.height == 1:  # onko kuolema pplatformi
                if self.velocity_y > 0 and self.rect.bottom >= platform.rect.top and self.rect.top < platform.rect.top:
                    # osuuko päälle
                    global current_level
                    current_level = 1  # resetoi to level 1
                    load_level(current_level)  # Reload level 1
                    return  # lopeta looppaaminen

            # Normal platform collision
            if self.rect.colliderect(platform.rect):
                # Horizontal collision
                if self.rect.right >= platform.rect.left and self.rect.left < platform.rect.left:
                    # Collides from the left
                    self.rect.right = platform.rect.left
                    self.velocity_y = 0
                elif self.rect.left <= platform.rect.right and self.rect.right > platform.rect.right:
                    # Collides from the right
                    self.rect.left = platform.rect.right
                    self.velocity_y = 0
                else:
                    # Vertical collision
                    if self.velocity_y > 0 and self.rect.bottom >= platform.rect.top and self.rect.top < platform.rect.top:
                        # Land on top
                        self.rect.bottom = platform.rect.top
                        self.velocity_y = 0
                        self.on_ground = True
                    elif self.velocity_y < 0 and self.rect.top >= platform.rect.bottom + self.velocity_y:
                        # Hit the platform from below
                        self.rect.top = platform.rect.bottom
                        self.velocity_y = 0
              
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width=200, height=20, color=BLACK):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)  # käytä annettua väriä
        self.rect = self.image.get_rect(topleft=(x, y))

player = Player(player_x, player_y)
all_sprites.add(player)

def load_level(level):
    global bg, platform_positions, exit_area, player
    # lopeta kaikki muu musiikki
    pygame.mixer.music.stop()

    # Platformit ja poistumiset
    if level == 1:
        bg = pygame.image.load("Images/pixil-frame-0.png")
        platform_positions = [
            (0, 590),
            (150, 500),
            (250, 400),
            (300 + 50, 300, SCREEN_WIDTH - (400 + 50), 20),
            (100, 200),
            (300 + 50, 100, SCREEN_WIDTH - (400 + 50), 20),
            (500, 100, 50, 600),
            (0, SCREEN_HEIGHT - 1, SCREEN_WIDTH, 1)  # 1-kuolemis death platform
        ]
        platform_colors = [GRAY, GRAY, GRAY, GRAY, GRAY, GRAY, GRAY, BLACK]  # Red for death platform
        exit_area = pygame.Rect(SCREEN_WIDTH - 50, SCREEN_HEIGHT - 50, 50, 50)  # poistumis area for level 1
        # Musiikki tasolle 1
        try:
            pygame.mixer.music.load("Music/stage_music.wav")
            pygame.mixer.music.play(-1)  # loop ikuisesti
        except pygame.error as e:
            print(f"Error loading music: {e}")

    elif level == 2:
        bg = pygame.image.load("Images/pixil-frame-0_1.png")
        platform_positions = [
            (0, 590, 210),
            (190, 90, 20, 600),
            (190, 80, 320, 20),
            (490, 90, 20, 300),
            (120, 500, 80),
            (0, 400, 80),
            (120, 290, 80),
            (0, 180, 80),
            (500, 150, 50),
            (550, 250, 50),
            (500, 350, 50),
            (400, 460, 200),
            (400, 320, 100, 20),
            (400, 200, 20, 120),
            (260, 460, 80),
            (200, 350, 80),
            (350, 250, 50),
            (0, SCREEN_HEIGHT - 1, SCREEN_WIDTH, 1)  # 1-pixel kuolemis platform
        ]
        platform_colors = []
        exit_area = pygame.Rect(420, 270, 80, 50)  # poistumis area for level 2
        # Musiikki tasolle 2
        try:
            pygame.mixer.music.load("Music/stage_music2.wav") #placeholder
            pygame.mixer.music.play(-1)  # loop ikuisesti
        except pygame.error as e:
            print(f"Error loading music: {e}")

    elif level == 3:
        bg = pygame.image.load("Images/pixil-frame-0_2.png")
        platform_positions = [
            (0, 590, 70),
            (100, 500, 90),
            (300, 500, 90),
            (500, 400, 100),
            (300, 300, 95),
            (150, 200, 95),
            (450, 150, 200),
            (0, SCREEN_HEIGHT - 1, SCREEN_WIDTH, 1)  # 1-pixel kuolemis platform
        ]
        platform_colors = []
        exit_area = pygame.Rect(600 - 60, 20, 40, 40)  # poistumis area for level 3

    elif level == 4:
        bg = pygame.image.load("Images/pixil-frame-0_3.png")
        platform_positions = [
            (0, 590, 70, 20),
            (100, 500, 70, 20),
            (0, 400, 70, 20),
            (100, 300, 70, 20),
            (0, 200, 70, 20),
            (80, 100, 100, 20),
            (220, 50, 300, 20),
            (500, 0, 50, SCREEN_HEIGHT),
            (0, SCREEN_HEIGHT - 1, SCREEN_WIDTH, 1)  # 1-pixel kuolemis platform
        ]
        platform_colors = []
        exit_area = pygame.Rect(SCREEN_WIDTH - 50, SCREEN_HEIGHT - 50, 50, 50)

    elif level == 5:
        bg = pygame.image.load("Images/pixil-frame-0_7.png")
        platform_positions = [
            (0, 500, 100),
            (200, 550, 100),
            (400, 500, 100),
            (500, 400),
            (300, 300, 100),
            (500, 200, 100),
            (400, 100, 150, 20),
            (0, SCREEN_HEIGHT - 1, SCREEN_WIDTH, 1)  # 1-pixel kuolemis platform
        ]
        platform_colors = [Green,Green,Green,Green,Green,Green,Green,Green,Green,Green,Green,Green,Green,Green,Green,Green,]
        exit_area = pygame.Rect(300, 40, 50, 50)  # poistumis area for level 5


    # Clear existing platforms and sprites
    platforms.empty()
    all_sprites.empty()
    all_sprites.add(player)  # Add the player back to the sprite group
    
    for i, pos in enumerate(platform_positions):
        color = platform_colors[i] if i < len(platform_colors) else BLACK  # käytä mustaa jos väriä ei anneta
        platform = Platform(*pos, color=color)
        platforms.add(platform)
        all_sprites.add(platform)

    # Reset player position and velocity
    player.rect.topleft = (0, SCREEN_HEIGHT - player_height - 100)
    player.velocity_y = 0

# Initial level load
load_level(current_level)     

# Main game loop
clock = pygame.time.Clock()
start_time = pygame.time.get_ticks()  # Start timer
running = True
game_completed = False

# Main game loop
while running:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif state == STATE_MENU:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    state = STATE_GAME
                    start_time = pygame.time.get_ticks()
                    load_level(current_level)
                elif quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
                elif leaderboard_button.collidepoint(event.pos):
                    state = STATE_LEADERBOARD
                    load_leaderboard()
        elif state == STATE_LEADERBOARD:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                state = STATE_MENU

    if state == STATE_MENU:
        draw_menu()
        pygame.display.flip()
    elif state == STATE_LEADERBOARD:
        draw_leaderboard()
        pygame.display.flip()
    elif state == STATE_GAME:
        # tapahtumat (event handling)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    if current_level < 5:  #  current_level ei voi olla suurempi kuin 5
                        current_level += 1
                        load_level(current_level)
                    else:
                        draw_menu()

        # Update player
        keys = pygame.key.get_pressed()
        player.update(keys)

        # Näyttö boundaries
        if player.rect.left < 0:
            player.rect.left = 0
        elif player.rect.right > SCREEN_WIDTH:
            player.rect.right = SCREEN_WIDTH
        if player.rect.bottom > SCREEN_HEIGHT:
            player.rect.bottom = SCREEN_HEIGHT
            player.velocity_y = 0
            player.on_ground = True

        # Timer logic
        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000  # muuta sekunneiksi
        timer_text = font.render(f"Aika: {elapsed_time}s", True, BLACK) 

        # Check for level completion
        if player.rect.colliderect(exit_area) and not game_completed:
            if current_level < 5:  # Check if there are more levels
                current_level += 1
                load_level(current_level)
            else:  # Final level completed
                save_score(player_name, elapsed_time)  # Save the player's time
                game_completed = True
                print("Peli valmis. Aika tallennettu csveen.")
                pygame.quit()

        # piirrä peli (draw everything)
        screen.blit(bg, (0, 0))  # Draw the background
        pygame.draw.rect(screen, (255, 0, 0), exit_area)  # Draw poistumis area
        all_sprites.draw(screen)  # Draw all sprites
        screen.blit(timer_text, (10, 10))  # Draw the timer
        
        # Päivitä näyttö (update the display)
        pygame.display.flip()
        clock.tick(60)  # 60 FPS
        pass