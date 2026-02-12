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


class TestSortShipsNewColumns:
    """Test cases for new column sorting in PROJ-101 Phase 2."""

    def test_sort_by_speed(self):
        """Sort by ship speed."""
        from game.ui.screens.fleet_report_filters import sort_ships
        from unittest.mock import patch

        ships = [
            make_mock_ship(design_name="Slow"),
            make_mock_ship(design_name="Fast"),
            make_mock_ship(design_name="Medium"),
        ]

        def mock_speed(ship):
            speeds = {"Slow": 3, "Fast": 7, "Medium": 5}
            return speeds[ship.name]

        with patch('game.strategy.services.fleet_speed_calculator.FleetSpeedCalculator.calculate_ship_speed', side_effect=mock_speed):
            result = sort_ships(ships, 'speed', descending=False)
            assert [s.name for s in result] == ["Slow", "Medium", "Fast"]

    def test_sort_by_tonnage(self):
        """Sort by ship tonnage/mass."""
        from game.ui.screens.fleet_report_filters import sort_ships

        ships = [
            make_mock_ship(design_name="Medium", mass=2000),
            make_mock_ship(design_name="Light", mass=500),
            make_mock_ship(design_name="Heavy", mass=5000),
        ]
        result = sort_ships(ships, 'tonnage', descending=False)

        masses = [s.get_calculated_stats()['mass'] for s in result]
        assert masses == [500, 2000, 5000]

    def test_sort_by_warp(self):
        """Sort by warp capability (Yes=1, No=0)."""
        from game.ui.screens.fleet_report_filters import sort_ships

        ships = [
            make_mock_ship(design_name="NoWarp", mass=1000, warp_tonnage=None),
            make_mock_ship(design_name="HasWarp", mass=1000, warp_tonnage=1500),
            make_mock_ship(design_name="AlsoNoWarp", mass=1000, warp_tonnage=500),
        ]
        result = sort_ships(ships, 'warp', descending=True)

        # HasWarp should be first (1), others second (0)
        assert result[0].name == "HasWarp"

    def test_sort_by_spaceyard(self):
        """Sort by spaceyard capability."""
        from game.ui.screens.fleet_report_filters import sort_ships
        from unittest.mock import patch

        ships = [
            make_mock_ship(design_name="NoYard"),
            make_mock_ship(design_name="HasYard"),
        ]

        def mock_has_yard(ship):
            return ship.name == "HasYard"

        with patch('game.strategy.data.fleet_capability_calculator.FleetCapabilityCalculator.ship_has_spaceyard', side_effect=mock_has_yard):
            result = sort_ships(ships, 'spaceyard', descending=True)
            assert result[0].name == "HasYard"

    def test_sort_by_transport(self):
        """Sort by transport capability (passenger capacity)."""
        from game.ui.screens.fleet_report_filters import sort_ships

        ship_no_pax = make_mock_ship(design_name="Warship")
        ship_no_pax.get_calculated_stats.return_value = {'mass': 1000, 'cargo_storage': {}}

        ship_with_pax = make_mock_ship(design_name="Transport")
        ship_with_pax.get_calculated_stats.return_value = {'mass': 1000, 'cargo_storage': {'passengers': 100}}

        ships = [ship_no_pax, ship_with_pax]
        result = sort_ships(ships, 'transport', descending=True)

        assert result[0].name == "Transport"

    def test_sort_by_cargo(self):
        """Sort by cargo contents."""
        from game.ui.screens.fleet_report_filters import sort_ships

        ship_empty = make_mock_ship(design_name="Empty")
        ship_empty.cargo_contents = {}

        ship_some = make_mock_ship(design_name="Some")
        ship_some.cargo_contents = {'minerals': 50}

        ship_full = make_mock_ship(design_name="Full")
        ship_full.cargo_contents = {'minerals': 100, 'food': 50}

        ships = [ship_some, ship_full, ship_empty]
        result = sort_ships(ships, 'cargo', descending=True)

        assert [s.name for s in result] == ["Full", "Some", "Empty"]

    def test_sort_by_resources_returns_stable_order(self):
        """Sort by resources column returns 0 for all (no meaningful sort)."""
        from game.ui.screens.fleet_report_filters import sort_ships

        ships = [
            make_mock_ship(design_name="A"),
            make_mock_ship(design_name="B"),
            make_mock_ship(design_name="C"),
        ]
        result = sort_ships(ships, 'resources', descending=False)

        # Order should be stable (same as input) since all return 0
        assert [s.name for s in result] == ["A", "B", "C"]


