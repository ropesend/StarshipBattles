import pytest
from unittest.mock import MagicMock, patch
from game.strategy.engine.game_session import GameSession
from game.strategy.engine.game_config import GameConfig
from game.strategy.engine.commands import IssueMoveCommand, IssueBuildShipCommand, CommandType
from game.strategy.data.fleet import Fleet, OrderType, FleetOrder
from game.core.hex_math import HexCoord
from game.strategy.data.empire import Empire

# Mock Galaxy and related classes to avoid full initialization
class MockGalaxy:
    def __init__(self):
        self.systems = {}
        self.warp_lanes = [] # minimal support
        self.planets_by_id = {}  # For ID-based lookups
        self.fleets_by_id = {}   # For fleet registry (PROJ-87)

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

    def get_fleet_by_id(self, fleet_id):
        """O(1) lookup of fleet by ID."""
        return self.fleets_by_id.get(fleet_id)

    def register_fleet(self, fleet):
        """Register a fleet for O(1) lookup."""
        self.fleets_by_id[fleet.id] = fleet

    def unregister_fleet(self, fleet):
        """Unregister a fleet."""
        self.fleets_by_id.pop(fleet.id, None)

def test_preview_fleet_path():
    """Test that preview_fleet_path returns a path without modifying state."""
    config = GameConfig(system_count=0)
    session = GameSession(config=config)
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
    config = GameConfig(system_count=0)
    session = GameSession(config=config)
    
    # Setup Fleet
    fleet = Fleet(101, 0, HexCoord(0,0))
    session.player_empire.fleets = [fleet] # Inject fleet
    
    target_hex = HexCoord(5,5)
    cmd = IssueMoveCommand(fleet.id, target_hex)
    
    # Mock pathfinding to ensure validation passes (path exists)
    with patch('game.strategy.engine.game_session.GameSession.preview_fleet_path') as mock_preview:
        mock_preview.return_value = [HexCoord(0,0), HexCoord(5,5)] # Path found
        
        result = session.handle_command(cmd)
        
        assert result.is_valid is True
        assert len(fleet.orders) == 1
        assert fleet.orders[0].type == OrderType.MOVE
        assert fleet.orders[0].target == target_hex

def test_handle_move_command_invalid_fleet():
    """Test IssueMoveCommand with bad fleet ID."""
    config = GameConfig(system_count=0)
    session = GameSession(config=config)
    cmd = IssueMoveCommand(9999, HexCoord(0,0)) # ID not in empire
    
    result = session.handle_command(cmd)
    
    assert result.is_valid is False
    assert "Fleet not found" in result.message

def test_handle_build_ship_command():
    """Test IssueBuildShipCommand adds to queue."""
    config = GameConfig(system_count=0)
    session = GameSession(config=config)
    
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
    
    assert result.is_valid is True
    # Verify planet lookup used proper ID
    session.galaxy.get_planet_by_id.assert_called_with(42)
    # Depending on implementation (calling add_production vs direct append)
    # The current code uses planet.add_production("Colony Ship", 1).
    assert planet.add_production.called or len(planet.construction_queue) > 0


# =============================================================================
# Intercept Command Handler Tests (Task 2.2)
# =============================================================================

