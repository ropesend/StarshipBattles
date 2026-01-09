import unittest
from unittest.mock import MagicMock, patch
import os
import sys
import pygame
import pygame_gui

# Set dummy video driver for headless testing
os.environ['SDL_VIDEODRIVER'] = 'dummy'

# Add root to sys.path if not already there
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from game.simulation.entities.ship import Ship, initialize_ship_data, LayerType
from game.simulation.components.component import load_components, load_modifiers
from game.core.registry import RegistryManager
from ui.builder.layer_panel import LayerPanel
from ui.builder.structure_list_items import LayerHeaderItem, LayerComponentItem, IndividualComponentItem

class TestStructureVisibility(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        # Clear registry before loading to ensure clean state
        RegistryManager.instance().clear()
        initialize_ship_data()
        load_components()
        load_modifiers()
    
    @classmethod
    def tearDownClass(cls):
        # Clean up registry after tests to prevent pollution of other tests
        RegistryManager.instance().clear()
        pygame.quit()

    def setUp(self):
        pygame.init()
        pygame.font.init()
        RegistryManager.instance().clear()
        initialize_ship_data()
        load_components()
        load_modifiers()

        # Patch UI elements in the structure_list_items namespace
        self.item_uipanel_patch = patch('ui.builder.structure_list_items.UIPanel')
        self.item_uilabel_patch = patch('ui.builder.structure_list_items.UILabel')
        self.item_uiimage_patch = patch('ui.builder.structure_list_items.UIImage')
        self.item_uibutton_patch = patch('ui.builder.structure_list_items.UIButton')
        
        # Patch UI elements in the layer_panel namespace
        self.panel_uipanel_patch = patch('ui.builder.layer_panel.UIPanel')
        self.panel_uilabel_patch = patch('ui.builder.layer_panel.UILabel')
        self.panel_uiscroll_patch = patch('ui.builder.layer_panel.UIScrollingContainer')
        self.panel_uidropdown_patch = patch('ui.builder.layer_panel.UIDropDownMenu')
        
        self.item_uipanel_patch.start()
        self.item_uilabel_patch.start()
        self.item_uiimage_patch.start()
        self.item_uibutton_patch.start()
        
        self.panel_uipanel_patch.start()
        self.panel_uilabel_patch.start()
        self.panel_uiscroll_patch.start()
        self.panel_uidropdown_patch.start()

        # Mock UIManager
        self.mock_manager = MagicMock(spec=pygame_gui.UIManager)
        
        # Configure mock manager to return proper values for font dimensions
        mock_rect = pygame.Rect(0, 0, 100, 20)
        mock_font = MagicMock()
        mock_font.get_rect.return_value = mock_rect
        self.mock_manager.get_theme.return_value.get_font.return_value = mock_font
        
        # Mock Builder
        self.mock_builder = MagicMock()
        self.ship = Ship("Test Escort", 0, 0, (255, 255, 255), ship_class="Escort")
        self.mock_builder.ship = self.ship
        
        # Mock SpriteManager
        dummy_surf = pygame.Surface((32, 32))
        self.mock_builder.sprite_mgr.get_sprite.return_value = dummy_surf
        self.mock_builder.selected_components = []
        
        # Create LayerPanel
        self.panel_rect = pygame.Rect(0, 0, 300, 600)
        self.layer_panel = LayerPanel(self.mock_builder, self.mock_manager, self.panel_rect)

    def tearDown(self):
        self.item_uipanel_patch.stop()
        self.item_uilabel_patch.stop()
        self.item_uiimage_patch.stop()
        self.item_uibutton_patch.stop()
        self.panel_uipanel_patch.stop()
        self.panel_uilabel_patch.stop()
        self.panel_uiscroll_patch.stop()
        self.panel_uidropdown_patch.stop()
        pygame.quit()

    def test_hull_is_hidden_from_structure_list(self):
        """Verify that hull components are not rendered in the structure list."""
        self.layer_panel.rebuild()
        
        hull_items = []
        for item in self.layer_panel.items:
            # Check Group Items
            if isinstance(item, LayerComponentItem):
                g_id = item.group_key[0] if isinstance(item.group_key, tuple) else item.group_key
                if g_id.startswith('hull_'):
                    hull_items.append(item)
            # Check Individual Items
            elif isinstance(item, IndividualComponentItem):
                if item.component.id.startswith('hull_'):
                    hull_items.append(item)
                    
        self.assertEqual(len(hull_items), 0, "Hull items detected in structure list!")

    def test_headers_remain_visible_with_hidden_hull(self):
        """Verify that layer headers are visible even if only a hidden hull exists in that layer."""
        self.layer_panel.rebuild()
        
        # Check for CORE layer header (which contains the hull_escort)
        core_header = next((i for i in self.layer_panel.items 
                           if isinstance(i, LayerHeaderItem) and i.layer_type == LayerType.CORE), None)
        
        self.assertIsNotNone(core_header, "CORE layer header is missing despite containing a (hidden) hull!")
        
    def test_structure_list_shows_all_available_layers(self):
        """Verify that all layers defined in the ship's layer config are shown."""
        self.layer_panel.rebuild()
        
        headers = [i for i in self.layer_panel.items if isinstance(i, LayerHeaderItem)]
        detected_layers = [h.layer_type for h in headers]
        
        # Ship class Escort has CORE, OUTER, ARMOR
        # We check at least CORE and OUTER which are in Capital_Escort config.
        self.assertIn(LayerType.CORE, detected_layers)
        self.assertIn(LayerType.OUTER, detected_layers)

if __name__ == '__main__':
    unittest.main()