class TestFilterShipsSpaceyard:
    """Test cases for spaceyard capability filtering in filter_ships."""

    def test_filter_hide_has_spaceyard(self):
        """Hide ships with spaceyards when filter is off."""
        from game.ui.screens.fleet_report_filters import filter_ships
        from unittest.mock import patch

        ship_with_yard = make_mock_ship(design_name="Carrier")
        ship_with_yard.cargo_contents = {}
        ship_no_yard = make_mock_ship(design_name="Destroyer")
        ship_no_yard.cargo_contents = {}
        ships = [ship_with_yard, ship_no_yard]

        def mock_has_yard(ship):
            return ship.name == "Carrier"

        filter_state = {
            'show_damaged': True,
            'show_undamaged': True,
            'show_derelict': True,
            'show_destroyed': True,
            'show_has_spaceyard': False,
            'show_no_spaceyard': True,
        }

        with patch('game.strategy.data.fleet_capability_calculator.FleetCapabilityCalculator.ship_has_spaceyard', side_effect=mock_has_yard):
            result = filter_ships(ships, filter_state)

        assert len(result) == 1
        assert result[0].name == "Destroyer"

    def test_filter_hide_no_spaceyard(self):
        """Hide ships without spaceyards when filter is off."""
        from game.ui.screens.fleet_report_filters import filter_ships
        from unittest.mock import patch

        ship_with_yard = make_mock_ship(design_name="Carrier")
        ship_with_yard.cargo_contents = {}
        ship_no_yard = make_mock_ship(design_name="Destroyer")
        ship_no_yard.cargo_contents = {}
        ships = [ship_with_yard, ship_no_yard]

        def mock_has_yard(ship):
            return ship.name == "Carrier"

        filter_state = {
            'show_damaged': True,
            'show_undamaged': True,
            'show_derelict': True,
            'show_destroyed': True,
            'show_has_spaceyard': True,
            'show_no_spaceyard': False,
        }

        with patch('game.strategy.data.fleet_capability_calculator.FleetCapabilityCalculator.ship_has_spaceyard', side_effect=mock_has_yard):
            result = filter_ships(ships, filter_state)

        assert len(result) == 1
        assert result[0].name == "Carrier"

    def test_filter_show_all_spaceyard_states(self):
        """With both spaceyard filters enabled, all ships pass."""
        from game.ui.screens.fleet_report_filters import filter_ships

        ship_with_yard = make_mock_ship(design_name="Carrier")
        ship_with_yard.cargo_contents = {}
        ship_no_yard = make_mock_ship(design_name="Destroyer")
        ship_no_yard.cargo_contents = {}
        ships = [ship_with_yard, ship_no_yard]

        filter_state = {
            'show_damaged': True,
            'show_undamaged': True,
            'show_derelict': True,
            'show_destroyed': True,
            'show_has_spaceyard': True,
            'show_no_spaceyard': True,
        }

        result = filter_ships(ships, filter_state)
        assert len(result) == 2


