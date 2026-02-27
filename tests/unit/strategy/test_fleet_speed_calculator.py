"""
Tests for FleetSpeedCalculator.

TDD Phase 2, Step 2.3: Tests for fleet speed calculation from strategic movement abilities.
"""

from unittest.mock import MagicMock


class TestFleetSpeedCalculatorShipSpeed:
    """Tests for calculate_ship_speed() method."""

    def test_calculate_ship_speed_formula(self):
        """Ship speed should follow the formula: floor((mp * K_STRATEGIC) / mass)."""
        from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator, K_STRATEGIC

        # Create mock ship instance with known values
        # mass=1000, strategic_movement=100 -> (100 * 25) / 1000 = 2500 / 1000 = 2.5 -> 2
        ship_instance = MagicMock()
        stats = {'mass': 1000, 'strategic_movement': 100}
        ship_instance.design_data = {
            'vehicle_type': 'Ship',
            'expected_stats': stats
        }
        ship_instance.get_calculated_stats.return_value = stats

        speed = FleetSpeedCalculator.calculate_ship_speed(ship_instance)

        expected = int((100 * K_STRATEGIC) / 1000)  # 2
        assert speed == expected

    def test_calculate_ship_speed_higher_movement(self):
        """Higher movement points should result in higher speed."""
        from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator, K_STRATEGIC

        # mass=1000, strategic_movement=300 -> (300 * 25) / 1000 = 7500 / 1000 = 7.5 -> 7
        ship_instance = MagicMock()
        stats = {'mass': 1000, 'strategic_movement': 300}
        ship_instance.design_data = {
            'vehicle_type': 'Ship',
            'expected_stats': stats
        }
        ship_instance.get_calculated_stats.return_value = stats

        speed = FleetSpeedCalculator.calculate_ship_speed(ship_instance)

        expected = int((300 * K_STRATEGIC) / 1000)  # 7
        assert speed == expected

    def test_calculate_ship_speed_clamped_to_max(self):
        """Ship speed should be clamped to maximum of 10 hexes/turn."""
        from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator

        # Extremely high movement points should still cap at 10
        ship_instance = MagicMock()
        stats = {'mass': 100, 'strategic_movement': 10000}  # Very light, very high
        ship_instance.design_data = {
            'vehicle_type': 'Ship',
            'expected_stats': stats
        }
        ship_instance.get_calculated_stats.return_value = stats

        speed = FleetSpeedCalculator.calculate_ship_speed(ship_instance)

        assert speed == 10  # Capped at maximum

    def test_calculate_ship_speed_zero_for_fighters(self):
        """Fighters should have 0 strategic movement (carrier-based)."""
        from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator

        ship_instance = MagicMock()
        ship_instance.design_data = {
            'vehicle_type': 'Fighter',
            'expected_stats': {
                'mass': 25,
                'strategic_movement': 40  # Even if they have movement points
            }
        }

        speed = FleetSpeedCalculator.calculate_ship_speed(ship_instance)

        assert speed == 0

    def test_calculate_ship_speed_zero_for_complexes(self):
        """Planetary Complexes should have 0 strategic movement."""
        from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator

        ship_instance = MagicMock()
        ship_instance.design_data = {
            'vehicle_type': 'Planetary Complex',
            'expected_stats': {
                'mass': 10000,
                'strategic_movement': 0
            }
        }

        speed = FleetSpeedCalculator.calculate_ship_speed(ship_instance)

        assert speed == 0

    def test_calculate_ship_speed_zero_for_no_movement(self):
        """Ships with no strategic movement should return 0."""
        from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator

        ship_instance = MagicMock()
        stats = {'mass': 1000, 'strategic_movement': 0}
        ship_instance.design_data = {
            'vehicle_type': 'Ship',
            'expected_stats': stats
        }
        ship_instance.get_calculated_stats.return_value = stats

        speed = FleetSpeedCalculator.calculate_ship_speed(ship_instance)

        assert speed == 0

    def test_calculate_ship_speed_handles_missing_stats(self):
        """Should handle missing expected_stats gracefully."""
        from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator

        ship_instance = MagicMock()
        ship_instance.design_data = {
            'vehicle_type': 'Ship',
            # No expected_stats
        }
        # get_calculated_stats returns empty dict when no components
        ship_instance.get_calculated_stats.return_value = {}

        speed = FleetSpeedCalculator.calculate_ship_speed(ship_instance)

        assert speed == 0


