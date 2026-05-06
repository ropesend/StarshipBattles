"""
Tests for turn processing structure and phases.

PROJ-187: Updated to reflect tick-based action processing.
Action orders (COLONIZE, TRANSFER, superweapons) are now processed via
ActionExecutionEngine in Phase 1.5 of each tick, not at end-of-turn.

This test file covers:
- Turn processing structure (100 ticks)
- Production processing delegation
- ActionExecutionEngine integration
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock

from game.strategy.engine.turn_engine import TurnEngine
from tests.fixtures.turn_engine import build_test_turn_engine
from game.strategy.data.order_types import Order, OrderType
from game.core.hex_math import HexCoord


# =============================================================================
# Test: Turn Processing Structure
# =============================================================================


class TestTurnProcessing:
    """Tests for process_turn method structure."""

    @patch.object(TurnEngine, '_process_tick')
    def test_process_turn_calls_subticks(self, mock_tick,
                                         turn_engine, mock_empire, mock_galaxy):
        """process_turn calls _process_tick 100 times."""
        mock_empire.fleets = []

        turn_engine.process_turn([mock_empire], mock_galaxy)

        assert mock_tick.call_count == 100

    def test_process_turn_calls_population_growth(self, turn_engine, mock_empire, mock_galaxy):
        """process_turn calls population growth at end of turn."""
        mock_empire.fleets = []
        mock_pop_engine = MagicMock()
        turn_engine._population_engine = mock_pop_engine

        turn_engine.process_turn([mock_empire], mock_galaxy)

        mock_pop_engine.process_population_growth.assert_called_once_with([mock_empire])


# =============================================================================
# Test: Tick Processing Phases
# =============================================================================


class TestTickProcessing:
    """Tests for _process_tick method phases."""

    def test_tick_calls_action_engine(self, turn_engine, mock_empire, mock_galaxy):
        """_process_tick calls ActionExecutionEngine.process_action_ticks."""
        mock_action_engine = MagicMock()
        turn_engine._action_engine = mock_action_engine
        mock_empire.fleets = []

        # Process one tick
        turn_engine._process_tick(50, [mock_empire], mock_galaxy)

        mock_action_engine.process_action_ticks.assert_called_once()

    def test_tick_calls_phases_in_order(self, turn_engine, mock_empire, mock_galaxy):
        """_process_tick calls phases in correct order."""
        # Track call order
        call_order = []

        def make_tracker(name, return_val=None):
            def tracker(*args, **kwargs):
                call_order.append(name)
                return return_val
            return tracker

        turn_engine._harvesting_engine = MagicMock()
        turn_engine._harvesting_engine.process_harvesting_tick = MagicMock(side_effect=make_tracker('harvest'))
        turn_engine._resource_engine = MagicMock()
        turn_engine._resource_engine.process_per_turn_consumption = MagicMock(side_effect=make_tracker('resource', []))
        turn_engine._resupply_engine = MagicMock()
        turn_engine._resupply_engine.process_fuel_generation = MagicMock(side_effect=make_tracker('fuel_gen', []))
        turn_engine._resupply_engine.process_fleet_resupply = MagicMock(side_effect=make_tracker('resupply', []))
        turn_engine._production_engine = MagicMock()
        turn_engine._production_engine.process_construction_tick = MagicMock(side_effect=make_tracker('construct'))
        turn_engine._order_processor = MagicMock()
        turn_engine._order_processor.process_instant_orders = MagicMock(side_effect=make_tracker('instant', []))
        turn_engine._action_engine = MagicMock()
        turn_engine._action_engine.process_action_ticks = MagicMock(side_effect=make_tracker('action', []))
        turn_engine._movement_engine = MagicMock()
        turn_engine._movement_engine.collect_movements = MagicMock(side_effect=make_tracker('collect', []))
        turn_engine._movement_engine.apply_movements = MagicMock(side_effect=make_tracker('apply', []))
        turn_engine._conflict_engine = MagicMock()
        turn_engine._conflict_engine.resolve_all_conflicts = MagicMock(side_effect=make_tracker('combat'))

        mock_empire.fleets = []

        turn_engine._process_tick(50, [mock_empire], mock_galaxy)

        # Verify phase order
        expected_order = [
            'harvest', 'resource', 'fuel_gen', 'resupply',
            'construct', 'instant', 'action', 'collect', 'apply', 'combat'
        ]
        assert call_order == expected_order


# =============================================================================
# Test: Action Engine Integration
# =============================================================================


class TestActionEngineIntegration:
    """Tests for ActionExecutionEngine integration in TurnEngine."""

    def test_action_engine_property_creates_default(self, turn_engine):
        """action_engine property lazily creates ActionExecutionEngine."""
        from game.strategy.engine.action_execution_engine import ActionExecutionEngine

        engine = turn_engine.action_engine

        assert isinstance(engine, ActionExecutionEngine)

    def test_action_engine_uses_injected(self, fresh_registries):
        """Injected action_engine is used instead of creating default."""
        mock_action_engine = MagicMock()

        turn_engine = build_test_turn_engine(fresh_registries, action_engine=mock_action_engine)

        assert turn_engine.action_engine is mock_action_engine

    def test_action_engine_receives_component_registry(self, turn_engine, mock_empire, mock_galaxy):
        """ActionExecutionEngine receives component_registry."""
        mock_action_engine = MagicMock()
        turn_engine._action_engine = mock_action_engine
        mock_empire.fleets = []

        turn_engine._process_tick(50, [mock_empire], mock_galaxy)

        # Check that component_registry was passed
        call_kwargs = mock_action_engine.process_action_ticks.call_args
        assert 'component_registry' in call_kwargs.kwargs

    def test_action_engine_receives_all_empires(self, turn_engine, mock_empire, mock_galaxy):
        """ActionExecutionEngine receives all_empires for superweapons."""
        mock_action_engine = MagicMock()
        turn_engine._action_engine = mock_action_engine
        mock_empire.fleets = []
        empires = [mock_empire]

        turn_engine._process_tick(50, empires, mock_galaxy)

        # Check that all_empires was passed
        call_kwargs = mock_action_engine.process_action_ticks.call_args
        assert call_kwargs.kwargs.get('all_empires') == empires
