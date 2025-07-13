"""
Debug configuration module for controlling logging and debug output.
"""
import os
import logging

# Global debug variables
DEBUG_MODE = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes', 'on')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO' if not DEBUG_MODE else 'DEBUG').upper()
SHOW_CONSOLE_LOGS = os.getenv('SHOW_CONSOLE_LOGS', 'False' if not DEBUG_MODE else 'True').lower() in ('true', '1', 'yes', 'on')

# Debug categories - enable/disable specific types of debug output
DEBUG_CATEGORIES = {
    'GAME_EVENTS': DEBUG_MODE,
    'COLLISION': DEBUG_MODE,
    'ENEMY_AI': DEBUG_MODE,
    'PLAYER_INPUT': DEBUG_MODE,
    'PERFORMANCE': DEBUG_MODE,
    'SOUND': DEBUG_MODE,
    'GRAPHICS': DEBUG_MODE,
}

def is_debug_enabled(category=None):
    """Check if debug is enabled for a specific category or globally."""
    if category:
        return DEBUG_CATEGORIES.get(category, False)
    return DEBUG_MODE

def debug_print(message, category=None):
    """Print debug message only if debug is enabled for the category."""
    if is_debug_enabled(category):
        if category:
            print(f"[DEBUG-{category}] {message}")
        else:
            print(f"[DEBUG] {message}")

def setup_debug_logging():
    """Setup logging configuration based on debug settings."""
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    from datetime import datetime
    log_file = os.path.join(log_dir, f'game_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    handlers = [logging.FileHandler(log_file)]
    
    if SHOW_CONSOLE_LOGS:
        handlers.append(logging.StreamHandler())
    
    # Set log level based on configuration
    numeric_level = getattr(logging, LOG_LEVEL, logging.INFO)
    
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        handlers=handlers,
        force=True
    )
    
    return logging.getLogger(__name__)