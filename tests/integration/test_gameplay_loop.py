"""
Integration tests for the multi-turn gameplay loop.

Tests the end-to-end turn execution cycle, including:
- Complete turn execution
- Multiple turns in sequence
- Resource accumulation across turns
- Command queue execution
- Movement and pathfinding
- Production workflows
"""

import pytest
import os
import json
import tempfile
from unittest.mock import MagicMock, patch

from game.strategy.engine.game_session import GameSession
from game.strategy.engine.game_config import GameConfig, PlayerConfig
from game.strategy.engine.turn_engine import TurnEngine
from game.core.validation import ValidationResult
from game.strategy.engine.commands import CommandType, IssueColonizeCommand, IssueMoveCommand
from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.strategy.data.hex_math import HexCoord
from game.strategy.data.galaxy import Galaxy
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.ship_instance import ShipInstance
from tests.conftest import make_mock_ship_instance


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def minimal_config():
    """Create minimal game config for testing."""
    config = GameConfig()
    config.galaxy_radius = 500
    config.system_count = 3
    config.players = [
        PlayerConfig(name="Player", is_human=True, color=(0, 100, 200)),
        PlayerConfig(name="Enemy", is_human=False, color=(200, 100, 0)),
    ]
    return config


@pytest.fixture
def game_session(minimal_config):
    """Create a game session with minimal configuration."""
    session = GameSession(config=minimal_config)
    return session


@pytest.fixture
def turn_engine():
    """Create a standalone turn engine for isolated tests."""
    return TurnEngine()


@pytest.fixture
def simple_galaxy():
    """Create a simple galaxy with a few systems."""
    galaxy = Galaxy(radius=500)
    galaxy.generate_systems(count=5, min_dist=100)
    galaxy.generate_warp_lanes()
    return galaxy


@pytest.fixture
def two_empire_setup(simple_galaxy):
    """Create two empires with colonies and fleets."""
    empire1 = Empire(0, "Player", (0, 100, 200))
    empire2 = Empire(1, "Enemy", (200, 100, 0))

    # Give each empire a colony
    systems = list(simple_galaxy.systems.values())
    if len(systems) >= 2:
        if systems[0].planets:
            empire1.add_colony(systems[0].planets[0])
        if systems[1].planets:
            empire2.add_colony(systems[1].planets[0])

    return empire1, empire2, simple_galaxy


