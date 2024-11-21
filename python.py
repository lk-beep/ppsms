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
    def __init__(self, x, y, width=200, height=20):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect(topleft=(x, y))


player = Player(player_x, player_y)
all_sprites.add(player)


def load_level(level):
    global bg, platform_positions, exit_area, player
    # platformit ja poistumiset
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
            (0, SCREEN_HEIGHT - 3, SCREEN_WIDTH, 1)  # 1-kuolemis death platform
        ]
        exit_area = pygame.Rect(SCREEN_WIDTH - 50, SCREEN_HEIGHT - 50, 50, 50)  # poistumis area for level 1

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
            (500, 160, 100),
            (400, 460, 200),
            (400, 320, 100, 20),
            (400, 200, 20, 120),
            (260, 460, 80),
            (200, 350, 80),
            (350, 250, 50),
            (0, SCREEN_HEIGHT - 1, SCREEN_WIDTH, 1)  # 1-pixel kuolemis platform
        ]
        exit_area = pygame.Rect(420, 270, 80, 50)  # poistumis area for level 2

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
        exit_area = pygame.Rect(600 - 60, 20, 40, 40)  # poistumis area for level 3

    elif level == 4:
        bg = pygame.image.load("Images/pixil-frame-0_3.png")
        platform_positions = [
            (0, 590),
            (200, 400),
            (350, 400),
            (500, 300),
            (200, 200),
            (100, 50, 50, 20),
            (0, SCREEN_HEIGHT - 1, SCREEN_WIDTH, 1)  # 1-pixel kuolemis platform
        ]
        exit_area = pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 150, 150, 150)  # poistumis area for level 4

    elif level == 5:
        bg = pygame.image.load("Images/pixil-frame-0_7.png")
        platform_positions = [
            (0, 590),
            (250, 500),
            (350, 400),
            (500, 300),
            (200, 200),
            (400, 100, 150, 20),
            (0, SCREEN_HEIGHT - 1, SCREEN_WIDTH, 1)  # 1-pixel kuolemis platform
        ]
        exit_area = pygame.Rect(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 200, 200, 200)  # poistumis area for level 5


    # Clear existing platforms and sprites
    platforms.empty()
    all_sprites.empty()
    all_sprites.add(player)  # Add the player back to the sprite group
    
    for pos in platform_positions:
        platform = Platform(*pos)
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
    # tapahtumat (event handling)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                if current_level < 5:  # Ensure it doesn't exceed the final level
                    current_level += 1
                    load_level(current_level)
                else:
                    print("Olet jo viimeisellä tasolla!")

   


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
