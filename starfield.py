# File: starfield.py

import pygame
import random

class Star:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed

    def update(self, height):
        self.y += self.speed
        if self.y > height:
            self.y = 0

    def draw(self, window):
        pygame.draw.circle(window, (255, 255, 255), (int(self.x), int(self.y)), 1)

class Starfield:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.stars = [Star(random.randint(0, width), random.randint(0, height), random.uniform(0.1, 0.5)) 
                      for _ in range(100)]

    def update(self):
        for star in self.stars:
            star.update(self.height)

    def draw(self, window):
        for star in self.stars:
            star.draw(window)