import pygame
import math
from game.settings import Settings

class PowerUp:
    def __init__(self, x: int, y: int, sprite: pygame.Surface, powerup_type: str, settings: Settings):
        self.x = x
        self.y = y
        self.sprite = sprite
        self.powerup_type = powerup_type
        self.settings = settings
        self.alive = True
        
        # Movement
        self.speed = 2
        self.float_timer = 0
        self.original_y = y
        
        # Visual effects
        self.glow_timer = 0
        self.rotation = 0
        
        # Rectangle for collision
        self.rect = pygame.Rect(x, y, sprite.get_width(), sprite.get_height())
    
    def update(self, dt: int):
        """Update powerup."""
        if not self.alive:
            return
        
        self.float_timer += dt * 0.003
        self.glow_timer += dt * 0.01
        self.rotation += 2
        
        # Floating motion
        self.y = self.original_y + math.sin(self.float_timer) * 10
        self.original_y += self.speed
        
        # Update rectangle
        self.rect.x = self.x
        self.rect.y = self.y
    
    def render(self, surface: pygame.Surface):
        """Render powerup with effects."""
        if self.alive:
            # Glow effect
            glow_alpha = int(128 + 127 * math.sin(self.glow_timer))
            glow_color = self.get_glow_color()
            
            # Create glow surface
            glow_size = max(self.sprite.get_width(), self.sprite.get_height()) + 20
            glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*glow_color, glow_alpha // 2), 
                             (glow_size // 2, glow_size // 2), glow_size // 2)
            
            # Blit glow
            glow_x = self.x - (glow_size - self.sprite.get_width()) // 2
            glow_y = self.y - (glow_size - self.sprite.get_height()) // 2
            surface.blit(glow_surface, (glow_x, glow_y))
            
            # Rotate and blit sprite
            rotated_sprite = pygame.transform.rotate(self.sprite, self.rotation)
            rotated_rect = rotated_sprite.get_rect(center=(self.x + self.sprite.get_width() // 2,
                                                         self.y + self.sprite.get_height() // 2))
            surface.blit(rotated_sprite, rotated_rect)
    
    def get_glow_color(self):
        """Get glow color based on powerup type."""
        colors = {
            'health': (0, 255, 0),      # Green
            'rapid_fire': (255, 255, 0), # Yellow
            'shield': (0, 255, 255),    # Cyan
            'missile': (255, 0, 255)    # Magenta
        }
        return colors.get(self.powerup_type, (255, 255, 255))