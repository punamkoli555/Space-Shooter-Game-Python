import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.game_engine import GameEngine

class CollisionManager:
    def __init__(self):
        pass
    
    def check_collisions(self, game_engine: 'GameEngine'):
        """Check all collision scenarios."""
        self.check_player_enemy_collisions(game_engine)
        self.check_player_boss_collisions(game_engine)
        self.check_player_powerup_collisions(game_engine)
        self.check_projectile_enemy_collisions(game_engine)
        self.check_projectile_boss_collisions(game_engine)
        self.check_projectile_player_collisions(game_engine)
    
    def check_player_enemy_collisions(self, game_engine: 'GameEngine'):
        """Check player collisions with enemies - FIXED TYPE ISSUES."""
        if not game_engine.player or not game_engine.player.alive:
            return
        
        for enemy in game_engine.enemies[:]:
            if enemy is not None and enemy.alive and game_engine.player.rect.colliderect(enemy.rect):
                collision_x = int((game_engine.player.rect.centerx + enemy.rect.centerx) // 2)
                collision_y = int((game_engine.player.rect.centery + enemy.rect.centery) // 2)
                
                game_engine.particle_system.add_collision_impact(
                    collision_x, collision_y, 'player_enemy'
                )
                
                damage = getattr(enemy, 'damage', 25)
                game_engine.player.take_damage(damage)
                
                enemy.alive = False
                
                game_engine.add_explosion(int(enemy.x), int(enemy.y), 'normal')
    
    def check_player_boss_collisions(self, game_engine: 'GameEngine'):
        """Check player collisions with bosses."""
        if not game_engine.player or not game_engine.player.alive:
            return
        
        for boss in game_engine.bosses:
            if boss is not None and boss.alive and game_engine.player.rect.colliderect(boss.rect):
                # Calculate collision center
                collision_x = int((game_engine.player.rect.centerx + boss.rect.centerx) // 2)
                collision_y = int((game_engine.player.rect.centery + boss.rect.centery) // 2)
                
                # Add MASSIVE collision effect for boss
                game_engine.particle_system.add_collision_impact(
                    collision_x, collision_y, 'player_boss'
                )
                
                # Player takes heavy damage from boss collision
                game_engine.player.take_damage(50)
                
                # Add large explosion
                game_engine.add_explosion(collision_x, collision_y, 'large')
    
    def check_player_powerup_collisions(self, game_engine: 'GameEngine'):
        """Check player collisions with powerups."""
        if not game_engine.player or not game_engine.player.alive:
            return
        
        for powerup in game_engine.powerups[:]:
            if powerup is not None and powerup.alive and game_engine.player.rect.colliderect(powerup.rect):
                # Apply powerup effect
                game_engine.player.apply_powerup(powerup.powerup_type)
                
                # Remove powerup
                powerup.alive = False
                
                # Play sound if available
                if hasattr(game_engine, 'audio_manager') and game_engine.audio_manager:
                    game_engine.audio_manager.play_sound('powerup')
    
    def check_projectile_enemy_collisions(self, game_engine: 'GameEngine'):
        """Check projectile collisions with enemies."""
        for projectile in game_engine.projectiles[:]:
            if (projectile is None or not projectile.alive or 
                projectile.projectile_type in ['enemy_bullet', 'boss_bullet', 'boss_missile']):
                continue
            
            for enemy in game_engine.enemies[:]:
                if enemy is not None and enemy.alive and projectile.rect.colliderect(enemy.rect):
                    hit_x = int(projectile.x + projectile.width // 2)
                    hit_y = int(projectile.y + projectile.height // 2)
                    game_engine.particle_system.add_hit_particles(hit_x, hit_y)
                    
                    # Enemy takes damage
                    if hasattr(enemy, 'take_damage'):
                        enemy.take_damage(projectile.damage)
                    else:
                        if hasattr(enemy, 'health'):
                            enemy.health -= projectile.damage
                            if enemy.health <= 0:
                                enemy.alive = False
                        else:
                            enemy.alive = False
                    
                    # Remove projectile
                    projectile.alive = False
                    
                    # If enemy dies, add explosion and score
                    if not enemy.alive:
                        game_engine.add_explosion(int(enemy.x), int(enemy.y), 'small')
                        if hasattr(game_engine, 'add_score'):
                            points = getattr(enemy, 'points', 10)  # Default points
                            game_engine.add_score(points)
                    
                    break
    
    def check_projectile_boss_collisions(self, game_engine: 'GameEngine'):
        """Check projectile collisions with bosses."""
        for projectile in game_engine.projectiles[:]:
            # Check if it's a player projectile (not enemy bullet)
            if (projectile is None or not projectile.alive or 
                projectile.projectile_type in ['enemy_bullet', 'boss_bullet', 'boss_missile']):
                continue
            
            for boss in game_engine.bosses[:]:
                if boss is not None and boss.alive and projectile.rect.colliderect(boss.rect):
                    # Add hit particles for boss hits
                    hit_x = int(projectile.x + projectile.width // 2)
                    hit_y = int(projectile.y + projectile.height // 2)
                    game_engine.particle_system.add_hit_particles(hit_x, hit_y)
                    
                    # Boss takes damage
                    if hasattr(boss, 'take_damage'):
                        boss.take_damage(projectile.damage)
                    else:
                        if hasattr(boss, 'health'):
                            boss.health -= projectile.damage
                            if boss.health <= 0:
                                boss.alive = False
                        else:
                            boss.alive = False  # Kill boss if no health system
                    
                    # Remove projectile
                    projectile.alive = False
                    
                    # If boss dies, add explosion and score
                    if not boss.alive:
                        game_engine.add_explosion(int(boss.x), int(boss.y), 'large')
                        if hasattr(game_engine, 'add_score'):
                            points = getattr(boss, 'points', 1000)  # Default boss points
                            game_engine.add_score(points)
                    
                    break
    
    def check_projectile_player_collisions(self, game_engine: 'GameEngine'):
        """Check enemy projectile collisions with player."""
        if not game_engine.player or not game_engine.player.alive:
            return
        
        for projectile in game_engine.projectiles[:]:
            if (projectile is not None and projectile.alive and 
                projectile.projectile_type in ['enemy_bullet', 'boss_bullet', 'boss_missile'] and
                projectile.rect.colliderect(game_engine.player.rect)):
                
                # Add hit effect on player
                hit_x = int(game_engine.player.x + game_engine.player.sprite.get_width() // 2)
                hit_y = int(game_engine.player.y + game_engine.player.sprite.get_height() // 2)
                game_engine.particle_system.add_hit_particles(hit_x, hit_y)
                
                # Player takes damage
                game_engine.player.take_damage(projectile.damage)
                
                # Remove projectile
                projectile.alive = False
                
                # Add small explosion
                game_engine.add_explosion(int(projectile.x), int(projectile.y), 'small')