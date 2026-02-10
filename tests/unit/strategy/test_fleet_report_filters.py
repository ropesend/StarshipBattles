"""Tests for fleet report filtering and stats calculation - PROJ-03 Phase 3."""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.ship_instance import ShipInstance


def make_mock_ship(
    serial=None,
    design_name="Destroyer",
    hp_pct=1.0,
    is_alive=True,
    is_derelict=False,
    is_damaged=False,
    mass=1000,
    max_fuel=100,
    current_fuel=100,
    max_energy=100,
    current_energy=100,
    warp_tonnage=None  # If set, adds WarpJump ability with this max_tonnage
):
    """Helper to create a mock ship for testing."""
    ship = MagicMock(spec=ShipInstance)
    ship.serial = serial
    ship.design_id = design_name.lower().replace(" ", "_")
    ship.name = design_name
    ship.is_alive = is_alive
    ship.is_derelict = is_derelict
    ship.is_damaged.return_value = is_damaged

    # Set up design_data with optional warp ability
    layers = {}
    expected_stats = {
        'mass': mass,
        'max_hp': 100,
        'resource_storage': {'fuel': max_fuel, 'energy': max_energy},
        'warp_max_tonnage': warp_tonnage if warp_tonnage is not None else 0,
    }

    ship.design_data = {
        'name': design_name,
        'expected_stats': expected_stats,
        'layers': layers
    }

    # Configure get_calculated_stats() to return the expected_stats
    # This is needed since code now uses get_calculated_stats() instead of expected_stats
    ship.get_calculated_stats.return_value = expected_stats

    # Set HP percentage
    ship.get_hp_percentage.return_value = hp_pct

    # Set current_hp based on hp_pct
    if hp_pct < 1.0:
        ship.current_hp = int(100 * hp_pct)
    else:
        ship.current_hp = None

    # PROJ-95: Resource levels always store actual values (no sparse dict convention)
    ship.resource_levels = {
        'fuel': current_fuel,
        'energy': current_energy,
    }

    # Combat capable status
    ship.is_combat_capable.return_value = is_alive and not is_derelict

    return ship


class TestCalculateFleetStats:
    """Test cases for calculate_fleet_stats function."""

    def test_empty_fleet_stats(self):
        """Empty fleet should return zero stats."""
        from game.ui.screens.fleet_report_filters import calculate_fleet_stats

        stats = calculate_fleet_stats([])

        assert stats['ship_count'] == 0
        assert stats['combat_capable_count'] == 0
        assert stats['total_tonnage'] == 0
        assert stats['avg_hp_percent'] == 0.0

    def test_single_ship_stats(self):
        """Single ship stats should be calculated correctly."""
        from game.ui.screens.fleet_report_filters import calculate_fleet_stats

        ship = make_mock_ship(mass=500, hp_pct=0.8)
        stats = calculate_fleet_stats([ship])

        assert stats['ship_count'] == 1
        assert stats['combat_capable_count'] == 1
        assert stats['total_tonnage'] == 500
        assert stats['avg_hp_percent'] == 0.8

    def test_multiple_ships_tonnage(self):
        """Total tonnage should sum all ship masses."""
        from game.ui.screens.fleet_report_filters import calculate_fleet_stats

        ships = [
            make_mock_ship(mass=1000),
            make_mock_ship(mass=2000),
            make_mock_ship(mass=500),
        ]
        stats = calculate_fleet_stats(ships)

        assert stats['total_tonnage'] == 3500

    def test_average_hp_calculation(self):
        """Average HP should be calculated correctly."""
        from game.ui.screens.fleet_report_filters import calculate_fleet_stats

        ships = [
            make_mock_ship(hp_pct=1.0),   # 100%
            make_mock_ship(hp_pct=0.5),   # 50%
            make_mock_ship(hp_pct=0.8),   # 80%
        ]
        stats = calculate_fleet_stats(ships)

        # Average: (1.0 + 0.5 + 0.8) / 3 = 0.7667
        assert abs(stats['avg_hp_percent'] - 0.7667) < 0.01

    def test_combat_capable_excludes_destroyed(self):
        """Combat capable count should exclude destroyed ships."""
        from game.ui.screens.fleet_report_filters import calculate_fleet_stats

        ships = [
            make_mock_ship(is_alive=True),
            make_mock_ship(is_alive=False),
            make_mock_ship(is_alive=True),
        ]
        stats = calculate_fleet_stats(ships)

        assert stats['ship_count'] == 3
        assert stats['combat_capable_count'] == 2

    def test_combat_capable_excludes_derelict(self):
        """Combat capable count should exclude derelict ships."""
        from game.ui.screens.fleet_report_filters import calculate_fleet_stats

        ships = [
            make_mock_ship(is_derelict=False),
            make_mock_ship(is_derelict=True),
        ]
        stats = calculate_fleet_stats(ships)

        assert stats['ship_count'] == 2
        assert stats['combat_capable_count'] == 1

    def test_damaged_count(self):
        """Damaged count should count ships with any damage."""
        from game.ui.screens.fleet_report_filters import calculate_fleet_stats

        ships = [
            make_mock_ship(is_damaged=True),
            make_mock_ship(is_damaged=False),
            make_mock_ship(is_damaged=True),
        ]
        stats = calculate_fleet_stats(ships)

        assert stats['damaged_count'] == 2

    def test_derelict_count(self):
        """Derelict count should count derelict ships."""
        from game.ui.screens.fleet_report_filters import calculate_fleet_stats

        ships = [
            make_mock_ship(is_derelict=True),
            make_mock_ship(is_derelict=False),
        ]
        stats = calculate_fleet_stats(ships)

        assert stats['derelict_count'] == 1

    def test_resource_totals(self):
        """Resource totals should sum current and max values."""
        from game.ui.screens.fleet_report_filters import calculate_fleet_stats

        ships = [
            make_mock_ship(max_fuel=100, current_fuel=80, max_energy=50, current_energy=50),
            make_mock_ship(max_fuel=200, current_fuel=100, max_energy=100, current_energy=75),
        ]
        stats = calculate_fleet_stats(ships)

        assert stats['max_fuel'] == 300
        assert stats['total_fuel'] == 180
        assert stats['max_energy'] == 150
        assert stats['total_energy'] == 125


