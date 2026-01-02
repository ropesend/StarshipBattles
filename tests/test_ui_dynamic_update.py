import unittest
from unittest.mock import MagicMock, patch
import pygame
import os
import sys

# Ensure project root is in path
sys.path.append(os.getcwd())

from ship import Ship
from ui.builder.right_panel import BuilderRightPanel

class TestUIDynamicUpdate(unittest.TestCase):
    def setUp(self):
        import importlib
        import ship
        import ui.builder.stats_config
        import ui.builder.right_panel
        
        # Force reload to clear any polluted module state
        importlib.reload(ship) # Resets VEHICLE_CLASSES
        importlib.reload(ui.builder.stats_config) # Resets STATS_CONFIG
        importlib.reload(ui.builder.right_panel) # Re-imports fresh classes
        
        # Capture fresh class references
        self.ShipClass = ship.Ship
        self.BuilderRightPanelClass = ui.builder.right_panel.BuilderRightPanel
        
        pygame.init()
        pygame.display.set_mode((800, 600), flags=pygame.HIDDEN)
        
        self.builder = MagicMock()
        self.builder.theme_manager.get_available_themes.return_value = ["Federation"]
        # Use fresh Ship class
        self.builder.ship = self.ShipClass("Test Ship", 0, 0, (255,255,255))
        
        self.manager = MagicMock()
        
    def tearDown(self):
        pygame.quit()

    @patch('pygame_gui.elements.UIScrollingContainer')
    @patch('ui.builder.right_panel.UIImage')
    @patch('ui.builder.right_panel.UITextBox')
    @patch('ui.builder.right_panel.UIDropDownMenu')
    @patch('ui.builder.right_panel.UITextEntryLine')
    @patch('ui.builder.right_panel.UILabel')
    def test_dynamic_row_addition(self, mock_label, mock_entry, mock_drop, mock_box, mock_img, mock_scroll_container):
        """Test that adding a resource triggers a UI rebuild to show the new row."""
        
        # 1. Create Panel with NO resources
        # Use fresh Panel class
        panel = self.BuilderRightPanelClass(self.builder, self.manager, pygame.Rect(0,0,400,600))
        
        # Confirm no fuel rows
        self.assertNotIn('max_fuel', panel.rows_map)
        
        # 2. Add Resource (Simulate adding a component)
        self.builder.ship.resources.register_storage('fuel', 100)
        
        # 3. Trigger Update
        panel.on_ship_updated(self.builder.ship)
        
        # 4. Verify Row Exists
        # This checks that on_ship_updated rebuilds the structure when keys change
        self.assertIn('max_fuel', panel.rows_map, "Fuel row should appear after adding fuel storage")

if __name__ == '__main__':
    unittest.main()
