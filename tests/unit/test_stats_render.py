
import unittest
from unittest.mock import MagicMock, patch
import pygame
import os
import sys

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from game.simulation.entities.ship import Ship
from game.simulation.components.component import Component
from game.ui.screens.builder.right_panel import BuilderRightPanel

class TestStatsRender(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((800, 600), flags=pygame.HIDDEN)
        
        self.builder = MagicMock()
        self.builder.theme_manager.get_available_themes.return_value = ["Federation"]
        self.builder.ship = Ship("Test Ship", 0, 0, (255,255,255))
        
        self.manager = MagicMock()
        
    def tearDown(self):
        pygame.quit()

    @patch('game.ui.screens.builder.right_panel.UITextEntryLine')
    @patch('game.ui.screens.builder.right_panel.UIDropDownMenu')
    @patch('game.ui.screens.builder.right_panel.UITextBox')
    @patch('game.ui.screens.builder.right_panel.UIImage')
    @patch('game.ui.screens.builder.right_panel.UILabel')
    @patch('pygame_gui.elements.UIScrollingContainer') # Used via fullname in module
    def test_stats_panel_creation_and_update(self, mock_scroll, mock_label, mock_img, mock_box, mock_drop, mock_entry):
        """Test that RightPanel creates stats based on config and updates them without error."""
        
        # Create Panel
        panel = BuilderRightPanel(self.builder, self.manager, pygame.Rect(0,0,400,600))
        
        # Verify Sections exist
        self.assertIn('mass', panel.rows_map)
        self.assertIn('max_speed', panel.rows_map)
        self.assertIn('shield_regen', panel.rows_map)
        
        # Verify update call
        panel.update_stats_display(self.builder.ship)
        
        # Verify label interactions
        # StatRow should have created labels
        self.assertTrue(mock_label.called)

    @patch('game.ui.screens.builder.right_panel.UITextEntryLine')
    @patch('game.ui.screens.builder.right_panel.UIDropDownMenu')
    @patch('game.ui.screens.builder.right_panel.UITextBox')
    @patch('game.ui.screens.builder.right_panel.UIImage')
    @patch('game.ui.screens.builder.right_panel.UILabel')
    @patch('pygame_gui.elements.UIScrollingContainer')
    def test_logistics_section(self, mock_scroll, mock_label, mock_img, mock_box, mock_drop, mock_entry):
         # Register resources
         self.builder.ship.resources.register_storage('fuel', 100)
         
         panel = BuilderRightPanel(self.builder, self.manager, pygame.Rect(0,0,400,600))
         
         self.assertIn('crew_required', panel.rows_map)
         self.assertIn('max_fuel', panel.rows_map)

if __name__ == '__main__':
    unittest.main()