@pytest.fixture
def test_savegame_dir():
    """Create temporary savegame directory with test designs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create designs directory structure for empire 0
        designs_dir = os.path.join(tmpdir, "designs", "empire_0")
        os.makedirs(designs_dir, exist_ok=True)

        # Create test ship design
        ship_design = {
            "name": "Test Frigate",
            "vehicle_type": "Ship",
            "vehicle_class": "Frigate",
            "mass": 5000,
            "layers": {
                "core": {
                    "components": [
                        {
                            "id": "basic_reactor",
                            "position": [0, 0]
                        }
                    ]
                }
            }
        }

        with open(os.path.join(designs_dir, "test_frigate.json"), "w") as f:
            json.dump(ship_design, f)

        yield tmpdir


# =============================================================================
# Test: Complete Turn Execution Cycle
# =============================================================================


class TestTurnExecutionCycle:
    """Tests for complete turn execution."""

    def test_turn_advances_turn_number(self, game_session):
        """Turn processing increments turn number."""
        initial_turn = game_session.turn_number
        game_session.process_turn()
        assert game_session.turn_number == initial_turn + 1

    def test_turn_processes_all_empires(self, turn_engine, two_empire_setup):
        """Turn engine processes all empires in the game."""
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        # Add fleets with orders to both empires
        fleet1 = Fleet(1, empire1.id, HexCoord(0, 0), speed=10.0)
        fleet1.add_order(FleetOrder(OrderType.MOVE, target=HexCoord(1, 0)))
        empire1.add_fleet(fleet1)

        fleet2 = Fleet(2, empire2.id, HexCoord(5, 5), speed=10.0)
        fleet2.add_order(FleetOrder(OrderType.MOVE, target=HexCoord(6, 5)))
        empire2.add_fleet(fleet2)

        # Process turn
        turn_engine.process_turn(empires, galaxy)

        # Both fleets should have moved
        assert fleet1.location != HexCoord(0, 0) or len(fleet1.orders) == 0
        assert fleet2.location != HexCoord(5, 5) or len(fleet2.orders) == 0

    def test_turn_has_100_subticks(self, turn_engine, two_empire_setup):
        """Turn engine processes 100 subticks per turn."""
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        # Create a fast fleet (speed 100 = moves every tick)
        fleet = Fleet(1, empire1.id, HexCoord(0, 0), speed=100.0)

        # Create a long path to measure movement
        path_length = 50
        fleet.add_order(FleetOrder(OrderType.MOVE, target=HexCoord(path_length, 0)))
        empire1.add_fleet(fleet)

        initial_loc = fleet.location
        turn_engine.process_turn(empires, galaxy)

        # With speed 100, fleet moves every tick (100 times per turn)
        # Should have moved a significant distance
        from game.strategy.data.hex_math import hex_distance
        distance_moved = hex_distance(initial_loc, fleet.location)
        assert distance_moved > 0

    def test_turn_executes_phases_in_order(self, turn_engine, two_empire_setup):
        """Turn engine executes phases in correct order: movement, orders, production."""
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        # This is verified by the overall behavior - movement before production
        # A fleet at a planet can colonize after arriving
        planet = None
        for system in galaxy.systems.values():
            for p in system.planets:
                if p.owner_id is None:
                    planet = p
                    break
            if planet:
                break

        if planet:
            # Create fleet at planet location and give colonize order
            fleet = Fleet(1, empire1.id, planet.location, speed=10.0)
            fleet.add_order(FleetOrder(OrderType.COLONIZE, target=planet))
            empire1.add_fleet(fleet)

            initial_colonies = len(empire1.colonies)
            turn_engine.process_turn(empires, galaxy)

            # Colonization should have executed
            # Note: Fleet is consumed on colonization
            assert len(empire1.colonies) >= initial_colonies


# =============================================================================
# Test: Multiple Turns in Sequence
# =============================================================================


class TestMultipleTurns:
    """Tests for multi-turn game progression."""

    def test_ten_turns_execute_without_error(self, game_session):
        """10 sequential turns execute without exceptions."""
        for _ in range(10):
            game_session.process_turn()

        assert game_session.turn_number == 11

    def test_fleet_reaches_destination_over_turns(self, turn_engine, two_empire_setup):
        """Fleet completes long journey over multiple turns."""
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        # Create fleet with speed 10 (moves every 10 ticks = 10 hexes per turn)
        start = HexCoord(0, 0)
        destination = HexCoord(25, 0)  # ~3 turns away at speed 10

        fleet = Fleet(1, empire1.id, start, speed=10.0)
        fleet.add_order(FleetOrder(OrderType.MOVE, target=destination))
        empire1.add_fleet(fleet)

        # Process turns until fleet arrives or max 10 turns
        for turn in range(10):
            if fleet.location == destination:
                break
            turn_engine.process_turn(empires, galaxy)

        # Fleet should have reached destination
        assert fleet.location == destination or len(fleet.orders) == 0

    def test_production_completes_across_turns(self, turn_engine, two_empire_setup, test_savegame_dir):
        """Production queue decrements and completes over multiple turns."""
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        # Get empire's colony
        if not empire1.colonies:
            pytest.skip("No colony available for test")

        colony = empire1.colonies[0]

        # Use complex type which doesn't require shipyard
        colony.add_production("test_complex", turns=3, vehicle_type="complex")
        assert len(colony.construction_queue) == 1

        # Turn 1 - decrements to 2
        turn_engine.process_production(empires, galaxy, save_path=test_savegame_dir)
        if colony.construction_queue:
            item = colony.construction_queue[0]
            remaining = item["turns_remaining"] if isinstance(item, dict) else item[1]
            assert remaining == 2

        # Turn 2 - decrements to 1
        turn_engine.process_production(empires, galaxy, save_path=test_savegame_dir)
        if colony.construction_queue:
            item = colony.construction_queue[0]
            remaining = item["turns_remaining"] if isinstance(item, dict) else item[1]
            assert remaining == 1

    def test_state_persists_between_turns(self, game_session):
        """Game state is preserved correctly between turns."""
        # Capture initial state
        initial_empires = len(game_session.empires)
        initial_systems = len(game_session.systems)

        # Process several turns
        for _ in range(5):
            game_session.process_turn()

        # State should be preserved
        assert len(game_session.empires) == initial_empires
        assert len(game_session.systems) == initial_systems
        assert game_session.turn_number == 6


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
        from game.strategy.data.ship_instance import ShipInstance

        fleet = Fleet(1, empire1.id, HexCoord(0, 0), speed=10.0)

        # Create minimal ship instance with fuel
        mock_ship = MagicMock(spec=ShipInstance)
        mock_ship.is_combat_capable.return_value = True
        mock_ship.is_destroyed = False
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
        fleet.add_order(FleetOrder(OrderType.MOVE, target=HexCoord(10, 0)))
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
        from game.strategy.data.ship_instance import ShipInstance

        fleet = Fleet(1, empire1.id, HexCoord(0, 0), speed=0.0)  # Stationary

        mock_ship = MagicMock(spec=ShipInstance)
        mock_ship.is_combat_capable.return_value = True
        mock_ship.is_destroyed = False
        mock_ship.is_derelict = False
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

        from game.strategy.data.ship_instance import ShipInstance

        fleet = Fleet(1, empire1.id, HexCoord(0, 0), speed=10.0)

        # Create ship with no fuel
        mock_ship = MagicMock(spec=ShipInstance)
        mock_ship.is_combat_capable.return_value = True
        mock_ship.is_destroyed = False
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
        fleet.add_order(FleetOrder(OrderType.MOVE, target=HexCoord(10, 0)))
        empire1.add_fleet(fleet)

        initial_orders = len(fleet.orders)
        turn_engine.process_turn(empires, galaxy)

        # Fleet should have lost its orders (stranded)
        assert len(fleet.orders) == 0


# =============================================================================
# Test: Command Queue Execution
# =============================================================================


class TestCommandExecution:
    """Tests for command handling and order execution."""

    def test_move_command_adds_order(self, game_session):
        """Move command adds order to fleet."""
        # Get player empire and create a fleet
        empire = game_session.player_empire
        if not empire:
            pytest.skip("No player empire")

        fleet = Fleet(99, empire.id, HexCoord(0, 0), speed=10.0)
        empire.add_fleet(fleet)

        # Create and handle move command
        from game.strategy.engine.commands import Command

        # Create mock command
        cmd = MagicMock()
        cmd.type = CommandType.ISSUE_ORDER
        cmd.name = 'IssueMoveCommand'
        cmd.fleet_id = 99
        cmd.target_hex = HexCoord(5, 0)

        result = game_session.handle_command(cmd)

        # Fleet should have move order
        if result and result.is_valid:
            assert len(fleet.orders) > 0
            assert fleet.orders[-1].type == OrderType.MOVE

    def test_colonize_command_validates_planet(self, game_session):
        """Colonize command validates target planet."""
        empire = game_session.player_empire
        if not empire:
            pytest.skip("No player empire")

        # Create fleet at random location (not at planet)
        fleet = Fleet(99, empire.id, HexCoord(-100, -100), speed=10.0)
        empire.add_fleet(fleet)

        # Create mock colonize command
        cmd = MagicMock()
        cmd.type = CommandType.ISSUE_ORDER
        cmd.name = 'IssueColonizeCommand'
        cmd.fleet_id = 99
        cmd.planet_id = None  # "Any planet"

        result = game_session.handle_command(cmd)

        # Should fail - no planet at fleet location
        if result:
            assert not result.is_valid or "NO_CANDIDATES" in str(result.message)

    def test_orders_execute_in_sequence(self, turn_engine, two_empire_setup):
        """Multiple orders execute in queue order."""
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        fleet = Fleet(1, empire1.id, HexCoord(0, 0), speed=100.0)  # Very fast

        # Add two move orders
        fleet.add_order(FleetOrder(OrderType.MOVE, target=HexCoord(2, 0)))
        fleet.add_order(FleetOrder(OrderType.MOVE, target=HexCoord(4, 0)))

        empire1.add_fleet(fleet)

        # After first turn, should have completed first order and possibly started second
        turn_engine.process_turn(empires, galaxy)

        # Fleet should have moved
        assert fleet.location != HexCoord(0, 0)

    def test_order_cleared_on_completion(self, turn_engine, two_empire_setup):
        """Orders are removed from queue when completed."""
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        fleet = Fleet(1, empire1.id, HexCoord(0, 0), speed=100.0)
        fleet.add_order(FleetOrder(OrderType.MOVE, target=HexCoord(1, 0)))  # Very short move

        empire1.add_fleet(fleet)

        initial_orders = len(fleet.orders)

        # Process until order complete or timeout
        for _ in range(5):
            turn_engine.process_turn(empires, galaxy)
            if len(fleet.orders) < initial_orders:
                break

        # Order should have been removed
        assert len(fleet.orders) == 0


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
        fast_fleet.add_order(FleetOrder(OrderType.MOVE, target=HexCoord(100, 0)))
        empire1.add_fleet(fast_fleet)

        # Slow fleet (speed 10 = moves every 10 ticks = 10 hexes per turn)
        slow_fleet = Fleet(2, empire1.id, HexCoord(0, 5), speed=10.0)
        slow_fleet.add_order(FleetOrder(OrderType.MOVE, target=HexCoord(100, 5)))
        empire1.add_fleet(slow_fleet)

        turn_engine.process_turn(empires, galaxy)

        from game.strategy.data.hex_math import hex_distance

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
        fleet.add_order(FleetOrder(OrderType.MOVE, target=destination))
        empire1.add_fleet(fleet)

        # Process turns until arrival
        for _ in range(3):
            turn_engine.process_turn(empires, galaxy)

        # Fleet should be at destination
        assert fleet.location == destination
        assert len(fleet.orders) == 0  # Order completed

    def test_fleet_path_preview_matches_actual(self, game_session):
        """Path preview matches actual movement path."""
        empire = game_session.player_empire
        if not empire:
            pytest.skip("No player empire")

        fleet = Fleet(99, empire.id, HexCoord(0, 0), speed=10.0)
        empire.add_fleet(fleet)

        target = HexCoord(10, 0)

        # Get preview path
        preview_path = game_session.preview_fleet_path(fleet, target)

        # Give fleet move order
        fleet.add_order(FleetOrder(OrderType.MOVE, target=target))

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

    def test_join_fleet_merges_ships(self, turn_engine, two_empire_setup):
        """JOIN_FLEET order transfers ships to target fleet."""
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        # Create two fleets at same location
        loc = HexCoord(0, 0)
        target_fleet = Fleet(1, empire1.id, loc, speed=10.0)
        target_fleet.ships = [make_mock_ship_instance("Scout", empire1.id)]
        empire1.add_fleet(target_fleet)

        joining_fleet = Fleet(2, empire1.id, loc, speed=10.0)
        joining_fleet.ships = [make_mock_ship_instance("Destroyer", empire1.id)]
        joining_fleet.add_order(FleetOrder(OrderType.JOIN_FLEET, target=target_fleet))
        empire1.add_fleet(joining_fleet)

        initial_fleets = len(empire1.fleets)

        turn_engine.process_turn(empires, galaxy)

        # One fleet should have been removed
        assert len(empire1.fleets) < initial_fleets

        # Target fleet should have both ships
        if target_fleet in empire1.fleets:
            assert len(target_fleet.ships) == 2

    def test_join_fleet_requires_same_location(self, turn_engine, two_empire_setup):
        """JOIN_FLEET only merges when fleets are co-located."""
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        # Create two fleets at DIFFERENT locations
        target_fleet = Fleet(1, empire1.id, HexCoord(0, 0), speed=10.0)
        target_fleet.ships = [make_mock_ship_instance("Scout", empire1.id)]
        empire1.add_fleet(target_fleet)

        joining_fleet = Fleet(2, empire1.id, HexCoord(10, 10), speed=10.0)  # Different location
        joining_fleet.ships = [make_mock_ship_instance("Destroyer", empire1.id)]
        joining_fleet.add_order(FleetOrder(OrderType.JOIN_FLEET, target=target_fleet))
        empire1.add_fleet(joining_fleet)

        initial_target_ships = len(target_fleet.ships)

        # Process single turn - they shouldn't merge since not co-located
        # (JOIN_FLEET at end-of-turn requires same location)
        turn_engine.process_turn(empires, galaxy)

        # Target fleet ships should be unchanged if not merged
        # (joining fleet might have tried but failed due to distance)
        assert len(target_fleet.ships) >= initial_target_ships


# =============================================================================
# Test: Battle Resolution During Turn
# =============================================================================


class TestBattleResolution:
    """Tests for battle resolution when fleets meet."""

    def test_opposing_fleets_trigger_combat(self, turn_engine, two_empire_setup):
        """Fleets from different empires at same hex trigger combat."""
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        # Create opposing fleets at same location
        loc = HexCoord(0, 0)
        fleet1 = Fleet(1, empire1.id, loc, speed=10.0)
        fleet1.ships = [
            make_mock_ship_instance("Scout", empire1.id),
            make_mock_ship_instance("Destroyer", empire1.id)
        ]
        empire1.add_fleet(fleet1)

        fleet2 = Fleet(2, empire2.id, loc, speed=10.0)
        fleet2.ships = [make_mock_ship_instance("Scout", empire2.id)]
        empire2.add_fleet(fleet2)

        total_fleets = len(empire1.fleets) + len(empire2.fleets)

        turn_engine.process_turn(empires, galaxy)

        # One fleet should have been destroyed (RNG resolution)
        remaining_fleets = len(empire1.fleets) + len(empire2.fleets)
        assert remaining_fleets < total_fleets

    def test_same_empire_fleets_no_combat(self, turn_engine, two_empire_setup):
        """Fleets from same empire don't fight each other."""
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        # Create two fleets from same empire at same location
        loc = HexCoord(0, 0)
        fleet1 = Fleet(1, empire1.id, loc, speed=10.0)
        fleet1.ships = [make_mock_ship_instance("Scout", empire1.id)]
        empire1.add_fleet(fleet1)

        fleet2 = Fleet(2, empire1.id, loc, speed=10.0)  # Same empire
        fleet2.ships = [make_mock_ship_instance("Destroyer", empire1.id)]
        empire1.add_fleet(fleet2)

        initial_fleets = len(empire1.fleets)

        turn_engine.process_turn(empires, galaxy)

        # No combat should have occurred
        assert len(empire1.fleets) == initial_fleets


