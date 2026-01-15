
import unittest
from unittest.mock import MagicMock, patch
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.strategy.data.hex_math import HexCoord
from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.data.empire import Empire

class TestAdvancedFleetOrders(unittest.TestCase):
    def setUp(self):
        self.engine = TurnEngine()
        self.galaxy = MagicMock()
        self.galaxy.systems = {}
        
        self.empire = Empire(0, "Test Empire", (255, 0, 0))
        
        self.f1 = Fleet(1, 0, HexCoord(0, 0), speed=10.0) # Fast fleet
        self.f2 = Fleet(2, 0, HexCoord(10, 0), speed=10.0)
        
        self.empire.add_fleet(self.f1)
        self.empire.add_fleet(self.f2)
        
    def test_fleet_merge_method(self):
        """Test the basic merge_with data operation."""
        self.f1.ships = ["ShipA"]
        self.f2.ships = ["ShipB"]
        self.f1.orders = ["SomeOrder"]
        
        self.f1.merge_with(self.f2)
        
        # F2 should have both
        self.assertIn("ShipA", self.f2.ships)
        self.assertIn("ShipB", self.f2.ships)
        
        # F1 should be empty
        self.assertEqual(len(self.f1.ships), 0)
        self.assertEqual(len(self.f1.orders), 0)

    @patch('game.strategy.data.pathfinding.project_fleet_path')
    @patch('game.strategy.data.pathfinding.find_hybrid_path')
    def test_move_to_fleet_logic(self, mock_find_path, mock_project_path):
        """Verify predictive pathing updates."""
        # Setup Order
        order = FleetOrder(OrderType.MOVE_TO_FLEET, self.f2)
        self.f1.add_order(order)
        
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

    @patch('game.strategy.data.pathfinding.calculate_intercept_point')
    @patch('game.strategy.data.pathfinding.find_hybrid_path')
    def test_intercept_integration(self, mock_find_path, mock_calc_intercept):
        """Verify TurnEngine calls calculate_intercept_point."""
        # Setup Order
        order = FleetOrder(OrderType.MOVE_TO_FLEET, self.f2)
        self.f1.add_order(order)
        
        # Mock Intercept Result
        predicted_hex = HexCoord(15, 0)
        mock_calc_intercept.return_value = predicted_hex
        
        # Mock Pathfinding to that predicted hex
        mock_find_path.return_value = [HexCoord(1, 0)]
        
        # Execute
        self.engine._execute_move_step(self.f1, self.galaxy)
        
        # Verify
        mock_calc_intercept.assert_called_with(self.f1, self.f2, self.galaxy)
        mock_find_path.assert_called_with(self.galaxy, HexCoord(0, 0), predicted_hex)
        self.assertEqual(self.f1.location, HexCoord(1, 0))

    @patch('game.strategy.data.pathfinding.find_hybrid_path')
    @patch('game.strategy.data.pathfinding.project_fleet_path')
    def test_calculate_intercept_algorithm(self, mock_project, mock_find_path):
        """Test the math of calculate_intercept_point using real path lengths."""
        from game.strategy.data.pathfinding import calculate_intercept_point
        
        # Scenario: Target is moving away slower than Chaser.
        # Chaser @ 0,0. Speed 2.
        # Target @ 4,0. Speed 1. Moving to 10,0.
        
        self.f1.location = HexCoord(0, 0)
        self.f1.speed = 2.0
        
        self.f2.location = HexCoord(4, 0)
        self.f2.speed = 1.0
        
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
        def path_mock(galaxy, start, end):
            # Return a list including start hex (like real pathfinding)
            dist = abs(end.q - start.q) + abs(end.r - start.r)  # Simplified hex dist
            return [HexCoord(i, 0) for i in range(dist + 1)]  # +1 to include start
        
        mock_find_path.side_effect = path_mock
        
        result = calculate_intercept_point(self.f1, self.f2, self.galaxy)
        
        # Now correctly intercepts at (7,0) - 1 turn earlier than old buggy result!
        self.assertEqual(result, HexCoord(7, 0))

    def test_join_fleet_execution(self):
        """Verify JOIN_FLEET order merges fleets."""
        # Setup: Co-located
        self.f1.location = HexCoord(5, 5)
        self.f2.location = HexCoord(5, 5)
        self.f1.ships = ["ShipA"]
        self.f2.ships = ["ShipB"]
        
        order = FleetOrder(OrderType.JOIN_FLEET, self.f2)
        self.f1.add_order(order)
        
        # Execute End Turn Orders
        # We need to pass [self.empire] usually, method is _process_end_turn_orders(fleet, empire, galaxy)
        result = self.engine._process_end_turn_orders(self.f1, self.empire, self.galaxy)
        
        self.assertTrue(result) # Should return True (fleet consumed)
        
        # Verify F2 state
        self.assertEqual(len(self.f2.ships), 2)
        
        # Verify Empire state
        self.assertNotIn(self.f1, self.empire.fleets)

    def test_join_fleet_fail_distance(self):
        """Verify JOIN_FLEET fails if not at location."""
        self.f1.location = HexCoord(0, 0)
        self.f2.location = HexCoord(10, 0)
        
        order = FleetOrder(OrderType.JOIN_FLEET, self.f2)
        self.f1.add_order(order)
        
        # Execute
        # Capturing print output is tricky, but we check state
        result = self.engine._process_end_turn_orders(self.f1, self.empire, self.galaxy)
        
        self.assertFalse(result) # Did not consume fleet
        self.assertIn(self.f1, self.empire.fleets)
        self.assertIsNone(self.f1.get_current_order()) # Should have popped failed order

    @patch('game.strategy.data.pathfinding.find_hybrid_path')
    @patch('game.strategy.data.pathfinding.project_fleet_path')
    def test_intercept_picks_earliest_chaser_arrival(self, mock_project, mock_find_path):
        """
        Regression test: Algorithm must pick EARLIEST chaser arrival, not first valid point.
        
        Scenario: Target path goes through point A (turn 5) then B (turn 10).
        Chaser can reach A in 6 turns (invalid - too slow) and B in 4 turns (valid).
        The old buggy code would never find B since it returns on first valid.
        The fix should find B since 4 < 6.
        """
        from game.strategy.data.pathfinding import calculate_intercept_point
        
        # Chaser @ 0,0. Speed 5.
        self.f1.location = HexCoord(0, 0)
        self.f1.speed = 5.0
        
        # Target @ 10,0.
        self.f2.location = HexCoord(10, 0)
        
        # Mock Target Path: Goes far then loops back closer
        # Turn 5: at (30, 0) - far away
        # Turn 10: at (15, 0) - closer 
        mock_project.return_value = [
            {'hex': HexCoord(30, 0), 'turn': 5},   # Chaser needs 30 steps = 6 turns. INVALID.
            {'hex': HexCoord(15, 0), 'turn': 10},  # Chaser needs 15 steps = 3 turns. VALID, arrives early!
        ]
        
        # Mock pathfinding to return paths of correct length (includes start hex)
        def path_mock(galaxy, start, end):
            dist = abs(end.q - start.q)  # Simple distance for 1D case
            return [HexCoord(i, 0) for i in range(dist + 1)]  # +1 to include start
        
        mock_find_path.side_effect = path_mock
        
        result = calculate_intercept_point(self.f1, self.f2, self.galaxy)
        
        # Should pick (15, 0) at turn 10 - chaser arrives in 3 turns, much earlier!
        # NOT (10, 0) at turn 0 (unreachable) or (30, 0) at turn 5 (can't reach in time)
        self.assertEqual(result, HexCoord(15, 0))

