import pygame
import math
import random
from typing import List, Dict, Optional, Tuple
from game.settings import Settings
from utils.debug_utils import debug_print

def easeInOutCubic(t):
    """Smooth cubic easing function for buttery animations."""
    return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2

def easeOutElastic(t):
    """Elastic bounce easing for dynamic effects."""
    c4 = (2 * math.pi) / 3
    if t == 0:
        return 0
    elif t == 1:
        return 1
    else:
        return pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1

def easeInOutQuart(t):
    """Smooth quartic easing for gentle animations."""
    return 8 * t * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 4) / 2

class StarfighterSelector:
    """
    To be added
    """
    
    def __init__(self, settings: Settings, resource_manager):
        self.settings = settings
        self.resource_manager = resource_manager
        
        # Modern typography with smooth scaling
        self.title_font = self._load_font(56)
        self.header_font = self._load_font(32)
        self.ship_font = self._load_font(24)
        self.stat_font = self._load_font(20)
        self.info_font = self._load_font(18)
        self.small_font = self._load_font(16)
        
        # Ship data
        self.ships = self._load_ship_catalog()
        self.selected_index = 0
        self.target_index = 0
        
        # animation state
        self.time = 0.0
        self.smooth_selection = 0.0  # Smooth interpolated selection
        self.selection_velocity = 0.0
        self.transition_time = 0.0
        self.transition_duration = 0.8
        
        # Advanced visual effects
        self.camera_shake = {'x': 0.0, 'y': 0.0, 'intensity': 0.0}
        self.ship_hover_state = {'scale': 1.0, 'rotation': 0.0, 'glow': 0.0}
        self.ui_animations = {
            'title_appear': 0.0,
            'stats_slide': 0.0,
            'ship_cards_emerge': 0.0,
            'hologram_strength': 0.0
        }
        # Particle systems
        self.floating_particles = []
        self.selection_particles = []
        self.energy_traces = []
        
        # layout dimensions
        self.screen_width = settings.SCREEN_WIDTH
        self.screen_height = settings.SCREEN_HEIGHT
        
        # Main ship display (center-right positioning)
        self.main_ship_size = min(320, int(self.screen_height * 0.4))
        self.main_ship_x = self.screen_width // 2 + 140
        self.main_ship_y = self.screen_height // 2 - 40
        
        # Compatibility attributes
        self.cosmic_wave = 0.0
        self.energy_pulse = 0.0
        self.rotation = 0.0
        self.pulse = 0.0
        self.selection_alpha = 1.0
        self.hover_scale = 1.0
        self.ship_rotation_3d = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.hologram_distortion = 0.0
        self.ship_display_width = self.main_ship_size
        self.ship_display_height = self.main_ship_size
        
        # Side panels for stats and info
        self.left_panel_width = 350
        self.right_panel_width = 400
        self.panel_margin = 40
        
        # Ship carousel at bottom
        self.carousel_height = 100  # Reduced height for better proportions
        self.carousel_y = self.screen_height - self.carousel_height - 30  # More margin
        self.ship_icon_size = 70  # Slightly smaller icons for better balance
        
        self.particles = []
        self.energy_particles = []
        self.background_stars = self._create_minimal_star_field()
        self.energy_rings = []
        self.scan_lines = []
        self.floating_elements = []
        
        # Compatibility attributes
        self.nebulae = []
        self.asteroids = []
        self.cosmic_dust = []
        self.energy_streams = []
        self.space_debris = []
          
        # Ensure colors are properly typed as RGB tuples
        self.colors: Dict[str, Tuple[int, int, int]] = {}
        self._init_professional_colors()
        
        self._init_modern_elements()
        
        debug_print(f"🚀 Modern Starfighter Selector initialized with {len(self.ships)} ships")
        
    def _init_professional_colors(self):
        """Initialize professional color scheme"""
        self.colors = {
            'background': (8, 12, 20),
            'panel_bg': (15, 25, 35),
            'accent_blue': (0, 150, 255),
            'accent_green': (0, 255, 150),
            'text_primary': (220, 230, 240),
            'text_secondary': (150, 160, 170),
            'border': (40, 60, 80),
            'stat_bg': (20, 30, 40),
            'selected': (0, 200, 100),
            'hover': (0, 120, 200),
            
            # Colors
            'primary': (64, 156, 255),
            'secondary': (126, 211, 33),
            'accent': (255, 138, 101),
            'info': (100, 200, 255),
            'success': (34, 197, 94),
            'warning': (251, 146, 60),
            'error': (239, 68, 68),
            'energy_bright': (255, 255, 255),
            'energy_dim': (100, 150, 200),
            'energy_glow': (64, 156, 255),
            'energy_trail': (89, 177, 255),
            'energy_core': (255, 255, 255),
            'selection_ring': (126, 211, 33),
            'text_accent': (0, 200, 150),
            'text_muted': (120, 130, 140),
            
            # Background layers
            'bg_deep': (12, 16, 28),
            'bg_mid': (18, 24, 38),
            'bg_surface': (24, 32, 48),
            'bg_elevated': (32, 42, 58),
            'bg_card': (28, 36, 52),
            
            # Glass effects (RGB only, no alpha in color definition)
            'glass_neutral': (20, 30, 40),
            'glass_primary': (64, 156, 255),
            'glass_secondary': (126, 211, 33),
            
            # Energy colors for compatibility
            'energy_blue': (64, 156, 255),
            'energy_cyan': (0, 255, 255),
            'energy_purple': (180, 100, 255),
            'energy_soft': (100, 150, 200),
            
            # Panel colors for compatibility
            'panel': (15, 25, 35)
        }
        
        
    def _init_modern_elements(self):
        """Initialize UI elements."""
        # Floating elements for subtle ambiance
        for _ in range(8):
            element = {
                'x': random.uniform(0, self.screen_width),
                'y': random.uniform(0, self.screen_height),
                'size': random.uniform(1, 3),
                'speed': random.uniform(5, 15),
                'opacity': random.uniform(0.05, 0.15),
                'color': random.choice([
                    self.colors['primary'],
                    self.colors['text_muted'],
                    self.colors['secondary']
                ])
            }
            self.floating_elements.append(element)
        
        # Minimal scan lines for subtle tech effect
        for i in range(0, self.screen_height, 8):
            self.scan_lines.append({
                'y': i,
                'opacity': random.uniform(0.02, 0.08),
                'speed': random.uniform(0.2, 1.0)
            })
    
    def _load_font(self, size: int) -> pygame.font.Font:
        """Load font with fallback to default."""
        try:
            return pygame.font.Font(None, size)
        except:
            return pygame.font.Font(pygame.font.get_default_font(), size)
    
    def _load_ship_catalog(self) -> List[Dict]:
        """Load and configure all available ships."""
        ships = []
        
        # Get ship sprites from resource manager
        try:
            ship_keys = self.resource_manager.get_all_ship_keys()
            debug_print(f"Found {len(ship_keys)} ship sprites")
        except:
            ship_keys = ['ship1', 'ship2', 'ship3', 'ship4', 'ship5']
            debug_print("Using fallback ship keys")
        
        # Ship class definitions with wider stat ranges
        ship_classes = {
            'interceptor': {
                'name': 'Interceptor',
                'description': 'Lightning-fast scout with superior agility and stealth capabilities',
                'stats': {'speed': 160, 'firepower': 60, 'armor': 50, 'shields': 70},
                'color': (0, 255, 150),
                'abilities': ['Afterburner', 'Stealth Cloak', 'Evasive Maneuvers']
            },
            'fighter': {
                'name': 'Fighter',
                'description': 'Balanced combat vessel perfect for versatile mission profiles',
                'stats': {'speed': 100, 'firepower': 90, 'armor': 70, 'shields': 80},
                'color': (100, 180, 255),
                'abilities': ['Rapid Fire', 'Energy Shield', 'Target Lock']
            },
            'assault': {
                'name': 'Assault',
                'description': 'Heavy gunship designed for frontline combat operations',
                'stats': {'speed': 70, 'firepower': 130, 'armor': 110, 'shields': 90},
                'color': (255, 120, 80),
                'abilities': ['Heavy Weapons', 'Armor Plating', 'Siege Mode']
            },
            'destroyer': {
                'name': 'Destroyer',
                'description': 'Massive dreadnought with devastating firepower and thick armor',
                'stats': {'speed': 60, 'firepower': 150, 'armor': 140, 'shields': 120},
                'color': (255, 80, 120),
                'abilities': ['Ion Cannon', 'Point Defense', 'Reinforced Hull']
            },
            'corvette': {
                'name': 'Corvette',
                'description': 'Multi-role vessel combining speed with moderate firepower',
                'stats': {'speed': 120, 'firepower': 70, 'armor': 60, 'shields': 70},
                'color': (180, 255, 100),
                'abilities': ['Boost Drive', 'Auto-Repair', 'Multi-Target']
            }
        }
        
        for i, ship_key in enumerate(ship_keys):
            sprite = self.resource_manager.get_sprite(ship_key)
            if sprite:
                # Determine ship class
                class_names = list(ship_classes.keys())
                ship_class = class_names[i % len(class_names)]
                class_data = ship_classes[ship_class]
                
                # Generate unique ship name
                ship_name = f"{class_data['name']}-{(i // len(class_names)) + 1:02d}"
                
                # Enhanced stat variation for guaranteed 5-star ships
                stats = {}
                
                # Create different quality tiers with higher legendary chance
                quality_roll = random.randint(1, 100)
                
                if quality_roll <= 10:  # 10% chance - Standard quality
                    # Standard ships: -30 to +10 variation
                    for stat_name, base_value in class_data['stats'].items():
                        variation = random.randint(-30, 10)
                        stats[stat_name] = max(20, min(200, base_value + variation))
                        
                elif quality_roll <= 35:  # 25% chance - Advanced quality  
                    # Advanced ships: -10 to +30 variation
                    for stat_name, base_value in class_data['stats'].items():
                        variation = random.randint(-10, 30)
                        stats[stat_name] = max(30, min(200, base_value + variation))
                        
                elif quality_roll <= 65:  # 30% chance - Superior quality
                    # Superior ships: +20 to +60 variation
                    for stat_name, base_value in class_data['stats'].items():
                        variation = random.randint(20, 60)
                        stats[stat_name] = min(200, base_value + variation)
                        
                elif quality_roll <= 85:  # 20% chance - Elite quality
                    # Elite ships: +50 to +90 variation
                    for stat_name, base_value in class_data['stats'].items():
                        variation = random.randint(50, 90)
                        stats[stat_name] = min(200, base_value + variation)
                        
                else:  # 15% chance - Legendary quality (GUARANTEED 5-star potential)
                    # Legendary ships: +100 to +150 variation (much higher!)
                    for stat_name, base_value in class_data['stats'].items():
                        variation = random.randint(100, 150)
                        stats[stat_name] = min(200, base_value + variation)
                
                ship_config = {
                    'id': i + 1,
                    'name': ship_name,
                    'class': class_data['name'],
                    'sprite_key': ship_key,
                    'sprite': sprite,
                    'description': class_data['description'],
                    'stats': stats,
                    'color': class_data['color'],
                    'abilities': class_data['abilities'],
                    'rating': self._calculate_rating(stats),
                    'tier': self._calculate_tier(stats)
                }
                
                ships.append(ship_config)
                
                total_stats = sum(stats.values())
                rating = ship_config['rating']
                tier = ship_config['tier']
                
                if rating >= 5.0:
                    debug_print(f"🌟🌟🌟🌟🌟 {ship_name}: {rating} stars | {tier} grade | Total: {total_stats} ⭐ LEGENDARY!")
                elif rating >= 4.5:
                    debug_print(f"-> {ship_name}: {rating} stars | {tier} grade | Total: {total_stats}")
                else:
                    debug_print(f"-> {ship_name}: {rating} stars | {tier} grade | Total: {total_stats}")
                    
                debug_print(f"Configured {ship_name}: {ship_class} class")
        
        if not ships:
            ships = self._create_fallback_ships()
        
        return ships
    
    def debug_ship_stats(self, ship_index: int):
        """Debug ship stats to verify calculations."""
        if 0 <= ship_index < len(self.ships):
            ship = self.ships[ship_index]
            stats = ship.get('stats', {})
            total = sum(stats.values())
            rating = ship.get('rating', 0)
            tier = ship.get('tier', 'Unknown')
            
            debug_print(f"\n🔍 DEBUG: {ship['name']}")
            debug_print(f"  Stats: {stats}")
            debug_print(f"  Total: {total}")
            debug_print(f"  Rating: {rating} stars")
            debug_print(f"  Tier: {tier}")
            debug_print(f"  Expected Tier: {self._calculate_tier(stats)}")
    
    def _calculate_rating(self, stats: Dict) -> float:
        """Calculate ship rating from 1.0 to 5.0."""
        total = sum(stats.values())
        
        if total < 250:
            rating = 1.0          # Poor ships
        elif total < 300:
            rating = 1.5          # Below average
        elif total < 350:
            rating = 2.0          # Standard (matches Standard tier)
        elif total < 420:
            rating = 2.5          # Good standard ships
        elif total < 500:
            rating = 3.0          # Advanced tier starts here
        elif total < 580:
            rating = 3.5          # Good advanced ships
        elif total < 650:
            rating = 4.0          # Superior tier starts here
        elif total < 720:
            rating = 4.5          # Great superior ships
        else:
            rating = 5.0          # Elite tier (720+ total stats)
        
        return rating

    def _calculate_tier(self, stats: Dict) -> str:
        """Calculate ship tier based on total stat."""
        total_stats = sum(stats.values())
        
        if total_stats < 350:      
            return "Standard"      # 1-2 stars (most basic ships)
        elif total_stats < 500:    
            return "Advanced"      # 2.5-3.5 stars (solid ships)
        elif total_stats < 650:    
            return "Superior"      # 4-4.5 stars (great ships)
        else:                      
            return "Elite"         # 5 stars (legendary ships)
    
    def _create_fallback_ships(self) -> List[Dict]:
        """Create fallback ships if no sprites available."""
        fallback = []
        for i in range(3):
            ship = {
                'id': i + 1,
                'name': f'Default Fighter {i + 1}',
                'class': 'Fighter',
                'sprite_key': 'default',
                'sprite': None,
                'description': 'Standard fighter configuration',
                'stats': {'speed': 100, 'firepower': 100, 'armor': 100, 'shields': 100},
                'color': (100, 180, 255),
                'abilities': ['Basic Systems'],
                'rating': 2.5,
                'tier': 'Standard'
            }
            fallback.append(ship)
        return fallback
    
    def _create_star_field(self) -> List[Dict]:
        """Create animated background stars."""
        stars = []
        for _ in range(150):
            star = {
                'x': random.randint(0, self.settings.SCREEN_WIDTH),
                'y': random.randint(0, self.settings.SCREEN_HEIGHT),
                'size': random.randint(1, 3),
                'brightness': random.uniform(0.3, 1.0),
                'twinkle_speed': random.uniform(0.5, 2.0),
                'drift_speed': random.uniform(0.1, 0.5),
                'phase': random.uniform(0, 2 * math.pi)
            }
            stars.append(star)
        return stars
    
    def _create_minimal_star_field(self) -> List[Dict]:
        """Create a minimal, clean star field."""
        stars = []
        for _ in range(60):  # Fewer stars for cleaner look
            star = {
                'x': random.uniform(0, self.screen_width),
                'y': random.uniform(0, self.screen_height),
                'size': random.choice([1, 1, 1, 2]),  # Mostly small stars
                'brightness': random.uniform(0.3, 0.8),
                'twinkle_speed': random.uniform(0.5, 2.0),
                'drift_speed': random.uniform(0.2, 0.8)
            }
            stars.append(star)
        return stars
    
    def _create_nebulae(self) -> List[Dict]:
        """Create animated nebula clouds for background."""
        nebulae = []
        for _ in range(8):
            nebula = {
                'x': random.uniform(-200, self.screen_width + 200),
                'y': random.uniform(-200, self.screen_height + 200),
                'size': random.uniform(150, 400),
                'color': random.choice([
                    (120, 50, 180, 30),   # Purple nebula
                    (50, 120, 200, 25),   # Blue nebula
                    (200, 80, 120, 20),   # Pink nebula
                    (80, 200, 150, 25),   # Cyan nebula
                ]),
                'drift_speed': random.uniform(5, 15),
                'pulse_speed': random.uniform(0.5, 1.5),
                'rotation': random.uniform(0, 360),
                'rotation_speed': random.uniform(-0.3, 0.3)
            }
            nebulae.append(nebula)
        return nebulae
    
    def _create_asteroids(self) -> List[Dict]:
        """Create moving asteroids for dynamic background."""
        asteroids = []
        for _ in range(12):
            asteroid = {
                'x': random.uniform(-100, self.screen_width + 100),
                'y': random.uniform(-100, self.screen_height + 100),
                'size': random.uniform(3, 12),
                'speed': random.uniform(8, 25),
                'direction': random.uniform(0, 2 * math.pi),
                'rotation': random.uniform(0, 360),
                'rotation_speed': random.uniform(-2, 2),
                'brightness': random.uniform(0.4, 0.8)
            }
            asteroids.append(asteroid)
        return asteroids
    
    def _create_cosmic_dust(self) -> List[Dict]:
        """Create cosmic dust particles for atmosphere."""
        dust = []
        for _ in range(200):
            particle = {
                'x': random.uniform(0, self.screen_width),
                'y': random.uniform(0, self.screen_height),
                'size': random.uniform(0.5, 2),
                'speed': random.uniform(2, 8),
                'direction': random.uniform(0, 2 * math.pi),
                'brightness': random.uniform(0.1, 0.4),
                'twinkle_speed': random.uniform(1, 3)
            }
            dust.append(particle)
        return dust
    
    def _create_energy_streams(self) -> List[Dict]:
        """Create flowing energy streams in background."""
        streams = []
        for _ in range(6):
            stream = {
                'points': [],
                'color': random.choice([
                    (100, 200, 255),
                    (255, 100, 200),
                    (100, 255, 180),
                    (200, 100, 255)
                ]),
                'width': random.uniform(2, 6),
                'speed': random.uniform(20, 40),
                'alpha': random.uniform(0.3, 0.7),
                'wave_amplitude': random.uniform(10, 30),
                'wave_frequency': random.uniform(0.01, 0.03)
            }
            for i in range(20):
                stream['points'].append({
                    'x': -50 + i * 15,
                    'y': random.uniform(0, self.screen_height),
                    'offset': i * 0.1
                })
            streams.append(stream)
        return streams
    
    def _create_space_debris(self) -> List[Dict]:
        """Create floating space debris for added realism."""
        debris = []
        for _ in range(15):
            piece = {
                'x': random.uniform(0, self.screen_width),
                'y': random.uniform(0, self.screen_height),
                'size': random.uniform(1, 4),
                'speed': random.uniform(3, 12),
                'direction': random.uniform(0, 2 * math.pi),
                'rotation': random.uniform(0, 360),
                'rotation_speed': random.uniform(-1, 1),
                'shape': random.choice(['rect', 'triangle', 'circle']),
                'color': random.choice([
                    (100, 100, 120),
                    (120, 100, 100),
                    (100, 120, 100),
                    (80, 80, 100)
                ])
            }
            debris.append(piece)
        return debris
    
    def handle_input(self, event) -> Optional[str]:
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_LEFT, pygame.K_a]:
                self._navigate(-1)
                return 'ship_changed'
            
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                self._navigate(1)
                return 'ship_changed'
            
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                return 'ship_selected'
            
            elif event.key == pygame.K_ESCAPE:
                return 'back_to_menu'
        
        return None
    def _navigate(self, direction: int):
        """Navigate ship selection with smooth transitions and effects."""
        if not self.ships:
            return
        
        old_index = self.selected_index
        self.selected_index = (self.selected_index + direction) % len(self.ships)
        
        if self.selected_index != old_index:
            self.target_index = self.selected_index
            self.transition_time = 0.0
            self._trigger_selection_effects()
    
    def _trigger_selection_effects(self):
        """Trigger smooth visual effects for selection change."""
        
        self.camera_shake['intensity'] = 2.0
        self._spawn_orbital_particles()
        self._create_selection_trace()
    
    def _spawn_orbital_particles(self):
        """Spawn particles that orbit around the selected ship."""
        for i in range(8):
            angle = (i / 8) * 2 * math.pi
            
            # Get selected ship color
            selected_ship = self.get_selected_ship()
            color = selected_ship['color'] if selected_ship else self.colors['primary']
            
            particle = {
                'x': self.main_ship_x,
                'y': self.main_ship_y,
                'orbit_angle': angle,
                'orbit_radius': 100 + random.uniform(-20, 20),
                'size': random.uniform(2, 4),
                'life': random.uniform(2, 4),
                'max_life': 4,
                'alpha': 255,
                'color': color
            }
            self.selection_particles.append(particle)
    
    def _create_selection_trace(self):
        """Create flowing energy trace effect."""
        selected_ship = self.get_selected_ship()
        color = selected_ship['color'] if selected_ship else self.colors['energy_bright']
        
        # Create trace from previous ship to current ship
        points = []
        for i in range(10):
            t = i / 9.0
            x = self.main_ship_x + math.sin(t * math.pi * 2) * 50
            y = self.main_ship_y + math.cos(t * math.pi * 4) * 20
            points.append({'x': x, 'y': y})
        
        trace = {
            'points': points,
            'color': color,
            'life': 1.5,
            'max_life': 1.5,
            'alpha': 150        }
        self.energy_traces.append(trace)
    
    def _spawn_selection_particles(self):
        """Spawn particles for selection change."""
        center_x = self.settings.SCREEN_WIDTH // 2
        center_y = self.settings.SCREEN_HEIGHT // 2 - 50
        
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            
            selected_ship = self.get_selected_ship()
            if not selected_ship:
                color = (100, 180, 255)  # Default color
            else:
                color = selected_ship['color']
            
            particle = {
                'x': center_x,
                'y': center_y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': random.uniform(0.5, 1.5),
                'max_life': 1.5,
                'color': color,
                'size': random.randint(2, 4),
                'alpha': 255
            }
            self.particles.append(particle)
    
    def get_selected_ship(self) -> Optional[Dict]:
        """Get currently selected ship."""        
        if self.ships and 0 <= self.selected_index < len(self.ships):
            return self.ships[self.selected_index]
        return None
    
    def update(self, dt: int):
        dt_sec = dt * 0.001
        self.time += dt_sec
        
        # Smooth selection interpolation with spring physics
        selection_diff = self.target_index - self.smooth_selection
        self.selection_velocity += selection_diff * 12.0 * dt_sec  # Spring constant
        self.selection_velocity *= 0.85  # Damping
        self.smooth_selection += self.selection_velocity * dt_sec
        # Transition animations with easing
        if self.transition_time < self.transition_duration:
            self.transition_time += dt_sec
            progress = min(1.0, self.transition_time / self.transition_duration)
            
            # UI emergence animations
            self.ui_animations['title_appear'] = easeOutElastic(min(1.0, progress * 1.5))
            self.ui_animations['stats_slide'] = easeInOutCubic(max(0.0, (progress - 0.2) * 1.25))
            self.ui_animations['ship_cards_emerge'] = easeInOutQuart(max(0.0, (progress - 0.4) * 1.67))
            self.ui_animations['hologram_strength'] = easeInOutCubic(progress)
        else:
            # Ensure animations are fully completed
            self.ui_animations['title_appear'] = 1.0
            self.ui_animations['stats_slide'] = 1.0
            self.ui_animations['ship_cards_emerge'] = 1.0
            self.ui_animations['hologram_strength'] = 1.0
        
        # Ship hover animations with smooth scaling
        target_scale = 1.1 if abs(self.smooth_selection - self.selected_index) < 0.1 else 1.0
        scale_diff = target_scale - self.ship_hover_state['scale']
        self.ship_hover_state['scale'] += scale_diff * 8.0 * dt_sec
        
        # Gentle ship rotation
        self.ship_hover_state['rotation'] += dt_sec * 15.0
        
        # Pulsing glow effect
        self.ship_hover_state['glow'] = 0.5 + 0.3 * math.sin(self.time * 2.0)
        
        # Smooth camera shake for impact
        self.camera_shake['intensity'] *= 0.9
        self.camera_shake['x'] = math.sin(self.time * 50) * self.camera_shake['intensity']
        self.camera_shake['y'] = math.cos(self.time * 37) * self.camera_shake['intensity']
        
        # Update floating particles for atmosphere
        self._update_floating_particles(dt_sec)
        self._update_selection_particles(dt_sec)
        self._update_energy_traces(dt_sec)
        
        # Update floating elements
        for element in self.floating_elements:
            element['x'] += element['speed'] * dt_sec
            element['y'] += math.sin(self.time + element['x'] * 0.01) * element['speed'] * dt_sec * 0.5
            
            # Wrap around screen
            if element['x'] > self.screen_width + 50:
                element['x'] = -50
                element['y'] = random.uniform(0, self.screen_height)
        
        # Update advanced space background elements
        self._update_nebulae(dt_sec)
        self._update_asteroids(dt_sec)
        self._update_cosmic_dust(dt_sec)
        self._update_energy_streams(dt_sec)
        self._update_space_debris(dt_sec)
        
        # Update background stars
        for star in self.background_stars:
            parallax_speed = star['drift_speed'] * (1 + star['size'] * 0.2)
            wave_influence = math.sin(self.cosmic_wave + star['y'] * 0.01) * 0.5
            star['x'] += parallax_speed * dt_sec * (15 + wave_influence)
            
            if star['x'] > self.screen_width + 10:
                star['x'] = -10
                star['y'] = random.randint(0, self.screen_height)
        
        for scan_line in self.scan_lines:
            pulse_speed = scan_line['speed'] * (1 + self.energy_pulse * 0.3)
            scan_line['y'] += pulse_speed * dt_sec * 20
            if scan_line['y'] > self.screen_height:
                scan_line['y'] = -2
                scan_line['opacity'] = random.uniform(0.05, 0.15)
                
        # DEBUG: Show current ship stats
        if hasattr(self, '_debug_counter'):
            self._debug_counter += dt
            if self._debug_counter > 2000:  # Every 2 seconds
                self.debug_ship_stats(self.selected_index)
                self._debug_counter = 0
        else:
            self._debug_counter = 0
        
    
    def _update_particle(self, particle: Dict, dt: float) -> bool:
        """Update particle and return True if still alive."""
        particle['x'] += particle['vx'] * dt
        particle['y'] += particle['vy'] * dt
        particle['life'] -= dt
        
        # Fade out
        particle['alpha'] = int(255 * (particle['life'] / particle['max_life']))
        
        return particle['life'] > 0
    def _update_energy_particle(self, particle: Dict, dt: float) -> bool:
        """Update energy particle with trail effects."""
        # Store previous position for trail
        if 'trail' not in particle:
            particle['trail'] = []
        
        # Add current position to trail
        particle['trail'].append((particle['x'], particle['y']))
        
        # Limit trail length
        if len(particle['trail']) > 8:
            particle['trail'].pop(0)
        
        # Update position
        particle['x'] += particle['vx'] * dt
        particle['y'] += particle['vy'] * dt
        particle['life'] -= dt
        
        # Apply gravity-like effect for ship energy particles
        if particle.get('type') == 'ship_energy':
            # Slight attraction to ship center
            center_x = self.screen_width // 2
            center_y = self.screen_height // 2 - 50
            
            dx = center_x - particle['x']
            dy = center_y - particle['y']
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                force = 50 / (distance + 1)
                particle['vx'] += (dx / distance) * force * dt
                particle['vy'] += (dy / distance) * force * dt
        
        # Fade out
        particle['alpha'] = int(255 * (particle['life'] / particle['max_life']))
        
        return particle['life'] > 0
    
    def _spawn_energy_particle(self):
        """Spawn ambient energy particle."""
        particle = {
            'x': random.uniform(-50, self.screen_width + 50),
            'y': random.uniform(-50, self.screen_height + 50),
            'vx': random.uniform(-30, 30),
            'vy': random.uniform(-30, 30),
            'life': random.uniform(2.0, 4.0),
            'max_life': 4.0,
            'color': random.choice([
                self.colors['energy_blue'],
                self.colors['energy_cyan'],
                self.colors['energy_purple']
            ]),
            'size': random.randint(1, 3),
            'alpha': random.randint(100, 200),
            'type': 'ambient',
            'trail': []        }
        self.energy_particles.append(particle)
    
    def _create_particle_burst(self):
        """Create dramatic particle burst effect."""
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            particle = {
                'x': center_x,
                'y': center_y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': random.uniform(1.0, 2.0),
                'max_life': 2.0,
                'color': random.choice([
                    self.colors['energy_blue'],
                    self.colors['energy_cyan'],
                    self.colors['accent']
                ]),
                'size': random.randint(2, 6),
                'alpha': 255,
                'type': 'burst'
            }
            self.particles.append(particle)

    def _update_nebulae(self, dt: float):
        """Update animated nebula movement and effects."""
        for nebula in self.nebulae:
            # Drift movement
            nebula['x'] += nebula['drift_speed'] * dt
            nebula['y'] += math.sin(self.time + nebula['x'] * 0.001) * nebula['drift_speed'] * dt * 0.3
            
            # Rotation
            nebula['rotation'] += nebula['rotation_speed'] * dt * 10
            
            # Wrap around screen
            if nebula['x'] > self.screen_width + 200:
                nebula['x'] = -400
                nebula['y'] = random.uniform(-200, self.screen_height + 200)

    def _update_asteroids(self, dt: float):
        """Update asteroid movement and rotation."""
        for asteroid in self.asteroids:
            # Movement
            asteroid['x'] += math.cos(asteroid['direction']) * asteroid['speed'] * dt
            asteroid['y'] += math.sin(asteroid['direction']) * asteroid['speed'] * dt
            
            # Rotation
            asteroid['rotation'] += asteroid['rotation_speed'] * dt * 10
            
            # Wrap around screen
            if asteroid['x'] > self.screen_width + 100:
                asteroid['x'] = -100
            elif asteroid['x'] < -100:
                asteroid['x'] = self.screen_width + 100
            if asteroid['y'] > self.screen_height + 100:
                asteroid['y'] = -100
            elif asteroid['y'] < -100:
                asteroid['y'] = self.screen_height + 100

    def _update_cosmic_dust(self, dt: float):
        """Update cosmic dust particle movement."""
        for dust in self.cosmic_dust:
            # Movement
            dust['x'] += math.cos(dust['direction']) * dust['speed'] * dt
            dust['y'] += math.sin(dust['direction']) * dust['speed'] * dt
            
            # Twinkling effect
            dust['brightness'] = 0.1 + 0.3 * (0.5 + 0.5 * math.sin(self.time * dust['twinkle_speed']))
            
            # Wrap around screen
            if dust['x'] > self.screen_width:
                dust['x'] = 0
            elif dust['x'] < 0:
                dust['x'] = self.screen_width
            if dust['y'] > self.screen_height:
                dust['y'] = 0
            elif dust['y'] < 0:
                dust['y'] = self.screen_height

    def _update_energy_streams(self, dt: float):
        """Update flowing energy stream movement."""
        for stream in self.energy_streams:
            # Move all points in the stream
            for point in stream['points']:
                point['x'] += stream['speed'] * dt
                # Add wave motion
                wave_offset = math.sin(self.time * stream['wave_frequency'] + point['offset']) * stream['wave_amplitude']
                point['y'] += wave_offset * dt * 0.1
                
                # Reset point when it goes off screen
                if point['x'] > self.screen_width + 50:
                    point['x'] = -50
                    point['y'] = random.uniform(0, self.screen_height)

    def _update_space_debris(self, dt: float):
        """Update space debris movement and rotation."""
        for debris in self.space_debris:
            # Movement
            debris['x'] += math.cos(debris['direction']) * debris['speed'] * dt
            debris['y'] += math.sin(debris['direction']) * debris['speed'] * dt
            
            # Rotation
            debris['rotation'] += debris['rotation_speed'] * dt * 10
            
            # Wrap around screen
            if debris['x'] > self.screen_width + 10:
                debris['x'] = -10
            elif debris['x'] < -10:
                debris['x'] = self.screen_width + 10
            if debris['y'] > self.screen_height + 10:
                debris['y'] = -10
            elif debris['y'] < -10:
                debris['y'] = self.screen_height + 10

    def _render_nebulae(self, surface: pygame.Surface):
        """Render animated nebula clouds."""
        for nebula in self.nebulae:
            # Create nebula surface with alpha
            nebula_surface = pygame.Surface((nebula['size'] * 2, nebula['size'] * 2), pygame.SRCALPHA)
            
            # Draw gradient circle with cosmic wave distortion
            center = (nebula['size'], nebula['size'])
            for radius in range(int(nebula['size']), 0, -5):
                alpha = int(nebula['color'][3] * (radius / nebula['size']) * 0.5)
                color = (*nebula['color'][:3], alpha)
                
                # Apply cosmic wave distortion
                wave_offset = math.sin(self.cosmic_wave + nebula['x'] * 0.001) * 3
                distorted_center = (center[0] + wave_offset, center[1])
                
                if alpha > 0:
                    pygame.draw.circle(nebula_surface, color, distorted_center, radius)
            
            # Rotate and blit
            rotated = pygame.transform.rotate(nebula_surface, nebula['rotation'])
            rect = rotated.get_rect(center=(nebula['x'], nebula['y']))
            surface.blit(rotated, rect)

    def _render_asteroids(self, surface: pygame.Surface):
        """Render moving asteroids."""
        for asteroid in self.asteroids:
            # Create irregular polygon shape
            points = []
            num_points = 6
            for i in range(num_points):
                angle = (i / num_points) * 2 * math.pi + math.radians(asteroid['rotation'])
                radius = asteroid['size'] * random.uniform(0.8, 1.2)
                x = asteroid['x'] + math.cos(angle) * radius
                y = asteroid['y'] + math.sin(angle) * radius
                points.append((x, y))
            
            color_val = int(asteroid['brightness'] * 255)
            color = (color_val, color_val, color_val)
            
            if len(points) >= 3:
                pygame.draw.polygon(surface, color, points)

    def _render_cosmic_dust(self, surface: pygame.Surface):
        """Render twinkling cosmic dust particles."""
        for dust in self.cosmic_dust:
            alpha = int(dust['brightness'] * 255)
            color = (200, 200, 255, alpha)
            
            # Create small surface for the dust particle
            dust_surface = pygame.Surface((int(dust['size'] * 2), int(dust['size'] * 2)), pygame.SRCALPHA)
            pygame.draw.circle(dust_surface, color, 
                             (int(dust['size']), int(dust['size'])), 
                             int(dust['size']))
            
            surface.blit(dust_surface, (dust['x'] - dust['size'], dust['y'] - dust['size']))

    def _render_energy_streams(self, surface: pygame.Surface):
        """Render flowing energy streams."""
        for stream in self.energy_streams:
            if len(stream['points']) >= 2:
                # Create smooth curved line
                points = [(point['x'], point['y']) for point in stream['points'] 
                         if 0 <= point['x'] <= self.screen_width]
                
                if len(points) >= 2:
                    # Draw stream with glow effect
                    for width in range(int(stream['width'] * 3), 0, -1):
                        alpha = int(stream['alpha'] * 255 * (1 - width / (stream['width'] * 3)) * 0.3)
                        color = (*stream['color'], alpha)
                        
                        # Create surface for alpha drawing
                        if alpha > 0:
                            stream_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                            pygame.draw.lines(stream_surface, color, False, points, width)
                            surface.blit(stream_surface, (0, 0))

    def _render_space_debris(self, surface: pygame.Surface):
        """Render floating space debris."""
        for debris in self.space_debris:
            color = debris['color']
            size = debris['size']
            
            if debris['shape'] == 'rect':
                rect = pygame.Rect(debris['x'] - size, debris['y'] - size, size * 2, size * 2)
                pygame.draw.rect(surface, color, rect)
            elif debris['shape'] == 'triangle':
                points = [
                    (debris['x'], debris['y'] - size),
                    (debris['x'] - size, debris['y'] + size),
                    (debris['x'] + size, debris['y'] + size)
                ]
                pygame.draw.polygon(surface, color, points)
            else:  # circle                
                pygame.draw.circle(surface, color, (int(debris['x']), int(debris['y'])), int(size))
                
    def render(self, surface: pygame.Surface):
        """Render professional starfighter selection interface."""
        # Create main render surface
        render_surface = pygame.Surface((self.screen_width, self.screen_height))
        
        self._render_professional_background(render_surface)
        self._render_grid_overlay(render_surface)
        self._render_professional_header(render_surface)
        self._render_main_content_area(render_surface)
        self._render_modern_ship_display(render_surface)
        self._render_professional_stats_panel(render_surface)
        self._render_professional_carousel(render_surface)
        self._render_professional_controls(render_surface)
        self._render_selection_indicators(render_surface)
        
        surface.blit(render_surface, (0, 0))
    
    def _render_cinematic_background(self, surface: pygame.Surface):
        """Render deep space cinematic background with cosmic wave effects."""
        # Deep space gradient background
        for y in range(self.screen_height):
            gradient_factor = y / self.screen_height
            wave_offset = math.sin((y * 0.01) + (self.time * 2.0)) * 10
            
            # Multi-layer cosmic colors
            r = int(self.colors['bg_deep'][0] + gradient_factor * 10 + wave_offset * 0.5)
            g = int(self.colors['bg_deep'][1] + gradient_factor * 15 + wave_offset * 0.3)
            b = int(self.colors['bg_deep'][2] + gradient_factor * 25 + wave_offset * 0.8)
            
            # Clamp values
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            pygame.draw.line(surface, (r, g, b), (0, y), (self.screen_width, y))
        
        # Render background stars
        for star in self.background_stars:
            star_alpha = int(star['brightness'] * 255)
            star_color = (*self.colors['text_secondary'], star_alpha)
            
            twinkle = math.sin(self.time * star['twinkle_speed'] + star['phase']) * 0.3 + 0.7
            star_size = max(1, int(star['size'] * twinkle))
            
            if star_size > 1:
                pygame.draw.circle(surface, star_color[:3], 
                                 (int(star['x']), int(star['y'])), star_size)
            else:
                surface.set_at((int(star['x']), int(star['y'])), star_color[:3])
        
        # Energy nebula effects
        nebula_time = self.time * 0.5
        for i in range(3):
            nebula_x = int(self.screen_width * (0.2 + i * 0.3))
            nebula_y = int(self.screen_height * 0.5)
            nebula_radius = int(200 + math.sin(nebula_time + i) * 50)
            
            # Create nebula surface for alpha blending
            nebula_surface = pygame.Surface((nebula_radius * 2, nebula_radius * 2), pygame.SRCALPHA)
            
            # Multiple energy rings for depth
            for ring in range(5):
                ring_radius = int(nebula_radius * (0.3 + ring * 0.15))
                ring_alpha = int(20 - ring * 3)
                color = (*self.colors['energy_blue'], ring_alpha)
                pygame.draw.circle(nebula_surface, color, 
                                 (nebula_radius, nebula_radius), ring_radius)
            
            surface.blit(nebula_surface, (nebula_x - nebula_radius, nebula_y - nebula_radius))

    def _render_atmosphere_particles(self, surface: pygame.Surface):
        """Render floating atmospheric particles for depth and ambiance."""
        for particle in self.floating_particles:
            # Calculate particle properties
            life_factor = particle['life']
            alpha = int(255 * life_factor * particle['alpha'])
            
            # Dynamic size based on life and distance
            size = particle['size'] * (0.5 + life_factor * 0.5)
            
            # Color based on particle type
            if particle['type'] == 'energy':
                base_color = self.colors['energy_cyan']
            elif particle['type'] == 'dust':
                base_color = self.colors['text_muted']
            else:  # ambient
                base_color = self.colors['energy_soft']
            
            # Create particle surface for alpha blending
            particle_size = int(size * 2)
            if particle_size > 0:
                particle_surface = pygame.Surface((particle_size, particle_size), pygame.SRCALPHA)
                
                # Soft glow effect
                for ring in range(3):
                    ring_radius = max(1, int(size * (1.0 - ring * 0.3)))
                    ring_alpha = int(alpha * (0.8 - ring * 0.2))
                    color = (*base_color, ring_alpha)
                    
                    if ring_radius > 0:
                        pygame.draw.circle(particle_surface, color, 
                                         (particle_size // 2, particle_size // 2), ring_radius)
                
                # Position with drift effect
                drift_x = math.sin(self.time * particle['drift_speed'] + particle['phase']) * 10
                drift_y = math.cos(self.time * particle['drift_speed'] * 0.7 + particle['phase']) * 5
                
                x = int(particle['x'] + drift_x)
                y = int(particle['y'] + drift_y)
                
                surface.blit(particle_surface, (x - particle_size // 2, y - particle_size // 2))    
                
    def _render_animated_title(self, surface: pygame.Surface):
        """Render the main title with smooth emergence animation and energy effects."""
        # Title emergence animation
        appear_progress = self.ui_animations['title_appear']
        
        # Force title to always show
        if appear_progress <= 0:
            appear_progress = 1.0
        
        if appear_progress < 1.0:
            # Elastic emergence from nothing
            scale = easeOutElastic(appear_progress)
            alpha = int(255 * easeInOutCubic(appear_progress))
        else:
            # Breathing effect when fully appeared
            breathing = math.sin(self.time * 2.0) * 0.05 + 1.0
            scale = breathing
            alpha = 255
        
        # Create title text
        title_text = "STARFIGHTER SELECTION"
        text_surface = self.title_font.render(title_text, True, self.colors['text_primary'])
        
        # Apply scaling
        if scale != 1.0:
            scaled_width = int(text_surface.get_width() * scale)
            scaled_height = int(text_surface.get_height() * scale)
            if scaled_width > 0 and scaled_height > 0:
                text_surface = pygame.transform.scale(text_surface, (scaled_width, scaled_height))
          # Position centered at top with optimized spacing
        text_rect = text_surface.get_rect()
        text_x = (self.screen_width - text_rect.width) // 2
        text_y = 20  # Slightly higher for better balance
        
        # Energy glow behind title
        if appear_progress > 0.3:
            glow_alpha = int(80 * (appear_progress - 0.3) / 0.7)
            glow_surface = pygame.Surface((text_rect.width + 40, text_rect.height + 20), pygame.SRCALPHA)
            
            # Multi-layer glow
            for glow_ring in range(4):
                glow_radius = 15 + glow_ring * 5
                glow_color = (*self.colors['energy_blue'], max(0, glow_alpha - glow_ring * 15))
                
                for offset_x in range(-glow_radius, glow_radius + 1, 4):
                    for offset_y in range(-glow_radius, glow_radius + 1, 4):
                        distance = math.sqrt(offset_x * offset_x + offset_y * offset_y)
                        if distance <= glow_radius:
                            glow_intensity = int(glow_color[3] * (1.0 - distance / glow_radius))
                            if glow_intensity > 0:
                                glow_pos = (20 + offset_x + text_rect.width // 2, 
                                           10 + offset_y + text_rect.height // 2)
                                if (0 <= glow_pos[0] < glow_surface.get_width() and 
                                    0 <= glow_pos[1] < glow_surface.get_height()):
                                    glow_surface.set_at(glow_pos, (*glow_color[:3], glow_intensity))
            
            surface.blit(glow_surface, (text_x - 20, text_y - 10))
        
        # Apply alpha to title
        if alpha < 255:
            alpha_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
            alpha_surface.fill((255, 255, 255, alpha))
            text_surface.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # Render main title
        surface.blit(text_surface, (text_x, text_y))
        
        # Energy scan lines across title
        if appear_progress > 0.5:
            scan_progress = (self.time * 3.0) % 2.0
            if scan_progress < 1.0:
                scan_x = int(text_x + text_rect.width * scan_progress)
                scan_color = (*self.colors['energy_cyan'], 120)
                
                for scan_width in range(1, 4):
                    if scan_x + scan_width < text_x + text_rect.width:
                        pygame.draw.line(surface, scan_color, 
                                       (scan_x + scan_width, text_y), 
                                       (scan_x + scan_width, text_y + text_rect.height))
    
    def _render_modern_background(self, surface: pygame.Surface):
        """Render advanced animated space background with cosmic effects."""
        # Multi-layer gradient with cosmic wave effects
        for y in range(self.screen_height):
            progress = y / self.screen_height
            
            # Dynamic color mixing with cosmic wave animation
            wave = math.sin(self.cosmic_wave * 0.5 + progress * 2) * 0.15
            nebula_influence = math.sin(self.time * 0.3 + progress * 4) * 0.1
            
            r = int(self.colors['background'][0] * (1 + wave + nebula_influence))
            g = int(self.colors['background'][1] * (1 + wave * 0.8 + nebula_influence * 1.2))
            b = int(self.colors['background'][2] * (1 + wave * 1.2 + nebula_influence * 0.8))
            
            # Add cosmic depth with enhanced variations
            depth_mod = math.sin(progress * math.pi + self.cosmic_wave * 0.2) * 8
            r = max(0, min(255, r + depth_mod))
            g = max(0, min(255, g + depth_mod))
            b = max(0, min(255, b + depth_mod))
            
            pygame.draw.line(surface, (int(r), int(g), int(b)), (0, y), (self.screen_width, y))
        
        # Render advanced space elements in layers
        self._render_nebulae(surface)
        self._render_energy_streams(surface) 
        self._render_layered_stars(surface)
        self._render_cosmic_dust(surface)
        self._render_asteroids(surface)
        self._render_space_debris(surface)
    
    def _render_layered_stars(self, surface: pygame.Surface):
        """Render stars in multiple layers for depth."""
        for i, star in enumerate(self.background_stars):
            # Different layers based on index
            layer = i % 3
            base_brightness = star['brightness']
            
            if layer == 0:  # Background stars
                twinkle = base_brightness * (0.3 + 0.2 * math.sin(self.time * star['twinkle_speed']))
                size = max(1, star['size'] - 1)
            elif layer == 1:  # Mid-ground stars  
                twinkle = base_brightness * (0.5 + 0.3 * math.sin(self.time * star['twinkle_speed'] * 1.5))
                size = star['size']
            else:  # Foreground stars
                twinkle = base_brightness * (0.7 + 0.3 * math.sin(self.time * star['twinkle_speed'] * 2))
                size = star['size'] + 1
            
            brightness = int(255 * twinkle)
            
            # Add color tint based on layer
            if layer == 0:
                color = (brightness, brightness, brightness)
            elif layer == 1:
                color = (brightness, brightness, min(255, brightness + 20))
            else:
                color = (min(255, brightness + 10), min(255, brightness + 15), brightness)
            
            # Render with glow effect for larger stars
            if size > 2:
                # Glow
                glow_surface = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                glow_color = (*color, 30)
                pygame.draw.circle(glow_surface, glow_color, (size * 2, size * 2), size * 2)
                surface.blit(glow_surface, (star['x'] - size * 2, star['y'] - size * 2))
            
            # Main star
            pygame.draw.circle(surface, color, (int(star['x']), int(star['y'])), size)
    
    def _render_floating_elements(self, surface: pygame.Surface):
        """Render floating UI elements for ambient effect."""
        for element in self.floating_elements:
            alpha = int(255 * element['opacity'] * (0.5 + 0.5 * math.sin(self.time * 2)))
            color = (*element['color'], alpha)
            
            # Create subtle floating geometric shapes
            size = int(element['size'])
            x, y = int(element['x']), int(element['y'])
            
            # Different shapes for variety
            shape_type = hash(str(element['x'])) % 3
            
            if shape_type == 0:  # Circle
                if alpha > 20:
                    glow_surf = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, color, (size * 3 // 2, size * 3 // 2), size)
                    surface.blit(glow_surf, (x - size, y - size))
            elif shape_type == 1:  # Square
                if alpha > 20:
                    glow_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surf, color, (0, 0, size * 2, size * 2), 0, size // 2)
                    surface.blit(glow_surf, (x - size, y - size))
            else:  # Triangle
                if alpha > 20:
                    points = [
                        (x, y - size),
                        (x - size, y + size),
                        (x + size, y + size)
                    ]
                    glow_surf = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
                    pygame.draw.polygon(glow_surf, color, [(p[0] - x + size, p[1] - y + size) for p in points])
                    surface.blit(glow_surf, (x - size, y - size))
    
    def _render_star_field(self, surface: pygame.Surface):
        """Render animated star field background."""
        for star in self.background_stars:
            twinkle = star['brightness'] * (0.7 + 0.3 * math.sin(self.time * star['twinkle_speed']))
            brightness = int(255 * twinkle)
            color = (brightness, brightness, brightness)
            
            if star['size'] == 1:
                pygame.draw.circle(surface, color, (int(star['x']), int(star['y'])), 1)
            else:
                pygame.draw.circle(surface, color, (int(star['x']), int(star['y'])), star['size'])
    
    def _render_header(self, surface: pygame.Surface):
        """Render header section."""
        # Title
        title_text = "STARFIGHTER SELECTION"
        title_surface = self.title_font.render(title_text, True, self.colors['primary'])
        title_x = self.settings.SCREEN_WIDTH // 2 - title_surface.get_width() // 2
        surface.blit(title_surface, (title_x, 30))
        
        # Subtitle with ship count
        if self.ships:
            subtitle_text = f"Choose your vessel • {len(self.ships)} fighters available"
            subtitle_surface = self.info_font.render(subtitle_text, True, self.colors['text_secondary'])
            subtitle_x = self.settings.SCREEN_WIDTH // 2 - subtitle_surface.get_width() // 2
            surface.blit(subtitle_surface, (subtitle_x, 75))
    
    def _render_ship_display(self, surface: pygame.Surface):
        """Render main ship display area."""
        if not self.ships:
            return
        
        ship = self.get_selected_ship()
        if not ship:
            return
        
        # Display area
        display_x = self.settings.SCREEN_WIDTH // 2 - self.ship_display_width // 2
        display_y = 120
        
        # Background panel
        panel_surface = pygame.Surface((self.ship_display_width, self.ship_display_height), pygame.SRCALPHA)
        panel_surface.fill((*self.colors['panel'], 100))
        
        # Animated border
        border_color = (*ship['color'], int(255 * self.selection_alpha))
        pygame.draw.rect(panel_surface, border_color, (0, 0, self.ship_display_width, self.ship_display_height), 3, 15)
        
        surface.blit(panel_surface, (display_x, display_y))
        
        # Ship sprite
        sprite_x = display_x + self.ship_display_width // 2
        sprite_y = display_y + self.ship_display_height // 2
        if ship['sprite']:
            # Rotation effect
            sprite_size = int(120 * (1 + self.hover_scale * 0.1))
            scaled_sprite = pygame.transform.scale(ship['sprite'], (sprite_size, sprite_size))
            
            # Apply 3D rotation with perspective distortion
            y_rotation = self.ship_rotation_3d['y']
            x_tilt = self.ship_rotation_3d['x']
            
            # Create perspective scaling effect
            perspective_scale_x = math.cos(math.radians(y_rotation * 0.5)) * 0.3 + 0.7
            perspective_scale_y = math.cos(math.radians(x_tilt * 0.5)) * 0.1 + 0.9
            
            # Apply perspective transformation
            persp_width = int(sprite_size * perspective_scale_x)
            persp_height = int(sprite_size * perspective_scale_y)
            
            if persp_width > 0 and persp_height > 0:
                perspective_sprite = pygame.transform.scale(scaled_sprite, (persp_width, persp_height))
                
                # Add hologram distortion effect
                if self.hologram_distortion > 0:
                    distorted_sprite = self._apply_hologram_distortion(perspective_sprite)
                    final_sprite = pygame.transform.rotate(distorted_sprite, y_rotation + self.rotation * 0.3)
                else:
                    final_sprite = pygame.transform.rotate(perspective_sprite, y_rotation + self.rotation * 0.3)
                
                # Multi-layer glow effect with energy pulse
                glow_layers = 3
                for layer in range(glow_layers):
                    glow_size = int(sprite_size * (1.3 + 0.3 * self.pulse + layer * 0.1))
                    glow_alpha = int(40 * self.energy_pulse / (layer + 1))
                    
                    if glow_alpha > 5:
                        glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
                        glow_color = (*ship['color'], glow_alpha)
                        pygame.draw.circle(glow_surface, glow_color, (glow_size // 2, glow_size // 2), glow_size // 2)
                        
                        # Add energy ring effect
                        if layer == 0:
                            ring_radius = glow_size // 2 - 5
                            ring_color = (*ship['color'], int(glow_alpha * 1.5))
                            pygame.draw.circle(glow_surface, ring_color, (glow_size // 2, glow_size // 2), ring_radius, 2)
                        
                        glow_rect = glow_surface.get_rect(center=(sprite_x, sprite_y))
                        surface.blit(glow_surface, glow_rect, special_flags=pygame.BLEND_ADD)
                
                # Render main sprite with energy aura
                sprite_rect = final_sprite.get_rect(center=(sprite_x, sprite_y))
                
                # Add scan line effect over ship
                self._render_ship_scan_lines(surface, sprite_rect, ship['color'])
                
                surface.blit(final_sprite, sprite_rect)
                
                # Add energy particles around ship
                self._spawn_ship_energy_particles(sprite_x, sprite_y, ship['color'])
        else:
            # Placeholder
            placeholder_size = 120
            placeholder_color = ship['color']
            pygame.draw.rect(surface, placeholder_color, 
                           (sprite_x - placeholder_size // 2, sprite_y - placeholder_size // 2, 
                            placeholder_size, placeholder_size), 0, 20)
        
        # Ship name
        name_surface = self.header_font.render(ship['name'], True, ship['color'])
        name_x = sprite_x - name_surface.get_width() // 2
        name_y = display_y + self.ship_display_height + 10
        surface.blit(name_surface, (name_x, name_y))
        
        # Ship class and tier
        class_text = f"{ship['class']} Class • {ship['tier']} Tier"
        class_surface = self.info_font.render(class_text, True, self.colors['text_secondary'])
        class_x = sprite_x - class_surface.get_width() // 2
        class_y = name_y + 35
        surface.blit(class_surface, (class_x, class_y))
    
    def _render_hero_ship_display(self, surface: pygame.Surface):
        """Render the main ship display with smooth scaling and effects."""
        if not self.ships:
            return
        
        current_ship = self.ships[self.selected_index]
        ship_sprite = self.resource_manager.get_sprite(current_ship['sprite_key'])
        
        if not ship_sprite:
            return
        
        # Smooth ship scaling with optimized hover effect
        base_scale = 2.5  # Reduced for better proportions in layout
        hover_scale = self.ship_hover_state['scale']
        final_scale = base_scale * hover_scale
        
        # Scale ship sprite smoothly
        ship_width = int(ship_sprite.get_width() * final_scale)
        ship_height = int(ship_sprite.get_height() * final_scale)
        scaled_ship = pygame.transform.smoothscale(ship_sprite, (ship_width, ship_height))
        
        # Gentle rotation
        rotation_angle = self.ship_hover_state['rotation']
        rotated_ship = pygame.transform.rotate(scaled_ship, rotation_angle)
        
        # Ship position with smooth animation
        ship_rect = rotated_ship.get_rect(center=(self.main_ship_x, self.main_ship_y))
        
        # Multi-layer glow effect
        glow_intensity = self.ship_hover_state['glow']
        glow_size = max(ship_width, ship_height) + 40
        
        # Outer energy ring
        ring_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        ring_alpha = int(glow_intensity * 60)
        pygame.draw.circle(ring_surface, (*self.colors['primary'], ring_alpha),
                          (glow_size, glow_size), glow_size, 3)
        
        # Inner energy ring
        inner_ring_size = glow_size - 20
        pygame.draw.circle(ring_surface, (*self.colors['secondary'], ring_alpha // 2),
                          (glow_size, glow_size), inner_ring_size, 2)
        
        ring_rect = ring_surface.get_rect(center=(self.main_ship_x, self.main_ship_y))
        surface.blit(ring_surface, ring_rect)
        
        # Ship glow backdrop
        glow_surface = pygame.Surface((ship_width + 60, ship_height + 60), pygame.SRCALPHA)
        glow_alpha = int(glow_intensity * 40)
        pygame.draw.ellipse(glow_surface, (*current_ship['color'], glow_alpha),
                           (0, 0, ship_width + 60, ship_height + 60))
        
        glow_rect = glow_surface.get_rect(center=(self.main_ship_x, self.main_ship_y))
        surface.blit(glow_surface, glow_rect)
        
        # Main ship
        surface.blit(rotated_ship, ship_rect)
        
        # Ship name and class
        ship_name = current_ship['name']
        ship_class = current_ship['class'].title()
        
        name_surface = self.ship_font.render(ship_name, True, current_ship['color'])
        name_rect = name_surface.get_rect(center=(self.main_ship_x, self.main_ship_y + ship_height // 2 + 40))
        surface.blit(name_surface, name_rect)
        
        class_surface = self.info_font.render(f"{ship_class} Class • Advanced Grade", True, self.colors['text_secondary'])
        class_rect = class_surface.get_rect(center=(self.main_ship_x, self.main_ship_y + ship_height // 2 + 65))
        surface.blit(class_surface, class_rect)      
    
    def _render_smooth_stats_panel(self, surface: pygame.Surface):
        """Render enhanced ship stats panel with better positioning and visual design."""
        slide_progress = self.ui_animations['stats_slide']
        
        # Ensure the stats panel shows even if animation hasn't started yet
        if slide_progress <= 0:
            slide_progress = 1.0  # Force it to show
            
        current_ship = self.ships[self.selected_index] if self.ships else None
        if not current_ship:
            return
        
        # Better panel sizing and positioning - optimized proportions
        panel_width = 280
        panel_height = 380
        panel_x = 40
        panel_y = 180
        
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)

        panel_surface.fill((*self.colors['bg_deep'], int(slide_progress * 200)))
        
        glass_overlay = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        glass_overlay.fill((*self.colors['glass_primary'][:3], int(slide_progress * self.colors['glass_primary'][3])))
        panel_surface.blit(glass_overlay, (0, 0))
       
        border_color = (*current_ship['color'], int(slide_progress * 180))
        pygame.draw.rect(panel_surface, border_color, (0, 0, panel_width, panel_height), 2)
        
        corner_size = 15
        corner_color = (*self.colors['energy_blue'], int(slide_progress * 200))
        for corner in [(0, 0), (panel_width - corner_size, 0), 
                      (0, panel_height - corner_size), (panel_width - corner_size, panel_height - corner_size)]:
            pygame.draw.rect(panel_surface, corner_color, (*corner, corner_size, corner_size))
        
        surface.blit(panel_surface, (panel_x, panel_y))
        
        content_alpha = int(slide_progress * 255)
        
        # Ship name header with enhanced styling
        name_y = panel_y + 20
        name_surface = self.header_font.render(current_ship['name'], True, current_ship['color'])
        name_surface.set_alpha(content_alpha)
        name_x = panel_x + (panel_width - name_surface.get_width()) // 2
        surface.blit(name_surface, (name_x, name_y))
        
        # Ship class and description
        class_y = name_y + 35
        class_text = f"{current_ship['class'].upper()} CLASS"
        class_surface = self.info_font.render(class_text, True, self.colors['text_accent'])
        class_surface.set_alpha(content_alpha)
        class_x = panel_x + (panel_width - class_surface.get_width()) // 2
        surface.blit(class_surface, (class_x, class_y))
        
        # Description with word wrapping
        desc_y = class_y + 25
        description = current_ship.get('description', 'Advanced starfighter')
        desc_lines = self._wrap_text(description, self.small_font, panel_width - 30)
        for i, line in enumerate(desc_lines[:2]):  # Max 2 lines to save space
            line_surface = self.small_font.render(line, True, self.colors['text_secondary'])
            line_surface.set_alpha(content_alpha)
            surface.blit(line_surface, (panel_x + 15, desc_y + i * 16))
        
        # Combat effectiveness header
        header_y = desc_y + len(desc_lines[:2]) * 16 + 20
        header_surface = self.stat_font.render("COMBAT EFFECTIVENESS", True, self.colors['energy_cyan'])
        header_surface.set_alpha(content_alpha)
        surface.blit(header_surface, (panel_x + 15, header_y))
        
        # Rating stars with enhanced animation
        rating = current_ship['rating']
        stars_y = header_y + 25
        self._render_smooth_rating_stars(surface, int(panel_x + 15), stars_y, rating, content_alpha, slide_progress)
        
        # Technical specifications
        specs_y = stars_y + 40
        specs_surface = self.info_font.render("TECHNICAL SPECIFICATIONS", True, self.colors['energy_blue'])
        specs_surface.set_alpha(content_alpha)
        surface.blit(specs_surface, (panel_x + 15, specs_y))
        
        # Enhanced stat bars with optimized spacing
        stats = ['speed', 'firepower', 'armor', 'shields']
        stat_names = ['VELOCITY', 'FIREPOWER', 'ARMOR', 'SHIELDS']
        stat_colors = [self.colors['energy_cyan'], self.colors['accent'], 
                      self.colors['energy_blue'], self.colors['energy_bright']]
        
        for i, (stat, name, color) in enumerate(zip(stats, stat_names, stat_colors)):
            stat_y = specs_y + 30 + i * 35  # Better spacing for smaller panel
            value = current_ship.get('stats', {}).get(stat, 50)
            max_value = 200  # Maximum stat value for scaling
            percentage = min(100, (value / max_value) * 100)
            self._render_smooth_stat_bar(surface, int(panel_x + 15), stat_y, name, percentage, color, content_alpha, slide_progress)
    

    def _render_smooth_rating_stars(self, surface: pygame.Surface, x: int, y: int, rating: float, alpha: int, progress: float = 1.0):
        """Render animated rating stars with enhanced effects."""
        star_size = 24
        star_spacing = 30
        
        for i in range(5):
            star_x = x + i * star_spacing
            
            # Determine fill amount for this star
            star_fill = max(0, min(1, rating - i))
            
            # Star emergence animation
            star_progress = max(0, min(1, (progress * 5) - i))
            current_star_size = int(star_size * star_progress)
            
            if current_star_size > 0:
                # Create star surface
                star_surface = pygame.Surface((current_star_size * 2, current_star_size * 2), pygame.SRCALPHA)
                
                # Star outline
                outline_color = (*self.colors['text_secondary'], alpha)
                self._draw_star(star_surface, current_star_size, current_star_size, current_star_size, outline_color)
                
                # Star fill with animated progress
                if star_fill > 0:
                    fill_alpha = int(alpha * star_fill)
                    fill_color = (*self.colors['energy_bright'], fill_alpha)
                    fill_size = int(current_star_size * star_fill)
                    self._draw_star(star_surface, current_star_size, current_star_size, fill_size, fill_color, filled=True)
                
                surface.blit(star_surface, (star_x - current_star_size, y - current_star_size))
    
    def _draw_star(self, surface: pygame.Surface, center_x: int, center_y: int, size: int, color: tuple, filled: bool = False):
        """Draw a star shape."""
        points = []
        for i in range(10):
            angle = (i * math.pi / 5) - (math.pi / 2)
            radius = size if i % 2 == 0 else size * 0.5
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append((x, y))        
        if filled:
            pygame.draw.polygon(surface, color, points)
        else:
            pygame.draw.polygon(surface, color, points, 2)      
            
    def _render_smooth_stat_bar(self, surface: pygame.Surface, x: int, y: int, 
                               name: str, value: int, color: tuple[int, int, int], alpha: int, progress: float = 1.0):
        """Render enhanced animated stat bar with progress animation."""
        bar_width = 200
        bar_height = 10
        
        # Stat name
        name_surface = self.small_font.render(name, True, self.colors['text_primary'])
        name_surface.set_alpha(alpha)
        surface.blit(name_surface, (x, y))
        
        # Value text with percentage
        value_text = f"{value}%"
        value_surface = self.small_font.render(value_text, True, color)
        value_surface.set_alpha(alpha)
        surface.blit(value_surface, (x + bar_width + 10, y))
        
        # Bar background with depth
        bar_y = y + 18
        bg_surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
        
        # Multi-layer background for depth
        bg_surface.fill((*self.colors['bg_mid'][:3], alpha // 2))
        pygame.draw.rect(bg_surface, (*self.colors['text_muted'][:3], alpha // 4), 
                        (0, 0, bar_width, bar_height))
        pygame.draw.rect(bg_surface, (*color[:3], alpha // 6), 
                        (0, 0, bar_width, bar_height), 1)
        
        surface.blit(bg_surface, (x, bar_y))
        
        fill_progress = min(1.0, (value / 100.0) * progress)
        fill_width = int(bar_width * fill_progress)
        
        if fill_width > 0:
            fill_surface = pygame.Surface((fill_width, bar_height), pygame.SRCALPHA)
            
            for i in range(fill_width):
                gradient_factor = i / fill_width
                
                r = int(color[0] * (0.6 + 0.4 * gradient_factor))
                g = int(color[1] * (0.6 + 0.4 * gradient_factor))
                b = int(color[2] * (0.6 + 0.4 * gradient_factor))
                
                gradient_color = (r, g, b, alpha)
                pygame.draw.line(fill_surface, gradient_color, (i, 0), (i, bar_height))
            
            surface.blit(fill_surface, (x, bar_y))
            
            highlight_pos = int(fill_width * (0.8 + 0.2 * math.sin(self.time * 4.0)))
            if highlight_pos < fill_width - 2:
                highlight_color = (*self.colors['energy_bright'][:3], int(alpha * 0.8))
                pygame.draw.line(surface, highlight_color, 
                               (x + highlight_pos, bar_y), (x + highlight_pos, bar_y + bar_height), 2)
        
        if value >= 90:
            glow_alpha = int(alpha * 0.3 * (0.5 + 0.5 * math.sin(self.time * 3.0)))
            glow_surface = pygame.Surface((bar_width + 6, bar_height + 6), pygame.SRCALPHA)
            glow_surface.fill((*color[:3], glow_alpha))
            surface.blit(glow_surface, (x - 3, bar_y - 3))
            
    def _render_ship_carousel(self, surface: pygame.Surface):
        """Render bottom ship carousel with smooth selection and circular previews."""
        emerge_progress = self.ui_animations['ship_cards_emerge']
        
        if len(self.ships) == 0:
            return
        
        if emerge_progress <= 0:
            emerge_progress = 1.0  # Force it to show
        
        carousel_y = self.carousel_y + (1 - emerge_progress) * 100
        
        carousel_bg = pygame.Surface((self.screen_width, self.carousel_height + 40), pygame.SRCALPHA)
        
        panel_color = (*self.colors['bg_elevated'], int(emerge_progress * 140))
        carousel_bg.fill(panel_color)
        
        border_color = (*self.colors['energy_blue'], int(emerge_progress * 80))
        pygame.draw.rect(carousel_bg, border_color, (0, 0, self.screen_width, self.carousel_height + 40), 2)
        
        surface.blit(carousel_bg, (0, carousel_y - 20))
        visible_ships = min(len(self.ships), 7)
        ship_spacing = self.ship_icon_size + 30
        
        # Calculate proper total width and center positioning
        if visible_ships > 0:
            total_width = visible_ships * ship_spacing - (ship_spacing - self.ship_icon_size)
            start_x = (self.screen_width - total_width) // 2
        else:
            start_x = self.screen_width // 2
        
        for i in range(visible_ships):
            if visible_ships >= len(self.ships):
                ship_index = i
            else:
                offset = i - visible_ships // 2
                ship_index = (self.selected_index + offset) % len(self.ships)
            
            ship = self.ships[ship_index]
            icon_x = start_x + i * ship_spacing
            icon_y = carousel_y + 20
            center_x = icon_x + self.ship_icon_size // 2
            center_y = icon_y + self.ship_icon_size // 2
            
            # Selection highlight
            selection_distance = abs(self.smooth_selection - ship_index)
            if selection_distance > len(self.ships) / 2:
                selection_distance = len(self.ships) - selection_distance
            
            highlight_intensity = max(0, 1 - selection_distance)
            is_selected = ship_index == self.selected_index
            
            # Circular background
            circle_radius = self.ship_icon_size // 2 + 5
            
            # Outer glow ring for selected ship
            if is_selected:
                for ring in range(3):
                    ring_radius = circle_radius + 8 + ring * 3
                    ring_alpha = int(emerge_progress * (100 - ring * 25))
                    ring_color = (*ship['color'], ring_alpha)
                    pygame.draw.circle(surface, ring_color, (center_x, center_y), ring_radius, 2)
            
            # Main circular background
            bg_alpha = int(emerge_progress * (180 if is_selected else 120))
            bg_color = (*self.colors['bg_surface'], bg_alpha)
            pygame.draw.circle(surface, bg_color, (center_x, center_y), circle_radius)
            
            # Circular border
            border_alpha = int(emerge_progress * (255 if is_selected else 180))
            border_color = (*ship['color'], border_alpha)
            border_width = 3 if is_selected else 1
            pygame.draw.circle(surface, border_color, (center_x, center_y), circle_radius, border_width)
            
            # Ship sprite with proper scaling
            ship_sprite = self.resource_manager.get_sprite(ship['sprite_key'])
            if ship_sprite:
                # Scale based on selection
                base_scale = 0.6 if is_selected else 0.5
                scale = base_scale + highlight_intensity * 0.1
                icon_size = int(self.ship_icon_size * scale)
                
                if icon_size > 0:
                    scaled_sprite = pygame.transform.smoothscale(ship_sprite, (icon_size, icon_size))
                    
                    # Rotation for selected ship
                    if is_selected:
                        rotation_angle = self.time * 30  # Slow rotation
                        scaled_sprite = pygame.transform.rotate(scaled_sprite, rotation_angle)
                    
                    sprite_rect = scaled_sprite.get_rect(center=(center_x, center_y))
                    surface.blit(scaled_sprite, sprite_rect)
            else:
                # Colored circle
                fallback_radius = int(circle_radius * 0.6)
                pygame.draw.circle(surface, ship['color'], (center_x, center_y), fallback_radius)
            
            # Ship name below icon
            if is_selected or highlight_intensity > 0.3:
                name_alpha = int(emerge_progress * 255 * (1.0 if is_selected else highlight_intensity))
                name_surface = self.small_font.render(ship['name'], True, self.colors['text_primary'])
                name_rect = name_surface.get_rect(center=(center_x, icon_y + self.ship_icon_size + 15))
                
                # Apply alpha blending properly
                if name_alpha < 255:
                    alpha_surface = pygame.Surface(name_surface.get_size(), pygame.SRCALPHA)
                    alpha_surface.fill((255, 255, 255, name_alpha))
                    name_surface.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                
                surface.blit(name_surface, name_rect)
    
    def _render_professional_background(self, surface: pygame.Surface):
        """Render clean gradient background with subtle depth."""
        for y in range(self.screen_height):
            progress = y / self.screen_height
            
            deep_color = self.colors['bg_deep']
            mid_color = self.colors['bg_mid']
            
            r = int(deep_color[0] + (mid_color[0] - deep_color[0]) * progress)
            g = int(deep_color[1] + (mid_color[1] - deep_color[1]) * progress)
            b = int(deep_color[2] + (mid_color[2] - deep_color[2]) * progress)
            
            pygame.draw.line(surface, (r, g, b), (0, y), (self.screen_width, y))
        
        # Vignette effect
        vignette_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        center_x, center_y = self.screen_width // 2, self.screen_height // 2
        max_distance = math.sqrt(center_x**2 + center_y**2)
        
        for y in range(0, self.screen_height, 4):
            for x in range(0, self.screen_width, 4):
                distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                vignette_strength = min(80, int(80 * (distance / max_distance) ** 2))
                if vignette_strength > 0:
                    pygame.draw.rect(vignette_surface, (0, 0, 0, vignette_strength), (x, y, 4, 4))
        
        surface.blit(vignette_surface, (0, 0))

    def _render_grid_overlay(self, surface: pygame.Surface):
        """Render subtle grid pattern for professional tech look."""
        grid_size = 32
        grid_alpha = 15
        grid_color = (*self.colors['text_muted'], grid_alpha)
        
        # Vertical lines
        for x in range(0, self.screen_width, grid_size):
            line_surface = pygame.Surface((1, self.screen_height), pygame.SRCALPHA)
            line_surface.fill(grid_color)
            surface.blit(line_surface, (x, 0))
        
        # Horizontal lines
        for y in range(0, self.screen_height, grid_size):
            line_surface = pygame.Surface((self.screen_width, 1), pygame.SRCALPHA)
            line_surface.fill(grid_color)
            surface.blit(line_surface, (0, y))

    def _render_professional_header(self, surface: pygame.Surface):
        """Render clean, professional header."""
        # Main title
        title_text = "STARFIGHTER SELECTION"
        title_surface = self.title_font.render(title_text, True, self.colors['text_primary'])
        title_x = (self.screen_width - title_surface.get_width()) // 2
        title_y = 40
        
        # Title background panel
        panel_width = title_surface.get_width() + 80
        panel_height = title_surface.get_height() + 30
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = title_y - 15
        
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((*self.colors['bg_card'], 120))
        
        # Border accent
        pygame.draw.rect(panel_surface, self.colors['primary'], (0, 0, panel_width, panel_height), 2, 8)
        
        surface.blit(panel_surface, (panel_x, panel_y))
        surface.blit(title_surface, (title_x, title_y))
        
        # Subtitle
        if self.ships:
            subtitle_text = f"Select your combat vessel • {len(self.ships)} available"
            subtitle_surface = self.info_font.render(subtitle_text, True, self.colors['text_secondary'])
            subtitle_x = (self.screen_width - subtitle_surface.get_width()) // 2
            subtitle_y = title_y + title_surface.get_height() + 20
            surface.blit(subtitle_surface, (subtitle_x, subtitle_y))

    def _render_main_content_area(self, surface: pygame.Surface):
        """Render main content area with proper spacing."""
        # Content area background
        content_y = 140
        content_height = self.screen_height - content_y - 120
        content_margin = 40
        
        content_surface = pygame.Surface((self.screen_width - content_margin * 2, content_height), pygame.SRCALPHA)
        content_surface.fill((*self.colors['bg_surface'], 40))
        
        # Subtle border
        pygame.draw.rect(content_surface, (*self.colors['primary'], 60), 
                        (0, 0, content_surface.get_width(), content_surface.get_height()), 1, 12)
        
        surface.blit(content_surface, (content_margin, content_y))

    def _render_modern_ship_display(self, surface: pygame.Surface):
        """Render main ship display with modern card design."""
        if not self.ships:
            return
        
        current_ship = self.ships[self.selected_index]
        ship_sprite = self.resource_manager.get_sprite(current_ship['sprite_key'])
        
        if not ship_sprite:
            return
        
        # Ship display area (center-right)
        display_width = 400
        display_height = 300
        display_x = self.screen_width // 2 + 50
        display_y = self.screen_height // 2 - display_height // 2
        
        card_surface = pygame.Surface((display_width, display_height), pygame.SRCALPHA)
        
        card_surface.fill((*self.colors['bg_elevated'], 180))
        
        glass_overlay = pygame.Surface((display_width, display_height), pygame.SRCALPHA)
        glass_color = self.colors.get('glass_neutral', (20, 30, 40))
        
        if isinstance(glass_color, (list, tuple)) and len(glass_color) >= 3:
            # Use only RGB values, not RGBA
            glass_rgb = glass_color[:3]
            glass_overlay.fill((*glass_rgb, 80))
        else:
            # Fallback to a safe default color
            glass_overlay.fill((20, 30, 40, 80))
        
        card_surface.blit(glass_overlay, (0, 0))
        
        pygame.draw.rect(card_surface, self.colors['primary'], (0, 0, display_width, display_height), 2, 16)
        
        # Corner accents
        accent_size = 20
        accent_color = self.colors.get('secondary', (126, 211, 33))
        for corner in [(8, 8), (display_width - accent_size - 8, 8), 
                    (8, display_height - accent_size - 8), 
                    (display_width - accent_size - 8, display_height - accent_size - 8)]:
            corner_surface = pygame.Surface((accent_size, accent_size), pygame.SRCALPHA)
            corner_surface.fill((*accent_color, 200))
            card_surface.blit(corner_surface, corner)
        
        surface.blit(card_surface, (display_x, display_y))
        
        # Ship sprite with proper scaling
        sprite_scale = 2.2
        scaled_width = int(ship_sprite.get_width() * sprite_scale)
        scaled_height = int(ship_sprite.get_height() * sprite_scale)
        scaled_sprite = pygame.transform.smoothscale(ship_sprite, (scaled_width, scaled_height))
        
        # Subtle rotation animation
        rotation_angle = math.sin(self.time * 0.5) * 5
        rotated_sprite = pygame.transform.rotate(scaled_sprite, rotation_angle)
        
        sprite_rect = rotated_sprite.get_rect(center=(display_x + display_width // 2, display_y + display_height // 2 - 20))
        surface.blit(rotated_sprite, sprite_rect)
        
        # Ship name and class with actual tier
        name_surface = self.ship_font.render(current_ship['name'], True, current_ship['color'])
        name_x = display_x + (display_width - name_surface.get_width()) // 2
        name_y = display_y + display_height - 60
        surface.blit(name_surface, (name_x, name_y))
        
        actual_tier = current_ship.get('tier', 'Standard').upper()
        class_text = f"{current_ship['class'].upper()} • {actual_tier}"
        class_surface = self.info_font.render(class_text, True, self.colors['text_accent'])
        class_x = display_x + (display_width - class_surface.get_width()) // 2
        class_y = name_y + 25
        surface.blit(class_surface, (class_x, class_y))

    def _render_professional_stats_panel(self, surface: pygame.Surface):
        """Render clean, professional stats panel."""
        if not self.ships:
            return
        
        current_ship = self.ships[self.selected_index]
        
        # Stats panel (left side)
        panel_width = 320
        panel_height = 380
        panel_x = 60
        panel_y = self.screen_height // 2 - panel_height // 2
        
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((*self.colors['bg_elevated'], 200))
        
        glass_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        glass_color = self.colors.get('glass_neutral', (20, 30, 40))
        
        # Handle both RGB and RGBA color formats safely
        if isinstance(glass_color, (list, tuple)):
            if len(glass_color) >= 4:
                glass_surface.fill(glass_color)
            elif len(glass_color) >= 3:
                # RGB only, add alpha
                glass_surface.fill((*glass_color[:3], 100))
            else:
                glass_surface.fill((20, 30, 40, 100))
        else:
            glass_surface.fill((20, 30, 40, 100))
        
        panel_surface.blit(glass_surface, (0, 0))
        
        pygame.draw.rect(panel_surface, self.colors['primary'], (0, 0, panel_width, panel_height), 2, 16)
        
        surface.blit(panel_surface, (panel_x, panel_y))
        
        # Header
        header_text = "VESSEL SPECIFICATIONS"
        header_surface = self.header_font.render(header_text, True, self.colors['text_primary'])
        header_x = panel_x + (panel_width - header_surface.get_width()) // 2
        header_y = panel_y + 25
        surface.blit(header_surface, (header_x, header_y))
        
        # Ship class and tier - USE ACTUAL CALCULATED TIER
        actual_tier = current_ship.get('tier', 'Standard').upper()
        class_text = f"{current_ship['class'].upper()} • {actual_tier} GRADE"
        class_surface = self.stat_font.render(class_text, True, self.colors['text_accent'])
        class_x = panel_x + (panel_width - class_surface.get_width()) // 2
        class_y = header_y + 35
        surface.blit(class_surface, (class_x, class_y))
        
        # Rating stars
        rating_x = panel_x + 40
        rating_y = class_y + 40
        ship_rating = current_ship.get('rating', 4.0)
        self._render_modern_rating_stars(surface, rating_x, rating_y, ship_rating)
        
        stats_y = rating_y + 40
        stats = ['speed', 'firepower', 'armor', 'shields']
        stat_names = ['VELOCITY', 'FIREPOWER', 'ARMOR', 'SHIELDS']
        stat_colors = [self.colors['primary'], self.colors['secondary'], 
                    self.colors['accent'], self.colors['info']]
        
        for i, (stat, name, color) in enumerate(zip(stats, stat_names, stat_colors)):
            stat_y = stats_y + 40 + i * 45
            raw_value = current_ship.get('stats', {}).get(stat, 50)
            # Pass the raw value - the stat bar will normalize it internally
            self._render_modern_stat_bar(surface, rating_x, stat_y, name, raw_value, color, panel_width - 40)

    def _render_modern_rating_stars(self, surface: pygame.Surface, x: int, y: int, rating: float):
        """Render modern rating stars with proper 5-star filling."""
        star_size = 16
        star_spacing = 22
        
        for i in range(5):
            star_x = x + i * star_spacing
            star_progress = rating - i  # How much of this star should be filled
            
            # Determine star state
            if star_progress >= 1.0:
                # Fully filled star
                color = self.colors['secondary']
                filled = True
            elif star_progress > 0.0:
                # Partially filled star
                color = self.colors['secondary']
                filled = True
            else:
                # Empty star
                color = self.colors['text_muted']
                filled = False
            
            self._draw_modern_star(surface, star_x + star_size // 2, y + star_size // 2, star_size, color, filled)

    def _draw_modern_star(self, surface: pygame.Surface, center_x: int, center_y: int, size: int, color: tuple, filled: bool = False):
        """Draw a modern star shape."""
        points = []
        for i in range(10):
            angle = i * math.pi / 5
            radius = size if i % 2 == 0 else size * 0.4
            x = center_x + radius * math.cos(angle - math.pi / 2)
            y = center_y + radius * math.sin(angle - math.pi / 2)        
            points.append((x, y))
        
        if filled:
            pygame.draw.polygon(surface, color, points)
        else:
            pygame.draw.polygon(surface, color, points, 2)

    def _render_modern_stat_bar(self, surface: pygame.Surface, x: int, y: int, name: str, value: int, color: tuple, max_width: int):
        """Render modern stat bar with clean design and proper bounds."""
        name_surface = self.small_font.render(name, True, self.colors['text_secondary'])
        
        min_stat = 20
        max_stat = 200
        normalized_percentage = min(100, max(0, ((value - min_stat) / (max_stat - min_stat)) * 100))
        
        value_text = f"{normalized_percentage:.0f}%"
        value_surface = self.small_font.render(value_text, True, self.colors['text_primary'])
        
        # Reserve space for name, value text, and margins
        reserved_space = value_surface.get_width() + 20  # Value text + margin
        safe_bar_width = max_width - reserved_space
        safe_bar_width = max(100, min(safe_bar_width, 180))  # Ensure reasonable bounds
        
        # Render stat name
        surface.blit(name_surface, (x, y))
        
        value_x = x + safe_bar_width + 10
        surface.blit(value_surface, (value_x, y))
        
        # Bar background
        bar_y = y + 18
        bar_height = 8
        
        bg_surface = pygame.Surface((safe_bar_width, bar_height), pygame.SRCALPHA)
        bg_surface.fill((*self.colors['bg_mid'], 150))
        pygame.draw.rect(bg_surface, (*self.colors['text_muted'], 100), (0, 0, safe_bar_width, bar_height), 0, 4)
        surface.blit(bg_surface, (x, bar_y))
        
        fill_percentage = normalized_percentage / 100
        fill_width = int(safe_bar_width * fill_percentage)
        
        if fill_width > 0:
            fill_surface = pygame.Surface((fill_width, bar_height), pygame.SRCALPHA)
            fill_surface.fill(color)
            pygame.draw.rect(fill_surface, color, (0, 0, fill_width, bar_height), 0, 4)
            surface.blit(fill_surface, (x, bar_y))
            
            if normalized_percentage >= 80:
                glow_alpha = int(40 * (0.5 + 0.5 * math.sin(self.time * 3.0)))
                glow_surface = pygame.Surface((fill_width + 4, bar_height + 4), pygame.SRCALPHA)
                glow_surface.fill((*color, glow_alpha))
                surface.blit(glow_surface, (x - 2, bar_y - 2))

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> list[str]:
        """Wrap text to fit within specified width."""
        if not text or not font or max_width <= 0:
            return [text] if text else []
        
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            # Test if adding this word would exceed the width
            test_line = current_line + (" " if current_line else "") + word
            try:
                test_width = font.size(test_line)[0]
            except:
                # If font.size fails, use a safe fallback
                test_width = len(test_line) * 8  # Rough character width estimation
            
            if test_width <= max_width:
                current_line = test_line
            else:
                # Start a new line
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        # Add the last line
        if current_line:
            lines.append(current_line)
        
        return lines if lines else [text]

    ########### THe following methods are just placeholder for now. I'll implement the functionality later ##########################
    def _update_floating_particles(self, dt: float):
        """Update floating particles."""
        pass
    
    def _update_selection_particles(self, dt: float):
        """Update selection particles."""
        pass
    
    def _update_energy_traces(self, dt: float):
        """Update energy traces."""
        pass
    
    def _apply_hologram_distortion(self, sprite: pygame.Surface) -> pygame.Surface:
        """Apply hologram distortion."""
        return sprite
    
    def _render_ship_scan_lines(self, surface: pygame.Surface, rect: pygame.Rect, color: Tuple[int, int, int]):
        """Render scan lines."""
        pass
    def _spawn_ship_energy_particles(self, x: int, y: int, color: Tuple[int, int, int]):
        """Spawn energy particles."""
        pass
    
    ############### End of placeholder methods ##########################

    def _render_professional_carousel(self, surface: pygame.Surface):
        """Render clean ship selection carousel."""
        if not self.ships:
            return
        
        # Carousel area
        carousel_height = 100
        carousel_y = self.screen_height - carousel_height - 40
        
        # Background panel
        panel_surface = pygame.Surface((self.screen_width, carousel_height), pygame.SRCALPHA)
        panel_surface.fill((*self.colors['bg_elevated'], 180))
        
        glass_surface = pygame.Surface((self.screen_width, carousel_height), pygame.SRCALPHA)
        glass_color = self.colors.get('glass_neutral', (20, 30, 40))
        
        if isinstance(glass_color, (list, tuple)):
            if len(glass_color) >= 4:
                glass_surface.fill(glass_color)
            elif len(glass_color) >= 3:
                glass_surface.fill((*glass_color[:3], 60))
            else:
                glass_surface.fill((20, 30, 40, 60))
        else:
            glass_surface.fill((20, 30, 40, 60))
        
        panel_surface.blit(glass_surface, (0, 0))
        
        pygame.draw.line(panel_surface, self.colors['primary'], (0, 0), (self.screen_width, 0), 2)
    
        surface.blit(panel_surface, (0, carousel_y))
        
        # Ship icons
        visible_ships = min(len(self.ships), 7)
        icon_size = 60
        icon_spacing = 90
        
        if visible_ships > 0:
            total_width = visible_ships * icon_spacing - (icon_spacing - icon_size)
            start_x = (self.screen_width - total_width) // 2
            
            for i in range(visible_ships):
                if visible_ships >= len(self.ships):
                    ship_index = i
                else:
                    offset = i - visible_ships // 2
                    ship_index = (self.selected_index + offset) % len(self.ships)
                
                ship = self.ships[ship_index]
                icon_x = start_x + i * icon_spacing
                icon_y = carousel_y + 20
                
                is_selected = ship_index == self.selected_index
                
                # Icon background
                icon_bg_size = icon_size + (12 if is_selected else 8)
                bg_color = self.colors['primary'] if is_selected else self.colors['bg_card']
                
                bg_surface = pygame.Surface((icon_bg_size, icon_bg_size), pygame.SRCALPHA)
                bg_surface.fill((*bg_color, 200 if is_selected else 120))
                pygame.draw.rect(bg_surface, bg_color, (0, 0, icon_bg_size, icon_bg_size), 2, 8)
                
                bg_x = icon_x + (icon_size - icon_bg_size) // 2
                bg_y = icon_y + (icon_size - icon_bg_size) // 2
                surface.blit(bg_surface, (bg_x, bg_y))
                
                # Ship sprite
                ship_sprite = self.resource_manager.get_sprite(ship['sprite_key'])
                if ship_sprite:
                    scale = 0.8 if is_selected else 0.6
                    scaled_size = int(icon_size * scale)
                    scaled_sprite = pygame.transform.smoothscale(ship_sprite, (scaled_size, scaled_size))
                    
                    sprite_rect = scaled_sprite.get_rect(center=(icon_x + icon_size // 2, icon_y + icon_size // 2))
                    surface.blit(scaled_sprite, sprite_rect)
                
                # Ship name
                if is_selected:
                    name_surface = self.small_font.render(ship['name'], True, self.colors['text_primary'])
                    name_x = icon_x + (icon_size - name_surface.get_width()) // 2
                    name_y = icon_y + icon_size + 8
                    surface.blit(name_surface, (name_x, name_y))

    def _render_professional_controls(self, surface: pygame.Surface):
        """Render clean control hints."""
        controls_y = self.screen_height - 30
        
        controls = [
            ("<- ->", "NAVIGATE"),
            ("ENTER", "SELECT"),
            ("ESC", "BACK")
        ]
        
        control_spacing = 160
        total_width = len(controls) * control_spacing - control_spacing + 120
        start_x = (self.screen_width - total_width) // 2
        
        for i, (key, action) in enumerate(controls):
            x = start_x + i * control_spacing
            
            key_surface = self.small_font.render(key, True, self.colors['text_primary'])
            
            if key == "<- ->" and key_surface.get_width() < 20:
                key = "LEFT/RIGHT"
                key_surface = self.small_font.render(key, True, self.colors['text_primary'])
            
            key_width = key_surface.get_width() + 16
            key_height = key_surface.get_height() + 8
            
            # Key background
            key_bg = pygame.Surface((key_width, key_height), pygame.SRCALPHA)
            key_bg.fill((*self.colors['bg_elevated'][:3], 200))
            pygame.draw.rect(key_bg, self.colors['primary'][:3], (0, 0, key_width, key_height), 1, 4)
            
            surface.blit(key_bg, (x, controls_y - key_height // 2))
            surface.blit(key_surface, (x + 8, controls_y - key_surface.get_height() // 2))
            
            # Action text
            action_surface = self.small_font.render(action, True, self.colors['text_secondary'])
            action_x = x + key_width + 8
            surface.blit(action_surface, (action_x, controls_y - action_surface.get_height() // 2))

    def _render_selection_indicators(self, surface: pygame.Surface):
        """Render subtle selection indicators."""
        if not self.ships:
            return
        # Selection counter
        counter_text = f"{self.selected_index + 1} / {len(self.ships)}"
        counter_surface = self.info_font.render(counter_text, True, self.colors['text_accent'])
        surface.blit(counter_surface, (self.screen_width - 120, 20))
        
        # Current selection indicator (top-right corner)
        current_ship = self.ships[self.selected_index]
        status_text = f"SELECTED: {current_ship['name'].upper()}"
        status_surface = self.small_font.render(status_text, True, self.colors['text_muted'])
        surface.blit(status_surface, (20, self.screen_height - 20))