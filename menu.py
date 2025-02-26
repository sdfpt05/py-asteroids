# File: menu.py

import pygame
import math
import random
from starfield import Starfield

class MenuItem:
    def __init__(self, text, action, font, position):
        self.text = text
        self.action = action
        self.font = font
        self.position = position
        self.selected = False
        self.hover_factor = 0
        self.hover_dir = 1
        self.pulse_offset = random.random() * math.pi * 2
        
    def update(self):
        # Update hover animation
        if self.selected:
            self.hover_factor += 0.05 * self.hover_dir
            if self.hover_factor >= 1.0:
                self.hover_factor = 1.0
                self.hover_dir = -1
            elif self.hover_factor <= 0.5:
                self.hover_factor = 0.5
                self.hover_dir = 1
        else:
            self.hover_factor = 0
            
    def draw(self, window, time):
        text_color = (255, 255, 255)
        shadow_offset = 2
        
        if self.selected:
            # Pulsing highlight effect
            pulse = math.sin(time * 0.005 + self.pulse_offset) * 0.5 + 0.5
            highlight_size = int(30 + 10 * pulse)
            
            # Draw glow
            for i in range(3):
                size = highlight_size - i * 5
                alpha = int(100 - i * 30)
                glow_color = (50, 100, 255, alpha)
                
                glow_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, glow_color, (size, size), size)
                
                # Position glow
                glow_rect = glow_surf.get_rect(center=self.position)
                window.blit(glow_surf, glow_rect)
            
            # Use brighter color for selected item
            text_color = (100, 200, 255)  # Bright blue
            shadow_offset = 3
        
        # Draw text shadow first
        shadow_surf = self.font.render(self.text, True, (0, 0, 0))
        shadow_rect = shadow_surf.get_rect(center=(self.position[0] + shadow_offset, 
                                                 self.position[1] + shadow_offset))
        window.blit(shadow_surf, shadow_rect)
        
        # Draw main text
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.position)
        window.blit(text_surf, text_rect)

