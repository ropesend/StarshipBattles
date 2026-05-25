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
    def setup_mocks(self, fresh_registries):
        """Setup mocks and teardown for each test."""
        # Note: pygame and registry initialization is handled by conftest fixtures
        # (enforce_headless, pygame_display_reset, and reset_game_state)

        # PROJ-494 T2.16: 8-patch with-stack → 2× patch.multiple, one per module group.
        with patch.multiple(
            'game.ui.screens.builder.structure_list_items',
            UIPanel=MagicMock(),
            UILabel=MagicMock(),
            UIImage=MagicMock(),
            UIButton=MagicMock(),
        ), patch.multiple(
            'game.ui.screens.builder.layer_panel',
            UIPanel=MagicMock(),
            UILabel=MagicMock(),
            UIScrollingContainer=MagicMock(),
            UIDropDownMenu=MagicMock(),
        ):

            # Mock UIManager
            mock_manager = MagicMock(spec=pygame_gui.UIManager)

            # Configure mock manager to return proper values for font dimensions
            mock_rect = pygame.Rect(0, 0, 100, 20)
            mock_font = MagicMock()
            mock_font.get_rect.return_value = mock_rect
            mock_manager.get_theme.return_value.get_font.return_value = mock_font

            # Mock Builder
            mock_builder = MagicMock()
            ship = Ship("Test Escort", 0, 0, (255, 255, 255), ship_class="Escort", registries=fresh_registries)
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

    def test_same_component_in_multiple_layers_shows_in_both(self):
        """BUG-64: Same component type placed in different layers must show in each layer."""
        # Use a Cruiser which has INNER and OUTER layers (Capital_Standard config)
        ship = Ship("Test Cruiser", 0, 0, (255, 255, 255), ship_class="Cruiser", registries=self.ship._registries)
        self.mock_builder.ship = ship
        self.mock_builder.viewmodel.ship = ship
        self.mock_builder.viewmodel.show_hull_layer = False

        # Add a life_support to INNER
        from game.simulation.components.component import create_component
        comp_inner = create_component("life_support", registries=ship._registries)
        ship.add_component(comp_inner, LayerType.INNER)

        # Add a life_support to OUTER
        comp_outer = create_component("life_support", registries=ship._registries)
        ship.add_component(comp_outer, LayerType.OUTER)

        # Rebuild layer panel with new ship
        # Clear old cache since ship changed
        for item in self.layer_panel.ui_cache.values():
            item.kill()
        self.layer_panel.ui_cache = {}
        self.layer_panel.rebuild()

        # Count life_support group items - group_key is (component_id, modifiers_tuple)
        life_support_groups = [
            item for item in self.layer_panel.items
            if isinstance(item, LayerComponentItem)
            and isinstance(item.group_key, tuple)
            and item.group_key[0] == 'life_support'
        ]

        # There must be 2 separate group items (one per layer), not 1
        assert len(life_support_groups) == 2, (
            f"Expected 2 life_support groups (one per layer), got {len(life_support_groups)}. "
            "Same component type in different layers should have unique UI entries."
        )

    def test_structure_list_shows_all_available_layers(self):
        """Verify that all layers defined in the ship's layer config are shown."""
        self.layer_panel.rebuild()

        headers = [i for i in self.layer_panel.items if isinstance(i, LayerHeaderItem)]
        detected_layers = [h.layer_type for h in headers]

        # Ship class Escort has CORE, OUTER, ARMOR
        # We check at least CORE and OUTER which are in Capital_Escort config.
        assert LayerType.CORE in detected_layers
        assert LayerType.OUTER in detected_layers
