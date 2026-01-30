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
from game.strategy.data.fleet import Fleet
from game.strategy.data.hex_math import HexCoord
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

    def test_save_path_passed_to_production(self, turn_engine, mock_empire, mock_galaxy):
        """save_path parameter passed to production."""
        mock_empire.fleets = []
        mock_empire.colonies = []

        with patch.object(turn_engine, 'process_production') as mock_prod:
            turn_engine.process_turn([mock_empire], mock_galaxy, save_path="/test/path")

            mock_prod.assert_called_with([mock_empire], mock_galaxy, "/test/path")


# =============================================================================
# Test: Iterator Safety
# =============================================================================


class TestFleetIteratorSafety:
    """Test that turn processing handles fleet modification safely.

    Regression test for PROJ-12 Phase 7 Fix 7.4:
    Line 104 iterates empire.fleets directly while colonization may remove fleets.
    While Python doesn't always raise RuntimeError for list modification during
    iteration, removing items can cause skipped iterations (silent bugs).
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

    @patch.object(TurnEngine, '_process_tick')
    @patch.object(TurnEngine, 'process_production')
    def test_process_turn_processes_all_fleets_when_modified(
        self, mock_production, mock_tick
    ):
        """Verify process_turn processes all fleets even if list is modified.

        After the fix, all fleets should be processed even if some are removed
        during end-turn processing.
        """
        turn_engine = TurnEngine()

        mock_empire = MagicMock(spec=Empire)
        mock_empire.id = 0

        fleet1 = MagicMock(spec=Fleet)
        fleet1.id = 1
        fleet1.orders = []
        fleet1.get_current_order = MagicMock(return_value=None)

        fleet2 = MagicMock(spec=Fleet)
        fleet2.id = 2
        fleet2.orders = []
        fleet2.get_current_order = MagicMock(return_value=None)

        fleet3 = MagicMock(spec=Fleet)
        fleet3.id = 3
        fleet3.orders = []
        fleet3.get_current_order = MagicMock(return_value=None)

        mock_empire.fleets = [fleet1, fleet2, fleet3]
        mock_galaxy = MagicMock()
        mock_galaxy.systems = {}

        # Track which fleets get processed
        processed_fleets = []

        def track_and_remove(fleet, empire, galaxy):
            processed_fleets.append(fleet.id)
            # Simulate colonization removing fleet2 when processing fleet1
            if fleet.id == 1 and fleet2 in mock_empire.fleets:
                mock_empire.fleets.remove(fleet2)

        with patch.object(turn_engine, '_process_end_turn_orders', side_effect=track_and_remove):
            turn_engine.process_turn([mock_empire], mock_galaxy)

        # After the fix, all 3 fleets should be processed
        # Before the fix, fleet3 would be skipped
        assert len(processed_fleets) == 3, f"Expected 3 fleets processed, got {processed_fleets}"


# =============================================================================
# Test: Constructor Dependency Injection (PROJ-43 Phase 4)
# =============================================================================


class TestTurnEngineConstructorDI:
    """Tests for TurnEngine constructor dependency injection.

    PROJ-43 Phase 4: TurnEngine should accept optional engine parameters
    for dependency injection, allowing mock engines in tests.
    """

    def test_default_engines_created_when_not_provided(self):
        """TurnEngine creates default engines when none provided."""
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine
        from game.strategy.engine.production_engine import ProductionEngine
        from game.strategy.engine.fleet_order_processor import FleetOrderProcessor
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = TurnEngine()

        assert isinstance(engine.movement_engine, FleetMovementEngine)
        assert isinstance(engine.production_engine, ProductionEngine)
        assert isinstance(engine.order_processor, FleetOrderProcessor)
        assert isinstance(engine.conflict_engine, ConflictResolutionEngine)
        assert isinstance(engine.resource_engine, ResourceManagementEngine)

    def test_movement_engine_injection(self):
        """TurnEngine uses injected movement engine."""
        from game.strategy.interfaces.engines import IMovementEngine

        mock_movement = MagicMock(spec=IMovementEngine)
        engine = TurnEngine(movement_engine=mock_movement)

        assert engine.movement_engine is mock_movement

    def test_production_engine_injection(self):
        """TurnEngine uses injected production engine."""
        from game.strategy.interfaces.engines import IProductionEngine

        mock_production = MagicMock(spec=IProductionEngine)
        engine = TurnEngine(production_engine=mock_production)

        assert engine.production_engine is mock_production

    def test_order_processor_injection(self):
        """TurnEngine uses injected order processor."""
        from game.strategy.interfaces.engines import IOrderProcessor

        mock_processor = MagicMock(spec=IOrderProcessor)
        engine = TurnEngine(order_processor=mock_processor)

        assert engine.order_processor is mock_processor

    def test_conflict_engine_injection(self):
        """TurnEngine uses injected conflict engine."""
        from game.strategy.interfaces.engines import IConflictEngine

        mock_conflict = MagicMock(spec=IConflictEngine)
        engine = TurnEngine(conflict_engine=mock_conflict)

        assert engine.conflict_engine is mock_conflict

    def test_resource_engine_injection(self):
        """TurnEngine uses injected resource engine."""
        from game.strategy.interfaces.engines import IResourceEngine

        mock_resource = MagicMock(spec=IResourceEngine)
        engine = TurnEngine(resource_engine=mock_resource)

        assert engine.resource_engine is mock_resource

    def test_battle_resolver_injection_still_works(self):
        """IBattleResolver injection should still work (existing API)."""
        from game.strategy.interfaces.battle_resolver import IBattleResolver

        mock_resolver = MagicMock(spec=IBattleResolver)
        engine = TurnEngine(battle_resolver=mock_resolver)

        # The conflict engine should receive the injected resolver
        # Note: After refactor, conflict engine is created in constructor
        assert engine._battle_resolver is mock_resolver

    def test_mixed_injection_and_defaults(self):
        """TurnEngine handles mix of injected and default engines."""
        from game.strategy.interfaces.engines import IMovementEngine, IProductionEngine
        from game.strategy.engine.fleet_order_processor import FleetOrderProcessor
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        mock_movement = MagicMock(spec=IMovementEngine)
        mock_production = MagicMock(spec=IProductionEngine)

        engine = TurnEngine(
            movement_engine=mock_movement,
            production_engine=mock_production
        )

        # Injected engines should be used
        assert engine.movement_engine is mock_movement
        assert engine.production_engine is mock_production

        # Non-injected engines should be defaults
        assert isinstance(engine.order_processor, FleetOrderProcessor)
        assert isinstance(engine.conflict_engine, ConflictResolutionEngine)
        assert isinstance(engine.resource_engine, ResourceManagementEngine)

    def test_injected_movement_engine_used_in_tick(self):
        """Injected movement engine is called during tick processing."""
        from game.strategy.interfaces.engines import IMovementEngine, IConflictEngine, IResourceEngine, IOrderProcessor

        mock_movement = MagicMock(spec=IMovementEngine)
        mock_movement.collect_movements.return_value = []
        mock_movement.apply_movements.return_value = []

        mock_conflict = MagicMock(spec=IConflictEngine)
        mock_resource = MagicMock(spec=IResourceEngine)
        mock_resource.process_per_turn_consumption.return_value = []
        mock_order = MagicMock(spec=IOrderProcessor)
        mock_order.process_instant_orders.return_value = []

        engine = TurnEngine(
            movement_engine=mock_movement,
            conflict_engine=mock_conflict,
            resource_engine=mock_resource,
            order_processor=mock_order
        )

        mock_empire = MagicMock()
        mock_empire.fleets = []
        mock_galaxy = MagicMock()

        engine._process_tick(1, [mock_empire], mock_galaxy)

        mock_movement.collect_movements.assert_called_once()
        mock_movement.apply_movements.assert_called_once()

    def test_injected_production_engine_used_in_production(self):
        """Injected production engine is called during production processing."""
        from game.strategy.interfaces.engines import IProductionEngine

        mock_production = MagicMock(spec=IProductionEngine)

        engine = TurnEngine(production_engine=mock_production)

        mock_empire = MagicMock()
        mock_empire.colonies = []
        mock_galaxy = MagicMock()

        engine.process_production([mock_empire], mock_galaxy)

        mock_production.process_production.assert_called_once()


# =============================================================================
# Test: Factory Function (PROJ-43 Phase 4)
# =============================================================================


class TestTurnEngineFactory:
    """Tests for create_default_turn_engine factory function.

    PROJ-43 Phase 4: Factory function simplifies TurnEngine instantiation
    for production code while keeping constructor flexible for testing.
    """

    def test_factory_function_exists(self):
        """Factory function should be importable from turn_engine module."""
        from game.strategy.engine.turn_engine import create_default_turn_engine
        assert create_default_turn_engine is not None

    def test_factory_returns_turn_engine(self):
        """Factory should return a TurnEngine instance."""
        from game.strategy.engine.turn_engine import create_default_turn_engine

        engine = create_default_turn_engine()

        assert isinstance(engine, TurnEngine)

    def test_factory_creates_all_default_engines(self):
        """Factory should create TurnEngine with all default engines."""
        from game.strategy.engine.turn_engine import create_default_turn_engine
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine
        from game.strategy.engine.production_engine import ProductionEngine
        from game.strategy.engine.fleet_order_processor import FleetOrderProcessor
        from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
        from game.strategy.engine.resource_management_engine import ResourceManagementEngine

        engine = create_default_turn_engine()

        assert isinstance(engine.movement_engine, FleetMovementEngine)
        assert isinstance(engine.production_engine, ProductionEngine)
        assert isinstance(engine.order_processor, FleetOrderProcessor)
        assert isinstance(engine.conflict_engine, ConflictResolutionEngine)
        assert isinstance(engine.resource_engine, ResourceManagementEngine)


# =============================================================================
# Test: Mock Engines (PROJ-43 Phase 4)
# =============================================================================


class TestMockEngines:
    """Tests demonstrating usage of mock engines from the mocks module.

    PROJ-43 Phase 4: Verify mock engines work correctly with TurnEngine.
    """

    def test_mock_movement_engine_tracks_calls(self):
        """MockMovementEngine tracks method calls."""
        from tests.unit.strategy.mocks import MockMovementEngine

        mock = MockMovementEngine()
        mock.collect_movements_result = []

        engine = TurnEngine(movement_engine=mock)

        # Access movement_engine to trigger usage
        result = engine.movement_engine.collect_movements([], None, 1)

        assert mock.collect_movements_called
        assert mock.collect_movements_calls == [([], None, 1)]
        assert result == []

    def test_mock_production_engine_tracks_calls(self):
        """MockProductionEngine tracks method calls."""
        from tests.unit.strategy.mocks import MockProductionEngine

        mock = MockProductionEngine()

        engine = TurnEngine(production_engine=mock)
        engine.process_production([], None, "/path")

        assert mock.process_production_called
        assert mock.process_production_calls == [([], None, "/path")]

    def test_full_tick_with_all_mocks(self):
        """TurnEngine._process_tick works with all mock engines."""
        from tests.unit.strategy.mocks import (
            MockMovementEngine,
            MockOrderProcessor,
            MockConflictEngine,
            MockResourceEngine,
        )

        mock_movement = MockMovementEngine()
        mock_order = MockOrderProcessor()
        mock_conflict = MockConflictEngine()
        mock_resource = MockResourceEngine()

        engine = TurnEngine(
            movement_engine=mock_movement,
            order_processor=mock_order,
            conflict_engine=mock_conflict,
            resource_engine=mock_resource
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

    def test_mock_order_processor_in_end_turn(self):
        """MockOrderProcessor works in _process_end_turn_orders."""
        from tests.unit.strategy.mocks import MockOrderProcessor

        mock = MockOrderProcessor()
        mock.process_end_turn_orders_result = True

        engine = TurnEngine(order_processor=mock)

        mock_fleet = MagicMock()
        mock_empire = MagicMock()
        mock_galaxy = MagicMock()

        result = engine._process_end_turn_orders(mock_fleet, mock_empire, mock_galaxy)

        assert result is True
        assert mock.process_end_turn_orders_called
        assert mock.process_end_turn_orders_calls == [(mock_fleet, mock_empire, mock_galaxy)]
