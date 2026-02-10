"""
Tests for ColumnManager - manages column configuration and ordering.

PROJ-44 Phase 7 Task 7.4: FleetReportWindow refactoring.
"""
import pytest


class TestColumnManager:
    """Test ColumnManager column configuration and visibility."""

    @pytest.fixture
    def manager(self):
        """Create ColumnManager instance with default columns."""
        from game.ui.screens.column_manager import ColumnManager
        return ColumnManager()

    @pytest.fixture
    def custom_columns(self):
        """Create custom column configuration."""
        return [
            {'id': 'col_a', 'width': 100, 'title': 'Column A', 'visible': True},
            {'id': 'col_b', 'width': 150, 'title': 'Column B', 'visible': True},
            {'id': 'col_c', 'width': 80, 'title': 'Column C', 'visible': False},
        ]

    def test_default_columns(self, manager):
        """Default columns are set for fleet report."""
        columns = manager.get_columns()
        assert len(columns) >= 5  # At least portrait, topdown, serial, design, name
        # Check required columns exist
        ids = [c['id'] for c in columns]
        assert 'serial' in ids
        assert 'name' in ids
        assert 'hp_pct' in ids

    def test_get_visible_columns(self, manager):
        """get_visible_columns returns only visible columns."""
        visible = manager.get_visible_columns()
        for col in visible:
            assert col.get('visible', True) is True

    def test_toggle_column_visibility(self, manager):
        """Toggle column visibility."""
        # Find a visible column
        columns = manager.get_visible_columns()
        col_id = columns[-1]['id']  # Use last visible column

        # Toggle off
        manager.toggle_column(col_id)
        col = manager.get_column(col_id)
        assert col['visible'] is False

        # Toggle on
        manager.toggle_column(col_id)
        col = manager.get_column(col_id)
        assert col['visible'] is True

    def test_get_column_by_id(self, manager):
        """Get column by ID."""
        col = manager.get_column('serial')
        assert col is not None
        assert col['id'] == 'serial'
        assert 'width' in col
        assert 'title' in col

    def test_get_column_not_found(self, manager):
        """Get column returns None for unknown ID."""
        col = manager.get_column('nonexistent')
        assert col is None

    def test_swap_columns(self, manager):
        """Swap adjacent columns."""
        columns = manager.get_columns()
        first_id = columns[0]['id']
        second_id = columns[1]['id']

        # Swap first with second (direction=1)
        manager.swap_column(columns[0], 1)

        columns = manager.get_columns()
        assert columns[0]['id'] == second_id
        assert columns[1]['id'] == first_id

    def test_swap_column_left(self, manager):
        """Swap column left."""
        columns = manager.get_columns()
        first_id = columns[0]['id']
        second_id = columns[1]['id']

        # Swap second with first (direction=-1)
        manager.swap_column(columns[1], -1)

        columns = manager.get_columns()
        assert columns[0]['id'] == second_id
        assert columns[1]['id'] == first_id

    def test_swap_column_boundary_no_change(self, manager):
        """Swap at boundary does nothing."""
        columns = manager.get_columns()
        first_id = columns[0]['id']

        # Try to swap first column left (invalid)
        manager.swap_column(columns[0], -1)

        columns = manager.get_columns()
        assert columns[0]['id'] == first_id  # Unchanged

    def test_get_total_visible_width(self, manager):
        """Get total width of visible columns."""
        width = manager.get_total_visible_width()
        assert width > 0

        # Should match sum of visible column widths
        expected = sum(c['width'] for c in manager.get_visible_columns())
        assert width == expected

    def test_custom_columns_init(self, custom_columns):
        """Initialize with custom columns."""
        from game.ui.screens.column_manager import ColumnManager
        mgr = ColumnManager(custom_columns)

        columns = mgr.get_columns()
        assert len(columns) == 3
        assert columns[0]['id'] == 'col_a'

    def test_image_columns_always_visible(self, manager):
        """Image columns don't appear in visibility toggles."""
        toggleable = manager.get_toggleable_columns()
        for col in toggleable:
            assert col.get('type') != 'image'

    def test_get_column_value_serial(self):
        """Get display value for serial column."""
        from game.ui.screens.column_manager import ColumnManager
        from unittest.mock import Mock

        mgr = ColumnManager()
        ship = Mock()
        ship.get_display_id = Mock(return_value="SN-0001")
        ship.instance_id = "abc123"

        col = mgr.get_column('serial')
        value = mgr.get_column_value(ship, col)
        assert value == "SN-0001"

    def test_get_column_value_hp_pct(self):
        """Get display value for HP percentage column."""
        from game.ui.screens.column_manager import ColumnManager
        from unittest.mock import Mock

        mgr = ColumnManager()
        ship = Mock()
        ship.get_hp_percentage = Mock(return_value=0.75)

        col = mgr.get_column('hp_pct')
        value = mgr.get_column_value(ship, col)
        assert value == "75%"

    def test_get_column_value_status_ok(self):
        """Get status column value for healthy ship."""
        from game.ui.screens.column_manager import ColumnManager
        from unittest.mock import Mock

        mgr = ColumnManager()
        ship = Mock()
        ship.is_alive = True
        ship.is_derelict = False
        ship.is_damaged = Mock(return_value=False)

        col = mgr.get_column('status')
        value = mgr.get_column_value(ship, col)
        assert value == "OK"

    def test_get_column_value_status_destroyed(self):
        """Get status column value for destroyed ship."""
        from game.ui.screens.column_manager import ColumnManager
        from unittest.mock import Mock

        mgr = ColumnManager()
        ship = Mock()
        ship.is_alive = False

        col = mgr.get_column('status')
        value = mgr.get_column_value(ship, col)
        assert value == "DESTROYED"

    def test_get_column_value_status_derelict(self):
        """Get status column value for derelict ship."""
        from game.ui.screens.column_manager import ColumnManager
        from unittest.mock import Mock

        mgr = ColumnManager()
        ship = Mock()
        ship.is_alive = True
        ship.is_derelict = True

        col = mgr.get_column('status')
        value = mgr.get_column_value(ship, col)
        assert value == "DERELICT"

    def test_get_column_value_status_damaged(self):
        """Get status column value for damaged ship."""
        from game.ui.screens.column_manager import ColumnManager
        from unittest.mock import Mock

        mgr = ColumnManager()
        ship = Mock()
        ship.is_alive = True
        ship.is_derelict = False
        ship.is_damaged = Mock(return_value=True)

        col = mgr.get_column('status')
        value = mgr.get_column_value(ship, col)
        assert value == "DAMAGED"
