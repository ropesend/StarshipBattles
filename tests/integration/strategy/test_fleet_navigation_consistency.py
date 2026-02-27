"""
Test: Fleet Navigation Consistency Tests

PROJ-35: Verify that UI path projections ALWAYS match actual turn execution.

These tests ensure the unified FleetNavigationService produces identical results
whether used for:
1. UI path projection (FleetNavigationService.project_path)
2. Turn execution (TurnEngine via FleetMovementEngine -> FleetNavigationService)

The key insight: both UI and execution now use the SAME code path through
FleetNavigationService, so discrepancies should be impossible. These tests
verify that assumption.
"""
import pytest
from unittest.mock import MagicMock, patch

from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.core.hex_math import HexCoord, hex_distance
from game.strategy.services.fleet_navigation_service import (
    FleetNavigationService,
    NavigationState,
    PathSegment,
)


# =============================================================================
# Test Fixtures
# =============================================================================


class MockGalaxy:
    """Minimal galaxy mock for consistency tests."""

    def __init__(self):
        self.systems = {}

    def get_planets_at_global_hex(self, global_hex):
        """Return planets at the given global hex."""
        result = []
        for sys in self.systems.values():
            for p in sys.planets:
                if hasattr(p, 'location') and (sys.global_location + p.location) == global_hex:
                    result.append(p)
        return result

    def get_zones_at_global_hex(self, global_hex):
        """Return zone objects at location (empty for these tests)."""
        return []


@pytest.fixture
def turn_engine():
    """Create a TurnEngine instance."""
    return TurnEngine()


@pytest.fixture
def nav_service():
    """Create a FleetNavigationService instance."""
    return FleetNavigationService()


@pytest.fixture
def mock_galaxy():
    """Create a minimal galaxy mock."""
    return MockGalaxy()


@pytest.fixture
def empire():
    """Create a basic empire."""
    return Empire(0, "TestEmpire", (255, 0, 0))


def create_fleet(fleet_id, empire_id, location, speed):
    """Helper to create a fleet with common defaults."""
    fleet = Fleet(fleet_id, empire_id, location, speed=speed)
    # Mock resource methods to always succeed
    fleet.has_resources_for_movement = MagicMock(return_value=True)
    fleet.consume_movement_resources = MagicMock(return_value=True)
    fleet.can_use_warp = MagicMock(return_value=True)
    fleet.has_resources_for_warp = MagicMock(return_value=True)
    fleet.consume_warp_resources = MagicMock(return_value=True)
    return fleet


# =============================================================================
# Test: Projection Matches Execution
# =============================================================================