class TestFilterShips:
    """Test cases for filter_ships function."""

    def test_filter_show_all(self):
        """With all filters enabled, all ships should pass."""
        from game.ui.screens.fleet_report_filters import filter_ships

        ships = [
            make_mock_ship(is_damaged=True),
            make_mock_ship(is_damaged=False),
            make_mock_ship(is_derelict=True),
        ]
        filter_state = {
            'show_damaged': True,
            'show_undamaged': True,
            'show_derelict': True,
            'show_destroyed': True,
        }
        result = filter_ships(ships, filter_state)

        assert len(result) == 3

    def test_filter_hide_damaged(self):
        """Hide damaged ships when filter is off."""
        from game.ui.screens.fleet_report_filters import filter_ships

        ships = [
            make_mock_ship(is_damaged=True),
            make_mock_ship(is_damaged=False),
        ]
        filter_state = {
            'show_damaged': False,
            'show_undamaged': True,
            'show_derelict': True,
            'show_destroyed': True,
        }
        result = filter_ships(ships, filter_state)

        assert len(result) == 1
        assert not result[0].is_damaged()

    def test_filter_hide_undamaged(self):
        """Hide undamaged ships when filter is off."""
        from game.ui.screens.fleet_report_filters import filter_ships

        ships = [
            make_mock_ship(is_damaged=True),
            make_mock_ship(is_damaged=False),
        ]
        filter_state = {
            'show_damaged': True,
            'show_undamaged': False,
            'show_derelict': True,
            'show_destroyed': True,
        }
        result = filter_ships(ships, filter_state)

        assert len(result) == 1
        assert result[0].is_damaged()

    def test_filter_hide_derelict(self):
        """Hide derelict ships when filter is off."""
        from game.ui.screens.fleet_report_filters import filter_ships

        ships = [
            make_mock_ship(is_derelict=True),
            make_mock_ship(is_derelict=False),
        ]
        filter_state = {
            'show_damaged': True,
            'show_undamaged': True,
            'show_derelict': False,
            'show_destroyed': True,
        }
        result = filter_ships(ships, filter_state)

        assert len(result) == 1
        assert not result[0].is_derelict

    def test_filter_hide_destroyed(self):
        """Hide destroyed ships when filter is off."""
        from game.ui.screens.fleet_report_filters import filter_ships

        ships = [
            make_mock_ship(is_alive=False),
            make_mock_ship(is_alive=True),
        ]
        filter_state = {
            'show_damaged': True,
            'show_undamaged': True,
            'show_derelict': True,
            'show_destroyed': False,
        }
        result = filter_ships(ships, filter_state)

        assert len(result) == 1
        assert result[0].is_alive


