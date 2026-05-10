"""Tests for DesignStatsPanel (PROJ-111 Phase 6 Task 6.8).

Tests the shared design stats panel widget for displaying ship statistics.
"""

import pytest
from unittest.mock import MagicMock, patch


# --- Helpers ---

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