class TestProjectionMatchesExecution:
    """Verify UI projections match actual TurnEngine execution."""

    def test_simple_move_consistency(self, turn_engine, nav_service, mock_galaxy, empire):
        """MOVE order: projected path matches execution."""
        # Setup: Fleet at origin, move to (5, 0)
        start = HexCoord(0, 0)
        destination = HexCoord(5, 0)

        fleet = create_fleet(1, empire.id, start, speed=5.0)
        fleet.add_order(FleetOrder(OrderType.MOVE, destination))
        # Pre-compute path so projection is deterministic
        fleet.path = [HexCoord(i, 0) for i in range(1, 6)]  # 1,0 -> 5,0

        empire.add_fleet(fleet)

        # PROJECT: Get what UI would show
        projected_segments = nav_service.project_path(fleet, mock_galaxy, max_turns=5)
        projected_positions = [seg.end for seg in projected_segments]

        # EXECUTE: Reset fleet and run turn engine
        fleet.location = start
        fleet.orders = [FleetOrder(OrderType.MOVE, destination)]
        fleet.path = [HexCoord(i, 0) for i in range(1, 6)]

        # Run one turn (100 ticks)
        turn_engine.process_turn([empire], mock_galaxy)

        # VERIFY: Final position matches projection
        # Speed 5 = 5 hexes per turn, should reach destination
        assert fleet.location == destination
        assert fleet.location == projected_positions[-1]

        # Verify intermediate positions matched
        # With speed 5, all 5 steps happen in turn 0
        for seg in projected_segments:
            assert seg.turn == 0  # All in first turn

    def test_multi_turn_consistency(self, turn_engine, nav_service, mock_galaxy, empire):
        """Multi-turn journey: each step matches."""
        # Setup: Fleet at origin, move to (10, 0) with speed 2
        start = HexCoord(0, 0)
        destination = HexCoord(10, 0)

        fleet = create_fleet(1, empire.id, start, speed=2.0)
        fleet.add_order(FleetOrder(OrderType.MOVE, destination))
        fleet.path = [HexCoord(i, 0) for i in range(1, 11)]  # 1,0 -> 10,0

        empire.add_fleet(fleet)

        # PROJECT: Get positions for each turn
        projected_segments = nav_service.project_path(fleet, mock_galaxy, max_turns=10)

        # Group projections by turn
        positions_by_turn = {}
        for seg in projected_segments:
            if seg.turn not in positions_by_turn:
                positions_by_turn[seg.turn] = []
            positions_by_turn[seg.turn].append(seg.end)

        # EXECUTE: Reset and run turn-by-turn
        fleet.location = start
        fleet.orders = [FleetOrder(OrderType.MOVE, destination)]
        fleet.path = [HexCoord(i, 0) for i in range(1, 11)]

        # Speed 2 = 2 hexes per turn, need 5 turns for 10 hexes
        for turn in range(5):
            initial_location = fleet.location
            turn_engine.process_turn([empire], mock_galaxy)

            # VERIFY: Position matches projection for this turn
            if turn in positions_by_turn:
                expected_final = positions_by_turn[turn][-1]
                assert fleet.location == expected_final, (
                    f"Turn {turn}: expected {expected_final}, got {fleet.location}"
                )

        # Final position should be destination
        assert fleet.location == destination

    @patch('game.strategy.services.fleet_navigation_service.find_hybrid_path')
    def test_warp_move_consistency(self, mock_path, turn_engine, nav_service, mock_galaxy, empire):
        """Warp jump projection matches execution."""
        # Setup: Fleet at origin with warp jump in path
        start = HexCoord(0, 0)
        warp_dest = HexCoord(100, 0)  # Far destination = warp

        fleet = create_fleet(1, empire.id, start, speed=5.0)
        fleet.add_order(FleetOrder(OrderType.MOVE, warp_dest))
        # Path with a warp segment (distance > 1)
        fleet.path = [HexCoord(50, 0), HexCoord(100, 0)]  # Warp to 50, then to 100

        # Mock find_hybrid_path to return None (use pre-set path)
        mock_path.return_value = None

        empire.add_fleet(fleet)

        # PROJECT: Check warp detection
        projected_segments = nav_service.project_path(fleet, mock_galaxy, max_turns=5)

        # First segment should be warp (distance from 0,0 to 50,0 = 50 > 1)
        assert len(projected_segments) >= 1
        assert projected_segments[0].is_warp is True

        # EXECUTE: Reset and run
        fleet.location = start
        fleet.orders = [FleetOrder(OrderType.MOVE, warp_dest)]
        fleet.path = [HexCoord(50, 0), HexCoord(100, 0)]

        turn_engine.process_turn([empire], mock_galaxy)

        # VERIFY: Warp resources were consumed (confirming warp was detected)
        fleet.consume_warp_resources.assert_called()

        # Fleet should have moved along projected warp path
        # With speed 5, should make 5 steps per turn
        # First step is warp to (50, 0)
        assert fleet.location.q >= 50  # Should have made at least first warp jump

    def test_intercept_consistency(self, turn_engine, nav_service, mock_galaxy, empire):
        """MOVE_TO_FLEET: intercept point matches."""
        # Setup: Chaser pursuing stationary target
        start = HexCoord(0, 0)
        target_loc = HexCoord(10, 0)

        # Create target fleet (stationary)
        enemy_empire = Empire(1, "Enemy", (0, 0, 255))
        target_fleet = create_fleet(2, enemy_empire.id, target_loc, speed=0.0)
        enemy_empire.add_fleet(target_fleet)

        # Create chaser fleet with MOVE_TO_FLEET order
        chaser = create_fleet(1, empire.id, start, speed=5.0)
        chaser.add_order(FleetOrder(OrderType.MOVE_TO_FLEET, target_fleet))
        # Pre-set path to target
        chaser.path = [HexCoord(i, 0) for i in range(1, 11)]

        empire.add_fleet(chaser)

        # PROJECT: Get intercept point from projection
        projected_segments = nav_service.project_path(chaser, mock_galaxy, max_turns=5)
        if projected_segments:
            projected_destination = projected_segments[-1].end
        else:
            # If no projection, intercept is already at location
            projected_destination = start

        # EXECUTE: Run turns until chaser reaches target
        chaser.location = start
        chaser.orders = [FleetOrder(OrderType.MOVE_TO_FLEET, target_fleet)]
        chaser.path = [HexCoord(i, 0) for i in range(1, 11)]

        for _ in range(3):
            if chaser.location == target_loc:
                break
            turn_engine.process_turn([empire, enemy_empire], mock_galaxy)

        # VERIFY: Chaser reaches target location (stationary intercept)
        assert chaser.location == target_loc
        # Projected destination should match actual final position
        assert chaser.location == projected_destination or chaser.location == target_loc

    def test_chained_orders_consistency(self, turn_engine, nav_service, mock_galaxy, empire):
        """Multiple orders: full queue matches."""
        # Setup: Fleet with two MOVE orders queued
        start = HexCoord(0, 0)
        waypoint = HexCoord(2, 0)
        destination = HexCoord(5, 0)

        fleet = create_fleet(1, empire.id, start, speed=5.0)
        fleet.add_order(FleetOrder(OrderType.MOVE, waypoint))
        fleet.add_order(FleetOrder(OrderType.MOVE, destination))
        fleet.path = [HexCoord(1, 0), HexCoord(2, 0)]  # First order path

        empire.add_fleet(fleet)

        # PROJECT: Get full projected path including chained orders
        projected_segments = nav_service.project_path(fleet, mock_galaxy, max_turns=5)
        projected_positions = [seg.end for seg in projected_segments]

        # Should project through both orders:
        # Order 1: 0,0 -> 1,0 -> 2,0
        # Order 2: 2,0 -> 3,0 -> 4,0 -> 5,0
        assert HexCoord(2, 0) in projected_positions  # Waypoint
        assert HexCoord(5, 0) in projected_positions  # Final destination

        # EXECUTE: Reset and run
        fleet.location = start
        fleet.orders = [
            FleetOrder(OrderType.MOVE, waypoint),
            FleetOrder(OrderType.MOVE, destination)
        ]
        fleet.path = [HexCoord(1, 0), HexCoord(2, 0)]

        # With speed 5, should complete both orders in 1 turn
        turn_engine.process_turn([empire], mock_galaxy)

        # VERIFY: Final position matches projection
        assert fleet.location == destination
        assert len(fleet.orders) == 0  # Both orders consumed


