import pygame
import os
import random
import math
from typing import List, Dict, Any
from game.scene_manager import SceneManager
from game.settings import Settings, GameState
from entities.player import Player
from entities.enemy import Enemy
from entities.boss import Boss
from entities.projectile import Projectile
from entities.powerup import PowerUp
from effects.particle_system import ParticleSystem
from effects.explosion import Explosion
from ui.hud import HUD
from utils.resource_manager import ResourceManager
from utils.audio_manager import AudioManager
from utils.collision_manager import CollisionManager
from utils.debug_utils import debug_print

class Star:
    def __init__(self, x: int, y: int, speed: float, brightness: int):
        self.x = x
        self.y = y
        self.speed = speed
        self.brightness = brightness
        self.size = 1 if brightness < 150 else 2
    
    def update(self, dt: int):
        """Update star position."""
        self.y += self.speed
    
    def render(self, surface: pygame.Surface):
        """Render star."""
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)

class Planet:
    def __init__(self, x: int, y: int, sprite: pygame.Surface, speed: float, size_scale: float = 1.0):
        self.original_sprite = sprite
        self.speed = speed
        self.size_scale = size_scale
        self.rotation = 0
        self.rotation_speed = random.uniform(-0.5, 0.5)  # Slow rotation
        self.alpha = random.randint(80, 150)  # Semi-transparent
        
        # Scale the planet
        scaled_size = int(sprite.get_width() * size_scale), int(sprite.get_height() * size_scale)
        self.sprite = pygame.transform.scale(sprite, scaled_size)
        self.sprite.set_alpha(self.alpha)
        
        # Position
        self.x = x
        self.y = y
        self.width = self.sprite.get_width()
        self.height = self.sprite.get_height()
        
        # Glow effect properties
        self.glow_timer = random.randint(0, 1000)
    
    def update(self, dt: int):
        """Update planet position and rotation."""
        self.y += self.speed
        self.rotation += self.rotation_speed
        self.glow_timer += dt * 0.001
        
        # Keep rotation in bounds
        if self.rotation >= 360:
            self.rotation -= 360
        elif self.rotation < 0:
            self.rotation += 360
    
    def render(self, surface: pygame.Surface):
        """Render planet with rotation and glow effect."""
        # Create rotated sprite
        rotated_sprite = pygame.transform.rotate(self.sprite, self.rotation)
        
        # Add subtle glow effect
        glow_intensity = math.sin(self.glow_timer) * 0.3 + 0.7
        glow_alpha = int(30 * glow_intensity)
        
        if glow_alpha > 0:
            glow_size = max(rotated_sprite.get_width(), rotated_sprite.get_height()) + 40
            glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            
            # Create gradient glow
            center = glow_size // 2
            for radius in range(center, 0, -2):
                alpha = int(glow_alpha * (1 - radius / center))
                if alpha > 0:
                    color = (100, 150, 200, alpha)  # Blueish glow
                    pygame.draw.circle(glow_surface, color, (center, center), radius)
            
            # Position glow
            glow_x = self.x + self.width // 2 - glow_size // 2
            glow_y = self.y + self.height // 2 - glow_size // 2
            surface.blit(glow_surface, (glow_x, glow_y))
        
        # Render the planet
        sprite_rect = rotated_sprite.get_rect()
        center_x = int(self.x + self.width // 2)  # Convert to int
        center_y = int(self.y + self.height // 2)  # Convert to int
        sprite_rect.center = (center_x, center_y)  # Now both are int
        surface.blit(rotated_sprite, sprite_rect)
    
    def is_off_screen(self, screen_height: int) -> bool:
        """Check if planet is completely off screen."""
        return self.y > screen_height + 100

class Background:
    def __init__(self, screen_width: int, screen_height: int, resource_manager: ResourceManager):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.resource_manager = resource_manager
        
        # Star layers for parallax effect
        self.star_layers = [
            {'stars': [], 'speed': 0.5, 'count': 80},   # Distant stars
            {'stars': [], 'speed': 1.0, 'count': 60},   # Far stars
            {'stars': [], 'speed': 1.5, 'count': 40},   # Medium stars
            {'stars': [], 'speed': 2.0, 'count': 20},   # Close stars
        ]
        
        # Planet layer
        self.planets = []
        self.planet_spawn_timer = 0
        self.planet_spawn_rate = 8000  # 8 seconds between planets
        
        # Nebula effects (optional colored regions)
        self.nebula_regions = []
        self.nebula_timer = 0
        
        self.initialize_stars()
        self.initialize_nebula()
    
    def initialize_stars(self):
        """Initialize all star layers."""
        for layer in self.star_layers:
            for _ in range(layer['count']):
                x = random.randint(0, self.screen_width)
                y = random.randint(0, self.screen_height)
                brightness = random.randint(50, 255)
                star = Star(x, y, layer['speed'], brightness)
                layer['stars'].append(star)
    
    def initialize_nebula(self):
        """Initialize nebula color regions."""
        colors = [
            (20, 0, 40),    # Purple
            (0, 20, 40),    # Blue
            (40, 0, 20),    # Red
            (0, 40, 20),    # Green
        ]
        
        for _ in range(3):  # 3 nebula regions
            x = random.randint(-200, self.screen_width + 200)
            y = random.randint(-300, self.screen_height + 300)
            color = random.choice(colors)
            size = random.randint(200, 400)
            speed = random.uniform(0.1, 0.3)
            
            self.nebula_regions.append({
                'x': x, 'y': y, 'color': color, 'size': size, 'speed': speed,
                'alpha': random.randint(20, 40)
            })
    
    def spawn_planet(self):
        """Spawn a new planet"""
        # Get available planet sprites
        planet_sprites = []
        for i in range(4):  # I have 4 planet sprites
            sprite = self.resource_manager.get_sprite(f'planet_{i}')
            if sprite:
                planet_sprites.append(sprite)
        
        if not planet_sprites:
            debug_print("❌ No planet sprites available for background")
            return  # No planet sprites available
        
        # Choose random planet
        sprite = random.choice(planet_sprites)
        
        # Random position (can be partially off-screen for variety)
        x = random.randint(-100, self.screen_width + 100)
        y = random.randint(-200, -100)  # Start above screen
        
        # Random size (some planets closer/farther)
        size_scale = random.uniform(0.4, 1.2)
        
        # Random speed (very slow)
        speed = random.uniform(0.2, 0.8)
        
        try:
            planet = Planet(x, y, sprite, speed, size_scale)
            self.planets.append(planet)
            debug_print(f"Spawned planet at ({x}, {y}) with scale {size_scale:.2f}")
        except Exception as e:
            debug_print(f"❌ Error creating planet: {e}")
    
    def update(self, dt: int):
        """Update background elements."""
        # Update stars
        for layer in self.star_layers:
            for star in layer['stars']:
                star.update(dt)
                
                # Wrap around screen
                if star.y > self.screen_height:
                    star.y = -10
                    star.x = random.randint(0, self.screen_width)
        
        # Update nebula
        self.nebula_timer += dt
        for nebula in self.nebula_regions:
            nebula['y'] += nebula['speed']
            if nebula['y'] > self.screen_height + 200:
                nebula['y'] = -400
                nebula['x'] = random.randint(-200, self.screen_width + 200)
        
        # Spawn planets periodically
        self.planet_spawn_timer += dt
        if self.planet_spawn_timer >= self.planet_spawn_rate:
            self.spawn_planet()
            self.planet_spawn_timer = 0
            # Vary spawn rate slightly
            self.planet_spawn_rate = random.randint(6000, 12000)
        
        # Update planets
        for planet in self.planets[:]:
            planet.update(dt)
            if planet.is_off_screen(self.screen_height):
                self.planets.remove(planet)
    
    def render(self, surface: pygame.Surface):
        """Render background with enhanced effects."""
        # Fill with deep space color
        surface.fill((2, 2, 8))
        
        # Render nebula regions first (background layer)
        for nebula in self.nebula_regions:
            nebula_surface = pygame.Surface((nebula['size'], nebula['size']), pygame.SRCALPHA)
            
            # Create gradient nebula effect
            center = nebula['size'] // 2
            for radius in range(center, 0, -5):
                alpha = int(nebula['alpha'] * (1 - radius / center))
                if alpha > 0:
                    color = (*nebula['color'], alpha)
                    pygame.draw.circle(nebula_surface, color, (center, center), radius)
            
            surface.blit(nebula_surface, (nebula['x'] - center, nebula['y'] - center))
        
        # Render star layers (back to front for parallax)
        for layer in self.star_layers:
            for star in layer['stars']:
                star.render(surface)
        
        # Render planets (in front of stars, behind game objects)
        for planet in self.planets:
            planet.render(surface)

class GameEngine:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        pygame.display.set_caption(settings.TITLE)
        
        # Set custom icon
        self.set_window_icon()
        
        self.clock = pygame.time.Clock()
        
        # Initialize managers
        self.resource_manager = ResourceManager()
        self.audio_manager = AudioManager(settings)
        self.collision_manager = CollisionManager()
        
        
        self.scene_manager = SceneManager(settings, self.resource_manager)
        
        # Background
        self.background = None
        
        # Game state
        self.state = GameState.MENU  # Start at menu
        self.score = 0
        self.level = 1
        self.running = True
        
        # Game objects - Initialize as empty
        self.player = None
        self.enemies: List[Enemy] = []
        self.bosses: List[Boss] = []
        self.projectiles: List[Projectile] = []
        self.powerups: List[PowerUp] = []
        self.explosions: List[Explosion] = []
        
        # Effects
        self.particle_system = ParticleSystem()
        
        # UI
        self.hud = HUD(settings)
        
        # Timers
        self.last_enemy_spawn = 0
        self.last_powerup_spawn = 0
        
        # Game time system for proper pausing
        self.game_time = 0  # Actual game time (pauses when game is paused)
        self.real_time = 0  # Real time (never pauses)
        self.pause_time_offset = 0  # Time lost to pausing
        
        # Selected ship type
        self.selected_ship_type = 'ship1'
        
        self._last_debug_state = None
        self._debug_counter = 0
        
        # Only load resources, don't initialize game yet
        self.load_initial_resources()
        
        debug_print("✅ GameEngine initialized - Starting at main menu")
        
    def load_initial_resources(self):
        """Load only essential resources needed for menus."""
        debug_print("Loading initial resources for menus...")
        
        # Load all assets (needed for ship selection)
        self.resource_manager.load_all_assets()
        
        # Initialize scene manager (this will load ship selector)
        self.scene_manager = SceneManager(self.settings, self.resource_manager)
        
        # Connect HUD to game engine for game time access
        self.hud.game_engine_ref = self
        
        # AUDIO: Connect audio manager to scene manager
        self.scene_manager.set_audio_manager(self.audio_manager)
        
        # SPLASH: Connect audio manager to splash screen and start splash music
        if self.scene_manager.splash_screen:
            self.scene_manager.splash_screen.set_audio_manager(self.audio_manager)
            # Start splash music immediately after connecting
            self.scene_manager.splash_screen.start_music()
        
        debug_print("✅ Initial resources loaded")
        
    def get_game_time(self) -> int:
        """Get current game time that respects pause state."""
        if self.state == GameState.PAUSED:
            # Return frozen time when paused
            return self.game_time
        else:
            # Update game time when not paused
            current_real_time = pygame.time.get_ticks()
            self.game_time = current_real_time - self.pause_time_offset
            return self.game_time
        
    def set_window_icon(self):
        """Set the window icon with proper loading and fallback creation."""
        icon_paths = [
            "icon.png",                    # Root directory
            "assets/icon.png",             # Assets folder
            "assets/sprites/icon.png",     # Sprites folder
            "assets/ui/icon.png",          # UI folder
            "icon.ico",                    # ICO format
            "assets/icon.ico",             # ICO in assets
            "game_icon.png",               # Alternative names
            "space_shooter_icon.png",      # Descriptive name
        ]
        
        icon_loaded = False
        
        # Try to load existing icon files
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                try:
                    # Load the icon
                    icon_surface = pygame.image.load(icon_path).convert_alpha()
                    
                    # Get original size info
                    original_size = icon_surface.get_size()
                    
                    # Resize icon if needed (optimal size is 32x32)
                    if original_size[0] != 32 or original_size[1] != 32:
                        icon_surface = pygame.transform.scale(icon_surface, (32, 32))
                        debug_print(f"✓ Resized icon from {original_size[0]}x{original_size[1]} to 32x32")
                    
                    # Set the icon
                    pygame.display.set_icon(icon_surface)
                    debug_print(f"✓ Window icon loaded successfully: {icon_path}")
                    icon_loaded = True
                    break
                    
                except pygame.error as e:
                    debug_print(f"Could not load icon from {icon_path}: {e}")
                except Exception as e:
                    debug_print(f"Error loading icon from {icon_path}: {e}")
        
        # If no icon found, create a simple fallback icon
        if not icon_loaded:
            debug_print("⚠ No icon file found, creating default space-themed icon...")
            icon_surface = self.create_default_icon()
            pygame.display.set_icon(icon_surface)
            debug_print("✓ Created and set default space shooter icon")
    
    def create_default_icon(self) -> pygame.Surface:
        """Create a simple default icon if no icon file is found."""
        # Create 32x32 icon surface
        icon = pygame.Surface((32, 32), pygame.SRCALPHA)
        
        # Space background (dark blue/black)
        icon.fill((10, 10, 30))
        
        # Draw a simple spaceship shape
        # Main body (triangle)
        ship_points = [(16, 8), (12, 24), (20, 24)]
        pygame.draw.polygon(icon, (150, 200, 255), ship_points)
        
        # Ship engines (small rectangles)
        pygame.draw.rect(icon, (255, 100, 100), (13, 24, 2, 4))  # Left engine
        pygame.draw.rect(icon, (255, 100, 100), (17, 24, 2, 4))  # Right engine
        
        # Add some stars
        star_positions = [(5, 5), (25, 7), (8, 18), (23, 20), (6, 28), (26, 25)]
        for star_x, star_y in star_positions:
            pygame.draw.circle(icon, (255, 255, 255), (star_x, star_y), 1)
        
        # Add ship glow
        pygame.draw.circle(icon, (100, 150, 255, 100), (16, 16), 12)
        
        return icon
    
    def initialize_game(self, selected_ship_type: str = None):
        """Initialize game objects when starting actual gameplay."""
        debug_print("Initializing game for gameplay...")
        
        # Initialize background for gameplay
        if self.background is None:
            self.background = Background(
                self.settings.SCREEN_WIDTH, 
                self.settings.SCREEN_HEIGHT, 
                self.resource_manager
            )
        
        # Reset game state
        self.reset_game()
        
        debug_print("✅ Game initialization complete for gameplay")
    
    def reset_game(self):
        """Reset game to initial state with selected ship."""
        debug_print("Resetting game...")
        
        # Reset time systems
        self.game_time = 0
        self.pause_time_offset = 0
        
        # Get selected ship type from scene manager
        self.selected_ship_type = self.scene_manager.get_selected_ship_type()
        debug_print(f"Selected ship type: {self.selected_ship_type}")
        
        # Get the correct sprite for the selected ship
        ship_sprite = self.resource_manager.get_sprite(self.selected_ship_type)
        if ship_sprite is None:
            # Try fallback sprites
            fallback_sprites = ['player', 'ship1', 'ship2']
            for fallback in fallback_sprites:
                ship_sprite = self.resource_manager.get_sprite(fallback)
                if ship_sprite is not None:
                    debug_print(f"Using fallback sprite: {fallback}")
                    break
            
            # If still no sprite, create a placeholder
            if ship_sprite is None:
                debug_print("❌ ERROR: No ship sprites available! Creating placeholder")
                ship_sprite = self.resource_manager.create_placeholder_sprite('emergency_player')
                if ship_sprite is None:
                    debug_print("❌ CRITICAL: Cannot create placeholder sprite")
                    return
        
        # Create player - ship_sprite is guaranteed to not be None here
        self.player = Player(
            self.settings.SCREEN_WIDTH // 2 - 25,
            self.settings.SCREEN_HEIGHT - 100,
            ship_sprite,  # Now guaranteed to be a valid Surface
            self.settings,
            ship_type=self.selected_ship_type
        )
        
        # Connect particle system to player for thruster effects
        self.player.particle_system_ref = self.particle_system
        
        # Set player to use game time system
        self.player.game_engine_ref = self
        
        debug_print("✓ Player connected to particle system and game time")
        
        # Clear all game objects
        self.enemies.clear()
        self.bosses.clear()
        self.projectiles.clear()
        self.powerups.clear()
        self.explosions.clear()
        
        # Reset game state with game time
        self.score = 0
        self.level = 1
        self.last_enemy_spawn = self.get_game_time()
        self.last_powerup_spawn = self.get_game_time()
        
        # Set state to playing
        self.state = GameState.PLAYING
        debug_print(f"Game reset complete with {self.selected_ship_type}")
    
    def run(self):
        """Main game loop"""
        debug_print("Starting main game loop...")
        self.clock = pygame.time.Clock()
        running = True
        
        while running:
            # Calculate delta time and get FPS
            dt = self.clock.tick(self.settings.FPS)
            current_fps = self.clock.get_fps()
            
            # Handle input and check for exit
            input_result = self.handle_input()
            if input_result == 'exit_game':
                debug_print("🚪 Exiting game...")
                running = False
                break
            
            # Update game (respects pause state now)
            self.update(dt)
            
            # Render game (with proper FPS)
            self.render(current_fps)
            
            # Update display
            pygame.display.flip()
        
        debug_print("🛑 Game loop ended")
        pygame.quit()
        
    def clear_game_state(self):
        """Clear game state without starting a new game."""
        debug_print("Clearing game state...")
        
        # Clear all game objects
        self.enemies.clear()
        self.bosses.clear()
        self.projectiles.clear()
        self.powerups.clear()
        self.explosions.clear()
        
        # Reset counters
        self.score = 0
        self.level = 1
        self.last_enemy_spawn = 0
        self.last_powerup_spawn = 0
        
        # Clear player but don't set state to PLAYING
        self.player = None
        
        debug_print("Game state cleared")
        
    def handle_victory_input(self, event):
        """Handle victory input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                debug_print("-> Restart requested from victory")
                return 'restart'
            elif event.key == pygame.K_m:
                debug_print("-> Main menu requested from victory via 'M' key")
                return 'main_menu'
            elif event.key == pygame.K_ESCAPE:
                debug_print("-> Exit requested from victory")
                return 'exit_game'
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                debug_print("-> Restart requested from victory (ENTER/SPACE)")
                return 'restart'
        
        return None
    
    def handle_input(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'exit_game'
            
            # Handle music crossfade events first
            if self.audio_manager:
                self.audio_manager.handle_crossfade_event(event)
                self.audio_manager.handle_menu_return_event(event)
            
            if self.state == GameState.MENU:
                # Scene manager handles splash screen automatically
                result = self.scene_manager.handle_menu_input(event)
                if result == 'start_game':
                    # Initialize the game when actually starting
                    self.initialize_game()
                elif result == 'exit_game':
                    return 'exit_game'
            
            elif self.state == GameState.PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        debug_print("-> GAME COMPLETELY PAUSED - All timers frozen")
                        debug_print(f"-> Game time frozen at: {self.get_game_time()}ms")
                        self.state = GameState.PAUSED
                        # Record when we paused for time calculations
                        self.pause_start_time = pygame.time.get_ticks()
            
            elif self.state == GameState.PAUSED:
                pause_result = self.scene_manager.handle_pause_input(event)
                if pause_result == 'resume':
                    debug_print("-> ▶ GAME RESUMED - All timers restored")
                    
                    # Calculate how long we were paused and add to offset
                    if hasattr(self, 'pause_start_time'):
                        pause_duration = pygame.time.get_ticks() - self.pause_start_time
                        self.pause_time_offset += pause_duration
                        debug_print(f"-> Added {pause_duration}ms to pause offset (total: {self.pause_time_offset}ms)")
                        debug_print(f"-> Game time will resume at: {self.get_game_time()}ms")
                    
                    self.state = GameState.PLAYING
                    
                elif pause_result == 'main_menu':
                    debug_print("-> Returning to main menu from pause")
                    self.state = GameState.MENU
                    self.scene_manager.current_menu = 'main'
                    self.clear_game_state()
                    if self.audio_manager:
                        self.audio_manager.return_to_menu_music()
                    
                elif pause_result == 'exit_game':
                    debug_print("-> Exit game from pause menu")
                    return 'exit_game'
            
            elif self.state == GameState.GAME_OVER:
                game_over_result = self.handle_game_over_input(event)
                if game_over_result == 'restart':
                    self.reset_game()
                elif game_over_result == 'main_menu':
                    debug_print("-> Returning to main menu from game over")
                    self.state = GameState.MENU
                    self.scene_manager.current_menu = 'main'
                    self.clear_game_state()
                    if self.audio_manager:
                        self.audio_manager.return_to_menu_music()
                elif game_over_result == 'exit_game':
                    debug_print("-> Exit game from game over")
                    return 'exit_game'
            
            elif self.state == GameState.VICTORY:
                victory_result = self.handle_victory_input(event)
                if victory_result == 'restart':
                    self.reset_game()
                elif victory_result == 'main_menu':
                    debug_print("-> Returning to main menu from victory")
                    self.state = GameState.MENU
                    self.scene_manager.current_menu = 'main'
                    self.clear_game_state()
                    if self.audio_manager:
                        self.audio_manager.return_to_menu_music()
                elif victory_result == 'exit_game':
                    debug_print("-> Exit game from victory")
                    return 'exit_game'
        
        return None  # Continue game
    
    def update(self, dt: int):
        """Update game logic."""
        # Update scene manager (always - for menus and pause animations)
        self.scene_manager.update(dt)
        
        # Update music fading (always update, even when paused)
        if self.audio_manager:
            self.audio_manager.update_music_fade(dt)
        
        # Only update background when NOT paused
        if self.state != GameState.PAUSED:
            # Update background only when not paused
            if self.background:
                self.background.update(dt)
        
        # Only update game logic when NOT paused
        if self.state != GameState.PAUSED:
            # Get current game time (respects pause)
            current_game_time = self.get_game_time()
            
            # Update player ONLY when not paused
            if self.player and self.player.alive:
                keys = pygame.key.get_pressed()
                self.player.handle_input(keys)
                self.player.update(dt)  # Player handles its own powerup expiration now
                
                # Enhanced player shooting - CONTINUOUS FIRE (only when not paused)
                if keys[pygame.K_SPACE]:
                    bullets = self.player.shoot()
                    if bullets:
                        self.projectiles.extend(bullets)
                        if hasattr(self.audio_manager, 'play_sound'):
                            self.audio_manager.play_sound('shoot')
            
            # Spawn enemies (only when not paused) - use game time
            spawn_rate = max(500, self.settings.ENEMY_SPAWN_RATE - (self.level * 100))
            if current_game_time - self.last_enemy_spawn > spawn_rate:
                self.spawn_enemy()
                self.last_enemy_spawn = current_game_time
            
            # Spawn powerups (only when not paused) - use game time
            if current_game_time - self.last_powerup_spawn > self.settings.POWERUP_SPAWN_RATE:
                self.spawn_powerup()
                self.last_powerup_spawn = current_game_time
            
            # Spawn boss (only when not paused)
            if self.score >= self.level * self.settings.BOSS_SPAWN_SCORE and not self.bosses:
                self.spawn_boss()
            
            # Update all entities (only when not paused)
            self.update_entities(dt)
            
            # Handle collisions (only when not paused)
            self.collision_manager.check_collisions(self)
            
            # Update effects (only when not paused)
            self.particle_system.update(dt)
            self.update_explosions(dt)
            
            # Clean up dead objects (only when not paused)
            self.cleanup_entities()
            
            # Check game over conditions (only when not paused)
            self.check_game_state()
    
    def spawn_enemy(self):
        """Spawn a new enemy."""
        x = random.randint(0, self.settings.SCREEN_WIDTH - 50)
        y = -50
        
        # Higher chance of stronger enemies at higher levels
        if self.level <= 2:
            enemy_type = random.choice(['basic', 'basic', 'fast'])
        elif self.level <= 5:
            enemy_type = random.choice(['basic', 'fast', 'heavy'])
        else:
            enemy_type = random.choice(['fast', 'heavy', 'heavy'])
        
        
        sprite = self.resource_manager.get_sprite(f'enemy_{enemy_type}')
        if sprite is None:
            # Try fallback enemy sprites
            fallback_enemies = ['enemy_basic', 'enemy_fast', 'enemy_heavy']
            for fallback in fallback_enemies:
                sprite = self.resource_manager.get_sprite(fallback)
                if sprite is not None:
                    debug_print(f"Using fallback enemy sprite: {fallback}")
                    break
            
            # If still no sprite, create placeholder
            if sprite is None:
                debug_print(f"Creating placeholder for enemy_{enemy_type}")
                sprite = self.resource_manager.create_placeholder_sprite(f'enemy_{enemy_type}')
                if sprite is None:
                    debug_print(f"❌ Failed to create enemy {enemy_type}, skipping spawn")
                    return
        
        # Create enemy - sprite is guaranteed to not be None here
        enemy = Enemy(x, y, sprite, enemy_type, self.settings)
        self.enemies.append(enemy)
    
    def spawn_powerup(self):
        """Spawn a new powerup."""
        x = random.randint(50, self.settings.SCREEN_WIDTH - 50)
        y = -50
        powerup_type = random.choice(['health', 'rapid_fire', 'shield', 'missile'])
        
        sprite = self.resource_manager.get_sprite(f'powerup_{powerup_type}')
        if sprite is None:
            fallback_powerups = ['powerup_health', 'powerup_rapid_fire', 'powerup_shield', 'powerup_missile']
            for fallback in fallback_powerups:
                sprite = self.resource_manager.get_sprite(fallback)
                if sprite is not None:
                    debug_print(f"Using fallback powerup sprite: {fallback}")
                    break
            
            # If still no sprite, create placeholder
            if sprite is None:
                debug_print(f"Creating placeholder for powerup_{powerup_type}")
                sprite = self.resource_manager.create_placeholder_sprite(f'powerup_{powerup_type}')
                if sprite is None:
                    debug_print(f"❌ Failed to create powerup {powerup_type}, skipping spawn")
                    return
        
        powerup = PowerUp(x, y, sprite, powerup_type, self.settings)
        self.powerups.append(powerup)
    
    def spawn_boss(self):
        """Spawn a boss enemy"""
        x = self.settings.SCREEN_WIDTH // 2 - 60
        y = -200
        
        sprite = self.resource_manager.get_sprite('boss')
        if sprite is None:
            debug_print("Boss sprite not found, creating placeholder")
            sprite = self.resource_manager.create_placeholder_sprite('boss', (200, 100, 100), (120, 80))
            if sprite is None:
                debug_print("❌ Failed to create boss, skipping spawn")
                return
        
        boss = Boss(x, y, sprite, self.settings)
        self.bosses.append(boss)
    
    def update_entities(self, dt: int):
        """Update all game entities."""
        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update(dt)
            
            # Enemy shooting for some types
            if hasattr(enemy, 'can_shoot_flag') and enemy.can_shoot_flag:
                bullet = enemy.shoot()
                if bullet:
                    self.projectiles.append(bullet)
            
            if enemy.y > self.settings.SCREEN_HEIGHT + 50:
                self.enemies.remove(enemy)
        
        # Update bosses
        for boss in self.bosses:
            boss.update(dt, self.player)
            
            # Boss shooting
            bullets = boss.shoot()
            if bullets:
                self.projectiles.extend(bullets)
            
            # Special attacks
            special_bullets = boss.special_attack()
            if special_bullets:
                self.projectiles.extend(special_bullets)
        
        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update(dt)
            if (projectile.y < -50 or projectile.y > self.settings.SCREEN_HEIGHT + 50 or
                projectile.x < -50 or projectile.x > self.settings.SCREEN_WIDTH + 50):
                self.projectiles.remove(projectile)
        
        # Update powerups
        for powerup in self.powerups[:]:
            powerup.update(dt)
            if powerup.y > self.settings.SCREEN_HEIGHT + 50:
                self.powerups.remove(powerup)
    
    def update_explosions(self, dt: int):
        """Update explosion effects."""
        for explosion in self.explosions[:]:
            explosion.update(dt)
            if explosion.finished:
                self.explosions.remove(explosion)
    
    def cleanup_entities(self):
        """Remove dead entities."""
        self.enemies = [e for e in self.enemies if e.alive]
        self.bosses = [b for b in self.bosses if b.alive]
        self.projectiles = [p for p in self.projectiles if p.alive]
        self.powerups = [p for p in self.powerups if p.alive]
    
    def check_game_state(self):
        """Check for game over or victory conditions."""
        if self.player and not self.player.alive:
            self.state = GameState.GAME_OVER
        
        # Level progression
        if self.score >= self.level * self.settings.LEVEL_SCORE_THRESHOLD:
            self.level += 1
    
    def add_explosion(self, x: int, y: int, explosion_type: str = 'normal'):
        """Add an explosion effect."""
        explosion = Explosion(x, y, explosion_type, self.resource_manager)
        self.explosions.append(explosion)
        self.audio_manager.play_sound('explosion')
        self.particle_system.add_explosion_particles(x, y)
    
    def add_score(self, points: int):
        """Add points to the score."""
        old_score = self.score
        self.score += points * self.level  # Level multiplier
        debug_print(f"Score updated: {old_score} -> {self.score} (+{points * self.level})")
    
    def render(self, fps: float = 0):
        """Render the current game state."""
        if self.state == GameState.MENU:
            if hasattr(self.audio_manager, 'play_music'):
                try:
                    if not pygame.mixer.music.get_busy():
                        self.audio_manager.play_music('background_music.wav')
                except:
                    pass  # Ignore music errors. I had to do because the music license can be restricted at that moment I don't have to face music errors when running the game
            
            self.scene_manager.render_menu(self.screen)
        elif self.state == GameState.PLAYING:
            self.render_game(fps)
        elif self.state == GameState.PAUSED:
            self.render_game(fps)
            self.scene_manager.render_pause_overlay(self.screen)
        elif self.state == GameState.GAME_OVER:
            self.render_game(fps)
            self.scene_manager.render_game_over(self.screen, self.score)
        elif self.state == GameState.VICTORY:
            self.render_game(fps)
            self.scene_manager.render_victory(self.screen, self.score)
        
        pygame.display.flip()
    
    def render_game(self, fps: float = 0):
        """Render the main game screen."""
        
        if self.background is not None:
            self.background.render(self.screen)
        else:
            self.screen.fill((2, 2, 8))
        
        # Game entities
        if self.player and self.player.alive:
            self.player.render(self.screen)
        
        for enemy in self.enemies:
            if enemy is not None:
                enemy.render(self.screen)
        
        for boss in self.bosses:
            if boss is not None:
                boss.render(self.screen)
        
        for projectile in self.projectiles:
            if projectile is not None:
                projectile.render(self.screen)
        
        for powerup in self.powerups:
            if powerup is not None:
                powerup.render(self.screen)
        
        for explosion in self.explosions:
            if explosion is not None:
                explosion.render(self.screen)
        
        #
        self.particle_system.render(self.screen)
        
        if self.player:
            self.hud.render(self.screen, self.player, self.score, self.level, fps)
                
    def handle_game_over_input(self, event):
        """Handle game over input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                debug_print("-> Restart requested from game over")
                return 'restart'
            elif event.key == pygame.K_m:
                debug_print("-> Main menu requested from game over via 'M' key")
                return 'main_menu'
            elif event.key == pygame.K_ESCAPE:
                debug_print("-> Exit requested from game over")
                return 'exit_game'
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                debug_print("-> Restart requested from game over (ENTER/SPACE)")
                return 'restart'
        
        return None