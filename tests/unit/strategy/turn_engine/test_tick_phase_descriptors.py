"""
PROJ-365 Phase 2 — Unit tests for ``TickPhase``, ``TickContext``, and
``DEFAULT_TICK_PHASE_LIST`` defined in
``game/strategy/engine/turn_phase_registry.py``.

These tests pin the descriptor shape and the default registry's order /
key uniqueness. They run independently of TurnEngine — pure data-shape
characterization.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError
from types import SimpleNamespace

import pytest

from game.strategy.engine.turn_phase_registry import (
    DEFAULT_TICK_PHASE_LIST,
    TickContext,
    TickPhase,
    _capture_move_queue,
    _derive_moved_fleet_ids,
)
from tests.unit.strategy.turn_engine.test_default_tick_phase_list import (
    GOLDEN_PHASE_ORDER,
)


class TestTickPhaseShape:
    """Pin the ``TickPhase`` dataclass contract."""

    def test_tick_phase_is_frozen(self):
        phase = TickPhase(
            phase_key='x',
            callable_target=lambda e: lambda: None,
            args_resolver=lambda ctx: ((), {}),
        )
        with pytest.raises(FrozenInstanceError):
            phase.phase_key = 'y'  # type: ignore[misc]

    def test_tick_phase_defaults(self):
        phase = TickPhase(
            phase_key='x',
            callable_target=lambda e: lambda: None,
            args_resolver=lambda ctx: ((), {}),
        )
        assert phase.error_policy == 'wrap'
        assert phase.tick_gating is None
        assert phase.timing_bucket is None
        assert phase.post_exec_hook is None


class TestTickContextShape:
    """Pin the ``TickContext`` mutability contract."""

    def test_tick_context_is_mutable(self):
        ctx = TickContext(tick=1, empires=[], galaxy=object())
        ctx.tick = 5
        assert ctx.tick == 5
        ctx.moved_fleet_ids = {7}
        assert ctx.moved_fleet_ids == {7}

    def test_tick_context_default_factories_are_independent(self):
        ctx_a = TickContext(tick=1, empires=[], galaxy=object())
        ctx_b = TickContext(tick=1, empires=[], galaxy=object())
        ctx_a.last_environmental_events.append('a')
        # Mutating one must not leak into the other (default_factory check).
        assert ctx_b.last_environmental_events == []


class TestTickPhaseHooks:
    """Pin module-level hooks that move state between descriptor phases."""

    def test_capture_move_queue_stores_result_and_pre_locations(self):
        fleet_a = SimpleNamespace(id=1, location='A')
        fleet_b = SimpleNamespace(id=2, location='B')
        ctx = TickContext(
            tick=20,
            empires=[SimpleNamespace(fleets=[fleet_a, fleet_b])],
            galaxy=object(),
        )
        move_queue = [(fleet_a, 'C')]

        _capture_move_queue(None, ctx, move_queue)

        assert ctx.move_queue is move_queue
        assert ctx.pre_movement_locations == {1: 'A', 2: 'B'}

    def test_derive_moved_fleet_ids_compares_pre_and_post_locations(self):
        fleet_a = SimpleNamespace(id=1, location='A')
        fleet_b = SimpleNamespace(id=2, location='B')
        ctx = TickContext(
            tick=20,
            empires=[SimpleNamespace(fleets=[fleet_a, fleet_b])],
            galaxy=object(),
            pre_movement_locations={1: 'old-A', 2: 'B'},
        )

        _derive_moved_fleet_ids(None, ctx, None)

        assert ctx.moved_fleet_ids == {1}


class TestDefaultTickPhaseList:
    """Pin the default registry's ordering, count, and key uniqueness."""

    def test_default_phase_list_count_matches_golden(self):
        assert len(DEFAULT_TICK_PHASE_LIST) == len(GOLDEN_PHASE_ORDER)

    def test_default_phase_list_order_matches_golden(self):
        keys = [p.phase_key for p in DEFAULT_TICK_PHASE_LIST]
        assert keys == GOLDEN_PHASE_ORDER

    def test_phase_keys_unique(self):
        keys = [p.phase_key for p in DEFAULT_TICK_PHASE_LIST]
        assert len(keys) == len(set(keys))

    def test_default_list_is_tuple(self):
        # Tuple to prevent accidental mutation of the registry.
        assert isinstance(DEFAULT_TICK_PHASE_LIST, tuple)
