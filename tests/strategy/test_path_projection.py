import pytest
from game.strategy.data.hex_math import HexCoord, hex_distance
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.strategy.data.pathfinding import project_fleet_path

# Mocks
class MockSystem:
    def __init__(self, name, global_loc):
        self.name = name
        self.global_location = global_loc
        self.warp_points = []

class MockGalaxy:
    def __init__(self):
        self.systems = {}
    
    def get_system_by_name(self, name):
        # Scan values
        for s in self.systems.values():
            if s.name == name: return s
        return None

def test_project_simple_path():
    """Test projecting a simple move path within one system."""
    # Setup
    start = HexCoord(0, 0)
    # Fleet speed 2.0 -> 2 hexes per turn
    fleet = Fleet(1, 1, start, speed=2.0)
    
    # Create current path of 6 hexes (3 turns worth)
    # Path: (0,1), (0,2), (0,3), (0,4), (0,5), (0,6)
    fleet.path = [HexCoord(0, i) for i in range(1, 7)]
    
    galaxy = MockGalaxy()
    
    # Execute
    segments = project_fleet_path(fleet, galaxy)
    
    # Verify
    assert len(segments) == 6
    assert segments[0]['turn'] == 0
    assert segments[1]['turn'] == 0
    assert segments[2]['turn'] == 1
    assert segments[3]['turn'] == 1
    assert segments[4]['turn'] == 2
    assert segments[5]['turn'] == 2
    assert segments[0]['is_warp'] == False

def test_project_chained_orders():
    """Test projecting across multiple queued orders."""
    # Setup
    # Path 1 (Active): 1 hex remaining. Target (1,0).
    # Order 2 (Queued): Move to (4,0).
    # Fleet Speed 2.
    
    fleet = Fleet(1, 1, HexCoord(0,0), speed=2.0)
    
    # Active Order: Move to (1,0)
    fleet.add_order(FleetOrder(OrderType.MOVE, HexCoord(1,0)))
    fleet.path = [HexCoord(1,0)] # 1 hex left
    
    # Queued Order: Move to (4,0)
    # Path pathfinding: 2,0 -> 3,0 -> 4,0
    p2 = HexCoord(4,0)
    order = FleetOrder(OrderType.MOVE, p2)
    fleet.add_order(order)
    
    galaxy = MockGalaxy()
    
    # Execute
    segments = project_fleet_path(fleet, galaxy)
    
    # Total Path:
    # 1. (1,0) [Active] -> Turn 0 (Move 1/2) -> End of Order 1
    # 2. (2,0) [Queue] -> Turn 0 (Move 2/2)
    # 3. (3,0) [Queue] -> Turn 1 (Move 1/2)
    # 4. (4,0) [Queue] -> Turn 1 (Move 2/2) -> End of Order 2
    
    assert len(segments) == 4
    # Ensure continuity
    assert segments[0]['hex'] == HexCoord(1,0)
    assert segments[1]['hex'] == HexCoord(2,0)
    assert segments[2]['hex'] == HexCoord(3,0)
    assert segments[3]['hex'] == HexCoord(4,0)
    
    assert segments[0]['turn'] == 0
    assert segments[1]['turn'] == 0
    assert segments[2]['turn'] == 1
    assert segments[3]['turn'] == 1
