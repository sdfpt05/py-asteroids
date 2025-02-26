# File: entities.py

import pygame
import math
import random
import colorsys

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
        self.thrusting = False
        self.thruster_particles = []
        self.invulnerable = False
        self.invulnerable_timer = 180  # 3 seconds
        self.blink_timer = 0
        self.visible = True
        self.color = (200, 200, 255)  # Slightly blue-tinted ship
        
    def rotate(self, direction):
        self.angle += direction * 5

    def thrust(self):
        angle_rad = math.radians(self.angle)
        self.speed[0] += math.cos(angle_rad) * 0.1
        self.speed[1] -= math.sin(angle_rad) * 0.1
        self.thrusting = True
        
        # Create thruster particles
        angle_rad = math.radians(self.angle + 180)  # Opposite direction
        for _ in range(2):
            offset = random.uniform(-0.3, 0.3)
            particle_angle = angle_rad + offset
            particle_x = self.position[0] + math.cos(angle_rad) * self.radius * 0.8
            particle_y = self.position[1] - math.sin(angle_rad) * self.radius * 0.8
            particle_speed = [math.cos(particle_angle) * random.uniform(1, 3),
                              -math.sin(particle_angle) * random.uniform(1, 3)]
            particle_life = random.randint(5, 15)
            
            # Blue-to-orange flame colors
            colors = [(255, 100 + random.randint(0, 155), 0), 
                     (200, 200, random.randint(0, 55)), 
                     (0, random.randint(100, 200), 255)]
            color = random.choice(colors)
            
            self.thruster_particles.append({
                'pos': [particle_x, particle_y],
                'speed': particle_speed,
                'life': particle_life,
                'max_life': particle_life,
                'color': color,
                'size': random.uniform(1.5, 3.5)
            })
    
    def update(self, width, height):
        self.position[0] += self.speed[0]
        self.position[1] += self.speed[1]
        
        # Apply friction
        self.speed[0] *= 0.99
        self.speed[1] *= 0.99

        # Screen wrapping
        self.position[0] %= width
        self.position[1] %= height
        
        # Reset thrusting flag
        self.thrusting = False
        
        # Update thruster particles
        for particle in self.thruster_particles[:]:
            particle['pos'][0] += particle['speed'][0]
            particle['pos'][1] += particle['speed'][1]
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.thruster_particles.remove(particle)

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
                
        # Invulnerability after respawn
        if self.invulnerable:
            self.invulnerable_timer -= 1
            self.blink_timer -= 1
            if self.blink_timer <= 0:
                self.visible = not self.visible
                self.blink_timer = 5  # Blink every 5 frames
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
                self.visible = True

    def draw(self, window):
        # Don't draw if blinking during invulnerability
        if not self.visible:
            return
            
        angle_rad = math.radians(self.angle)
        
        # Draw thruster particles first (behind ship)
        for particle in self.thruster_particles:
            alpha = (particle['life'] / particle['max_life']) * 255
            color = list(particle['color'])
            size = particle['size'] * (particle['life'] / particle['max_life'])
            pygame.draw.circle(window, color, 
                             (int(particle['pos'][0]), int(particle['pos'][1])), 
                             int(size))
        
        # Draw ship
        points = [
            (self.position[0] + self.radius * math.cos(angle_rad),
             self.position[1] - self.radius * math.sin(angle_rad)),
            (self.position[0] + self.radius * math.cos(angle_rad + 2.5),
             self.position[1] - self.radius * math.sin(angle_rad + 2.5)),
            (self.position[0] + self.radius * 0.5,  # Center back point
             self.position[1]),
            (self.position[0] + self.radius * math.cos(angle_rad - 2.5),
             self.position[1] - self.radius * math.sin(angle_rad - 2.5))
        ]
        
        # Draw filled ship with outline
        pygame.draw.polygon(window, self.color, points)
        pygame.draw.polygon(window, (255, 255, 255), points, 1)
        
        # Draw thruster flame if thrusting
        if self.thrusting:
            thrust_points = [
                (self.position[0] + self.radius * 0.5 * math.cos(angle_rad + math.pi),
                 self.position[1] - self.radius * 0.5 * math.sin(angle_rad + math.pi)),
                (self.position[0] + self.radius * 0.7 * math.cos(angle_rad + math.pi + 0.3),
                 self.position[1] - self.radius * 0.7 * math.sin(angle_rad + math.pi + 0.3)),
                (self.position[0] + self.radius * 1.5 * math.cos(angle_rad + math.pi),
                 self.position[1] - self.radius * 1.5 * math.sin(angle_rad + math.pi)),
                (self.position[0] + self.radius * 0.7 * math.cos(angle_rad + math.pi - 0.3),
                 self.position[1] - self.radius * 0.7 * math.sin(angle_rad + math.pi - 0.3))
            ]
            pygame.draw.polygon(window, (255, 150, 50), thrust_points)

        # Draw shield if active
        if self.shield_active:
            # Pulsating shield effect
            pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) * 0.5
            shield_color = (int(100 + 155 * pulse), int(200 + 55 * pulse), 255)
            
            # Inner shield
            pygame.draw.circle(window, shield_color, 
                               (int(self.position[0]), int(self.position[1])), 
                               self.radius + 5, 2)
            
            # Outer shield (more transparent)
            pygame.draw.circle(window, (shield_color[0]//2, shield_color[1]//2, shield_color[2]//2), 
                               (int(self.position[0]), int(self.position[1])), 
                               self.radius + 8, 1)

    def reset(self, x, y):
        self.position = [x, y]
        self.speed = [0, 0]
        self.angle = 0
        self.invulnerable = True
        self.invulnerable_timer = 180  # 3 seconds
        self.blink_timer = 5

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
        if self.invulnerable:
            return False
            
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
        self.speed = [random.uniform(-1, 1) * (4 / size), random.uniform(-1, 1) * (4 / size)]
        self.rotation = 0
        self.rotation_speed = random.uniform(-1, 1) * (2 / size)
        self.vertices = self.generate_vertices()
        
        # Color properties - each asteroid has a unique color tint
        hue = random.uniform(0, 0.1)  # Brown-gray range
        saturation = random.uniform(0.1, 0.3)
        value = random.uniform(0.5, 0.7)
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        self.color = (int(r*255), int(g*255), int(b*255))
        self.detail_color = (min(self.color[0] + 30, 255), 
                            min(self.color[1] + 30, 255), 
                            min(self.color[2] + 30, 255))

    def get_spawn_position(self, width, height):
        # Ensure asteroids don't spawn directly on the player ship
        center_x, center_y = width // 2, height // 2
        safe_distance = 100  # Minimum distance from center
        
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
        self.rotation += self.rotation_speed
        
        # Screen wrapping
        self.position[0] %= width
        self.position[1] %= height

    def draw(self, window):
        # Rotate vertices
        rotated_vertices = []
        for x, y in self.vertices:
            cos_rot = math.cos(math.radians(self.rotation))
            sin_rot = math.sin(math.radians(self.rotation))
            rotated_x = x * cos_rot - y * sin_rot
            rotated_y = x * sin_rot + y * cos_rot
            rotated_vertices.append((self.position[0] + rotated_x, self.position[1] + rotated_y))
        
        # Draw filled asteroid with detail color
        pygame.draw.polygon(window, self.color, rotated_vertices)
        pygame.draw.polygon(window, (255, 255, 255), rotated_vertices, 2)
        
        # Draw some details/craters
        for i in range(3):
            x_offset = self.radius * 0.6 * math.cos(math.radians(self.rotation + i * 120))
            y_offset = self.radius * 0.6 * math.sin(math.radians(self.rotation + i * 120))
            radius = self.radius * 0.2
            pygame.draw.circle(window, self.detail_color, 
                             (int(self.position[0] + x_offset), int(self.position[1] + y_offset)), 
                             int(radius), 1)


class Bullet:
    def __init__(self, position, angle, power=1.0):
        self.position = list(position)
        self.speed = [math.cos(math.radians(angle)) * 7,
                      -math.sin(math.radians(angle)) * 7]
        self.lifetime = 60  # frames
        self.radius = 2
        self.power = power  # More powerful bullets do more damage
        self.trail = []  # Store previous positions for trail effect

    def update(self, width, height):
        # Store current position for trail
        self.trail.append((self.position[0], self.position[1]))
        if len(self.trail) > 5:  # Limit trail length
            self.trail.pop(0)
            
        self.position[0] += self.speed[0]
        self.position[1] += self.speed[1]
        self.lifetime -= 1

        # Screen wrapping
        self.position[0] %= width
        self.position[1] %= height

    def draw(self, window):
        # Draw trail
        for i, pos in enumerate(self.trail):
            alpha = i / len(self.trail)
            radius = 1 + alpha
            color = (255, int(255 * alpha), int(100 * alpha))
            pygame.draw.circle(window, color, (int(pos[0]), int(pos[1])), int(radius))
        
        # Draw bullet
        if self.power > 1.0:
            # Special color for powered up bullets
            pygame.draw.circle(window, (100, 200, 255), 
                             (int(self.position[0]), int(self.position[1])), 
                             self.radius + 1)
        
        pygame.draw.circle(window, (255, 255, 255), 
                          (int(self.position[0]), int(self.position[1])), 
                          self.radius)

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
        self.color = (150, 150, 255)  # Light blue saucer
        self.detail_color = (200, 200, 255)
        self.lights_timer = 0
        self.light_state = 0

    def get_spawn_position(self, width, height):
        return [random.choice([-self.radius, width + self.radius]), random.randint(0, height)]

    def update(self, ship, width, height):
        self.position[0] += self.speed[0]
        
        # Vertical movement: Sine wave pattern
        wave_height = height / 6
        time_factor = pygame.time.get_ticks() / 1000
        self.position[1] = height/2 + math.sin(time_factor + self.position[0]/100) * wave_height
        
        # Wrap around horizontally
        if self.position[0] < -self.radius and self.speed[0] < 0:
            self.position[0] = width + self.radius
        elif self.position[0] > width + self.radius and self.speed[0] > 0:
            self.position[0] = -self.radius

        # Shooting logic
        self.shoot_timer -= 1
        
        # Lights effect
        self.lights_timer += 1
        if self.lights_timer >= 10:  # Change lights every 10 frames
            self.lights_timer = 0
            self.light_state = (self.light_state + 1) % 3
            
        if self.shoot_timer <= 0:
            self.shoot_timer = random.randint(60, 120)
            return self.shoot(ship)
        return None

    def shoot(self, ship):
        # Improved aiming for larger saucers
        if self.size == 1:  # Small saucer: perfect aim
            angle = math.atan2(ship.position[1] - self.position[1], 
                               ship.position[0] - self.position[0])
        else:  # Large saucer: some inaccuracy
            angle = math.atan2(ship.position[1] - self.position[1], 
                              ship.position[0] - self.position[0])
            angle += random.uniform(-0.5, 0.5)  # Add some random deviation
            
        return Bullet(self.position, math.degrees(angle))

    def draw(self, window):
        # Draw saucer body
        pygame.draw.ellipse(window, self.color, 
                          (self.position[0] - self.radius, 
                           self.position[1] - self.radius // 2,
                           self.radius * 2, self.radius), 0)
        pygame.draw.ellipse(window, (255, 255, 255), 
                          (self.position[0] - self.radius, 
                           self.position[1] - self.radius // 2,
                           self.radius * 2, self.radius), 1)
        
        # Draw cockpit
        pygame.draw.ellipse(window, self.detail_color, 
                          (self.position[0] - self.radius // 2,
                           self.position[1] - self.radius // 3,
                           self.radius, self.radius // 1.5), 0)
        pygame.draw.ellipse(window, (255, 255, 255), 
                          (self.position[0] - self.radius // 2,
                           self.position[1] - self.radius // 3,
                           self.radius, self.radius // 1.5), 1)
        
        # Draw running lights
        light_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        for i in range(3):
            if (i + self.light_state) % 3 == 0:
                light_color = light_colors[i]
            else:
                light_color = (100, 100, 100)
                
            pygame.draw.circle(window, light_color, 
                              (int(self.position[0] - self.radius * 0.6 + i * self.radius * 0.6), 
                               int(self.position[1] + self.radius * 0.3)), 
                              2)


class PowerUp:
    def __init__(self, power_type, width, height):
        self.type = power_type
        self.position = [random.randint(0, width), random.randint(0, height)]
        self.radius = 10
        self.duration = 600  # 10 seconds at 60 FPS
        self.angle = 0
        self.pulse_timer = 0
        self.pulse_direction = 1
        
        # Set color based on power-up type
        if self.type == "shield":
            self.color = (0, 200, 255)  # Cyan
            self.icon = "S"
        elif self.type == "rapid_fire":
            self.color = (255, 200, 0)  # Yellow
            self.icon = "R"
        elif self.type == "multi_shot":
            self.color = (255, 0, 255)  # Magenta
            self.icon = "M"
        elif self.type == "extra_life":
            self.color = (50, 255, 50)  # Green
            self.icon = "L"
        else:
            self.color = (255, 255, 255)
            self.icon = "?"

    def update(self):
        self.duration -= 1
        self.angle += 2  # Rotate effect
        
        # Pulsing effect
        self.pulse_timer += self.pulse_direction
        if self.pulse_timer >= 30:
            self.pulse_direction = -1
        elif self.pulse_timer <= 0:
            self.pulse_direction = 1

    def draw(self, window):
        # Pulsing factor (0.8 to 1.2)
        pulse_factor = 1 + (self.pulse_timer / 30) * 0.4
        
        # Draw outer circle with pulsing effect
        pulse_radius = int(self.radius * pulse_factor)
        pygame.draw.circle(window, self.color, 
                          (int(self.position[0]), int(self.position[1])), 
                          pulse_radius, 2)
        
        # Draw inner circle
        pygame.draw.circle(window, (255, 255, 255), 
                          (int(self.position[0]), int(self.position[1])), 
                          self.radius - 3, 1)
        
        # Draw rotated particles around power-up
        for i in range(4):
            angle = math.radians(self.angle + i * 90)
            offset_x = math.cos(angle) * (self.radius + 2)
            offset_y = math.sin(angle) * (self.radius + 2)
            
            pygame.draw.circle(window, self.color, 
                              (int(self.position[0] + offset_x), 
                               int(self.position[1] + offset_y)), 
                              2)
            
        # Draw icon text in the center
        font = pygame.font.Font(None, 24)
        text = font.render(self.icon, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.position[0], self.position[1]))
        window.blit(text, text_rect)