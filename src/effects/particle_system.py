import pygame
import math
import random
from typing import List, Optional

class Particle:
    def __init__(self, x: float, y: float, vel_x: float, vel_y: float, 
                 color: tuple, life: int, size: int = 2, particle_type: str = 'default'):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.color = color
        self.max_life = life
        self.life = life
        self.size = size
        self.alive = True
        self.particle_type = particle_type
        self.alpha = 255
        self.gravity: float = 0.0
        self.fade_rate = 255.0 / life
        
    def update(self, dt: int):
        """Update particle position and life."""
        if not self.alive:
            return
            
        # Update position
        self.x += self.vel_x * dt * 0.1
        self.y += self.vel_y * dt * 0.1
        
        # Apply gravity for some particle types
        if self.particle_type in ['explosion', 'debris']:
            self.vel_y += self.gravity * dt * 0.001
        
        # Update life and alpha
        self.life -= dt
        if self.life <= 0:
            self.alive = False
        else:
            # Fade out over time
            self.alpha = int(255 * (self.life / self.max_life))
            
    def render(self, surface: pygame.Surface):
        """Render particle with proper alpha blending."""
        if not self.alive or self.alpha <= 0:
            return
            
        # Create particle surface with alpha
        particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        
        # Different rendering based on particle type
        if self.particle_type == 'thruster':
            # Thruster particles have a fiery gradient
            center = self.size
            for radius in range(self.size, 0, -1):
                alpha = int(self.alpha * (radius / self.size))
                color = (*self.color, alpha)
                pygame.draw.circle(particle_surface, color, (center, center), radius)
                
        elif self.particle_type == 'spark':
            # Sparks are bright and sharp
            pygame.draw.circle(particle_surface, (*self.color, self.alpha), (self.size, self.size), self.size)
            
        elif self.particle_type == 'collision':
            # Collision particles are larger and more intense
            for i in range(3):
                alpha = int(self.alpha * (1 - i * 0.3))
                size = self.size + i
                pygame.draw.circle(particle_surface, (*self.color, alpha), (self.size + i, self.size + i), size)
                
        else:
            # Default particle rendering
            pygame.draw.circle(particle_surface, (*self.color, self.alpha), (self.size, self.size), self.size)
        
        surface.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))

