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
)
from tests.unit.strategy.turn_engine.test_default_tick_phase_list import (
    GOLDEN_PHASE_ORDER,
)


def _get_movement_calc_post_hook(engine=None):
    """Return the bound ``movement_calc`` post-exec hook.

    PROJ-428: hooks may live either on the registry module (pre-refactor)
    or on a TurnEngine collaborator (post-refactor). The lookup walks
    DEFAULT_TICK_PHASE_LIST so the characterization tests survive the
    relocation.
    """
    for phase in DEFAULT_TICK_PHASE_LIST:
        if phase.phase_key == 'movement_calc':
            return phase.post_exec_hook
    raise AssertionError("movement_calc phase missing from registry")


def _get_movement_apply_post_hook():
    for phase in DEFAULT_TICK_PHASE_LIST:
        if phase.phase_key == 'movement_apply':
            return phase.post_exec_hook
    raise AssertionError("movement_apply phase missing from registry")


def _get_env_post_hook():
    for phase in DEFAULT_TICK_PHASE_LIST:
        if phase.phase_key == 'environmental':
            return phase.post_exec_hook
    raise AssertionError("environmental phase missing from registry")


def _engine_stub_for_movement(_registries=None):
    """SimpleNamespace stub exposing the movement collaborator surface
    that the descriptor hooks resolve through (PROJ-428 Phase 3).
    """
    from game.strategy.engine.movement_phase_collaborator import (
        MovementPhaseCollaborator,
    )

    return SimpleNamespace(
        _registries=_registries,
        _movement_phase_collaborator=MovementPhaseCollaborator(),
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

        hook = _get_movement_calc_post_hook()
        hook(_engine_stub_for_movement(), ctx, move_queue)

        assert ctx.move_queue is move_queue
        assert ctx.pre_movement_locations == {1: 'A', 2: 'B'}

    def test_derive_moved_fleet_ids_compares_pre_and_post_locations(self):
        fleet_a = SimpleNamespace(id=1, location='A')
        fleet_b = SimpleNamespace(id=2, location='B')
        ctx = TickContext(
            tick=20,
            empires=[SimpleNamespace(
                id=0, fleets=[fleet_a, fleet_b], _booster_dirty=False,
            )],
            galaxy=object(),
            pre_movement_locations={1: 'old-A', 2: 'B'},
        )

        hook = _get_movement_apply_post_hook()
        hook(_engine_stub_for_movement(), ctx, None)

        assert ctx.moved_fleet_ids == {1}

    def test_derive_moved_fleet_ids_threads_registries_to_minefield_resolver(self):
        """PROJ-FMS-B audit Fix 1: the minefield resolver must receive the
        engine's GameRegistries so strategic damage routes through the real
        DamageCalculator pipeline (shields + emissive armor + SRA) instead
        of the direct-HP fallback. Pre-fix, ``_derive_moved_fleet_ids``
        omitted ``registries=`` and every live mine hit silently bypassed
        shields.
        """
        captured: dict = {}

        # A fleet that "moved" so the hook tries the resolver branch.
        moved_fleet = SimpleNamespace(
            id=1,
            location='B',
            ships=[SimpleNamespace(instance_id="s1", is_alive=True)],
        )
        empire = SimpleNamespace(id=1, fleets=[moved_fleet], _booster_dirty=False)
        ctx = TickContext(
            tick=5,
            empires=[empire],
            galaxy=object(),
            pre_movement_locations={1: 'A'},
        )

        sentinel_registries = object()
        engine = _engine_stub_for_movement(_registries=sentinel_registries)

        from game.strategy.engine import minefield_resolver as _mr_mod

        class _CaptureResolver:
            def __init__(self, *args, **kwargs) -> None:
                pass

            def resolve_minefield_entry(self, **kwargs):
                captured.update(kwargs)
                return _mr_mod.MinefieldResolutionResult()

        original = _mr_mod.MinefieldResolver
        _mr_mod.MinefieldResolver = _CaptureResolver
        try:
            hook = _get_movement_apply_post_hook()
            hook(engine, ctx, None)
        finally:
            _mr_mod.MinefieldResolver = original

        assert captured, "Expected resolver to be invoked"
        assert captured.get("registries") is sentinel_registries, (
            "MinefieldResolver must be called with the engine's _registries "
            "so strategic mine damage uses the real damage pipeline."
        )


class TestPhase428Characterization:
    """PROJ-428 Phase 0: pin behavioral contracts before relocating hooks.

    These tests must remain green when the registry helpers move onto
    ``TurnEngine`` (Phase 2) or ``MovementPhaseCollaborator`` (Phase 3).
    They are robust to the post-exec hook callable's location: they look
    it up via ``DEFAULT_TICK_PHASE_LIST``'s descriptor binding.
    """

    def test_env_hook_accumulates_events_on_ctx(self, fresh_registries):
        from tests.fixtures.turn_engine import build_test_turn_engine

        engine = build_test_turn_engine(fresh_registries)
        ctx = TickContext(tick=3, empires=[], galaxy=object())
        hook = _get_env_post_hook()

        hook(engine, ctx, ['evt_a', 'evt_b'])
        hook(engine, ctx, ['evt_c'])

        assert ctx.last_environmental_events == ['evt_a', 'evt_b', 'evt_c']

    def test_env_hook_ignores_falsy_result(self, fresh_registries):
        from tests.fixtures.turn_engine import build_test_turn_engine

        engine = build_test_turn_engine(fresh_registries)
        ctx = TickContext(tick=3, empires=[], galaxy=object())
        hook = _get_env_post_hook()

        hook(engine, ctx, [])
        hook(engine, ctx, None)

        assert ctx.last_environmental_events == []

    def test_booster_dirty_flips_only_for_moved_empires(self):
        """Empire A's fleet moves; empire B's fleet stays put. Only A's
        ``_booster_dirty`` should flip."""
        fleet_a = SimpleNamespace(id=1, location='Y')  # moved
        fleet_b = SimpleNamespace(id=2, location='Z')  # stayed
        empire_a = SimpleNamespace(id=10, fleets=[fleet_a], _booster_dirty=False)
        empire_b = SimpleNamespace(id=20, fleets=[fleet_b], _booster_dirty=False)
        ctx = TickContext(
            tick=4,
            empires=[empire_a, empire_b],
            galaxy=object(),
            pre_movement_locations={1: 'X', 2: 'Z'},
        )

        hook = _get_movement_apply_post_hook()
        hook(_engine_stub_for_movement(), ctx, None)

        assert empire_a._booster_dirty is True
        assert empire_b._booster_dirty is False

    def test_fleets_emptied_by_minefield_damage_removed_from_empire(self):
        """A moved fleet whose ships are all destroyed by mines must be
        pruned from the owning empire's fleet list."""
        ship = SimpleNamespace(instance_id='s1', is_alive=True)
        moved_fleet = SimpleNamespace(
            id=42,
            location='B',
            ships=[ship],
        )
        empire = SimpleNamespace(
            id=7, fleets=[moved_fleet], _booster_dirty=False,
        )
        ctx = TickContext(
            tick=5,
            empires=[empire],
            galaxy=object(),
            pre_movement_locations={42: 'A'},
        )
        engine = _engine_stub_for_movement(_registries=object())

        from game.strategy.engine import minefield_resolver as _mr_mod

        class _DestroyAllResolver:
            def __init__(self, *args, **kwargs) -> None:
                pass

            def resolve_minefield_entry(self, **kwargs):
                # Destroy every ship in the entering fleet.
                fleet = kwargs['fleet']
                result = _mr_mod.MinefieldResolutionResult()
                result.destroyed_ship_ids = [s.instance_id for s in fleet.ships]
                return result

        original = _mr_mod.MinefieldResolver
        _mr_mod.MinefieldResolver = _DestroyAllResolver
        try:
            hook = _get_movement_apply_post_hook()
            hook(engine, ctx, None)
        finally:
            _mr_mod.MinefieldResolver = original

        # Fleet has no ships left → pruned from empire.
        assert moved_fleet.ships == []
        assert moved_fleet not in empire.fleets


class TestPhase428TurnEngineHookMethods:
    """PROJ-428 Phase 2: tick-1 logs and env-event accumulator are
    named methods on TurnEngine. The registry hooks resolve through
    these methods rather than module-level helpers.
    """

    def test_log_turn_start_tick_1_only_logs_on_tick_1(self, fresh_registries):
        from tests.fixtures.turn_engine import build_test_turn_engine

        engine = build_test_turn_engine(fresh_registries)
        empires = [SimpleNamespace(id=0)]

        from unittest.mock import patch

        ctx_one = TickContext(tick=1, empires=empires, galaxy=object())
        ctx_other = TickContext(tick=2, empires=empires, galaxy=object())
        with patch.object(engine, '_log_empire_state') as mock_log:
            engine._tick_phase_log_turn_start(ctx_one)
            engine._tick_phase_log_turn_start(ctx_other)

        assert mock_log.call_count == 1
        # Label must match the existing 'TURN START tick=1' contract.
        assert mock_log.call_args.args[1] == "TURN START tick=1"

    def test_log_after_construction_tick_1_only_logs_on_tick_1(
        self, fresh_registries,
    ):
        from tests.fixtures.turn_engine import build_test_turn_engine

        engine = build_test_turn_engine(fresh_registries)
        empires = [SimpleNamespace(id=0)]

        from unittest.mock import patch

        ctx_one = TickContext(tick=1, empires=empires, galaxy=object())
        ctx_other = TickContext(tick=2, empires=empires, galaxy=object())
        with patch.object(engine, '_log_empire_state') as mock_log:
            engine._tick_phase_log_after_construction(ctx_one, None)
            engine._tick_phase_log_after_construction(ctx_other, None)

        assert mock_log.call_count == 1
        assert mock_log.call_args.args[1] == "Tick 1 AFTER CONSTRUCTION"

    def test_accumulate_env_events_appends_to_ctx(self, fresh_registries):
        from tests.fixtures.turn_engine import build_test_turn_engine

        engine = build_test_turn_engine(fresh_registries)
        ctx = TickContext(tick=3, empires=[], galaxy=object())

        engine._tick_phase_accumulate_env_events(ctx, ['a', 'b'])
        engine._tick_phase_accumulate_env_events(ctx, [])
        engine._tick_phase_accumulate_env_events(ctx, ['c'])

        assert ctx.last_environmental_events == ['a', 'b', 'c']


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
