# File: menu.py

import pygame

class Menu:
    def __init__(self, window, width, height):
        self.window = window
        self.width = width
        self.height = height
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 72)
        self.load_high_score()

    def load_high_score(self):
        try:
            with open("high_score.txt", "r") as file:
                self.high_score = int(file.read())
        except FileNotFoundError:
            self.high_score = 0

    def save_high_score(self, score):
        if score > self.high_score:
            self.high_score = score
            with open("high_score.txt", "w") as file:
                file.write(str(self.high_score))

    def draw_text(self, text, font, color, position):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=position)
        self.window.blit(text_surface, text_rect)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        return "start"
                    elif event.key == pygame.K_q:
                        return "quit"

            self.window.fill((0, 0, 0))
            self.draw_text("ASTEROIDS", self.title_font, (255, 255, 255), (self.width // 2, self.height // 3))
            self.draw_text("Press SPACE to start", self.font, (255, 255, 255), (self.width // 2, self.height * 2 // 3))
            self.draw_text("Press Q to quit", self.font, (255, 255, 255), (self.width // 2, self.height * 3 // 4))
            self.draw_text(f"High Score: {self.high_score}", self.font, (255, 255, 255), (self.width // 2, self.height * 5 // 6))

            pygame.display.flip()

    def run_game_over(self, score):
        self.save_high_score(score)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        return "restart"
                    elif event.key == pygame.K_m:
                        return "menu"

            self.window.fill((0, 0, 0))
            self.draw_text("GAME OVER", self.title_font, (255, 255, 255), (self.width // 2, self.height // 3))
            self.draw_text(f"Final Score: {score}", self.font, (255, 255, 255), (self.width // 2, self.height // 2))
            self.draw_text("Press SPACE to restart", self.font, (255, 255, 255), (self.width // 2, self.height * 2 // 3))
            self.draw_text("Press M for main menu", self.font, (255, 255, 255), (self.width // 2, self.height * 3 // 4))

            pygame.display.flip()