class TestInterceptCommandHandler:
    """Tests for IssueInterceptCommand handling."""

    def test_intercept_command_success(self):
        """Intercept command creates MOVE_TO_FLEET order targeting the fleet."""
        from game.strategy.engine.commands import IssueInterceptCommand

        config = GameConfig(system_count=0)
        session = GameSession(config=config)
        session.galaxy = MockGalaxy()

        # Setup two fleets
        fleet = Fleet(101, 0, HexCoord(0, 0))
        target_fleet = Fleet(102, 0, HexCoord(10, 10))
        session.player_empire.fleets = [fleet, target_fleet]

        cmd = IssueInterceptCommand(fleet_id=101, target_fleet_id=102)
        result = session.handle_command(cmd)

        assert result.is_valid is True
        assert "Intercept" in result.message or "intercept" in result.message.lower()
        assert len(fleet.orders) == 1
        assert fleet.orders[0].type == OrderType.MOVE_TO_FLEET
        assert fleet.orders[0].target == target_fleet

    def test_intercept_command_invalid_fleet(self):
        """Intercept command fails if source fleet doesn't exist."""
        from game.strategy.engine.commands import IssueInterceptCommand

        config = GameConfig(system_count=0)
        session = GameSession(config=config)
        session.galaxy = MockGalaxy()

        target_fleet = Fleet(102, 0, HexCoord(10, 10))
        session.player_empire.fleets = [target_fleet]

        cmd = IssueInterceptCommand(fleet_id=9999, target_fleet_id=102)
        result = session.handle_command(cmd)

        assert result.is_valid is False
        assert "Fleet not found" in result.message or "not found" in result.message.lower()

    def test_intercept_command_invalid_target(self):
        """Intercept command fails if target fleet doesn't exist."""
        from game.strategy.engine.commands import IssueInterceptCommand

        config = GameConfig(system_count=0)
        session = GameSession(config=config)
        session.galaxy = MockGalaxy()

        fleet = Fleet(101, 0, HexCoord(0, 0))
        session.player_empire.fleets = [fleet]

        cmd = IssueInterceptCommand(fleet_id=101, target_fleet_id=9999)
        result = session.handle_command(cmd)

        assert result.is_valid is False
        assert "Target fleet" in result.message or "target" in result.message.lower()


# =============================================================================
# Join Fleet Command Handler Tests (Task 2.3)
# =============================================================================

class TestJoinFleetCommandHandler:
    """Tests for IssueJoinFleetCommand handling."""

    def test_join_fleet_command_success(self):
        """Join fleet command creates MOVE_TO_FLEET and JOIN_FLEET orders."""
        from game.strategy.engine.commands import IssueJoinFleetCommand

        config = GameConfig(system_count=0)
        session = GameSession(config=config)
        session.galaxy = MockGalaxy()

        # Setup two fleets
        fleet = Fleet(101, 0, HexCoord(0, 0))
        target_fleet = Fleet(102, 0, HexCoord(10, 10))
        session.player_empire.fleets = [fleet, target_fleet]

        cmd = IssueJoinFleetCommand(fleet_id=101, target_fleet_id=102)
        result = session.handle_command(cmd)

        assert result.is_valid is True
        # Should have 2 orders: MOVE_TO_FLEET then JOIN_FLEET
        assert len(fleet.orders) == 2
        assert fleet.orders[0].type == OrderType.MOVE_TO_FLEET
        assert fleet.orders[0].target == target_fleet
        assert fleet.orders[1].type == OrderType.JOIN_FLEET
        assert fleet.orders[1].target == target_fleet

    def test_join_fleet_command_invalid_fleet(self):
        """Join fleet command fails if source fleet doesn't exist."""
        from game.strategy.engine.commands import IssueJoinFleetCommand

        config = GameConfig(system_count=0)
        session = GameSession(config=config)
        session.galaxy = MockGalaxy()

        target_fleet = Fleet(102, 0, HexCoord(10, 10))
        session.player_empire.fleets = [target_fleet]

        cmd = IssueJoinFleetCommand(fleet_id=9999, target_fleet_id=102)
        result = session.handle_command(cmd)

        assert result.is_valid is False
        assert "Fleet not found" in result.message or "not found" in result.message.lower()

    def test_join_fleet_command_invalid_target(self):
        """Join fleet command fails if target fleet doesn't exist."""
        from game.strategy.engine.commands import IssueJoinFleetCommand

        config = GameConfig(system_count=0)
        session = GameSession(config=config)
        session.galaxy = MockGalaxy()

        fleet = Fleet(101, 0, HexCoord(0, 0))
        session.player_empire.fleets = [fleet]

        cmd = IssueJoinFleetCommand(fleet_id=101, target_fleet_id=9999)
        result = session.handle_command(cmd)

        assert result.is_valid is False
        assert "Target fleet" in result.message or "target" in result.message.lower()