class TestFleetSpeedCalculatorFleetSpeed:
    """Tests for calculate_fleet_speed() method."""

    def test_calculate_fleet_speed_uses_slowest(self):
        """Fleet speed should be the minimum of all ship speeds."""
        from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator

        # Create fleet with two ships - one fast, one slow
        fast_stats = {'mass': 500, 'strategic_movement': 200}
        fast_ship = MagicMock()
        fast_ship.design_data = {
            'vehicle_type': 'Ship',
            'expected_stats': fast_stats
        }
        fast_ship.get_calculated_stats.return_value = fast_stats
        fast_ship.is_combat_capable.return_value = True

        slow_stats = {'mass': 10000, 'strategic_movement': 100}
        slow_ship = MagicMock()
        slow_ship.design_data = {
            'vehicle_type': 'Ship',
            'expected_stats': slow_stats
        }
        slow_ship.get_calculated_stats.return_value = slow_stats
        slow_ship.is_combat_capable.return_value = True

        fleet = MagicMock()
        fleet.get_ship_instances.return_value = [fast_ship, slow_ship]
        fleet.speed = 5.0  # Default

        speed = FleetSpeedCalculator.calculate_fleet_speed(fleet)

        # Should be the slower ship's speed
        slow_speed = FleetSpeedCalculator.calculate_ship_speed(slow_ship)
        assert speed == float(slow_speed)

    def test_calculate_fleet_speed_single_ship(self):
        """Fleet with one ship should use that ship's speed."""
        from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator

        stats = {'mass': 1000, 'strategic_movement': 150}
        ship = MagicMock()
        ship.design_data = {
            'vehicle_type': 'Ship',
            'expected_stats': stats
        }
        ship.get_calculated_stats.return_value = stats
        ship.is_combat_capable.return_value = True

        fleet = MagicMock()
        fleet.ships = [ship]
        fleet.speed = 5.0

        speed = FleetSpeedCalculator.calculate_fleet_speed(fleet)

        expected = FleetSpeedCalculator.calculate_ship_speed(ship)
        assert speed == float(expected)

    def test_calculate_fleet_speed_empty_fleet(self):
        """Empty fleet should return 0."""
        from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator

        fleet = MagicMock()
        fleet.ships = []
        fleet.speed = 5.0

        speed = FleetSpeedCalculator.calculate_fleet_speed(fleet)

        assert speed == 0.0

    def test_calculate_fleet_speed_excludes_destroyed(self):
        """Should exclude destroyed/derelict ships from speed calculation."""
        from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator

        working_stats = {'mass': 1000, 'strategic_movement': 100}
        working_ship = MagicMock()
        working_ship.design_data = {
            'vehicle_type': 'Ship',
            'expected_stats': working_stats
        }
        working_ship.get_calculated_stats.return_value = working_stats
        working_ship.is_combat_capable.return_value = True

        destroyed_stats = {'mass': 500, 'strategic_movement': 50}  # Would be slower
        destroyed_ship = MagicMock()
        destroyed_ship.design_data = {
            'vehicle_type': 'Ship',
            'expected_stats': destroyed_stats
        }
        destroyed_ship.get_calculated_stats.return_value = destroyed_stats
        destroyed_ship.is_combat_capable.return_value = False  # Destroyed

        fleet = MagicMock()
        fleet.ships = [working_ship, destroyed_ship]

        speed = FleetSpeedCalculator.calculate_fleet_speed(fleet)

        # Should only consider the working ship
        expected = FleetSpeedCalculator.calculate_ship_speed(working_ship)
        assert speed == float(expected)

    def test_update_fleet_speed_updates_attribute(self):
        """update_fleet_speed() should update fleet.speed attribute."""
        from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator

        stats = {'mass': 1000, 'strategic_movement': 150}
        ship = MagicMock()
        ship.design_data = {
            'vehicle_type': 'Ship',
            'expected_stats': stats
        }
        ship.get_calculated_stats.return_value = stats
        ship.is_combat_capable.return_value = True

        fleet = MagicMock()
        fleet.ships = [ship]
        fleet.speed = 5.0  # Original value

        FleetSpeedCalculator.update_fleet_speed(fleet)

        # Check that fleet.speed was updated
        expected = float(FleetSpeedCalculator.calculate_ship_speed(ship))
        assert fleet.speed == expected


