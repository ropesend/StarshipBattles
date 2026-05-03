"""
Tests for FleetSpeedCalculator.

TDD Phase 2, Step 2.3: Tests for fleet speed calculation from strategic movement abilities.
"""

from unittest.mock import MagicMock

from game.strategy.services.fleet_speed_calculator import (
    BASE_TICKS_PER_MOVEMENT,
    FleetSpeedCalculator,
    K_STRATEGIC,
    get_tick_interval,
)


def _make_mock_ship_with_stats(
    mass: float,
    strategic_movement: float,
    *,
    vehicle_type: str = "Ship",
    is_combat_capable: bool = True,
    expected_stats_only: bool = False,
):
    """Build a MagicMock ship with the standard `design_data` + `get_calculated_stats`
    + `is_combat_capable` shape used throughout this file.

    `expected_stats_only=True` skips the `get_calculated_stats` setup so callers
    can simulate "missing stats" / fighter / complex shapes.
    """
    stats = {"mass": mass, "strategic_movement": strategic_movement}
    ship = MagicMock()
    ship.design_data = {"vehicle_type": vehicle_type, "expected_stats": stats}
    if not expected_stats_only:
        ship.get_calculated_stats.return_value = stats
    ship.is_combat_capable.return_value = is_combat_capable
    return ship


def _make_mock_fleet(ships):
    fleet = MagicMock()
    fleet.ships = list(ships)
    fleet.get_ship_instances.return_value = list(ships)
    fleet.speed = 5.0
    return fleet


class TestFleetSpeedCalculatorShipSpeed:
    """Tests for calculate_ship_speed() method."""

    def test_calculate_ship_speed_formula(self):
        """Ship speed should follow the formula: floor((mp * K_STRATEGIC) / mass)."""
        # mass=1000, strategic_movement=100 -> (100 * 25) / 1000 = 2500 / 1000 = 2.5 -> 2
        ship = _make_mock_ship_with_stats(mass=1000, strategic_movement=100)
        speed = FleetSpeedCalculator.calculate_ship_speed(ship)
        expected = int((100 * K_STRATEGIC) / 1000)  # 2
        assert speed == expected

    def test_calculate_ship_speed_higher_movement(self):
        """Higher movement points should result in higher speed."""
        # mass=1000, strategic_movement=300 -> (300 * 25) / 1000 = 7500 / 1000 = 7.5 -> 7
        ship = _make_mock_ship_with_stats(mass=1000, strategic_movement=300)
        speed = FleetSpeedCalculator.calculate_ship_speed(ship)
        expected = int((300 * K_STRATEGIC) / 1000)  # 7
        assert speed == expected

    def test_calculate_ship_speed_clamped_to_max(self):
        """Ship speed should be clamped to maximum of 10 hexes/turn."""
        # Extremely high movement points should still cap at 10
        ship = _make_mock_ship_with_stats(mass=100, strategic_movement=10000)
        speed = FleetSpeedCalculator.calculate_ship_speed(ship)
        assert speed == 10  # Capped at maximum

    def test_calculate_ship_speed_zero_for_fighters(self):
        """Fighters should have 0 strategic movement (carrier-based)."""
        ship = _make_mock_ship_with_stats(
            mass=25, strategic_movement=40,
            vehicle_type="Fighter", expected_stats_only=True,
        )
        speed = FleetSpeedCalculator.calculate_ship_speed(ship)
        assert speed == 0

    def test_calculate_ship_speed_zero_for_complexes(self):
        """Planetary Complexes should have 0 strategic movement."""
        ship = _make_mock_ship_with_stats(
            mass=10000, strategic_movement=0,
            vehicle_type="Planetary Complex", expected_stats_only=True,
        )
        speed = FleetSpeedCalculator.calculate_ship_speed(ship)
        assert speed == 0

    def test_calculate_ship_speed_zero_for_no_movement(self):
        """Ships with no strategic movement should return 0."""
        ship = _make_mock_ship_with_stats(mass=1000, strategic_movement=0)
        speed = FleetSpeedCalculator.calculate_ship_speed(ship)
        assert speed == 0

    def test_calculate_ship_speed_handles_missing_stats(self):
        """Should handle missing expected_stats gracefully."""
        ship = MagicMock()
        ship.design_data = {"vehicle_type": "Ship"}  # No expected_stats
        # get_calculated_stats returns empty dict when no components
        ship.get_calculated_stats.return_value = {}
        speed = FleetSpeedCalculator.calculate_ship_speed(ship)
        assert speed == 0


