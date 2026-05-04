"""
PROJ-332 — Characterization tests for `TurnEngine._reset_phase_times` and
`TurnEngine._time_phase`.

Pins:
- `_reset_phase_times` populates an exact 14-key float dict.
- `_time_phase` accumulates duration in the failure path (the `finally`-style
  dual-update) and wraps the original exception in `EnginePhaseError`.
- `_time_phase` re-raises a pre-existing `EnginePhaseError` without
  double-wrapping (the original exception object is propagated unchanged).

MIN-003 mocking note: timing assertions monkeypatch `time.perf_counter` to a
deterministic sequence so we can assert the accumulator value exactly, not
just `> 0`. Asserting `> 0` would mask regressions where the accumulator
stops working entirely.

Discipline: pure characterization — no production refactors.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.core.error_codes import ErrorCode
from game.core.exceptions import EnginePhaseError
from game.strategy.engine.turn_engine import TurnEngine


class TestResetPhaseTimes:
    """Pin the exact key set populated by `_reset_phase_times`."""

    def test_reset_phase_times_returns_dict_with_14_canonical_keys(
        self, fresh_registries
    ):
        """`_reset_phase_times` populates `_phase_times` with exactly 14
        canonical keys, all zero floats.

        OBSERVATION: production uses key 'harvesting' (not 'harvest'); the
        full set also includes 'planet_energy', 'planet_actions', and
        'activation_timers'. Pinning as observed.
        """
        engine = TurnEngine(registries=fresh_registries)

        # Force a re-reset to make sure this method (not just __init__)
        # is what's pinned.
        engine._phase_times['combat'] = 99.0
        engine._reset_phase_times()

        expected_keys = {
            'harvesting',
            'resources',
            'fuel_gen',
            'planet_energy',
            'resupply',
            'production',
            'environmental',
            'instant_orders',
            'actions',
            'planet_actions',
            'activation_timers',
            'movement_calc',
            'movement_apply',
            'combat',
        }
        assert set(engine._phase_times.keys()) == expected_keys
        assert len(engine._phase_times) == 14
        assert all(v == 0.0 for v in engine._phase_times.values())
        assert all(isinstance(v, float) for v in engine._phase_times.values())


class TestTimePhase:
    """Pin `_time_phase` failure-path timing and exception-wrapping behavior."""

    def test_time_phase_accumulates_timing_in_finally_block_when_wrapped_callable_raises(
        self, fresh_registries, monkeypatch
    ):
        """When the wrapped callable raises a non-EnginePhaseError, the
        elapsed delta is still accumulated to `_phase_times[key]` before
        the exception is wrapped and re-raised.

        Uses a deterministic `time.perf_counter` sequence [0.0, 2.5] so
        the accumulator value can be asserted exactly.
        """
        # Two-call sequence: t0=0.0, after-fn=2.5 → delta = 2.5.
        perf_values = iter([0.0, 2.5])
        # Patch where _time_phase reads it from: `time.perf_counter` in
        # the `time` module imported by turn_engine.
        import game.strategy.engine.turn_engine as turn_engine_mod
        monkeypatch.setattr(
            turn_engine_mod.time, 'perf_counter', lambda: next(perf_values)
        )

        engine = TurnEngine(registries=fresh_registries)
        # Sanity: combat starts at zero.
        assert engine._phase_times['combat'] == 0.0

        def raising_fn():
            raise RuntimeError("inner failure")

        with pytest.raises(EnginePhaseError) as exc_info:
            engine._time_phase('combat', raising_fn)

        # Pin the exact accumulated delta (not just > 0).
        assert engine._phase_times['combat'] == 2.5

        # Pin the wrapping shape: EnginePhaseError(...) from RuntimeError.
        assert exc_info.value.__cause__.__class__ is RuntimeError
        assert str(exc_info.value.__cause__) == "inner failure"
        # Pin the wrapped error code + context fields.
        assert exc_info.value.code == ErrorCode.PHASE_FAILED.value
        assert exc_info.value.context["phase_name"] == 'combat'
        assert exc_info.value.context["original_type"] == "RuntimeError"
        assert exc_info.value.context["original_error"] == "inner failure"

    def test_time_phase_reraises_preexisting_engine_phase_error_without_double_wrapping(
        self, fresh_registries
    ):
        """If the wrapped callable raises an EnginePhaseError directly
        (e.g. a nested phase already wrapped its own failure), `_time_phase`
        re-raises the SAME exception object. It must not wrap it again
        in another EnginePhaseError.
        """
        engine = TurnEngine(registries=fresh_registries)

        original_err = EnginePhaseError(
            "nested phase failure",
            code=ErrorCode.PHASE_FAILED.value,
            context={
                "phase_name": "nested",
                "tick": 42,
                "original_error": "inner",
                "original_type": "RuntimeError",
            },
        )

        def raising_fn():
            raise original_err

        with pytest.raises(EnginePhaseError) as exc_info:
            engine._time_phase('combat', raising_fn)

        # Identity check: the propagated exception IS the original — no
        # second EnginePhaseError wrapping it.
        assert exc_info.value is original_err
        # And, by extension, no spurious __cause__ chain has been added by
        # _time_phase itself (whatever __cause__ was on `original_err`
        # remains, but it must not be a new EnginePhaseError).
        assert not isinstance(exc_info.value.__cause__, EnginePhaseError)
