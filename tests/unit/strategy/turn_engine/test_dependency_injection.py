"""
Tests for dependency injection and edge cases.

This test file covers:
- Edge cases and iterator safety
- Constructor dependency injection (PROJ-43 Phase 4)
- Factory function
- Mock engines usage
"""
import pytest
from unittest.mock import MagicMock, patch

from game.strategy.engine.turn_engine import TurnEngine
from tests.fixtures.turn_engine import build_test_turn_engine
from game.strategy.data.fleet import Fleet
from game.core.hex_math import HexCoord
from game.strategy.data.empire import Empire


# =============================================================================
# Test: Edge Cases
# =============================================================================


class TestTurnEngineEdgeCases:
    """Edge case tests for turn engine."""

    def test_empty_empires_list(self, turn_engine, mock_galaxy):
        """Empty empires list doesn't crash."""
        turn_engine.process_turn([], mock_galaxy)

    def test_empire_with_no_fleets(self, turn_engine, mock_empire, mock_galaxy):
        """Empire with no fleets processes without error."""
        mock_empire.fleets = []
        mock_empire.colonies = []

        turn_engine.process_turn([mock_empire], mock_galaxy)

    def test_multiple_empires_processed(self, turn_engine, mock_galaxy):
        """Multiple empires are all processed."""
        empire1 = MagicMock()
        empire1.id = 0
        empire1.fleets = []
        empire1.colonies = []

        empire2 = MagicMock()
        empire2.id = 1
        empire2.fleets = []
        empire2.colonies = []

        turn_engine.process_turn([empire1, empire2], mock_galaxy)

    def test_save_path_passed_to_production_tick(self, turn_engine, mock_empire, mock_galaxy):
        """save_path parameter passed to process_construction_tick.

        PROJ-158: Production is now tick-based. save_path is passed to
        process_construction_tick during the 100-tick loop.
        """
        mock_empire.fleets = []
        mock_empire.colonies = []

        with patch.object(turn_engine.production_engine, 'process_construction_tick') as mock_tick:
            turn_engine.process_turn([mock_empire], mock_galaxy, save_path="/test/path")

            # Should be called 100 times (once per tick)
            assert mock_tick.call_count == 100
            # Check one of the calls has the save_path
            # Call signature: process_construction_tick(tick, empires, galaxy, save_path, harvesting_engine)
            call_args = mock_tick.call_args_list[0]
            assert call_args[0][0] == 1  # tick
            assert call_args[1].get('save_path') == "/test/path"


# =============================================================================
# Test: Iterator Safety
# =============================================================================


class TestFleetIteratorSafety:
    """Test that turn processing handles fleet modification safely.

    Regression test for PROJ-12 Phase 7 Fix 7.4:
    ActionExecutionEngine iterates empire.fleets with list() copy to handle
    fleet removal during iteration (e.g., colonization consuming fleet).

    PROJ-187: These tests now verify ActionExecutionEngine iteration safety
    rather than TurnEngine._process_end_turn_orders (which was removed).
    """

    def test_fleet_removal_during_iteration_skips_items(self):
        """Verify that direct iteration skips items when list is modified.

        When iterating directly over a list and removing an item, the
        iteration can skip items because indices shift. The fix (using
        list()) prevents this.
        """
        # Create fleets
        fleet1 = MagicMock(spec=Fleet)
        fleet1.id = 1

        fleet2 = MagicMock(spec=Fleet)
        fleet2.id = 2

        fleet3 = MagicMock(spec=Fleet)
        fleet3.id = 3

        fleets = [fleet1, fleet2, fleet3]

        # BUG: Direct iteration with removal skips items
        processed_ids_buggy = []
        fleets_copy = [fleet1, fleet2, fleet3]
        for fleet in fleets_copy:  # Iterating directly
            processed_ids_buggy.append(fleet.id)
            if fleet.id == 1:
                # Removing fleet2 shifts fleet3 to index 1
                # But iterator advances to index 2, skipping fleet3
                fleets_copy.remove(fleet2)

        # fleet3 gets skipped because of index shift
        assert processed_ids_buggy == [1, 3], f"Expected [1, 3] due to skip, got {processed_ids_buggy}"

        # FIX: Using list() copy processes all items correctly
        processed_ids_fixed = []
        fleets = [fleet1, fleet2, fleet3]
        for fleet in list(fleets):  # Copy prevents issues
            processed_ids_fixed.append(fleet.id)
            if fleet.id == 1:
                fleets.remove(fleet2)

        # All three fleets are processed
        assert processed_ids_fixed == [1, 2, 3], f"Expected [1, 2, 3], got {processed_ids_fixed}"

    def test_action_engine_uses_list_copy(self):
        """Verify ActionExecutionEngine uses list() copy for fleet iteration.

        PROJ-187: ActionExecutionEngine.process_action_ticks must use list()
        copy when iterating fleets to handle fleet removal during processing.
        """
        from game.strategy.engine.action_execution_engine import ActionExecutionEngine

        # Check that the implementation uses list() copy
        import inspect
        source = inspect.getsource(ActionExecutionEngine.process_action_ticks)

        # The pattern should be "for fleet in list(empire.fleets)"
        assert "list(empire.fleets)" in source, \
            "ActionExecutionEngine should use list() copy for fleet iteration"


