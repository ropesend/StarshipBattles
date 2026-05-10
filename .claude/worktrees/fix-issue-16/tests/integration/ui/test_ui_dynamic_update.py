"""
Integration tests for dynamic UI updates in BuilderRightPanel.

Verifies that adding resources to a ship triggers on_ship_updated() to
rebuild the stats panel and show new logistics rows.

Replaces the old unit test (tests/unit/ui/test_ui_dynamic_update.py) which used
fragile module monkey-patching + importlib.reload() that contaminated other tests.
"""

import pytest
import pygame
from unittest.mock import MagicMock

from game.simulation.entities.ship import Ship
from game.ui.screens.builder.right_panel import BuilderRightPanel
from game.ui.services.vehicle_class_service import VehicleClassService


class TestUIDynamicUpdate:

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries, ui_manager):
        """Set up real pygame + pygame_gui environment and a mock builder."""
        self.manager = ui_manager

        self.ship = Ship("Test Ship", 0, 0, (255, 255, 255), registries=fresh_registries)

        builder = MagicMock()
        builder.ship = self.ship
        builder.viewmodel.ship = self.ship
        builder.theme_manager.get_available_themes.return_value = ["Federation"]
        self.builder = builder

        # PROJ-211: Create VehicleClassService for DI
        self.vehicle_class_service = VehicleClassService(fresh_registries)

        yield

    def test_dynamic_row_addition(self):
        """Adding a resource triggers a UI rebuild to show the new row."""
        # Create panel with NO resources
        self.ship.resources.reset_stats()
        # PROJ-211: Pass VehicleClassService for DI
        panel = BuilderRightPanel(
            self.builder, self.manager, pygame.Rect(0, 0, 500, 800),
            vehicle_class_service=self.vehicle_class_service
        )

        # Confirm no fuel rows initially
        assert 'max_fuel' not in panel.rows_map

        # Add fuel storage (simulates adding a component with ResourceStorage)
        self.ship.resources.register_storage('fuel', 100)

        # Trigger update — should rebuild stats to include the new fuel row
        panel.on_ship_updated(self.ship)

        # Verify fuel row now exists
        assert 'max_fuel' in panel.rows_map, "Fuel row should appear after adding fuel storage"
