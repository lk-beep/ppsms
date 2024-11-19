import pygame
import sys
import csv
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

ground_img = pygame.Surface((200, 20))  # Placeholder for platform image
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
        if keys[pygame.K_LSHIFT] and keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rect.x += player_speed*1.145
        if keys[pygame.K_LSHIFT] and keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rect.x -= player_speed*1.145
        # Jump
        if keys[pygame.K_SPACE] and self.on_ground or keys[pygame.K_w] and self.on_ground:
            self.velocity_y = -player_jump_power
            self.on_ground = False

        # gravity
        self.velocity_y += player_gravity
        self.rect.y += self.velocity_y

        self.check_platform_collision()
        
    def check_platform_collision(self):
        self.on_ground = False  # Oletuksena pelaaja ei ole maassa
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # sivujen collision check
                if self.rect.right >= platform.rect.left and self.rect.left < platform.rect.left:
                    #  osuuko vasemmalta
                    self.rect.right = platform.rect.left
                    self.velocity_y = 0
                    self.on_ground = False
                elif self.rect.left <= platform.rect.right and self.rect.right > platform.rect.right:
                    # osuuko oikealta
                    self.rect.left = platform.rect.right
                    self.velocity_y = 0
                    self.on_ground = False
                else:
                    # sivujen collision check
                    if self.velocity_y > 0 and self.rect.bottom >= platform.rect.top and self.rect.top < platform.rect.top:
                        # Osuuko päällä
                        self.rect.bottom = platform.rect.top
                        self.velocity_y = 0
                        self.on_ground = True
                    elif self.velocity_y < 0 and self.rect.top >= platform.rect.bottom + self.velocity_y:
                        # osuuko alta
                        self.rect.top = platform.rect.bottom
                        self.velocity_y = 0
                    
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width=200, height=20):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect(topleft=(x, y))


player = Player(player_x, player_y)
all_sprites.add(player)
# tee poistumis area
EXIT_WIDTH = 50
EXIT_HEIGHT = 50
exit_area = pygame.Rect(SCREEN_WIDTH - EXIT_WIDTH, SCREEN_HEIGHT - EXIT_HEIGHT, EXIT_WIDTH, EXIT_HEIGHT)

def load_level(level):
    global bg, platform_positions, player
    #green mountain
    if level == 1:
        bg = pygame.image.load("ppsms/Images/pixil-frame-0.png")
        platform_positions = [
            (0, 590),
            (150, 500),
            (250, 400),
            (300 + EXIT_WIDTH, 300, SCREEN_WIDTH - (400 + EXIT_WIDTH), 20),
            (100, 200),
            (300 + EXIT_WIDTH, 100, SCREEN_WIDTH - (400 + EXIT_WIDTH), 20),
            (500, 100, 50, 600)
        ]
    # well    
    elif level == 2:
        bg = pygame.image.load("ppsms/Images/pixil-frame-0_1.png")
        platform_positions = [
            (0, 590),
            (200, 500),
            (300, 400),
            (450, 300),
            (150, 200),
            (350, 100, 200, 20)
        ]
    # snowy mountain    
    elif level == 3:
        bg = pygame.image.load("ppsms/Images/pixil-frame-0_2.png")
        platform_positions = [
            (0, 590),
            (250, 500),
            (350, 400),
            (500, 300),
            (200, 200),
            (400, 100, 150, 20)
        ]
    # heaven    
    elif level == 4:
        bg = pygame.image.load("ppsms/Images/pixil-frame-0_3.png")
        platform_positions = [
            (0, 590),
            (250, 500),
            (350, 400),
            (500, 300),
            (200, 200),
            (400, 100, 150, 20)
        ]    
    # hell
    elif level == 5:
        bg = pygame.image.load("ppsms/Images/pixil-frame-0_7.png")
        platform_positions = [
            (0, 590),
            (250, 500),
            (350, 400),
            (500, 300),
            (200, 200),
            (400, 100, 150, 20)
        ]   
    # tyhjennä mappi
    platforms.empty()
    all_sprites.empty()
    all_sprites.add(player)  # lisää pelaaja uudestaan
    for pos in platform_positions:
        platform = Platform(*pos)
        platforms.add(platform)
        all_sprites.add(platform)
    # resetoi pelaajan paikka
    player.rect.topleft = (0, SCREEN_HEIGHT - player_height - 100)
    player.velocity_y = 0

# Initial level load
load_level(current_level)     
for pos in platform_positions:
    platform = Platform(*pos)
    platforms.add(platform)
    all_sprites.add(platform)

# loop
clock = pygame.time.Clock()
start_time = pygame.time.get_ticks()  # aloita ajastin milisekunneissa
running = True
game_completed = False

# Main game loop
while running:
    # tapahtumat (event handling)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
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
            with open("game_results.csv", "w", newline="") as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(["Player", "Time (s)"])
                csv_writer.writerow(["Player", elapsed_time])
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
