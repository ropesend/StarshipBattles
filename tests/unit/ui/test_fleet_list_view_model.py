"""
Tests for FleetListViewModel - manages filtering, sorting, and pagination state.

PROJ-44 Phase 7 Task 7.4: FleetReportWindow refactoring.
"""
import pytest
from unittest.mock import Mock, MagicMock


class TestFleetListViewModel:
    """Test FleetListViewModel filtering, sorting, and state management."""

    @pytest.fixture
    def mock_ships(self):
        """Create mock ships for testing."""
        ships = []
        for i in range(5):
            ship = Mock()
            ship.instance_id = f"ship-{i}"
            ship.serial = i + 1
            ship.name = f"Ship {i}"
            ship.design_id = f"design-{i % 2}"
            ship.design_data = {'name': f'Design {i % 2}', 'theme_id': 'Federation'}
            ship.is_destroyed = (i == 4)  # Last ship is destroyed
            ship.is_derelict = (i == 3)   # 4th ship is derelict
            ship.is_damaged = Mock(return_value=(i >= 2))  # Ships 2,3,4 are damaged
            ship.get_hp_percentage = Mock(return_value=(1.0 - i * 0.2))  # 100%, 80%, 60%, 40%, 20%
            ship.get_display_id = Mock(return_value=f"SN-{i:04d}")
            ships.append(ship)
        return ships

    @pytest.fixture
    def view_model(self, mock_ships):
        """Create FleetListViewModel instance."""
        from game.ui.screens.fleet_report_view_model import FleetListViewModel
        return FleetListViewModel(mock_ships)

    def test_init_sets_default_filters(self, view_model):
        """ViewModel initializes with default filter state."""
        assert view_model.filter_show_damaged is True
        assert view_model.filter_show_undamaged is True
        assert view_model.filter_show_derelict is True
        assert view_model.filter_show_destroyed is False  # Destroyed hidden by default
        assert view_model.filter_show_warp_capable is True
        assert view_model.filter_show_not_warp_capable is True

    def test_init_sets_default_sort(self, view_model):
        """ViewModel initializes with default sort state."""
        assert view_model.sort_column_id == 'serial'
        assert view_model.sort_descending is False

    def test_get_filtered_ships_excludes_destroyed_by_default(self, view_model, mock_ships):
        """Default filter excludes destroyed ships."""
        filtered = view_model.get_filtered_ships()
        # Should have 4 ships (destroyed one excluded)
        assert len(filtered) == 4
        assert mock_ships[4] not in filtered  # Destroyed ship excluded

    def test_toggle_filter_damaged(self, view_model):
        """Toggle damaged filter updates state."""
        assert view_model.filter_show_damaged is True
        view_model.toggle_filter('damaged')
        assert view_model.filter_show_damaged is False
        view_model.toggle_filter('damaged')
        assert view_model.filter_show_damaged is True

    def test_toggle_filter_destroyed(self, view_model, mock_ships):
        """Toggle destroyed filter includes/excludes destroyed ships."""
        # Initially destroyed ships excluded
        assert len(view_model.get_filtered_ships()) == 4

        # Enable destroyed
        view_model.toggle_filter('destroyed')
        assert view_model.filter_show_destroyed is True
        assert len(view_model.get_filtered_ships()) == 5

    def test_toggle_filter_derelict(self, view_model, mock_ships):
        """Toggle derelict filter includes/excludes derelict ships."""
        view_model.toggle_filter('derelict')
        assert view_model.filter_show_derelict is False
        filtered = view_model.get_filtered_ships()
        assert mock_ships[3] not in filtered  # Derelict ship excluded

    def test_set_sort_column(self, view_model):
        """Set sort column changes sort state."""
        view_model.set_sort('name')
        assert view_model.sort_column_id == 'name'
        assert view_model.sort_descending is False

    def test_set_sort_same_column_toggles_direction(self, view_model):
        """Setting same sort column toggles direction."""
        view_model.set_sort('serial')  # Already sorted by serial
        assert view_model.sort_descending is True  # Toggled to descending

        view_model.set_sort('serial')
        assert view_model.sort_descending is False  # Toggled back

    def test_get_filtered_ships_applies_sort(self, view_model, mock_ships):
        """Filtered ships are sorted by current sort settings."""
        view_model.set_sort('hp_pct')
        view_model.sort_descending = False  # Ascending
        filtered = view_model.get_filtered_ships()

        # Check HP percentages are ascending
        hps = [s.get_hp_percentage() for s in filtered]
        assert hps == sorted(hps)

    def test_get_filtered_ships_applies_sort_descending(self, view_model, mock_ships):
        """Filtered ships are sorted descending when set."""
        view_model.set_sort('hp_pct')
        view_model.sort_descending = True
        filtered = view_model.get_filtered_ships()

        # Check HP percentages are descending
        hps = [s.get_hp_percentage() for s in filtered]
        assert hps == sorted(hps, reverse=True)

    def test_get_filter_state_dict(self, view_model):
        """get_filter_state returns dict for filter_ships function."""
        state = view_model.get_filter_state()
        assert state['show_damaged'] is True
        assert state['show_undamaged'] is True
        assert state['show_derelict'] is True
        assert state['show_destroyed'] is False
        assert state['show_warp_capable'] is True
        assert state['show_not_warp_capable'] is True

    def test_update_ships_refreshes_filtered_list(self, view_model):
        """Updating ships refreshes the filtered list."""
        new_ships = [Mock() for _ in range(3)]
        for i, ship in enumerate(new_ships):
            ship.is_destroyed = False
            ship.is_derelict = False
            ship.is_damaged = Mock(return_value=False)
            ship.get_hp_percentage = Mock(return_value=1.0)
            ship.serial = i

        view_model.update_ships(new_ships)
        assert len(view_model.get_filtered_ships()) == 3

    def test_filter_undamaged_only(self, view_model, mock_ships):
        """Filter to show only undamaged ships."""
        view_model.toggle_filter('damaged')
        view_model.toggle_filter('derelict')
        # Keep undamaged on, destroyed already off

        filtered = view_model.get_filtered_ships()
        # Ships 0, 1 are undamaged
        assert len(filtered) == 2
        assert mock_ships[0] in filtered
        assert mock_ships[1] in filtered

    def test_get_ship_count(self, view_model):
        """get_ship_count returns count of filtered ships."""
        assert view_model.get_ship_count() == 4  # Destroyed excluded

    def test_get_total_ship_count(self, view_model, mock_ships):
        """get_total_ship_count returns total ships."""
        assert view_model.get_total_ship_count() == 5


