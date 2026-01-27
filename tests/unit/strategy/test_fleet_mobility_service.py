"""
Tests for FleetMobilityService.

TDD Phase 2, Step 2.3: Tests for fleet speed calculation from strategic movement abilities.
"""

from unittest.mock import MagicMock


class TestFleetMobilityServiceShipSpeed:
    """Tests for calculate_ship_speed() method."""

    def test_calculate_ship_speed_formula(self):
        """Ship speed should follow the formula: floor((mp * K_STRATEGIC) / mass)."""
        from game.strategy.services.fleet_mobility_service import FleetMobilityService, K_STRATEGIC

        # Create mock ship instance with known values
        # mass=1000, strategic_movement=100 -> (100 * 25) / 1000 = 2500 / 1000 = 2.5 -> 2
        ship_instance = MagicMock()
        stats = {'mass': 1000, 'strategic_movement': 100}
        ship_instance.design_data = {
            'vehicle_type': 'Ship',
            'expected_stats': stats
        }
        ship_instance.get_calculated_stats.return_value = stats

        speed = FleetMobilityService.calculate_ship_speed(ship_instance)

        expected = int((100 * K_STRATEGIC) / 1000)  # 2
        assert speed == expected

    def test_calculate_ship_speed_higher_movement(self):
        """Higher movement points should result in higher speed."""
        from game.strategy.services.fleet_mobility_service import FleetMobilityService, K_STRATEGIC

        # mass=1000, strategic_movement=300 -> (300 * 25) / 1000 = 7500 / 1000 = 7.5 -> 7
        ship_instance = MagicMock()
        stats = {'mass': 1000, 'strategic_movement': 300}
        ship_instance.design_data = {
            'vehicle_type': 'Ship',
            'expected_stats': stats
        }
        ship_instance.get_calculated_stats.return_value = stats

        speed = FleetMobilityService.calculate_ship_speed(ship_instance)

        expected = int((300 * K_STRATEGIC) / 1000)  # 7
        assert speed == expected

    def test_calculate_ship_speed_clamped_to_max(self):
        """Ship speed should be clamped to maximum of 10 hexes/turn."""
        from game.strategy.services.fleet_mobility_service import FleetMobilityService

        # Extremely high movement points should still cap at 10
        ship_instance = MagicMock()
        stats = {'mass': 100, 'strategic_movement': 10000}  # Very light, very high
        ship_instance.design_data = {
            'vehicle_type': 'Ship',
            'expected_stats': stats
        }
        ship_instance.get_calculated_stats.return_value = stats

        speed = FleetMobilityService.calculate_ship_speed(ship_instance)

        assert speed == 10  # Capped at maximum

    def test_calculate_ship_speed_zero_for_fighters(self):
        """Fighters should have 0 strategic movement (carrier-based)."""
        from game.strategy.services.fleet_mobility_service import FleetMobilityService

        ship_instance = MagicMock()
        ship_instance.design_data = {
            'vehicle_type': 'Fighter',
            'expected_stats': {
                'mass': 25,
                'strategic_movement': 40  # Even if they have movement points
            }
        }

        speed = FleetMobilityService.calculate_ship_speed(ship_instance)

        assert speed == 0

    def test_calculate_ship_speed_zero_for_complexes(self):
        """Planetary Complexes should have 0 strategic movement."""
        from game.strategy.services.fleet_mobility_service import FleetMobilityService

        ship_instance = MagicMock()
        ship_instance.design_data = {
            'vehicle_type': 'Planetary Complex',
            'expected_stats': {
                'mass': 10000,
                'strategic_movement': 0
            }
        }

        speed = FleetMobilityService.calculate_ship_speed(ship_instance)

        assert speed == 0

    def test_calculate_ship_speed_zero_for_no_movement(self):
        """Ships with no strategic movement should return 0."""
        from game.strategy.services.fleet_mobility_service import FleetMobilityService

        ship_instance = MagicMock()
        stats = {'mass': 1000, 'strategic_movement': 0}
        ship_instance.design_data = {
            'vehicle_type': 'Ship',
            'expected_stats': stats
        }
        ship_instance.get_calculated_stats.return_value = stats

        speed = FleetMobilityService.calculate_ship_speed(ship_instance)

        assert speed == 0

    def test_calculate_ship_speed_handles_missing_stats(self):
        """Should handle missing expected_stats gracefully."""
        from game.strategy.services.fleet_mobility_service import FleetMobilityService

        ship_instance = MagicMock()
        ship_instance.design_data = {
            'vehicle_type': 'Ship',
            # No expected_stats
        }
        # get_calculated_stats returns empty dict when no components
        ship_instance.get_calculated_stats.return_value = {}

        speed = FleetMobilityService.calculate_ship_speed(ship_instance)

        assert speed == 0


class TestFleetMobilityServiceFleetSpeed:
    """Tests for calculate_fleet_speed() method."""

    def test_calculate_fleet_speed_uses_slowest(self):
        """Fleet speed should be the minimum of all ship speeds."""
        from game.strategy.services.fleet_mobility_service import FleetMobilityService

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

        speed = FleetMobilityService.calculate_fleet_speed(fleet)

        # Should be the slower ship's speed
        slow_speed = FleetMobilityService.calculate_ship_speed(slow_ship)
        assert speed == float(slow_speed)

    def test_calculate_fleet_speed_single_ship(self):
        """Fleet with one ship should use that ship's speed."""
        from game.strategy.services.fleet_mobility_service import FleetMobilityService

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

        speed = FleetMobilityService.calculate_fleet_speed(fleet)

        expected = FleetMobilityService.calculate_ship_speed(ship)
        assert speed == float(expected)

    def test_calculate_fleet_speed_empty_fleet(self):
        """Empty fleet should return 0."""
        from game.strategy.services.fleet_mobility_service import FleetMobilityService

        fleet = MagicMock()
        fleet.ships = []
        fleet.speed = 5.0

        speed = FleetMobilityService.calculate_fleet_speed(fleet)

        assert speed == 0.0

    def test_calculate_fleet_speed_excludes_destroyed(self):
        """Should exclude destroyed/derelict ships from speed calculation."""
        from game.strategy.services.fleet_mobility_service import FleetMobilityService

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

        speed = FleetMobilityService.calculate_fleet_speed(fleet)

        # Should only consider the working ship
        expected = FleetMobilityService.calculate_ship_speed(working_ship)
        assert speed == float(expected)

    def test_recalculate_fleet_speed_updates_attribute(self):
        """recalculate_fleet_speed() should update fleet.speed attribute."""
        from game.strategy.services.fleet_mobility_service import FleetMobilityService

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

        FleetMobilityService.recalculate_fleet_speed(fleet)

        # Check that fleet.speed was updated
        expected = float(FleetMobilityService.calculate_ship_speed(ship))
        assert fleet.speed == expected
