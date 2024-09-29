# File: entities.py

import pygame
import math
import random

class Ship:
    def __init__(self, x, y):
        self.position = [x, y]
        self.angle = 0
        self.speed = [0, 0]
        self.radius = 15
        self.shield_active = False
        self.shield_timer = 0
        self.rapid_fire_active = False
        self.rapid_fire_timer = 0
        self.multi_shot_active = False
        self.multi_shot_timer = 0

    def rotate(self, direction):
        self.angle += direction * 5

    def thrust(self):
        angle_rad = math.radians(self.angle)
        self.speed[0] += math.cos(angle_rad) * 0.1
        self.speed[1] -= math.sin(angle_rad) * 0.1

    def update(self, width, height):
        self.position[0] += self.speed[0]
        self.position[1] += self.speed[1]
        
        # Apply friction
        self.speed[0] *= 0.99
        self.speed[1] *= 0.99

        # Screen wrapping
        self.position[0] %= width
        self.position[1] %= height

        # Update power-up timers
        if self.shield_active:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield_active = False

        if self.rapid_fire_active:
            self.rapid_fire_timer -= 1
            if self.rapid_fire_timer <= 0:
                self.rapid_fire_active = False

        if self.multi_shot_active:
            self.multi_shot_timer -= 1
            if self.multi_shot_timer <= 0:
                self.multi_shot_active = False

    def draw(self, window):
        angle_rad = math.radians(self.angle)
        points = [
            (self.position[0] + self.radius * math.cos(angle_rad),
             self.position[1] - self.radius * math.sin(angle_rad)),
            (self.position[0] + self.radius * math.cos(angle_rad + 2.5),
             self.position[1] - self.radius * math.sin(angle_rad + 2.5)),
            (self.position[0] + self.radius * math.cos(angle_rad - 2.5),
             self.position[1] - self.radius * math.sin(angle_rad - 2.5))
        ]
        pygame.draw.polygon(window, (255, 255, 255), points, 2)

        if self.shield_active:
            pygame.draw.circle(window, (0, 255, 255), (int(self.position[0]), int(self.position[1])), self.radius + 5, 1)

    def reset(self, x, y):
        self.position = [x, y]
        self.speed = [0, 0]
        self.angle = 0

    def activate_shield(self):
        self.shield_active = True
        self.shield_timer = 300  # 5 seconds at 60 FPS

    def activate_rapid_fire(self):
        self.rapid_fire_active = True
        self.rapid_fire_timer = 300  # 5 seconds at 60 FPS

    def activate_multi_shot(self):
        self.multi_shot_active = True
        self.multi_shot_timer = 300  # 5 seconds at 60 FPS

    def collides_with(self, other):
        distance = math.hypot(self.position[0] - other.position[0], self.position[1] - other.position[1])
        return distance < self.radius + other.radius

class Asteroid:
    def __init__(self, size, width, height, position=None):
        self.size = size
        self.radius = size * 10
        if position:
            self.position = list(position)
        else:
            self.position = self.get_spawn_position(width, height)
        self.speed = [random.uniform(-1, 1), random.uniform(-1, 1)]
        self.vertices = self.generate_vertices()

    def get_spawn_position(self, width, height):
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            return [random.randint(0, width), -self.radius]
        elif side == 'bottom':
            return [random.randint(0, width), height + self.radius]
        elif side == 'left':
            return [-self.radius, random.randint(0, height)]
        else:  # right
            return [width + self.radius, random.randint(0, height)]

    def generate_vertices(self):
        num_vertices = random.randint(8, 12)
        vertices = []
        for i in range(num_vertices):
            angle = i * (2 * math.pi / num_vertices)
            distance = self.radius * random.uniform(0.8, 1.2)
            x = distance * math.cos(angle)
            y = distance * math.sin(angle)
            vertices.append((x, y))
        return vertices

    def update(self, width, height):
        self.position[0] += self.speed[0]
        self.position[1] += self.speed[1]
        
        # Screen wrapping
        self.position[0] %= width
        self.position[1] %= height

    def draw(self, window):
        points = [(self.position[0] + x, self.position[1] + y) for x, y in self.vertices]
        pygame.draw.polygon(window, (255, 255, 255), points, 2)

class Bullet:
    def __init__(self, position, angle):
        self.position = list(position)
        self.speed = [math.cos(math.radians(angle)) * 5,
                      -math.sin(math.radians(angle)) * 5]
        self.lifetime = 60  # frames
        self.radius = 2

    def update(self, width, height):
        self.position[0] += self.speed[0]
        self.position[1] += self.speed[1]
        self.lifetime -= 1

        # Screen wrapping
        self.position[0] %= width
        self.position[1] %= height

    def draw(self, window):
        pygame.draw.circle(window, (255, 255, 255), (int(self.position[0]), int(self.position[1])), self.radius)

    def collides_with(self, other):
        distance = math.hypot(self.position[0] - other.position[0], self.position[1] - other.position[1])
        return distance < self.radius + other.radius


class FlyingSaucer:
    def __init__(self, width, height):
        self.size = random.choice([1, 2])
        self.radius = self.size * 15
        self.position = self.get_spawn_position(width, height)
        self.speed = [random.choice([-1, 1]) * (3 - self.size), 0]
        self.shoot_timer = 0

    def get_spawn_position(self, width, height):
        return [random.choice([-self.radius, width + self.radius]), random.randint(0, height)]

    def update(self, ship, width, height):
        self.position[0] += self.speed[0]
        self.position[1] = max(self.radius, min(height - self.radius, self.position[1] + random.uniform(-1, 1)))
        
        # Wrap around horizontally
        if self.position[0] < -self.radius and self.speed[0] < 0:
            self.position[0] = width + self.radius
        elif self.position[0] > width + self.radius and self.speed[0] > 0:
            self.position[0] = -self.radius

        # Shooting logic
        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            self.shoot_timer = random.randint(60, 120)
            return self.shoot(ship)
        return None

    def shoot(self, ship):
        angle = math.atan2(ship.position[1] - self.position[1], ship.position[0] - self.position[0])
        return Bullet(self.position, math.degrees(angle))

    def draw(self, window):
        pygame.draw.ellipse(window, (255, 255, 255), (self.position[0] - self.radius, self.position[1] - self.radius // 2, 
                                            self.radius * 2, self.radius), 2)
        pygame.draw.rect(window, (255, 255, 255), (self.position[0] - self.radius // 2, self.position[1] - self.radius // 4, 
                                         self.radius, self.radius // 2), 2)

class PowerUp:
    def __init__(self, power_type, width, height):
        self.type = power_type
        self.position = [random.randint(0, width), random.randint(0, height)]
        self.radius = 10
        self.duration = 600  # 10 seconds at 60 FPS

    def update(self):
        self.duration -= 1

    def draw(self, window):
        color = (0, 255, 0) if self.type == "shield" else (255, 255, 0) if self.type == "rapid_fire" else (255, 0, 255)
        pygame.draw.circle(window, color, (int(self.position[0]), int(self.position[1])), self.radius)
        pygame.draw.circle(window, (255, 255, 255), (int(self.position[0]), int(self.position[1])), self.radius, 1)