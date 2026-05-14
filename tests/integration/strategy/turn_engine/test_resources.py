"""Turn engine resource tests - per-turn consumption, depletion, movement gating."""
import pytest
from game.strategy.engine.turn_engine import TurnEngine
from tests.fixtures.turn_engine import build_test_turn_engine
from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.core.hex_math import HexCoord
from unittest.mock import MagicMock, patch

from .conftest import MockGalaxy, create_mock_ship_instance


class TestPerTurnResourceConsumption:
    """Group 5.1: Per-Turn Resource Consumption Tests"""

    def test_per_turn_resource_consumption_single_ship(self, fresh_registries):
        """Verify per-turn consumption is spread over 100 ticks (amount/100 per tick)."""
        engine = build_test_turn_engine(fresh_registries)

        # Create ship with mocked per-turn cost
        ship = create_mock_ship_instance(
            consumable_levels={'energy': 100.0}
        )
        # Mock get_all_resource_costs_per_turn to return energy cost of 50 per turn
        ship.get_all_resource_costs_per_turn = MagicMock(return_value={'energy': 50.0})
        ship.get_resource_capacity = MagicMock(return_value=100.0)
        ship.is_combat_capable = MagicMock(return_value=True)

        # Track consume_resource calls
        consumed_amounts = []
        def mock_consume(resource_type, amount):
            consumed_amounts.append((resource_type, amount))
            return True
        ship.consume_resource = mock_consume

        fleet = Fleet(1, 0, HexCoord(0, 0))
        fleet.ships = [ship]
        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_fleet(fleet)

        # Process single tick
        engine.resource_engine.process_per_turn_consumption(1, [empire])

        # Should consume 1/100th of the per-turn cost
        assert len(consumed_amounts) == 1
        assert consumed_amounts[0] == ('energy', 0.5)  # 50 / 100 = 0.5

    def test_per_turn_resource_consumption_multiple_resources(self, fresh_registries):
        """Verify multiple resource types are consumed per tick."""
        engine = build_test_turn_engine(fresh_registries)

        ship = create_mock_ship_instance(
            consumable_levels={'energy': 100.0, 'fuel': 200.0}
        )
        # Multiple resources with per-turn costs
        ship.get_all_resource_costs_per_turn = MagicMock(return_value={
            'energy': 30.0,
            'fuel': 10.0
        })
        ship.is_combat_capable = MagicMock(return_value=True)

        consumed = {}
        def mock_consume(resource_type, amount):
            consumed[resource_type] = consumed.get(resource_type, 0) + amount
            return True
        ship.consume_resource = mock_consume

        fleet = Fleet(1, 0, HexCoord(0, 0))
        fleet.ships = [ship]
        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_fleet(fleet)

        engine.resource_engine.process_per_turn_consumption(1, [empire])

        assert consumed['energy'] == pytest.approx(0.3, rel=1e-6)  # 30/100
        assert consumed['fuel'] == pytest.approx(0.1, rel=1e-6)    # 10/100

    def test_per_turn_resource_consumption_multiple_ships_in_fleet(self, fresh_registries):
        """Verify all ships in a fleet consume resources per tick."""
        engine = build_test_turn_engine(fresh_registries)

        ships = []
        for i in range(3):
            ship = create_mock_ship_instance(name=f"Ship{i}")
            ship.get_all_resource_costs_per_turn = MagicMock(return_value={'energy': 20.0})
            ship.is_combat_capable = MagicMock(return_value=True)
            ship.consume_resource = MagicMock(return_value=True)
            ships.append(ship)

        fleet = Fleet(1, 0, HexCoord(0, 0))
        fleet.ships = ships
        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_fleet(fleet)

        engine.resource_engine.process_per_turn_consumption(1, [empire])

        # Each ship should have consumed
        for ship in ships:
            ship.consume_resource.assert_called_once_with('energy', 0.2)  # 20/100

    def test_per_turn_consumption_non_combat_ships_skipped(self, fresh_registries):
        """Verify destroyed/derelict ships don't consume per-turn resources."""
        engine = build_test_turn_engine(fresh_registries)

        combat_ship = create_mock_ship_instance(name="CombatShip")
        combat_ship.is_combat_capable = MagicMock(return_value=True)
        combat_ship.get_all_resource_costs_per_turn = MagicMock(return_value={'energy': 10.0})
        combat_ship.consume_resource = MagicMock(return_value=True)

        destroyed_ship = create_mock_ship_instance(name="DestroyedShip", is_alive=False)
        destroyed_ship.is_combat_capable = MagicMock(return_value=False)
        destroyed_ship.get_all_resource_costs_per_turn = MagicMock(return_value={'energy': 10.0})
        destroyed_ship.consume_resource = MagicMock(return_value=True)

        derelict_ship = create_mock_ship_instance(name="DerelictShip", is_derelict=True)
        derelict_ship.is_combat_capable = MagicMock(return_value=False)
        derelict_ship.get_all_resource_costs_per_turn = MagicMock(return_value={'energy': 10.0})
        derelict_ship.consume_resource = MagicMock(return_value=True)

        fleet = Fleet(1, 0, HexCoord(0, 0))
        fleet.ships = [combat_ship, destroyed_ship, derelict_ship]
        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_fleet(fleet)

        engine.resource_engine.process_per_turn_consumption(1, [empire])

        # Only combat-capable ship should consume
        combat_ship.consume_resource.assert_called_once()
        destroyed_ship.consume_resource.assert_not_called()
        derelict_ship.consume_resource.assert_not_called()

    def test_per_turn_consumption_zero_cost_components_ignored(self, fresh_registries):
        """Verify components with zero per-turn cost don't attempt consumption."""
        engine = build_test_turn_engine(fresh_registries)

        ship = create_mock_ship_instance()
        # Return zero costs
        ship.get_all_resource_costs_per_turn = MagicMock(return_value={'energy': 0.0})
        ship.is_combat_capable = MagicMock(return_value=True)
        ship.consume_resource = MagicMock(return_value=True)

        fleet = Fleet(1, 0, HexCoord(0, 0))
        fleet.ships = [ship]
        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_fleet(fleet)

        engine.resource_engine.process_per_turn_consumption(1, [empire])

        # Zero cost should not trigger consumption
        ship.consume_resource.assert_not_called()


