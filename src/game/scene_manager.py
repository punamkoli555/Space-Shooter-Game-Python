import pygame
import math
import os
from typing import TYPE_CHECKING
from game.settings import GameState
import random
from game.starfighter_selector import StarfighterSelector
from utils.resource_manager import ResourceManager
from utils.debug_utils import debug_print
from game.settings import Settings

if TYPE_CHECKING:
    from game.game_engine import GameEngine
    

class SceneManager:
    def __init__(self, settings: Settings, resource_manager):
        self.settings = settings
        self.resource_manager = resource_manager
        
        # Initialize fonts
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 48)
        self.text_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Menu state
        self.current_scene = 'menu'
        self.current_menu = 'main'
        self.main_menu_options = ["Start Game", "Settings", "Credits", "Exit"]
        self.main_menu_index = 0
        
        # Animation timer
        self.menu_timer = 0
        
        # Pause menu
        self.pause_menu_options = ["Resume Game", "Return to Ship Menu", "Exit Game"]
        self.pause_menu_index = 0
        
        # Ship selection - Initialize both selector attributes
        self.starfighter_selector = None
        self.ship_selector = None
        self.selected_ship_type = 'ship1'
        
        # Background elements for main menu
        self.menu_planets = []
        self.menu_stars = []
        self.planet_spawn_timer = 0
        
        # COSMIC EFFECTS
        self.cosmic_effects = {
            'nebulae': [],
            'black_holes': [],
            'cosmic_dust': [],
            'energy_fields': []
        }
        
        self.generate_cosmic_phenomena()
        self.initialize_menu_background()
        
        # Notification system
        self.notification = None
        self.notification_timer = 0
        self.notification_duration = 2000  # 2 seconds
        
        # Audio manager reference (will be set by game engine)
        self.audio_manager = None
        
        self.time = 0
        
        # SPLASH SCREEN
        from game.splash_screen import SplashScreen
        self.splash_screen = SplashScreen(settings)
        self.show_splash = True  # Show splash on startup
        
        # Music state tracking
        self.current_scene = 'splash'
        
        # AUDIO: Don't start any music yet - let splash screen control it
        self.audio_manager = None  # Will be set later
        
        debug_print("✓ Scene Manager initialized with splash screen support")
        
    def initialize_menu_background(self):
        """Initialize realistic space background with more stars."""
        # Generate star field
        for _ in range(500):  # More stars for realistic space
            star = {
                'x': random.randint(0, self.settings.SCREEN_WIDTH),
                'y': random.randint(0, self.settings.SCREEN_HEIGHT),
                'brightness': random.randint(20, 255),
                'size': random.choices([1, 2, 3], weights=[70, 25, 5])[0],  # Most stars are small, it's realistic dude don't worry.
                'twinkle_speed': random.uniform(0.2, 1.0),
                'phase': random.uniform(0, 3.14159),
                'color_type': random.choices(['white', 'blue', 'yellow', 'red'], weights=[60, 20, 15, 5])[0]
            }
            self.menu_stars.append(star)
        
        debug_print(f"✓ Initialized {len(self.menu_stars)} realistic stars")
        
    def set_audio_manager(self, audio_manager):
        """Set the audio manager reference."""
        self.audio_manager = audio_manager
        
        if self.splash_screen:
            self.splash_screen.set_audio_manager(audio_manager)
        
        debug_print("-> Audio manager ready, waiting for splash screen to finish")
    
    def load_unicode_font(self, size: int) -> pygame.font.Font:
        """Load a font that supports Unicode characters."""
        # List of fonts commonly available that support Unicode
        font_candidates = [
            # Code default fonts
            "Consolas",
            "Cascadia Code",
            "Cascadia Mono", 
            "Fira Code",
            "JetBrains Mono",
            "Source Code Pro",
            "Monaco",
            "Menlo",
            
            # System fonts with Unicode support
            "DejaVu Sans Mono",
            "Liberation Mono",
            "Courier New",
            "Arial Unicode MS",
            "Segoe UI Symbol",
            "Noto Sans",
            
            # Fallback fonts
            "arial.ttf",
            "calibri.ttf",
            "segoeui.ttf"
        ]
        
        # Try system fonts first
        for font_name in font_candidates:
            try:
                font = pygame.font.SysFont(font_name, size)
                # Test if font supports Unicode arrows
                test_surface = font.render("↑←→↓", True, (255, 255, 255))
                if test_surface.get_width() > 0:  # Font rendered something
                    return font
            except:
                continue
        
        # Try loading from common font file locations
        font_paths = [
            # Windows
            "C:/Windows/Fonts/consola.ttf",
            "C:/Windows/Fonts/arial.ttf", 
            "C:/Windows/Fonts/calibri.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            
            # NOTE: Assets folder (if you want to include a font)
            "assets/fonts/unicode_font.ttf",
            "assets/fonts/consolas.ttf",
            
            # Linux/Unix
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/System/Library/Fonts/Monaco.ttf",  # macOS
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    font = pygame.font.Font(font_path, size)
                    return font
                except:
                    continue
        
        # Fallback to default pygame font
        return pygame.font.Font(None, size)
    
    def get_icon_font(self, size: int):
        """Get the best available icon font."""
        try:
            return pygame.font.Font(None, size)
        except:
            return pygame.font.Font(pygame.font.get_default_font(), size)
    
    def generate_stars(self, count: int) -> list:
        """Generate background stars for menu."""
        stars = []
        for _ in range(count):
            star = {
                'x': random.randint(0, self.settings.SCREEN_WIDTH),
                'y': random.randint(0, self.settings.SCREEN_HEIGHT),
                'brightness': random.randint(50, 255),
                'size': random.randint(1, 3),
                'twinkle': random.randint(0, 1000)
            }
            stars.append(star)
        return stars
    
    def initialize_ship_selector(self):
        """Initialize the starfighter selector when needed."""
        if self.starfighter_selector is None:
            debug_print("-> Initializing Starfighter Selector...")
            self.starfighter_selector = StarfighterSelector(self.settings, self.resource_manager)
            self.ship_selector = self.starfighter_selector
            debug_print("-> Starfighter Selector initialized")
        return self.starfighter_selector
    
    def initialize_menu_planets(self):
        """Initialize planets for menu background."""
        for _ in range(2):
            self.spawn_menu_planet()
    
    def spawn_menu_planet(self):
        """Spawn a planet for menu background."""
        planet_sprites = []
        for i in range(4):
            sprite = self.resource_manager.get_sprite(f'planet_{i}')
            if sprite:
                planet_sprites.append(sprite)
        
        if planet_sprites:
            sprite = random.choice(planet_sprites)
            x = random.randint(-200, self.settings.SCREEN_WIDTH + 200)
            y = random.randint(-200, self.settings.SCREEN_HEIGHT + 200)
            speed = random.uniform(5, 20)  # Slower movement
            scale = random.uniform(0.2, 0.8)  # Smaller planets
            
            from game.game_engine import Planet
            planet = Planet(x, y, sprite, speed, scale)
            self.menu_planets.append(planet)
            
    def generate_cosmic_phenomena(self):
        """Generate REALISTIC space environment with actual planet assets."""
       
        self.cosmic_effects = {
            'distant_stars': [],
            'moving_planets': [],
            'meteors': [],
            'cosmic_dust': [],
            'nebula_dust': [],  # Very subtle nebula particles instead of big circles
            'nebulae': [],      
            'black_holes': [],    
            'energy_fields': [] 
        }
        
        # Generate distant star field (multiple layers for depth)
        for layer in range(3):  # 3 depth layers
            for _ in range(150 + layer * 50):  # More stars in distant layers
                star = {
                    'x': random.randint(0, self.settings.SCREEN_WIDTH),
                    'y': random.randint(0, self.settings.SCREEN_HEIGHT),
                    'brightness': random.randint(20, 255),
                    'size': random.choices([1, 2], weights=[85, 15])[0],  # Mostly small stars
                    'twinkle_speed': random.uniform(0.1, 0.8),
                    'phase': random.uniform(0, 6.28),
                    'color_type': random.choices(['white', 'blue', 'yellow', 'red'], 
                                                weights=[70, 15, 10, 5])[0],
                    'layer': layer,  # Depth layer
                    'parallax_speed': (layer + 1) * 0.02  # Distant stars move slower
                }
                self.cosmic_effects['distant_stars'].append(star)
        
        # Generate moving planets using actual assets
        planet_count = random.randint(2, 4)  # 2-4 planets visible at once
        for i in range(planet_count):
            planet_sprite = self.resource_manager.get_sprite(f'planet_{i % 4}')  # Cycle through 4 planets
            if planet_sprite:
                planet = {
                    'sprite': planet_sprite,
                    'original_width': planet_sprite.get_width(),
                    'original_height': planet_sprite.get_height(),
                    'x': random.randint(-200, self.settings.SCREEN_WIDTH + 200),
                    'y': random.randint(-300, self.settings.SCREEN_HEIGHT + 100),
                    'scale': random.uniform(0.3, 0.8),  # Distant planets are smaller
                    'speed': random.uniform(8, 25),  # Slower, more realistic speed
                    'drift_x': random.uniform(-1, 1),  # Horizontal drift for realism
                    'rotation': random.uniform(0, 360),
                    'rotation_speed': random.uniform(-0.3, 0.3),  # Slower rotation
                    'alpha': random.randint(180, 255),  # Some planets more distant
                    'glow': random.choice([True, False]),  # Some planets have subtle glow
                    'planet_name': f'planet_{i % 4}'
                }
                self.cosmic_effects['moving_planets'].append(planet)
        
        # Generate realistic meteor shower (occasional streaks)
        for _ in range(3):  # Just a few meteors
            meteor = {
                'x': random.randint(-100, self.settings.SCREEN_WIDTH + 100),
                'y': random.randint(-50, self.settings.SCREEN_HEIGHT // 2),
                'size': random.randint(2, 5),
                'speed_x': random.uniform(30, 80),
                'speed_y': random.uniform(50, 120),
                'color': random.choice([(255, 220, 150), (255, 200, 100), (255, 180, 80)]),
                'trail_length': random.randint(8, 15),
                'brightness': random.randint(180, 255)
            }
            self.cosmic_effects['meteors'].append(meteor)
        
        # Generate subtle cosmic dust (replace big nebula circles)
        for _ in range(200):  # Lots of tiny particles
            dust = {
                'x': random.randint(0, self.settings.SCREEN_WIDTH),
                'y': random.randint(0, self.settings.SCREEN_HEIGHT),
                'size': 1,  # Always tiny
                'brightness': random.randint(20, 80),  # Very dim
                'speed': random.uniform(1, 5),  # Slow drift
                'drift': random.uniform(-0.5, 0.5),  # Slight horizontal drift
                'twinkle_speed': random.uniform(0.1, 0.3)  # Subtle twinkle
            }
            self.cosmic_effects['cosmic_dust'].append(dust)
        
        # Generate very subtle nebula dust (tiny colored particles, not big circles)
        nebula_colors = [(80, 40, 120, 30), (40, 80, 120, 30), (120, 80, 40, 30)]
        for _ in range(50):  # Just 50 tiny colored particles
            dust = {
                'x': random.randint(0, self.settings.SCREEN_WIDTH),
                'y': random.randint(0, self.settings.SCREEN_HEIGHT),
                'color': random.choice(nebula_colors),
                'size': 1,  # Always tiny
                'speed': random.uniform(0.5, 2),
                'alpha_variation': random.uniform(0.5, 1.0)
            }
            self.cosmic_effects['nebula_dust'].append(dust)
        
        # OPTIONAL: Add very subtle nebulae (much smaller and dimmer than before)
        for _ in range(2):  # Just 2 very subtle nebulae
            nebula = {
                'x': random.randint(-100, self.settings.SCREEN_WIDTH + 100),
                'y': random.randint(-100, self.settings.SCREEN_HEIGHT + 100),
                'size': random.randint(80, 120),  # Much smaller
                'color': random.choice([(20, 10, 40), (10, 20, 40), (40, 20, 10)]),  # Much dimmer colors
                'alpha': random.randint(15, 30),  # Very low alpha
                'speed': random.uniform(2, 5),
                'rotation': random.uniform(0, 360),
                'rotation_speed': random.uniform(-0.2, 0.2)
            }
            self.cosmic_effects['nebulae'].append(nebula)
        
        debug_print("-> Generated realistic deep space environment with real planets")
            
            
    def update_cosmic_effects(self, dt: int):
        """Update space environment with planet movement."""
        dt_sec = dt * 0.001
        
        # Update distant stars (subtle parallax movement)
        for star in self.cosmic_effects['distant_stars']:
            star['y'] += star['parallax_speed'] * dt
            if star['y'] > self.settings.SCREEN_HEIGHT:
                star['y'] = -5
                star['x'] = random.randint(0, self.settings.SCREEN_WIDTH)
        
        for planet in self.cosmic_effects['moving_planets']:
            planet['y'] += planet['speed'] * dt_sec * 60
            planet['x'] += planet.get('drift_x', 0) * dt_sec * 30  # horizontal drift
            planet['rotation'] += planet['rotation_speed'] * dt_sec * 60  # Smooth rotation
            
            if planet['y'] > self.settings.SCREEN_HEIGHT + 200:
                planet['y'] = random.randint(-400, -200)
                planet['x'] = random.randint(-200, self.settings.SCREEN_WIDTH + 200)
                planet['drift_x'] = random.uniform(-2, 2)
        
        # Update meteors
        for meteor in self.cosmic_effects['meteors']:
            meteor['x'] += meteor['speed_x'] * dt_sec
            meteor['y'] += meteor['speed_y'] * dt_sec
            
            # Reset if off screen
            if (meteor['x'] > self.settings.SCREEN_WIDTH + 100 or 
                meteor['y'] > self.settings.SCREEN_HEIGHT + 100):
                meteor['x'] = random.randint(-100, 0)
                meteor['y'] = random.randint(-50, self.settings.SCREEN_HEIGHT // 2)
        
        # Update cosmic dust
        for dust in self.cosmic_effects['cosmic_dust']:
            dust['y'] += dust['speed'] * dt_sec
            dust['x'] += dust['drift'] * dt_sec
            
            if dust['y'] > self.settings.SCREEN_HEIGHT:
                dust['y'] = 0
                dust['x'] = random.randint(0, self.settings.SCREEN_WIDTH)
        
        # Update nebula dust
        for dust in self.cosmic_effects['nebula_dust']:
            dust['y'] += dust['speed'] * dt_sec
            
            if dust['y'] > self.settings.SCREEN_HEIGHT:
                dust['y'] = 0
                dust['x'] = random.randint(0, self.settings.SCREEN_WIDTH)
        
        # Update subtle nebulae
        for nebula in self.cosmic_effects['nebulae']:
            nebula['y'] += nebula['speed'] * dt_sec
            nebula['rotation'] += nebula['rotation_speed'] * dt_sec
            
            if nebula['y'] > self.settings.SCREEN_HEIGHT + 200:
                nebula['y'] = random.randint(-300, -100)
                nebula['x'] = random.randint(-100, self.settings.SCREEN_WIDTH + 100)
                
    def render_realistic_space_background(self, surface: pygame.Surface):
        """Render deep space background with planets."""
        surface.fill((0, 0, 5))
        
        # Render layered stars with depth
        for star in self.cosmic_effects['distant_stars']:
            # Twinkling effect
            twinkle = math.sin(self.time * star['twinkle_speed'] + star['phase']) * 0.3 + 0.7
            brightness = int(star['brightness'] * twinkle * (0.4 + star['layer'] * 0.2))
            
            # Star colors
            if star['color_type'] == 'blue':
                color = (brightness // 3, brightness // 2, brightness)
            elif star['color_type'] == 'yellow':
                color = (brightness, brightness, brightness // 3)
            elif star['color_type'] == 'red':
                color = (brightness, brightness // 3, brightness // 4)
            else:  # white
                color = (brightness, brightness, brightness)
            
            # Render star
            if star['size'] > 1:
                pygame.draw.circle(surface, color, (int(star['x']), int(star['y'])), star['size'])
            else:
                if 0 <= int(star['x']) < surface.get_width() and 0 <= int(star['y']) < surface.get_height():
                    surface.set_at((int(star['x']), int(star['y'])), color)
        
        for planet in self.cosmic_effects['moving_planets']:
            if planet['sprite']:
                try:
                    # SMOOTH position calculations with sub-pixel precision
                    planet_x = float(planet['x'])
                    planet_y = float(planet['y'])
                    
                    # Scale planet
                    scaled_width = max(1, int(planet['original_width'] * planet['scale']))
                    scaled_height = max(1, int(planet['original_height'] * planet['scale']))
                    scaled_sprite = pygame.transform.scale(planet['sprite'], (scaled_width, scaled_height))
                    
                    # SMOOTH rotation with sub-degree precision
                    rotation_angle = float(planet['rotation']) % 360
                    if abs(rotation_angle) > 0.1:
                        rotated_sprite = pygame.transform.rotate(scaled_sprite, rotation_angle)
                    else:
                        rotated_sprite = scaled_sprite
                    
                    # Apply transparency for distance effect
                    if planet['alpha'] < 255:
                        rotated_sprite = rotated_sprite.copy()
                        rotated_sprite.set_alpha(planet['alpha'])
                    
                    # Add subtle glow for some planets
                    if planet['glow']:
                        glow_size = max(scaled_width, scaled_height) + 20
                        glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
                        glow_color = (40, 60, 100, 20)  # Subtle blue glow
                        pygame.draw.circle(glow_surface, glow_color, 
                                         (glow_size // 2, glow_size // 2), glow_size // 2)
                        
                        glow_rect = glow_surface.get_rect()
                        glow_rect.center = (int(planet_x), int(planet_y))
                        surface.blit(glow_surface, glow_rect)
                    
                    # Render planet with SMOOTH positioning
                    planet_rect = rotated_sprite.get_rect()
                    planet_rect.center = (int(planet_x), int(planet_y))
                    surface.blit(rotated_sprite, planet_rect)
                    
                    # OPTIONAL: Add subtle motion blur for fast-moving planets
                    planet_speed = (planet['speed'] ** 2 + planet.get('drift_x', 0) ** 2) ** 0.5
                    if planet_speed > 15:  # Only for fast planets
                        # Create subtle trail effect
                        trail_alpha = min(30, int(planet_speed - 10))
                        trail_surface = rotated_sprite.copy()
                        trail_surface.set_alpha(trail_alpha)
                        
                        # Render trail slightly behind
                        trail_offset_x = -planet.get('drift_x', 0) * 2
                        trail_offset_y = -planet['speed'] * 0.1
                        trail_rect = trail_surface.get_rect()
                        trail_rect.center = (int(planet_x + trail_offset_x), int(planet_y + trail_offset_y))
                        surface.blit(trail_surface, trail_rect)
                    
                except Exception as e:
                    continue  # Skip problematic planets
        
        # Render meteors with trails
        for meteor in self.cosmic_effects['meteors']:
            # Draw trail
            for i in range(meteor['trail_length']):
                trail_x = meteor['x'] - (meteor['speed_x'] * 0.01 * i * 5)
                trail_y = meteor['y'] - (meteor['speed_y'] * 0.01 * i * 5)
                
                if (0 <= trail_x <= surface.get_width() and 
                    0 <= trail_y <= surface.get_height()):
                    trail_alpha = max(0, 255 - i * 20)
                    trail_color = tuple(max(0, int(c * (1 - i * 0.05))) for c in meteor['color'])
                    
                    if trail_alpha > 20:
                        pygame.draw.circle(surface, trail_color, 
                                         (int(trail_x), int(trail_y)), max(1, meteor['size'] - i // 3))
            
            # Draw meteor head
            if (0 <= meteor['x'] <= surface.get_width() and 
                0 <= meteor['y'] <= surface.get_height()):
                pygame.draw.circle(surface, meteor['color'], 
                                 (int(meteor['x']), int(meteor['y'])), meteor['size'])
        
        # Render subtle cosmic dust
        for dust in self.cosmic_effects['cosmic_dust']:
            if dust['brightness'] > 20:
                twinkle = math.sin(self.time * dust['twinkle_speed']) * 0.3 + 0.7
                brightness = int(dust['brightness'] * twinkle)
                color = (brightness, brightness, brightness)
                
                if 0 <= int(dust['x']) < surface.get_width() and 0 <= int(dust['y']) < surface.get_height():
                    surface.set_at((int(dust['x']), int(dust['y'])), color)
        
        # Render very subtle nebula dust (tiny colored particles)
        for dust in self.cosmic_effects['nebula_dust']:
            alpha_mod = math.sin(self.time * 0.5) * dust['alpha_variation']
            alpha = max(10, int(dust['color'][3] + alpha_mod * 20))
            color = (*dust['color'][:3], alpha)
            
            if 0 <= int(dust['x']) < surface.get_width() and 0 <= int(dust['y']) < surface.get_height():
                # Create tiny colored dot
                dot_surface = pygame.Surface((2, 2), pygame.SRCALPHA)
                pygame.draw.circle(dot_surface, color, (1, 1), 1)
                surface.blit(dot_surface, (int(dust['x']), int(dust['y'])))
                
    def render_spectacular_space_effects(self, surface: pygame.Surface):
        """Render CLEAN space environment with planets only."""
        if not hasattr(self, 'cosmic_effects'):
            return
        
        # Render layered distant stars first
        for star in self.cosmic_effects['distant_stars']:
            twinkle = math.sin(self.menu_timer * star['twinkle_speed'] * 0.001 + star['phase']) * 0.4 + 0.6
            brightness = int(star['brightness'] * twinkle * (0.5 + star['layer'] * 0.25))
            
            # Star colors
            if star['color_type'] == 'blue':
                color = (brightness // 3, brightness // 2, brightness)
            elif star['color_type'] == 'yellow':
                color = (brightness, brightness, brightness // 3)
            elif star['color_type'] == 'red':
                color = (brightness, brightness // 3, brightness // 4)
            else:  # white
                color = (brightness, brightness, brightness)
            
            if star['size'] > 1:
                pygame.draw.circle(surface, color, (int(star['x']), int(star['y'])), star['size'])
            else:
                # Bounds check before setting pixel
                star_x, star_y = int(star['x']), int(star['y'])
                if 0 <= star_x < surface.get_width() and 0 <= star_y < surface.get_height():
                    surface.set_at((star_x, star_y), color)
        
        
        for planet in self.cosmic_effects['moving_planets']:
            if planet['sprite']:
                try:
                    scaled_width = int(planet['original_width'] * planet['scale'])
                    scaled_height = int(planet['original_height'] * planet['scale'])
                    
                    # Ensure minimum size to prevent errors
                    scaled_width = max(1, scaled_width)
                    scaled_height = max(1, scaled_height)
                    
                    scaled_sprite = pygame.transform.scale(planet['sprite'], (scaled_width, scaled_height))
                    
                    # Apply rotation if needed
                    if abs(planet['rotation']) > 0.1:  # Only rotate if significant rotation
                        rotated_sprite = pygame.transform.rotate(scaled_sprite, planet['rotation'])
                    else:
                        rotated_sprite = scaled_sprite
                    
                    # Apply transparency
                    if planet['alpha'] < 255:
                        rotated_sprite.set_alpha(planet['alpha'])
                    
                    # Render the planet
                    planet_rect = rotated_sprite.get_rect()
                    planet_rect.centerx = int(planet['x'])
                    planet_rect.centery = int(planet['y'])
                    
                    # Only render if on screen or close to it
                    screen_buffer = 200
                    if (planet_rect.right >= -screen_buffer and 
                        planet_rect.left <= surface.get_width() + screen_buffer and
                        planet_rect.bottom >= -screen_buffer and 
                        planet_rect.top <= surface.get_height() + screen_buffer):
                        surface.blit(rotated_sprite, planet_rect)
                            
                except Exception as e:
                    debug_print(f"-> Error rendering planet {planet.get('planet_name', 'unknown')}: {e}")
        
        # Render enhanced meteor shower
        for meteor in self.cosmic_effects['meteors']:
            trail_spacing = 6
            
            for i in range(meteor['trail_length']):
                trail_x = meteor['x'] - (meteor['speed_x'] * 0.008 * i * trail_spacing)
                trail_y = meteor['y'] - (meteor['speed_y'] * 0.008 * i * trail_spacing)
                
                if (0 <= trail_x <= surface.get_width() and 
                    0 <= trail_y <= surface.get_height()):
                    trail_alpha = max(0, 255 - i * 8)
                    trail_size = max(1, meteor['size'] - i // 3)
                    trail_color = tuple(max(0, int(c * (1 - i * 0.03))) for c in meteor['color'])
                    
                    if trail_alpha > 10:
                        pygame.draw.circle(surface, trail_color, 
                                        (int(trail_x), int(trail_y)), trail_size)
            
            
            if (0 <= meteor['x'] <= surface.get_width() and 
                0 <= meteor['y'] <= surface.get_height()):
                # Outer glow
                glow_size = meteor['size'] + 2
                glow_color = tuple(min(255, int(c * 0.7)) for c in meteor['color'])
                pygame.draw.circle(surface, glow_color, 
                                (int(meteor['x']), int(meteor['y'])), glow_size)
                
                # Main meteor
                pygame.draw.circle(surface, meteor['color'], 
                                (int(meteor['x']), int(meteor['y'])), meteor['size'])
                
                # Bright core
                core_size = max(1, meteor['size'] - 2)
                core_color = (255, 255, 255)
                pygame.draw.circle(surface, core_color, 
                                (int(meteor['x']), int(meteor['y'])), core_size)
        
        # Render minimal cosmic dust
        for dust in self.cosmic_effects['cosmic_dust']:
            if dust['brightness'] > 30:
                dust_x, dust_y = int(dust['x']), int(dust['y'])
                if (0 <= dust_x < surface.get_width() and 
                    0 <= dust_y < surface.get_height()):
                    layer_alpha = 0.6 + dust['layer'] * 0.2
                    brightness = int(dust['brightness'] * layer_alpha)
                    color = (brightness, brightness, brightness + 10)
                    pygame.draw.circle(surface, color, (dust_x, dust_y), 1)
                
    def render_realistic_space_effects(self, surface: pygame.Surface):
        """Render realistic space environment."""
        if not hasattr(self, 'cosmic_effects'):
            return
        
        # Render moving planets (distant background objects)
        for planet in self.cosmic_effects['moving_planets']:
            # Create planet surface with subtle shading
            planet_surface = pygame.Surface((planet['size'] * 2, planet['size'] * 2), pygame.SRCALPHA)
            
            # Main planet body
            pygame.draw.circle(planet_surface, planet['color'], 
                            (planet['size'], planet['size']), planet['size'])
            
            # Add subtle shading for 3D effect
            shade_color = tuple(max(0, c - 30) for c in planet['color'])
            pygame.draw.circle(planet_surface, shade_color, 
                            (planet['size'] + 5, planet['size'] + 5), planet['size'] - 10)
            
            # Highlight for spherical appearance
            highlight_color = tuple(min(255, c + 40) for c in planet['color'])
            pygame.draw.circle(planet_surface, highlight_color, 
                            (planet['size'] - 8, planet['size'] - 8), planet['size'] // 4)
            
            # Rotate and render
            if planet['rotation'] != 0:
                rotated_planet = pygame.transform.rotate(planet_surface, planet['rotation'])
                planet_rect = rotated_planet.get_rect(center=(planet['x'], planet['y']))
                surface.blit(rotated_planet, planet_rect)
            else:
                planet_rect = planet_surface.get_rect(center=(planet['x'], planet['y']))
                surface.blit(planet_surface, planet_rect)
        
        # Render meteor shower
        for meteor in self.cosmic_effects['meteors']:
            # Calculate trail effect using a fixed trail spacing
            trail_spacing = 8  # Fixed spacing for trail effect
            
            # Draw meteor trail
            for i in range(meteor['trail_length']):
                trail_x = meteor['x'] - (meteor['speed_x'] * 0.01 * i * trail_spacing)
                trail_y = meteor['y'] - (meteor['speed_y'] * 0.01 * i * trail_spacing)
                
                if 0 <= trail_x <= self.settings.SCREEN_WIDTH and 0 <= trail_y <= self.settings.SCREEN_HEIGHT:
                    trail_alpha = int(meteor['brightness'] * (1 - i / meteor['trail_length']))
                    trail_color = (255, 200 + trail_alpha // 5, 100)
                    
                    if trail_alpha > 20:  # Only draw visible trail parts
                        # Create trail particle with alpha
                        trail_size = max(1, meteor['size'] - i // 5)
                        if trail_size > 0:
                            pygame.draw.circle(surface, trail_color, 
                                            (int(trail_x), int(trail_y)), trail_size)
            
            # Draw meteor head
            meteor_color = (255, 220, 150)
            if 0 <= meteor['x'] <= self.settings.SCREEN_WIDTH and 0 <= meteor['y'] <= self.settings.SCREEN_HEIGHT:
                pygame.draw.circle(surface, meteor_color, 
                                (int(meteor['x']), int(meteor['y'])), meteor['size'])
                
                # Bright core
                core_color = (255, 255, 200)
                core_size = max(1, meteor['size'] - 2)
                pygame.draw.circle(surface, core_color, 
                                (int(meteor['x']), int(meteor['y'])), core_size)
        
        # Render subtle cosmic dust
        for dust in self.cosmic_effects['cosmic_dust']:
            if dust['brightness'] > 30:
                color = (dust['brightness'], dust['brightness'], dust['brightness'] + 10)
                pygame.draw.circle(surface, color, (int(dust['x']), int(dust['y'])), 1)
    
    def update_menu_planets(self, dt: int):
        """Update menu background planets."""
        # Update existing planets
        for planet in self.menu_planets[:]:
            planet.update(dt)
            if planet.is_off_screen(self.settings.SCREEN_HEIGHT):
                self.menu_planets.remove(planet)
        
        # Spawn new planets occasionally
        self.planet_spawn_timer += dt
        if self.planet_spawn_timer >= 5000:  # Every 5 seconds
            if len(self.menu_planets) < 3:  # Max 3 planets
                self.spawn_menu_planet()
            self.planet_spawn_timer = 0
            
    def render_cosmic_effects(self, surface: pygame.Surface):
        """Render cosmic background effects."""
        if not hasattr(self, 'cosmic_effects'):
            return
        
        # Render nebulae
        for nebula in self.cosmic_effects['nebulae']:
            nebula_surface = pygame.Surface((nebula['size'] * 2, nebula['size'] * 2), pygame.SRCALPHA)
            
            # Create gradient nebula effect
            for radius in range(nebula['size'], 0, -10):
                alpha = int(nebula['alpha'] * (radius / nebula['size']))
                color = (*nebula['color'], alpha)
                pygame.draw.circle(nebula_surface, color, 
                                (nebula['size'], nebula['size']), radius)
            
            # Rotate nebula
            rotated_nebula = pygame.transform.rotate(nebula_surface, nebula['rotation'])
            nebula_rect = rotated_nebula.get_rect(center=(nebula['x'], nebula['y']))
            surface.blit(rotated_nebula, nebula_rect, special_flags=pygame.BLEND_ADD)
        
        # Render black holes
        for black_hole in self.cosmic_effects['black_holes']:
            black_hole_surface = pygame.Surface((black_hole['size'] * 2, black_hole['size'] * 2), pygame.SRCALPHA)
            
            # Create black hole with event horizon
            center = black_hole['size']
            
            # Outer accretion disk (glowing)
            for ring in range(5):
                ring_radius = black_hole['size'] - ring * 10
                ring_alpha = int(80 - ring * 15)
                ring_color = (255, 100, 0, ring_alpha)  # Orange glow
                
                if ring_radius > 0:
                    pygame.draw.circle(black_hole_surface, ring_color, 
                                    (center, center), ring_radius, 3)
            
            # Dark center
            pygame.draw.circle(black_hole_surface, (0, 0, 0, 200), 
                            (center, center), black_hole['size'] // 3)
            
            # Rotate for dynamic effect
            rotated_hole = pygame.transform.rotate(black_hole_surface, black_hole['rotation'])
            hole_rect = rotated_hole.get_rect(center=(black_hole['x'], black_hole['y']))
            surface.blit(rotated_hole, hole_rect)
        
        # Render cosmic dust
        for dust in self.cosmic_effects['cosmic_dust']:
            color = (dust['brightness'], dust['brightness'], dust['brightness'])
            pygame.draw.circle(surface, color, (int(dust['x']), int(dust['y'])), dust['size'])
    
    def render_stars(self, surface: pygame.Surface):
        """Render realistic twinkling stars with different colors."""
        for star in self.menu_stars:
            # Twinkling effect
            twinkle = math.sin(self.menu_timer * star['twinkle_speed'] * 0.001 + star['phase']) * 0.3 + 0.7
            brightness = int(star['brightness'] * twinkle)
            
            # Star colors based on type
            if star['color_type'] == 'blue':
                color = (brightness // 2, brightness // 2, brightness)
            elif star['color_type'] == 'yellow':
                color = (brightness, brightness, brightness // 2)
            elif star['color_type'] == 'red':
                color = (brightness, brightness // 2, brightness // 2)
            else:  # white
                color = (brightness, brightness, brightness)
            
            if star['size'] > 1:
                pygame.draw.circle(surface, color, (int(star['x']), int(star['y'])), star['size'])
            else:
                surface.set_at((int(star['x']), int(star['y'])), color)
    
    def render_menu_planets(self, surface: pygame.Surface):
        """Render menu planets."""
        for planet in self.menu_planets:
            planet.render(surface)
    
    def handle_menu_input(self, event):
        """Handle menu input."""
        # NOTE: Handle splash screen input first
        if self.show_splash and self.splash_screen:
            if self.splash_screen.handle_input(event):
                # User skipped splash, go to menu
                self.show_splash = False
                self.current_scene = 'menu'
                # Start menu music after a short delay to let splash music fade
                if self.audio_manager:
                    # Use timer to delay menu music start
                    pygame.time.set_timer(pygame.USEREVENT + 5, 800)  # 800ms delay
                debug_print("-> Splash screen skipped, going to menu")
            return None  # Don't handle other input during splash
        
        # Handle splash music events
        if self.audio_manager:
            self.audio_manager.handle_crossfade_event(event)
            self.audio_manager.handle_menu_return_event(event)
            self.audio_manager.handle_splash_music_event(event)
            
            # Handle delayed menu music start
            if event.type == pygame.USEREVENT + 5:
                self.audio_manager.play_menu_music()
                pygame.time.set_timer(pygame.USEREVENT + 5, 0)  # Cancel timer
        
        if event.type == pygame.KEYDOWN:
            debug_print(f"Key pressed: {pygame.key.name(event.key)}")
            
            if event.key == pygame.K_ESCAPE:
                if self.current_menu == 'ship_select':
                    debug_print("Returning to main menu from ship select")
                    # Play back sound
                    if self.audio_manager:
                        self.audio_manager.play_menu_sound('back')
                    self.current_menu = 'main'
                    return 'main_menu'
                elif self.current_menu == 'main':
                    debug_print("Exit requested from main menu")
                    return 'exit_game'

        # Handle main menu directly
        if self.current_menu == 'main':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.main_menu_index = (self.main_menu_index - 1) % len(self.main_menu_options)
                    debug_print(f"Main menu navigation: UP to index {self.main_menu_index} ({self.main_menu_options[self.main_menu_index]})")
                    # Play navigation sound
                    if self.audio_manager:
                        self.audio_manager.play_menu_sound('navigate')
                    return None
                    
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.main_menu_index = (self.main_menu_index + 1) % len(self.main_menu_options)
                    debug_print(f"Main menu navigation: DOWN to index {self.main_menu_index} ({self.main_menu_options[self.main_menu_index]})")
                    # Play navigation sound
                    if self.audio_manager:
                        self.audio_manager.play_menu_sound('navigate')
                    return None
                    
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    selected_option = self.main_menu_options[self.main_menu_index]
                    debug_print(f"Main menu selection: {selected_option}")
                    
                    # Play selection sound
                    if self.audio_manager:
                        self.audio_manager.play_menu_sound('select')
                    
                    if selected_option == "Start Game":
                        debug_print("Switching to starfighter selection")
                        # Initialize starfighter selector before switching
                        if self.starfighter_selector is None:
                            debug_print("-> Initializing starfighter selector...")
                            self.initialize_ship_selector()
                        
                        self.current_menu = 'ship_select'
                        return 'ship_select'
                    elif selected_option == "Settings":
                        debug_print("Settings menu requested - showing coming soon notification")
                        self.show_notification("-> Settings Menu - Coming Soon!", (255, 200, 100))
                        return None
                    elif selected_option == "Credits":
                        debug_print("Credits menu requested - showing coming soon notification") 
                        self.show_notification("-> Credits & About - Coming Soon!", (100, 200, 255))
                        return None
                    elif selected_option == "Exit":
                        debug_print("Exit game requested - returning exit_game")
                        return 'exit_game'

        elif self.current_menu == 'ship_select':
            # Ensure starfighter_selector is always available
            if self.starfighter_selector is None:
                debug_print("-> Starfighter selector missing! Initializing now...")
                self.initialize_ship_selector()
            
            if self.starfighter_selector:
                result = self.starfighter_selector.handle_input(event)
                if result == 'ship_selected':
                    selected_ship = self.starfighter_selector.get_selected_ship()
                    if selected_ship:
                        debug_print(f"Selected ship: {selected_ship['name']} ({selected_ship['class']})")
                        
                        # Play confirmation sound
                        if self.audio_manager:
                            self.audio_manager.play_menu_sound('confirm')
                            
                            # Give a moment for confirmation sound to play
                            # then start music transition
                            debug_print("-> Starting crossfade to game music")
                            # Use a slight delay to let confirmation sound play
                            pygame.time.wait(100)  # 100ms delay
                            self.audio_manager.crossfade_to_game_music(1.5)  # Shorter, more reliable crossfade
                        
                        # Set ship type for game
                        self.selected_ship_type = selected_ship.get('sprite_key', 'ship1')
                        ship_name = selected_ship.get('name', 'Unknown Fighter')
                        
                        debug_print(f"Starting game with {ship_name}")
                        self.current_scene = 'game'  # Update scene state
                        return 'start_game'
                    
                elif result == 'back_to_menu':
                    debug_print("Returning to main menu from ship selector")
                    # Play back sound
                    if self.audio_manager:
                        self.audio_manager.play_menu_sound('back')
                    self.current_menu = 'main'
                    return 'main_menu'
                
                elif result == 'ship_changed':
                    # Play navigation sound
                    if self.audio_manager:
                        self.audio_manager.play_menu_sound('move')
            else:
                debug_print("-> CRITICAL: Cannot initialize starfighter selector!")
                self.current_menu = 'main'
                self.show_notification("-> Ship selection unavailable", (255, 100, 100))
                return 'main_menu'
        
        return None
    
    def return_to_menu_from_game(self):
        """Handle returning to menu from game with music transition."""
        debug_print("-> Returning to menu - switching music")
        self.current_scene = 'menu'
        
        if self.audio_manager:
            self.audio_manager.return_to_menu_music(1.2)
    
    def show_notification(self, message: str, color: tuple = (255, 255, 255)):
        """Show a temporary notification message."""
        self.notification = {
            'message': message,
            'color': color,
            'alpha': 255
        }
        self.notification_timer = 0
        debug_print(f"-> Notification: {message}")
    
    
    def handle_pause_input(self, event):
        """Pause menu handling using index-based logic."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.pause_menu_index = (self.pause_menu_index - 1) % len(self.pause_menu_options)
                debug_print(f"Navigation: Index {self.pause_menu_index} - {self.pause_menu_options[self.pause_menu_index]}")
                return 'menu_changed'
            
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.pause_menu_index = (self.pause_menu_index + 1) % len(self.pause_menu_options)
                debug_print(f"Navigation: Index {self.pause_menu_index} - {self.pause_menu_options[self.pause_menu_index]}")
                return 'menu_changed'
            
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                debug_print(f"SELECTION: Index {self.pause_menu_index} selected")
                
                if self.pause_menu_index == 0:
                    debug_print("✓ Action: Resume Game")
                    return 'resume'
                elif self.pause_menu_index == 1:
                    debug_print("✓ Action: Return to Main Menu")
                    return 'main_menu'
                elif self.pause_menu_index == 2:
                    debug_print("✓ Action: Exit Game")
                    return 'exit_game'
                
                # Should never reach here
                debug_print(f"-> Invalid index: {self.pause_menu_index}")
                return None
            
            elif event.key == pygame.K_ESCAPE:
                debug_print("✓ Quick resume via ESC")
                return 'resume'
        
        return None
    
    def update(self, dt: int):
        """Update scene manager and music fading."""
        if self.show_splash and self.splash_screen:
            if self.splash_screen.update(dt):
                self.show_splash = False
                self.current_scene = 'menu'
                if self.audio_manager:
                    pygame.time.set_timer(pygame.USEREVENT + 5, 1000)
                debug_print("-> Splash screen finished, transitioning to menu")
            return  # Don't update other things during splash
        
        if self.audio_manager:
            self.audio_manager.update_music_fade(dt)
        
        self.time += dt * 0.001
        
        if self.current_menu == 'main' or self.current_menu == 'ship_select':
            self.update_menu_planets(dt)
            self.update_cosmic_effects(dt)
            
            for star in self.menu_stars:
                star['brightness'] = 0.3 + 0.7 * abs(math.sin(self.time * star['twinkle_speed'] + star['phase']))
        
        # Update notification
        if self.notification:
            self.notification_timer += dt
            if self.notification_timer >= self.notification_duration:
                self.notification = None
                self.notification_timer = 0
            
    def render_notification(self, surface: pygame.Surface):
        """Render notification popup if active."""
        if not self.notification:
            return
        
        message = self.notification['message']
        color = self.notification['color']
        alpha = self.notification['alpha']
        
        # Create notification surface
        notification_font = self.text_font
        text_surface = notification_font.render(message, True, color)
        
        # Notification panel dimensions
        panel_width = text_surface.get_width() + 60
        panel_height = text_surface.get_height() + 30
        panel_x = self.settings.SCREEN_WIDTH // 2 - panel_width // 2
        panel_y = 150  # Position near top
        
        # Create notification panel with rounded corners effect
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        
        # Background with transparency
        bg_color = (*color[:3], int(alpha * 0.15))
        panel_surface.fill(bg_color)
        
        # Border glow effect
        border_color = (*color, int(alpha * 0.8))
        pygame.draw.rect(panel_surface, border_color, (0, 0, panel_width, panel_height), 3, 10)
        
        # Inner glow
        inner_glow_color = (*color, int(alpha * 0.3))
        pygame.draw.rect(panel_surface, inner_glow_color, (2, 2, panel_width - 4, panel_height - 4), 1, 8)
        
        # Apply alpha to panel
        panel_surface.set_alpha(alpha)
        surface.blit(panel_surface, (panel_x, panel_y))
        
        # Render notification text with alpha
        text_surface.set_alpha(alpha)
        text_x = panel_x + (panel_width - text_surface.get_width()) // 2
        text_y = panel_y + (panel_height - text_surface.get_height()) // 2
        surface.blit(text_surface, (text_x, text_y))
        
        # Add subtle animation pulse
        pulse = math.sin(self.notification_timer * 0.01) * 0.2 + 0.8
        if pulse != 1.0:
            # Create pulsing outer glow
            glow_size = int(10 * pulse)
            glow_surface = pygame.Surface((panel_width + glow_size * 2, panel_height + glow_size * 2), pygame.SRCALPHA)
            glow_color = (*color, int(alpha * 0.1 * pulse))
            pygame.draw.rect(glow_surface, glow_color, 
                            (glow_size, glow_size, panel_width, panel_height), 0, 15)
            surface.blit(glow_surface, (panel_x - glow_size, panel_y - glow_size))
    
    def render_menu(self, surface: pygame.Surface):
        """Render appropriate menu based on current state."""
        # Render splash if active
        if self.show_splash and self.splash_screen:
            self.splash_screen.render(surface)
            return
        
        # Regular menu rendering
        if self.current_menu == 'main':
            self.render_main_menu(surface)
        elif self.current_menu == 'ship_select':
            self.render_ship_selection(surface)
            
    def render_minimalist_cosmic_effects(self, surface: pygame.Surface):
        """Render subtle, minimalist cosmic effects."""
        if not hasattr(self, 'cosmic_effects'):
            return
        
        # Very subtle nebulae - almost invisible
        for nebula in self.cosmic_effects['nebulae']:
            if len(self.cosmic_effects['nebulae']) > 2:  # Remove some nebulae
                continue
                
            nebula_surface = pygame.Surface((nebula['size'], nebula['size']), pygame.SRCALPHA)
            
            # Much more subtle nebula effect
            for radius in range(nebula['size'] // 2, 0, -15):
                alpha = int(15 * (radius / (nebula['size'] // 2)))  # Very low alpha
                # Subtle blue/purple tones only
                color = (20, 30, 60, alpha)
                pygame.draw.circle(nebula_surface, color, 
                                (nebula['size'] // 2, nebula['size'] // 2), radius)
            
            surface.blit(nebula_surface, (nebula['x'] - nebula['size'] // 2, 
                                        nebula['y'] - nebula['size'] // 2), 
                        special_flags=pygame.BLEND_ADD)
        
        
        # Keep minimal cosmic dust but much more subtle
        dust_count = 0
        for dust in self.cosmic_effects['cosmic_dust']:
            dust_count += 1
            if dust_count > 50:  # Limit dust particles
                break
                
            brightness = min(dust['brightness'] * 0.3, 80)  # Much dimmer
            color = (brightness, brightness, brightness + 10)  # Slight blue tint
            
            # Only render larger dust particles
            if dust['size'] > 1:
                pygame.draw.circle(surface, color, (int(dust['x']), int(dust['y'])), 1)
    
    def render_main_menu(self, surface: pygame.Surface):
        """Render professional deep space main menu with realistic space background."""
        # Render the space background
        self.render_realistic_space_background(surface)
        
        title_text = "SPACE SHOOTER"
        title_surface = self.title_font.render(title_text, True, (255, 255, 255))
        
        for offset in range(1, 3):
            glow_alpha = 30 - offset * 10
            glow_surface = self.title_font.render(title_text, True, (200, 220, 255))
            glow_surface.set_alpha(glow_alpha)
            glow_x = self.settings.SCREEN_WIDTH // 2 - title_surface.get_width() // 2
            glow_y = 120
            for dx in [-offset, offset]:
                for dy in [-offset, offset]:
                    surface.blit(glow_surface, (glow_x + dx, glow_y + dy))
        
        title_x = self.settings.SCREEN_WIDTH // 2 - title_surface.get_width() // 2
        title_y = 120
        surface.blit(title_surface, (title_x, title_y))
        
        subtitle_text = "Cosmic Combat Simulator"
        subtitle_surface = self.menu_font.render(subtitle_text, True, (180, 200, 220))
        subtitle_x = self.settings.SCREEN_WIDTH // 2 - subtitle_surface.get_width() // 2
        subtitle_y = title_y + title_surface.get_height() + 20
        surface.blit(subtitle_surface, (subtitle_x, subtitle_y))
        
        # version info
        version_text = "Enhanced Edition v1.0"
        version_surface = self.small_font.render(version_text, True, (120, 140, 160))
        version_x = self.settings.SCREEN_WIDTH // 2 - version_surface.get_width() // 2
        version_y = subtitle_y + subtitle_surface.get_height() + 15
        surface.blit(version_surface, (version_x, version_y))
        
        if self.selected_ship_type != 'ship1':
            ship_text = f"Active: {self.selected_ship_type.upper()}"
            ship_surface = self.text_font.render(ship_text, True, (100, 200, 100))
            ship_x = self.settings.SCREEN_WIDTH // 2 - ship_surface.get_width() // 2
            ship_y = version_y + 40
            surface.blit(ship_surface, (ship_x, ship_y))
        
        menu_start_y = 350
        menu_spacing = 55
        
        for i, option in enumerate(self.main_menu_options):
            option_y = menu_start_y + i * menu_spacing
            
            if i == self.main_menu_index:
                indicator = ">"
                indicator_surface = self.text_font.render(indicator, True, (255, 255, 255))
                indicator_x = self.settings.SCREEN_WIDTH // 2 - 150
                surface.blit(indicator_surface, (indicator_x, option_y))
                
                # Clean selection line
                line_width = 200
                line_x = self.settings.SCREEN_WIDTH // 2 - line_width // 2
                pygame.draw.line(surface, (80, 120, 160), 
                            (line_x, option_y + 35), 
                            (line_x + line_width, option_y + 35), 2)
                
                text_color = (255, 255, 255)
            else:
                text_color = (180, 200, 220)
            
            # Clean menu text
            option_surface = self.text_font.render(option, True, text_color)
            option_x = self.settings.SCREEN_WIDTH // 2 - option_surface.get_width() // 2
            surface.blit(option_surface, (option_x, option_y))
        
        # feature list
        features = [
            "18 Unique Star-fighters",
            "Advanced Combat Systems", 
            "Dynamic Space Environments"
        ]
        
        feature_start_y = 600
        for i, feature in enumerate(features):
            feature_surface = self.small_font.render(f"• {feature}", True, (120, 150, 180))
            feature_x = self.settings.SCREEN_WIDTH // 2 - feature_surface.get_width() // 2
            feature_y = feature_start_y + i * 25
            surface.blit(feature_surface, (feature_x, feature_y))
        
        nav_text = "[UP/DOWN] Navigate  •  ENTER Select  •  ESC Exit"
        nav_surface = self.small_font.render(nav_text, True, (100, 120, 140))
        nav_x = self.settings.SCREEN_WIDTH // 2 - nav_surface.get_width() // 2
        nav_y = self.settings.SCREEN_HEIGHT - 80
        surface.blit(nav_surface, (nav_x, nav_y))
        
        copyright_text = "© 2025 Bismaya Jyoti Dalei - All Rights Reserved"
        copyright_surface = self.small_font.render(copyright_text, True, (80, 100, 120))
        copyright_x = self.settings.SCREEN_WIDTH // 2 - copyright_surface.get_width() // 2
        copyright_y = self.settings.SCREEN_HEIGHT - 40
        surface.blit(copyright_surface, (copyright_x, copyright_y))
        
        self.render_notification(surface)
        
    def render_enhanced_cosmic_effects(self, surface: pygame.Surface):
        """Render cosmic effects."""
        if not hasattr(self, 'cosmic_effects'):
            return
        
        for nebula in self.cosmic_effects['nebulae']:
            nebula_surface = pygame.Surface((nebula['size'] * 2, nebula['size'] * 2), pygame.SRCALPHA)
            
            # Create MORE VIBRANT gradient nebula effect
            for radius in range(nebula['size'], 0, -8):
                alpha = int(nebula['alpha'] * 1.5 * (radius / nebula['size']))  # Increased alpha
                color = (*nebula['color'], min(alpha, 150))  # Brighter colors
                pygame.draw.circle(nebula_surface, color, 
                                (nebula['size'], nebula['size']), radius)
            
            # Rotate nebula
            rotated_nebula = pygame.transform.rotate(nebula_surface, nebula['rotation'])
            nebula_rect = rotated_nebula.get_rect(center=(nebula['x'], nebula['y']))
            surface.blit(rotated_nebula, nebula_rect, special_flags=pygame.BLEND_ADD)
        
        # Black holes
        for black_hole in self.cosmic_effects['black_holes']:
            black_hole_surface = pygame.Surface((black_hole['size'] * 3, black_hole['size'] * 3), pygame.SRCALPHA)
            
            center = black_hole['size'] * 1.5
            
            for ring in range(8):  # More rings
                ring_radius = black_hole['size'] + ring * 8
                ring_alpha = int(120 - ring * 12)  # Brighter rings
                ring_color = (255, 150 + ring * 10, 0, ring_alpha)  # orange
                
                if ring_radius > 0 and ring_alpha > 0:
                    pygame.draw.circle(black_hole_surface, ring_color, 
                                    (int(center), int(center)), ring_radius, 4)
            
            pygame.draw.circle(black_hole_surface, (0, 0, 0, 255), 
                            (int(center), int(center)), black_hole['size'] // 2)
            
            rotated_hole = pygame.transform.rotate(black_hole_surface, black_hole['rotation'])
            hole_rect = rotated_hole.get_rect(center=(black_hole['x'], black_hole['y']))
            surface.blit(rotated_hole, hole_rect)
        
        for dust in self.cosmic_effects['cosmic_dust']:
            brightness = min(dust['brightness'] * 1.8, 255)  # Brighter dust
            color = (brightness, brightness, brightness)
            
            if dust['size'] > 1:
                pygame.draw.circle(surface, color, (int(dust['x']), int(dust['y'])), dust['size'])
            else:
                surface.set_at((int(dust['x']), int(dust['y'])), color)
            
            
    
    def render_ship_selection(self, surface: pygame.Surface):
        """Render new starfighter selection screen."""
        if self.starfighter_selector:
            self.starfighter_selector.render(surface)
        else:
            surface.fill((20, 30, 50))
            error_text = "Starfighter selection unavailable. Press ESC to return."
            if hasattr(self, 'text_font') and self.text_font:
                error_surface = self.text_font.render(error_text, True, (255, 100, 100))
                error_x = self.settings.SCREEN_WIDTH // 2 - error_surface.get_width() // 2
                error_y = self.settings.SCREEN_HEIGHT // 2
                surface.blit(error_surface, (error_x, error_y))
    
    def render_pause_overlay(self, surface: pygame.Surface):
        
        overlay = pygame.Surface((self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 30))
        surface.blit(overlay, (0, 0))
        
        panel_width = 600
        panel_height = 450
        panel_x = self.settings.SCREEN_WIDTH // 2 - panel_width // 2
        panel_y = self.settings.SCREEN_HEIGHT // 2 - panel_height // 2
        
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((20, 30, 50, 220))
        
        pygame.draw.rect(panel_surface, (100, 150, 200), (0, 0, panel_width, panel_height), 3)
        
        surface.blit(panel_surface, (panel_x, panel_y))
        
        pause_text = "GAME PAUSED"
        title_surface = self.menu_font.render(pause_text, True, (255, 255, 255))
        title_x = panel_x + (panel_width - title_surface.get_width()) // 2
        title_y = panel_y + 40
        surface.blit(title_surface, (title_x, title_y))
        
        line_y = panel_y + 100
        line_start_x = panel_x + 60
        line_end_x = panel_x + panel_width - 60
        pygame.draw.line(surface, (150, 180, 255), (line_start_x, line_y), (line_end_x, line_y), 2)
        
        option_start_y = panel_y + 140
        option_spacing = 70
        option_width = 450
        option_height = 55
        
        for i, option in enumerate(self.pause_menu_options):
            option_y = option_start_y + i * option_spacing
            option_x = panel_x + (panel_width - option_width) // 2
            
            if i == self.pause_menu_index:
                selection_color = (80, 120, 200, 100)
                selection_surface = pygame.Surface((option_width, option_height), pygame.SRCALPHA)
                selection_surface.fill(selection_color)
                pygame.draw.rect(selection_surface, (150, 200, 255), (0, 0, option_width, option_height), 2)
                surface.blit(selection_surface, (option_x, option_y - 10))
                
                text_color = (255, 255, 255)
            else:
                text_color = (200, 220, 240)
            
            option_surface = self.text_font.render(option, True, text_color)
            text_x = option_x + (option_width - option_surface.get_width()) // 2
            text_y = option_y + (option_height - option_surface.get_height()) // 2
            surface.blit(option_surface, (text_x, text_y))
        
        instructions_y = panel_y + panel_height - 60
        instruction_text = "UP/DOWN Navigate  •  ENTER Select  •  ESC Quick Resume"
        instruction_surface = self.small_font.render(instruction_text, True, (180, 200, 220))
        instruction_x = panel_x + (panel_width - instruction_surface.get_width()) // 2
        surface.blit(instruction_surface, (instruction_x, instructions_y))
        
        status_text = "⏸ ALL GAME SYSTEMS FROZEN"
        status_surface = self.small_font.render(status_text, True, (100, 255, 100))
        status_x = 20
        status_y = 20
        surface.blit(status_surface, (status_x, status_y))
    
    def render_game_over(self, surface: pygame.Surface, score: int):
        """Render game over screen."""
        overlay = pygame.Surface((self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((20, 0, 0))
        surface.blit(overlay, (0, 0))
        
        ############################################
        game_over_text = "GAME OVER"
        game_over_surface = self.title_font.render(game_over_text, True, (255, 100, 100))
        game_over_x = self.settings.SCREEN_WIDTH // 2 - game_over_surface.get_width() // 2
        game_over_y = self.settings.SCREEN_HEIGHT // 2 - 100
        surface.blit(game_over_surface, (game_over_x, game_over_y))
        
        #####################################
        score_text = f"Final Score: {score}"
        score_surface = self.menu_font.render(score_text, True, (255, 255, 255))
        score_x = self.settings.SCREEN_WIDTH // 2 - score_surface.get_width() // 2
        score_y = game_over_y + 80
        surface.blit(score_surface, (score_x, score_y))
        
        ################################################
        instruction_text = "Press R to restart or M for main menu"
        instruction_surface = self.text_font.render(instruction_text, True, (200, 200, 200))
        instruction_x = self.settings.SCREEN_WIDTH // 2 - instruction_surface.get_width() // 2
        instruction_y = score_y + 60
        surface.blit(instruction_surface, (instruction_x, instruction_y))
    
    def render_victory(self, surface: pygame.Surface, score: int):
        """Render victory screen."""
        overlay = pygame.Surface((self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 20, 0))
        surface.blit(overlay, (0, 0))
        
        ############################################
        victory_text = "VICTORY!"
        victory_surface = self.title_font.render(victory_text, True, (100, 255, 100))
        victory_x = self.settings.SCREEN_WIDTH // 2 - victory_surface.get_width() // 2
        victory_y = self.settings.SCREEN_HEIGHT // 2 - 100
        surface.blit(victory_surface, (victory_x, victory_y))
        
        ################################################
        score_text = f"Final Score: {score}"
        score_surface = self.menu_font.render(score_text, True, (255, 255, 255))
        score_x = self.settings.SCREEN_WIDTH // 2 - score_surface.get_width() // 2
        score_y = victory_y + 80
        surface.blit(score_surface, (score_x, score_y))
        
        ########################################################
        instruction_text = "Press R to restart or M for main menu"
        instruction_surface = self.text_font.render(instruction_text, True, (200, 200, 200))
        instruction_x = self.settings.SCREEN_WIDTH // 2 - instruction_surface.get_width() // 2
        instruction_y = score_y + 60
        surface.blit(instruction_surface, (instruction_x, instruction_y))
    
    def get_selected_ship_type(self) -> str:
        """Get the currently selected ship type"""
        if self.starfighter_selector:
            selected_ship = self.starfighter_selector.get_selected_ship()
            if selected_ship and isinstance(selected_ship, dict):
                ship_key = selected_ship.get('sprite_key')
                if ship_key and isinstance(ship_key, str):
                    return ship_key
                else:
                    debug_print(f"Warning: Invalid sprite_key in selected ship: {ship_key}")
                    return 'ship1'
            else:
                debug_print("Warning: No valid ship selected, using default")
                return 'ship1'
        else:
            debug_print("Warning: Starfighter selector not initialized, using default")
            return 'ship1'