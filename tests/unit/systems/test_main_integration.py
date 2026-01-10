
import unittest
import sys
import os
import importlib
import pygame
from unittest.mock import patch, MagicMock
from game.core.registry import RegistryManager

# Ensure we use dummy video driver to prevent window opening
os.environ["SDL_VIDEODRIVER"] = "dummy"

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestMainIntegration(unittest.TestCase):
    """
    Smoke tests to verify that the main application entry point and key modules 
    can be imported and instantiated without errors. This prevents regression 
    where refactoring global variables (like BATTLE_LOG) breaks imports in main.py.
    """

    def setUp(self):
        # We need to make sure we can import main even if it was already imported
        pass

    def tearDown(self):
        """Cleanup pygame and registry."""
        # CRITICAL: Clean up ALL mocks first (prevents mock object pollution)
        patch.stopall()
        
        pygame.quit()
        RegistryManager.instance().clear()

    def test_import_main(self):
        """Test that main.py can be imported without ImportError."""
        try:
            from game import app
        except ImportError as e:
            self.fail(f"Failed to import main.py: {e}")
        except Exception as e:
            # Main might fail on init due to pygame headless issues, but we want to catch ImportErrors primarily/
            # However, if it fails due to display, that's fine for this specific test case regarding BATTLE_LOG
            print(f"Warning: main.py raised exception during import (likely pygame init): {e}")

    def test_game_instantiation(self):
        """Test that the Game class can be instantiated."""
        # Use real pygame.display.Info() in headless mode rather than mocking it,
        # as over-mocking display globals can break pygame_gui's internal state.
        
        # We allow real set_mode to run (with dummy driver defined in imports)
        # to ensure surfaces can be converted.

        try:
            from game import app
            # Mock display Info and ensure set_mode is called for convert_alpha
            if not pygame.display.get_surface():
                pygame.display.set_mode((1440, 900), pygame.NOFRAME)
            with patch('pygame.display.Info', return_value=MagicMock(current_w=1920, current_h=1080)):
                game = app.Game()
                self.assertIsNotNone(game)
            self.assertIsNotNone(game.battle_scene)
            self.assertIsNotNone(game.battle_scene.engine)
            
            # Verify the engine has a logger (instance based)
            self.assertTrue(hasattr(game.battle_scene.engine, 'logger'))
            
            # Verify BATTLE_LOG is NOT a property of the battle module anymore
            from game.ui.screens import battle_scene
            self.assertFalse(hasattr(battle_scene, 'BATTLE_LOG'), "battle_scene module should not export global BATTLE_LOG")
            
        except ImportError as e:
            self.fail(f"Game instantiation failed due to ImportError: {e}")
        except Exception as e:
            self.fail(f"Game instantiation failed with exception: {e}")

if __name__ == '__main__':
    unittest.main()