# =============================================================================
# Colonize Mission Command Handler Tests (Task 2.4)
# =============================================================================

class TestColonizeMissionCommandHandler:
    """Tests for QueueColonizeMissionCommand handling."""

    def test_colonize_mission_success(self):
        """Colonize mission queues MOVE and COLONIZE orders with path."""
        from game.strategy.engine.commands import QueueColonizeMissionCommand

        config = GameConfig(system_count=0)
        session = GameSession(config=config)
        session.galaxy = MockGalaxy()

        # Setup fleet and mock planet
        fleet = Fleet(101, 0, HexCoord(0, 0))
        session.player_empire.fleets = [fleet]

        planet = MagicMock()
        planet.id = 42
        planet.name = "Test Planet"
        session.galaxy.planets_by_id[42] = planet

        target_hex = HexCoord(10, 10)
        cmd = QueueColonizeMissionCommand(fleet_id=101, target_hex=target_hex, planet_id=42)

        # Mock pathfinding
        with patch('game.strategy.data.pathfinding.find_hybrid_path') as mock_path:
            mock_path.return_value = [HexCoord(0, 0), HexCoord(5, 5), HexCoord(10, 10)]

            result = session.handle_command(cmd)

            assert result.is_valid is True
            assert len(fleet.orders) == 2
            # First order should be MOVE
            assert fleet.orders[0].type == OrderType.MOVE
            assert fleet.orders[0].target == target_hex
            # Second order should be COLONIZE
            assert fleet.orders[1].type == OrderType.COLONIZE
            assert fleet.orders[1].target == planet

    def test_colonize_mission_no_path(self):
        """Colonize mission fails if no path to target."""
        from game.strategy.engine.commands import QueueColonizeMissionCommand

        config = GameConfig(system_count=0)
        session = GameSession(config=config)
        session.galaxy = MockGalaxy()

        fleet = Fleet(101, 0, HexCoord(0, 0))
        session.player_empire.fleets = [fleet]

        planet = MagicMock()
        planet.id = 42
        session.galaxy.planets_by_id[42] = planet

        cmd = QueueColonizeMissionCommand(fleet_id=101, target_hex=HexCoord(100, 100), planet_id=42)

        # Mock pathfinding to return None (no path)
        with patch('game.strategy.data.pathfinding.find_hybrid_path') as mock_path:
            mock_path.return_value = None

            result = session.handle_command(cmd)

            assert result.is_valid is False
            assert "path" in result.message.lower() or "unreachable" in result.message.lower()

    def test_colonize_mission_invalid_fleet(self):
        """Colonize mission fails if fleet doesn't exist."""
        from game.strategy.engine.commands import QueueColonizeMissionCommand

        config = GameConfig(system_count=0)
        session = GameSession(config=config)
        session.galaxy = MockGalaxy()

        cmd = QueueColonizeMissionCommand(fleet_id=9999, target_hex=HexCoord(10, 10), planet_id=42)
        result = session.handle_command(cmd)

        assert result.is_valid is False
        assert "Fleet not found" in result.message

    def test_colonize_mission_invalid_planet(self):
        """Colonize mission fails if planet doesn't exist."""
        from game.strategy.engine.commands import QueueColonizeMissionCommand

        config = GameConfig(system_count=0)
        session = GameSession(config=config)
        session.galaxy = MockGalaxy()

        fleet = Fleet(101, 0, HexCoord(0, 0))
        session.player_empire.fleets = [fleet]

        cmd = QueueColonizeMissionCommand(fleet_id=101, target_hex=HexCoord(10, 10), planet_id=9999)
        result = session.handle_command(cmd)

        assert result.is_valid is False
        assert "Planet not found" in result.message or "planet" in result.message.lower()

    def test_colonize_mission_uses_last_order_target_as_start(self):
        """If fleet has existing orders, use last order target as path start."""
        from game.strategy.engine.commands import QueueColonizeMissionCommand

        config = GameConfig(system_count=0)
        session = GameSession(config=config)
        session.galaxy = MockGalaxy()

        # Fleet at (0,0) with existing MOVE order to (5,5)
        fleet = Fleet(101, 0, HexCoord(0, 0))
        existing_order = FleetOrder(OrderType.MOVE, HexCoord(5, 5))
        fleet.add_order(existing_order)
        session.player_empire.fleets = [fleet]

        planet = MagicMock()
        planet.id = 42
        session.galaxy.planets_by_id[42] = planet

        target_hex = HexCoord(10, 10)
        cmd = QueueColonizeMissionCommand(fleet_id=101, target_hex=target_hex, planet_id=42)

        # Mock pathfinding - path should start from (5,5) not (0,0)
        with patch('game.strategy.data.pathfinding.find_hybrid_path') as mock_path:
            mock_path.return_value = [HexCoord(5, 5), HexCoord(10, 10)]

            result = session.handle_command(cmd)

            assert result.is_valid is True
            # Pathfinding should be called with start_hex=(5,5)
            mock_path.assert_called_once()
            call_args = mock_path.call_args
            assert call_args[0][1] == HexCoord(5, 5)  # second arg is start_hex


