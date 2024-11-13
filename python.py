import pygame
import sys
pygame.init()

# näytön asetukset
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pepen mahtava seikkailu")

# värit
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# pelaaja 
player_width = 40
player_height = 60
player_x = 100
player_y = SCREEN_HEIGHT - player_height - 100
player_speed = 5
player_jump_power = 45
player_gravity = 0.8 
player_velocity_y = 0
on_ground = False

# Platformeja olemaan
platforms = [
    pygame.Rect(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50),  
    pygame.Rect(200, 450, 200, 20),                       
    pygame.Rect(500, 350, 200, 20),
    pygame.Rect(300, 250, 200, 20)
]

# loop
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # liikkuminen
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed

    # hyppy (ei toimi vielä)
    if keys[pygame.K_SPACE] and on_ground == True:
        player_velocity_y = -player_jump_power
        on_ground = False

    # takaisin maahan
    player_velocity_y += player_gravity
    player_y += player_velocity_y

    # koskemisen detection
    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)

    on_ground = False
    for platform in platforms:
        if player_rect.colliderect(platform):
            # osuu päälle
            if player_velocity_y > 0 and player_y + player_height - platform.top < player_velocity_y:
                player_y = platform.top - player_height
                player_velocity_y = 0
                on_ground = True
            # osuu alta
            elif player_velocity_y < 0 and player_y - platform.bottom < player_velocity_y:
                player_y = platform.bottom
                player_velocity_y = 0

    # näyttö borderit
    if player_x < 0:
        player_x = 0
    elif player_x + player_width > SCREEN_WIDTH:
        player_x = SCREEN_WIDTH - player_width
    if player_y + player_height > SCREEN_HEIGHT:
        player_y = SCREEN_HEIGHT - player_height
        on_ground = True
        player_velocity_y = 0

    # piirrä
    screen.fill(WHITE)
    pygame.draw.rect(screen, BLUE, player_rect)  # pelaaja
    for platform in platforms:
        pygame.draw.rect(screen, BLACK, platform)  # hyppely

    # päivitä pelin tapahtumat
    pygame.display.flip()
    clock.tick(60)  # lock the frame rate at 60 FPS