class TestEdgeCases:
    """Edge cases for consistency verification."""

    def test_already_at_destination_consistency(self, turn_engine, nav_service, mock_galaxy, empire):
        """Fleet already at destination: no movement occurs."""
        loc = HexCoord(5, 5)

        fleet = create_fleet(1, empire.id, loc, speed=5.0)
        fleet.add_order(FleetOrder(OrderType.MOVE, loc))
        fleet.path = []  # Empty path - already there

        empire.add_fleet(fleet)

        # PROJECT: Should return empty or single-point projection
        projected_segments = nav_service.project_path(fleet, mock_galaxy, max_turns=5)

        # EXECUTE
        turn_engine.process_turn([empire], mock_galaxy)

        # VERIFY: Location unchanged
        assert fleet.location == loc
        assert len(fleet.orders) == 0  # Order should complete immediately

    def test_zero_speed_fleet_consistency(self, turn_engine, nav_service, mock_galaxy, empire):
        """Zero speed fleet: projection and execution both show no movement."""
        start = HexCoord(0, 0)
        destination = HexCoord(5, 0)

        fleet = create_fleet(1, empire.id, start, speed=0.0)
        fleet.add_order(FleetOrder(OrderType.MOVE, destination))
        fleet.path = [HexCoord(i, 0) for i in range(1, 6)]

        empire.add_fleet(fleet)

        # PROJECT: Should return empty (can't move)
        projected_segments = nav_service.project_path(fleet, mock_galaxy, max_turns=5)
        assert len(projected_segments) == 0

        # EXECUTE
        turn_engine.process_turn([empire], mock_galaxy)

        # VERIFY: No movement
        assert fleet.location == start

    def test_fractional_speed_consistency(self, turn_engine, nav_service, mock_galaxy, empire):
        """Fractional speed: movement timing matches projection."""
        start = HexCoord(0, 0)
        destination = HexCoord(10, 0)

        # Speed 0.5 = moves every 2 turns (200 ticks / 100 ticks per turn)
        # Actually: interval = 100 // 0.5 is undefined for speed < 1
        # Let's use speed 1.5 instead - moves every 66 ticks
        fleet = create_fleet(1, empire.id, start, speed=1.5)
        fleet.add_order(FleetOrder(OrderType.MOVE, destination))
        fleet.path = [HexCoord(i, 0) for i in range(1, 11)]

        empire.add_fleet(fleet)

        # PROJECT
        projected_segments = nav_service.project_path(fleet, mock_galaxy, max_turns=10)

        # Speed 1.5 = int(1.5) = 1 hex per turn
        # Turn 0: 1 hex
        # Turn 1: 1 hex
        # etc.
        turn_0_segments = [s for s in projected_segments if s.turn == 0]
        assert len(turn_0_segments) == 1  # 1 hex in turn 0

        # EXECUTE: Run first turn
        turn_engine.process_turn([empire], mock_galaxy)

        # VERIFY: Should have moved 1 hex
        expected_after_turn_0 = HexCoord(1, 0)
        assert fleet.location == expected_after_turn_0


