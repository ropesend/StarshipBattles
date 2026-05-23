"""Tests for ActionExecutionEngine - tick-based action order execution.

PROJ-187: Strategy Orders Tick-Based Action System.

ActionExecutionEngine processes action orders (COLONIZE, TRANSFER, superweapons)
over multiple ticks based on fleet speed and action_time from component abilities.
"""
import pytest
from unittest.mock import MagicMock, patch

from game.strategy.engine.action_execution_engine import (
    ActionExecutionEngine,
    ActionTickResult,
)
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.data.empire import Empire
from game.core.hex_math import HexCoord


# --- Helpers ---

def _make_empire(empire_id: int = 0) -> Empire:
    """Create a real Empire for testing."""
    return Empire(empire_id=empire_id, name="Test Empire", color=(255, 0, 0))


def _make_real_fleet(
    fleet_id: int = 100,
    owner_id: int = 0,
    speed: float = 5.0,
    location: HexCoord = None
) -> Fleet:
    """Create a Fleet for testing."""
    loc = location or HexCoord(0, 0)
    return Fleet(fleet_id=fleet_id, owner_id=owner_id, location=loc, speed=speed)


def _make_mock_order_processor():
    """Create a mock OrderProcessor."""
    processor = MagicMock()
    processor.execute_action_order.return_value = False  # Fleet not consumed
    return processor


def _make_mock_galaxy():
    """Create a mock Galaxy."""
    return MagicMock()


class StubActionTimeResolver:
    """Minimal :class:`ActionTimeResolver`-shaped stub.

    PROJ-491 Phase 3 / DI-2026-05-23-003: ``ActionExecutionEngine``
    already accepts an injectable ``action_time_resolver`` constructor
    parameter that ``_process_fleet_action_tick`` prefers over the static
    method (``game/strategy/engine/action_execution_engine.py:55-68`` +
    ``183-192``). This stub exposes the one method the engine reads —
    ``resolve_action_time(fleet, order, component_registry)`` — and
    returns a fixed value supplied at construction time, replacing the
    prior ``patch('...ActionTimeResolver.resolve_action_time', return_value=N)``
    static-method patch pattern.
    """

    def __init__(self, action_time: int):
        self._action_time = action_time

    def resolve_action_time(self, fleet, order, component_registry):
        return self._action_time


class TestActionTickInterval:
    """Test tick interval calculation based on fleet speed."""

    def test_speed_5_fleet_acts_every_20_ticks(self):
        """Speed 5 fleet should act on ticks 20, 40, 60, 80, 100."""
        processor = _make_mock_order_processor()
        engine = ActionExecutionEngine(processor)

        empire = _make_empire()
        fleet = _make_real_fleet(speed=5.0)
        fleet.add_order(Order(OrderType.COLONIZE, None))
        empire.fleets.append(fleet)

        galaxy = _make_mock_galaxy()

        # Should NOT act on tick 1
        results = engine.process_action_ticks([empire], galaxy, 1)
        assert len(results) == 0
        assert fleet.get_current_order().execution_progress == 0

        # Should act on tick 20
        results = engine.process_action_ticks([empire], galaxy, 20)
        assert len(results) == 1
        assert fleet.get_current_order().execution_progress == 1

    # PROJ-480 Task 1.28: parametrize on tick so each non-acting tick value
    # fails in isolation rather than the first failure short-circuiting.
    @pytest.mark.parametrize("tick", [1, 20, 50, 99])
    def test_speed_1_fleet_does_not_act_on_non_100_tick(self, tick):
        """Speed 1 fleet should NOT act on ticks before 100."""
        processor = _make_mock_order_processor()
        engine = ActionExecutionEngine(processor)

        empire = _make_empire()
        fleet = _make_real_fleet(speed=1.0)
        fleet.add_order(Order(OrderType.COLONIZE, None))
        empire.fleets.append(fleet)

        galaxy = _make_mock_galaxy()

        results = engine.process_action_ticks([empire], galaxy, tick)
        assert len(results) == 0

    def test_speed_1_fleet_acts_on_tick_100(self):
        """Speed 1 fleet acts on tick 100."""
        processor = _make_mock_order_processor()
        engine = ActionExecutionEngine(processor)

        empire = _make_empire()
        fleet = _make_real_fleet(speed=1.0)
        fleet.add_order(Order(OrderType.COLONIZE, None))
        empire.fleets.append(fleet)

        galaxy = _make_mock_galaxy()

        results = engine.process_action_ticks([empire], galaxy, 100)
        assert len(results) == 1
        assert fleet.get_current_order().execution_progress == 1

    def test_speed_0_fleet_is_skipped(self):
        """Speed 0 fleet should never act (immobile)."""
        processor = _make_mock_order_processor()
        engine = ActionExecutionEngine(processor)

        empire = _make_empire()
        fleet = _make_real_fleet(speed=0.0)
        fleet.add_order(Order(OrderType.COLONIZE, None))
        empire.fleets.append(fleet)

        galaxy = _make_mock_galaxy()

        # Should never act
        for tick in [1, 20, 50, 100]:
            results = engine.process_action_ticks([empire], galaxy, tick)
            assert len(results) == 0
        assert fleet.get_current_order().execution_progress == 0


