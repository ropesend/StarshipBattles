"""Tests for fleet report filtering and stats calculation - PROJ-03 Phase 3.

PROJ-220: Updated filter tests from paired-bool to tri-state FilterState.
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.ship_instance import ShipInstance
from game.ui.filters.filter_state import FilterState


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

    # PROJ-162: Mock get_cargo_capacity to return 0 by default (sort_ships calls this)
    ship.get_cargo_capacity = MagicMock(return_value=0)

    # Set HP percentage
    ship.get_hp_percentage.return_value = hp_pct

    # Set current_hp based on hp_pct
    if hp_pct < 1.0:
        ship.current_hp = int(100 * hp_pct)
    else:
        ship.current_hp = None

    # PROJ-95: Resource levels always store actual values (no sparse dict convention)
    ship.consumable_levels = {
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
        """Average HP should be calculated correctly.

        PROJ-323 Task 5.23: hardcoded reference 0.7667 (validated against
        calculate_fleet_stats 2026-05-03). For inputs (1.0, 0.5, 0.8) the
        production avg is (1.0 + 0.5 + 0.8) / 3 ≈ 0.7666666...
        """
        from game.ui.screens.fleet_report_filters import calculate_fleet_stats

        ships = [
            make_mock_ship(hp_pct=1.0),
            make_mock_ship(hp_pct=0.5),
            make_mock_ship(hp_pct=0.8),
        ]
        stats = calculate_fleet_stats(ships)

        # Hardcoded reference; see docstring derivation.
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
    """Test cases for has_warp_capability function.

    PROJ-40: Updated to use canonical import from ShipStatsCalculator directly.
    """

    def test_ship_without_warp_drive(self):
        """Ship without WarpJump ability should return False."""
        from game.strategy.services.component_inspector import has_warp_capability

        ship = make_mock_ship(mass=1000, warp_tonnage=None)
        assert has_warp_capability(ship) is False

    def test_ship_with_sufficient_warp_drive(self):
        """Ship with WarpJump exceeding mass should return True."""
        from game.strategy.services.component_inspector import has_warp_capability

        ship = make_mock_ship(mass=1000, warp_tonnage=1500)
        assert has_warp_capability(ship) is True

    def test_ship_with_equal_warp_tonnage(self):
        """Ship with WarpJump equal to mass should return True."""
        from game.strategy.services.component_inspector import has_warp_capability

        ship = make_mock_ship(mass=1000, warp_tonnage=1000)
        assert has_warp_capability(ship) is True

    def test_ship_with_insufficient_warp_drive(self):
        """Ship with WarpJump less than mass should return False."""
        from game.strategy.services.component_inspector import has_warp_capability

        ship = make_mock_ship(mass=1000, warp_tonnage=500)
        assert has_warp_capability(ship) is False

    def test_ship_with_zero_mass(self):
        """Ship with zero mass should return False (edge case)."""
        from game.strategy.services.component_inspector import has_warp_capability

        ship = make_mock_ship(mass=0, warp_tonnage=1000)
        assert has_warp_capability(ship) is False

    def test_warp_capability_with_expected_stats(self):
        """Warp capability determined from expected_stats should work."""
        from game.strategy.services.component_inspector import has_warp_capability

        ship = make_mock_ship(mass=1000, warp_tonnage=1500)
        # Verify expected_stats has warp_max_tonnage
        assert ship.design_data['expected_stats']['warp_max_tonnage'] == 1500
        assert has_warp_capability(ship) is True


class TestFilterShipsWarp:
    """Test cases for warp capability filtering in filter_ships."""

    def test_filter_hide_warp_capable(self):
        """NO filter shows only non-warp-capable ships."""
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
            'warp_capable': FilterState.NO,
        }
        result = filter_ships(ships, filter_state)

        assert len(result) == 1
        assert result[0].design_data['expected_stats']['warp_max_tonnage'] == 0

    def test_filter_hide_not_warp_capable(self):
        """YES filter shows only warp-capable ships."""
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
            'warp_capable': FilterState.YES,
        }
        result = filter_ships(ships, filter_state)

        assert len(result) == 1
        assert result[0].design_data['expected_stats']['warp_max_tonnage'] == 1500

    def test_filter_show_all_warp_states(self):
        """IGNORE filter passes all ships through warp filter."""
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
            'warp_capable': FilterState.IGNORE,
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
        ship_no_pax.get_cargo_capacity = MagicMock(return_value=0)

        ship_with_pax = make_mock_ship(design_name="Transport")
        ship_with_pax.get_calculated_stats.return_value = {'mass': 1000, 'cargo_storage': {'passengers': 100}}
        ship_with_pax.get_cargo_capacity = MagicMock(return_value=100)  # PROJ-162: sort_ships uses get_cargo_capacity

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
    """Test cases for spaceyard capability filtering in filter_ships.

    PROJ-323 Task 3.1: 3 spaceyard NO/YES/IGNORE tests parametrized.
    """

    @staticmethod
    def _make_carrier_destroyer_pair():
        ship_with_yard = make_mock_ship(design_name="Carrier")
        ship_with_yard.cargo_contents = {}
        ship_no_yard = make_mock_ship(design_name="Destroyer")
        ship_no_yard.cargo_contents = {}
        return [ship_with_yard, ship_no_yard]

    @pytest.mark.parametrize("filter_value,expected_names", [
        pytest.param(FilterState.NO, ["Destroyer"], id="hide_has_spaceyard"),
        pytest.param(FilterState.YES, ["Carrier"], id="hide_no_spaceyard"),
        pytest.param(FilterState.IGNORE, ["Carrier", "Destroyer"], id="ignore_passes_all"),
    ])
    def test_spaceyard_filter(self, filter_value, expected_names):
        """Spaceyard filter respects NO/YES/IGNORE states."""
        from game.ui.screens.fleet_report_filters import filter_ships
        from unittest.mock import patch

        ships = self._make_carrier_destroyer_pair()

        def mock_has_yard(ship):
            return ship.name == "Carrier"

        filter_state = {
            'show_damaged': True,
            'show_undamaged': True,
            'show_derelict': True,
            'show_destroyed': True,
            'has_spaceyard': filter_value,
        }

        with patch(
            'game.strategy.data.fleet_capability_calculator.FleetCapabilityCalculator.ship_has_spaceyard',
            side_effect=mock_has_yard,
        ):
            result = filter_ships(ships, filter_state)

        assert sorted(s.name for s in result) == sorted(expected_names)


class TestFilterShipsCargo:
    """Test cases for cargo filtering in filter_ships.

    PROJ-323 Task 3.1: 3 cargo NO/YES/IGNORE tests parametrized.
    """

    @staticmethod
    def _make_freighter_warship_pair():
        ship_with_cargo = make_mock_ship(design_name="Freighter")
        ship_with_cargo.cargo_contents = {'minerals': 100}
        ship_no_cargo = make_mock_ship(design_name="Warship")
        ship_no_cargo.cargo_contents = {}
        return [ship_with_cargo, ship_no_cargo]

    @pytest.mark.parametrize("filter_value,expected_names", [
        pytest.param(FilterState.NO, ["Warship"], id="hide_has_cargo"),
        pytest.param(FilterState.YES, ["Freighter"], id="hide_no_cargo"),
    ])
    def test_cargo_filter_no_or_yes(self, filter_value, expected_names):
        """Cargo NO/YES filter selects ships by cargo presence."""
        from game.ui.screens.fleet_report_filters import filter_ships

        ships = self._make_freighter_warship_pair()
        filter_state = {
            'show_damaged': True,
            'show_undamaged': True,
            'show_derelict': True,
            'show_destroyed': True,
            'has_cargo': filter_value,
        }
        result = filter_ships(ships, filter_state)
        assert sorted(s.name for s in result) == sorted(expected_names)

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
            'has_cargo': FilterState.NO,
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
            'has_cargo': FilterState.NO,
        }

        result = filter_ships(ships, filter_state)
        assert len(result) == 1  # Treated as no cargo

    def test_filter_show_all_cargo_states(self):
        """IGNORE filter passes all ships through cargo filter."""
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
            'has_cargo': FilterState.IGNORE,
        }

        result = filter_ships(ships, filter_state)
        assert len(result) == 2


class TestFilterStatusPrecedence:
    """Test cases for status filter precedence (PROJ-200)."""

    def test_derelict_ship_not_counted_as_damaged(self):
        """Derelict ship: show_derelict=False, show_damaged=True -> NOT shown.

        A derelict ship is technically damaged, but the derelict filter
        should take precedence. This is a critical invariant.
        """
        from game.ui.screens.fleet_report_filters import filter_ships

        # Create a derelict ship (which is also damaged by definition)
        derelict_ship = make_mock_ship(serial=1, is_derelict=True, is_damaged=True)
        normal_damaged_ship = make_mock_ship(serial=2, is_derelict=False, is_damaged=True)

        ships = [derelict_ship, normal_damaged_ship]

        # Hide derelict but show damaged
        filter_state = {
            'show_damaged': True,
            'show_undamaged': True,
            'show_derelict': False,  # Hide derelict
            'show_destroyed': True,
        }

        result = filter_ships(ships, filter_state)

        # Only the normal damaged ship should be shown
        # The derelict ship should be hidden (derelict takes precedence)
        assert len(result) == 1
        assert result[0].serial == 2


class TestFilterEdgeCases:
    """Test cases for filter edge cases (PROJ-200)."""

    def test_filter_empty_filter_state_shows_all(self):
        """Verify filter_ships(ships, {}) shows all ships (defaults to True)."""
        from game.ui.screens.fleet_report_filters import filter_ships

        ships = [
            make_mock_ship(serial=1, is_damaged=True),
            make_mock_ship(serial=2, is_damaged=False),
            make_mock_ship(serial=3, is_derelict=True),
            make_mock_ship(serial=4, is_alive=False),
        ]

        # Empty filter state - all keys default to True
        result = filter_ships(ships, {})

        assert len(result) == 4

    def test_filter_hide_all_returns_empty(self):
        """Verify setting all status filters to False returns empty list."""
        from game.ui.screens.fleet_report_filters import filter_ships

        ships = [
            make_mock_ship(serial=1, is_damaged=True),
            make_mock_ship(serial=2, is_damaged=False),
            make_mock_ship(serial=3, is_derelict=True),
            make_mock_ship(serial=4, is_alive=False),
        ]

        # All status filters off
        filter_state = {
            'show_damaged': False,
            'show_undamaged': False,
            'show_derelict': False,
            'show_destroyed': False,
        }

        result = filter_ships(ships, filter_state)

        assert len(result) == 0


class TestFilterCombinations:
    """Test cases for multi-filter combinations (PROJ-200)."""

    def test_filter_warp_and_damaged_combined(self):
        """Filter by warp capability AND damaged status simultaneously."""
        from game.ui.screens.fleet_report_filters import filter_ships

        # 4 ships: warp+damaged, warp+undamaged, nowarp+damaged, nowarp+undamaged
        ship_warp_damaged = make_mock_ship(serial=1, mass=1000, warp_tonnage=1500, is_damaged=True)
        ship_warp_undamaged = make_mock_ship(serial=2, mass=1000, warp_tonnage=1500, is_damaged=False)
        ship_nowarp_damaged = make_mock_ship(serial=3, mass=1000, warp_tonnage=None, is_damaged=True)
        ship_nowarp_undamaged = make_mock_ship(serial=4, mass=1000, warp_tonnage=None, is_damaged=False)
        ships = [ship_warp_damaged, ship_warp_undamaged, ship_nowarp_damaged, ship_nowarp_undamaged]

        # Filter: show only warp-capable AND damaged
        filter_state = {
            'show_damaged': True,
            'show_undamaged': False,  # hide undamaged
            'show_derelict': True,
            'show_destroyed': True,
            'warp_capable': FilterState.YES,  # only warp-capable
        }
        result = filter_ships(ships, filter_state)

        assert len(result) == 1
        assert result[0].serial == 1  # only warp+damaged ship

    def test_filter_cargo_and_spaceyard_combined(self):
        """Filter by cargo AND spaceyard simultaneously."""
        from game.ui.screens.fleet_report_filters import filter_ships
        from unittest.mock import patch

        # 4 ships: yard+cargo, yard+nocargo, noyard+cargo, noyard+nocargo
        ship_yard_cargo = make_mock_ship(serial=1, design_name="Carrier")
        ship_yard_cargo.cargo_contents = {'minerals': 100}

        ship_yard_nocargo = make_mock_ship(serial=2, design_name="Station")
        ship_yard_nocargo.cargo_contents = {}

        ship_noyard_cargo = make_mock_ship(serial=3, design_name="Freighter")
        ship_noyard_cargo.cargo_contents = {'food': 50}

        ship_noyard_nocargo = make_mock_ship(serial=4, design_name="Scout")
        ship_noyard_nocargo.cargo_contents = {}

        ships = [ship_yard_cargo, ship_yard_nocargo, ship_noyard_cargo, ship_noyard_nocargo]

        def mock_has_yard(ship):
            return ship.name in ("Carrier", "Station")

        filter_state = {
            'show_damaged': True,
            'show_undamaged': True,
            'show_derelict': True,
            'show_destroyed': True,
            'has_spaceyard': FilterState.YES,  # only ships with spaceyard
            'has_cargo': FilterState.YES,  # only ships with cargo
        }

        with patch('game.strategy.data.fleet_capability_calculator.FleetCapabilityCalculator.ship_has_spaceyard', side_effect=mock_has_yard):
            result = filter_ships(ships, filter_state)

        assert len(result) == 1
        assert result[0].serial == 1  # only yard+cargo ship

    def test_filter_all_categories_active(self):
        """Test with all filter categories having restrictions."""
        from game.ui.screens.fleet_report_filters import filter_ships
        from unittest.mock import patch

        # Ship that passes all filters: warp + spaceyard + cargo + damaged
        ship_pass = make_mock_ship(serial=1, design_name="Flagship", mass=1000, warp_tonnage=1500, is_damaged=True)
        ship_pass.cargo_contents = {'fuel': 100}

        # Ship fails warp filter
        ship_fail_warp = make_mock_ship(serial=2, design_name="Destroyer", mass=1000, warp_tonnage=None, is_damaged=True)
        ship_fail_warp.cargo_contents = {'fuel': 50}

        # Ship fails cargo filter
        ship_fail_cargo = make_mock_ship(serial=3, design_name="Cruiser", mass=1000, warp_tonnage=1500, is_damaged=True)
        ship_fail_cargo.cargo_contents = {}

        # Ship fails damage filter (undamaged)
        ship_fail_damage = make_mock_ship(serial=4, design_name="Battleship", mass=1000, warp_tonnage=1500, is_damaged=False)
        ship_fail_damage.cargo_contents = {'fuel': 75}

        ships = [ship_pass, ship_fail_warp, ship_fail_cargo, ship_fail_damage]

        def mock_has_yard(ship):
            return True  # All have spaceyard

        filter_state = {
            'show_damaged': True,
            'show_undamaged': False,  # exclude undamaged
            'show_derelict': True,
            'show_destroyed': True,
            'warp_capable': FilterState.YES,  # only warp-capable
            'has_cargo': FilterState.YES,  # only ships with cargo
        }

        with patch('game.strategy.data.fleet_capability_calculator.FleetCapabilityCalculator.ship_has_spaceyard', side_effect=mock_has_yard):
            result = filter_ships(ships, filter_state)

        assert len(result) == 1
        assert result[0].serial == 1  # only ship_pass matches all criteria


class TestSpecialCapabilityFilter:
    """Tests for special capability filtering (BUG-83)."""

    def test_filter_hides_ships_with_ability(self):
        """Filter can hide ships that have a special ability."""
        from game.ui.screens.fleet_report_filters import filter_ships
        from unittest.mock import patch

        ship_with = make_mock_ship(serial=1, design_name="Planet Killer")
        ship_without = make_mock_ship(serial=2, design_name="Scout")

        def mock_has_ability(ship, ability_name, registry):
            return ship.serial == 1 and ability_name == 'DestroyPlanet'

        filter_state = {
            'show_damaged': True,
            'show_undamaged': True,
            'show_derelict': True,
            'show_destroyed': True,
            'destroy_planet': FilterState.NO,
        }

        with patch('game.strategy.services.component_inspector.ship_has_ability',
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

        def mock_has_ability(ship, ability_name, registry):
            return ship.serial == 1 and ability_name == 'DestroyPlanet'

        filter_state = {
            'show_damaged': True,
            'show_undamaged': True,
            'show_derelict': True,
            'show_destroyed': True,
            'destroy_planet': FilterState.YES,
        }

        with patch('game.strategy.services.component_inspector.ship_has_ability',
                   side_effect=mock_has_ability):
            result = filter_ships([ship_with, ship_without], filter_state)

        assert len(result) == 1
        assert result[0].serial == 1

    def test_filter_default_shows_all(self):
        """Default filter state shows all ships regardless of special abilities."""
        from game.ui.screens.fleet_report_filters import filter_ships

        ships = [make_mock_ship(serial=i) for i in range(5)]

        # Default filter state - tri-state defaults to IGNORE
        filter_state = {
            'show_damaged': True,
            'show_undamaged': True,
            'show_derelict': True,
            'show_destroyed': True,
        }

        result = filter_ships(ships, filter_state)
        assert len(result) == 5

    # PROJ-323 Task 3.1: 4 special-ability filter tests parametrized.
    @pytest.mark.parametrize("filter_key,ability_name,design_name", [
        pytest.param('open_warp', 'OpenWarpPoint', 'Warp Opener', id='OpenWarpPoint'),
        pytest.param('close_warp', 'CloseWarpPoint', 'Warp Closer', id='CloseWarpPoint'),
        pytest.param('destroy_star', 'DestroyStar', 'Star Destroyer', id='DestroyStar'),
        pytest.param('create_sphere', 'CreateSphereWorld', 'Sphere Builder', id='CreateSphereWorld'),
    ])
    def test_filter_hides_ships_with_ability_by_capability(self, filter_key, ability_name, design_name):
        """Filter hides ships that possess the given special ability when filter_key=NO."""
        from game.ui.screens.fleet_report_filters import filter_ships
        from unittest.mock import patch

        ship_with = make_mock_ship(serial=1, design_name=design_name)
        ship_without = make_mock_ship(serial=2, design_name="Scout")

        def mock_has_ability(ship, requested_ability, registry):
            return ship.serial == 1 and requested_ability == ability_name

        filter_state = {
            'show_damaged': True,
            'show_undamaged': True,
            'show_derelict': True,
            'show_destroyed': True,
            filter_key: FilterState.NO,
        }

        with patch('game.strategy.services.component_inspector.ship_has_ability',
                   side_effect=mock_has_ability):
            result = filter_ships([ship_with, ship_without], filter_state)

        assert len(result) == 1
        assert result[0].serial == 2


class TestSpecialCapabilitySort:
    """Tests for special capability column sorting (BUG-83)."""

    def test_sort_by_special_capability(self):
        """Sort by special capability column puts 'Yes' ships first when descending."""
        from game.ui.screens.fleet_report_filters import sort_ships
        from unittest.mock import patch

        ship1 = make_mock_ship(serial=1, design_name="Scout")
        ship2 = make_mock_ship(serial=2, design_name="Planet Killer")
        ship3 = make_mock_ship(serial=3, design_name="Frigate")

        def mock_has_ability(ship, ability_name, registry):
            return ship.serial == 2 and ability_name == 'DestroyPlanet'

        with patch('game.strategy.services.component_inspector.ship_has_ability',
                   side_effect=mock_has_ability):
            result = sort_ships([ship1, ship2, ship3], 'can_destroy_planet', descending=True)

        # Ship2 (has ability, sort key=1) should be first when descending
        assert result[0].serial == 2


class TestViewModelTriStateFilters:
    """Tests for FleetListViewModel tri-state filter API (PROJ-220)."""

    def test_set_filter_state(self):
        """set_filter_state changes tri-state filter."""
        from game.ui.screens.fleet_report_view_model import FleetListViewModel

        vm = FleetListViewModel()
        assert vm.get_tri_state('destroy_planet') is FilterState.IGNORE

        vm.set_filter_state('destroy_planet', FilterState.YES)
        assert vm.get_tri_state('destroy_planet') is FilterState.YES

    def test_tri_state_filters_in_get_filter_state(self):
        """Tri-state filter keys appear in get_filter_state()."""
        from game.ui.screens.fleet_report_view_model import FleetListViewModel

        vm = FleetListViewModel()
        state = vm.get_filter_state()

        assert state['destroy_planet'] is FilterState.IGNORE
        assert state['open_warp'] is FilterState.IGNORE
        assert state['close_warp'] is FilterState.IGNORE
        assert state['destroy_star'] is FilterState.IGNORE
        assert state['create_sphere'] is FilterState.IGNORE
        assert state['warp_capable'] is FilterState.IGNORE
        assert state['has_spaceyard'] is FilterState.IGNORE
        assert state['has_cargo'] is FilterState.IGNORE

    def test_tri_state_labels(self):
        """Tri-state filters have display labels."""
        from game.ui.screens.fleet_report_view_model import FleetListViewModel

        vm = FleetListViewModel()

        assert vm.get_filter_label('destroy_planet') == 'Destroy Planet'
        assert vm.get_filter_label('open_warp') == 'Open Warp'
        assert vm.get_filter_label('destroy_star') == 'Destroy Star'
        assert vm.get_filter_label('create_sphere') == 'Create Sphere'

    def test_status_toggle_still_works(self):
        """Status filter toggle is unchanged."""
        from game.ui.screens.fleet_report_view_model import FleetListViewModel

        vm = FleetListViewModel()
        assert vm.filter_show_damaged is True

        result = vm.toggle_filter('damaged')
        assert result is False
        assert vm.filter_show_damaged is False

    def test_filter_manager_exposed(self):
        """filter_manager property provides access to FilterStateManager."""
        from game.ui.screens.fleet_report_view_model import FleetListViewModel

        vm = FleetListViewModel()
        mgr = vm.filter_manager
        assert mgr.get_state('warp_capable') is FilterState.IGNORE


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
