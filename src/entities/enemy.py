import pygame
import random
import math
from typing import Optional
from entities.projectile import Projectile
from game.settings import Settings

class Enemy:
    def __init__(self, x: int, y: int, sprite: pygame.Surface, enemy_type: str, settings: Settings):
        self.x = x
        self.y = y
        self.sprite = sprite
        self.enemy_type = enemy_type
        self.settings = settings
        
        # Set stats based on enemy type
        if enemy_type == 'basic':
            self.health = 30
            self.speed = random.randint(2, 4)
            self.points = 10
        elif enemy_type == 'fast':
            self.health = 20
            self.speed = random.randint(4, 6)
            self.points = 15
        elif enemy_type == 'heavy':
            self.health = 60
            self.speed = random.randint(1, 3)
            self.points = 25
        
        self.max_health = self.health
        self.alive = True
        
        # Shooting (for some enemy types)
        self.last_shot = 0
        self.fire_rate = random.randint(2000, 5000)  # Random fire rate
        self.can_shoot_flag = enemy_type in ['heavy']
        
        # Movement pattern
        self.movement_pattern = random.choice(['straight', 'zigzag', 'sine'])
        self.movement_timer = 0
        self.direction = random.choice([-1, 1])
        
        # Rectangle for collision
        self.rect = pygame.Rect(x, y, sprite.get_width(), sprite.get_height())
    
    def update(self, dt: int):
        """Update enemy."""
        if not self.alive:
            return
        
        self.movement_timer += dt
        
        # Movement patterns
        if self.movement_pattern == 'straight':
            self.y += self.speed
        elif self.movement_pattern == 'zigzag':
            self.y += self.speed
            if self.movement_timer % 1000 < 500:
                self.x += self.direction * 2
            else:
                self.x -= self.direction * 2
        elif self.movement_pattern == 'sine':
            self.y += self.speed
            self.x += int(2 * math.sin(self.movement_timer * 0.005))
        
        # Keep enemy on screen horizontally
        self.x = max(0, min(self.settings.SCREEN_WIDTH - self.sprite.get_width(), self.x))
        
        # Update rectangle
        self.rect.x = self.x
        self.rect.y = self.y
    
    def shoot(self) -> Optional[Projectile]:
        """Enemy shooting."""
        if not self.can_shoot_flag:
            return None
        
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.fire_rate:
            self.last_shot = current_time
            
            # Create bullet
            bullet_x = self.x + self.sprite.get_width() // 2
            bullet_y = self.y + self.sprite.get_height()
            
            return Projectile(bullet_x, bullet_y, 'enemy_bullet', self.settings)
        
        return None
    
    def take_damage(self, amount: int):
        """Take damage."""
        self.health -= amount
        if self.health <= 0:
            self.alive = False
    
    def render(self, surface: pygame.Surface):
        """Render enemy."""
        if self.alive:
            surface.blit(self.sprite, (self.x, self.y))
            
            # Draw health bar for heavy enemies
            if self.enemy_type == 'heavy' and self.health < self.max_health:
                bar_width = self.sprite.get_width()
                bar_height = 5
                bar_x = self.x
                bar_y = self.y - 10
                
                # Background
                pygame.draw.rect(surface, (255, 0, 0), 
                               (bar_x, bar_y, bar_width, bar_height))
                # Health
                health_width = int((self.health / self.max_health) * bar_width)
                pygame.draw.rect(surface, (0, 255, 0), 
                               (bar_x, bar_y, health_width, bar_height))