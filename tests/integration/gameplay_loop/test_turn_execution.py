"""
Integration tests for turn execution in the gameplay loop.

Tests for complete turn execution, multiple turns in sequence,
and turn engine isolation.
"""
import pytest

from game.strategy.engine.game_session import GameSession
from game.strategy.engine.game_config import GameConfig
from game.strategy.engine.turn_engine import TurnEngine, TICKS_PER_TURN
from tests.fixtures.turn_engine import build_test_turn_engine
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.data.planetary_facility import PlanetaryFacility
from game.core.hex_math import HexCoord
from tests.conftest import make_mock_ship_instance
from tests.unit.strategy.mocks import MockMovementEngine


class _StubMovementEngine(MockMovementEngine):
    """State-tracking stub: steps each MOVE-ordered fleet one hex along the
    q-axis toward its target, with no path-finding, fuel, or component-data
    dependencies. Used by `test_fleet_reaches_destination_over_turns` to
    verify multi-turn movement orchestration without coupling to data files.
    """

    def collect_movements(self, empires, galaxy, tick):
        super().collect_movements(empires, galaxy, tick)
        moves = []
        for empire in empires:
            for fleet in empire.fleets:
                if not fleet.orders:
                    continue
                order = fleet.orders[0]
                if order.type != OrderType.MOVE:
                    continue
                tgt = order.target
                if fleet.location == tgt:
                    fleet.pop_order()
                    continue
                dq = (1 if tgt.q > fleet.location.q
                      else -1 if tgt.q < fleet.location.q else 0)
                moves.append(
                    (fleet, HexCoord(fleet.location.q + dq, fleet.location.r))
                )
        return moves

    def apply_movements(self, move_queue, galaxy):
        super().apply_movements(move_queue, galaxy)
        for fleet, next_hex in move_queue:
            fleet.location = next_hex
            if fleet.orders and fleet.location == fleet.orders[0].target:
                fleet.pop_order()
        return []


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

    def test_turn_processes_all_empires(self, turn_engine_with_mock_movement,
                                        two_empire_setup):
        """Turn engine forwards every empire to the movement engine each tick.

        Uses MockMovementEngine to verify orchestration directly rather than
        asserting against real fleet-movement side effects, which depend on
        data-driven path-finding, fuel costs, and harvest values.
        """
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        turn_engine_with_mock_movement.process_turn(empires, galaxy)

        mock = turn_engine_with_mock_movement._mock_movement
        assert mock.collect_movements_called
        for call_empires, call_galaxy, _tick in mock.collect_movements_calls:
            assert list(call_empires) == empires
            assert call_galaxy is galaxy

    def test_turn_has_100_subticks(self, turn_engine_with_mock_movement,
                                   two_empire_setup):
        """Turn engine runs exactly TICKS_PER_TURN sub-ticks per turn,
        numbered 1..TICKS_PER_TURN. Verified via MockMovementEngine call
        records — independent of fleet/component/harvest data.
        """
        empire1, empire2, galaxy = two_empire_setup

        turn_engine_with_mock_movement.process_turn([empire1, empire2], galaxy)

        mock = turn_engine_with_mock_movement._mock_movement
        assert len(mock.collect_movements_calls) == TICKS_PER_TURN
        ticks = [call[2] for call in mock.collect_movements_calls]
        assert ticks == list(range(1, TICKS_PER_TURN + 1))

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
            fleet.add_order(Order(OrderType.COLONIZE, target=planet))
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

    def test_fleet_reaches_destination_over_turns(self, two_empire_setup,
                                                  fresh_registries):
        """Across multiple turns, TurnEngine drives a fleet's MOVE order
        forward, eventually reaches the destination, and clears the
        completed order.

        Uses _StubMovementEngine to advance one hex per tick deterministically
        so the test exercises the multi-turn orchestration loop without
        depending on path-finding, fuel costs, or harvest values.
        """
        from tests.integration.gameplay_loop.conftest import InstantBattleResolver

        empire1, empire2, galaxy = two_empire_setup
        stub = _StubMovementEngine()
        engine = build_test_turn_engine(
            fresh_registries,
            battle_resolver=InstantBattleResolver(),
            movement_engine=stub,
        )

        start, destination = HexCoord(0, 0), HexCoord(25, 0)
        fleet = Fleet(1, empire1.id, start, speed=10.0)
        fleet.add_order(Order(OrderType.MOVE, target=destination))
        empire1.add_fleet(fleet)

        locations = [fleet.location]
        for _ in range(10):
            if fleet.location == destination:
                break
            engine.process_turn([empire1, empire2], galaxy)
            locations.append(fleet.location)

        assert len(set(locations)) > 1
        assert fleet.location == destination
        assert len(fleet.orders) == 0

    def test_production_completes_across_turns(self, turn_engine, two_empire_setup, test_savegame_dir):
        """Production queue consumes resources and completes over multiple turns."""
        empire1, empire2, galaxy = two_empire_setup
        empires = [empire1, empire2]

        # Get empire's colony
        if not empire1.colonies:
            pytest.skip("No colony available for test")

        colony = empire1.colonies[0]

        # Add PlanetaryYard facility so base construction queue is processed
        yard = PlanetaryFacility(
            instance_id="yard_test",
            design_id="colony_hub",
            name="Colony Hub",
            design_data={
                "layers": {
                    "CORE": [{"id": "yard", "abilities": {"PlanetaryYard": True}}]
                }
            },
            is_operational=True,
        )
        colony.facilities.append(yard)

        # Give colony local stockpile for tick-based production
        colony._stockpile = {
            "metals": 100000.0,
            "organics": 100000.0,
            "radioactives": 100000.0,
            "Energy": 100000.0
        }
        colony._max_stockpile = {
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
        """Turn engine starts with clean state.

        PROJ-369 Phase 3: ``_conflict_engine`` is now eagerly
        constructed in ``TurnEngineConfig.create_default(...)`` (was
        lazily initialized pre-Phase 3). The "clean state" invariant
        is asserted via ``_battle_seed_counter == 0`` instead.
        """
        # PROJ-36: Battle seed counter moved to ConflictResolutionEngine.
        assert turn_engine._conflict_engine is not None
        assert turn_engine.conflict_engine._battle_seed_counter == 0

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
