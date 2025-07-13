import pygame
import math
import random
from game.settings import Settings

class Projectile:
    def __init__(self, x: int, y: int, projectile_type: str, settings: Settings, 
                 angle: float = 0, damage: int = 10):
        self.x = float(x)
        self.y = float(y)
        self.projectile_type = projectile_type
        self.settings = settings
        self.alive = True
        self.angle = angle
        self.damage = damage
        
        # Visual effects
        self.trail_positions = []
        self.particle_timer = 0
        self.glow_intensity = 0
        
        # Set properties based on type
        if projectile_type == 'basic' or projectile_type == 'player_bullet':
            self.velocity_x = math.sin(angle) * 3
            self.velocity_y = -settings.BULLET_SPEED + math.cos(angle) * 3
            self.width = 4
            self.height = 12
            self.color = (255, 255, 100)
            self.glow_color = (255, 255, 0)
        
        elif projectile_type == 'enhanced':
            self.velocity_x = math.sin(angle) * 3
            self.velocity_y = -settings.BULLET_SPEED * 1.2 + math.cos(angle) * 3
            self.width = 6
            self.height = 15
            self.color = (100, 255, 255)
            self.glow_color = (0, 255, 255)
        
        elif projectile_type == 'missile':
            self.velocity_x = math.sin(angle) * 2
            self.velocity_y = -settings.MISSILE_SPEED + math.cos(angle) * 2
            self.width = 8
            self.height = 20
            self.color = (255, 100, 0)
            self.glow_color = (255, 0, 0)
        
        elif projectile_type == 'laser':
            self.velocity_x = 0
            self.velocity_y = -settings.BULLET_SPEED * 2
            self.width = 6
            self.height = 30
            self.color = (255, 50, 255)
            self.glow_color = (255, 0, 255)
        
        elif projectile_type == 'enemy_bullet':
            self.velocity_x = math.sin(angle) * 2
            self.velocity_y = settings.BULLET_SPEED // 2 + math.cos(angle) * 2
            self.width = 4
            self.height = 8
            self.color = (255, 50, 50)
            self.glow_color = (255, 0, 0)
        
        elif projectile_type == 'boss_bullet':
            self.velocity_x = math.sin(angle) * 4
            self.velocity_y = settings.BULLET_SPEED // 2 + math.cos(angle) * 4
            self.width = 6
            self.height = 12
            self.color = (255, 0, 255)
            self.glow_color = (150, 0, 150)
        
        elif projectile_type == 'boss_missile':
            self.velocity_x = math.sin(angle) * 3
            self.velocity_y = settings.MISSILE_SPEED + math.cos(angle) * 3
            self.width = 8
            self.height = 16
            self.color = (255, 100, 0)
            self.glow_color = (255, 50, 0)
        
        # Rectangle for collision
        self.rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
    
    def update(self, dt: int):
        """Update projectile with enhanced effects."""
        if not self.alive:
            return
        
        # Store trail position
        self.trail_positions.append((self.x, self.y))
        if len(self.trail_positions) > 8:
            self.trail_positions.pop(0)
        
        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Update visual effects
        self.particle_timer += dt
        self.glow_intensity = (math.sin(self.particle_timer * 0.01) + 1) * 0.5
        
        # Update rectangle
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
    
    def render(self, surface: pygame.Surface):
        """Render projectile with enhanced visual effects."""
        if not self.alive:
            return
        
        # Render trail
        for i, (trail_x, trail_y) in enumerate(self.trail_positions):
            alpha = int(255 * (i / len(self.trail_positions)) * 0.5)
            trail_color = (*self.color, alpha)
            
            # Create trail segment
            trail_surface = pygame.Surface((self.width // 2, self.height // 2), pygame.SRCALPHA)
            trail_surface.fill(trail_color)
            surface.blit(trail_surface, (int(trail_x), int(trail_y)))
        
        # Render glow effect
        glow_radius = max(self.width, self.height) // 2 + 5
        glow_alpha = int(100 + 50 * self.glow_intensity)
        
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        glow_color = (*self.glow_color, glow_alpha)
        
        # Multiple glow layers for depth
        for radius in range(glow_radius, 0, -2):
            layer_alpha = int(glow_alpha * (1 - radius / glow_radius))
            layer_color = (*self.glow_color, layer_alpha)
            pygame.draw.circle(glow_surface, layer_color, 
                             (glow_radius, glow_radius), radius)
        
        glow_x = int(self.x - glow_radius + self.width // 2)
        glow_y = int(self.y - glow_radius + self.height // 2)
        surface.blit(glow_surface, (glow_x, glow_y))
        
        # Render main projectile
        if self.projectile_type == 'laser':
            # Special laser rendering
            for i in range(0, self.height, 3):
                segment_alpha = int(255 * (1 - i / self.height))
                segment_color = (*self.color, segment_alpha)
                
                segment_surface = pygame.Surface((self.width, 3), pygame.SRCALPHA)
                segment_surface.fill(segment_color)
                surface.blit(segment_surface, (int(self.x), int(self.y + i)))
        else:
            # Standard projectile rendering with gradient
            projectile_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
            # Create gradient effect
            for i in range(self.height):
                alpha = int(255 * (1 - i / self.height))
                line_color = (*self.color, alpha)
                pygame.draw.line(projectile_surface, line_color,
                               (0, i), (self.width, i))
            
            surface.blit(projectile_surface, (int(self.x), int(self.y)))
        
        # Special effects for enhanced projectiles
        if self.projectile_type in ['enhanced', 'missile']:
            # Add sparkle effect
            sparkle_x = int(self.x + random.randint(-2, 2))
            sparkle_y = int(self.y + random.randint(-2, 2))
            sparkle_color = (255, 255, 255, 150)
            
            sparkle_surface = pygame.Surface((2, 2), pygame.SRCALPHA)
            sparkle_surface.fill(sparkle_color)
            surface.blit(sparkle_surface, (sparkle_x, sparkle_y))