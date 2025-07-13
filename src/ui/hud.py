import pygame
from typing import Optional, TYPE_CHECKING
from game.settings import Settings

if TYPE_CHECKING:
    from game.game_engine import GameEngine

class HUD:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 48)
        
        # Colors
        self.text_color = (255, 255, 255)
        self.health_color = (0, 255, 0)
        self.health_bg_color = (255, 0, 0)
        self.powerup_color = (255, 255, 0)
        
        # Positions
        self.health_bar_pos = (20, 20)
        self.score_pos = (settings.SCREEN_WIDTH - 200, 20)
        self.level_pos = (settings.SCREEN_WIDTH - 200, 60)
        self.powerup_pos = (20, 60)
        
        # Create FPS clock for accurate timing
        self.fps_clock = pygame.time.Clock()
        
        # Add reference to game engine for game time
        self.game_engine_ref: Optional['GameEngine'] = None
    
    def get_current_game_time(self) -> int:
        """Get current game time that respects pause state."""
        if self.game_engine_ref:
            return self.game_engine_ref.get_game_time()
        else:
            return pygame.time.get_ticks()
    
    def render(self, surface: pygame.Surface, player, score: int, level: int, fps: float = 0):
        """Render the HUD."""
        if player:
            self.render_health_bar(surface, player)
            self.render_powerup_status(surface, player)
        
        self.render_score(surface, score)
        self.render_level(surface, level)
        self.render_fps(surface, fps)
    
    def render_health_bar(self, surface: pygame.Surface, player):
        """Render player health bar."""
        bar_width = 200
        bar_height = 20
        x, y = self.health_bar_pos
        
        # Background
        pygame.draw.rect(surface, self.health_bg_color, (x, y, bar_width, bar_height))
        
        # Health
        health_percentage = player.health / player.max_health
        health_width = int(bar_width * health_percentage)
        pygame.draw.rect(surface, self.health_color, (x, y, health_width, bar_height))
        
        # Border
        pygame.draw.rect(surface, self.text_color, (x, y, bar_width, bar_height), 2)
        
        # Health text
        health_text = f"Health: {player.health}/{player.max_health}"
        text_surface = self.small_font.render(health_text, True, self.text_color)
        surface.blit(text_surface, (x, y + bar_height + 5))
    
    def render_powerup_status(self, surface: pygame.Surface, player):
        """Render active powerup status using GAME TIME."""
        x, y = self.powerup_pos
        y_offset = 0
        
        # Use game time instead of real time
        current_time = self.get_current_game_time()
        
        if hasattr(player, 'has_rapid_fire') and player.has_rapid_fire:
            time_left = (player.rapid_fire_end_time - current_time) / 1000
            # Prevent negative time display
            if time_left > 0:
                text = f"Rapid Fire: {time_left:.1f}s"
                text_surface = self.small_font.render(text, True, self.powerup_color)
                surface.blit(text_surface, (x, y + y_offset))
                y_offset += 25
        
        if hasattr(player, 'has_shield') and player.has_shield:
            time_left = (player.shield_end_time - current_time) / 1000
            # Prevent negative time display
            if time_left > 0:
                text = f"Shield: {time_left:.1f}s"
                text_surface = self.small_font.render(text, True, (0, 255, 255))
                surface.blit(text_surface, (x, y + y_offset))
                y_offset += 25
        
        if hasattr(player, 'has_spread_shot') and player.has_spread_shot:
            time_left = (player.spread_shot_end_time - current_time) / 1000
            # Prevent negative time display
            if time_left > 0:
                text = f"Spread Shot: {time_left:.1f}s"
                text_surface = self.small_font.render(text, True, (255, 100, 255))
                surface.blit(text_surface, (x, y + y_offset))
    
    def render_score(self, surface: pygame.Surface, score: int):
        """Render score."""
        text = f"Score: {score:,}"
        text_surface = self.font.render(text, True, self.text_color)
        surface.blit(text_surface, self.score_pos)
    
    def render_level(self, surface: pygame.Surface, level: int):
        """Render level."""
        text = f"Level: {level}"
        text_surface = self.font.render(text, True, self.text_color)
        surface.blit(text_surface, self.level_pos)
    
    def render_fps(self, surface: pygame.Surface, fps: float = 0):
        """Render FPS counter with proper formatting."""
        if fps > 0:
            # Color code FPS: Green = good, Yellow = ok, Red = bad
            if fps >= 50:
                color = (0, 255, 0)      # Green - excellent
            elif fps >= 30:
                color = (255, 255, 0)    # Yellow - acceptable
            else:
                color = (255, 100, 100)  # Red - poor
            
            text = f"FPS: {fps:.1f}"
        else:
            color = (128, 128, 128)      # Gray - no data
            text = "FPS: --"
        
        text_surface = self.small_font.render(text, True, color)
        surface.blit(text_surface, (10, self.settings.SCREEN_HEIGHT - 30))