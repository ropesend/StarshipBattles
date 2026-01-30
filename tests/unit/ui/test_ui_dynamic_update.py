import pytest
from unittest.mock import MagicMock, patch
import pygame
import os
import sys

# Ensure project root is in path


from game.simulation.entities.ship import Ship
from game.ui.screens.builder.right_panel import BuilderRightPanel


class TestUIDynamicUpdate:

    @pytest.fixture(autouse=True)
    def setup_builder(self, fresh_registries):
        """Setup builder and manager for each test."""
        # Note: pygame and registry initialization handled by conftest fixtures
        # pygame.init() and pygame.display are managed at session scope

        builder = MagicMock()
        builder.theme_manager.get_available_themes.return_value = ["Federation"]

        # Use real Ship (no reload)
        test_ship = Ship("Test Ship", 0, 0, (255,255,255), registries=fresh_registries)
        builder.ship = test_ship

        # MVVM: viewmodel must return the same ship for refactored panels
        builder.viewmodel.ship = test_ship

        manager = MagicMock()

        self.builder = builder
        self.test_ship = test_ship
        self.manager = manager

        yield

        # Note: pygame and registry cleanup is handled by conftest fixtures
        # (pygame_display_reset and reset_game_state)
        # DO NOT call pygame.quit() here as it conflicts with session-level fixture

    @patch('pygame_gui.elements.UIScrollingContainer')
    @patch('pygame_gui.elements.UIImage')
    @patch('pygame_gui.elements.UITextBox')
    @patch('pygame_gui.elements.UIDropDownMenu')
    @patch('pygame_gui.elements.UITextEntryLine')
    @patch('pygame_gui.elements.UILabel')
    def test_dynamic_row_addition(self, mock_label, mock_entry, mock_drop, mock_box, mock_img, mock_scroll_container):
        """Test that adding a resource triggers a UI rebuild to show the new row."""

        # PROJ-46/51: Import path updated from ui.builder.right_panel
        import game.ui.screens.builder.right_panel
        import importlib
        import sys
        if 'game.ui.screens.builder.right_panel' in sys.modules:
            importlib.reload(sys.modules['game.ui.screens.builder.right_panel'])

        # 1. Create Panel with NO resources (ensure ship is empty initially)
        self.builder.ship.resources.reset_stats()

        panel = BuilderRightPanel(self.builder, self.manager, pygame.Rect(0,0,400,600))

        # Confirm no fuel rows
        assert 'max_fuel' not in panel.rows_map

        # 2. Add Resource (Simulate adding a component)
        # We need to simulate the ship logic that adds capacity.
        # Since we use real Ship logic, we can just register storage directly on the registry,
        # mimicking what ShipStatsCalculator would do.
        self.builder.ship.resources.register_storage('fuel', 100)

        # 3. Trigger Update
        panel.on_ship_updated(self.builder.ship)

        # 4. Verify Row Exists
        # This checks that on_ship_updated rebuilds the structure when keys change
        assert 'max_fuel' in panel.rows_map, "Fuel row should appear after adding fuel storage"
