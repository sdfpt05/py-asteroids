import pygame
import sys
from game import Game
from menu import Menu

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Set up the game window
WIDTH = 800
HEIGHT = 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids")

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

while True:
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

    pygame.display.flip()
    clock.tick(60)