class TestProgressAccumulation:
    """Test execution_progress accumulation over ticks."""

    def test_progress_accumulates_correctly(self):
        """Progress should increment each time fleet acts.

        PROJ-491 Phase 3 Task 3.2 (DI-2026-05-23-003): inject a stub
        ``ActionTimeResolver`` via the production DI seam instead of
        patching the static method.
        """
        processor = _make_mock_order_processor()
        engine = ActionExecutionEngine(
            processor,
            action_time_resolver=StubActionTimeResolver(action_time=3),
        )

        empire = _make_empire()
        fleet = _make_real_fleet(speed=5.0)  # Acts every 20 ticks
        fleet.add_order(Order(OrderType.COLONIZE, None))
        empire.fleets.append(fleet)

        galaxy = _make_mock_galaxy()

        # Tick 20: progress = 1
        engine.process_action_ticks([empire], galaxy, 20)
        assert fleet.get_current_order().execution_progress == 1

        # Tick 40: progress = 2
        engine.process_action_ticks([empire], galaxy, 40)
        assert fleet.get_current_order().execution_progress == 2

        # Tick 60: progress = 3 -> action completes
        results = engine.process_action_ticks([empire], galaxy, 60)
        assert len(results) == 1
        assert results[0].action_completed is True
        assert results[0].execution_progress == 3