class TestFilterShipsCargo:
    """Test cases for cargo filtering in filter_ships."""

    def test_filter_hide_has_cargo(self):
        """Hide ships with cargo when filter is off."""
        from game.ui.screens.fleet_report_filters import filter_ships

        ship_with_cargo = make_mock_ship(design_name="Freighter")
        ship_with_cargo.cargo_contents = {'minerals': 100}

        ship_no_cargo = make_mock_ship(design_name="Warship")
        ship_no_cargo.cargo_contents = {}

        ships = [ship_with_cargo, ship_no_cargo]

        filter_state = {
            'show_damaged': True,
            'show_undamaged': True,
            'show_derelict': True,
            'show_destroyed': True,
            'show_has_cargo': False,
            'show_no_cargo': True,
        }

        result = filter_ships(ships, filter_state)
        assert len(result) == 1
        assert result[0].name == "Warship"

    def test_filter_hide_no_cargo(self):
        """Hide ships without cargo when filter is off."""
        from game.ui.screens.fleet_report_filters import filter_ships

        ship_with_cargo = make_mock_ship(design_name="Freighter")
        ship_with_cargo.cargo_contents = {'minerals': 100}

        ship_no_cargo = make_mock_ship(design_name="Warship")
        ship_no_cargo.cargo_contents = {}

        ships = [ship_with_cargo, ship_no_cargo]

        filter_state = {
            'show_damaged': True,
            'show_undamaged': True,
            'show_derelict': True,
            'show_destroyed': True,
            'show_has_cargo': True,
            'show_no_cargo': False,
        }

        result = filter_ships(ships, filter_state)
        assert len(result) == 1
        assert result[0].name == "Freighter"

    def test_filter_cargo_with_population(self):
        """Cargo filter includes population as cargo."""
        from game.ui.screens.fleet_report_filters import filter_ships

        ship_with_pax = make_mock_ship(design_name="Transport")
        ship_with_pax.cargo_contents = {'population': 500}

        ship_empty = make_mock_ship(design_name="Scout")
        ship_empty.cargo_contents = {}

        ships = [ship_with_pax, ship_empty]

        filter_state = {
            'show_damaged': True,
            'show_undamaged': True,
            'show_derelict': True,
            'show_destroyed': True,
            'show_has_cargo': False,
            'show_no_cargo': True,
        }

        result = filter_ships(ships, filter_state)
        assert len(result) == 1
        assert result[0].name == "Scout"

    def test_filter_cargo_zero_value_treated_as_no_cargo(self):
        """Ship with cargo dict but zero values treated as no cargo."""
        from game.ui.screens.fleet_report_filters import filter_ships

        ship_zero = make_mock_ship(design_name="EmptyHold")
        ship_zero.cargo_contents = {'minerals': 0, 'food': 0}

        ships = [ship_zero]

        filter_state = {
            'show_damaged': True,
            'show_undamaged': True,
            'show_derelict': True,
            'show_destroyed': True,
            'show_has_cargo': False,
            'show_no_cargo': True,
        }

        result = filter_ships(ships, filter_state)
        assert len(result) == 1  # Treated as no cargo

    def test_filter_show_all_cargo_states(self):
        """With both cargo filters enabled, all ships pass."""
        from game.ui.screens.fleet_report_filters import filter_ships

        ship_with_cargo = make_mock_ship(design_name="Freighter")
        ship_with_cargo.cargo_contents = {'minerals': 100}

        ship_no_cargo = make_mock_ship(design_name="Warship")
        ship_no_cargo.cargo_contents = {}

        ships = [ship_with_cargo, ship_no_cargo]

        filter_state = {
            'show_damaged': True,
            'show_undamaged': True,
            'show_derelict': True,
            'show_destroyed': True,
            'show_has_cargo': True,
            'show_no_cargo': True,
        }

        result = filter_ships(ships, filter_state)
        assert len(result) == 2