class TestResourceDepletion:
    """Group 5.2: Resource Depletion Tests"""

    def test_resource_depletion_during_tick_returns_false(self, fresh_registries):
        """Verify consume_resource returns False when resources depleted."""
        engine = build_test_turn_engine(fresh_registries)

        ship = create_mock_ship_instance()
        ship.get_all_resource_costs_per_turn = MagicMock(return_value={'energy': 100.0})
        ship.is_combat_capable = MagicMock(return_value=True)
        # Simulate depletion - consume returns False
        ship.consume_resource = MagicMock(return_value=False)

        fleet = Fleet(1, 0, HexCoord(0, 0))
        fleet.ships = [ship]
        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_fleet(fleet)

        # Patch _auto_disable_components_for_resource to verify it's called
        with patch.object(engine.resource_engine, '_auto_disable_components_for_resource') as mock_auto:
            engine.resource_engine.process_per_turn_consumption(1, [empire])
            mock_auto.assert_called_once_with(ship, 'energy')

    def test_resource_depletion_triggers_auto_disable(self, fresh_registries):
        """Verify auto-disable is triggered when resource depleted mid-tick."""
        engine = build_test_turn_engine(fresh_registries)

        ship = create_mock_ship_instance()
        ship.get_all_resource_costs_per_turn = MagicMock(return_value={'fuel': 50.0})
        ship.is_combat_capable = MagicMock(return_value=True)
        ship.consume_resource = MagicMock(return_value=False)  # Depleted

        fleet = Fleet(1, 0, HexCoord(0, 0))
        fleet.ships = [ship]
        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_fleet(fleet)

        with patch.object(engine.resource_engine, '_auto_disable_components_for_resource') as mock_auto:
            engine.resource_engine.process_per_turn_consumption(50, [empire])
            mock_auto.assert_called_once_with(ship, 'fuel')

    def test_no_auto_disable_for_non_per_turn_resources(self, fresh_registries):
        """Verify auto-disable only triggered for per_turn consumption failures."""
        engine = build_test_turn_engine(fresh_registries)

        ship = create_mock_ship_instance()
        # No per-turn costs
        ship.get_all_resource_costs_per_turn = MagicMock(return_value={})
        ship.is_combat_capable = MagicMock(return_value=True)
        ship.consume_resource = MagicMock(return_value=True)

        fleet = Fleet(1, 0, HexCoord(0, 0))
        fleet.ships = [ship]
        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_fleet(fleet)

        with patch.object(engine.resource_engine, '_auto_disable_components_for_resource') as mock_auto:
            engine.resource_engine.process_per_turn_consumption(1, [empire])
            mock_auto.assert_not_called()


