"""
Debug utilities for the space shooter game.
"""
from .debug_config import debug_print, is_debug_enabled, DEBUG_MODE
import time
import functools

def debug_timer(category="PERFORMANCE"):
    """Decorator to time function execution (only in debug mode)."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if is_debug_enabled(category):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                debug_print(f"{func.__name__} took {end_time - start_time:.4f}s", category)
                return result
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator

def log_collision(obj1, obj2):
    """Log collision events (only in debug mode)."""
    if is_debug_enabled("COLLISION"):
        debug_print(f"Collision: {type(obj1).__name__} <-> {type(obj2).__name__}", "COLLISION")

def log_enemy_action(enemy_type, action):
    """Log enemy AI actions (only in debug mode)."""
    debug_print(f"{enemy_type}: {action}", "ENEMY_AI")

def log_player_input(input_type, value=None):
    """Log player input (only in debug mode)."""
    message = f"Input: {input_type}"
    if value is not None:
        message += f" = {value}"
    debug_print(message, "PLAYER_INPUT")

def log_sound_event(sound_name, volume=None):
    """Log sound events (only in debug mode)."""
    message = f"Sound: {sound_name}"
    if volume is not None:
        message += f" (volume: {volume})"
    debug_print(message, "SOUND")