class TestSpecialCapabilityFilter:
    """Tests for special capability filtering (BUG-83)."""

    def test_filter_hides_ships_with_ability(self):
        """Filter can hide ships that have a special ability."""
        from game.ui.screens.fleet_report_filters import filter_ships
        from unittest.mock import patch

        ship_with = make_mock_ship(serial=1, design_name="Planet Killer")
        ship_without = make_mock_ship(serial=2, design_name="Scout")

        def mock_has_ability(ship, ability_name):
            return ship.serial == 1 and ability_name == 'DestroyPlanet'

        filter_state = {
            'show_damaged': True,
            'show_undamaged': True,
            'show_derelict': True,
            'show_destroyed': True,
            'show_can_destroy_planet': False,  # Hide ships with ability
            'show_no_destroy_planet': True,
        }

        with patch('game.strategy.data.fleet_capability_calculator.FleetCapabilityCalculator._ship_has_ability',
                   side_effect=mock_has_ability):
            result = filter_ships([ship_with, ship_without], filter_state)

        assert len(result) == 1
        assert result[0].serial == 2

    def test_filter_hides_ships_without_ability(self):
        """Filter can hide ships that lack a special ability."""
        from game.ui.screens.fleet_report_filters import filter_ships
        from unittest.mock import patch

        ship_with = make_mock_ship(serial=1, design_name="Planet Killer")
        ship_without = make_mock_ship(serial=2, design_name="Scout")

        def mock_has_ability(ship, ability_name):
            return ship.serial == 1 and ability_name == 'DestroyPlanet'

        filter_state = {
            'show_damaged': True,
            'show_undamaged': True,
            'show_derelict': True,
            'show_destroyed': True,
            'show_can_destroy_planet': True,
            'show_no_destroy_planet': False,  # Hide ships without ability
        }

        with patch('game.strategy.data.fleet_capability_calculator.FleetCapabilityCalculator._ship_has_ability',
                   side_effect=mock_has_ability):
            result = filter_ships([ship_with, ship_without], filter_state)

        assert len(result) == 1
        assert result[0].serial == 1

    def test_filter_default_shows_all(self):
        """Default filter state shows all ships regardless of special abilities."""
        from game.ui.screens.fleet_report_filters import filter_ships

        ships = [make_mock_ship(serial=i) for i in range(5)]

        # Default filter state - all show flags True
        filter_state = {
            'show_damaged': True,
            'show_undamaged': True,
            'show_derelict': True,
            'show_destroyed': True,
        }

        result = filter_ships(ships, filter_state)
        assert len(result) == 5


class TestSpecialCapabilitySort:
    """Tests for special capability column sorting (BUG-83)."""

    def test_sort_by_special_capability(self):
        """Sort by special capability column puts 'Yes' ships first when descending."""
        from game.ui.screens.fleet_report_filters import sort_ships
        from unittest.mock import patch

        ship1 = make_mock_ship(serial=1, design_name="Scout")
        ship2 = make_mock_ship(serial=2, design_name="Planet Killer")
        ship3 = make_mock_ship(serial=3, design_name="Frigate")

        def mock_has_ability(ship, ability_name):
            return ship.serial == 2 and ability_name == 'DestroyPlanet'

        with patch('game.strategy.data.fleet_capability_calculator.FleetCapabilityCalculator._ship_has_ability',
                   side_effect=mock_has_ability):
            result = sort_ships([ship1, ship2, ship3], 'can_destroy_planet', descending=True)

        # Ship2 (has ability, sort key=1) should be first when descending
        assert result[0].serial == 2


class TestViewModelSpecialFilters:
    """Tests for FleetListViewModel special capability filter state (BUG-83)."""

    def test_toggle_special_filter(self):
        """Toggle special capability filter changes state."""
        from game.ui.screens.fleet_report_view_model import FleetListViewModel

        vm = FleetListViewModel()
        assert vm.filter_show_can_destroy_planet is True

        result = vm.toggle_filter('can_destroy_planet')
        assert result is False
        assert vm.filter_show_can_destroy_planet is False

    def test_special_filter_state_included(self):
        """Special capability filters appear in get_filter_state()."""
        from game.ui.screens.fleet_report_view_model import FleetListViewModel

        vm = FleetListViewModel()
        state = vm.get_filter_state()

        assert 'show_can_destroy_planet' in state
        assert 'show_no_destroy_planet' in state
        assert 'show_can_open_warp' in state
        assert 'show_can_close_warp' in state
        assert 'show_can_destroy_star' in state
        assert 'show_can_create_sphere' in state

    def test_special_filter_labels(self):
        """Special capability filters have display labels."""
        from game.ui.screens.fleet_report_view_model import FleetListViewModel

        vm = FleetListViewModel()

        assert vm.get_filter_label('can_destroy_planet') == 'Can Destroy Planet'
        assert vm.get_filter_label('no_destroy_planet') == 'No Planet Destroyer'
        assert vm.get_filter_label('can_open_warp') == 'Can Open Warp'
        assert vm.get_filter_label('can_destroy_star') == 'Can Destroy Star'
        assert vm.get_filter_label('can_create_sphere') == 'Can Create Sphere'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