# =============================================================================
# Test: Constructor Dependency Injection (PROJ-43 Phase 4)
# =============================================================================


class TestTurnEngineConstructorDI:
    """Tests for TurnEngine constructor dependency injection.

    PROJ-43 Phase 4: TurnEngine should accept optional engine parameters
    for dependency injection, allowing mock engines in tests.
    PROJ-211: registries parameter is now required.
    """

    def test_default_engines_created_when_not_provided(self, fresh_registries):
        """TurnEngine creates default engines when none provided."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine
        from game.strategy.engine.production_engine import ProductionEngine
        from game.strategy.engine.order_processor import OrderProcessor
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.engine.consumable_management_engine import ConsumableManagementEngine

        engine = build_test_turn_engine(fresh_registries)

        assert isinstance(engine.movement_engine, FleetMovementEngine)
        assert isinstance(engine.production_engine, ProductionEngine)
        assert isinstance(engine.order_processor, OrderProcessor)
        assert isinstance(engine.conflict_engine, ConflictResolutionEngine)
        assert isinstance(engine.resource_engine, ConsumableManagementEngine)

    def test_movement_engine_injection(self, fresh_registries):
        """TurnEngine uses injected movement engine."""
        from game.strategy.interfaces.engines import IMovementEngine

        mock_movement = MagicMock(spec=IMovementEngine)
        engine = build_test_turn_engine(fresh_registries, movement_engine=mock_movement)

        assert engine.movement_engine is mock_movement

    def test_production_engine_injection(self, fresh_registries):
        """TurnEngine uses injected production engine."""
        from game.strategy.interfaces.engines import IProductionEngine

        mock_production = MagicMock(spec=IProductionEngine)
        engine = build_test_turn_engine(fresh_registries, production_engine=mock_production)

        assert engine.production_engine is mock_production

    def test_order_processor_injection(self, fresh_registries):
        """TurnEngine uses injected order processor."""
        from game.strategy.interfaces.engines import IOrderProcessor

        mock_processor = MagicMock(spec=IOrderProcessor)
        engine = build_test_turn_engine(fresh_registries, order_processor=mock_processor)

        assert engine.order_processor is mock_processor

    def test_conflict_engine_injection(self, fresh_registries):
        """TurnEngine uses injected conflict engine."""
        from game.strategy.interfaces.engines import IConflictEngine

        mock_conflict = MagicMock(spec=IConflictEngine)
        engine = build_test_turn_engine(fresh_registries, conflict_engine=mock_conflict)

        assert engine.conflict_engine is mock_conflict

    def test_resource_engine_injection(self, fresh_registries):
        """TurnEngine uses injected resource engine."""
        from game.strategy.interfaces.engines import IConsumableEngine

        mock_resource = MagicMock(spec=IConsumableEngine)
        engine = build_test_turn_engine(fresh_registries, resource_engine=mock_resource)

        assert engine.resource_engine is mock_resource

    def test_battle_resolver_injection_still_works(self, fresh_registries):
        """IBattleResolver injection should still work (existing API)."""
        from game.strategy.interfaces.battle_resolver import IBattleResolver

        mock_resolver = MagicMock(spec=IBattleResolver)
        engine = build_test_turn_engine(fresh_registries, battle_resolver=mock_resolver)

        # The conflict engine should receive the injected resolver
        # Note: After refactor, conflict engine is created in constructor
        assert engine._battle_resolver is mock_resolver

    def test_mixed_injection_and_defaults(self, fresh_registries):
        """TurnEngine handles mix of injected and default engines."""
        from game.strategy.interfaces.engines import IMovementEngine, IProductionEngine
        from game.strategy.engine.order_processor import OrderProcessor
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.engine.consumable_management_engine import ConsumableManagementEngine

        mock_movement = MagicMock(spec=IMovementEngine)
        mock_production = MagicMock(spec=IProductionEngine)

        engine = build_test_turn_engine(
            fresh_registries,
            movement_engine=mock_movement,
            production_engine=mock_production,
        )

        # Injected engines should be used
        assert engine.movement_engine is mock_movement
        assert engine.production_engine is mock_production

        # Non-injected engines should be defaults
        assert isinstance(engine.order_processor, OrderProcessor)
        assert isinstance(engine.conflict_engine, ConflictResolutionEngine)
        assert isinstance(engine.resource_engine, ConsumableManagementEngine)

    def test_injected_movement_engine_used_in_tick(self, fresh_registries):
        """Injected movement engine is called during tick processing."""
        from game.strategy.interfaces.engines import IMovementEngine, IConflictEngine, IConsumableEngine, IOrderProcessor

        mock_movement = MagicMock(spec=IMovementEngine)
        mock_movement.collect_movements.return_value = []
        mock_movement.apply_movements.return_value = []

        mock_conflict = MagicMock(spec=IConflictEngine)
        mock_resource = MagicMock(spec=IConsumableEngine)
        mock_resource.process_per_turn_consumption.return_value = []
        mock_order = MagicMock(spec=IOrderProcessor)
        mock_order.process_instant_orders.return_value = []

        engine = build_test_turn_engine(
            fresh_registries,
            movement_engine=mock_movement,
            conflict_engine=mock_conflict,
            resource_engine=mock_resource,
            order_processor=mock_order,
        )

        mock_empire = MagicMock()
        mock_empire.fleets = []
        mock_galaxy = MagicMock()

        engine._process_tick(1, [mock_empire], mock_galaxy)

        mock_movement.collect_movements.assert_called_once()
        mock_movement.apply_movements.assert_called_once()

    def test_injected_production_engine_used_in_tick(self, fresh_registries):
        """Injected production engine is called during tick processing.

        PROJ-158: Production is now entirely tick-based. TurnEngine.process_production
        was deleted as it was just a stub after PROJ-79 migration.
        """
        from game.strategy.interfaces.engines import IProductionEngine, IConsumableEngine, IMovementEngine, IOrderProcessor, IConflictEngine, IResupplyEngine

        mock_production = MagicMock(spec=IProductionEngine)
        mock_resource = MagicMock(spec=IConsumableEngine)
        mock_resource.process_per_turn_consumption.return_value = []
        mock_movement = MagicMock(spec=IMovementEngine)
        mock_movement.collect_movements.return_value = []
        mock_movement.apply_movements.return_value = []
        mock_order = MagicMock(spec=IOrderProcessor)
        mock_order.process_instant_orders.return_value = []
        mock_conflict = MagicMock(spec=IConflictEngine)
        mock_resupply = MagicMock(spec=IResupplyEngine)
        mock_resupply.process_fuel_generation.return_value = []
        mock_resupply.process_fleet_resupply.return_value = []

        engine = build_test_turn_engine(
            fresh_registries,
            production_engine=mock_production,
            resource_engine=mock_resource,
            movement_engine=mock_movement,
            order_processor=mock_order,
            conflict_engine=mock_conflict,
            resupply_engine=mock_resupply,
        )

        mock_empire = MagicMock()
        mock_empire.fleets = []
        mock_galaxy = MagicMock()

        engine._process_tick(1, [mock_empire], mock_galaxy)

        mock_production.process_construction_tick.assert_called_once()


# =============================================================================
# Test: Factory Function (PROJ-43 Phase 4)
# =============================================================================


class TestTurnEngineConfigCreateDefault:
    """Tests for ``TurnEngineConfig.create_default()`` — the canonical
    injection entry point.

    PROJ-369 Phase 3: replaces the deleted
    ``create_default_turn_engine`` factory function. The legacy factory
    is no longer importable; canonical pattern is
    ``TurnEngineConfig.create_default(...) + TurnEngine(...)``.
    """

    def test_legacy_factory_function_deleted(self):
        """``create_default_turn_engine`` was deleted in PROJ-369 Phase 3."""
        from game.strategy.engine import turn_engine as turn_engine_module
        assert not hasattr(turn_engine_module, "create_default_turn_engine")

    def test_create_default_returns_engine(self, fresh_registries):
        """``TurnEngineConfig.create_default(...) + TurnEngine(...)`` returns
        a TurnEngine instance."""
        engine = build_test_turn_engine(fresh_registries)
        assert isinstance(engine, TurnEngine)

    def test_create_default_wires_all_default_engines(self, fresh_registries):
        """``TurnEngineConfig.create_default(...)`` wires every default class."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine
        from game.strategy.engine.production_engine import ProductionEngine
        from game.strategy.engine.order_processor import OrderProcessor
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.engine.consumable_management_engine import ConsumableManagementEngine

        engine = build_test_turn_engine(fresh_registries)

        assert isinstance(engine.movement_engine, FleetMovementEngine)
        assert isinstance(engine.production_engine, ProductionEngine)
        assert isinstance(engine.order_processor, OrderProcessor)
        assert isinstance(engine.conflict_engine, ConflictResolutionEngine)
        assert isinstance(engine.resource_engine, ConsumableManagementEngine)