class TestActionCompletion:
    """Test action completion when progress reaches action_time."""

    def test_action_time_1_completes_immediately(self):
        """Action with action_time=1 should complete on first tick."""
        processor = _make_mock_order_processor()
        engine = ActionExecutionEngine(processor)

        empire = _make_empire()
        fleet = _make_real_fleet(speed=5.0)
        fleet.add_order(Order(OrderType.TRANSFER, None))
        empire.fleets.append(fleet)

        galaxy = _make_mock_galaxy()

        # action_time=1 by default for TRANSFER
        results = engine.process_action_ticks([empire], galaxy, 20)

        assert len(results) == 1
        assert results[0].action_completed is True
        assert results[0].action_time == 1
        processor.execute_action_order.assert_called_once()

    def test_multi_tick_action_takes_correct_ticks(self):
        """Action with action_time=3 should take 3 action ticks.

        PROJ-491 Phase 3 Task 3.3 (DI-2026-05-23-003): inject the stub
        resolver via the production DI seam.
        """
        processor = _make_mock_order_processor()
        engine = ActionExecutionEngine(
            processor,
            action_time_resolver=StubActionTimeResolver(action_time=3),
        )

        empire = _make_empire()
        fleet = _make_real_fleet(speed=5.0)  # Acts every 20 ticks
        fleet.add_order(Order(OrderType.COLONIZE, None))
        empire.fleets.append(fleet)

        galaxy = _make_mock_galaxy()

        # Tick 20: progress 1/3 - not complete
        results = engine.process_action_ticks([empire], galaxy, 20)
        assert results[0].action_completed is False
        assert results[0].execution_progress == 1

        # Tick 40: progress 2/3 - not complete
        results = engine.process_action_ticks([empire], galaxy, 40)
        assert results[0].action_completed is False
        assert results[0].execution_progress == 2

        # Tick 60: progress 3/3 - complete!
        results = engine.process_action_ticks([empire], galaxy, 60)
        assert results[0].action_completed is True
        assert results[0].execution_progress == 3

    def test_speed_5_completes_action_time_1_on_tick_20(self):
        """Speed 5 fleet with action_time=1 should complete on tick 20."""
        processor = _make_mock_order_processor()
        engine = ActionExecutionEngine(processor)

        empire = _make_empire()
        fleet = _make_real_fleet(speed=5.0)
        fleet.add_order(Order(OrderType.TRANSFER, None))
        empire.fleets.append(fleet)

        galaxy = _make_mock_galaxy()

        # Should complete on tick 20
        results = engine.process_action_ticks([empire], galaxy, 20)
        assert len(results) == 1
        assert results[0].action_completed is True

    def test_speed_1_completes_action_time_1_on_tick_100(self):
        """Speed 1 fleet with action_time=1 should complete on tick 100."""
        processor = _make_mock_order_processor()
        engine = ActionExecutionEngine(processor)

        empire = _make_empire()
        fleet = _make_real_fleet(speed=1.0)
        fleet.add_order(Order(OrderType.TRANSFER, None))
        empire.fleets.append(fleet)

        galaxy = _make_mock_galaxy()

        # Should not complete before tick 100
        for tick in [1, 20, 50, 99]:
            results = engine.process_action_ticks([empire], galaxy, tick)
            assert len(results) == 0

        # Should complete on tick 100
        results = engine.process_action_ticks([empire], galaxy, 100)
        assert len(results) == 1
        assert results[0].action_completed is True


class TestOrderTypeFiltering:
    """Test that movement and BUILD orders are skipped."""

    @pytest.mark.parametrize("order_type", [
        OrderType.MOVE,
        OrderType.MOVE_TO_FLEET,
        OrderType.WARP,
    ])
    def test_movement_orders_skipped(self, order_type):
        """Movement orders should not be processed."""
        processor = _make_mock_order_processor()
        engine = ActionExecutionEngine(processor)

        empire = _make_empire()
        fleet = _make_real_fleet(speed=5.0)
        fleet.add_order(Order(order_type, HexCoord(1, 1)))
        empire.fleets.append(fleet)

        galaxy = _make_mock_galaxy()

        results = engine.process_action_ticks([empire], galaxy, 20)
        assert len(results) == 0
        assert fleet.get_current_order().execution_progress == 0

    def test_build_order_skipped(self):
        """BUILD orders should not be processed (handled by ProductionEngine)."""
        processor = _make_mock_order_processor()
        engine = ActionExecutionEngine(processor)

        empire = _make_empire()
        fleet = _make_real_fleet(speed=5.0)
        fleet.add_order(Order(OrderType.BUILD, None))
        fleet.construction_queue = [{"design_id": "test"}]  # Non-empty queue
        empire.fleets.append(fleet)

        galaxy = _make_mock_galaxy()

        results = engine.process_action_ticks([empire], galaxy, 20)
        assert len(results) == 0
        assert fleet.get_current_order().execution_progress == 0

    def test_build_order_auto_pops_when_queue_empty(self):
        """BUILD order should auto-pop when construction_queue is empty."""
        processor = _make_mock_order_processor()
        engine = ActionExecutionEngine(processor)

        empire = _make_empire()
        fleet = _make_real_fleet(speed=5.0)
        fleet.add_order(Order(OrderType.BUILD, None))
        fleet.construction_queue = []  # Empty queue
        empire.fleets.append(fleet)

        galaxy = _make_mock_galaxy()

        engine.process_action_ticks([empire], galaxy, 20)
        # BUILD order should be popped
        assert fleet.get_current_order() is None


