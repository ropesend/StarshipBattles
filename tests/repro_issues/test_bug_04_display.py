from contextlib import ExitStack

import pytest
from unittest.mock import MagicMock, patch
import pygame
import pygame_gui

from game.simulation.entities.ship import Ship
from game.ui.services.vehicle_class_service import VehicleClassService


# PROJ-494 T2.12: 15-patch 4-level-nested setup from BUG-04 test now driven
# from a single declarative table consumed by a `patched_right_panel_imports`
# fixture. The imports stay inside the fixture (rather than module top) to
# avoid the circular-import chain documented in the original test body:
#     ui.builder -> game.ui -> builder_screen -> ui.builder
_RIGHT_PANEL_PATCH_TARGETS = (
    'game.ui.screens.builder.right_panel.UIPanel',
    'game.ui.screens.builder.right_panel.UILabel',
    'game.ui.screens.builder.right_panel.UITextEntryLine',
    'game.ui.screens.builder.right_panel.UIDropDownMenu',
    'game.ui.screens.builder.right_panel.UITextBox',
    'game.ui.screens.builder.right_panel.UIImage',
    'game.ui.screens.builder.right_panel.pygame_gui.elements.UIScrollingContainer',
    'game.ui.panels.design_stats_panel.UILabel',
    'game.ui.panels.design_stats_panel.UITextBox',
    'game.ui.panels.design_stats_panel.UIScrollingContainer',
    'game.ui.screens.builder.right_panel.BuilderRightPanel.update_portrait_image',
)


@pytest.fixture
def patched_right_panel_imports():
    """Stand up the 15-deep patch stack required by BUG-04. Yields the mock
    captured for `get_logistics_rows` so the test can configure its return.
    """
    with ExitStack() as stack:
        for target in _RIGHT_PANEL_PATCH_TARGETS:
            stack.enter_context(patch(target))
        mock_get_inv = stack.enter_context(
            patch('game.ui.screens.builder.stats_config.get_logistics_rows')
        )
        stack.enter_context(
            patch('game.ui.screens.builder.stats_config.get_construction_rows',
                  return_value=[])
        )
        stack.enter_context(
            patch('game.ui.screens.builder.stats_config.STATS_CONFIG', new={})
        )
        stack.enter_context(
            patch('game.ui.screens.builder.stats_config.SECTIONS_CONFIG', new={})
        )
        stack.enter_context(
            patch('game.ui.screens.builder.stats_config.ALWAYS_VISIBLE', new={})
        )
        yield mock_get_inv


class TestBug04Display:
    @pytest.fixture
    def mock_builder(self):
        builder = MagicMock()
        builder.ship = MagicMock(spec=Ship)
        builder.ship.name = "Test Ship"
        builder.ship.ship_class = "Frigate"
        builder.ship.theme_id = "Federation"
        builder.ship.vehicle_type = "Ship"
        builder.ship.layers = {}
        builder.ship.mass_limits_ok = True
        builder.ship.get_missing_requirements.return_value = []
        builder.ship.get_validation_warnings.return_value = []
        builder.ship.movement_policy = "kite_max"
        builder.ship.targeting_policy = "standard"
        builder.ship.design_role = "general_purpose"
        builder.ship.mass = 1000
        builder.ship.max_mass_budget = 2000

        # Mock theme manager
        builder.theme_manager = MagicMock()
        builder.theme_manager.get_available_themes.return_value = ["Federation"]

        return builder

    def test_stats_rebuild_leaves_hashes(
        self, mock_builder, mock_registries, patched_right_panel_imports,
    ):
        """
        Reproduce BUG-04: When `rebuild_stats` is called (due to new resource keys),
        the stats display remains at "--" because update is not called.

        PROJ-80: Stats logic now delegated to DesignStatsPanel.needs_rebuild().
        PROJ-211: Updated to pass VehicleClassService for DI.
        PROJ-494 T2.12: 15-patch 4-level setup moved to the
        `patched_right_panel_imports` fixture.
        """
        mock_get_inv = patched_right_panel_imports

        # Import here to avoid circular import at collection time
        from game.ui.screens.builder.right_panel import BuilderRightPanel

        # Setup
        manager = MagicMock()
        rect = pygame.Rect(0, 0, 100, 100)

        # Mock get_logistics_rows to simulate changing keys
        # Initial state: No resources
        row_mock = MagicMock()
        row_mock.key = "power"  # Pretend we always have power
        mock_get_inv.return_value = [row_mock]

        # PROJ-211: Create VehicleClassService for DI
        vehicle_class_service = VehicleClassService(mock_registries)
        panel = BuilderRightPanel(
            mock_builder, manager, rect,
            vehicle_class_service=vehicle_class_service,
        )

        # Let's spy on update_stats_display
        with patch.object(panel, 'update_stats_display') as spy_update:
            # PROJ-80: Now we need to patch stats_panel.needs_rebuild() and stats_panel.rebuild()
            with patch.object(panel.stats_panel, 'needs_rebuild', return_value=False):
                with patch.object(panel.stats_panel, 'rebuild') as spy_panel_rebuild:
                    # 1. Trigger update with SAME keys (needs_rebuild returns False)
                    panel.on_ship_updated(mock_builder.ship)

                    spy_update.assert_called()
                    spy_panel_rebuild.assert_not_called()

                    spy_update.reset_mock()
                    spy_panel_rebuild.reset_mock()

            # 2. Trigger update with NEW keys (needs_rebuild returns True)
            with patch.object(panel.stats_panel, 'needs_rebuild', return_value=True):
                with patch.object(panel.stats_panel, 'rebuild') as spy_panel_rebuild:
                    # This should trigger rebuild because needs_rebuild returns True
                    panel.on_ship_updated(mock_builder.ship)

                    spy_panel_rebuild.assert_called()

                    # THE BUG FIX: update_stats_display should ALWAYS be called,
                    # even after rebuild, to populate the values
                    spy_update.assert_called()
