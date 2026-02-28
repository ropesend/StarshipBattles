"""
Tests for advanced fleet order operations.

PROJ-187: Updated join fleet tests to use FleetOrderProcessor directly
instead of TurnEngine._process_end_turn_orders (which was removed when
action orders moved to tick-based processing).
"""
import pytest
from unittest.mock import MagicMock, patch
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import FleetOrder, OrderType
from game.core.hex_math import HexCoord
from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.engine.fleet_order_processor import FleetOrderProcessor
from game.strategy.data.empire import Empire
from game.strategy.data.ship_instance import ShipInstance


def make_mock_ship_instance(name="Test Ship", owner_id=0):
    """Create a mock ShipInstance for testing."""
    return ShipInstance(
        instance_id=f"test-{name.lower().replace(' ', '-')}-{id(name)}",
        design_id=name,
        name=name,
        owner_id=owner_id,
        design_data={
            'name': name,
            'vehicle_type': 'Ship',
            'stats': {'mass': 100}
        },
    )


@pytest.fixture
def turn_engine():
    """Create a fresh TurnEngine for each test."""
    engine = TurnEngine()
    yield engine


@pytest.fixture
def order_processor():
    """Create a fresh FleetOrderProcessor for each test."""
    processor = FleetOrderProcessor()
    yield processor


@pytest.fixture
def test_empire():
    """Create a test empire with proper cleanup."""
    empire = Empire(0, "Test Empire", (255, 0, 0))
    yield empire
    empire.fleets.clear()


@pytest.fixture
def galaxy_mock():
    """Create mock galaxy."""
    galaxy = MagicMock()
    galaxy.systems = {}
    return galaxy


