import pygame
import random
import math
from typing import Optional, List
from entities.projectile import Projectile
from game.settings import Settings

class Boss:
    def __init__(self, x: int, y: int, sprite: pygame.Surface, settings: Settings):
        self.x = x
        self.y = y
        self.sprite = sprite
        self.settings = settings
        
        # Boss stats
        self.max_health = settings.BOSS_HEALTH
        self.health = self.max_health
        self.speed = settings.BOSS_SPEED
        self.alive = True
        self.points = 1000
        
        # Movement
        self.target_x = x
        self.target_y = 100
        self.movement_timer = 0
        self.movement_phase = 'enter'
        
        # Shooting patterns
        self.last_shot = 0
        self.fire_rate = 1000
        self.attack_pattern = 'spread'
        self.pattern_timer = 0
        
        # Special attacks
        self.special_attack_timer = 0
        self.special_attack_cooldown = 5000
        
        # Rectangle for collision
        self.rect = pygame.Rect(x, y, sprite.get_width(), sprite.get_height())
    
    def update(self, dt: int, player):
        """Update boss."""
        if not self.alive:
            return
        
        self.movement_timer += dt
        self.pattern_timer += dt
        self.special_attack_timer += dt
        
        # Movement phases
        if self.movement_phase == 'enter':
            if self.y < self.target_y:
                self.y += self.speed
            else:
                self.movement_phase = 'combat'
        
        elif self.movement_phase == 'combat':
            # Side-to-side movement
            if self.movement_timer % 3000 < 1500:
                self.target_x = 100
            else:
                self.target_x = self.settings.SCREEN_WIDTH - self.sprite.get_width() - 100
            
            # Move towards target
            if abs(self.x - self.target_x) > 5:
                if self.x < self.target_x:
                    self.x += self.speed
                else:
                    self.x -= self.speed
        
        # Change attack patterns
        if self.pattern_timer > 4000:
            self.attack_pattern = random.choice(['spread', 'aimed', 'spiral'])
            self.pattern_timer = 0
        
        # Update rectangle
        self.rect.x = self.x
        self.rect.y = self.y
    
    def shoot(self) -> List[Projectile]:
        """Boss shooting with different patterns."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot < self.fire_rate:
            return []
        
        self.last_shot = current_time
        projectiles = []
        
        center_x = self.x + self.sprite.get_width() // 2
        center_y = self.y + self.sprite.get_height()
        
        if self.attack_pattern == 'spread':
            # Spread shot
            for i in range(-2, 3):
                angle = i * 0.3
                vel_x = math.sin(angle) * 5
                vel_y = 8
                projectile = Projectile(center_x + i * 20, center_y, 'boss_bullet', self.settings)
                projectile.velocity_x = vel_x
                projectile.velocity_y = vel_y
                projectiles.append(projectile)
        
        elif self.attack_pattern == 'spiral':
            # Spiral pattern
            for i in range(6):
                angle = (self.movement_timer * 0.01) + (i * math.pi / 3)
                vel_x = math.cos(angle) * 4
                vel_y = math.sin(angle) * 4 + 6
                projectile = Projectile(center_x, center_y, 'boss_bullet', self.settings)
                projectile.velocity_x = vel_x
                projectile.velocity_y = vel_y
                projectiles.append(projectile)
        
        elif self.attack_pattern == 'aimed':
            # Single aimed shot (would need player position)
            projectile = Projectile(center_x, center_y, 'boss_bullet', self.settings)
            projectiles.append(projectile)
        
        return projectiles
    
    def special_attack(self) -> List[Projectile]:
        """Special attack with higher damage."""
        if self.special_attack_timer < self.special_attack_cooldown:
            return []
        
        self.special_attack_timer = 0
        projectiles = []
        
        # Massive spread attack
        center_x = self.x + self.sprite.get_width() // 2
        center_y = self.y + self.sprite.get_height()
        
        for i in range(-4, 5):
            for j in range(3):
                projectile = Projectile(
                    center_x + i * 30, 
                    center_y + j * 20, 
                    'boss_missile', 
                    self.settings
                )
                projectiles.append(projectile)
        
        return projectiles
    
    def take_damage(self, amount: int):
        """Take damage."""
        self.health -= amount
        if self.health <= 0:
            self.alive = False
    
    def render(self, surface: pygame.Surface):
        """Render boss."""
        if self.alive:
            # Flash effect when taking damage
            surface.blit(self.sprite, (self.x, self.y))
            
            # Health bar
            bar_width = self.sprite.get_width()
            bar_height = 10
            bar_x = self.x
            bar_y = self.y - 20
            
            # Background
            pygame.draw.rect(surface, (255, 0, 0), 
                           (bar_x, bar_y, bar_width, bar_height))
            # Health
            health_width = int((self.health / self.max_health) * bar_width)
            pygame.draw.rect(surface, (0, 255, 0), 
                           (bar_x, bar_y, health_width, bar_height))
            
            # Boss name
            font = pygame.font.Font(None, 36)
            text = font.render("BOSS", True, (255, 255, 255))
            text_rect = text.get_rect(center=(bar_x + bar_width // 2, bar_y - 25))
            surface.blit(text, text_rect)