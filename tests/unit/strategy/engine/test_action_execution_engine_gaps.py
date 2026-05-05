"""Gap-fill characterization tests for ActionExecutionEngine (PROJ-341 §3).

Pins behaviors the existing `test_action_execution_engine.py` does NOT cover:
- `_validate_tick_inputs` happy + unhappy paths (PROJ-251).
- `ActionTimeResolver`-injection constructor wiring — PROJ-351 T6.3:
  the engine now consumes the injected resolver instance when one is
  supplied, and falls back to the static class method otherwise.
- Order-popping responsibility belongs to the processor (OBS-007).
- `_execute_action` kwarg threading.
- Iteration safety with multiple consumed fleets per empire.
"""
import pytest
from unittest.mock import MagicMock, patch

from game.core.exceptions import ValidationException
from game.core.hex_math import HexCoord
from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.action_execution_engine import (
    ActionExecutionEngine,
)


# ---------------------------------------------------------------------------
# Helpers (copied per D-007 — kept self-contained for PROJ-341)
# ---------------------------------------------------------------------------


def _make_empire(empire_id: int = 0) -> Empire:
    return Empire(empire_id=empire_id, name="Test Empire", color=(255, 0, 0))


def _make_fleet(
    *,
    fleet_id: int = 100,
    owner_id: int = 0,
    speed: float = 5.0,
    location=None,
) -> Fleet:
    loc = location if location is not None else HexCoord(0, 0)
    return Fleet(fleet_id=fleet_id, owner_id=owner_id, location=loc, speed=speed)


def _make_processor(*, returns_consumed: bool = False):
    proc = MagicMock()
    proc.execute_action_order.return_value = returns_consumed
    return proc


def _make_galaxy():
    return MagicMock()


# ---------------------------------------------------------------------------
# §3.1 _validate_tick_inputs
# ---------------------------------------------------------------------------


class TestValidateTickInputs:
    """PROJ-251 precondition guard."""

    def test_validate_tick_inputs_raises_validation_exception_when_fleet_location_is_none(self):
        proc = _make_processor()
        engine = ActionExecutionEngine(proc)

        empire = _make_empire(empire_id=42)
        fleet = _make_fleet(speed=5.0, location=HexCoord(0, 0))
        fleet.add_order(Order(OrderType.COLONIZE, None))
        # Force None location AFTER construction (constructor requires HexCoord).
        fleet.location = None
        empire.fleets.append(fleet)

        with pytest.raises(ValidationException) as exc_info:
            engine.process_action_ticks([empire], _make_galaxy(), 20)

        ctx = exc_info.value.context
        assert ctx.get("empire_id") == 42
        assert ctx.get("fleet_id") == fleet.id
        # Validation runs before any progress mutation.
        assert fleet.get_current_order().execution_progress == 0
        proc.execute_action_order.assert_not_called()

    def test_validate_tick_inputs_does_not_raise_for_valid_empires(self):
        proc = _make_processor()
        engine = ActionExecutionEngine(proc)

        empire = _make_empire()
        fleet = _make_fleet(speed=5.0)
        fleet.add_order(Order(OrderType.COLONIZE, None))
        empire.fleets.append(fleet)

        # Direct call: should not raise.
        assert engine._validate_tick_inputs([empire]) is None

    def test_process_action_ticks_does_not_mutate_state_when_validate_raises(self):
        """Validate runs BEFORE any iteration. Two empires; the second has a
        None-location fleet. Assert the first empire's fleet did not have
        execution_progress incremented."""
        proc = _make_processor()
        engine = ActionExecutionEngine(proc)

        empire1 = _make_empire(empire_id=0)
        fleet1 = _make_fleet(fleet_id=101, speed=5.0)
        fleet1.add_order(Order(OrderType.COLONIZE, None))
        empire1.fleets.append(fleet1)

        empire2 = _make_empire(empire_id=1)
        fleet2 = _make_fleet(fleet_id=102, speed=5.0)
        fleet2.add_order(Order(OrderType.COLONIZE, None))
        fleet2.location = None  # Triggers raise
        empire2.fleets.append(fleet2)

        with pytest.raises(ValidationException):
            engine.process_action_ticks([empire1, empire2], _make_galaxy(), 20)

        # First empire's fleet should be untouched.
        assert fleet1.get_current_order().execution_progress == 0
        proc.execute_action_order.assert_not_called()


