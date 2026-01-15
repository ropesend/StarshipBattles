import pytest
from unittest.mock import MagicMock, patch
from game.strategy.engine.game_session import GameSession
from game.strategy.engine.commands import IssueMoveCommand, IssueBuildShipCommand, CommandType
from game.strategy.data.fleet import Fleet, OrderType, FleetOrder
from game.strategy.data.hex_math import HexCoord
from game.strategy.data.empire import Empire

# Mock Galaxy and related classes to avoid full initialization
class MockGalaxy:
    def __init__(self):
        self.systems = {}
        self.warp_lanes = [] # minimal support
        self.planets_by_id = {}  # For ID-based lookups
        
    def get_planets_at_global_hex(self, global_hex):
        """Return planets at the given global hex (calculates from system data)."""
        result = []
        for sys in self.systems.values():
            for p in getattr(sys, 'planets', []):
                if hasattr(p, 'location') and (sys.global_location + p.location) == global_hex:
                    result.append(p)
        return result
    
    def get_planet_by_id(self, planet_id):
        """O(1) lookup of planet by ID."""
        return self.planets_by_id.get(planet_id)

def test_preview_fleet_path():
    """Test that preview_fleet_path returns a path without modifying state."""
    session = GameSession(system_count=0)
    session.galaxy = MockGalaxy() # Override with empty mock
    
    # Mock TurnEngine or internal pathfinder helper
    # We expect preview_fleet_path to call find_hybrid_path or similar
    with patch('game.strategy.data.pathfinding.find_hybrid_path') as mock_find:
        expected_path_full = [HexCoord(0,0), HexCoord(1,0), HexCoord(2,0)]
        mock_find.return_value = expected_path_full
        
        fleet = MagicMock()
        fleet.location = HexCoord(0,0)
        
        path = session.preview_fleet_path(fleet, HexCoord(2,0))
        
        # Expect start hex to be stripped
        assert path == [HexCoord(1,0), HexCoord(2,0)]
        mock_find.assert_called_once() 
        # Ensure fleet state not modified
        assert fleet.location == HexCoord(0,0)

def test_handle_move_command():
    """Test handling of IssueMoveCommand."""
    session = GameSession(system_count=0)
    
    # Setup Fleet
    fleet = Fleet(101, 0, HexCoord(0,0))
    session.player_empire.fleets = [fleet] # Inject fleet
    
    target_hex = HexCoord(5,5)
    cmd = IssueMoveCommand(fleet.id, target_hex)
    
    # Mock pathfinding to ensure validation passes (path exists)
    with patch('game.strategy.engine.game_session.GameSession.preview_fleet_path') as mock_preview:
        mock_preview.return_value = [HexCoord(0,0), HexCoord(5,5)] # Path found
        
        result = session.handle_command(cmd)
        
        assert result.is_valid == True
        assert len(fleet.orders) == 1
        assert fleet.orders[0].type == OrderType.MOVE
        assert fleet.orders[0].target == target_hex

def test_handle_move_command_invalid_fleet():
    """Test IssueMoveCommand with bad fleet ID."""
    session = GameSession(system_count=0)
    cmd = IssueMoveCommand(9999, HexCoord(0,0)) # ID not in empire
    
    result = session.handle_command(cmd)
    
    assert result.is_valid == False
    assert "Fleet not found" in result.message

def test_handle_build_ship_command():
    """Test IssueBuildShipCommand adds to queue."""
    session = GameSession(system_count=0)
    
    # Setup Planet with proper ID (not Python id())
    planet = MagicMock()
    planet.id = 42  # Proper entity ID
    planet.owner_id = session.player_empire.id
    planet.construction_queue = []
    
    # Mock galaxy's entity registry lookup
    session.galaxy = MockGalaxy()
    session.galaxy.get_planet_by_id = MagicMock(return_value=planet)
    
    cmd = IssueBuildShipCommand(planet.id, "Colony Ship")
    
    result = session.handle_command(cmd)
    
    assert result.is_valid == True
    # Verify planet lookup used proper ID
    session.galaxy.get_planet_by_id.assert_called_with(42)
    # Depending on implementation (calling add_production vs direct append)
    # The current code uses planet.add_production("Colony Ship", 1).
    assert planet.add_production.called or len(planet.construction_queue) > 0