class ParticleSystem:
    def __init__(self):
        self.particles: List[Particle] = []
        
    def add_thruster_particles(self, x: int, y: int, direction: str, intensity: float = 1.0):
        """Add realistic thruster particles based on movement direction."""
        num_particles = int(3 * intensity)
        
        # Thruster positions and directions based on ship movement
        if direction == 'forward':  # Moving up - rear thrusters
            for _ in range(num_particles):
                # Particles shoot down from rear of ship
                particle_x = x + random.uniform(-8, 8)
                particle_y = y + 20  # Below the ship
                vel_x = random.uniform(-0.5, 0.5)
                vel_y = random.uniform(2, 5)  # Downward
                
                # Fiery colors - red to yellow
                colors = [(255, 100, 0), (255, 150, 0), (255, 200, 50), (255, 255, 100)]
                color = random.choice(colors)
                
                particle = Particle(particle_x, particle_y, vel_x, vel_y, 
                                   color, random.randint(200, 400), 2, 'thruster')
                self.particles.append(particle)
                
        elif direction == 'backward':  # Moving down - front thrusters
            for _ in range(num_particles):
                # Particles shoot up from front of ship
                particle_x = x + random.uniform(-6, 6)
                particle_y = y - 10  # Above the ship
                vel_x = random.uniform(-0.3, 0.3)
                vel_y = random.uniform(-3, -1)  # Upward
                
                # Blue thruster colors for reverse thrust
                colors = [(0, 150, 255), (50, 180, 255), (100, 200, 255)]
                color = random.choice(colors)
                
                particle = Particle(particle_x, particle_y, vel_x, vel_y, 
                                   color, random.randint(150, 300), 2, 'thruster')
                self.particles.append(particle)
                
        elif direction == 'left':  # Moving left - right side thrusters
            for _ in range(num_particles):
                # Particles shoot right from right side of ship
                particle_x = x + 25  # Right side of ship
                particle_y = y + random.uniform(5, 15)
                vel_x = random.uniform(1, 3)  # Rightward
                vel_y = random.uniform(-0.5, 0.5)
                
                # Orange side thruster colors
                colors = [(255, 150, 0), (255, 200, 50), (255, 180, 30)]
                color = random.choice(colors)
                
                particle = Particle(particle_x, particle_y, vel_x, vel_y, 
                                   color, random.randint(150, 250), 1, 'thruster')
                self.particles.append(particle)
                
        elif direction == 'right':  # Moving right - left side thrusters
            for _ in range(num_particles):
                # Particles shoot left from left side of ship
                particle_x = x - 5  # Left side of ship
                particle_y = y + random.uniform(5, 15)
                vel_x = random.uniform(-3, -1)  # Leftward
                vel_y = random.uniform(-0.5, 0.5)
                
                # Orange side thruster colors
                colors = [(255, 150, 0), (255, 200, 50), (255, 180, 30)]
                color = random.choice(colors)
                
                particle = Particle(particle_x, particle_y, vel_x, vel_y, 
                                   color, random.randint(150, 250), 1, 'thruster')
                self.particles.append(particle)
    
    
    
    
    def add_weapon_fire_particles(self, x: int, y: int, weapon_type: str = 'basic'):
        """Add muzzle flash and weapon firing effects."""
        if weapon_type == 'basic':
            # Small muzzle flash
            for _ in range(3):
                particle_x = x + random.uniform(-3, 3)
                particle_y = y + random.uniform(-5, 5)
                vel_x = random.uniform(-1, 1)
                vel_y = random.uniform(-2, 0)
                
                color = random.choice([(255, 255, 100), (255, 255, 150), (255, 200, 0)])
                
                particle = Particle(particle_x, particle_y, vel_x, vel_y, 
                                   color, random.randint(50, 100), 1, 'spark')
                self.particles.append(particle)
                
        elif weapon_type == 'enhanced':
            # Bigger muzzle flash
            for _ in range(6):
                particle_x = x + random.uniform(-5, 5)
                particle_y = y + random.uniform(-8, 3)
                vel_x = random.uniform(-2, 2)
                vel_y = random.uniform(-3, 1)
                
                color = random.choice([(255, 100, 255), (255, 150, 255), (200, 100, 255)])
                
                particle = Particle(particle_x, particle_y, vel_x, vel_y, 
                                   color, random.randint(100, 200), 2, 'spark')
                self.particles.append(particle)
    
    def add_collision_impact(self, x: int, y: int, collision_type: str = 'player_enemy'):
        """Add dramatic collision impact effects."""
        if collision_type == 'player_enemy':
            # Intense collision sparks
            for _ in range(15):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(2, 8)
                vel_x = math.cos(angle) * speed
                vel_y = math.sin(angle) * speed
                
                # Bright impact colors
                colors = [
                    (255, 255, 255),  # White sparks
                    (255, 255, 0),    # Yellow sparks
                    (255, 150, 0),    # Orange sparks
                    (255, 0, 0),      # Red sparks
                ]
                color = random.choice(colors)
                
                particle = Particle(x, y, vel_x, vel_y, color, 
                                   random.randint(300, 600), random.randint(2, 4), 'collision')
                self.particles.append(particle)
                
            # Add some debris particles
            for _ in range(8):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(1, 4)
                vel_x = math.cos(angle) * speed
                vel_y = math.sin(angle) * speed
                
                # Metal debris colors
                color = random.choice([(150, 150, 150), (100, 100, 100), (80, 80, 80)])
                
                particle = Particle(x, y, vel_x, vel_y, color, 
                                   random.randint(500, 1000), 1, 'debris')
                particle.gravity = 0.5  # FIXED: Now properly typed as float
                self.particles.append(particle)
    
    def add_explosion_particles(self, x: int, y: int, size: str = 'normal'):
        """Add explosion particles with different intensities."""
        if size == 'small':
            particle_count = 8
            max_speed = 3
            life_range = (200, 400)
        elif size == 'large':
            particle_count = 25
            max_speed = 6
            life_range = (400, 800)
        else:  # normal
            particle_count = 15
            max_speed = 4
            life_range = (300, 600)
        
        for _ in range(particle_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, max_speed)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            # Explosion colors
            colors = [
                (255, 100, 0),    # Orange
                (255, 150, 0),    # Light orange
                (255, 0, 0),      # Red
                (255, 255, 0),    # Yellow
                (200, 200, 200),  # Smoke
            ]
            color = random.choice(colors)
            
            life = random.randint(*life_range)
            size_val = random.randint(2, 4)
            
            particle = Particle(x, y, vel_x, vel_y, color, life, size_val, 'explosion')
            particle.gravity = 0.2
            self.particles.append(particle)
    
    def add_hit_particles(self, x: int, y: int):
        """Add hit effect particles."""
        for _ in range(5):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            color = (255, 255, 255)
            life = random.randint(100, 300)
            
            particle = Particle(x, y, vel_x, vel_y, color, life, 1, 'spark')
            self.particles.append(particle)
    
    def update(self, dt: int):
        """Update all particles."""
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.alive:
                self.particles.remove(particle)
    
    def render(self, surface: pygame.Surface):
        """Render all particles."""
        for particle in self.particles:
            particle.render(surface)