# =============================================================================
# Clear Fleet Orders Command Handler Tests (Task 2.5)
# =============================================================================

class TestClearFleetOrdersCommandHandler:
    """Tests for ClearFleetOrdersCommand handling."""

    def test_clear_orders_success(self):
        """Clear orders command removes all orders and path from fleet."""
        from game.strategy.engine.commands import ClearFleetOrdersCommand

        config = GameConfig(system_count=0)
        session = GameSession(config=config)
        session.galaxy = MockGalaxy()

        # Fleet with existing orders and path
        fleet = Fleet(101, 0, HexCoord(0, 0))
        fleet.orders = [
            FleetOrder(OrderType.MOVE, HexCoord(5, 5)),
            FleetOrder(OrderType.COLONIZE, MagicMock())
        ]
        fleet.path = [HexCoord(1, 1), HexCoord(2, 2), HexCoord(5, 5)]
        session.player_empire.fleets = [fleet]

        cmd = ClearFleetOrdersCommand(fleet_id=101)
        result = session.handle_command(cmd)

        assert result.is_valid is True
        assert len(fleet.orders) == 0
        assert len(fleet.path) == 0

    def test_clear_orders_empty_fleet(self):
        """Clear orders succeeds even if fleet has no orders."""
        from game.strategy.engine.commands import ClearFleetOrdersCommand

        config = GameConfig(system_count=0)
        session = GameSession(config=config)
        session.galaxy = MockGalaxy()

        # Fleet with no orders
        fleet = Fleet(101, 0, HexCoord(0, 0))
        session.player_empire.fleets = [fleet]

        cmd = ClearFleetOrdersCommand(fleet_id=101)
        result = session.handle_command(cmd)

        assert result.is_valid is True
        assert len(fleet.orders) == 0
        assert len(fleet.path) == 0

    def test_clear_orders_invalid_fleet(self):
        """Clear orders fails if fleet doesn't exist."""
        from game.strategy.engine.commands import ClearFleetOrdersCommand

        config = GameConfig(system_count=0)
        session = GameSession(config=config)
        session.galaxy = MockGalaxy()

        cmd = ClearFleetOrdersCommand(fleet_id=9999)
        result = session.handle_command(cmd)

        assert result.is_valid is False
        assert "Fleet not found" in result.message