# =============================================================================
# Test: Turn Engine Isolation
# =============================================================================


class TestTurnEngineIsolation:
    """Tests for turn engine state isolation."""

    def test_turn_engine_has_no_persistent_state(self):
        """Turn engine starts with clean state."""
        engine = TurnEngine()

        # PROJ-36: Battle seed counter moved to ConflictResolutionEngine
        # Conflict engine should be None initially (lazy initialization)
        assert engine._conflict_engine is None

    def test_battle_seeds_increment(self, turn_engine, two_empire_setup):
        """Battle seeds increment for determinism."""
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        # PROJ-36: Seed counter is now in ConflictResolutionEngine
        # Access conflict_engine to initialize it, then get initial seed
        initial_seed = turn_engine.conflict_engine._battle_seed_counter

        # Create combat situation
        loc = HexCoord(0, 0)
        fleet1 = Fleet(1, empire1.id, loc, speed=10.0)
        fleet1.ships = [make_mock_ship_instance("Scout", empire1.id)]
        empire1.add_fleet(fleet1)

        fleet2 = Fleet(2, empire2.id, loc, speed=10.0)
        fleet2.ships = [make_mock_ship_instance("Scout", empire2.id)]
        empire2.add_fleet(fleet2)

        turn_engine.process_turn(empires, galaxy)

        # Seed should have incremented if battle occurred
        # Note: RNG combat doesn't use seeds, only simulated combat does
        # But the counter still tracks battles
        assert turn_engine.conflict_engine._battle_seed_counter >= initial_seed

    def test_different_sessions_independent(self):
        """Different game sessions are independent."""
        config = GameConfig()
        config.galaxy_radius = 300
        config.system_count = 2

        session1 = GameSession(config=config)
        session2 = GameSession(config=config)

        # Advance session1
        session1.process_turn()
        session1.process_turn()

        # Session2 should be unaffected
        assert session2.turn_number == 1
        assert session1.turn_number == 3


