# File: particles.py

import pygame
import random
import math

class Particle:
    def __init__(self, x, y, color=(255, 255, 255), velocity=None, size=None, lifetime=None):
        self.x = x
        self.y = y
        self.color = color
        
        # Random velocity if none provided
        if velocity:
            self.speed = velocity
        else:
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 2.5)
            self.speed = [math.cos(angle) * speed, math.sin(angle) * speed]
        
        # Random size if none provided
        self.size = size if size else random.uniform(1, 3)
        
        # Random lifetime if none provided
        self.lifetime = lifetime if lifetime else random.randint(30, 60)
        self.max_lifetime = self.lifetime
        
        # Rotation and flickering properties
        self.angle = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-5, 5)
        self.flicker = random.uniform(0.8, 1.2)

    def update(self):
        self.x += self.speed[0]
        self.y += self.speed[1]
        self.lifetime -= 1
        
        # Gradually slow down
        self.speed[0] *= 0.98
        self.speed[1] *= 0.98
        
        # Rotate and flicker
        self.angle += self.rotation_speed
        self.flicker = max(0.7, min(1.3, self.flicker + random.uniform(-0.1, 0.1)))

    def draw(self, window, offset=(0, 0)):
        # Alpha based on remaining lifetime
        alpha = int((self.lifetime / self.max_lifetime) * 255)
        
        # Adjusted color with alpha
        color = list(self.color)
        
        # Calculate flickering size
        size = self.size * self.flicker * (self.lifetime / self.max_lifetime)
        
        # Draw the particle with screen shake offset
        pos_x = int(self.x + offset[0])
        pos_y = int(self.y + offset[1])
        
        # Use different shapes for visual interest
        shape = random.randint(0, 10)
        if shape < 6:  # 60% circles
            pygame.draw.circle(window, color, (pos_x, pos_y), size)
        elif shape < 9:  # 30% squares
            rect = pygame.Rect(pos_x - size, pos_y - size, size * 2, size * 2)
            pygame.draw.rect(window, color, rect)
        else:  # 10% triangles
            points = [
                (pos_x, pos_y - size),
                (pos_x - size, pos_y + size),
                (pos_x + size, pos_y + size)
            ]
            pygame.draw.polygon(window, color, points)

class ParticleSystem:
    def __init__(self):
        self.particles = []
        
        # Explosion presets for quick access
        self.explosion_colors = [
            (255, 255, 200),  # Yellow-white
            (255, 200, 100),  # Orange
            (255, 100, 50),   # Red-orange
            (255, 50, 50),    # Red
            (200, 200, 255),  # Light blue
            (100, 100, 255)   # Blue
        ]

    def create_explosion(self, position, size=1, color=None):
        # Determine number of particles based on size
        num_particles = random.randint(10, 20) * size
        
        # Use provided color or random from presets
        if color is None:
            base_color = random.choice(self.explosion_colors)
        else:
            base_color = color
        
        # Create particles with variety
        for _ in range(num_particles):
            # Vary color slightly
            r = min(255, max(0, base_color[0] + random.randint(-20, 20)))
            g = min(255, max(0, base_color[1] + random.randint(-20, 20)))
            b = min(255, max(0, base_color[2] + random.randint(-20, 20)))
            color = (r, g, b)
            
            # Calculate velocity
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 3) * size
            velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
            
            # Calculate size and lifetime
            part_size = random.uniform(1, 3) * size
            lifetime = random.randint(30, 60)
            
            # Create particle
            self.particles.append(Particle(
                position[0], position[1],
                color, velocity, part_size, lifetime
            ))
            
        # Add a bright flash at the center
        flash_size = 10 * size
        flash_color = (255, 255, 255)
        flash_lifetime = 5
        self.particles.append(Particle(
            position[0], position[1],
            flash_color, [0, 0], flash_size, flash_lifetime
        ))

    def create_effect(self, position, color):
        # Specialized particle effect for power-ups, etc.
        num_particles = random.randint(15, 25)
        
        for i in range(num_particles):
            # Create particles that expand outward in a ring
            angle = (i / num_particles) * math.pi * 2
            speed = random.uniform(1.5, 3.0)
            velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
            
            # Use the provided color with slight variation
            r = min(255, max(0, color[0] + random.randint(-20, 20)))
            g = min(255, max(0, color[1] + random.randint(-20, 20)))
            b = min(255, max(0, color[2] + random.randint(-20, 20)))
            part_color = (r, g, b)
            
            self.particles.append(Particle(
                position[0], position[1],
                part_color, velocity, random.uniform(1.5, 3), random.randint(30, 50)
            ))

    def update(self):
        # Remove expired particles and update remaining ones
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for particle in self.particles:
            particle.update()

    def draw(self, window, offset=(0, 0)):
        for particle in self.particles:
            particle.draw(window, offset)


# File: starfield.py

import pygame
import random
import math

