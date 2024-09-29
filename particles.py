# File: particles.py

import pygame
import random
import math

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(1, 3)
        self.speed = [random.uniform(-1, 1), random.uniform(-1, 1)]
        self.lifetime = random.randint(30, 60)  # frames

    def update(self):
        self.x += self.speed[0]
        self.y += self.speed[1]
        self.lifetime -= 1

    def draw(self, window):
        pygame.draw.circle(window, self.color, (int(self.x), int(self.y)), self.size)

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def create_explosion(self, position, color=(255, 255, 255)):
        num_particles = random.randint(10, 20)
        for _ in range(num_particles):
            self.particles.append(Particle(position[0], position[1], color))

    def update(self):
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for particle in self.particles:
            particle.update()

    def draw(self, window):
        for particle in self.particles:
            particle.draw(window)