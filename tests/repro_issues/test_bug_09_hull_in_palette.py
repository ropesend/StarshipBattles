import os
import pygame
import pygame_gui
import pytest
from unittest.mock import MagicMock

# Set dummy video driver for headless testing
os.environ['SDL_VIDEODRIVER'] = 'dummy'

from game.simulation.entities.ship import Ship
from game.simulation.components.component import get_all_components
from game.ui.screens.builder.left_panel import BuilderLeftPanel


class TestBug09Reproduction:
    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        pygame.init()
        self.window_surface = pygame.display.set_mode((800, 600))
        self.ui_manager = pygame_gui.UIManager((800, 600))

        # Mock Builder
        self.mock_builder = MagicMock()
        # Escort class has 'hull_escort' as default hull
        self.ship = Ship("Test Escort", 0, 0, (255, 255, 255), ship_class="Escort",
                         registries=fresh_registries)
        self.mock_builder.ship = self.ship

        # Mock sprite manager
        dummy_surf = pygame.Surface((32, 32))
        self.mock_builder.sprite_mgr.get_sprite.return_value = dummy_surf
        self.mock_builder.available_components = get_all_components(registries=fresh_registries)

        # Create BuilderLeftPanel
        self.panel_rect = pygame.Rect(0, 0, 300, 600)
        self.left_panel = BuilderLeftPanel(self.mock_builder, self.ui_manager, self.panel_rect)

        yield

        pygame.quit()

    def test_hull_visibility_in_component_palette(self):
        """BUG-09: Hull components should NOT be visible in the Component Palette (Left Panel)."""
        # Trigger list update
        self.left_panel.update_component_list()

        # Check all items in the component list
        hull_items = []
        for item in self.left_panel.items:
            # item is ComponentListItem
            if item.component.type_str == "Hull" or item.component.id.startswith('hull_'):
                hull_items.append(item.component.id)

        # Assertion: No hull items should be present
        assert len(hull_items) == 0, \
            f"Found {len(hull_items)} hull components in the palette: {hull_items}"