class TestFleetSpeedCalculatorEnvironmentalEffects:
    """Tests for environmental effects integration (PROJ-189 Phase 4)."""

    def test_strategic_mult_half_halves_speed(self):
        """Fleet with strategic_mult=0.5 has half the speed."""
        from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator
        from game.strategy.services.area_effect_manager import EnvironmentalEffects

        # Create ship with base speed of 6 hexes/turn
        # mass=1000, strategic_movement=250 -> (250 * 25) / 1000 = 6.25 -> 6
        stats = {'mass': 1000, 'strategic_movement': 250}
        ship = MagicMock()
        ship.design_data = {'vehicle_type': 'Ship', 'expected_stats': stats}
        ship.get_calculated_stats.return_value = stats
        ship.is_combat_capable.return_value = True

        fleet = MagicMock()
        fleet.ships = [ship]

        # Base speed (no storm)
        base_speed = FleetSpeedCalculator.calculate_fleet_speed(fleet)
        assert base_speed == 6.0

        # Speed with 50% storm penalty
        env_effects = EnvironmentalEffects(strategic_mult=0.5)
        storm_speed = FleetSpeedCalculator.calculate_fleet_speed_with_environment(
            fleet, env_effects
        )

        # 6 * 0.5 = 3
        assert storm_speed == 3.0

    def test_strategic_mult_one_unchanged_speed(self):
        """Fleet with strategic_mult=1.0 (no storm) has unchanged speed."""
        from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator
        from game.strategy.services.area_effect_manager import EnvironmentalEffects

        stats = {'mass': 1000, 'strategic_movement': 200}
        ship = MagicMock()
        ship.design_data = {'vehicle_type': 'Ship', 'expected_stats': stats}
        ship.get_calculated_stats.return_value = stats
        ship.is_combat_capable.return_value = True

        fleet = MagicMock()
        fleet.ships = [ship]

        base_speed = FleetSpeedCalculator.calculate_fleet_speed(fleet)

        env_effects = EnvironmentalEffects(strategic_mult=1.0)
        storm_speed = FleetSpeedCalculator.calculate_fleet_speed_with_environment(
            fleet, env_effects
        )

        assert storm_speed == base_speed

    def test_strategic_mult_extreme_still_clamps_to_zero(self):
        """Fleet with strategic_mult=0.1 still has at least speed 0 (clamping works)."""
        from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator
        from game.strategy.services.area_effect_manager import EnvironmentalEffects

        # Create ship with base speed of 2 hexes/turn
        stats = {'mass': 1000, 'strategic_movement': 100}
        ship = MagicMock()
        ship.design_data = {'vehicle_type': 'Ship', 'expected_stats': stats}
        ship.get_calculated_stats.return_value = stats
        ship.is_combat_capable.return_value = True

        fleet = MagicMock()
        fleet.ships = [ship]

        # With extreme reduction, speed should still be >= 0
        env_effects = EnvironmentalEffects(strategic_mult=0.1)
        storm_speed = FleetSpeedCalculator.calculate_fleet_speed_with_environment(
            fleet, env_effects
        )

        # 2 * 0.1 = 0.2 -> floors to 0
        assert storm_speed >= 0.0

    def test_none_environmental_effects_same_as_base(self):
        """When environmental_effects is None, use base calculation."""
        from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator

        stats = {'mass': 1000, 'strategic_movement': 200}
        ship = MagicMock()
        ship.design_data = {'vehicle_type': 'Ship', 'expected_stats': stats}
        ship.get_calculated_stats.return_value = stats
        ship.is_combat_capable.return_value = True

        fleet = MagicMock()
        fleet.ships = [ship]

        base_speed = FleetSpeedCalculator.calculate_fleet_speed(fleet)
        env_speed = FleetSpeedCalculator.calculate_fleet_speed_with_environment(
            fleet, None
        )

        assert env_speed == base_speed


class TestGetTickInterval:
    """Tests for get_tick_interval() function (PROJ-204 Phase 2, CQ-44)."""

    def test_speed_ten_gives_interval_ten(self):
        """Speed 10 should give tick interval of 10 (fastest)."""
        from game.strategy.services.fleet_speed_calculator import get_tick_interval

        interval = get_tick_interval(10.0)

        assert interval == 10

    def test_speed_five_gives_interval_twenty(self):
        """Speed 5 should give tick interval of 20 (medium)."""
        from game.strategy.services.fleet_speed_calculator import get_tick_interval

        interval = get_tick_interval(5.0)

        assert interval == 20

    def test_speed_one_gives_interval_hundred(self):
        """Speed 1 should give tick interval of 100 (slow)."""
        from game.strategy.services.fleet_speed_calculator import get_tick_interval

        interval = get_tick_interval(1.0)

        assert interval == 100

    def test_speed_two_gives_interval_fifty(self):
        """Speed 2 should give tick interval of 50."""
        from game.strategy.services.fleet_speed_calculator import get_tick_interval

        interval = get_tick_interval(2.0)

        assert interval == 50

    def test_speed_zero_gives_maximum_interval(self):
        """Speed 0 (immobile) should give maximum interval of 100."""
        from game.strategy.services.fleet_speed_calculator import get_tick_interval, BASE_TICKS_PER_MOVEMENT

        interval = get_tick_interval(0.0)

        assert interval == BASE_TICKS_PER_MOVEMENT

    def test_negative_speed_gives_maximum_interval(self):
        """Negative speed should give maximum interval (safety case)."""
        from game.strategy.services.fleet_speed_calculator import get_tick_interval, BASE_TICKS_PER_MOVEMENT

        interval = get_tick_interval(-5.0)

        assert interval == BASE_TICKS_PER_MOVEMENT

    def test_interval_minimum_is_one(self):
        """Very high speed should still give minimum interval of 1."""
        from game.strategy.services.fleet_speed_calculator import get_tick_interval

        # Speed 1000 would give 100 // 1000 = 0, but clamped to 1
        interval = get_tick_interval(1000.0)

        assert interval == 1

    def test_fractional_speed_rounds_down_interval(self):
        """Fractional speed should round interval properly."""
        from game.strategy.services.fleet_speed_calculator import get_tick_interval

        # Speed 3.0 -> 100 // 3 = 33
        interval = get_tick_interval(3.0)

        assert interval == 33

    def test_returns_integer(self):
        """Interval should always be an integer."""
        from game.strategy.services.fleet_speed_calculator import get_tick_interval

        interval = get_tick_interval(7.5)

        assert isinstance(interval, int)
