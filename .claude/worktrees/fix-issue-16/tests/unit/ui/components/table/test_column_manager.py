"""Tests for TableColumnManager."""

import pytest


class TestTableColumnManager:
    """Tests for the TableColumnManager class."""

    def _sample_columns(self):
        """Return sample column definitions for testing."""
        return [
            {"id": "name", "label": "Name", "width": 100, "visible": True},
            {"id": "status", "label": "Status", "width": 80, "visible": True},
            {"id": "hidden", "label": "Hidden", "width": 50, "visible": False},
            {"id": "icon", "label": "Icon", "width": 60, "visible": True, "type": "image"},
        ]

    def test_constructor_deep_copies_columns(self):
        """Constructor should deep-copy columns to prevent mutation."""
        from game.ui.components.table.column_manager import TableColumnManager

        original_cols = self._sample_columns()
        manager = TableColumnManager(original_cols)

        # Modify original
        original_cols[0]["width"] = 999

        # Manager's copy should be unaffected
        cols = manager.get_columns()
        assert cols[0]["width"] == 100

    def test_get_columns_returns_all(self):
        """get_columns returns all columns including hidden."""
        from game.ui.components.table.column_manager import TableColumnManager

        manager = TableColumnManager(self._sample_columns())
        cols = manager.get_columns()

        assert len(cols) == 4
        assert cols[2]["id"] == "hidden"

    def test_get_visible_columns_filters_hidden(self):
        """get_visible_columns filters by visible=True."""
        from game.ui.components.table.column_manager import TableColumnManager

        manager = TableColumnManager(self._sample_columns())
        visible = manager.get_visible_columns()

        assert len(visible) == 3
        assert all(c["id"] != "hidden" for c in visible)

    def test_get_column_returns_correct_column(self):
        """get_column returns the correct column by ID."""
        from game.ui.components.table.column_manager import TableColumnManager

        manager = TableColumnManager(self._sample_columns())
        col = manager.get_column("status")

        assert col is not None
        assert col["id"] == "status"
        assert col["width"] == 80

    def test_get_column_returns_none_for_missing(self):
        """get_column returns None for non-existent ID."""
        from game.ui.components.table.column_manager import TableColumnManager

        manager = TableColumnManager(self._sample_columns())
        col = manager.get_column("nonexistent")

        assert col is None

    def test_toggle_column_toggles_visible(self):
        """toggle_column toggles the visible state."""
        from game.ui.components.table.column_manager import TableColumnManager

        manager = TableColumnManager(self._sample_columns())

        # Toggle hidden column to visible
        result = manager.toggle_column("hidden")
        assert result is True  # Now visible
        assert manager.get_column("hidden")["visible"] is True

        # Toggle back to hidden
        result = manager.toggle_column("hidden")
        assert result is False  # Now hidden
        assert manager.get_column("hidden")["visible"] is False

    def test_swap_column_moves_right(self):
        """swap_column(col, 1) moves column right."""
        from game.ui.components.table.column_manager import TableColumnManager

        manager = TableColumnManager(self._sample_columns())
        visible_before = [c["id"] for c in manager.get_visible_columns()]

        # Move 'name' right
        result = manager.swap_column("name", 1)

        assert result is True
        visible_after = [c["id"] for c in manager.get_visible_columns()]
        assert visible_after[0] == "status"
        assert visible_after[1] == "name"

    def test_swap_column_moves_left(self):
        """swap_column(col, -1) moves column left."""
        from game.ui.components.table.column_manager import TableColumnManager

        manager = TableColumnManager(self._sample_columns())

        # Move 'status' left
        result = manager.swap_column("status", -1)

        assert result is True
        visible = [c["id"] for c in manager.get_visible_columns()]
        assert visible[0] == "status"
        assert visible[1] == "name"

    def test_swap_column_returns_false_at_edges(self):
        """swap_column returns False when at first/last position."""
        from game.ui.components.table.column_manager import TableColumnManager

        manager = TableColumnManager(self._sample_columns())

        # Can't move first column left
        result = manager.swap_column("name", -1)
        assert result is False

        # Can't move last visible column right
        result = manager.swap_column("icon", 1)
        assert result is False

    def test_get_total_visible_width(self):
        """get_total_visible_width sums visible column widths."""
        from game.ui.components.table.column_manager import TableColumnManager

        manager = TableColumnManager(self._sample_columns())
        total = manager.get_total_visible_width()

        # name(100) + status(80) + icon(60) = 240
        assert total == 240

    def test_is_image_column_detects_image_type(self):
        """is_image_column checks for type='image'."""
        from game.ui.components.table.column_manager import TableColumnManager

        manager = TableColumnManager(self._sample_columns())

        assert manager.is_image_column("icon") is True
        assert manager.is_image_column("name") is False
        assert manager.is_image_column("nonexistent") is False

    def test_set_sort_sets_column_id(self):
        """set_sort sets sort_column_id."""
        from game.ui.components.table.column_manager import TableColumnManager

        manager = TableColumnManager(self._sample_columns())
        manager.set_sort("name")

        assert manager.sort_column_id == "name"
        assert manager.sort_descending is False

    def test_set_sort_same_column_toggles_direction(self):
        """Calling set_sort on same column toggles sort_descending."""
        from game.ui.components.table.column_manager import TableColumnManager

        manager = TableColumnManager(self._sample_columns())
        manager.set_sort("name")
        assert manager.sort_descending is False

        manager.set_sort("name")
        assert manager.sort_descending is True

        manager.set_sort("name")
        assert manager.sort_descending is False

    def test_set_sort_different_column_resets_direction(self):
        """Calling set_sort on different column resets sort_descending."""
        from game.ui.components.table.column_manager import TableColumnManager

        manager = TableColumnManager(self._sample_columns())
        manager.set_sort("name")
        manager.set_sort("name")  # Now descending
        assert manager.sort_descending is True

        manager.set_sort("status")  # Different column
        assert manager.sort_column_id == "status"
        assert manager.sort_descending is False

    def test_initial_sort_state(self):
        """Initial sort state should be None/False."""
        from game.ui.components.table.column_manager import TableColumnManager

        manager = TableColumnManager(self._sample_columns())

        assert manager.sort_column_id is None
        assert manager.sort_descending is False

    def test_toggle_nonexistent_column(self):
        """toggle_column on nonexistent column returns None."""
        from game.ui.components.table.column_manager import TableColumnManager

        manager = TableColumnManager(self._sample_columns())
        result = manager.toggle_column("nonexistent")

        assert result is None

    def test_swap_nonexistent_column(self):
        """swap_column on nonexistent column returns False."""
        from game.ui.components.table.column_manager import TableColumnManager

        manager = TableColumnManager(self._sample_columns())
        result = manager.swap_column("nonexistent", 1)

        assert result is False
