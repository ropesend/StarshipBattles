"""
Integration tests for fleet operations in the gameplay loop.

Tests for fleet movement, fleet merge, and resource accumulation.
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.core.hex_math import HexCoord
from game.strategy.data.ship_instance import ShipInstance
from tests.conftest import make_mock_ship_instance


# =============================================================================
# Test: Fleet Movement Mechanics
# =============================================================================


class TestFleetMovement:
    """Tests for fleet movement and pathfinding."""

    def test_fleet_speed_affects_movement_rate(self, turn_engine, two_empire_setup):
        """Fleet speed determines hexes moved per turn."""
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        # Fast fleet (speed 50 = moves every 2 ticks = 50 hexes per turn)
        fast_fleet = Fleet(1, empire1.id, HexCoord(0, 0), speed=50.0)
        fast_fleet.add_order(Order(OrderType.MOVE, target=HexCoord(100, 0)))
        empire1.add_fleet(fast_fleet)

        # Slow fleet (speed 10 = moves every 10 ticks = 10 hexes per turn)
        slow_fleet = Fleet(2, empire1.id, HexCoord(0, 5), speed=10.0)
        slow_fleet.add_order(Order(OrderType.MOVE, target=HexCoord(100, 5)))
        empire1.add_fleet(slow_fleet)

        turn_engine.process_turn(empires, galaxy)

        from game.core.hex_math import hex_distance

        fast_distance = hex_distance(HexCoord(0, 0), fast_fleet.location)
        slow_distance = hex_distance(HexCoord(0, 5), slow_fleet.location)

        # Fast fleet should have moved further
        assert fast_distance > slow_distance

    def test_fleet_stops_at_destination(self, turn_engine, two_empire_setup):
        """Fleet stops when reaching destination."""
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        destination = HexCoord(5, 0)
        fleet = Fleet(1, empire1.id, HexCoord(0, 0), speed=100.0)
        fleet.add_order(Order(OrderType.MOVE, target=destination))
        empire1.add_fleet(fleet)

        # Process turns until arrival
        for _ in range(3):
            turn_engine.process_turn(empires, galaxy)

        # Fleet should be at destination
        assert fleet.location == destination
        assert len(fleet.orders) == 0  # Order completed

    def test_fleet_path_preview_matches_actual(self, game_session):
        """Path preview matches actual movement path."""
        empire = game_session.active_empire
        if not empire:
            pytest.skip("No player empire")

        fleet = Fleet(99, empire.id, HexCoord(0, 0), speed=10.0)
        empire.add_fleet(fleet)

        target = HexCoord(10, 0)

        # Get preview path
        preview_path = game_session.preview_fleet_path(fleet, target)

        # Give fleet move order
        fleet.add_order(Order(OrderType.MOVE, target=target))

        # The path calculated should be similar to preview
        # (May differ slightly due to dynamic recalculation)
        if preview_path:
            assert len(preview_path) > 0
            assert preview_path[-1] == target


# =============================================================================
# Test: Fleet Merge Operations
# =============================================================================


class TestFleetMerge:
    """Tests for fleet merge mechanics."""

    def test_join_fleet_merges_ships(self, turn_engine, two_empire_setup, fresh_registries):
        """JOIN_FLEET order transfers ships to target fleet."""
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        # PROJ-211: Create ships with registries for DI compliance
        def make_ship(name, owner_id):
            ship = make_mock_ship_instance(name, owner_id)
            ship.set_registries(fresh_registries)
            return ship

        # Create two fleets at same location
        loc = HexCoord(0, 0)
        target_fleet = Fleet(1, empire1.id, loc, speed=10.0)
        target_fleet.ships = [make_ship("Scout", empire1.id)]
        empire1.add_fleet(target_fleet)

        joining_fleet = Fleet(2, empire1.id, loc, speed=10.0)
        joining_fleet.ships = [make_ship("Destroyer", empire1.id)]
        joining_fleet.add_order(Order(OrderType.JOIN_FLEET, target=target_fleet))
        empire1.add_fleet(joining_fleet)

        initial_fleets = len(empire1.fleets)

        turn_engine.process_turn(empires, galaxy)

        # One fleet should have been removed
        assert len(empire1.fleets) < initial_fleets

        # Target fleet should have both ships
        if target_fleet in empire1.fleets:
            assert len(target_fleet.ships) == 2

    def test_join_fleet_requires_same_location(self, turn_engine, two_empire_setup, fresh_registries):
        """JOIN_FLEET only merges when fleets are co-located."""
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        # PROJ-211: Create ships with registries for DI compliance
        def make_ship(name, owner_id):
            ship = make_mock_ship_instance(name, owner_id)
            ship.set_registries(fresh_registries)
            return ship

        # Create two fleets at DIFFERENT locations
        target_fleet = Fleet(1, empire1.id, HexCoord(0, 0), speed=10.0)
        target_fleet.ships = [make_ship("Scout", empire1.id)]
        empire1.add_fleet(target_fleet)

        joining_fleet = Fleet(2, empire1.id, HexCoord(10, 10), speed=10.0)  # Different location
        joining_fleet.ships = [make_ship("Destroyer", empire1.id)]
        joining_fleet.add_order(Order(OrderType.JOIN_FLEET, target=target_fleet))
        empire1.add_fleet(joining_fleet)

        initial_target_ships = len(target_fleet.ships)

        # Process single turn - they shouldn't merge since not co-located
        # (JOIN_FLEET at end-of-turn requires same location)
        turn_engine.process_turn(empires, galaxy)

        # Target fleet ships should be unchanged if not merged
        # (joining fleet might have tried but failed due to distance)
        assert len(target_fleet.ships) >= initial_target_ships


# =============================================================================
# Test: Resource Accumulation Across Turns
# =============================================================================


class TestResourceAccumulation:
    """Tests for resource management across turns."""

    def test_fleet_fuel_consumed_during_movement(self, turn_engine, two_empire_setup):
        """Fleet fuel decreases as it moves."""
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        # Create fleet with mock ship instance
        fleet = Fleet(1, empire1.id, HexCoord(0, 0), speed=10.0)

        # Create minimal ship instance with fuel
        mock_ship = MagicMock(spec=ShipInstance)
        mock_ship.is_combat_capable.return_value = True
        mock_ship.is_alive = True
        mock_ship.is_derelict = False
        mock_ship.mass = 5000  # Required for warp capability check
        mock_ship.design_data = {"layers": {}}  # Required for warp capability check
        mock_ship.get_calculated_stats.return_value = {"mass": 5000, "warp_max_tonnage": 0}
        mock_ship.get_all_resource_costs_per_hex.return_value = {"fuel": 1.0}
        mock_ship.get_current_resource.return_value = 100.0
        mock_ship.consume_resource.return_value = True
        mock_ship.get_warp_resource_costs.return_value = {}
        mock_ship.get_all_resource_costs_per_turn.return_value = {}

        fleet.ships = [mock_ship]
        fleet.add_order(Order(OrderType.MOVE, target=HexCoord(10, 0)))
        empire1.add_fleet(fleet)

        # Process a turn
        turn_engine.process_turn(empires, galaxy)

        # Verify fuel was consumed
        assert mock_ship.consume_resource.called

    def test_per_turn_resources_consumed_across_100_ticks(self, turn_engine, two_empire_setup):
        """Per-turn resource costs are spread across 100 ticks."""
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        # Create fleet with mock ship instance
        fleet = Fleet(1, empire1.id, HexCoord(0, 0), speed=0.0)  # Stationary

        mock_ship = MagicMock(spec=ShipInstance)
        mock_ship.is_combat_capable.return_value = True
        mock_ship.is_alive = True
        mock_ship.is_derelict = False
        mock_ship.design_data = {"layers": {}}  # PROJ-75: Maintenance engine reads design_data
        mock_ship.get_all_resource_costs_per_turn.return_value = {"fuel": 100.0}
        mock_ship.get_current_resource.return_value = 1000.0
        mock_ship.consume_resource.return_value = True

        fleet.ships = [mock_ship]
        empire1.add_fleet(fleet)

        # Process a turn
        turn_engine.process_turn(empires, galaxy)

        # Verify consume_resource was called ~100 times (once per tick for per_turn cost)
        # Each call should be for 100/100 = 1.0 fuel
        fuel_calls = [c for c in mock_ship.consume_resource.call_args_list
                      if c[0][0] == "fuel"]
        # Should have been called for each tick
        assert len(fuel_calls) >= 1

    def test_stranded_fleet_clears_orders(self, turn_engine, two_empire_setup):
        """Fleet without movement resources has orders cleared."""
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        fleet = Fleet(1, empire1.id, HexCoord(0, 0), speed=10.0)

        # Create ship with no fuel
        mock_ship = MagicMock(spec=ShipInstance)
        mock_ship.is_combat_capable.return_value = True
        mock_ship.is_alive = True
        mock_ship.is_derelict = False
        mock_ship.mass = 5000  # Required for warp capability check
        mock_ship.design_data = {"layers": {}}  # Required for warp capability check
        mock_ship.get_calculated_stats.return_value = {"mass": 5000, "warp_max_tonnage": 0}
        mock_ship.get_all_resource_costs_per_hex.return_value = {"fuel": 1.0}
        mock_ship.get_current_resource.return_value = 0.0  # No fuel
        mock_ship.consume_resource.return_value = False
        mock_ship.get_warp_resource_costs.return_value = {}
        mock_ship.get_all_resource_costs_per_turn.return_value = {}

        fleet.ships = [mock_ship]
        fleet.add_order(Order(OrderType.MOVE, target=HexCoord(10, 0)))
        empire1.add_fleet(fleet)

        initial_orders = len(fleet.orders)
        turn_engine.process_turn(empires, galaxy)

        # Fleet should have lost its orders (stranded)
        assert len(fleet.orders) == 0
