import pytest
from unittest.mock import MagicMock, patch
import pygame
import pygame_gui

from game.simulation.entities.ship import Ship


class TestBug04Display:
    @pytest.fixture
    def mock_builder(self):
        builder = MagicMock()
        builder.ship = MagicMock(spec=Ship)
        builder.ship.name = "Test Ship"
        builder.ship.ship_class = "Frigate"
        builder.ship.layers = {}
        builder.ship.mass_limits_ok = True
        builder.ship.get_missing_requirements.return_value = []
        builder.ship.get_validation_warnings.return_value = []
        builder.ship.ai_strategy = "standard_ranged"
        builder.ship.mass = 1000

        # Mock theme manager
        builder.theme_manager = MagicMock()
        builder.theme_manager.get_available_themes.return_value = ["Federation"]

        return builder

    def test_stats_rebuild_leaves_hashes(self, mock_builder):
        """
        Reproduce BUG-04: When `rebuild_stats` is called (due to new resource keys),
        the stats display remains at "--" because update is not called.

        PROJ-80: Stats logic now delegated to DesignStatsPanel.needs_rebuild().
        """
        # All patches applied inside the test to avoid circular import at decorator time
        # The circular import chain is: ui.builder -> game.ui -> builder_screen -> ui.builder
        with patch('game.ui.screens.builder.right_panel.UIPanel'), \
             patch('game.ui.screens.builder.right_panel.UILabel'), \
             patch('game.ui.screens.builder.right_panel.UITextEntryLine'), \
             patch('game.ui.screens.builder.right_panel.UIDropDownMenu'), \
             patch('game.ui.screens.builder.right_panel.UITextBox'), \
             patch('game.ui.screens.builder.right_panel.UIImage'), \
             patch('game.ui.screens.builder.right_panel.pygame_gui.elements.UIScrollingContainer'), \
             patch('game.ui.panels.design_stats_panel.UILabel'), \
             patch('game.ui.panels.design_stats_panel.UITextBox'), \
             patch('game.ui.panels.design_stats_panel.UIScrollingContainer'), \
             patch('game.ui.screens.builder.stats_config.get_logistics_rows') as mock_get_inv, \
             patch('game.ui.screens.builder.stats_config.get_construction_rows', return_value=[]), \
             patch('game.ui.screens.builder.stats_config.STATS_CONFIG', new={}), \
             patch('game.ui.screens.builder.right_panel.BuilderRightPanel.update_portrait_image'):

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

            panel = BuilderRightPanel(mock_builder, manager, rect)

            # Let's spy on update_stats_display
            with patch.object(panel, 'update_stats_display') as spy_update:
                # PROJ-80: Now we need to patch stats_panel.needs_rebuild() and stats_panel.rebuild()
                with patch.object(panel.stats_panel, 'needs_rebuild', return_value=False) as spy_needs_rebuild:
                    with patch.object(panel.stats_panel, 'rebuild') as spy_panel_rebuild:

                        # 1. Trigger update with SAME keys (needs_rebuild returns False)
                        panel.on_ship_updated(mock_builder.ship)

                        spy_update.assert_called()
                        spy_panel_rebuild.assert_not_called()

                        spy_update.reset_mock()
                        spy_panel_rebuild.reset_mock()

                # 2. Trigger update with NEW keys (needs_rebuild returns True)
                with patch.object(panel.stats_panel, 'needs_rebuild', return_value=True) as spy_needs_rebuild:
                    with patch.object(panel.stats_panel, 'rebuild') as spy_panel_rebuild:

                        # This should trigger rebuild because needs_rebuild returns True
                        panel.on_ship_updated(mock_builder.ship)

                        spy_panel_rebuild.assert_called()

                        # THE BUG FIX: update_stats_display should ALWAYS be called,
                        # even after rebuild, to populate the values
                        spy_update.assert_called()
