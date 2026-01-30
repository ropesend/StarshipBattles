import pytest
from unittest.mock import MagicMock, patch
import os
import sys
import pygame
import pygame_gui

# Set dummy video driver for headless testing
os.environ['SDL_VIDEODRIVER'] = 'dummy'



from game.simulation.entities.ship import Ship, LayerType
from game.ui.screens.builder.layer_panel import LayerPanel
from game.ui.screens.builder.structure_list_items import LayerHeaderItem, LayerComponentItem, IndividualComponentItem


class TestStructureVisibility:
    # Class-level setup removed to ensure per-test isolation
    # setUpClass / tearDownClass removed

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Setup mocks and teardown for each test."""
        # Note: pygame and registry initialization is handled by conftest fixtures
        # (enforce_headless, pygame_display_reset, and reset_game_state)

        # Patch UI elements in the structure_list_items namespace
        with patch('ui.builder.structure_list_items.UIPanel') as item_uipanel_patch, \
             patch('ui.builder.structure_list_items.UILabel') as item_uilabel_patch, \
             patch('ui.builder.structure_list_items.UIImage') as item_uiimage_patch, \
             patch('ui.builder.structure_list_items.UIButton') as item_uibutton_patch, \
             patch('ui.builder.layer_panel.UIPanel') as panel_uipanel_patch, \
             patch('ui.builder.layer_panel.UILabel') as panel_uilabel_patch, \
             patch('ui.builder.layer_panel.UIScrollingContainer') as panel_uiscroll_patch, \
             patch('ui.builder.layer_panel.UIDropDownMenu') as panel_uidropdown_patch:

            # Mock UIManager
            mock_manager = MagicMock(spec=pygame_gui.UIManager)

            # Configure mock manager to return proper values for font dimensions
            mock_rect = pygame.Rect(0, 0, 100, 20)
            mock_font = MagicMock()
            mock_font.get_rect.return_value = mock_rect
            mock_manager.get_theme.return_value.get_font.return_value = mock_font

            # Mock Builder
            mock_builder = MagicMock()
            ship = Ship("Test Escort", 0, 0, (255, 255, 255), ship_class="Escort")
            mock_builder.ship = ship

            # MVVM: viewmodel must return the same ship/selected_components for refactored panels
            mock_builder.viewmodel.ship = ship
            mock_builder.viewmodel.selected_components = []

            # Mock SpriteManager
            dummy_surf = pygame.Surface((32, 32))
            mock_builder.sprite_mgr.get_sprite.return_value = dummy_surf
            mock_builder.selected_components = []

            # Create LayerPanel
            panel_rect = pygame.Rect(0, 0, 300, 600)
            layer_panel = LayerPanel(mock_builder, mock_manager, panel_rect)

            # Store references for tests
            self.mock_builder = mock_builder
            self.mock_manager = mock_manager
            self.ship = ship
            self.layer_panel = layer_panel

            yield

        # Note: pygame and registry cleanup is handled by conftest fixtures
        # (pygame_display_reset and reset_game_state)
        # DO NOT call pygame.quit() here as it conflicts with session-level fixture

    def test_hull_is_hidden_from_structure_list_by_default(self):
        """Verify that hull components are not rendered when show_hull_layer=False (default)."""
        # Ensure default state
        self.mock_builder.viewmodel.show_hull_layer = False
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
            # Check Headers
            elif isinstance(item, LayerHeaderItem):
                if item.layer_type == LayerType.HULL:
                    hull_items.append(item)

        assert len(hull_items) == 0, "Hull items detected in structure list when show_hull_layer=False!"

    def test_hull_is_shown_when_toggle_enabled(self):
        """Verify that hull layer and components are shown when show_hull_layer=True."""
        # Enable hull visibility
        self.mock_builder.viewmodel.show_hull_layer = True
        self.layer_panel.rebuild()

        # Check for HULL layer header
        hull_header = next((i for i in self.layer_panel.items
                           if isinstance(i, LayerHeaderItem) and i.layer_type == LayerType.HULL), None)

        assert hull_header is not None, "HULL layer header should be visible when show_hull_layer=True!"

        # Check for hull component (should be at least one)
        hull_components = []
        for item in self.layer_panel.items:
            if isinstance(item, LayerComponentItem):
                g_id = item.group_key[0] if isinstance(item.group_key, tuple) else item.group_key
                if g_id.startswith('hull_'):
                    hull_components.append(item)
            elif isinstance(item, IndividualComponentItem):
                if item.component.id.startswith('hull_'):
                    hull_components.append(item)

        assert len(hull_components) > 0, "Hull component should be visible when show_hull_layer=True!"

    def test_headers_remain_visible_with_hidden_hull(self):
        """Verify that layer headers are visible even if only a hidden hull exists in that layer."""
        self.layer_panel.rebuild()

        # Check for CORE layer header (which contains the hull_escort)
        core_header = next((i for i in self.layer_panel.items
                           if isinstance(i, LayerHeaderItem) and i.layer_type == LayerType.CORE), None)

        assert core_header is not None, "CORE layer header is missing despite containing a (hidden) hull!"

    def test_structure_list_shows_all_available_layers(self):
        """Verify that all layers defined in the ship's layer config are shown."""
        self.layer_panel.rebuild()

        headers = [i for i in self.layer_panel.items if isinstance(i, LayerHeaderItem)]
        detected_layers = [h.layer_type for h in headers]

        # Ship class Escort has CORE, OUTER, ARMOR
        # We check at least CORE and OUTER which are in Capital_Escort config.
        assert LayerType.CORE in detected_layers
        assert LayerType.OUTER in detected_layers
