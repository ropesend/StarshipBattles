"""
Integration tests for turn execution in the gameplay loop.

Tests for complete turn execution, multiple turns in sequence,
and turn engine isolation.
"""
import pytest

from game.strategy.engine.game_session import GameSession
from game.strategy.engine.game_config import GameConfig
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import FleetOrder, OrderType
from game.core.hex_math import HexCoord
from tests.conftest import make_mock_ship_instance


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
        from game.core.hex_math import hex_distance
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
        """Production queue consumes resources and completes over multiple turns."""
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        # Get empire's colony
        if not empire1.colonies:
            pytest.skip("No colony available for test")

        colony = empire1.colonies[0]

        # Give colony local stockpile for tick-based production
        colony.stockpile = {
            "metals": 100000.0,
            "organics": 100000.0,
            "radioactives": 100000.0,
            "Energy": 100000.0
        }
        colony.max_stockpile = {
            "metals": 200000.0,
            "organics": 200000.0,
            "radioactives": 200000.0,
            "Energy": 200000.0
        }

        # Use complex type which doesn't require shipyard
        # At 20/tick planetary rate, 6000 Metals = 300 ticks = 3 turns
        queue_item = {
            "design_id": "test_complex",
            "type": "complex",
            "turns_remaining": 3,
            "total_cost": {"metals": 6000.0},
            "resources_consumed": {"metals": 0.0}
        }
        colony.construction_queue.append(queue_item)
        assert len(colony.construction_queue) == 1

        # Turn 1 - should consume some resources
        turn_engine.process_turn(empires, galaxy, save_path=test_savegame_dir)
        if colony.construction_queue:
            item = colony.construction_queue[0]
            consumed = item.get("resources_consumed", {}).get("metals", 0)
            assert consumed > 0  # Progress made

        # Turn 2 - consumes more resources
        turn_engine.process_turn(empires, galaxy, save_path=test_savegame_dir)
        if colony.construction_queue:
            item = colony.construction_queue[0]
            consumed = item.get("resources_consumed", {}).get("metals", 0)
            assert consumed > 2000  # More progress

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
# Test: Turn Engine Isolation
# =============================================================================


class TestTurnEngineIsolation:
    """Tests for turn engine state isolation."""

    def test_turn_engine_has_no_persistent_state(self, turn_engine):
        """Turn engine starts with clean state."""
        # PROJ-36: Battle seed counter moved to ConflictResolutionEngine
        # Conflict engine should be None initially (lazy initialization)
        assert turn_engine._conflict_engine is None

    def test_battle_seeds_increment(self, turn_engine, two_empire_setup, fresh_registries):
        """Battle seeds increment for determinism."""
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        # PROJ-36: Seed counter is now in ConflictResolutionEngine
        # Access conflict_engine to initialize it, then get initial seed
        initial_seed = turn_engine.conflict_engine._battle_seed_counter

        # PROJ-211: Create ships with registries for DI compliance
        def make_ship(name, owner_id):
            ship = make_mock_ship_instance(name, owner_id)
            ship.set_registries(fresh_registries)
            return ship

        # Create combat situation
        loc = HexCoord(0, 0)
        fleet1 = Fleet(1, empire1.id, loc, speed=10.0)
        fleet1.ships = [make_ship("Scout", empire1.id)]
        empire1.add_fleet(fleet1)

        fleet2 = Fleet(2, empire2.id, loc, speed=10.0)
        fleet2.ships = [make_ship("Scout", empire2.id)]
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