class TestFullTurnIntegration:
    """Group 5.4: Full Turn Integration Tests"""

    @staticmethod
    def _build_per_turn_scenario(fresh_registries, costs, consume_fn):
        """Set up engine + single-ship empire with given per-turn costs and consume callback.

        PROJ-323 Task 3.7: shared setup helper for full-turn integration tests.
        """
        engine = build_test_turn_engine(fresh_registries)
        ship = create_mock_ship_instance()
        ship.get_all_resource_costs_per_turn = MagicMock(return_value=costs)
        ship.is_combat_capable = MagicMock(return_value=True)
        ship.consume_resource = consume_fn

        fleet = Fleet(1, 0, HexCoord(0, 0), speed=0)  # No movement
        fleet.ships = [ship]
        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_fleet(fleet)
        return engine, empire

    def test_full_turn_depletes_per_turn_resources_completely(self, fresh_registries):
        """Verify a full turn (100 ticks) consumes the entire per-turn cost."""
        # Track total consumption
        total_consumed = {'energy': 0.0}
        def mock_consume(resource_type, amount):
            total_consumed[resource_type] = total_consumed.get(resource_type, 0) + amount
            return True

        engine, empire = self._build_per_turn_scenario(
            fresh_registries, {'energy': 50.0}, mock_consume,
        )

        # Process all 100 ticks
        for tick in range(1, 101):
            engine.resource_engine.process_per_turn_consumption(tick, [empire])

        # Should have consumed exactly 50 energy total
        assert total_consumed['energy'] == pytest.approx(50.0, rel=1e-6)

    def test_full_turn_does_not_overconsume_resources(self, fresh_registries):
        """Verify full turn consumes exactly the per-turn amount, not more."""
        consume_calls = []
        def mock_consume(resource_type, amount):
            consume_calls.append(amount)
            return True

        engine, empire = self._build_per_turn_scenario(
            fresh_registries, {'fuel': 25.0}, mock_consume,
        )

        for tick in range(1, 101):
            engine.resource_engine.process_per_turn_consumption(tick, [empire])

        # Each tick should consume 0.25 (25/100)
        assert len(consume_calls) == 100
        for call in consume_calls:
            assert call == pytest.approx(0.25, rel=1e-6)
        assert sum(consume_calls) == pytest.approx(25.0, rel=1e-6)

    @patch('game.strategy.services.galaxy_pathfinding_service.GalaxyPathfindingService.find_hybrid_path')
    def test_per_turn_and_movement_resources_both_consumed(self, mock_path, fresh_registries):
        """Verify both per-turn and movement resources are consumed during a turn."""
        engine = build_test_turn_engine(fresh_registries)

        # PROJ-211: Pass registries for DI compliance (fleet adds ship triggering speed calc)
        ship = create_mock_ship_instance(registries=fresh_registries)
        ship.is_combat_capable = MagicMock(return_value=True)

        # Per-turn: 10 energy
        ship.get_all_resource_costs_per_turn = MagicMock(return_value={'energy': 10.0})

        per_turn_consumed = {'energy': 0.0}
        def mock_consume(resource_type, amount):
            per_turn_consumed[resource_type] = per_turn_consumed.get(resource_type, 0) + amount
            return True
        ship.consume_resource = mock_consume

        # Create fleet with movement
        fleet = Fleet(1, 0, HexCoord(0, 0), speed=5.0)
        fleet.ships = [ship]
        fleet.path = [HexCoord(1, 0), HexCoord(2, 0), HexCoord(3, 0), HexCoord(4, 0), HexCoord(5, 0)]
        fleet.add_order(Order(OrderType.MOVE, HexCoord(5, 0)))

        # Mock movement resources
        fleet.resources.has_resources_for_movement = MagicMock(return_value=True)
        fleet.resources.consume_movement_resources = MagicMock(return_value=True)

        mock_path.return_value = None

        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_fleet(fleet)

        engine.process_turn([empire], MockGalaxy())

        # Per-turn consumption should have occurred (100 ticks x 0.1 = 10)
        assert per_turn_consumed['energy'] == pytest.approx(10.0, rel=1e-6)
        # Movement should have been consumed (speed 5 = 5 hexes moved)
        assert fleet.resources.consume_movement_resources.call_count == 5