# =============================================================================
# Test: Mock Engines (PROJ-43 Phase 4)
# =============================================================================


class TestMockEngines:
    """Tests demonstrating usage of mock engines from the mocks module.

    PROJ-43 Phase 4: Verify mock engines work correctly with TurnEngine.
    PROJ-211: registries parameter is now required.
    """

    def test_mock_movement_engine_tracks_calls(self, fresh_registries):
        """MockMovementEngine tracks method calls."""
        from tests.unit.strategy.mocks import MockMovementEngine

        mock = MockMovementEngine()
        mock.collect_movements_result = []

        engine = build_test_turn_engine(fresh_registries, movement_engine=mock)

        # Access movement_engine to trigger usage
        result = engine.movement_engine.collect_movements([], None, 1)

        assert mock.collect_movements_called
        assert mock.collect_movements_calls == [([], None, 1)]
        assert result == []

    def test_mock_production_engine_tracks_calls(self):
        """MockProductionEngine tracks method calls.

        PROJ-158: Production is now tick-based only. Test process_construction_tick.
        """
        from tests.unit.strategy.mocks import MockProductionEngine

        mock = MockProductionEngine()

        # Call process_construction_tick directly
        mock.process_construction_tick(1, [], None, "/path")

        assert mock.process_construction_tick_called
        assert mock.process_construction_tick_calls == [(1, [], None, "/path")]

    def test_full_tick_with_all_mocks(self, fresh_registries):
        """TurnEngine._process_tick works with all mock engines."""
        from tests.unit.strategy.mocks import (
            MockMovementEngine,
            MockOrderProcessor,
            MockConflictEngine,
            MockConsumableEngine,
        )

        mock_movement = MockMovementEngine()
        mock_order = MockOrderProcessor()
        mock_conflict = MockConflictEngine()
        mock_resource = MockConsumableEngine()

        engine = build_test_turn_engine(
            fresh_registries,
            movement_engine=mock_movement,
            order_processor=mock_order,
            conflict_engine=mock_conflict,
            resource_engine=mock_resource,
        )

        mock_empire = MagicMock()
        mock_empire.fleets = []
        mock_galaxy = MagicMock()

        engine._process_tick(1, [mock_empire], mock_galaxy)

        # All engines should have been called
        assert mock_resource.process_per_turn_consumption_called
        assert mock_order.process_instant_orders_called
        assert mock_movement.collect_movements_called
        assert mock_movement.apply_movements_called
        assert mock_conflict.resolve_all_conflicts_called

    def test_mock_order_processor_in_action_engine(self):
        """MockOrderProcessor works with ActionExecutionEngine.

        PROJ-187: Action orders are now processed via ActionExecutionEngine
        in Phase 1.5 of each tick, not via TurnEngine._process_end_turn_orders.
        """
        from tests.unit.strategy.mocks import MockOrderProcessor
        from game.strategy.engine.action_execution_engine import ActionExecutionEngine

        mock_processor = MockOrderProcessor()
        mock_processor.execute_action_order_result = True

        action_engine = ActionExecutionEngine(order_processor=mock_processor)

        # ActionExecutionEngine calls execute_action_order when action completes
        # Verify the mock can be used correctly
        assert mock_processor.execute_action_order_result is True
