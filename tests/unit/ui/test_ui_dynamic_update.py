import unittest
from unittest.mock import MagicMock, patch
import pygame
import os
import sys

# Ensure project root is in path


from game.simulation.entities.ship import Ship
from ui.builder.right_panel import BuilderRightPanel

class TestUIDynamicUpdate(unittest.TestCase):
    def setUp(self):
        from game.core.registry import RegistryManager
        RegistryManager.instance().clear()
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.font.init()
        pygame.display.set_mode((800, 600), flags=pygame.HIDDEN)
        
        self.builder = MagicMock()
        self.builder.theme_manager.get_available_themes.return_value = ["Federation"]
        
        # Use real Ship (no reload)
        self.builder.ship = Ship("Test Ship", 0, 0, (255,255,255))
        
        self.manager = MagicMock()
        
        
    def tearDown(self):
        # CRITICAL: Clean up ALL mocks first (prevents mock object pollution)
        patch.stopall()
        
        pygame.display.quit()
        pygame.quit()
        from game.core.registry import RegistryManager
        RegistryManager.instance().clear()

    @patch('pygame_gui.elements.UIScrollingContainer')
    @patch('pygame_gui.elements.UIImage')
    @patch('pygame_gui.elements.UITextBox')
    @patch('pygame_gui.elements.UIDropDownMenu')
    @patch('pygame_gui.elements.UITextEntryLine')
    @patch('pygame_gui.elements.UILabel')
    def test_dynamic_row_addition(self, mock_label, mock_entry, mock_drop, mock_box, mock_img, mock_scroll_container):
        """Test that adding a resource triggers a UI rebuild to show the new row."""
        
        import ui.builder.right_panel
        import importlib
        import sys
        if 'ui.builder.right_panel' in sys.modules:
            importlib.reload(sys.modules['ui.builder.right_panel'])
        
        # 1. Create Panel with NO resources (ensure ship is empty initially)
        self.builder.ship.resources.reset_stats() 
        
        panel = BuilderRightPanel(self.builder, self.manager, pygame.Rect(0,0,400,600))
        
        # Confirm no fuel rows
        self.assertNotIn('max_fuel', panel.rows_map)
        
        # 2. Add Resource (Simulate adding a component)
        # We need to simulate the ship logic that adds capacity.
        # Since we use real Ship logic, we can just register storage directly on the registry,
        # mimicking what ShipStatsCalculator would do.
        self.builder.ship.resources.register_storage('fuel', 100)
        
        # 3. Trigger Update
        panel.on_ship_updated(self.builder.ship)
        
        # 4. Verify Row Exists
        # This checks that on_ship_updated rebuilds the structure when keys change
        self.assertIn('max_fuel', panel.rows_map, "Fuel row should appear after adding fuel storage")

if __name__ == '__main__':
    unittest.main()