class TestMovementGating:
    """Group 5.5: Movement Gating Tests"""

    @patch('game.strategy.services.galaxy_pathfinding_service.GalaxyPathfindingService.find_hybrid_path')
    def test_movement_requires_generic_resources(self, mock_path, fresh_registries):
        """Verify movement is blocked when has_resources_for_movement returns False."""
        engine = build_test_turn_engine(fresh_registries)

        fleet = Fleet(1, 0, HexCoord(0, 0), speed=5.0)
        fleet.path = [HexCoord(1, 0)]
        fleet.add_order(Order(OrderType.MOVE, HexCoord(1, 0)))

        # No resources for movement
        fleet.resources.has_resources_for_movement = MagicMock(return_value=False)
        fleet.resources.consume_movement_resources = MagicMock()

        mock_path.return_value = None

        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_fleet(fleet)

        # Process tick 20 (when speed-5 fleet would move)
        engine._process_tick(20, [empire], MockGalaxy())

        # Movement should not have happened
        assert fleet.location == HexCoord(0, 0)
        fleet.resources.consume_movement_resources.assert_not_called()
        # Orders should be cleared (stranded)
        assert len(fleet.orders) == 0

    @patch('game.strategy.services.galaxy_pathfinding_service.GalaxyPathfindingService.find_hybrid_path')
    def test_generic_movement_resource_consumption(self, mock_path, fresh_registries):
        """Verify consume_movement_resources is called for each hex moved."""
        engine = build_test_turn_engine(fresh_registries)

        fleet = Fleet(1, 0, HexCoord(0, 0), speed=10.0)
        fleet.path = [HexCoord(i, 0) for i in range(1, 11)]
        fleet.add_order(Order(OrderType.MOVE, HexCoord(10, 0)))

        fleet.resources.has_resources_for_movement = MagicMock(return_value=True)
        fleet.resources.consume_movement_resources = MagicMock(return_value=True)

        mock_path.return_value = None

        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_fleet(fleet)

        engine.process_turn([empire], MockGalaxy())

        # Speed 10 = 10 moves per turn, each consuming resources
        assert fleet.resources.consume_movement_resources.call_count == 10
        # Each call should be for 1 hex
        for call in fleet.resources.consume_movement_resources.call_args_list:
            assert call[0] == (1,)

    @patch('game.strategy.services.galaxy_pathfinding_service.GalaxyPathfindingService.find_hybrid_path')
    def test_warp_uses_generic_methods(self, mock_path, fresh_registries):
        """Verify warp uses has_resources_for_warp and consume_warp_resources."""
        engine = build_test_turn_engine(fresh_registries)

        fleet = Fleet(1, 0, HexCoord(0, 0), speed=5.0)
        # Warp jump = distance > 1 hex
        fleet.path = [HexCoord(10, 0)]  # Far destination = warp
        fleet.add_order(Order(OrderType.MOVE, HexCoord(10, 0)))

        fleet.resources.has_resources_for_movement = MagicMock(return_value=True)
        fleet.capabilities.can_use_warp = MagicMock(return_value=True)
        fleet.resources.has_resources_for_warp = MagicMock(return_value=True)
        fleet.resources.consume_movement_resources = MagicMock(return_value=True)
        fleet.resources.consume_warp_resources = MagicMock(return_value=True)

        mock_path.return_value = None

        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_fleet(fleet)

        # Process tick 20 (when speed-5 fleet would move)
        engine._process_tick(20, [empire], MockGalaxy())

        # Warp check and consumption should have been called
        fleet.resources.has_resources_for_warp.assert_called_once()
        fleet.resources.consume_warp_resources.assert_called_once()