class TestFleetConsumption:
    """Test handling of fleets consumed by actions."""

    def test_fleet_consumed_by_action(self):
        """Actions that consume the fleet should report fleet_consumed=True."""
        processor = _make_mock_order_processor()
        processor.execute_action_order.return_value = True  # Fleet consumed
        engine = ActionExecutionEngine(processor)

        empire = _make_empire()
        fleet = _make_real_fleet(speed=5.0)
        fleet.add_order(Order(OrderType.STELLERATE_STAR, None))
        empire.fleets.append(fleet)

        galaxy = _make_mock_galaxy()

        results = engine.process_action_ticks([empire], galaxy, 20)
        assert len(results) == 1
        assert results[0].fleet_consumed is True

    def test_iterating_over_fleet_copy(self):
        """Should iterate over a copy of fleets list to handle removals."""
        processor = _make_mock_order_processor()

        # Simulate fleet removal during iteration
        def remove_fleet_on_call(fleet, empire, galaxy, component_registry, empires):
            empire.fleets.remove(fleet)
            return True

        processor.execute_action_order.side_effect = remove_fleet_on_call
        engine = ActionExecutionEngine(processor)

        empire = _make_empire()
        fleet1 = _make_real_fleet(fleet_id=101, speed=5.0)
        fleet1.add_order(Order(OrderType.COLONIZE, None))
        fleet2 = _make_real_fleet(fleet_id=102, speed=5.0)
        fleet2.add_order(Order(OrderType.COLONIZE, None))
        empire.fleets.extend([fleet1, fleet2])

        galaxy = _make_mock_galaxy()

        # Should not raise even though fleets are removed during iteration
        results = engine.process_action_ticks([empire], galaxy, 20)
        # Both fleets should have been processed
        assert len(results) == 2


class TestOrderPopping:
    """Test that orders are popped after completion."""

    def test_order_popped_after_completion(self):
        """Completed action should pop the order (via order processor)."""
        processor = _make_mock_order_processor()
        engine = ActionExecutionEngine(processor)

        empire = _make_empire()
        fleet = _make_real_fleet(speed=5.0)
        order = Order(OrderType.TRANSFER, None)
        fleet.add_order(order)
        empire.fleets.append(fleet)

        galaxy = _make_mock_galaxy()

        engine.process_action_ticks([empire], galaxy, 20)
        # Order processor should have been called to handle the order
        processor.execute_action_order.assert_called_once()

    def test_multi_order_chain(self):
        """After first action completes, second should become active."""
        processor = _make_mock_order_processor()

        # Simulate order processor popping the order only once
        call_count = [0]
        def pop_order_on_call(fleet, empire, galaxy, component_registry, empires):
            call_count[0] += 1
            if call_count[0] == 1:
                # First call: pop TRANSFER order
                fleet.pop_order()
            # Second call: don't pop (we want to check progress)
            return False

        processor.execute_action_order.side_effect = pop_order_on_call
        engine = ActionExecutionEngine(processor)

        empire = _make_empire()
        fleet = _make_real_fleet(speed=5.0)
        fleet.add_order(Order(OrderType.TRANSFER, None))
        fleet.add_order(Order(OrderType.COLONIZE, None))
        empire.fleets.append(fleet)

        galaxy = _make_mock_galaxy()

        # Complete first order
        engine.process_action_ticks([empire], galaxy, 20)

        # Second order should now be active
        current = fleet.get_current_order()
        assert current is not None
        assert current.type == OrderType.COLONIZE
        assert current.execution_progress == 0

        # Second order should start progressing on next tick
        # At tick 40, progress should be 1 (from 0), action_time=1, so action completes
        results = engine.process_action_ticks([empire], galaxy, 40)
        assert len(results) == 1
        # The action completes (progress=1, action_time=1), so processor is called
        assert results[0].action_completed is True
        assert results[0].order_type == OrderType.COLONIZE


