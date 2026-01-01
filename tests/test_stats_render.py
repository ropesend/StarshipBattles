
import unittest
from unittest.mock import MagicMock, patch
import pygame
import os
import sys

# Ensure project root is in path
sys.path.append(os.getcwd())

from ship import Ship, LayerType
from components import Component

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

    @patch('pygame_gui.elements.UIScrollingContainer')
    @patch('ui.builder.right_panel.UIImage')
    @patch('ui.builder.right_panel.UITextBox')
    @patch('ui.builder.right_panel.UIDropDownMenu')
    @patch('ui.builder.right_panel.UITextEntryLine')
    @patch('ui.builder.right_panel.UILabel')
    def test_stats_panel_creation_and_update(self, mock_label, mock_entry, mock_drop, mock_box, mock_img, mock_scroll_container):
        """Test that RightPanel creates stats based on config and updates them without error."""
        from ui.builder.right_panel import BuilderRightPanel
        # Create Panel
        panel = BuilderRightPanel(self.builder, self.manager, pygame.Rect(0,0,400,600))
        
        # Verify Sections exist
        self.assertIn('mass', panel.rows_map)
        self.assertIn('max_speed', panel.rows_map)
        self.assertIn('shield_regen', panel.rows_map)
        self.assertIn('emissive_armor', panel.rows_map)
        self.assertIn('targeting', panel.rows_map)
        self.assertIn('crew_required', panel.rows_map)
        
        # Verify update call
        panel.update_stats_display(self.builder.ship)
        
        # Check if rows updated
        # Since StatRow uses the injected UILabel (which is now a Mock due to patch),
        # accessing panel.rows_map['mass'].label will give a Mock instance.
        # We can verify set_text was called?
        # StatRow calls self.label.set_text if visible.
        # But wait, StatRow is ALSO defined in right_panel, but it imports UILabel from pygame_gui.groups.
        # The Patch targets 'ui.builder.right_panel.UILabel'.
        # Since StatRow is in the same file, it uses the global symbol UILabel which we patched.
        # So yes, StatRow.label is a Mock.
        
    @patch('pygame_gui.elements.UIScrollingContainer')
    @patch('ui.builder.right_panel.UIImage')
    @patch('ui.builder.right_panel.UITextBox')
    @patch('ui.builder.right_panel.UIDropDownMenu')
    @patch('ui.builder.right_panel.UITextEntryLine')
    @patch('ui.builder.right_panel.UILabel')
    def test_logistics_section(self, mock_label, mock_entry, mock_drop, mock_box, mock_img, mock_scroll_container):
         from ui.builder.right_panel import BuilderRightPanel
         panel = BuilderRightPanel(self.builder, self.manager, pygame.Rect(0,0,400,600))
         self.assertIn('crew_required', panel.rows_map)
         self.assertIn('fuel_endurance', panel.rows_map)

if __name__ == '__main__':
    unittest.main()
