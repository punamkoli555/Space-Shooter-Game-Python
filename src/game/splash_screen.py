import pygame
import math
import os
from game.settings import Settings
from utils.debug_utils import debug_print

class SplashScreen:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.duration = 3500  # 3.5 seconds total
        self.timer = 0
        self.finished = False
        self.music_started = False  # Track if music has started
        
        # Animation phases
        self.fade_in_time = 800    # 0.8s fade in
        self.hold_time = 2000      # 2.0s hold
        self.fade_out_time = 700   # 0.7s fade out
        
        # Colors and styling
        self.bg_color = (5, 10, 20)  # Deep space blue
        self.primary_color = (100, 200, 255)  # Bright blue
        self.secondary_color = (80, 160, 220)  # Slightly dimmer blue
        self.accent_color = (255, 200, 100)   # Golden accent
        
        self.audio_manager = None
        
        try:
            self.title_font = self.get_best_font(72)  # Larger, smoother title
            self.engine_font = self.get_best_font(42)  # Cleaner engine text
            self.subtitle_font = self.get_best_font(28)  # Better subtitle
            debug_print("-> High-quality fonts loaded for splash screen")
        except Exception as e:
            debug_print(f"-> Font loading failed, using fallbacks: {e}")
            self.title_font = pygame.font.Font(None, 72)
            self.engine_font = pygame.font.Font(None, 42)
            self.subtitle_font = pygame.font.Font(None, 28)
        
        self.particles = []
        self.generate_particles()
        
        debug_print("-> Splash screen initialized with music support")
        
    def get_best_font(self, size: int):
        """Get the best available fonts."""
        font_candidates = [
            "Segoe UI",
            "Arial", 
            "Helvetica",
            "Calibri",
            "Trebuchet MS",
            "Verdana",
            "Consolas",
            "Courier New",
            "Monaco",
            "DejaVu Sans",
            "Liberation Sans"
        ]
        
        # Try system fonts first
        for font_name in font_candidates:
            try:
                font = pygame.font.SysFont(font_name, size)
                test_surface = font.render("Test", True, (255, 255, 255))
                if test_surface.get_width() > 0:
                    return font
            except:
                continue
        
        # Try loading from font files if available
        font_paths = [
            "C:/Windows/Fonts/arial.ttf",          # Windows Arial
            "C:/Windows/Fonts/calibri.ttf",        # Windows Calibri  
            "C:/Windows/Fonts/segoeui.ttf",        # Windows Segoe UI
            "/System/Library/Fonts/Arial.ttf",     # macOS Arial
            "/usr/share/fonts/truetype/arial.ttf", # Linux Arial
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return pygame.font.Font(font_path, size)
                except:
                    continue
        
        return pygame.font.Font(None, int(size * 1.2))
    
    def set_audio_manager(self, audio_manager):
        """Set audio manager reference for music control."""
        self.audio_manager = audio_manager
        debug_print("-> Audio manager connected to splash screen")
        
    def start_music(self):
        """Start splash screen music."""
        if self.audio_manager and not self.music_started:
            debug_print("-> Starting splash screen music...")
            self.audio_manager.play_splash_music()
            self.music_started = True
        elif self.music_started:
            debug_print("-> Splash music already started")
        else:
            debug_print("-> No audio manager available for splash music")

    def stop_music(self, fade_time: float = 1.0):
        """Stop splash screen music with fade out."""
        if self.audio_manager and self.music_started:
            self.audio_manager.stop_splash_music(fade_time)
    
    def generate_particles(self):
        """Generate animated particles for background."""
        import random
        for _ in range(80):
            particle = {
                'x': random.randint(0, self.settings.SCREEN_WIDTH),
                'y': random.randint(0, self.settings.SCREEN_HEIGHT),
                'size': random.randint(1, 3),
                'speed': random.uniform(0.1, 0.5),
                'brightness': random.randint(30, 150),
                'phase': random.uniform(0, 6.28),
                'twinkle_speed': random.uniform(0.5, 2.0)
            }
            self.particles.append(particle)
    
    def update(self, dt: int) -> bool:
        """Update splash screen. Returns True when finished."""
        if self.timer > 100 and not self.music_started:
            self.start_music()
        
        self.timer += dt
        
        for particle in self.particles:
            particle['y'] += particle['speed'] * dt * 0.05
            if particle['y'] > self.settings.SCREEN_HEIGHT:
                particle['y'] = -10
                import random
                particle['x'] = random.randint(0, self.settings.SCREEN_WIDTH)
        
        if self.timer >= self.duration:
            self.stop_music(0.8)
            self.finished = True
            return True
        
        return False
    
    def handle_input(self, event) -> bool:
        """Handle input events. Returns True if should skip splash."""
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE]:
                debug_print("-> Splash screen skipped by user")
                self.stop_music(0.5)
                self.finished = True
                return True
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            debug_print("-> Splash screen skipped by mouse click")
            self.stop_music(0.5)
            self.finished = True
            return True
        
        return False
    
    def get_alpha(self) -> int:
        """Calculate current alpha based on animation phase."""
        if self.timer < self.fade_in_time:
            # Fade in
            progress = self.timer / self.fade_in_time
            return int(255 * self.ease_in_out_cubic(progress))
        
        elif self.timer < self.fade_in_time + self.hold_time:
            # Hold at full opacity
            return 255
        
        else:
            # Fade out
            fade_start = self.fade_in_time + self.hold_time
            fade_progress = (self.timer - fade_start) / self.fade_out_time
            fade_progress = min(1.0, fade_progress)
            return int(255 * (1.0 - self.ease_in_out_cubic(fade_progress)))
    
    def ease_in_out_cubic(self, t: float) -> float:
        """Smooth easing function."""
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 3) / 2
    
    def render(self, surface: pygame.Surface):
        
        surface.fill(self.bg_color)
        
        alpha = self.get_alpha()
        if alpha <= 0:
            return
        
        self.render_particles(surface, alpha)
        
        content_surface = pygame.Surface((self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        
        progress = min(1.0, self.timer / (self.fade_in_time + self.hold_time))
        
        title_text = "BismayaByte"
        
        if progress > 0.3:
            glow_alpha = int(alpha * 0.15)
            
            if glow_alpha > 10:
                for offset in range(1, 3):
                    glow_surface = self.title_font.render(title_text, True, self.primary_color)
                    glow_surface.set_alpha(glow_alpha // offset)
                    
                    for dx, dy in [(-offset, 0), (offset, 0), (0, -offset), (0, offset)]:
                        glow_x = self.settings.SCREEN_WIDTH // 2 - glow_surface.get_width() // 2 + dx
                        glow_y = 250 + dy
                        content_surface.blit(glow_surface, (glow_x, glow_y))
        
        # MAIN TITLE
        title_surface = self.title_font.render(title_text, True, self.primary_color)
        title_x = self.settings.SCREEN_WIDTH // 2 - title_surface.get_width() // 2
        title_y = 250
        content_surface.blit(title_surface, (title_x, title_y))
        
        # ENGINE SUBTITLE
        engine_text = "Game Engine"
        engine_surface = self.engine_font.render(engine_text, True, self.secondary_color)
        engine_x = self.settings.SCREEN_WIDTH // 2 - engine_surface.get_width() // 2
        engine_y = title_y + title_surface.get_height() + 15
        content_surface.blit(engine_surface, (engine_x, engine_y))
        
        if progress > 0.2:
            powered_text = "Powered By"
            powered_surface = self.subtitle_font.render(powered_text, True, self.accent_color)
            powered_x = self.settings.SCREEN_WIDTH // 2 - powered_surface.get_width() // 2
            powered_y = title_y - powered_surface.get_height() - 25
            content_surface.blit(powered_surface, (powered_x, powered_y))
        
        if progress > 0.5:
            version_text = "Version 1.0 • Enhanced Edition"
            version_font = self.get_best_font(20)
            version_surface = version_font.render(version_text, True, (150, 180, 200))
            version_x = self.settings.SCREEN_WIDTH // 2 - version_surface.get_width() // 2
            version_y = engine_y + engine_surface.get_height() + 35
            content_surface.blit(version_surface, (version_x, version_y))
        
        # Skip instruction (fades in after hold period starts) - fresh render
        if self.timer > self.fade_in_time + 500:
            skip_text = "Press any key or click to continue"
            skip_font = self.get_best_font(18)
            skip_surface = skip_font.render(skip_text, True, (120, 140, 160))
            skip_x = self.settings.SCREEN_WIDTH // 2 - skip_surface.get_width() // 2
            skip_y = self.settings.SCREEN_HEIGHT - 80
            
            # Subtle pulse effect
            pulse = math.sin(self.timer * 0.003) * 0.3 + 0.7
            skip_alpha = int(alpha * pulse)
            skip_surface.set_alpha(skip_alpha)
            content_surface.blit(skip_surface, (skip_x, skip_y))
        
      
        content_surface.set_alpha(alpha)
        surface.blit(content_surface, (0, 0))
        
        if progress < 1.0 and alpha > 100:
            self.render_scan_effect(surface, progress, alpha)
    
    def render_particles(self, surface: pygame.Surface, alpha: int):
        """Render animated background particles."""
        for particle in self.particles:
            twinkle = math.sin(self.timer * particle['twinkle_speed'] * 0.001 + particle['phase']) * 0.4 + 0.6
            brightness = int(particle['brightness'] * twinkle * (alpha / 255))
            
            if brightness > 20:
                color = (brightness, brightness, brightness + 20)
                if particle['size'] > 1:
                    pygame.draw.circle(surface, color, 
                                     (int(particle['x']), int(particle['y'])), particle['size'])
                else:
                    if (0 <= particle['x'] < surface.get_width() and 
                        0 <= particle['y'] < surface.get_height()):
                        surface.set_at((int(particle['x']), int(particle['y'])), color)
    
    def render_scan_effect(self, surface: pygame.Surface, progress: float, alpha: int):
        
        scan_speed = 3.0  # Faster scan
        scan_y = int(150 + (progress * scan_speed * 300) % 400)  # Continuous scan
        
        # Much lower alpha for subtlety
        scan_alpha = int(alpha * 0.08 * (1 - progress * 0.5))  # Very subtle, fades as progress increases
        
        if scan_alpha > 5:  # Only render if barely visible
            # Create a very thin, subtle scan line
            scan_color = (self.primary_color[0], self.primary_color[1], self.primary_color[2])
            
            # Single thin line instead of multiple thick lines
            if 0 <= scan_y < surface.get_height():
                # Create a temporary surface for the scan line with proper alpha
                scan_surface = pygame.Surface((surface.get_width(), 2), pygame.SRCALPHA)
                
                # Gradient scan line (thicker in center, thinner at edges)
                center_alpha = scan_alpha
                edge_alpha = scan_alpha // 3
                
                # Draw gradient scan line
                pygame.draw.line(scan_surface, (*scan_color, center_alpha), 
                               (0, 0), (surface.get_width(), 0))
                pygame.draw.line(scan_surface, (*scan_color, edge_alpha), 
                               (0, 1), (surface.get_width(), 1))
                
                # Blit the scan line
                surface.blit(scan_surface, (0, scan_y))