import pygame
import math
from typing import Optional, TYPE_CHECKING
from entities.projectile import Projectile
from game.settings import Settings
from utils.debug_utils import debug_print

if TYPE_CHECKING:
    from effects.particle_system import ParticleSystem
    from game.game_engine import GameEngine

class Player:
    def __init__(self, x: int, y: int, sprite: pygame.Surface, settings: Settings, ship_type: str = 'ship1'):
        self.x = float(x)
        self.y = float(y)
        self.sprite = sprite
        self.settings = settings
        self.ship_type = ship_type
        
        # Smooth movement with friction
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.acceleration = 0.8
        self.deceleration = 0.85
        self.friction = 0.85
        self.max_speed = float(settings.PLAYER_SPEED)
        
        # Player stats
        self.max_health = settings.PLAYER_HEALTH
        self.health = self.max_health
        self.alive = True
        
        # Enhanced shooting system
        self.last_shot = 0
        self.base_fire_rate = 150
        self.fire_rate = self.base_fire_rate
        self.bullet_type = 'basic'
        self.bullet_spread = 0
        self.bullet_damage = 20
        
        # Power-ups with visual feedback
        self.has_rapid_fire = False
        self.has_shield = False
        self.has_spread_shot = False
        self.has_laser = False
        self.rapid_fire_end_time = 0
        self.shield_end_time = 0
        self.spread_shot_end_time = 0
        self.laser_end_time = 0
        
        # Visual effects
        self.engine_timer = 0.0
        self.shield_pulse = 0.0
        self.hit_flash_timer = 0
        
        # particle system reference
        self.particle_system_ref: Optional['ParticleSystem'] = None
        
        self.game_engine_ref: Optional['GameEngine'] = None
        
        # Ship-specific stats
        self.apply_ship_stats()
        
        # Rectangle for collision
        self.rect = pygame.Rect(int(self.x), int(self.y), sprite.get_width(), sprite.get_height())
        
        # Movement bounds
        self.min_x = 0
        self.max_x = settings.SCREEN_WIDTH - sprite.get_width()
        self.min_y = 0
        self.max_y = settings.SCREEN_HEIGHT - sprite.get_height()
        
        # Damage attribute for collision damage
        self.damage = 25  # Damage dealt to enemies on collision
        
    def get_current_time(self) -> int:
        """Get current time that respects pause state."""
        if self.game_engine_ref:
            return self.game_engine_ref.get_game_time()
        else:
            # Fallback to real time if no game engine reference
            return pygame.time.get_ticks()
    
    def apply_ship_stats(self):
        """Apply different stats based on ship type"""
        # Expanded ship stats for all your ships
        ship_stats = {
            # Ship_1_ Series (Fighters)
            'ship1': {'speed_mult': 1.3, 'fire_rate_mult': 1.0, 'health_mult': 0.8},
            'ship2': {'speed_mult': 1.2, 'fire_rate_mult': 1.2, 'health_mult': 0.9},
            'ship3': {'speed_mult': 1.1, 'fire_rate_mult': 1.1, 'health_mult': 1.0},
            'ship4': {'speed_mult': 1.4, 'fire_rate_mult': 0.9, 'health_mult': 0.8},
            'ship5': {'speed_mult': 1.2, 'fire_rate_mult': 1.3, 'health_mult': 0.9},
            
            # Ship_2_ Series (Cruisers)
            'ship6': {'speed_mult': 1.0, 'fire_rate_mult': 1.1, 'health_mult': 1.2},
            'ship7': {'speed_mult': 0.9, 'fire_rate_mult': 1.0, 'health_mult': 1.4},
            'ship8': {'speed_mult': 1.1, 'fire_rate_mult': 1.2, 'health_mult': 1.1},
            'ship9': {'speed_mult': 0.8, 'fire_rate_mult': 0.9, 'health_mult': 1.5},
            'ship10': {'speed_mult': 1.2, 'fire_rate_mult': 1.4, 'health_mult': 1.0},
            
            # Custom Ships (Large sprites)
            'ship11': {'speed_mult': 1.1, 'fire_rate_mult': 1.3, 'health_mult': 1.2},
            'ship12': {'speed_mult': 1.3, 'fire_rate_mult': 1.1, 'health_mult': 1.1},
            'ship13': {'speed_mult': 0.9, 'fire_rate_mult': 1.5, 'health_mult': 1.3},
            'ship14': {'speed_mult': 0.8, 'fire_rate_mult': 1.2, 'health_mult': 1.6},
            'ship15': {'speed_mult': 1.2, 'fire_rate_mult': 1.4, 'health_mult': 1.0},
            'ship16': {'speed_mult': 1.0, 'fire_rate_mult': 1.6, 'health_mult': 1.2},
            'ship17': {'speed_mult': 1.4, 'fire_rate_mult': 1.0, 'health_mult': 1.0},
            'ship18': {'speed_mult': 1.1, 'fire_rate_mult': 1.3, 'health_mult': 1.4},
        }
        
        stats = ship_stats.get(self.ship_type, ship_stats['ship1'])
        self.max_speed *= stats['speed_mult']
        self.base_fire_rate = int(self.base_fire_rate / stats['fire_rate_mult'])
        self.fire_rate = self.base_fire_rate
        self.max_health = int(self.max_health * stats['health_mult'])
        self.health = self.max_health
        
        debug_print(f"Applied {self.ship_type} stats: Speed x{stats['speed_mult']}, Fire Rate x{stats['fire_rate_mult']}, Health x{stats['health_mult']}")
    
    def handle_input(self, keys):
        """Handle smooth input with acceleration."""
        # Horizontal movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity_x = max(self.velocity_x - self.acceleration, -self.max_speed)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x = min(self.velocity_x + self.acceleration, self.max_speed)
        else:
            self.velocity_x *= self.deceleration
        
        # Vertical movement
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.velocity_y = max(self.velocity_y - self.acceleration, -self.max_speed)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.velocity_y = min(self.velocity_y + self.acceleration, self.max_speed)
        else:
            self.velocity_y *= self.deceleration
        
        # Apply movement
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Keep player on screen
        if self.x < self.min_x:
            self.x = self.min_x
            self.velocity_x = 0
        elif self.x > self.max_x:
            self.x = self.max_x
            self.velocity_x = 0
            
        if self.y < self.min_y:
            self.y = self.min_y
            self.velocity_y = 0
        elif self.y > self.max_y:
            self.y = self.max_y
            self.velocity_y = 0
    
    def update(self, dt: int):
        """Update player state with enhanced thruster effects."""
        # Get current game time for powerup expiration checks
        current_time = self.get_current_time()
        
        # Apply movement
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Apply friction
        self.velocity_x *= self.friction
        self.velocity_y *= self.friction
        
        # Keep player on screen
        self.x = max(0, min(self.x, self.max_x))
        self.y = max(0, min(self.y, self.max_y))
        
        # Update rectangle position
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        # Check powerup expiration using game time
        if self.has_rapid_fire and current_time > self.rapid_fire_end_time:
            self.has_rapid_fire = False
            self.fire_rate = self.base_fire_rate
            self.bullet_type = 'basic'
            self.bullet_damage = 20
            debug_print("🔫 Rapid fire expired")
        
        if self.has_shield and current_time > self.shield_end_time:
            self.has_shield = False
            debug_print("🛡️ Shield expired")
        
        if self.has_spread_shot and current_time > self.spread_shot_end_time:
            self.has_spread_shot = False
            self.bullet_type = 'basic'
            self.bullet_damage = 20
            debug_print("🎯 Spread shot expired")
        
        if self.has_laser and current_time > self.laser_end_time:
            self.has_laser = False
            self.bullet_type = 'basic'
            self.bullet_damage = 20
            debug_print("⚡ Laser expired")
        
        # Determine thruster direction based on actual movement
        movement_threshold = 0.5
        center_x = int(self.x + self.sprite.get_width() // 2) 
        center_y = int(self.y + self.sprite.get_height() // 2) 
        
        # Calculate movement intensity for particle effects
        movement_intensity = abs(self.velocity_x) + abs(self.velocity_y)
        
        # Thruster particles based on movement direction
        if self.particle_system_ref is not None:
            if abs(self.velocity_y) > movement_threshold:
                if self.velocity_y < 0:  # Moving up
                    self.particle_system_ref.add_thruster_particles(
                        center_x, center_y, 'forward', movement_intensity * 0.3
                    )
                else:  # Moving down
                    self.particle_system_ref.add_thruster_particles(
                        center_x, center_y, 'backward', movement_intensity * 0.2
                    )
            
            if abs(self.velocity_x) > movement_threshold:
                if self.velocity_x < 0:  # Moving left
                    self.particle_system_ref.add_thruster_particles(
                        center_x, center_y, 'left', movement_intensity * 0.2
                    )
                else:  # Moving right
                    self.particle_system_ref.add_thruster_particles(
                        center_x, center_y, 'right', movement_intensity * 0.2
                    )
        
        # Update visual effects
        self.engine_timer += dt * 0.01
        self.shield_pulse += dt * 0.008
        
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt
    
    def can_shoot(self) -> bool:
        """Check if player can shoot using game time."""
        current_time = self.get_current_time()
        return current_time - self.last_shot > self.fire_rate

    def shoot(self) -> list:
        """Create enhanced projectiles with muzzle flash effects using game time."""
        if not self.can_shoot():
            return []
        
        self.last_shot = self.get_current_time()  # Use game time
        projectiles = []
        
        # Calculate shooting position
        center_x = int(self.x + self.sprite.get_width() // 2)
        shoot_y = int(self.y)
        
        # Add weapon firing particles
        if self.particle_system_ref is not None:
            self.particle_system_ref.add_weapon_fire_particles(
                center_x, shoot_y, self.bullet_type
            )
        
        
        if self.has_spread_shot:
            # Spread shot pattern
            angles = [-0.3, -0.15, 0, 0.15, 0.3]
            for angle in angles:
                projectile = Projectile(
                    center_x - 2, shoot_y, 
                    self.bullet_type, self.settings,
                    angle=angle, damage=self.bullet_damage
                )
                projectiles.append(projectile)
        
        elif self.has_laser:
            # Continuous laser beam
            projectile = Projectile(
                center_x - 4, shoot_y,
                'laser', self.settings,
                damage=self.bullet_damage * 2
            )
            projectiles.append(projectile)
        
        else:
            # Standard shot
            if self.has_rapid_fire:
                # Dual shot for rapid fire
                projectile1 = Projectile(
                    center_x - 8, shoot_y,
                    self.bullet_type, self.settings,
                    damage=self.bullet_damage
                )
                projectile2 = Projectile(
                    center_x + 4, shoot_y,
                    self.bullet_type, self.settings,
                    damage=self.bullet_damage
                )
                projectiles.extend([projectile1, projectile2])
            else:
                # Single shot
                projectile = Projectile(
                    center_x - 2, shoot_y,
                    self.bullet_type, self.settings,
                    damage=self.bullet_damage
                )
                projectiles.append(projectile)
        
        return projectiles
    
    def take_damage(self, amount: int):
        """Take damage with enhanced collision effects."""
        if self.has_shield:
            return  # Shield blocks damage
        
        self.health -= amount
        self.hit_flash_timer = 200
        
        # Collision impact effect
        if self.particle_system_ref is not None:
            center_x = int(self.x + self.sprite.get_width() // 2)
            center_y = int(self.y + self.sprite.get_height() // 2)
            self.particle_system_ref.add_collision_impact(center_x, center_y, 'player_enemy')
        
        if self.health <= 0:
            self.health = 0
            self.alive = False
            
            # Death explosion
            if self.particle_system_ref is not None:
                center_x = int(self.x + self.sprite.get_width() // 2)
                center_y = int(self.y + self.sprite.get_height() // 2)
                self.particle_system_ref.add_explosion_particles(center_x, center_y, 'large')
    
    def heal(self, amount: int):
        """Heal player."""
        self.health = min(self.max_health, self.health + amount)
    
    def apply_powerup(self, powerup_type: str):
        """Apply power-up effect with enhanced weapons using game time."""
        current_time = self.get_current_time()  # Use game time
        duration = self.settings.POWERUP_DURATION
        
        if powerup_type == 'health':
            self.heal(25)
        elif powerup_type == 'rapid_fire':
            self.has_rapid_fire = True
            self.fire_rate = self.base_fire_rate // 4  # Very fast
            self.bullet_type = 'enhanced'
            self.bullet_damage = 30
            self.rapid_fire_end_time = current_time + duration  # Game time
            debug_print(f"🔫 Rapid fire activated until game time {self.rapid_fire_end_time}")
        elif powerup_type == 'shield':
            self.has_shield = True
            self.shield_end_time = current_time + duration  # Game time
            debug_print(f"🛡️ Shield activated until game time {self.shield_end_time}")
        elif powerup_type == 'missile':
            self.has_spread_shot = True
            self.bullet_type = 'missile'
            self.bullet_damage = 40
            self.spread_shot_end_time = current_time + duration  # Game time
    
    def render(self, surface: pygame.Surface):
        """Render player with enhanced effects."""
        if not self.alive:
            return
        
        # Hit flash effect
        if self.hit_flash_timer > 0:
            flash_surface = self.sprite.copy()
            flash_surface.fill((255, 255, 255), special_flags=pygame.BLEND_ADD)
            surface.blit(flash_surface, (int(self.x), int(self.y)))
        
        # Shield effect
        if self.has_shield:
            shield_radius = max(self.sprite.get_width(), self.sprite.get_height()) // 2 + 15
            shield_alpha = int(100 + 50 * math.sin(self.shield_pulse))
            
            shield_surface = pygame.Surface((shield_radius * 2, shield_radius * 2), pygame.SRCALPHA)
            shield_color = (0, 255, 255, shield_alpha)
            
            for i in range(3):
                ring_radius = shield_radius - i * 5
                pygame.draw.circle(shield_surface, shield_color, 
                                 (shield_radius, shield_radius), ring_radius, 2)
            
            shield_x = int(self.x + self.sprite.get_width() // 2 - shield_radius)
            shield_y = int(self.y + self.sprite.get_height() // 2 - shield_radius)
            surface.blit(shield_surface, (shield_x, shield_y))
        
        # Power-up glow effects
        if self.has_rapid_fire:
            glow_color = (255, 255, 0, 50)
            self.render_glow(surface, glow_color)
        elif self.has_spread_shot:
            glow_color = (255, 0, 255, 50)
            self.render_glow(surface, glow_color)
        
        # Render the ship
        surface.blit(self.sprite, (int(self.x), int(self.y)))
    
    def render_glow(self, surface: pygame.Surface, color: tuple):
        """Render glow effect around ship."""
        glow_size = max(self.sprite.get_width(), self.sprite.get_height()) + 20
        glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        
        for radius in range(glow_size // 2, 0, -2):
            alpha = int(color[3] * (1 - radius / (glow_size // 2)))
            glow_color = (*color[:3], alpha)
            pygame.draw.circle(glow_surface, glow_color, 
                             (glow_size // 2, glow_size // 2), radius)
        
        glow_x = int(self.x - (glow_size - self.sprite.get_width()) // 2)
        glow_y = int(self.y - (glow_size - self.sprite.get_height()) // 2)
        surface.blit(glow_surface, (glow_x, glow_y))