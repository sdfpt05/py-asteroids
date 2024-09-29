# File: game.py

import pygame
import random
from entities import Ship, Asteroid, Bullet, FlyingSaucer, PowerUp
from particles import ParticleSystem
from starfield import Starfield

class Game:
    def __init__(self, window, width, height):
        self.window = window
        self.width = width
        self.height = height
        self.ship = Ship(width // 2, height // 2)
        self.asteroids = []
        self.bullets = []
        self.flying_saucers = []
        self.power_ups = []
        self.score = 0
        self.lives = 3
        self.level = 1
        self.particle_system = ParticleSystem()
        self.starfield = Starfield(width, height)
        self.font = pygame.font.Font(None, 36)
        self.load_sounds()
        self.spawn_asteroids(4)

    def load_sounds(self):
        self.shoot_sound = pygame.mixer.Sound("sounds/shoot.wav")
        self.explosion_sound = pygame.mixer.Sound("sounds/explosion.wav")
        self.thrust_sound = pygame.mixer.Sound("sounds/thrust.wav")

    def reset(self):
        self.ship = Ship(self.width // 2, self.height // 2)
        self.asteroids = []
        self.bullets = []
        self.flying_saucers = []
        self.power_ups = []
        self.score = 0
        self.lives = 3
        self.level = 1
        self.spawn_asteroids(4)

    def spawn_asteroids(self, num):
        for _ in range(num):
            size = random.randint(1, 3)
            asteroid = Asteroid(size, self.width, self.height)
            self.asteroids.append(asteroid)
        print(f"Spawned {num} asteroids. Total asteroids: {len(self.asteroids)}")

    def run(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.bullets.append(Bullet(self.ship.position, self.ship.angle))
                    self.shoot_sound.play()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.ship.rotate(1)
        if keys[pygame.K_RIGHT]:
            self.ship.rotate(-1)
        if keys[pygame.K_UP]:
            self.ship.thrust()
            self.thrust_sound.play()

        self.update()
        self.check_collisions()
        self.draw()

        return self.lives <= 0

    def update(self):
        self.ship.update(self.width, self.height)
        for asteroid in self.asteroids:
            asteroid.update(self.width, self.height)
        for bullet in self.bullets:
            bullet.update(self.width, self.height)
        for saucer in self.flying_saucers:
            saucer_bullet = saucer.update(self.ship, self.width, self.height)
            if saucer_bullet:
                self.bullets.append(saucer_bullet)
        for power_up in self.power_ups:
            power_up.update()

        self.particle_system.update()
        self.starfield.update()

        # Spawn flying saucers
        if random.randint(1, 1000) == 1:
            self.flying_saucers.append(FlyingSaucer(self.width, self.height))

        # Spawn power-ups
        if random.randint(1, 600) == 1:
            self.power_ups.append(PowerUp(random.choice(["shield", "rapid_fire", "multi_shot"]), self.width, self.height))

        # Remove expired bullets and power-ups
        self.bullets = [bullet for bullet in self.bullets if bullet.lifetime > 0]
        self.power_ups = [power_up for power_up in self.power_ups if power_up.duration > 0]

        # Level progression
        if len(self.asteroids) == 0:
            self.level += 1
            self.spawn_asteroids(self.level + 3)

        print(f"Number of asteroids: {len(self.asteroids)}")

    def check_collisions(self):
        for bullet in self.bullets[:]:
            # Bullet-Asteroid collision
            for asteroid in self.asteroids[:]:
                if bullet.collides_with(asteroid):
                    self.bullets.remove(bullet)
                    self.asteroids.remove(asteroid)
                    self.explosion_sound.play()
                    self.score += 100 * asteroid.size
                    self.particle_system.create_explosion(asteroid.position)
                    if asteroid.size > 1:
                        for _ in range(2):
                            self.asteroids.append(Asteroid(asteroid.size - 1, self.width, self.height, asteroid.position))
                    break

            # Bullet-Flying Saucer collision
            for saucer in self.flying_saucers[:]:
                if bullet.collides_with(saucer):
                    self.bullets.remove(bullet)
                    self.flying_saucers.remove(saucer)
                    self.explosion_sound.play()
                    self.score += 500 * saucer.size
                    self.particle_system.create_explosion(saucer.position)
                    break

        # Ship-Asteroid collision
        for asteroid in self.asteroids:
            if self.ship.collides_with(asteroid) and not self.ship.shield_active:
                self.lives -= 1
                self.explosion_sound.play()
                self.particle_system.create_explosion(self.ship.position)
                self.ship.reset(self.width // 2, self.height // 2)
                break

        # Ship-Flying Saucer collision
        for saucer in self.flying_saucers[:]:
            if self.ship.collides_with(saucer) and not self.ship.shield_active:
                self.lives -= 1
                self.explosion_sound.play()
                self.particle_system.create_explosion(self.ship.position)
                self.ship.reset(self.width // 2, self.height // 2)
                self.flying_saucers.remove(saucer)
                break

        # Ship-PowerUp collision
        for power_up in self.power_ups[:]:
            if self.ship.collides_with(power_up):
                if power_up.type == "shield":
                    self.ship.activate_shield()
                elif power_up.type == "rapid_fire":
                    self.ship.activate_rapid_fire()
                elif power_up.type == "multi_shot":
                    self.ship.activate_multi_shot()
                self.power_ups.remove(power_up)

    def draw(self):
        self.window.fill((0, 0, 0))
        self.starfield.draw(self.window)
        self.ship.draw(self.window)
        for asteroid in self.asteroids:
            asteroid.draw(self.window)
        for bullet in self.bullets:
            bullet.draw(self.window)
        for saucer in self.flying_saucers:
            saucer.draw(self.window)
        for power_up in self.power_ups:
            power_up.draw(self.window)
        self.particle_system.draw(self.window)

        # Draw HUD
        self.draw_text(f"Score: {self.score}", (100, 30))
        self.draw_text(f"Lives: {self.lives}", (self.width - 100, 30))
        self.draw_text(f"Level: {self.level}", (self.width // 2, 30))

    def draw_text(self, text, position):
        text_surface = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=position)
        self.window.blit(text_surface, text_rect)