class TestAdvancedFleetOrders:
    def test_fleet_merge_method(self, turn_engine, test_empire, galaxy_mock):
        """Test the basic merge_with data operation."""
        f1 = Fleet(1, 0, HexCoord(0, 0), speed=10.0)
        f2 = Fleet(2, 0, HexCoord(10, 0), speed=10.0)

        test_empire.add_fleet(f1)
        test_empire.add_fleet(f2)

        ship_a = make_mock_ship_instance("ShipA", 0)
        ship_b = make_mock_ship_instance("ShipB", 0)
        f1.ships = [ship_a]
        f2.ships = [ship_b]
        f1.orders = ["SomeOrder"]

        f1.merge_with(f2)

        # F2 should have both
        assert ship_a in f2.ships
        assert ship_b in f2.ships

        # F1 should be empty
        assert len(f1.ships) == 0
        assert len(f1.orders) == 0

    @patch('game.strategy.data.pathfinding.project_fleet_path')
    @patch('game.strategy.data.pathfinding.find_hybrid_path')
    def test_move_to_fleet_logic(self, mock_find_path, mock_project_path, turn_engine, test_empire, galaxy_mock):
        """Verify predictive pathing updates."""
        f1 = Fleet(1, 0, HexCoord(0, 0), speed=10.0)
        f2 = Fleet(2, 0, HexCoord(10, 0), speed=10.0)

        test_empire.add_fleet(f1)
        test_empire.add_fleet(f2)

        # Setup Order
        order = FleetOrder(OrderType.MOVE_TO_FLEET, f2)
        f1.add_order(order)

        # Scenario: F2 is moving.
        # T=0 (now): F2 @ (10, 0)
        # T=1: F2 @ (11, 0)
        # T=2: F2 @ (12, 0)
        # F1 Speed 10. Distance to (10,0) is 10.

        # Mock Projection: Returns future path of F2
        mock_project_path.return_value = [
            {'hex': HexCoord(11, 0), 'turn': 1},
            {'hex': HexCoord(12, 0), 'turn': 2}
        ]

        # Mock Pathfinding
        # calculate_intercept_point should call project_fleet_path.
        # It sees:
        # T=0, Target=(10,0), D=10. F1 T_reach = 10/10 = 1.0. T_target=0. FAIL.
        # T=1, Target=(11,0), D=11. F1 T_reach = 1.1. T_target=1. FAIL? (1.1 > 1)
        # Wait, if F1 moves 10/turn.
        # Dist(0,0 -> 11,0) = 11. Time = 1.1 turns.
        # But Turn 1 happens in 1 turn.
        # So F1 reaches (11,0) at T=1.1. Target is there at T=1.
        # Game Turn Engine steps:
        # If I start now, at end of Turn 1 I am at (10,0). Target is at (11,0).
        # At end of Turn 2, I am at (20,0). Target is at (12,0).
        # Optimization should pick a point where I can reach it.
        # Let's say F2 slows down or loops.

        # Let's try Static Target first for simpler mock?
        # No, current test logic relies on 'calculate_intercept_point' importing 'project_fleet_path'.
        # Since we use real 'calculate_intercept_point', we need to mock what it calls.
        # But wait, 'from game.strategy.data.pathfinding import calculate_intercept_point' inside updated TurnEngine
        # might import the REAL function which calls REAL project_fleet_path.

        # We need to control the projection to test prediction.

        # Update Mock for calculate_intercept_point results directly?
        # That tests TurnEngine integration, not the Algo.
        # Let's mock find_hybrid_path only and assume calculation works,
        # OR mock calculate_intercept_point in TurnEngine to verify it's utilized.
        pass

    # PROJ-35: Patch paths updated - FleetMovementEngine now delegates to FleetNavigationService
    # calculate_intercept_point is imported locally in get_destination(), so patch at source
    # find_hybrid_path is imported at module level in FleetNavigationService
    @patch('game.strategy.data.pathfinding.calculate_intercept_point')
    @patch('game.strategy.services.fleet_navigation_service.find_hybrid_path')
    def test_intercept_integration(self, mock_find_path, mock_calc_intercept, turn_engine, test_empire, galaxy_mock):
        """Verify TurnEngine calls calculate_intercept_point."""
        f1 = Fleet(1, 0, HexCoord(0, 0), speed=10.0)
        f2 = Fleet(2, 0, HexCoord(10, 0), speed=10.0)

        test_empire.add_fleet(f1)
        test_empire.add_fleet(f2)

        # Setup Order
        order = FleetOrder(OrderType.MOVE_TO_FLEET, f2)
        f1.add_order(order)

        # Mock Intercept Result
        predicted_hex = HexCoord(15, 0)
        mock_calc_intercept.return_value = predicted_hex

        # Mock Pathfinding to that predicted hex
        mock_find_path.return_value = [HexCoord(1, 0)]

        # Execute: Calculate next hex and apply movement manually
        # PROJ-36: Use movement_engine directly instead of legacy wrapper
        next_hex = turn_engine.movement_engine.calculate_next_hex(f1, galaxy_mock)
        if next_hex:
            f1.location = next_hex
            if not f1.path:
                f1.pop_order()

        # Verify
        mock_calc_intercept.assert_called()
        mock_find_path.assert_called()
        assert f1.location == HexCoord(1, 0)

    @patch('game.strategy.data.pathfinding.find_hybrid_path')
    @patch('game.strategy.data.pathfinding.project_fleet_path')
    def test_calculate_intercept_algorithm(self, mock_project, mock_find_path, turn_engine, test_empire, galaxy_mock):
        """Test the math of calculate_intercept_point using real path lengths."""
        from game.strategy.data.pathfinding import calculate_intercept_point

        f1 = Fleet(1, 0, HexCoord(0, 0), speed=10.0)
        f2 = Fleet(2, 0, HexCoord(10, 0), speed=10.0)

        test_empire.add_fleet(f1)
        test_empire.add_fleet(f2)

        # Scenario: Target is moving away slower than Chaser.
        # Chaser @ 0,0. Speed 2.
        # Target @ 4,0. Speed 1. Moving to 10,0.

        f1.location = HexCoord(0, 0)
        f1.speed = 2.0

        f2.location = HexCoord(4, 0)
        f2.speed = 1.0

        # Mock Target Path
        mock_project.return_value = [
            {'hex': HexCoord(5, 0), 'turn': 1},
            {'hex': HexCoord(6, 0), 'turn': 2},
            {'hex': HexCoord(7, 0), 'turn': 3},
            {'hex': HexCoord(8, 0), 'turn': 4},
            {'hex': HexCoord(9, 0), 'turn': 5}
        ]

        # Mock find_hybrid_path to return paths of correct lengths
        # Path includes start hex, so path_length = dist + 1, steps = dist
        # Target occupies hex for entire turn, so chaser can intercept if: chaser_turns < target_turn + 1
        # Path to (4,0) = 4 steps. Time = 4/2 = 2 turns. Target at T=0. 2 < 1? FAIL.
        # Path to (5,0) = 5 steps. Time = 2.5 turns. Target at T=1. 2.5 < 2? FAIL.
        # Path to (6,0) = 6 steps. Time = 3.0 turns. Target at T=2. 3.0 < 3? FAIL.
        # Path to (7,0) = 7 steps. Time = 3.5 turns. Target at T=3. 3.5 < 4? SUCCESS!
        def path_mock(galaxy, start, end, fleet=None):
            # Return a list including start hex (like real pathfinding)
            dist = abs(end.q - start.q) + abs(end.r - start.r)  # Simplified hex dist
            return [HexCoord(i, 0) for i in range(dist + 1)]  # +1 to include start

        mock_find_path.side_effect = path_mock

        result = calculate_intercept_point(f1, f2, galaxy_mock)

        # Now correctly intercepts at (7,0) - 1 turn earlier than old buggy result!
        assert result == HexCoord(7, 0)

    def test_join_fleet_execution(self, order_processor, test_empire, galaxy_mock):
        """Verify JOIN_FLEET order merges fleets.

        PROJ-207 EP-001: JOIN_FLEET is now handled by process_instant_orders only,
        not by process_end_turn_orders. It fires instantly when co-located.
        """
        f1 = Fleet(1, 0, HexCoord(0, 0), speed=10.0)
        f2 = Fleet(2, 0, HexCoord(10, 0), speed=10.0)

        test_empire.add_fleet(f1)
        test_empire.add_fleet(f2)

        # Setup: Co-located
        f1.location = HexCoord(5, 5)
        f2.location = HexCoord(5, 5)
        ship_a = make_mock_ship_instance("ShipA", 0)
        ship_b = make_mock_ship_instance("ShipB", 0)
        f1.ships = [ship_a]
        f2.ships = [ship_b]

        order = FleetOrder(OrderType.JOIN_FLEET, f2)
        f1.add_order(order)

        # Execute via instant path (PROJ-207)
        removed = order_processor.process_instant_orders([test_empire])

        # Should have merged
        assert len(removed) == 1
        assert removed[0] == (test_empire, f1)

        # Verify F2 state
        assert len(f2.ships) == 2

        # Verify Empire state (removal happens after process_instant_orders)
        assert f1 not in test_empire.fleets

    def test_join_fleet_waits_when_not_colocated(self, order_processor, test_empire, galaxy_mock):
        """Verify JOIN_FLEET waits when fleets not co-located.

        PROJ-207 EP-001: JOIN_FLEET order stays queued when not at target's location.
        The preceding MOVE_TO_FLEET will bring the fleet to the target first.
        """
        f1 = Fleet(1, 0, HexCoord(0, 0), speed=10.0)
        f2 = Fleet(2, 0, HexCoord(10, 0), speed=10.0)

        test_empire.add_fleet(f1)
        test_empire.add_fleet(f2)

        f1.location = HexCoord(0, 0)
        f2.location = HexCoord(10, 0)  # Different location

        order = FleetOrder(OrderType.JOIN_FLEET, f2)
        f1.add_order(order)

        # Execute via instant path (PROJ-207)
        removed = order_processor.process_instant_orders([test_empire])

        # Should NOT merge - not co-located yet
        assert len(removed) == 0
        assert f1 in test_empire.fleets
        # Order should stay queued (waiting for fleet to arrive)
        assert f1.get_current_order() is not None
        assert f1.get_current_order().type == OrderType.JOIN_FLEET

    @patch('game.strategy.data.pathfinding.find_hybrid_path')
    @patch('game.strategy.data.pathfinding.project_fleet_path')
    def test_intercept_picks_earliest_chaser_arrival(self, mock_project, mock_find_path, turn_engine, test_empire, galaxy_mock):
        """
        Regression test: Algorithm must pick EARLIEST chaser arrival, not first valid point.

        Scenario: Target path goes through point A (turn 5) then B (turn 10).
        Chaser can reach A in 6 turns (invalid - too slow) and B in 4 turns (valid).
        The old buggy code would never find B since it returns on first valid.
        The fix should find B since 4 < 6.
        """
        from game.strategy.data.pathfinding import calculate_intercept_point

        f1 = Fleet(1, 0, HexCoord(0, 0), speed=10.0)
        f2 = Fleet(2, 0, HexCoord(10, 0), speed=10.0)

        test_empire.add_fleet(f1)
        test_empire.add_fleet(f2)

        # Chaser @ 0,0. Speed 5.
        f1.location = HexCoord(0, 0)
        f1.speed = 5.0

        # Target @ 10,0.
        f2.location = HexCoord(10, 0)

        # Mock Target Path: Goes far then loops back closer
        # Turn 5: at (30, 0) - far away
        # Turn 10: at (15, 0) - closer
        mock_project.return_value = [
            {'hex': HexCoord(30, 0), 'turn': 5},   # Chaser needs 30 steps = 6 turns. INVALID.
            {'hex': HexCoord(15, 0), 'turn': 10},  # Chaser needs 15 steps = 3 turns. VALID, arrives early!
        ]

        # Mock pathfinding to return paths of correct length (includes start hex)
        def path_mock(galaxy, start, end, fleet=None):
            dist = abs(end.q - start.q)  # Simple distance for 1D case
            return [HexCoord(i, 0) for i in range(dist + 1)]  # +1 to include start

        mock_find_path.side_effect = path_mock

        result = calculate_intercept_point(f1, f2, galaxy_mock)

        # Should pick (15, 0) at turn 10 - chaser arrives in 3 turns, much earlier!
        # NOT (10, 0) at turn 0 (unreachable) or (30, 0) at turn 5 (can't reach in time)
        assert result == HexCoord(15, 0)