class TestActionTickResult:
    """Test ActionTickResult dataclass."""

    def test_result_contains_correct_data(self):
        """ActionTickResult should capture all relevant data.

        PROJ-491 Phase 3 Task 3.4 (DI-2026-05-23-003): inject the stub
        resolver via the production DI seam.
        """
        processor = _make_mock_order_processor()
        engine = ActionExecutionEngine(
            processor,
            action_time_resolver=StubActionTimeResolver(action_time=2),
        )

        empire = _make_empire()
        fleet = _make_real_fleet(fleet_id=999, speed=5.0)
        fleet.add_order(Order(OrderType.COLONIZE, None))
        empire.fleets.append(fleet)

        galaxy = _make_mock_galaxy()

        results = engine.process_action_ticks([empire], galaxy, 20)

        assert len(results) == 1
        result = results[0]
        assert result.fleet_id == 999
        assert result.order_type == OrderType.COLONIZE
        assert result.action_completed is False
        assert result.fleet_consumed is False
        assert result.execution_progress == 1
        assert result.action_time == 2


class TestNoOrder:
    """Test handling of fleets with no orders."""

    def test_fleet_with_no_order_skipped(self):
        """Fleet with no current order should be skipped."""
        processor = _make_mock_order_processor()
        engine = ActionExecutionEngine(processor)

        empire = _make_empire()
        fleet = _make_real_fleet(speed=5.0)
        # No orders added
        empire.fleets.append(fleet)

        galaxy = _make_mock_galaxy()

        results = engine.process_action_ticks([empire], galaxy, 20)
        assert len(results) == 0


class TestMultipleEmpires:
    """Test processing multiple empires."""

    def test_processes_all_empires(self):
        """Should process fleets from all empires."""
        processor = _make_mock_order_processor()
        engine = ActionExecutionEngine(processor)

        empire1 = _make_empire(empire_id=0)
        empire2 = _make_empire(empire_id=1)

        fleet1 = _make_real_fleet(fleet_id=101, owner_id=0, speed=5.0)
        fleet1.add_order(Order(OrderType.TRANSFER, None))
        empire1.fleets.append(fleet1)

        fleet2 = _make_real_fleet(fleet_id=102, owner_id=1, speed=5.0)
        fleet2.add_order(Order(OrderType.TRANSFER, None))
        empire2.fleets.append(fleet2)

        galaxy = _make_mock_galaxy()

        results = engine.process_action_ticks([empire1, empire2], galaxy, 20)
        assert len(results) == 2


class TestAllActionOrderTypes:
    """Test that all action order types are processed."""

    # PROJ-207 EP-001: JOIN_FLEET removed - now handled by instant path only
    @pytest.mark.parametrize("order_type", [
        OrderType.COLONIZE,
        OrderType.TRANSFER,
        OrderType.LOAD_POPULATION,
        OrderType.UNLOAD_POPULATION,
        OrderType.IMPLODE_PLANET,
        OrderType.STELLERATE_STAR,
        OrderType.OPEN_WARP_POINT,
        OrderType.CLOSE_WARP_POINT,
        OrderType.CREATE_DYSON_SPHERE,
        OrderType.SELF_DESTRUCT,
    ])
    def test_action_order_type_processed(self, order_type):
        """All ACTION_ORDER_TYPES should be processed."""
        processor = _make_mock_order_processor()
        engine = ActionExecutionEngine(processor)

        empire = _make_empire()
        fleet = _make_real_fleet(speed=5.0)
        fleet.add_order(Order(order_type, None))
        empire.fleets.append(fleet)

        galaxy = _make_mock_galaxy()

        results = engine.process_action_ticks([empire], galaxy, 20)
        assert len(results) == 1
        assert results[0].order_type == order_type
