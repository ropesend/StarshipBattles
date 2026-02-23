"""
Integration tests for BuilderRightPanel stats rendering.

Verifies that BuilderRightPanel creates expected stat rows in rows_map
and that update_stats_display runs without error.

Replaces the old unit test (tests/unit/ui/test_stats_render.py) which used
fragile module monkey-patching + importlib.reload() that contaminated other tests.
"""

import pytest
import pygame
import pygame_gui
from unittest.mock import MagicMock

from game.simulation.entities.ship import Ship
from game.ui.screens.builder.right_panel import BuilderRightPanel


class TestStatsRender:

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        """Set up real pygame + pygame_gui environment and a mock builder."""
        pygame.init()
        screen = pygame.display.set_mode((1024, 768))
        self.manager = pygame_gui.UIManager((1024, 768))

        self.ship = Ship("Test Ship", 0, 0, (255, 255, 255), registries=fresh_registries)

        builder = MagicMock()
        builder.ship = self.ship
        builder.viewmodel.ship = self.ship
        builder.theme_manager.get_available_themes.return_value = ["Federation"]
        self.builder = builder

        yield

        pygame.quit()

    def test_stats_panel_creation_and_update(self):
        """BuilderRightPanel creates expected stat rows and updates without error."""
        panel = BuilderRightPanel(self.builder, self.manager, pygame.Rect(0, 0, 500, 800))

        # Verify key stat sections exist
        assert 'mass' in panel.rows_map
        assert 'max_speed' in panel.rows_map
        assert 'shield_regen' in panel.rows_map
        assert 'emissive_armor' in panel.rows_map
        assert 'targeting' in panel.rows_map
        assert 'crew_required' in panel.rows_map

        # Verify update runs without error
        panel.update_stats_display(self.ship)

    def test_logistics_section(self):
        """BuilderRightPanel shows logistics rows when ship has resources."""
        # Register fuel storage before creating the panel
        self.ship.resources.register_storage('fuel', 100)

        panel = BuilderRightPanel(self.builder, self.manager, pygame.Rect(0, 0, 500, 800))

        assert 'crew_required' in panel.rows_map
        assert 'max_fuel' in panel.rows_map
