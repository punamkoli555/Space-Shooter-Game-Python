import pygame
from enum import Enum
from dataclasses import dataclass
from typing import Tuple

class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    VICTORY = "victory"

@dataclass
class Settings:
    # Screen settings
    SCREEN_WIDTH: int = 1024
    SCREEN_HEIGHT: int = 768
    FPS: int = 60
    TITLE: str = "Space Shooter Enhanced"
    
    # Colors
    BLACK: Tuple[int, int, int] = (0, 0, 0)
    WHITE: Tuple[int, int, int] = (255, 255, 255)
    RED: Tuple[int, int, int] = (255, 0, 0)
    GREEN: Tuple[int, int, int] = (0, 255, 0)
    BLUE: Tuple[int, int, int] = (0, 0, 255)
    YELLOW: Tuple[int, int, int] = (255, 255, 0)
    
    # Player settings
    PLAYER_SPEED: int = 8
    PLAYER_HEALTH: int = 100
    PLAYER_FIRE_RATE: int = 250  # milliseconds
    
    # Enemy settings
    ENEMY_SPEED_MIN: int = 2
    ENEMY_SPEED_MAX: int = 6
    ENEMY_SPAWN_RATE: int = 1500  # milliseconds
    
    # Boss settings
    BOSS_HEALTH: int = 500
    BOSS_SPEED: int = 3
    
    # Projectile settings
    BULLET_SPEED: int = 12
    MISSILE_SPEED: int = 8
    
    # Power-up settings
    POWERUP_SPAWN_RATE: int = 10000  # milliseconds
    POWERUP_DURATION: int = 5000  # milliseconds
    
    # Audio settings
    MASTER_VOLUME: float = 0.7
    MUSIC_VOLUME: float = 0.5
    SFX_VOLUME: float = 0.8
    
    # Game progression
    LEVEL_SCORE_THRESHOLD: int = 1000
    BOSS_SPAWN_SCORE: int = 5000