# ---------------------------------------------------------------------------
# §3.2 ActionTimeResolver-injection constructor path
# ---------------------------------------------------------------------------


class TestActionTimeResolverInjection:

    def test_engine_consults_injected_action_time_resolver(self):
        """PROJ-351 T6.3: when an `ActionTimeResolver` is injected, the engine
        consumes it via `self._action_time_resolver.resolve_action_time(...)`
        rather than calling the static class method.
        """
        proc = _make_processor()
        custom_resolver = MagicMock()
        custom_resolver.resolve_action_time.return_value = 2
        engine = ActionExecutionEngine(proc, action_time_resolver=custom_resolver)

        assert engine._action_time_resolver is custom_resolver

        empire = _make_empire()
        fleet = _make_fleet(speed=5.0)
        order = Order(OrderType.COLONIZE, None)
        fleet.add_order(order)
        empire.fleets.append(fleet)

        with patch(
            "game.strategy.engine.action_execution_engine."
            "ActionTimeResolver.resolve_action_time",
            return_value=99,
        ) as mock_static:
            engine.process_action_ticks([empire], _make_galaxy(), 20)

        # Injected instance IS consulted, with the engine's call signature.
        custom_resolver.resolve_action_time.assert_called_once_with(
            fleet, order, None
        )
        # Static path is NOT used when an instance is injected.
        mock_static.assert_not_called()

    def test_engine_falls_back_to_static_resolver_when_no_resolver_injected(self):
        """PROJ-351 T6.3: with `action_time_resolver=None` (the default), the
        engine falls back to the static `ActionTimeResolver.resolve_action_time`.
        """
        proc = _make_processor()
        engine = ActionExecutionEngine(proc)

        assert engine._action_time_resolver is None

        empire = _make_empire()
        fleet = _make_fleet(speed=5.0)
        fleet.add_order(Order(OrderType.COLONIZE, None))
        empire.fleets.append(fleet)

        with patch(
            "game.strategy.engine.action_execution_engine."
            "ActionTimeResolver.resolve_action_time",
            return_value=2,
        ) as mock_static:
            engine.process_action_ticks([empire], _make_galaxy(), 20)

        mock_static.assert_called_once()

    def test_engine_defaults_to_none_action_time_resolver_when_omitted(self):
        proc = _make_processor()
        engine = ActionExecutionEngine(proc)

        assert engine._action_time_resolver is None


# ---------------------------------------------------------------------------
# §3.3 Order-popping responsibility (OBS-007)
# ---------------------------------------------------------------------------


class TestOrderPoppingResponsibility:

    def test_engine_does_not_pop_order_when_action_completes(self):
        """OBS-007: the engine does NOT pop the order on completion. The
        injected processor is responsible. Use a processor that does NOT pop."""
        proc = _make_processor(returns_consumed=False)  # Does not pop

        engine = ActionExecutionEngine(proc)

        empire = _make_empire()
        fleet = _make_fleet(speed=5.0)
        original_order = Order(OrderType.TRANSFER, None)
        fleet.add_order(original_order)
        empire.fleets.append(fleet)

        # action_time=1 default for TRANSFER → completes on tick 20.
        results = engine.process_action_ticks([empire], _make_galaxy(), 20)
        assert len(results) == 1
        assert results[0].action_completed is True

        # Engine itself did not pop — the same Order instance is still current.
        current = fleet.get_current_order()
        assert current is original_order

    def test_engine_does_not_pop_order_for_in_progress_action(self):
        """When action_time > progress, engine returns in-progress result and
        does NOT call the processor (so processor cannot pop)."""
        proc = _make_processor(returns_consumed=False)
        engine = ActionExecutionEngine(proc)

        empire = _make_empire()
        fleet = _make_fleet(speed=5.0)
        order = Order(OrderType.COLONIZE, None)
        fleet.add_order(order)
        empire.fleets.append(fleet)

        with patch(
            "game.strategy.engine.action_execution_engine."
            "ActionTimeResolver.resolve_action_time",
            return_value=3,
        ):
            results = engine.process_action_ticks([empire], _make_galaxy(), 20)

        assert len(results) == 1
        assert results[0].action_completed is False
        assert results[0].execution_progress == 1
        # Processor was not called — completion didn't occur.
        proc.execute_action_order.assert_not_called()
        # Order still active.
        assert fleet.get_current_order() is order