class Star:
    def __init__(self, x, y, depth):
        self.x = x
        self.y = y
        self.depth = depth  # 0.1 (far) to 1.0 (close)
        self.speed = 0.2 * depth
        self.brightness = int(155 + 100 * depth)  # Brighter stars are closer
        self.size = 1 + int(depth * 2)  # Larger stars are closer
        self.twinkle_state = random.random()
        self.twinkle_speed = random.uniform(0.02, 0.05)
        self.color_base = random.choice([
            (self.brightness, self.brightness, self.brightness),  # White
            (self.brightness, self.brightness * 0.8, self.brightness * 0.8),  # Slightly red
            (self.brightness * 0.8, self.brightness * 0.8, self.brightness),  # Slightly blue
            (self.brightness, self.brightness * 0.8, self.brightness)  # Slightly green
        ])

    def update(self, height):
        self.y += self.speed
        if self.y > height:
            self.y = 0
            
        # Update twinkle effect
        self.twinkle_state += self.twinkle_speed
        if self.twinkle_state > 2 * math.pi:
            self.twinkle_state -= 2 * math.pi

    def draw(self, window):
        # Calculate twinkle factor (0.7 to 1.3)
        twinkle = 0.7 + (math.sin(self.twinkle_state) + 1) * 0.3
        
        # Apply twinkle to brightness
        r = min(255, int(self.color_base[0] * twinkle))
        g = min(255, int(self.color_base[1] * twinkle))
        b = min(255, int(self.color_base[2] * twinkle))
        color = (r, g, b)
        
        # Draw the star
        if self.size <= 1:
            window.set_at((int(self.x), int(self.y)), color)
        else:
            # Draw larger stars with a glow effect
            pygame.draw.circle(window, color, (int(self.x), int(self.y)), self.size)
            
            # Add a small glow for the brightest stars
            if self.depth > 0.8:
                glow_size = self.size + 1
                glow_color = (r//3, g//3, b//3)  # Dimmer for the glow
                pygame.draw.circle(window, glow_color, (int(self.x), int(self.y)), glow_size, 1)


class Nebula:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Create a surface for the nebula
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Generate some random nebula colors (blues, purples, teals)
        self.colors = [
            (20, 30, 60, 2),     # Dark blue
            (50, 20, 70, 2),     # Purple
            (20, 50, 60, 2),     # Teal
            (30, 20, 80, 2)      # Indigo
        ]
        
        # Generate nebula cloud shapes
        self.clouds = []
        for _ in range(5):
            color = random.choice(self.colors)
            center_x = random.randint(0, width)
            center_y = random.randint(0, height)
            radius = random.randint(100, 300)
            self.clouds.append((center_x, center_y, radius, color))
        
        # Render the nebula to the surface
        self.render()
        
        # Add scrolling
        self.scroll_y = 0
        self.scroll_speed = 0.1
        
    def render(self):
        self.surface.fill((0, 0, 0, 0))  # Clear with transparent
        
        # Draw each cloud as a collection of semi-transparent circles
        for center_x, center_y, radius, color in self.clouds:
            for _ in range(100):
                # Calculate random position within the cloud radius
                angle = random.uniform(0, math.pi * 2)
                distance = random.uniform(0, radius)
                x = center_x + math.cos(angle) * distance
                y = center_y + math.sin(angle) * distance
                
                # Calculate size and opacity based on distance from center
                size = random.randint(5, 20) * (1 - distance / radius)
                opacity = random.randint(1, 4) * (1 - distance / radius)
                
                # Create slightly varied color
                r = min(255, max(0, color[0] + random.randint(-10, 10)))
                g = min(255, max(0, color[1] + random.randint(-10, 10)))
                b = min(255, max(0, color[2] + random.randint(-10, 10)))
                
                # Draw the cloud particle
                pygame.draw.circle(self.surface, (r, g, b, opacity), (int(x), int(y)), int(size))
    
    def update(self):
        # Slowly scroll the nebula
        self.scroll_y += self.scroll_speed
        if self.scroll_y >= self.height:
            self.scroll_y = 0
    
    def draw(self, window):
        # Draw nebula with scrolling
        window.blit(self.surface, (0, int(self.scroll_y) - self.height))
        window.blit(self.surface, (0, int(self.scroll_y)))


class Starfield:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Create multiple layers of stars
        self.stars = []
        
        # Distant stars (many, small, slow)
        for _ in range(100):
            depth = random.uniform(0.1, 0.3)
            self.stars.append(Star(random.randint(0, width), random.randint(0, height), depth))
        
        # Mid-distance stars
        for _ in range(50):
            depth = random.uniform(0.3, 0.6)
            self.stars.append(Star(random.randint(0, width), random.randint(0, height), depth))
        
        # Close stars (few, large, fast)
        for _ in range(20):
            depth = random.uniform(0.6, 1.0)
            self.stars.append(Star(random.randint(0, width), random.randint(0, height), depth))
        
        # Create nebula
        self.nebula = Nebula(width, height)

    def update(self):
        # Update all stars
        for star in self.stars:
            star.update(self.height)
            
        # Update nebula
        self.nebula.update()

    def draw(self, window):
        # Draw nebula first (background)
        self.nebula.draw(window)
        
        # Draw stars by depth (distant first)
        for star in sorted(self.stars, key=lambda s: s.depth):
            star.draw(window)