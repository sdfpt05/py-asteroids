import pygame
import sys
import os
from game import Game
from menu import Menu

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Set up the game window with icon
WIDTH = 800
HEIGHT = 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids")

# Try to load and set an icon
try:
    icon = pygame.image.load("images/asteroid_icon.png")
    pygame.display.set_icon(icon)
except:
    # If icon file is missing, create a simple icon
    icon_surface = pygame.Surface((32, 32))
    icon_surface.fill((0, 0, 0))
    pygame.draw.circle(icon_surface, (200, 200, 200), (16, 16), 14, 2)
    pygame.draw.circle(icon_surface, (150, 150, 150), (10, 10), 3, 0)
    pygame.draw.circle(icon_surface, (150, 150, 150), (22, 20), 5, 0)
    pygame.display.set_icon(icon_surface)

# Try to create directories for assets if they don't exist
for directory in ["sounds", "fonts", "images"]:
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except:
            pass

# Create game and menu instances
game = Game(window, WIDTH, HEIGHT)
menu = Menu(window, WIDTH, HEIGHT)

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2

# Main game loop
clock = pygame.time.Clock()
current_state = MENU
frame_counter = 0
show_fps = False

while True:
    # Calculate FPS
    frame_counter += 1
    fps = clock.get_fps()
    
    # Toggle FPS display with F key
    keys = pygame.key.get_pressed()
    if keys[pygame.K_f] and frame_counter % 30 == 0:
        show_fps = not show_fps
    
    # Game state machine
    if current_state == MENU:
        action = menu.run()
        if action == "start":
            current_state = PLAYING
            game.reset()
        elif action == "quit":
            pygame.quit()
            sys.exit()
    elif current_state == PLAYING:
        game_over = game.run()
        if game_over:
            current_state = GAME_OVER
    elif current_state == GAME_OVER:
        action = menu.run_game_over(game.score)
        if action == "restart":
            current_state = PLAYING
            game.reset()
        elif action == "menu":
            current_state = MENU

    # Show FPS counter if enabled
    if show_fps:
        fps_text = f"FPS: {int(fps)}"
        font = pygame.font.Font(None, 24)
        fps_surface = font.render(fps_text, True, (100, 255, 100))
        window.blit(fps_surface, (10, 10))

    pygame.display.flip()
    clock.tick(60)