class TestFleetListViewModelWarpFilters:
    """Test warp capability filtering."""

    @pytest.fixture
    def mock_ships_with_warp(self):
        """Create mock ships with mixed warp capabilities."""
        ships = []
        for i in range(4):
            ship = Mock()
            ship.instance_id = f"ship-{i}"
            ship.serial = i + 1
            ship.is_destroyed = False
            ship.is_derelict = False
            ship.is_damaged = Mock(return_value=False)
            ship.get_hp_percentage = Mock(return_value=1.0)
            # Ships 0,1 have warp; ships 2,3 don't
            ship.has_warp = (i < 2)
            ships.append(ship)
        return ships

    @pytest.fixture
    def view_model(self, mock_ships_with_warp):
        """Create FleetListViewModel with mocked warp check."""
        from game.ui.screens.fleet_report_view_model import FleetListViewModel

        # Create view model
        vm = FleetListViewModel(mock_ships_with_warp)
        return vm

    def test_toggle_warp_capable_filter(self, view_model):
        """Toggle warp capable filter."""
        assert view_model.filter_show_warp_capable is True
        view_model.toggle_filter('warp_capable')
        assert view_model.filter_show_warp_capable is False

    def test_toggle_not_warp_capable_filter(self, view_model):
        """Toggle not warp capable filter."""
        assert view_model.filter_show_not_warp_capable is True
        view_model.toggle_filter('not_warp_capable')
        assert view_model.filter_show_not_warp_capable is False
