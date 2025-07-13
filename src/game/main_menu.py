import pygame
import math
from typing import List, Optional
from utils.debug_utils import debug_print

class MainMenu:
    """
    Cosmic combat simulator main menu.
    """
    
    def __init__(self, settings):
        self.settings = settings
        
        # Load fonts with fallbacks
        self.title_font = self._load_font(64)
        self.menu_font = self._load_font(36)
        self.subtitle_font = self._load_font(24)
        self.version_font = self._load_font(18)
        
        # Menu options
        self.menu_options = [
            "Start Game",
            "Settings", 
            "Credits",
            "Exit"
        ]
        
        self.selected_index = 0
        self.animation_time = 0.0
        self.selection_alpha = 0.0
        self.title_pulse = 0.0
        
        # Colors
        self.colors = {
            'background': (5, 10, 25),
            'title': (100, 200, 255),
            'selected': (255, 180, 0),
            'normal': (180, 200, 220),
            'accent': (0, 255, 150),
            'glow': (100, 150, 255)
        }
        
        # Background stars
        self.stars = self._create_stars()
        
        debug_print(f"Main menu initialized with options: {self.menu_options}")
    
    def _load_font(self, size: int) -> pygame.font.Font:
        """Load font with fallback."""
        try:
            return pygame.font.Font(None, size)
        except:
            return pygame.font.Font(pygame.font.get_default_font(), size)
    
    def _create_stars(self) -> List[dict]:
        """Create background stars."""
        import random
        stars = []
        for _ in range(100):
            star = {
                'x': random.randint(0, self.settings.SCREEN_WIDTH),
                'y': random.randint(0, self.settings.SCREEN_HEIGHT),
                'brightness': random.uniform(0.3, 1.0),
                'twinkle_speed': random.uniform(0.5, 3.0),
                'size': random.randint(1, 2)
            }
            stars.append(star)
        return stars
    
    def handle_input(self, event) -> Optional[str]:
        """Handle input events and return selected option."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_index = (self.selected_index - 1) % len(self.menu_options)
                debug_print(f"Menu navigation: UP to index {self.selected_index} ({self.menu_options[self.selected_index]})")
                return None
                
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_index = (self.selected_index + 1) % len(self.menu_options)
                debug_print(f"Menu navigation: DOWN to index {self.selected_index} ({self.menu_options[self.selected_index]})")
                return None
                
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                selected_option = self.menu_options[self.selected_index]
                debug_print(f"Menu selection: {selected_option}")
                return selected_option
                
            elif event.key == pygame.K_ESCAPE:
                debug_print("Menu: ESC pressed - Exit")
                return "Exit"
        
        return None
    
    def update(self, dt: int):
        """Update animations."""
        dt_sec = dt * 0.001
        self.animation_time += dt_sec
        
        # Pulsing effects
        self.selection_alpha = 0.7 + 0.3 * math.sin(self.animation_time * 4)
        self.title_pulse = 0.8 + 0.2 * math.sin(self.animation_time * 2)
        
        # Update stars
        for star in self.stars:
            star['brightness'] = abs(math.sin(self.animation_time * star['twinkle_speed']))
    
    def render(self, surface: pygame.Surface):
        """Render the main menu."""
        # Clear background
        surface.fill(self.colors['background'])
        
        self._render_stars(surface)
        
        # Title
        title_text = "SPACE SHOOTER"
        title_surface = self.title_font.render(title_text, True, self.colors['title'])
        title_scale = self.title_pulse
        
        # Scale title for pulse effect
        if title_scale != 1.0:
            title_width = int(title_surface.get_width() * title_scale)
            title_height = int(title_surface.get_height() * title_scale)
            title_surface = pygame.transform.scale(title_surface, (title_width, title_height))
        
        title_x = self.settings.SCREEN_WIDTH // 2 - title_surface.get_width() // 2
        title_y = 100
        surface.blit(title_surface, (title_x, title_y))
        
        # Subtitle
        subtitle_text = "Enhanced Edition"
        subtitle_surface = self.subtitle_font.render(subtitle_text, True, self.colors['accent'])
        subtitle_x = self.settings.SCREEN_WIDTH // 2 - subtitle_surface.get_width() // 2
        subtitle_y = title_y + title_surface.get_height() + 10
        surface.blit(subtitle_surface, (subtitle_x, subtitle_y))
        
        # Menu options
        menu_start_y = 280
        option_spacing = 60
        
        for i, option in enumerate(self.menu_options):
            y = menu_start_y + i * option_spacing
            
            # Selection highlight
            if i == self.selected_index:
                # Glow effect
                glow_width = 300
                glow_height = 50
                glow_surface = pygame.Surface((glow_width, glow_height), pygame.SRCALPHA)
                
                glow_color = (*self.colors['glow'], int(50 * self.selection_alpha))
                pygame.draw.rect(glow_surface, glow_color, (0, 0, glow_width, glow_height), 0, 25)
                
                glow_x = self.settings.SCREEN_WIDTH // 2 - glow_width // 2
                glow_y = y - 10
                surface.blit(glow_surface, (glow_x, glow_y))
                
                # Text color
                text_color = self.colors['selected']
                
                # Selection indicator
                indicator_text = "► "
                indicator_surface = self.menu_font.render(indicator_text, True, text_color)
                indicator_x = self.settings.SCREEN_WIDTH // 2 - 150
                surface.blit(indicator_surface, (indicator_x, y))
                
            else:
                text_color = self.colors['normal']
            
            # Menu option text
            option_surface = self.menu_font.render(option, True, text_color)
            option_x = self.settings.SCREEN_WIDTH // 2 - option_surface.get_width() // 2
            surface.blit(option_surface, (option_x, y))
        
        # Controls help
        controls_text = "↑↓ Navigate • ENTER Select • ESC Exit"
        controls_surface = self.version_font.render(controls_text, True, (100, 120, 140))
        controls_x = self.settings.SCREEN_WIDTH // 2 - controls_surface.get_width() // 2
        controls_y = self.settings.SCREEN_HEIGHT - 50
        surface.blit(controls_surface, (controls_x, controls_y))
        
        # Version info
        version_text = "v1.0 Enhanced"
        version_surface = self.version_font.render(version_text, True, (80, 100, 120))
        version_x = self.settings.SCREEN_WIDTH - version_surface.get_width() - 20
        version_y = self.settings.SCREEN_HEIGHT - 30
        surface.blit(version_surface, (version_x, version_y))
    
    def _render_stars(self, surface: pygame.Surface):
        """Render twinkling background stars."""
        for star in self.stars:
            brightness = int(255 * star['brightness'])
            color = (brightness, brightness, brightness)
            pygame.draw.circle(surface, color, (star['x'], star['y']), star['size'])