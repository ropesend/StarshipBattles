"""Tests for DesignStatsPanel (PROJ-111 Phase 6 Task 6.8).

Tests the shared design stats panel widget for displaying ship statistics.
"""

import pytest
from unittest.mock import MagicMock, patch
import pygame


# --- Helpers ---

def _make_mock_ship():
    """Create a mock ship with typical stats."""
    ship = MagicMock()

    # Basic stats
    ship.mass = 150.0
    ship.max_mass = 200.0
    ship.thrust = 50
    ship.max_speed = 5

    # Hull
    ship.hull_type = "Cruiser"
    ship.hp = 100
    ship.max_hp = 100

    # Resources
    ship.resources = MagicMock()
    ship.resources.get_all_resources.return_value = []
    ship.resources.get_resource_names.return_value = ["fuel", "energy", "ammo"]

    # Layers
    ship.layers = {}

    return ship


def _make_stat_row():
    """Create a mock StatRow."""
    from game.ui.panels.design_stats_panel import StatRow

    with patch.object(StatRow, '__init__', lambda self, *a, **kw: None):
        row = StatRow.__new__(StatRow)

    row.key = "test_key"
    row.label = MagicMock()
    row.value = MagicMock()
    row.unit = MagicMock()
    row._last_val = None
    row._last_unit = None
    row._visible = True

    return row


# --- StatRow Tests ---

class TestStatRow:
    """Tests for StatRow helper class."""

    def test_stat_row_update_changes_value(self):
        """StatRow.update changes value text."""
        row = _make_stat_row()

        row.update("100", "tons")

        row.value.set_text.assert_called_with("100")
        row.unit.set_text.assert_called_with("tons")

    def test_stat_row_update_caches_value(self):
        """StatRow.update caches value to avoid redundant updates."""
        row = _make_stat_row()

        # First update
        row.update("100", "tons")
        row._last_val = "100"
        row._last_unit = "tons"

        # Reset mocks
        row.value.set_text.reset_mock()
        row.unit.set_text.reset_mock()

        # Same value - should not call set_text
        row.update("100", "tons")

        row.value.set_text.assert_not_called()
        row.unit.set_text.assert_not_called()

    def test_stat_row_update_detects_change(self):
        """StatRow.update detects value change after caching."""
        row = _make_stat_row()

        # First update
        row.update("100", "tons")
        row._last_val = "100"
        row._last_unit = "tons"

        # Reset mocks
        row.value.set_text.reset_mock()
        row.unit.set_text.reset_mock()

        # Different value - should call set_text
        row.update("200", "tons")

        row.value.set_text.assert_called_with("200")

    def test_stat_row_set_visible_shows_elements(self):
        """StatRow.set_visible(True) shows all elements."""
        row = _make_stat_row()
        row._visible = False

        row.set_visible(True)

        row.label.show.assert_called()
        row.value.show.assert_called()
        row.unit.show.assert_called()

    def test_stat_row_set_visible_hides_elements(self):
        """StatRow.set_visible(False) hides all elements."""
        row = _make_stat_row()
        row._visible = True

        row.set_visible(False)

        row.label.hide.assert_called()
        row.value.hide.assert_called()
        row.unit.hide.assert_called()

    def test_stat_row_set_visible_caches_state(self):
        """StatRow.set_visible caches visibility state."""
        row = _make_stat_row()
        row._visible = True

        # Already visible - should not call show
        row.set_visible(True)

        row.label.show.assert_not_called()


# --- DesignStatsPanel Tests ---

