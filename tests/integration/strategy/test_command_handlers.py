import pytest
from unittest.mock import MagicMock, patch
from game.strategy.engine.game_session import GameSession
from game.strategy.engine.game_config import GameConfig
from game.strategy.engine.commands import IssueMoveCommand, CommandType
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import OrderType, FleetOrder
from game.core.hex_math import HexCoord
from game.strategy.data.empire import Empire
from game.strategy.data.ship_instance import ShipInstance


def make_colony_ship(planet_type: str, owner_id: int, instance_id: str = "colony-ship-1") -> ShipInstance:
    """Create a ship with a colony pod for the specified planet type.

    PROJ-140: Ships need colony pods to colonize specific planet types.
    """
    pod_id = f"{planet_type.lower()}_colony_pod"

    return ShipInstance(
        instance_id=instance_id,
        design_id=f"{planet_type}_colony_ship",
        name=f"Colony Ship ({planet_type})",
        owner_id=owner_id,
        design_data={
            'name': f"Colony Ship ({planet_type})",
            'vehicle_type': 'Ship',
            'stats': {'mass': 100},
            'layers': {
                'HULL': [{'id': pod_id}]
            }
        },
    )

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

    def get_system_of_object(self, obj):
        """Return the system at the object's location, or None."""
        location = getattr(obj, 'location', None)
        return self.systems.get(location)

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
    session.galaxy = MockGalaxy()

    # Setup Fleet
    fleet = Fleet(101, 0, HexCoord(0,0))
    session.player_empire.fleets = [fleet]
    session.galaxy.register_fleet(fleet)

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

# NOTE: test_handle_build_ship_command removed in PROJ-208 Phase 2.
# IssueBuildShipCommand was dead code - use AddToConstructionQueueCommand.
# See tests/unit/strategy/engine/test_command_handlers.py for new tests.


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
        session.galaxy.register_fleet(fleet)
        session.galaxy.register_fleet(target_fleet)

        cmd = IssueInterceptCommand(fleet_id=101, target_fleet_id=102)
        result = session.handle_command(cmd)

        assert result.is_valid is True
        assert result.errors == []
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
        session.galaxy.register_fleet(fleet)

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
        session.galaxy.register_fleet(fleet)
        session.galaxy.register_fleet(target_fleet)

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
        session.galaxy.register_fleet(fleet)

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

        # Setup fleet with colony ship (PROJ-140: needs matching pod)
        fleet = Fleet(101, 0, HexCoord(0, 0))
        fleet.ships = [make_colony_ship("CONTINENTAL", owner_id=0)]
        session.player_empire.fleets = [fleet]
        session.galaxy.register_fleet(fleet)

        # Mock planet with proper planet_type
        planet = MagicMock()
        planet.id = 42
        planet.name = "Test Planet"
        planet_type = MagicMock()
        planet_type.name = "CONTINENTAL"
        planet.planet_type = planet_type
        session.galaxy.planets_by_id[42] = planet

        target_hex = HexCoord(10, 10)
        cmd = QueueColonizeMissionCommand(fleet_id=101, target_hex=target_hex, planet_id=42)

        # Mock pathfinding
        with patch('game.strategy.data.pathfinding.find_hybrid_path') as mock_path:
            mock_path.return_value = [HexCoord(0, 0), HexCoord(5, 5), HexCoord(10, 10)]

            result = session.handle_command(cmd)

            assert result.is_valid is True
            # BUG-70: Order queue is now LOAD_POPULATION + MOVE + COLONIZE
            assert len(fleet.orders) == 3
            assert fleet.orders[0].type == OrderType.LOAD_POPULATION
            assert fleet.orders[1].type == OrderType.MOVE
            assert fleet.orders[1].target == target_hex
            assert fleet.orders[2].type == OrderType.COLONIZE
            assert fleet.orders[2].target == planet

    def test_colonize_mission_no_path(self):
        """Colonize mission fails if no path to target."""
        from game.strategy.engine.commands import QueueColonizeMissionCommand

        config = GameConfig(system_count=0)
        session = GameSession(config=config)
        session.galaxy = MockGalaxy()

        # PROJ-140: Fleet needs colony ship with matching pod
        fleet = Fleet(101, 0, HexCoord(0, 0))
        fleet.ships = [make_colony_ship("ICE_DWARF", owner_id=0)]
        session.player_empire.fleets = [fleet]
        session.galaxy.register_fleet(fleet)

        # Mock planet with proper planet_type
        planet = MagicMock()
        planet.id = 42
        planet_type = MagicMock()
        planet_type.name = "ICE_DWARF"
        planet.planet_type = planet_type
        session.galaxy.planets_by_id[42] = planet

        cmd = QueueColonizeMissionCommand(fleet_id=101, target_hex=HexCoord(100, 100), planet_id=42)

        # Mock pathfinding to return None (no path)
        # PROJ-207: Patch at command_handlers where function is imported
        with patch('game.strategy.engine.command_handlers.find_hybrid_path') as mock_path:
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
        session.galaxy.register_fleet(fleet)

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
        # PROJ-140: Fleet needs colony ship with matching pod
        # Use JOVIAN which has jovian_colony_pod in components.json
        fleet = Fleet(101, 0, HexCoord(0, 0))
        fleet.ships = [make_colony_ship("JOVIAN", owner_id=0)]
        existing_order = FleetOrder(OrderType.MOVE, HexCoord(5, 5))
        fleet.add_order(existing_order)
        session.player_empire.fleets = [fleet]
        session.galaxy.register_fleet(fleet)

        # Mock planet with proper planet_type
        planet = MagicMock()
        planet.id = 42
        planet_type = MagicMock()
        planet_type.name = "JOVIAN"
        planet.planet_type = planet_type
        session.galaxy.planets_by_id[42] = planet

        target_hex = HexCoord(10, 10)
        cmd = QueueColonizeMissionCommand(fleet_id=101, target_hex=target_hex, planet_id=42)

        # Mock pathfinding - path should start from (5,5) not (0,0)
        # PROJ-207: Patch at command_handlers where function is imported
        with patch('game.strategy.engine.command_handlers.find_hybrid_path') as mock_path:
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
        session.galaxy.register_fleet(fleet)

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
        session.galaxy.register_fleet(fleet)

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

    def test_clear_orders_discards_execution_progress(self):
        """Clear orders discards FleetOrder execution_progress (PROJ-187).

        Multi-tick actions accumulate execution_progress on the FleetOrder.
        When orders are cleared, the entire FleetOrder object is removed,
        so execution_progress is naturally discarded.
        """
        from game.strategy.engine.commands import ClearFleetOrdersCommand

        config = GameConfig(system_count=0)
        session = GameSession(config=config)
        session.galaxy = MockGalaxy()

        # Fleet with an order that has accumulated execution_progress
        fleet = Fleet(101, 0, HexCoord(0, 0))
        colonize_order = FleetOrder(OrderType.COLONIZE, MagicMock())
        colonize_order.execution_progress = 3  # Simulating partial progress
        fleet.orders = [colonize_order]
        session.player_empire.fleets = [fleet]
        session.galaxy.register_fleet(fleet)

        # Verify progress exists before clear
        assert fleet.orders[0].execution_progress == 3

        cmd = ClearFleetOrdersCommand(fleet_id=101)
        result = session.handle_command(cmd)

        assert result.is_valid is True
        assert len(fleet.orders) == 0  # Order with progress is gone

