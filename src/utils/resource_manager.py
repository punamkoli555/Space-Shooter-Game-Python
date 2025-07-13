import pygame
import os
import glob
import random
from typing import Dict, Optional
from utils.debug_utils import debug_print

class ResourceManager:
    def __init__(self):
        self.sprites: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.fonts: Dict[str, pygame.font.Font] = {}
        
        # Asset paths
        self.sprites_path = "assets/sprites"
        self.sounds_path = "assets/sounds"
        self.fonts_path = "assets/fonts"
    
    def load_all_assets(self):
        """Load all game assets."""
        debug_print("🎮 Loading all game assets...")
        self.load_sprites()
        self.load_fonts()
        
        # Explicitly load planets last to ensure they're available
        debug_print("🪐 Final planet loading check...")
        self.load_planets()
        
        debug_print(f"✅ Asset loading complete. Total sprites: {len(self.sprites)}")
        
        # Debug: List all loaded sprites
        debug_print("📋 Loaded sprites:")
        for key in sorted(self.sprites.keys()):
            if 'planet' in key.lower():
                sprite = self.sprites[key]
                debug_print(f"   🪐 {key}: {sprite.get_width()}x{sprite.get_height()}")
    
    def load_sprites(self):
        """Load all sprite assets from your specific files."""
        debug_print("Loading sprites from your assets...")
        
        self.load_all_ship_sprites()
        self.load_enemy_ships()
        self.load_boss()
        self.load_powerups()
        self.load_missiles()
        self.load_planets()
        
        debug_print(f"Loaded {len(self.sprites)} sprites total")
    
    def load_all_ship_sprites(self):
        """Load ALL ship sprites for player selection."""
        ships_path = os.path.join(self.sprites_path, 'ships')
        
        debug_print(f"Scanning ships folder: {ships_path}")
        
        # Get all ship image files
        ship_files = []
        image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif']
        
        # Check if the path exists
        if not os.path.exists(ships_path):
            debug_print(f"Ships folder not found: {ships_path}")
            # Try alternative paths
            alt_paths = [
                os.path.join("assets", "sprites", "ships"),
                os.path.join("..", "assets", "sprites", "ships"),
                os.path.join("src", "..", "assets", "sprites", "ships")
            ]
            for alt_path in alt_paths:
                if os.path.exists(alt_path):
                    ships_path = alt_path
                    debug_print(f"Using alternative ships path: {ships_path}")
                    break
        
        for ext in image_extensions:
            pattern = os.path.join(ships_path, ext)
            ship_files.extend(glob.glob(pattern))
            subfolder_pattern = os.path.join(ships_path, '*', ext)
            ship_files.extend(glob.glob(subfolder_pattern))
        
        debug_print(f"Found {len(ship_files)} ship files")
        
        if len(ship_files) == 0:
            debug_print("No ship files found! Creating placeholder ships")
            self.create_placeholder_ships()
            return
        
        # Load player sprite (first priority)
        player_loaded = False
        player_candidates = [
            'Ship_1_A_Small.png', 'ship1.png'
        ]
        
        for candidate in player_candidates:
            for ship_file in ship_files:
                if candidate in os.path.basename(ship_file):
                    try:
                        sprite = pygame.image.load(ship_file).convert_alpha()
                        if sprite.get_width() > 100:
                            sprite = pygame.transform.scale(sprite, (64, 64))
                        self.sprites['player'] = sprite
                        debug_print(f"✓ Loaded player: {os.path.basename(ship_file)}")
                        player_loaded = True
                        break
                    except pygame.error as e:
                        debug_print(f"Could not load {ship_file}: {e}")
            if player_loaded:
                break
        
        # Track loaded ships
        ship_counter = 1
        
        # Load Ship_1_ Series (Light Fighters)
        for variant in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
            ship_key = f'ship{ship_counter}'
            loaded = False
            
            # Try different naming patterns
            patterns = [
                f'Ship_1_{variant}_Small.png',
                f'Ship_1_{variant}.png'
            ]
            
            for pattern in patterns:
                for ship_file in ship_files:
                    if pattern in os.path.basename(ship_file):
                        try:
                            sprite = pygame.image.load(ship_file).convert_alpha()
                            # Ensure consistent sizing
                            if sprite.get_width() > 100:
                                sprite = pygame.transform.scale(sprite, (64, 64))
                            self.sprites[ship_key] = sprite
                            debug_print(f"✓ Loaded {ship_key}: {os.path.basename(ship_file)} (Fighter Mk{variant})")
                            loaded = True
                            break
                        except pygame.error as e:
                            debug_print(f"Could not load {ship_file}: {e}")
                if loaded:
                    break
            
            if loaded:
                ship_counter += 1
        
        # Load Ship_2_ Series (Heavy Fighters/Cruisers)
        for variant in ['A', 'B', 'C', 'D', 'E', 'F']:
            ship_key = f'ship{ship_counter}'
            loaded = False
            
            patterns = [
                f'Ship_2_{variant}_Small.png',
                f'Ship_2_{variant}.png'
            ]
            
            for pattern in patterns:
                for ship_file in ship_files:
                    if pattern in os.path.basename(ship_file):
                        try:
                            sprite = pygame.image.load(ship_file).convert_alpha()
                            # Ensure consistent sizing
                            if sprite.get_width() > 100:
                                sprite = pygame.transform.scale(sprite, (64, 64))
                            self.sprites[ship_key] = sprite
                            debug_print(f"✓ Loaded {ship_key}: {os.path.basename(ship_file)} (Cruiser Mk{variant})")
                            loaded = True
                            break
                        except pygame.error as e:
                            debug_print(f"Could not load {ship_file}: {e}")
                if loaded:
                    break
            
            if loaded:
                ship_counter += 1
        
        # Load the large ship1-ship8 sprites (Custom Ships)
        for ship_num in range(1, 9):
            ship_key = f'ship{ship_counter}'
            filename = f'ship{ship_num}.png'
            loaded = False
            
            for ship_file in ship_files:
                if filename in os.path.basename(ship_file):
                    try:
                        sprite = pygame.image.load(ship_file).convert_alpha()
                        # Scale down large sprites to consistent size
                        if sprite.get_width() > 100:
                            sprite = pygame.transform.scale(sprite, (80, 80))  # Slightly larger for these special ships
                        self.sprites[ship_key] = sprite
                        debug_print(f"✓ Loaded {ship_key}: {filename} (Custom Ship {ship_num})")
                        loaded = True
                        break
                    except pygame.error as e:
                        debug_print(f"Could not load {ship_file}: {e}")
            
            if loaded:
                ship_counter += 1
        
        # Ensure we have at least one ship
        if ship_counter == 1 and not player_loaded:
            # Create a basic placeholder
            self.sprites['player'] = self.create_placeholder_sprite('player')
            self.sprites['ship1'] = self.sprites['player']
            debug_print("Created placeholder ships")
        elif not player_loaded and 'ship1' in self.sprites:
            self.sprites['player'] = self.sprites['ship1']
            debug_print("Using ship1 as player fallback")
        
        debug_print(f"Total ships loaded: {ship_counter - 1}")
    
    def load_enemy_ships(self):
        """Load enemy ship sprites."""
        enemies_path = os.path.join(self.sprites_path, 'enemies')
        
        # Map enemy types to specific files
        enemy_mapping = {
            'enemy_basic': ['Enemy_1_A_Small.png', 'Enemy_1_B_Small.png'],
            'enemy_fast': ['Enemy_2_A_Small.png', 'Enemy_2_B_Small.png'],
            'enemy_heavy': ['Enemy_3_A_Small.png', 'Enemy_3_B_Small.png', 'Enemy_4_A_Small.png']
        }
        
        for enemy_type, file_candidates in enemy_mapping.items():
            loaded = False
            for candidate in file_candidates:
                file_path = os.path.join(enemies_path, candidate)
                if os.path.exists(file_path):
                    try:
                        self.sprites[enemy_type] = pygame.image.load(file_path).convert_alpha()
                        debug_print(f"✓ Loaded {enemy_type}: {candidate}")
                        loaded = True
                        break
                    except pygame.error as e:
                        debug_print(f"Could not load {candidate}: {e}")
            
            if not loaded:
                self.sprites[enemy_type] = self.create_placeholder_sprite(enemy_type)
                debug_print(f"Created placeholder for {enemy_type}")
    
    def load_boss(self):
        """Load boss sprite."""
        boss_path = os.path.join(self.sprites_path, 'boss')
        
        boss_candidates = ['Boss_1_A_Small.png', 'Boss_1_B_Small.png']
        
        for candidate in boss_candidates:
            file_path = os.path.join(boss_path, candidate)
            if os.path.exists(file_path):
                try:
                    self.sprites['boss'] = pygame.image.load(file_path).convert_alpha()
                    debug_print(f"✓ Loaded boss: {candidate}")
                    return
                except pygame.error as e:
                    debug_print(f"Could not load {candidate}: {e}")
        
        # Fallback to placeholder
        self.sprites['boss'] = self.create_placeholder_sprite('boss')
        debug_print("Created placeholder for boss")
    
    def load_powerups(self):
        """Load powerup sprites."""
        pickup_path = os.path.join(self.sprites_path, 'pickup')
        
        # Map powerup types to pickup files
        powerup_mapping = {
            'powerup_health': ['Pickup_1_A_Small.png', 'Pickup_1_B_Small.png'],
            'powerup_rapid_fire': ['Pickup_2_A_Small.png', 'Pickup_2_B_Small.png'],
            'powerup_shield': ['Pickup_3_A_Small.png', 'Pickup_3_B_Small.png'],
            'powerup_missile': ['Pickup_1_C_Small.png', 'Pickup_2_C_Small.png']
        }
        
        for powerup_type, file_candidates in powerup_mapping.items():
            loaded = False
            for candidate in file_candidates:
                file_path = os.path.join(pickup_path, candidate)
                if os.path.exists(file_path):
                    try:
                        self.sprites[powerup_type] = pygame.image.load(file_path).convert_alpha()
                        debug_print(f"✓ Loaded {powerup_type}: {candidate}")
                        loaded = True
                        break
                    except pygame.error as e:
                        debug_print(f"Could not load {candidate}: {e}")
            
            if not loaded:
                self.sprites[powerup_type] = self.create_placeholder_sprite(powerup_type)
                debug_print(f"Created placeholder for {powerup_type}")
    
    def load_missiles(self):
        """Load missile sprites."""
        missile_path = os.path.join(self.sprites_path, 'missile')
        
        missile_files = [
            'Missile_A_Small.png',
            'Missile_B_Small.png',
            'Missile_C_Small.png'
        ]
        
        for i, missile_file in enumerate(missile_files):
            file_path = os.path.join(missile_path, missile_file)
            if os.path.exists(file_path):
                try:
                    self.sprites[f'missile_{i}'] = pygame.image.load(file_path).convert_alpha()
                    debug_print(f"✓ Loaded missile_{i}: {missile_file}")
                except pygame.error as e:
                    debug_print(f"Could not load {missile_file}: {e}")
    
    def load_planets(self):
        """Load planet sprites for background decoration."""
        planets_path = os.path.join(self.sprites_path, 'planets')
        
        debug_print(f"🪐 Loading planets from: {planets_path}")
        
        if not os.path.exists(planets_path):
            debug_print(f"❌ Planets folder not found: {planets_path}")
            return
        
        # Your exact planet files
        planet_files = [
            'Planet_01.png',
            'Planet_02.png', 
            'Planet_03.png',
            'Planet_04.png'
        ]
        
        loaded_count = 0
        for i, planet_file in enumerate(planet_files):
            file_path = os.path.join(planets_path, planet_file)
            if os.path.exists(file_path):
                try:
                    # Load the planet sprite
                    planet_sprite = pygame.image.load(file_path).convert_alpha()
                    debug_print(f"📸 Original planet size: {planet_sprite.get_width()}x{planet_sprite.get_height()}")
                    
                    # Scale to reasonable size for background (these are quite large)
                    target_size = 150  # Reasonable size for background planets
                    scaled_planet = pygame.transform.scale(planet_sprite, (target_size, target_size))
                    
                    # Store with the expected naming pattern
                    self.sprites[f'planet_{i}'] = scaled_planet
                    debug_print(f"✓ Loaded planet_{i}: {planet_file} (scaled to {target_size}x{target_size})")
                    loaded_count += 1
                    
                except pygame.error as e:
                    debug_print(f"❌ Could not load {planet_file}: {e}")
            else:
                debug_print(f"❌ Planet file not found: {file_path}")
        
        if loaded_count > 0:
            debug_print(f"🌍 Successfully loaded {loaded_count} planet sprites")
        else:
            debug_print("❌ Failed to load any planet sprites!")
    
    def load_fonts(self):
        """Load fonts."""
        try:
            self.fonts['default'] = pygame.font.Font(None, 36)
            self.fonts['large'] = pygame.font.Font(None, 72)
            self.fonts['small'] = pygame.font.Font(None, 24)
        except pygame.error as e:
            debug_print(f"Could not load fonts: {e}")
            self.fonts['default'] = pygame.font.Font(None, 36)
            self.fonts['large'] = pygame.font.Font(None, 72)
            self.fonts['small'] = pygame.font.Font(None, 24)
    
    def create_placeholder_ships(self):
        """Create placeholder ship sprites when no ship files are found."""
        debug_print("Creating placeholder ships")
        
        ship_colors = [
            (100, 150, 255),  # Blue
            (255, 150, 100),  # Orange
            (150, 255, 100),  # Green
            (255, 100, 150),  # Pink
            (200, 200, 100),  # Yellow
        ]
        
        for i, color in enumerate(ship_colors):
            sprite = self.create_placeholder_sprite(f'ship{i+1}', color, (64, 64))
            self.sprites[f'ship{i+1}'] = sprite
            if i == 0:
                self.sprites['player'] = sprite
    
    def create_placeholder_sprite(self, name: str, color=(100, 150, 255), size=(64, 64)) -> pygame.Surface:
        """Create a simple colored rectangle as a placeholder sprite - GUARANTEED RETURN."""
        try:
            sprite = pygame.Surface(size, pygame.SRCALPHA)
            # Create a simple ship-like shape
            pygame.draw.polygon(sprite, color, [
                (size[0]//2, 0),           # Top point
                (0, size[1]),              # Bottom left
                (size[0]//4, size[1]*3//4), # Inner bottom left
                (size[0]*3//4, size[1]*3//4), # Inner bottom right
                (size[0], size[1])         # Bottom right
            ])
            # Add a small highlight
            pygame.draw.polygon(sprite, tuple(min(255, c + 50) for c in color), [
                (size[0]//2, 0),
                (size[0]//3, size[1]//2),
                (size[0]*2//3, size[1]//2)
            ])
            debug_print(f"Created placeholder for {name}")
            return sprite
        except Exception as e:
            debug_print(f"❌ Error creating placeholder sprite for {name}: {e}")
            # Create minimal fallback sprite
            fallback_sprite = pygame.Surface(size)
            fallback_sprite.fill(color[:3])  # Use only RGB components
            return fallback_sprite
    
    def get_sprite(self, name: str) -> Optional[pygame.Surface]:
        """Get sprite by name."""
        return self.sprites.get(name)
    
    def get_sound(self, name: str) -> Optional[pygame.mixer.Sound]:
        """Get sound by name."""
        return self.sounds.get(name)
    
    def get_font(self, name: str) -> Optional[pygame.font.Font]:
        """Get font by name."""
        return self.fonts.get(name, self.fonts.get('default'))
    
    def list_available_sprites(self):
        """Print all available sprites for debugging."""
        debug_print("\n=== Available Sprites ===")
        ship_sprites = {k: v for k, v in self.sprites.items() if 'ship' in k}
        for name, sprite in ship_sprites.items():
            size = sprite.get_size()
            debug_print(f"{name}: {size[0]}x{size[1]}")
        debug_print("========================\n")
    
    def get_all_ship_keys(self):
        """Get all available ship sprite keys."""
        return [key for key in self.sprites.keys() if key.startswith('ship') and key != 'ship_selector']