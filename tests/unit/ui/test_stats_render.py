
import unittest
from unittest.mock import MagicMock, patch
import pygame
import os
import sys

# Ensure project root is in path


from game.simulation.entities.ship import Ship, LayerType
from game.simulation.components.component import Component

class TestStatsRender(unittest.TestCase):
    def setUp(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.set_mode((800, 600), flags=pygame.HIDDEN)
        
        self.builder = MagicMock()
        self.builder.theme_manager.get_available_themes.return_value = ["Federation"]
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
    @patch('pygame_gui.elements.ui_label.UILabel')
    def test_stats_panel_creation_and_update(self, mock_label, mock_entry, mock_drop, mock_box, mock_img, mock_scroll_container):
        """Test that RightPanel creates stats based on config and updates them without error."""
        import sys
        import importlib
        import pygame_gui.elements
        
        # Manually patch the module attribute to ensure it sticks
        orig_label = pygame_gui.elements.UILabel
        orig_img = pygame_gui.elements.UIImage
        orig_box = pygame_gui.elements.UITextBox
        orig_drop = pygame_gui.elements.UIDropDownMenu
        orig_entry = pygame_gui.elements.UITextEntryLine
        orig_scroll = pygame_gui.elements.UIScrollingContainer
        
        pygame_gui.elements.UILabel = MagicMock()
        pygame_gui.elements.UIImage = MagicMock()
        pygame_gui.elements.UITextBox = MagicMock()
        pygame_gui.elements.UIDropDownMenu = MagicMock()
        pygame_gui.elements.UITextEntryLine = MagicMock()
        pygame_gui.elements.UIScrollingContainer = MagicMock()
        
        try:
            if 'ui.builder.right_panel' in sys.modules:
                importlib.reload(sys.modules['ui.builder.right_panel'])
                
            from ui.builder.right_panel import BuilderRightPanel
            
            # Create Panel
            panel = BuilderRightPanel(self.builder, self.manager, pygame.Rect(0,0,400,600))
            
            # Verify Sections exist
            self.assertIn('mass', panel.rows_map)
            # ...
            
        finally:
            # Restore
            pygame_gui.elements.UILabel = orig_label
            pygame_gui.elements.UIImage = orig_img
            pygame_gui.elements.UITextBox = orig_box
            pygame_gui.elements.UIDropDownMenu = orig_drop
            pygame_gui.elements.UITextEntryLine = orig_entry
            pygame_gui.elements.UIScrollingContainer = orig_scroll
            
        # Re-import to clean up for other tests?
        if 'ui.builder.right_panel' in sys.modules:
             importlib.reload(sys.modules['ui.builder.right_panel'])
        
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
    @patch('pygame_gui.elements.UIImage')
    @patch('pygame_gui.elements.UITextBox')
    @patch('pygame_gui.elements.UIDropDownMenu')
    @patch('pygame_gui.elements.UITextEntryLine')
    @patch('pygame_gui.elements.ui_label.UILabel')
    def test_logistics_section(self, mock_label, mock_entry, mock_drop, mock_box, mock_img, mock_scroll_container):
         import sys
         import importlib
         import pygame_gui.elements
         
         # Manually patch
         orig_label = pygame_gui.elements.UILabel
         orig_img = pygame_gui.elements.UIImage
         orig_box = pygame_gui.elements.UITextBox
         orig_drop = pygame_gui.elements.UIDropDownMenu
         orig_entry = pygame_gui.elements.UITextEntryLine
         orig_scroll = pygame_gui.elements.UIScrollingContainer
         
         pygame_gui.elements.UILabel = MagicMock()
         pygame_gui.elements.UIImage = MagicMock()
         pygame_gui.elements.UITextBox = MagicMock()
         pygame_gui.elements.UIDropDownMenu = MagicMock()
         pygame_gui.elements.UITextEntryLine = MagicMock()
         pygame_gui.elements.UIScrollingContainer = MagicMock()
         
         try:
             if 'ui.builder.right_panel' in sys.modules:
                 importlib.reload(sys.modules['ui.builder.right_panel'])
                 
             from ui.builder.right_panel import BuilderRightPanel
             
             # Register resources...
             self.builder.ship.resources.register_storage('fuel', 100)
             
             panel = BuilderRightPanel(self.builder, self.manager, pygame.Rect(0,0,400,600))
             self.assertIn('crew_required', panel.rows_map)
             self.assertIn('max_fuel', panel.rows_map)
             
         finally:
             pygame_gui.elements.UILabel = orig_label
             pygame_gui.elements.UIImage = orig_img
             pygame_gui.elements.UITextBox = orig_box
             pygame_gui.elements.UIDropDownMenu = orig_drop
             pygame_gui.elements.UITextEntryLine = orig_entry
             pygame_gui.elements.UIScrollingContainer = orig_scroll
             
             if 'ui.builder.right_panel' in sys.modules:
                 importlib.reload(sys.modules['ui.builder.right_panel'])

if __name__ == '__main__':
    unittest.main()
