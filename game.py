# File: game.py

import pygame
import random
import math
from entities import Ship, Asteroid, Bullet, FlyingSaucer, PowerUp
from particles import ParticleSystem
from starfield import Starfield
from pygame import gfxdraw

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
        self.load_fonts()
        self.load_sounds()
        self.spawn_asteroids(4)
        
        # Visual effects
        self.screen_shake = 0
        self.flash_effect = 0
        
        # Score animation
        self.score_animations = []
        
        # Game state
        self.paused = False
        self.combo = 0
        self.combo_timer = 0
        self.next_saucer = random.randint(1000, 1500)
        self.next_power_up = random.randint(600, 900)
        
        # Create surfaces for HUD elements
        self.create_hud_surfaces()

    def load_fonts(self):
        try:
            self.main_font = pygame.font.Font("fonts/Hyperspace.ttf", 36)
            self.large_font = pygame.font.Font("fonts/Hyperspace.ttf", 48)
            self.small_font = pygame.font.Font("fonts/Hyperspace.ttf", 24)
        except:
            # Fallback to default font if custom font not available
            self.main_font = pygame.font.Font(None, 36)
            self.large_font = pygame.font.Font(None, 48)
            self.small_font = pygame.font.Font(None, 24)

    def create_hud_surfaces(self):
        # Create a translucent surface for the HUD background
        self.hud_surface = pygame.Surface((self.width, 60), pygame.SRCALPHA)
        self.hud_surface.fill((0, 0, 0, 128))  # Semi-transparent black
        
        # Create life icon
        self.life_icon = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.polygon(self.life_icon, (255, 255, 255), [
            (10, 0),  # Top point
            (0, 20),  # Bottom left
            (20, 20)  # Bottom right
        ], 1)

    def load_sounds(self):
        try:
            self.shoot_sound = pygame.mixer.Sound("sounds/shoot.wav")
            self.explosion_sound = pygame.mixer.Sound("sounds/explosion.wav")
            self.thrust_sound = pygame.mixer.Sound("sounds/thrust.wav")
            self.power_up_sound = pygame.mixer.Sound("sounds/powerup.wav")
            self.ufo_sound = pygame.mixer.Sound("sounds/ufo.wav")
            self.game_over_sound = pygame.mixer.Sound("sounds/gameover.wav")
            self.level_up_sound = pygame.mixer.Sound("sounds/levelup.wav")
            
            # Background music
            pygame.mixer.music.load("sounds/background.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)  # Loop indefinitely
            
        except:
            # Fallback to simpler sounds if files aren't available
            self.shoot_sound = pygame.mixer.Sound(self._generate_shoot_sound())
            self.explosion_sound = pygame.mixer.Sound(self._generate_explosion_sound())
            self.thrust_sound = pygame.mixer.Sound(self._generate_thrust_sound())
            self.power_up_sound = self.shoot_sound  # Reuse sound
            self.ufo_sound = self.shoot_sound  # Reuse sound
            self.game_over_sound = self.explosion_sound  # Reuse sound
            self.level_up_sound = self.shoot_sound  # Reuse sound
    
    def _generate_shoot_sound(self):
        """Generate a simple shoot sound if file not available"""
        pygame.mixer.init(frequency=44100, size=-16, channels=1)
        sound = pygame.sndarray.array([4096 * math.sin(2.0 * math.pi * 440 * t / 44100) 
                                       for t in range(44100//8)])
        return sound
        
    def _generate_explosion_sound(self):
        """Generate a simple explosion sound if file not available"""
        pygame.mixer.init(frequency=44100, size=-16, channels=1)
        sound = pygame.sndarray.array([(4096 * random.random() - 2048) 
                                       for t in range(44100//4)])
        return sound
        
    def _generate_thrust_sound(self):
        """Generate a simple thrust sound if file not available"""
        pygame.mixer.init(frequency=44100, size=-16, channels=1)
        sound = pygame.sndarray.array([(2048 * random.random()) 
                                       for t in range(44100//8)])
        return sound

    def reset(self):
        self.ship = Ship(self.width // 2, self.height // 2)
        self.asteroids = []
        self.bullets = []
        self.flying_saucers = []
        self.power_ups = []
        self.score = 0
        self.lives = 3
        self.level = 1
        self.combo = 0
        self.combo_timer = 0
        self.spawn_asteroids(4)
        self.next_saucer = random.randint(1000, 1500)
        self.next_power_up = random.randint(600, 900)
        self.screen_shake = 0
        self.flash_effect = 0
        self.score_animations = []
        self.paused = False

    def spawn_asteroids(self, num):
        for _ in range(num):
            size = random.randint(1, 3)
            asteroid = Asteroid(size, self.width, self.height)
            # Make sure asteroids don't spawn too close to the ship
            while math.hypot(asteroid.position[0] - self.ship.position[0], 
                           asteroid.position[1] - self.ship.position[1]) < 150:
                asteroid.position = asteroid.get_spawn_position(self.width, self.height)
            self.asteroids.append(asteroid)

    def run(self):
        # Check for game events
        quit_game = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.paused:
                    self.fire_weapon()
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                elif event.key == pygame.K_ESCAPE:
                    quit_game = True

        if not self.paused:
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
        
        # Always draw the game (even when paused)
        self.draw()
        
        if self.paused:
            # Draw pause screen overlay
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Semi-transparent black
            self.window.blit(overlay, (0, 0))
            
            # Draw "PAUSED" text
            pause_text = self.large_font.render("PAUSED", True, (255, 255, 255))
            pause_rect = pause_text.get_rect(center=(self.width // 2, self.height // 2))
            self.window.blit(pause_text, pause_rect)
            
            # Draw controls reminder
            controls_text = self.small_font.render("Press P to resume, ESC to quit", True, (200, 200, 200))
            controls_rect = controls_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
            self.window.blit(controls_text, controls_rect)

        return quit_game or self.lives <= 0

    def fire_weapon(self):
        # Normal bullet
        if not self.ship.rapid_fire_active and not self.ship.multi_shot_active:
            self.bullets.append(Bullet(self.ship.position, self.ship.angle))
            self.shoot_sound.play()
        
        # Rapid fire (multiple bullets in sequence)
        elif self.ship.rapid_fire_active and not self.ship.multi_shot_active:
            # Add slight spread to rapid fire
            self.bullets.append(Bullet(self.ship.position, self.ship.angle + random.uniform(-3, 3), 1.5))
            self.shoot_sound.play()
        
        # Multi-shot (spread pattern)
        elif self.ship.multi_shot_active:
            for i in range(3):  # 3 bullets in a spread
                angle_offset = (i - 1) * 15  # -15, 0, 15 degrees
                self.bullets.append(Bullet(self.ship.position, self.ship.angle + angle_offset, 1.2))
            self.shoot_sound.play()

    def update(self):
        # Screen shake effect (gradually reduce)
        if self.screen_shake > 0:
            self.screen_shake -= 1
            
        # Flash effect (gradually reduce)
        if self.flash_effect > 0:
            self.flash_effect -= 1
        
        # Update ship
        self.ship.update(self.width, self.height)
        
        # Update asteroids
        for asteroid in self.asteroids:
            asteroid.update(self.width, self.height)
        
        # Update bullets
        for bullet in self.bullets:
            bullet.update(self.width, self.height)
        
        # Update flying saucers
        for saucer in self.flying_saucers:
            saucer_bullet = saucer.update(self.ship, self.width, self.height)
            if saucer_bullet:
                self.bullets.append(saucer_bullet)
                self.shoot_sound.play()
        
        # Update power-ups
        for power_up in self.power_ups:
            power_up.update()

        # Update particles and starfield
        self.particle_system.update()
        self.starfield.update()
        
        # Update score animations
        for anim in self.score_animations[:]:
            anim['life'] -= 1
            anim['y'] -= 1  # Move up
            if anim['life'] <= 0:
                self.score_animations.remove(anim)

        # Spawn flying saucers
        self.next_saucer -= 1
        if self.next_saucer <= 0:
            self.flying_saucers.append(FlyingSaucer(self.width, self.height))
            self.ufo_sound.play()
            self.next_saucer = random.randint(1000, 1500)

        # Spawn power-ups
        self.next_power_up -= 1
        if self.next_power_up <= 0:
            power_type = random.choice(["shield", "rapid_fire", "multi_shot", "extra_life"])
            self.power_ups.append(PowerUp(power_type, self.width, self.height))
            self.next_power_up = random.randint(600, 900)

        # Update combo system
        if self.combo > 0:
            self.combo_timer -= 1
            if self.combo_timer <= 0:
                self.combo = 0

        # Remove expired bullets and power-ups
        self.bullets = [bullet for bullet in self.bullets if bullet.lifetime > 0]
        self.power_ups = [power_up for power_up in self.power_ups if power_up.duration > 0]

        # Level progression
        if len(self.asteroids) == 0:
            self.level += 1
            self.level_up_sound.play()
            
            # Screen flash effect
            self.flash_effect = 10
            
            # Add score for completing level
            level_bonus = 1000 * self.level
            self.add_score(level_bonus, (self.width // 2, self.height // 2), "LEVEL BONUS")
            
            # Spawn more asteroids based on level
            self.spawn_asteroids(self.level + 3)

    def check_collisions(self):
        for bullet in self.bullets[:]:
            if bullet in self.bullets:  # Check if bullet still exists
                # Bullet-Asteroid collision
                for asteroid in self.asteroids[:]:
                    if asteroid in self.asteroids and bullet in self.bullets:  # Double-check
                        if bullet.collides_with(asteroid):
                            self.bullets.remove(bullet)
                            self.asteroids.remove(asteroid)
                            self.explosion_sound.play()
                            
                            # Add screen shake for big asteroids
                            if asteroid.size >= 2:
                                self.screen_shake = asteroid.size * 3
                            
                            # Calculate score based on asteroid size and combo
                            base_score = 100 * asteroid.size
                            combo_multiplier = 1.0 + (self.combo * 0.1)  # 10% bonus per combo level
                            score_value = int(base_score * combo_multiplier)
                            
                            # Add score and update combo
                            self.add_score(score_value, asteroid.position)
                            self.combo += 1
                            self.combo_timer = 120  # 2 seconds to continue combo
                            
                            # Create explosion
                            self.particle_system.create_explosion(asteroid.position, size=asteroid.size)
                            
                            # Split asteroid if large enough
                            if asteroid.size > 1:
                                for _ in range(2):
                                    smaller = Asteroid(asteroid.size - 1, self.width, self.height, asteroid.position)
                                    self.asteroids.append(smaller)
                            break

            if bullet in self.bullets:  # Check if bullet still exists after asteroid check
                # Bullet-Flying Saucer collision
                for saucer in self.flying_saucers[:]:
                    if bullet.collides_with(saucer):
                        self.bullets.remove(bullet)
                        self.flying_saucers.remove(saucer)
                        self.explosion_sound.play()
                        
                        # Add screen shake
                        self.screen_shake = saucer.size * 4
                        
                        # Calculate score
                        base_score = 500 * saucer.size
                        combo_multiplier = 1.0 + (self.combo * 0.1)
                        score_value = int(base_score * combo_multiplier)
                        
                        # Add score and update combo
                        self.add_score(score_value, saucer.position, "SAUCER")
                        self.combo += 2  # Higher combo for saucers
                        self.combo_timer = 120
                        
                        # Create explosion
                        self.particle_system.create_explosion(saucer.position, size=saucer.size+1, 
                                                           color=(150, 150, 255))
                        break

        # Ship-Asteroid collision
        for asteroid in self.asteroids:
            if self.ship.collides_with(asteroid):
                self.lives -= 1
                self.explosion_sound.play()
                
                # Maximum screen shake
                self.screen_shake = 20
                
                # Create explosion
                self.particle_system.create_explosion(self.ship.position, size=3, 
                                                   color=(255, 200, 50))
                
                # Reset combo
                self.combo = 0
                
                # Reset ship position
                self.ship.reset(self.width // 2, self.height // 2)
                break

        # Ship-Flying Saucer collision
        for saucer in self.flying_saucers[:]:
            if self.ship.collides_with(saucer):
                self.lives -= 1
                self.explosion_sound.play()
                
                # Maximum screen shake
                self.screen_shake = 20
                
                # Create explosion
                self.particle_system.create_explosion(self.ship.position, size=3, 
                                                   color=(255, 200, 50))
                self.particle_system.create_explosion(saucer.position, size=2, 
                                                   color=(150, 150, 255))
                
                # Remove the saucer
                self.flying_saucers.remove(saucer)
                
                # Reset combo
                self.combo = 0
                
                # Reset ship position
                self.ship.reset(self.width // 2, self.height // 2)
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
                elif power_up.type == "extra_life":
                    self.lives += 1
                    
                # Play power-up sound
                self.power_up_sound.play()
                
                # Create power-up particles
                self.particle_system.create_effect(power_up.position, power_up.color)
                
                # Add score
                self.add_score(250, power_up.position, "POWER-UP")
                
                # Remove the power-up
                self.power_ups.remove(power_up)

    def add_score(self, value, position, text=""):
        # Add to total score
        self.score += value
        
        # Create score animation
        color = (255, 255, 255)
        if self.combo >= 10:
            color = (255, 100, 100)  # Red for high combos
        elif self.combo >= 5:
            color = (255, 255, 100)  # Yellow for medium combos
            
        display_text = f"+{value}"
        if text:
            display_text = f"{text}: +{value}"
            
        self.score_animations.append({
            'text': display_text,
            'x': position[0],
            'y': position[1],
            'life': 60,  # 1 second
            'color': color
        })

    def draw(self):
        # Apply screen shake
        shake_offset = (0, 0)
        if self.screen_shake > 0:
            shake_offset = (random.randint(-self.screen_shake, self.screen_shake),
                           random.randint(-self.screen_shake, self.screen_shake))
            
        # Clear screen
        self.window.fill((0, 0, 0))
        
        # Draw flash effect
        if self.flash_effect > 0:
            alpha = min(255, self.flash_effect * 25)
            flash_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            flash_surface.fill((255, 255, 255, alpha))
            self.window.blit(flash_surface, (0, 0))
        
        # Draw starfield
        self.starfield.draw(self.window)
        
        # Draw game elements with screen shake
        for obj in [*self.asteroids, *self.bullets, *self.flying_saucers, *self.power_ups]:
            # Save original position
            orig_pos = obj.position.copy() if hasattr(obj, 'position') else None
            
            # Apply screen shake
            if orig_pos:
                obj.position[0] += shake_offset[0]
                obj.position[1] += shake_offset[1]
            
            # Draw the object
            obj.draw(self.window)
            
            # Restore original position
            if orig_pos:
                obj.position = orig_pos
        
        # Draw particles
        self.particle_system.draw(self.window, shake_offset)
        
        # Draw ship (with screen shake)
        orig_ship_pos = self.ship.position.copy()
        self.ship.position[0] += shake_offset[0]
        self.ship.position[1] += shake_offset[1]
        self.ship.draw(self.window)
        self.ship.position = orig_ship_pos
        
        # Draw HUD
        self.draw_hud()
        
        # Draw score animations
        for anim in self.score_animations:
            alpha = min(255, anim['life'] * 4)
            color = list(anim['color'])
            text = self.small_font.render(anim['text'], True, color)
            text.set_alpha(alpha)
            text_rect = text.get_rect(center=(anim['x'] + shake_offset[0], 
                                             anim['y'] + shake_offset[1]))
            self.window.blit(text, text_rect)
        
        # Draw active power-up indicators
        self.draw_power_up_indicators()
        
        # Draw combo indicator
        if self.combo > 0:
            combo_text = f"COMBO x{self.combo}"
            combo_color = (255, 255, 255)
            if self.combo >= 10:
                combo_color = (255, 100, 100)  # Red for high combos
            elif self.combo >= 5:
                combo_color = (255, 255, 100)  # Yellow for medium combos
                
            combo_surface = self.small_font.render(combo_text, True, combo_color)
            combo_rect = combo_surface.get_rect(center=(self.width // 2, self.height - 30))
            self.window.blit(combo_surface, combo_rect)

    def draw_hud(self):
        # Draw HUD background
        self.window.blit(self.hud_surface, (0, 0))
        
        # Draw score
        score_text = self.main_font.render(f"SCORE: {self.score}", True, (255, 255, 255))
        self.window.blit(score_text, (20, 15))
        
        # Draw level
        level_text = self.main_font.render(f"LEVEL: {self.level}", True, (255, 255, 255))
        level_rect = level_text.get_rect(center=(self.width // 2, 30))
        self.window.blit(level_text, level_rect)
        
        # Draw lives
        for i in range(self.lives):
            life_x = self.width - 30 - (i * 30)
            self.window.blit(self.life_icon, (life_x, 20))

    def draw_power_up_indicators(self):
        indicators = []
        
        # Check active power-ups
        if self.ship.shield_active:
            indicators.append(("SHIELD", (0, 200, 255), self.ship.shield_timer / 300))
            
        if self.ship.rapid_fire_active:
            indicators.append(("RAPID FIRE", (255, 200, 0), self.ship.rapid_fire_timer / 300))
            
        if self.ship.multi_shot_active:
            indicators.append(("MULTI-SHOT", (255, 0, 255), self.ship.multi_shot_timer / 300))
        
        # Draw indicators
        for i, (text, color, progress) in enumerate(indicators):
            # Position at bottom of screen
            y_pos = self.height - 10 - (i * 25)
            
            # Draw text
            text_surface = self.small_font.render(text, True, color)
            self.window.blit(text_surface, (10, y_pos))
            
            # Draw progress bar
            bar_width = 100
            pygame.draw.rect(self.window, (100, 100, 100), (110, y_pos + 10, bar_width, 10))
            pygame.draw.rect(self.window, color, (110, y_pos + 10, int(bar_width * progress), 10))