class Menu:
    def __init__(self, window, width, height):
        self.window = window
        self.width = width
        self.height = height
        
        # Load fonts
        try:
            self.title_font = pygame.font.Font("fonts/Hyperspace.ttf", 72)
            self.menu_font = pygame.font.Font("fonts/Hyperspace.ttf", 36)
            self.small_font = pygame.font.Font("fonts/Hyperspace.ttf", 24)
        except:
            # Fallback to default font
            self.title_font = pygame.font.Font(None, 72)
            self.menu_font = pygame.font.Font(None, 36)
            self.small_font = pygame.font.Font(None, 24)
        
        # Initialize starfield
        self.starfield = Starfield(width, height)
        
        # Create menu items
        self.main_menu_items = [
            MenuItem("START GAME", "start", self.menu_font, (width // 2, height * 2 // 3)),
            MenuItem("QUIT", "quit", self.menu_font, (width // 2, height * 3 // 4))
        ]
        
        self.game_over_menu_items = [
            MenuItem("PLAY AGAIN", "restart", self.menu_font, (width // 2, height * 2 // 3)),
            MenuItem("MAIN MENU", "menu", self.menu_font, (width // 2, height * 3 // 4))
        ]
        
        # Select first item by default
        self.selected_index = 0
        self.main_menu_items[self.selected_index].selected = True
        
        # Create particle system for menu effects
        self.particles = []
        
        # Load high score
        self.load_high_score()
        
        # Play sound effects
        self.load_sounds()
        
        # Decorative asteroid animation
        self.rotating_asteroids = self.create_decorative_asteroids()
        
        # Animation effects
        self.title_offset = 0
        self.title_direction = 1
        
    def load_sounds(self):
        try:
            self.select_sound = pygame.mixer.Sound("sounds/select.wav")
            self.confirm_sound = pygame.mixer.Sound("sounds/confirm.wav")
        except:
            # Fallback to simpler sounds
            self.select_sound = pygame.mixer.Sound(self._generate_select_sound())
            self.confirm_sound = pygame.mixer.Sound(self._generate_confirm_sound())
    
    def _generate_select_sound(self):
        """Generate a simple select sound if file not available"""
        pygame.mixer.init(frequency=44100, size=-16, channels=1)
        sound = pygame.sndarray.array([4096 * math.sin(2.0 * math.pi * 440 * t / 44100) 
                                     for t in range(44100//16)])
        return sound
        
    def _generate_confirm_sound(self):
        """Generate a simple confirm sound if file not available"""
        pygame.mixer.init(frequency=44100, size=-16, channels=1)
        sound = pygame.sndarray.array([4096 * math.sin(2.0 * math.pi * 880 * t / 44100) 
                                     for t in range(44100//8)])
        return sound

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
            return True  # New high score achieved
        return False  # No new high score

    def create_particle(self, position, color):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(0.5, 2.0)
        velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
        return {
            'pos': list(position),
            'velocity': velocity,
            'color': color,
            'size': random.uniform(1, 3),
            'life': random.randint(30, 60)
        }

    def update_particles(self):
        # Update existing particles
        for particle in self.particles[:]:
            particle['pos'][0] += particle['velocity'][0]
            particle['pos'][1] += particle['velocity'][1]
            particle['life'] -= 1
            
            # Remove expired particles
            if particle['life'] <= 0:
                self.particles.remove(particle)
        
        # Generate new particles around menu items
        current_items = self.main_menu_items if self.game_over_menu_items[0].selected == False else self.game_over_menu_items
        for item in current_items:
            if item.selected and random.random() < 0.1:  # 10% chance each frame
                pos = (item.position[0] + random.uniform(-100, 100),
                      item.position[1] + random.uniform(-20, 20))
                color = (100, 200, 255)  # Blue particles
                self.particles.append(self.create_particle(pos, color))

    def create_decorative_asteroids(self):
        asteroids = []
        for _ in range(5):
            angle = random.uniform(0, math.pi * 2)
            distance = random.uniform(100, 300)
            x = self.width // 2 + math.cos(angle) * distance
            y = self.height // 3 + math.sin(angle) * distance
            
            asteroids.append({
                'pos': [x, y],
                'vel': [random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)],
                'radius': random.randint(20, 50),
                'rotation': random.uniform(0, 360),
                'rot_speed': random.uniform(-1, 1),
                'vertices': self._generate_asteroid_vertices(random.randint(20, 50))
            })
        return asteroids
    
    def _generate_asteroid_vertices(self, radius):
        num_vertices = random.randint(8, 12)
        vertices = []
        for i in range(num_vertices):
            angle = i * (2 * math.pi / num_vertices)
            distance = radius * random.uniform(0.8, 1.2)
            x = distance * math.cos(angle)
            y = distance * math.sin(angle)
            vertices.append((x, y))
        return vertices

    def update_decorative_asteroids(self):
        for asteroid in self.rotating_asteroids:
            # Update position
            asteroid['pos'][0] += asteroid['vel'][0]
            asteroid['pos'][1] += asteroid['vel'][1]
            
            # Update rotation
            asteroid['rotation'] += asteroid['rot_speed']
            
            # Screen wrapping
            if asteroid['pos'][0] < -asteroid['radius']:
                asteroid['pos'][0] = self.width + asteroid['radius']
            elif asteroid['pos'][0] > self.width + asteroid['radius']:
                asteroid['pos'][0] = -asteroid['radius']
                
            if asteroid['pos'][1] < -asteroid['radius']:
                asteroid['pos'][1] = self.height + asteroid['radius']
            elif asteroid['pos'][1] > self.height + asteroid['radius']:
                asteroid['pos'][1] = -asteroid['radius']

    def draw_decorative_asteroids(self, window):
        for asteroid in self.rotating_asteroids:
            # Rotate vertices
            rotated_vertices = []
            for x, y in asteroid['vertices']:
                cos_rot = math.cos(math.radians(asteroid['rotation']))
                sin_rot = math.sin(math.radians(asteroid['rotation']))
                rotated_x = x * cos_rot - y * sin_rot
                rotated_y = x * sin_rot + y * cos_rot
                rotated_vertices.append((asteroid['pos'][0] + rotated_x, 
                                       asteroid['pos'][1] + rotated_y))
            
            # Draw asteroid outline
            pygame.draw.polygon(window, (100, 100, 100), rotated_vertices)
            pygame.draw.polygon(window, (255, 255, 255), rotated_vertices, 2)

    def run(self):
        clock = pygame.time.Clock()
        selected_menu_items = self.main_menu_items
        
        while True:
            time = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_menu_items[self.selected_index].selected = False
                        self.selected_index = (self.selected_index - 1) % len(selected_menu_items)
                        selected_menu_items[self.selected_index].selected = True
                        self.select_sound.play()
                    elif event.key == pygame.K_DOWN:
                        selected_menu_items[self.selected_index].selected = False
                        self.selected_index = (self.selected_index + 1) % len(selected_menu_items)
                        selected_menu_items[self.selected_index].selected = True
                        self.select_sound.play()
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.confirm_sound.play()
                        return selected_menu_items[self.selected_index].action

            # Update starfield
            self.starfield.update()
            
            # Update particles
            self.update_particles()
            
            # Update decorative asteroids
            self.update_decorative_asteroids()
            
            # Update menu items animations
            for item in selected_menu_items:
                item.update()
                
            # Update title animation
            self.title_offset += 0.2 * self.title_direction
            if abs(self.title_offset) > 10:
                self.title_direction *= -1

            # Draw background
            self.window.fill((0, 0, 0))
            self.starfield.draw(self.window)
            
            # Draw decorative asteroids
            self.draw_decorative_asteroids(self.window)
            
            # Draw particles
            for particle in self.particles:
                alpha = int((particle['life'] / 60) * 255)
                color = list(particle['color']) + [alpha]
                size = particle['size'] * (particle['life'] / 60)
                pygame.draw.circle(self.window, color, 
                                 (int(particle['pos'][0]), int(particle['pos'][1])), 
                                 int(size))
            
            # Draw title with floating effect
            title_y = self.height // 3 + self.title_offset
            self.draw_text("ASTEROIDS", self.title_font, (255, 255, 255), 
                         (self.width // 2, title_y))
            
            # Draw menu items
            for item in selected_menu_items:
                item.draw(self.window, time)
            
            # Draw high score
            high_score_text = f"HIGH SCORE: {self.high_score}"
            self.draw_text(high_score_text, self.small_font, (200, 200, 200), 
                         (self.width // 2, self.height * 7 // 8))
            
            pygame.display.flip()
            clock.tick(60)

    def run_game_over(self, score):
        # Check if new high score was achieved
        new_high_score = self.save_high_score(score)
        
        # Reset selected index
        self.selected_index = 0
        for i, item in enumerate(self.game_over_menu_items):
            item.selected = (i == self.selected_index)
        
        clock = pygame.time.Clock()
        
        while True:
            time = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.game_over_menu_items[self.selected_index].selected = False
                        self.selected_index = (self.selected_index - 1) % len(self.game_over_menu_items)
                        self.game_over_menu_items[self.selected_index].selected = True
                        self.select_sound.play()
                    elif event.key == pygame.K_DOWN:
                        self.game_over_menu_items[self.selected_index].selected = False
                        self.selected_index = (self.selected_index + 1) % len(self.game_over_menu_items)
                        self.game_over_menu_items[self.selected_index].selected = True
                        self.select_sound.play()
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.confirm_sound.play()
                        return self.game_over_menu_items[self.selected_index].action

            # Update starfield
            self.starfield.update()
            
            # Update particles
            self.update_particles()
            
            # Update decorative asteroids
            self.update_decorative_asteroids()
            
            # Update menu items animations
            for item in self.game_over_menu_items:
                item.update()
                
            # Update title animation
            self.title_offset += 0.2 * self.title_direction
            if abs(self.title_offset) > 10:
                self.title_direction *= -1

            # Draw background
            self.window.fill((0, 0, 0))
            self.starfield.draw(self.window)
            
            # Draw decorative asteroids
            self.draw_decorative_asteroids(self.window)
            
            # Draw particles
            for particle in self.particles:
                alpha = int((particle['life'] / 60) * 255)
                color = list(particle['color']) + [alpha]
                size = particle['size'] * (particle['life'] / 60)
                pygame.draw.circle(self.window, color, 
                                 (int(particle['pos'][0]), int(particle['pos'][1])), 
                                 int(size))
            
            # Draw Game Over text with floating effect
            title_y = self.height // 4 + self.title_offset
            self.draw_text("GAME OVER", self.title_font, (255, 50, 50), 
                         (self.width // 2, title_y))
            
            # Draw score
            score_text = f"FINAL SCORE: {score}"
            self.draw_text(score_text, self.menu_font, (255, 255, 255), 
                         (self.width // 2, self.height // 2))
            
            # Draw new high score message if achieved
            if new_high_score:
                self.draw_text("NEW HIGH SCORE!", self.menu_font, (255, 255, 0), 
                             (self.width // 2, self.height // 2 + 50))
            
            # Draw menu items
            for item in self.game_over_menu_items:
                item.draw(self.window, time)
            
            # Draw high score
            high_score_text = f"HIGH SCORE: {self.high_score}"
            self.draw_text(high_score_text, self.small_font, (200, 200, 200), 
                         (self.width // 2, self.height * 7 // 8))
            
            pygame.display.flip()
            clock.tick(60)

    def draw_text(self, text, font, color, position):
        # Draw text shadow
        shadow_surface = font.render(text, True, (0, 0, 0))
        shadow_rect = shadow_surface.get_rect(center=(position[0] + 2, position[1] + 2))
        self.window.blit(shadow_surface, shadow_rect)
        
        # Draw main text
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=position)
        self.window.blit(text_surface, text_rect)