# ---------------------------------------------------------------------------
# §3.4 _execute_action kwarg threading
# ---------------------------------------------------------------------------


class TestExecuteActionKwargThreading:

    def test_execute_action_forwards_component_registry_and_all_empires_to_processor(self):
        proc = _make_processor()
        engine = ActionExecutionEngine(proc)

        empire = _make_empire()
        fleet = _make_fleet(speed=5.0)
        fleet.add_order(Order(OrderType.TRANSFER, None))
        empire.fleets.append(fleet)

        sentinel_registry = {"sentinel": "registry"}
        other_empire = _make_empire(empire_id=99)
        all_empires_arg = [other_empire]

        engine.process_action_ticks(
            [empire],
            _make_galaxy(),
            20,
            component_registry=sentinel_registry,
            all_empires=all_empires_arg,
        )

        proc.execute_action_order.assert_called_once()
        call_kwargs = proc.execute_action_order.call_args.kwargs
        assert call_kwargs["component_registry"] is sentinel_registry
        assert call_kwargs["empires"] is all_empires_arg
        assert call_kwargs["fleet"] is fleet
        assert call_kwargs["empire"] is empire

    def test_execute_action_forwards_none_kwargs_when_caller_omits_them(self):
        proc = _make_processor()
        engine = ActionExecutionEngine(proc)

        empire = _make_empire()
        fleet = _make_fleet(speed=5.0)
        fleet.add_order(Order(OrderType.TRANSFER, None))
        empire.fleets.append(fleet)

        engine.process_action_ticks([empire], _make_galaxy(), 20)

        call_kwargs = proc.execute_action_order.call_args.kwargs
        assert call_kwargs["component_registry"] is None
        assert call_kwargs["empires"] is None


# ---------------------------------------------------------------------------
# §3.5 Iteration safety — multiple consumed fleets per empire
# ---------------------------------------------------------------------------


class TestMultipleConsumedFleetsIterationSafety:

    def test_process_action_ticks_handles_multiple_consumed_fleets_in_same_empire(self):
        """`list(empire.fleets)` copy at line 107 protects iteration when
        all three fleets are removed mid-loop."""
        def remove_and_consume(fleet, empire, galaxy, component_registry, empires):
            empire.fleets.remove(fleet)
            return True

        proc = MagicMock()
        proc.execute_action_order.side_effect = remove_and_consume
        engine = ActionExecutionEngine(proc)

        empire = _make_empire()
        fleets = []
        for i in range(3):
            f = _make_fleet(fleet_id=200 + i, speed=5.0)
            f.add_order(Order(OrderType.STELLERATE_STAR, None))
            empire.fleets.append(f)
            fleets.append(f)

        results = engine.process_action_ticks([empire], _make_galaxy(), 20)

        # All three processed — no IndexError / ValueError on the third.
        assert len(results) == 3
        assert all(r.fleet_consumed for r in results)
        assert empire.fleets == []
        seen_ids = {r.fleet_id for r in results}
        assert seen_ids == {200, 201, 202}