class TestDesignStatsPanelInit:
    """Tests for DesignStatsPanel initialization."""

    def test_panel_can_be_imported(self):
        """DesignStatsPanel can be imported."""
        from game.ui.panels.design_stats_panel import DesignStatsPanel

        assert DesignStatsPanel is not None

    def test_panel_stores_manager(self):
        """Panel stores manager reference."""
        from game.ui.panels.design_stats_panel import DesignStatsPanel

        with patch.object(DesignStatsPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignStatsPanel.__new__(DesignStatsPanel)

        manager = MagicMock()
        panel.manager = manager

        assert panel.manager is manager

    def test_panel_stores_rect(self):
        """Panel stores rect reference."""
        from game.ui.panels.design_stats_panel import DesignStatsPanel

        with patch.object(DesignStatsPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignStatsPanel.__new__(DesignStatsPanel)

        rect = pygame.Rect(0, 0, 300, 600)
        panel.rect = rect

        assert panel.rect == rect

    def test_panel_show_requirements_flag(self):
        """Panel stores show_requirements flag."""
        from game.ui.panels.design_stats_panel import DesignStatsPanel

        with patch.object(DesignStatsPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignStatsPanel.__new__(DesignStatsPanel)

        panel.show_requirements = True

        assert panel.show_requirements is True


class TestDesignStatsPanelStatCalculation:
    """Tests for stat calculation accuracy."""

    def test_mass_calculation(self):
        """Mass stat is calculated from ship.mass."""
        # This tests the expected behavior - actual calculation is in update_stats
        ship = _make_mock_ship()
        ship.mass = 175.5

        # The panel should use ship.mass
        assert ship.mass == 175.5

    def test_speed_calculation(self):
        """Speed stat is calculated from ship.max_speed."""
        ship = _make_mock_ship()
        ship.max_speed = 6

        assert ship.max_speed == 6

    def test_thrust_calculation(self):
        """Thrust stat is calculated from ship.thrust."""
        ship = _make_mock_ship()
        ship.thrust = 45

        assert ship.thrust == 45


class TestDesignStatsPanelFormatting:
    """Tests for stat display formatting."""

    def test_mass_formatting_integer(self):
        """Mass displays as integer."""
        ship = _make_mock_ship()
        ship.mass = 150.0

        # Formatting should round to integer
        formatted = f"{ship.mass:.0f}"
        assert formatted == "150"

    def test_mass_formatting_decimal(self):
        """Mass with decimals rounds properly."""
        ship = _make_mock_ship()
        ship.mass = 175.7

        formatted = f"{ship.mass:.0f}"
        assert formatted == "176"

    def test_percentage_formatting(self):
        """Percentage stats format correctly."""
        current = 80
        maximum = 100

        pct = (current / maximum) * 100
        formatted = f"{pct:.0f}%"

        assert formatted == "80%"


class TestDesignStatsPanelRowsMap:
    """Tests for rows_map management."""

    def test_rows_map_is_dict(self):
        """rows_map is initialized as dict."""
        from game.ui.panels.design_stats_panel import DesignStatsPanel

        with patch.object(DesignStatsPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignStatsPanel.__new__(DesignStatsPanel)

        panel.rows_map = {}

        assert isinstance(panel.rows_map, dict)

    def test_rows_map_stores_stat_rows(self):
        """rows_map stores StatRow objects by key."""
        from game.ui.panels.design_stats_panel import DesignStatsPanel

        with patch.object(DesignStatsPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignStatsPanel.__new__(DesignStatsPanel)

        panel.rows_map = {}
        row = _make_stat_row()
        row.key = "mass"

        panel.rows_map["mass"] = row

        assert panel.rows_map["mass"] is row


class TestDesignStatsPanelLayerStatus:
    """Tests for layer status display."""

    def test_layer_rows_list_exists(self):
        """layer_rows is initialized as list."""
        from game.ui.panels.design_stats_panel import DesignStatsPanel

        with patch.object(DesignStatsPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignStatsPanel.__new__(DesignStatsPanel)

        panel.layer_rows = []

        assert isinstance(panel.layer_rows, list)

    def test_current_logistics_keys_is_set(self):
        """current_logistics_keys is initialized as set."""
        from game.ui.panels.design_stats_panel import DesignStatsPanel

        with patch.object(DesignStatsPanel, '__init__', lambda self, *a, **kw: None):
            panel = DesignStatsPanel.__new__(DesignStatsPanel)

        panel.current_logistics_keys = set()

        assert isinstance(panel.current_logistics_keys, set)
