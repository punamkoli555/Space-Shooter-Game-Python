"""
Production launcher for Space Shooter Game
"""
import pygame
import sys
import os
import traceback
import logging
from datetime import datetime
from utils.debug_config import setup_debug_logging, DEBUG_MODE, debug_print

def get_resource_path(relative_path):

    try:

        base_path = sys._MEIPASS # type: ignore
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def setup_logging():

    try:
        return setup_debug_logging()
    except Exception as e:
        # Fallback to basic logging
        logging.basicConfig(level=logging.INFO if not DEBUG_MODE else logging.DEBUG)
        return logging.getLogger(__name__)

def main():
    """Production main function with error handling."""
    logger = setup_logging()
    
    debug_print("Starting Space Shooter Enhanced v1.0")
    debug_print("Starting space shooter game...", "GAME_EVENTS")
    
    if DEBUG_MODE:
        logger.info("Debug mode enabled")
    else:
        logger.info("Production mode - limited console output")
    
    try:
        # Initialize Pygame
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        logger.info("Pygame initialized successfully")
        
         # CRITICAL: Set working directory to bundle location
        if hasattr(sys, '_MEIPASS'):
            os.chdir(sys._MEIPASS) # type: ignore
            logger.info(f"Changed working directory to: {sys._MEIPASS}") # type: ignore
        
        # Import and run game
        from game.settings import Settings
        from game.game_engine import GameEngine
        
        settings = Settings()
        logger.info("Game settings loaded")
        
        game = GameEngine(settings)
        logger.info("SpaceWarzone Game engine initialized Successfully")
        
        # NOW set window icon after display is created
        try:
            icon_path = get_resource_path("icon.png")
            if os.path.exists(icon_path):
                icon_surface = pygame.image.load(icon_path).convert_alpha()
                # Ensure icon is proper size (32x32 recommended for Windows)
                if icon_surface.get_size() != (32, 32):
                    icon_surface = pygame.transform.scale(icon_surface, (32, 32))
                pygame.display.set_icon(icon_surface)
                logger.info("✓ Window icon set successfully")
            else:
                logger.warning(f"Icon file not found at: {icon_path}")
        except Exception as e:
            logger.warning(f"Could not set window icon: {e}")
        
        # Run the game
        logger.info("Window icon set successfully")
        result = game.run()
        logger.info("Starting game loop...")
        
    except Exception as e:
        logger.error(f"Critical error: {e}")
        logger.error(traceback.format_exc())
        
        # Show user-friendly error message
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()
            
            messagebox.showerror(
                "Space Shooter Enhanced - Error",
                f"An unexpected error occurred:\n{str(e)}\n\nCheck the logs folder for more details.\n\nPlease report this issue to the developer."
            )
        except:
            # Fallback error display
            print(f"\n GAME ERROR: {e}")
            print("\nPlease check the logs folder for more details.")
            input("\nPress Enter to exit...")
    
    finally:
        try:
            pygame.mixer.quit()
            pygame.quit()
        except:
            pass
        logger.info("Game shutdown complete")

if __name__ == "__main__":
    main()