class TestFleetSpeedCalculatorFleetSpeed:
    """Tests for calculate_fleet_speed() method."""

    def test_calculate_fleet_speed_uses_slowest(self):
        """Fleet speed should be the minimum of all ship speeds."""
        fast_ship = _make_mock_ship_with_stats(mass=500, strategic_movement=200)
        slow_ship = _make_mock_ship_with_stats(mass=10000, strategic_movement=100)
        fleet = _make_mock_fleet([fast_ship, slow_ship])

        speed = FleetSpeedCalculator.calculate_fleet_speed(fleet)

        # Should be the slower ship's speed
        slow_speed = FleetSpeedCalculator.calculate_ship_speed(slow_ship)
        assert speed == float(slow_speed)

    def test_calculate_fleet_speed_single_ship(self):
        """Fleet with one ship should use that ship's speed."""
        ship = _make_mock_ship_with_stats(mass=1000, strategic_movement=150)
        fleet = _make_mock_fleet([ship])

        speed = FleetSpeedCalculator.calculate_fleet_speed(fleet)

        expected = FleetSpeedCalculator.calculate_ship_speed(ship)
        assert speed == float(expected)

    def test_calculate_fleet_speed_empty_fleet(self):
        """Empty fleet should return 0."""
        fleet = _make_mock_fleet([])
        speed = FleetSpeedCalculator.calculate_fleet_speed(fleet)
        assert speed == 0.0

    def test_calculate_fleet_speed_excludes_destroyed(self):
        """Should exclude destroyed/derelict ships from speed calculation."""
        working_ship = _make_mock_ship_with_stats(mass=1000, strategic_movement=100)
        destroyed_ship = _make_mock_ship_with_stats(
            mass=500, strategic_movement=50, is_combat_capable=False,
        )
        fleet = _make_mock_fleet([working_ship, destroyed_ship])

        speed = FleetSpeedCalculator.calculate_fleet_speed(fleet)

        # Should only consider the working ship
        expected = FleetSpeedCalculator.calculate_ship_speed(working_ship)
        assert speed == float(expected)

    def test_update_fleet_speed_updates_attribute(self):
        """update_fleet_speed() should update fleet.speed attribute."""
        ship = _make_mock_ship_with_stats(mass=1000, strategic_movement=150)
        fleet = _make_mock_fleet([ship])

        FleetSpeedCalculator.update_fleet_speed(fleet)

        # Check that fleet.speed was updated
        expected = float(FleetSpeedCalculator.calculate_ship_speed(ship))
        assert fleet.speed == expected


class TestFleetSpeedCalculatorStrategicMult:
    """PROJ-300 Phase 7: signature simplified to take a scalar multiplier."""

    def test_strategic_mult_half_halves_speed(self):
        ship = _make_mock_ship_with_stats(mass=1000, strategic_movement=250)
        fleet = _make_mock_fleet([ship])

        base_speed = FleetSpeedCalculator.calculate_fleet_speed(fleet)
        assert base_speed == 6.0

        storm_speed = FleetSpeedCalculator.calculate_fleet_speed_with_strategic_mult(
            fleet, strategic_mult=0.5,
        )
        assert storm_speed == 3.0

    def test_strategic_mult_one_unchanged_speed(self):
        ship = _make_mock_ship_with_stats(mass=1000, strategic_movement=200)
        fleet = _make_mock_fleet([ship])

        base_speed = FleetSpeedCalculator.calculate_fleet_speed(fleet)
        storm_speed = FleetSpeedCalculator.calculate_fleet_speed_with_strategic_mult(
            fleet, strategic_mult=1.0,
        )
        assert storm_speed == base_speed

    def test_strategic_mult_extreme_still_clamps_to_zero(self):
        ship = _make_mock_ship_with_stats(mass=1000, strategic_movement=100)
        fleet = _make_mock_fleet([ship])

        storm_speed = FleetSpeedCalculator.calculate_fleet_speed_with_strategic_mult(
            fleet, strategic_mult=0.1,
        )
        assert storm_speed >= 0.0

    def test_default_strategic_mult_same_as_base(self):
        """Default strategic_mult=1.0 returns base speed unchanged."""
        ship = _make_mock_ship_with_stats(mass=1000, strategic_movement=200)
        fleet = _make_mock_fleet([ship])

        base_speed = FleetSpeedCalculator.calculate_fleet_speed(fleet)
        env_speed = FleetSpeedCalculator.calculate_fleet_speed_with_strategic_mult(fleet)

        assert env_speed == base_speed


class TestGetTickInterval:
    """Tests for get_tick_interval() function (PROJ-204 Phase 2, CQ-44)."""

    def test_speed_ten_gives_interval_ten(self):
        """Speed 10 should give tick interval of 10 (fastest)."""
        assert get_tick_interval(10.0) == 10

    def test_speed_five_gives_interval_twenty(self):
        """Speed 5 should give tick interval of 20 (medium)."""
        assert get_tick_interval(5.0) == 20

    def test_speed_one_gives_interval_hundred(self):
        """Speed 1 should give tick interval of 100 (slow)."""
        assert get_tick_interval(1.0) == 100

    def test_speed_two_gives_interval_fifty(self):
        """Speed 2 should give tick interval of 50."""
        assert get_tick_interval(2.0) == 50

    def test_speed_zero_gives_maximum_interval(self):
        """Speed 0 (immobile) should give maximum interval of 100."""
        assert get_tick_interval(0.0) == BASE_TICKS_PER_MOVEMENT

    def test_negative_speed_gives_maximum_interval(self):
        """Negative speed should give maximum interval (safety case)."""
        assert get_tick_interval(-5.0) == BASE_TICKS_PER_MOVEMENT

    def test_interval_minimum_is_one(self):
        """Very high speed should still give minimum interval of 1."""
        # Speed 1000 would give 100 // 1000 = 0, but clamped to 1
        assert get_tick_interval(1000.0) == 1

    def test_fractional_speed_rounds_down_interval(self):
        """Fractional speed should round interval properly."""
        # Speed 3.0 -> 100 // 3 = 33
        assert get_tick_interval(3.0) == 33

    def test_returns_integer(self):
        """Interval should always be an integer."""
        assert isinstance(get_tick_interval(7.5), int)
