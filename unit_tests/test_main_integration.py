
import unittest
import sys
import os
import importlib
from unittest.mock import patch, MagicMock

# Ensure we use dummy video driver to prevent window opening
os.environ["SDL_VIDEODRIVER"] = "dummy"

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestMainIntegration(unittest.TestCase):
    """
    Smoke tests to verify that the main application entry point and key modules 
    can be imported and instantiated without errors. This prevents regression 
    where refactoring global variables (like BATTLE_LOG) breaks imports in main.py.
    """

    def setUp(self):
        # We need to make sure we can import main even if it was already imported
        if 'main' in sys.modules:
            del sys.modules['main']
        if 'battle' in sys.modules:
            del sys.modules['battle']

    def test_import_main(self):
        """Test that main.py can be imported without ImportError."""
        try:
            import main
        except ImportError as e:
            self.fail(f"Failed to import main.py: {e}")
        except Exception as e:
            # Main might fail on init due to pygame headless issues, but we want to catch ImportErrors primarily/
            # However, if it fails due to display, that's fine for this specific test case regarding BATTLE_LOG
            print(f"Warning: main.py raised exception during import (likely pygame init): {e}")

    @patch('pygame.display.Info')
    def test_game_instantiation(self, mock_info):
        """Test that the Game class can be instantiated."""
        # Setup mocks for screen resolution
        mock_info_obj = MagicMock()
        type(mock_info_obj).current_w = unittest.mock.PropertyMock(return_value=1920)
        type(mock_info_obj).current_h = unittest.mock.PropertyMock(return_value=1080)
        # Fallback for direct attribute access if not property
        mock_info_obj.current_w = 1920
        mock_info_obj.current_h = 1080
        mock_info.return_value = mock_info_obj
        
        # We allow real set_mode to run (with dummy driver defined in imports)
        # to ensure surfaces can be converted.

        try:
            import main
            game = main.Game()
            self.assertIsNotNone(game)
            self.assertIsNotNone(game.battle_scene)
            self.assertIsNotNone(game.battle_scene.engine)
            
            # Verify the engine has a logger (instance based)
            self.assertTrue(hasattr(game.battle_scene.engine, 'logger'))
            
            # Verify BATTLE_LOG is NOT a property of the battle module anymore
            import battle
            self.assertFalse(hasattr(battle, 'BATTLE_LOG'), "battle module should not export global BATTLE_LOG")
            
        except ImportError as e:
            self.fail(f"Game instantiation failed due to ImportError: {e}")
        except Exception as e:
            self.fail(f"Game instantiation failed with exception: {e}")

if __name__ == '__main__':
    unittest.main()