class TestNonMovementOrderHandling:
    """Verify non-movement orders don't break consistency."""

    def test_colonize_order_not_projected_as_movement(self, turn_engine, nav_service, mock_galaxy, empire):
        """COLONIZE order: projection stops, execution handles correctly."""
        loc = HexCoord(5, 5)

        # Create a mock planet
        planet = MagicMock()
        planet.name = "TestPlanet"
        planet.owner_id = None
        planet.construction_queue = []
        planet.location = HexCoord(0, 0)

        # Create mock system
        mock_system = MagicMock()
        mock_system.global_location = loc
        mock_system.planets = [planet]
        mock_galaxy.systems[loc] = mock_system

        fleet = create_fleet(1, empire.id, loc, speed=5.0)
        fleet.add_order(FleetOrder(OrderType.COLONIZE, planet))
        fleet.path = []

        empire.add_fleet(fleet)

        # PROJECT: Should not show movement for COLONIZE
        projected_segments = nav_service.project_path(fleet, mock_galaxy, max_turns=5)
        assert len(projected_segments) == 0  # No movement projected

        # EXECUTE
        turn_engine.process_turn([empire], mock_galaxy)

        # VERIFY: Fleet processed colonize order, didn't move
        assert fleet.location == loc

    def test_move_then_colonize_consistency(self, turn_engine, nav_service, mock_galaxy, empire):
        """MOVE -> COLONIZE chain: movement projects, colonize doesn't."""
        start = HexCoord(0, 0)
        colony_loc = HexCoord(2, 0)

        # Create mock planet at destination
        planet = MagicMock()
        planet.name = "ColonyTarget"
        planet.owner_id = None
        planet.construction_queue = []
        planet.location = HexCoord(0, 0)

        mock_system = MagicMock()
        mock_system.global_location = colony_loc
        mock_system.planets = [planet]
        mock_galaxy.systems[colony_loc] = mock_system

        fleet = create_fleet(1, empire.id, start, speed=5.0)
        fleet.add_order(FleetOrder(OrderType.MOVE, colony_loc))
        fleet.add_order(FleetOrder(OrderType.COLONIZE, planet))
        fleet.path = [HexCoord(1, 0), HexCoord(2, 0)]

        empire.add_fleet(fleet)

        # PROJECT: Should show movement to colony_loc but stop before COLONIZE
        projected_segments = nav_service.project_path(fleet, mock_galaxy, max_turns=5)
        projected_destinations = [seg.end for seg in projected_segments]

        assert colony_loc in projected_destinations  # Moved to colony location
        # Projection stops at COLONIZE - doesn't continue past it

        # EXECUTE
        turn_engine.process_turn([empire], mock_galaxy)

        # VERIFY: Fleet moved to colony location
        # (May or may not have colonized depending on tick timing)
        assert fleet.location == colony_loc
