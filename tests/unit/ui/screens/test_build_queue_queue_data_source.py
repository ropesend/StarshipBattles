"""Tests for BuildQueueQueueDataSource (PROJ-221 Phase 3).

Verifies the ITableDataSource implementation for per-planet build queues:
- Row count from queue length
- Cell value formatting for all column types
- Portrait image loading
- Queue switching via set_queue()
- Column definitions
"""

import pytest
from unittest.mock import MagicMock

from game.ui.screens.build_queue_queue_data_source import (
    BuildQueueQueueDataSource,
    BUILD_QUEUE_COLUMNS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_queue_item(
    design_id="Cruiser Mk I",
    item_type="ship",
    turns_remaining=5.0,
    total_cost=None,
    resources_consumed=None,
):
    """Create a sample queue item dict."""
    if total_cost is None:
        total_cost = {
            "Metals": 6000.0,
            "Organics": 1500.0,
            "Vapors": 3000.0,
            "Radioactives": 0.0,
            "Exotics": 0.0,
        }
    if resources_consumed is None:
        resources_consumed = {
            "Metals": 0.0,
            "Organics": 0.0,
            "Vapors": 0.0,
            "Radioactives": 0.0,
            "Exotics": 0.0,
        }
    return {
        "design_id": design_id,
        "type": item_type,
        "turns_remaining": turns_remaining,
        "total_cost": total_cost,
        "resources_consumed": resources_consumed,
    }


def _make_build_rate():
    """Create a sample build rate dict."""
    return {
        "Metals": 3000.0,
        "Organics": 3000.0,
        "Vapors": 3000.0,
        "Radioactives": 3000.0,
        "Exotics": 3000.0,
    }


def _make_data_source(queue=None, build_rate=None):
    """Create a BuildQueueQueueDataSource with mock portrait loader."""
    if queue is None:
        queue = [
            _make_queue_item("Cruiser Mk I", "ship", 5.0),
            _make_queue_item("Fighter Bay", "complex", 2.5),
            _make_queue_item("Destroyer X", "ship", 10.0),
        ]
    if build_rate is None:
        build_rate = _make_build_rate()

    portrait_loader = MagicMock()
    portrait_loader.load_queue_item_portrait = MagicMock(return_value=None)

    ds = BuildQueueQueueDataSource(
        columns=BUILD_QUEUE_COLUMNS,
        portrait_loader=portrait_loader,
        build_rate=build_rate,
    )
    ds.set_queue(queue, build_rate)
    return ds, portrait_loader


# =======================================================================
# Column Definition Tests
# =======================================================================

class TestBuildQueueColumns:
    """BUILD_QUEUE_COLUMNS should have correct structure."""

    def test_all_columns_have_required_fields(self):
        """Each column must have id, title, width, visible."""
        for col in BUILD_QUEUE_COLUMNS:
            assert "id" in col, f"Column missing 'id': {col}"
            assert "title" in col, f"Column missing 'title': {col}"
            assert "width" in col, f"Column missing 'width': {col}"
            assert "visible" in col, f"Column missing 'visible': {col}"

    def test_column_ids_are_unique(self):
        """Column IDs must be unique."""
        ids = [col["id"] for col in BUILD_QUEUE_COLUMNS]
        assert len(ids) == len(set(ids)), f"Duplicate column IDs: {ids}"

    def test_expected_columns_present(self):
        """Expected columns should be present."""
        ids = {col["id"] for col in BUILD_QUEUE_COLUMNS}
        expected = {"order", "item", "turns", "met_rate", "org_rate", "vap_rate",
                    "rad_rate", "exo_rate", "met_rem", "org_rem", "vap_rem",
                    "rad_rem", "exo_rem"}
        for col_id in expected:
            assert col_id in ids, f"Missing expected column: {col_id}"


# =======================================================================
# Row Count Tests
# =======================================================================

class TestRowCount:
    """get_row_count() should return queue length."""

    def test_row_count_returns_queue_length(self):
        """Row count should equal number of queue items."""
        ds, _ = _make_data_source()
        assert ds.get_row_count() == 3

    def test_row_count_empty_queue(self):
        """Empty queue should return 0."""
        ds, _ = _make_data_source(queue=[])
        assert ds.get_row_count() == 0


# =======================================================================
# Cell Value Tests
# =======================================================================

class TestCellValues:
    """get_cell_value() should return correct formatted values."""

    def test_order_column_first_item(self):
        """Order column for first item should be '1'."""
        ds, _ = _make_data_source()
        assert ds.get_cell_value(0, "order") == "1"

    def test_order_column_third_item(self):
        """Order column for third item should be '3'."""
        ds, _ = _make_data_source()
        assert ds.get_cell_value(2, "order") == "3"

    def test_item_column(self):
        """Item column should show design_id (type)."""
        ds, _ = _make_data_source()
        result = ds.get_cell_value(0, "item")
        assert "Cruiser Mk I" in result
        assert "ship" in result

    def test_turns_column(self):
        """Turns column should show turns_remaining."""
        ds, _ = _make_data_source()
        result = ds.get_cell_value(0, "turns")
        assert "5" in result

    def test_met_rate_column(self):
        """Met/t column should show per-turn Metals spend."""
        ds, _ = _make_data_source()
        result = ds.get_cell_value(0, "met_rate")
        # With costs: Metals=6000, Organics=1500, Vapors=3000
        # Rates: all 3000/turn
        # Limiting: Metals 6000/3000 = 2 turns
        # Met spend = 6000/2 = 3000
        assert result == "3,000"

    def test_org_rate_column(self):
        """Org/t column should show proportional Organics spend for first item.

        With queue-wide distribution (BUG-98): item 1 is Metals-limited
        (6000/3000 = 2 turns). Resources consumed proportionally:
        Organics = 1500/2 = 750 per turn.
        """
        ds, _ = _make_data_source()
        result = ds.get_cell_value(0, "org_rate")
        assert result == "750"

    def test_met_rem_column(self):
        """Met remaining column should show remaining cost."""
        ds, _ = _make_data_source()
        result = ds.get_cell_value(0, "met_rem")
        # Remaining: 6000 - 0 = 6000
        assert result == "6,000"

    def test_zero_remaining_shows_dash(self):
        """Zero remaining cost should show '-'."""
        item = _make_queue_item(
            total_cost={"Metals": 100.0, "Organics": 0.0, "Vapors": 0.0,
                        "Radioactives": 0.0, "Exotics": 0.0},
            resources_consumed={"Metals": 0.0, "Organics": 0.0, "Vapors": 0.0,
                                "Radioactives": 0.0, "Exotics": 0.0},
        )
        ds, _ = _make_data_source(queue=[item])
        result = ds.get_cell_value(0, "org_rem")
        assert result == "-"

    def test_zero_rate_shows_dash(self):
        """Zero per-turn spend should show '-'."""
        item = _make_queue_item(
            total_cost={"Metals": 100.0, "Organics": 0.0, "Vapors": 0.0,
                        "Radioactives": 0.0, "Exotics": 0.0},
            resources_consumed={"Metals": 0.0, "Organics": 0.0, "Vapors": 0.0,
                                "Radioactives": 0.0, "Exotics": 0.0},
        )
        ds, _ = _make_data_source(queue=[item])
        result = ds.get_cell_value(0, "org_rate")
        assert result == "-"


# =======================================================================
# Cell Image Tests
# =======================================================================

class TestCellImages:
    """get_cell_image() should return images for portrait column."""

    def test_portrait_column_calls_loader(self):
        """Portrait column should call portrait loader."""
        ds, loader = _make_data_source()
        mock_surface = MagicMock()
        loader.load_queue_item_portrait.return_value = mock_surface

        result = ds.get_cell_image(0, "portrait")

        assert result == mock_surface
        loader.load_queue_item_portrait.assert_called()

    def test_non_portrait_column_returns_none(self):
        """Non-portrait column should return None."""
        ds, _ = _make_data_source()
        result = ds.get_cell_image(0, "item")
        assert result is None


# =======================================================================
# Column Access Tests
# =======================================================================

class TestGetColumns:
    """get_columns() should return deep copy of columns."""

    def test_returns_columns(self):
        """get_columns() should return column list."""
        ds, _ = _make_data_source()
        cols = ds.get_columns()
        assert len(cols) > 0

    def test_returns_deep_copy(self):
        """Modifying returned columns should not affect source."""
        ds, _ = _make_data_source()
        cols = ds.get_columns()
        original_id = cols[0]["id"]
        cols[0]["id"] = "modified"

        # Re-fetch should be unchanged
        cols2 = ds.get_columns()
        assert cols2[0]["id"] == original_id


# =======================================================================
# Queue Switch Tests
# =======================================================================

class TestSetQueue:
    """set_queue() should update the active queue and build rate."""

    def test_set_queue_updates_row_count(self):
        """set_queue() should change row count."""
        ds, _ = _make_data_source()
        assert ds.get_row_count() == 3

        new_queue = [_make_queue_item("New Ship", "ship", 1.0)]
        ds.set_queue(new_queue, _make_build_rate())
        assert ds.get_row_count() == 1

    def test_set_queue_updates_cell_values(self):
        """set_queue() should affect subsequent get_cell_value() calls."""
        ds, _ = _make_data_source()
        assert "Cruiser" in ds.get_cell_value(0, "item")

        new_queue = [_make_queue_item("Battleship Alpha", "ship", 1.0)]
        ds.set_queue(new_queue, _make_build_rate())
        assert "Battleship Alpha" in ds.get_cell_value(0, "item")