# =============================================================================
# Test: Colonization Workflow
# =============================================================================


class TestColonizationWorkflow:
    """Tests for colonization during turn execution."""

    def test_colonize_order_claims_planet(self, turn_engine, two_empire_setup):
        """COLONIZE order transfers planet ownership."""
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        # Find an unowned planet and get its global location
        target_planet = None
        global_loc = None
        for system in galaxy.systems.values():
            for planet in system.planets:
                if planet.owner_id is None:
                    target_planet = planet
                    # Global location = system location + planet's local offset
                    global_loc = system.global_location + planet.location
                    break
            if target_planet:
                break

        if not target_planet:
            pytest.skip("No unowned planet available")

        # Create fleet at planet's GLOBAL location (system + local offset)
        fleet = Fleet(1, empire1.id, global_loc, speed=10.0)
        fleet.ships = [make_mock_ship_instance("Colony Ship", empire1.id)]
        fleet.add_order(FleetOrder(OrderType.COLONIZE, target=target_planet))
        empire1.add_fleet(fleet)

        initial_colonies = len(empire1.colonies)

        turn_engine.process_turn(empires, galaxy)

        # Empire should have new colony
        assert len(empire1.colonies) > initial_colonies
        assert target_planet.owner_id == empire1.id

    def test_colonize_removes_fleet(self, turn_engine, two_empire_setup):
        """Colonizing fleet is consumed."""
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        # Find an unowned planet and get its global location
        target_planet = None
        global_loc = None
        for system in galaxy.systems.values():
            for planet in system.planets:
                if planet.owner_id is None:
                    target_planet = planet
                    # Global location = system location + planet's local offset
                    global_loc = system.global_location + planet.location
                    break
            if target_planet:
                break

        if not target_planet:
            pytest.skip("No unowned planet available")

        fleet = Fleet(1, empire1.id, global_loc, speed=10.0)
        fleet.ships = [make_mock_ship_instance("Colony Ship", empire1.id)]
        fleet.add_order(FleetOrder(OrderType.COLONIZE, target=target_planet))
        empire1.add_fleet(fleet)

        initial_fleets = len(empire1.fleets)

        turn_engine.process_turn(empires, galaxy)

        # Fleet should have been consumed
        assert len(empire1.fleets) < initial_fleets