class TestHasWarpCapability:
    """Test cases for ShipStatsCalculator.has_warp_capability function.

    PROJ-40: Updated to use canonical import from ShipStatsCalculator directly.
    """

    def test_ship_without_warp_drive(self):
        """Ship without WarpJump ability should return False."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        ship = make_mock_ship(mass=1000, warp_tonnage=None)
        assert ShipStatsCalculator.has_warp_capability(ship) is False

    def test_ship_with_sufficient_warp_drive(self):
        """Ship with WarpJump exceeding mass should return True."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        ship = make_mock_ship(mass=1000, warp_tonnage=1500)
        assert ShipStatsCalculator.has_warp_capability(ship) is True

    def test_ship_with_equal_warp_tonnage(self):
        """Ship with WarpJump equal to mass should return True."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        ship = make_mock_ship(mass=1000, warp_tonnage=1000)
        assert ShipStatsCalculator.has_warp_capability(ship) is True

    def test_ship_with_insufficient_warp_drive(self):
        """Ship with WarpJump less than mass should return False."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        ship = make_mock_ship(mass=1000, warp_tonnage=500)
        assert ShipStatsCalculator.has_warp_capability(ship) is False

    def test_ship_with_zero_mass(self):
        """Ship with zero mass should return False (edge case)."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        ship = make_mock_ship(mass=0, warp_tonnage=1000)
        assert ShipStatsCalculator.has_warp_capability(ship) is False

    def test_warp_capability_with_expected_stats(self):
        """Warp capability determined from expected_stats should work."""
        from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

        ship = make_mock_ship(mass=1000, warp_tonnage=1500)
        # Verify expected_stats has warp_max_tonnage
        assert ship.design_data['expected_stats']['warp_max_tonnage'] == 1500
        assert ShipStatsCalculator.has_warp_capability(ship) is True


class TestFilterShipsWarp:
    """Test cases for warp capability filtering in filter_ships."""

    def test_filter_hide_warp_capable(self):
        """Hide warp-capable ships when filter is off."""
        from game.ui.screens.fleet_report_filters import filter_ships

        ships = [
            make_mock_ship(mass=1000, warp_tonnage=1500),  # warp capable
            make_mock_ship(mass=1000, warp_tonnage=None),   # not warp capable
        ]
        filter_state = {
            'show_damaged': True,
            'show_undamaged': True,
            'show_derelict': True,
            'show_destroyed': True,
            'show_warp_capable': False,
            'show_not_warp_capable': True,
        }
        result = filter_ships(ships, filter_state)

        assert len(result) == 1
        # The remaining ship should not have warp capability
        assert 'WarpJump' not in result[0].design_data['layers'].get('CORE', [{}])[0].get('abilities', {})

    def test_filter_hide_not_warp_capable(self):
        """Hide non-warp-capable ships when filter is off."""
        from game.ui.screens.fleet_report_filters import filter_ships

        ships = [
            make_mock_ship(mass=1000, warp_tonnage=1500),  # warp capable
            make_mock_ship(mass=1000, warp_tonnage=None),   # not warp capable
        ]
        filter_state = {
            'show_damaged': True,
            'show_undamaged': True,
            'show_derelict': True,
            'show_destroyed': True,
            'show_warp_capable': True,
            'show_not_warp_capable': False,
        }
        result = filter_ships(ships, filter_state)

        assert len(result) == 1
        # The remaining ship should have warp capability (via expected_stats)
        assert result[0].design_data['expected_stats']['warp_max_tonnage'] == 1500

    def test_filter_show_all_warp_states(self):
        """With both warp filters enabled, all ships should pass warp filter."""
        from game.ui.screens.fleet_report_filters import filter_ships

        ships = [
            make_mock_ship(mass=1000, warp_tonnage=1500),  # warp capable
            make_mock_ship(mass=1000, warp_tonnage=None),   # not warp capable
        ]
        filter_state = {
            'show_damaged': True,
            'show_undamaged': True,
            'show_derelict': True,
            'show_destroyed': True,
            'show_warp_capable': True,
            'show_not_warp_capable': True,
        }
        result = filter_ships(ships, filter_state)

        assert len(result) == 2


class TestSortShips:
    """Test cases for sort_ships function."""

    def test_sort_by_serial_ascending(self):
        """Sort by serial number ascending."""
        from game.ui.screens.fleet_report_filters import sort_ships

        ships = [
            make_mock_ship(serial=3),
            make_mock_ship(serial=1),
            make_mock_ship(serial=2),
        ]
        result = sort_ships(ships, 'serial', descending=False)

        assert [s.serial for s in result] == [1, 2, 3]

    def test_sort_by_serial_descending(self):
        """Sort by serial number descending."""
        from game.ui.screens.fleet_report_filters import sort_ships

        ships = [
            make_mock_ship(serial=1),
            make_mock_ship(serial=3),
            make_mock_ship(serial=2),
        ]
        result = sort_ships(ships, 'serial', descending=True)

        assert [s.serial for s in result] == [3, 2, 1]

    def test_sort_by_hp_pct(self):
        """Sort by HP percentage."""
        from game.ui.screens.fleet_report_filters import sort_ships

        ships = [
            make_mock_ship(hp_pct=0.5),
            make_mock_ship(hp_pct=1.0),
            make_mock_ship(hp_pct=0.8),
        ]
        result = sort_ships(ships, 'hp_pct', descending=False)

        hp_values = [s.get_hp_percentage() for s in result]
        assert hp_values == [0.5, 0.8, 1.0]

    def test_sort_by_design_name(self):
        """Sort by design name alphabetically."""
        from game.ui.screens.fleet_report_filters import sort_ships

        ships = [
            make_mock_ship(design_name="Cruiser"),
            make_mock_ship(design_name="Destroyer"),
            make_mock_ship(design_name="Battleship"),
        ]
        result = sort_ships(ships, 'design', descending=False)

        names = [s.design_data['name'] for s in result]
        assert names == ["Battleship", "Cruiser", "Destroyer"]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
