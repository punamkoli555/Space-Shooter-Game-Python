import pygame
from typing import List

class Explosion:
    def __init__(self, x: int, y: int, explosion_type: str, resource_manager):
        self.x = x
        self.y = y
        self.explosion_type = explosion_type
        self.resource_manager = resource_manager
        
        # Animation
        self.frame = 0
        self.frame_count = 8
        self.frame_duration = 100  # milliseconds
        self.last_frame_time = pygame.time.get_ticks()
        self.finished = False
        
        # Create explosion frames if no sprites available
        self.frames = self.create_explosion_frames()
        
        # Scale based on type
        if explosion_type == 'large':
            self.scale = 2.0
        else:
            self.scale = 1.0
    
    def create_explosion_frames(self) -> List[pygame.Surface]:
        """Create explosion animation frames."""
        frames = []
        base_size = 32 if self.explosion_type == 'small' else 64
        
        for i in range(self.frame_count):
            # Create frame
            size = int(base_size * (1 + i * 0.3))
            frame = pygame.Surface((size, size), pygame.SRCALPHA)
            
            # Color progression: yellow -> orange -> red -> dark red
            progress = i / self.frame_count
            if progress < 0.3:
                color = (255, 255, int(255 * (1 - progress * 2)))
            elif progress < 0.6:
                color = (255, int(255 * (1 - (progress - 0.3) * 2)), 0)
            else:
                color = (int(255 * (1 - (progress - 0.6) * 2)), 0, 0)
            
            # Draw explosion circle with fade
            alpha = int(255 * (1 - progress))
            explosion_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(explosion_surface, (*color, alpha), 
                             (size // 2, size // 2), size // 2)
            
            # Add inner bright core
            if i < self.frame_count // 2:
                core_size = size // 3
                pygame.draw.circle(explosion_surface, (255, 255, 255, alpha), 
                                 (size // 2, size // 2), core_size)
            
            frames.append(explosion_surface)
        
        return frames
    
    def update(self, dt: int):
        """Update explosion animation."""
        current_time = pygame.time.get_ticks()
        
        if current_time - self.last_frame_time > self.frame_duration:
            self.frame += 1
            self.last_frame_time = current_time
            
            if self.frame >= self.frame_count:
                self.finished = True
    
    def render(self, surface: pygame.Surface):
        """Render explosion."""
        if self.finished or self.frame >= len(self.frames):
            return
        
        frame_surface = self.frames[self.frame]
        
        # Scale if needed
        if self.scale != 1.0:
            new_size = (int(frame_surface.get_width() * self.scale),
                       int(frame_surface.get_height() * self.scale))
            frame_surface = pygame.transform.scale(frame_surface, new_size)
        
        # Center the explosion
        x = self.x - frame_surface.get_width() // 2
        y = self.y - frame_surface.get_height() // 2
        
        surface.blit(frame_surface, (x, y))