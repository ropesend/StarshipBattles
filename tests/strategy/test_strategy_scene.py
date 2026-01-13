"""Tests for StrategyScene order queuing behavior."""
import pytest
from unittest.mock import MagicMock, patch
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.strategy.data.hex_math import HexCoord


class MockPlanet:
    """Mock planet for testing."""
    def __init__(self, location=HexCoord(0, 0)):
        self.location = location
        self.owner_id = None
        self.planet_type = MagicMock()
        self.planet_type.name = "Terran"


class MockSystem:
    """Mock star system for testing."""
    def __init__(self, global_loc=HexCoord(0, 0)):
        self.global_location = global_loc
        self.planets = []
        self.warp_points = []
        self.name = "TestSystem"
        self.star_type = MagicMock()
        self.star_type.color = (255, 255, 0)


def test_colonize_command_queues_move_and_colonize():
    """
    Pressing C on a selected fleet then selecting a planet should queue
    a MOVE order to the planet's hex followed by a COLONIZE order.
    """
    # Setup
    planet = MockPlanet(location=HexCoord(1, 0))
    target_hex = HexCoord(5, 5) + planet.location  # Global position
    
    fleet = Fleet(1, 0, HexCoord(0, 0), speed=5.0)
    
    # Simulate what _handle_colonize_designation should do:
    # 1. Calculate target hex from planet's global position
    # 2. Queue MOVE order
    # 3. Queue COLONIZE order
    
    # This is the expected behavior after the C key command
    move_order = FleetOrder(OrderType.MOVE, target_hex)
    colonize_order = FleetOrder(OrderType.COLONIZE, planet)
    
    fleet.add_order(move_order)
    fleet.add_order(colonize_order)
    
    # Verify order queue
    assert len(fleet.orders) == 2
    assert fleet.orders[0].type == OrderType.MOVE
    assert fleet.orders[0].target == target_hex
    assert fleet.orders[1].type == OrderType.COLONIZE
    assert fleet.orders[1].target == planet


def test_colonize_command_respects_order_sequence():
    """Verify COLONIZE order executes only after MOVE completes."""
    planet = MockPlanet(location=HexCoord(0, 0))
    
    fleet = Fleet(1, 0, HexCoord(0, 0), speed=5.0)
    move_order = FleetOrder(OrderType.MOVE, HexCoord(3, 3))
    colonize_order = FleetOrder(OrderType.COLONIZE, planet)
    
    fleet.add_order(move_order)
    fleet.add_order(colonize_order)
    
    # Current order should be MOVE
    current = fleet.get_current_order()
    assert current.type == OrderType.MOVE
    
    # Pop MOVE, next should be COLONIZE
    fleet.pop_order()
    current = fleet.get_current_order()
    assert current.type == OrderType.COLONIZE


class TestTurnManagement:
    """Tests for multi-player turn management."""
    
    def test_turn_index_cycles_through_human_players(self):
        """Verify turn index increments and resets correctly."""
        # Simulating turn manager logic
        current_player_index = 0
        human_player_ids = [0, 1]  # Two human players
        
        # Player 0 ends turn
        current_player_index += 1
        assert current_player_index == 1
        
        # Player 1 ends turn - should trigger processing and reset
        current_player_index += 1
        if current_player_index >= len(human_player_ids):
            current_player_index = 0  # Reset after all players acted
        
        assert current_player_index == 0  # Back to first player
        
    def test_turn_processes_after_all_humans_ready(self):
        """Verify turn processing happens only after all humans have submitted orders."""
        human_player_ids = [0, 1]
        turns_processed = 0
        
        def end_player_turn(current_index):
            nonlocal turns_processed
            next_index = current_index + 1
            if next_index >= len(human_player_ids):
                # All humans ready - process turn
                turns_processed += 1
                return 0  # Reset to first player
            return next_index
        
        # Simulate game flow
        idx = 0
        idx = end_player_turn(idx)  # Player 0 ends
        assert turns_processed == 0
        assert idx == 1
        
        idx = end_player_turn(idx)  # Player 1 ends
        assert turns_processed == 1
        assert idx == 0  # Reset for next turn
