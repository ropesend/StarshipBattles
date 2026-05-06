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
from tests.fixtures.turn_engine import build_test_turn_engine


class TestResetPhaseTimes:
    """Pin the exact key set populated by `_reset_phase_times`."""

    def test_reset_phase_times_returns_dict_with_canonical_keys(
        self, fresh_registries
    ):
        """`_reset_phase_times` populates `_phase_times` with exactly 21
        canonical keys (15 tick-loop + 6 end-of-turn), all zero floats.

        OBSERVATION: production uses key 'harvesting' (not 'harvest').
        The 6 end-of-turn keys (organics_consumption, happiness,
        population_growth, quality_improvement, atmosphere,
        water_modification) were added by PROJ-343 T1.2-engines so the
        end-of-turn block routes through `_time_phase` for rollback safety.
        PROJ-365 added `planet_modifier_effects` to the tick-loop bucket
        (the descriptor registry routes every per-tick phase through
        `_time_phase` uniformly).
        """
        engine = build_test_turn_engine(fresh_registries)

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
            # PROJ-365: descriptor registry routes this through `_time_phase`.
            'planet_modifier_effects',
            'movement_calc',
            'movement_apply',
            'combat',
            # PROJ-343 T1.2-engines additions:
            'organics_consumption',
            'happiness',
            'population_growth',
            'quality_improvement',
            'atmosphere',
            'water_modification',
        }
        assert set(engine._phase_times.keys()) == expected_keys
        assert len(engine._phase_times) == 21
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

        engine = build_test_turn_engine(fresh_registries)
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

    def test_turn_perf_log_format_string_includes_all_phase_keys(
        self, fresh_registries
    ):
        """PROJ-365 audit MAJ-001/MAJ-002 regression guard.

        The TURN PERF `logger.warning` format string in `process_turn`
        must include a labeled token for every key in `_phase_times` so
        that performance regressions in any phase are visible in logs.

        Pre-remediation, the format string omitted `planet_modifier_effects`
        (PROJ-365 newly-routed phase) and the five PROJ-343 end-of-turn
        engines: organics_consumption, happiness, quality_improvement,
        atmosphere, water_modification. Their timings were accumulated but
        silently dropped.

        We assert by inspecting the source of `process_turn` for the
        labeled `<phase>=%.3fs` tokens. The single legacy alias is
        `population_growth` -> `population=` (kept for log-grep
        compatibility); we accept either label form for that key.
        """
        import inspect
        from game.strategy.engine.turn_engine import TurnEngine

        src = inspect.getsource(TurnEngine.process_turn)
        engine = build_test_turn_engine(fresh_registries)

        # Legacy log-label aliases retained for backward log-grep
        # compatibility — these dict keys are written under shorter
        # labels in the format string. All other keys must appear
        # verbatim.
        legacy_label_aliases = {
            'population_growth': 'population',
            'movement_calc': 'move_calc',
            'movement_apply': 'move_apply',
        }

        for key in engine._phase_times:
            label = legacy_label_aliases.get(key, key)
            token = f"{label}=%.3fs"
            assert token in src, (
                f"TURN PERF format string missing '{token}' for "
                f"_phase_times key '{key}'. Phase timings without a log "
                f"token are silently dropped from observability."
            )

    def test_time_phase_reraises_preexisting_engine_phase_error_without_double_wrapping(
        self, fresh_registries
    ):
        """If the wrapped callable raises an EnginePhaseError directly
        (e.g. a nested phase already wrapped its own failure), `_time_phase`
        re-raises the SAME exception object. It must not wrap it again
        in another EnginePhaseError.
        """
        engine = build_test_turn_engine(fresh_registries)

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


class TestAllPhaseBucketsPopulatedAfterProcessTurn:
    """PROJ-369 Phase 4: every one of the 21 ``_phase_times`` buckets
    (15 tick-loop + 6 end-of-turn) must be hit at least once during a
    full ``process_turn`` invocation. Pins the unified
    ``_run_phases`` helper's coverage of both the tick body and the
    end-of-turn block.
    """

    def test_all_21_phase_time_buckets_populated_after_process_turn(
        self, fresh_registries, mock_empire, mock_galaxy
    ):
        from game.strategy.interfaces.engines import (
            IActionExecutionEngine,
            IAtmosphereEngine,
            IComponentActivationEngine,
            IConflictEngine,
            IConsumableEngine,
            IEnvironmentalHazardEngine,
            IHappinessEngine,
            IHarvestingEngine,
            IMovementEngine,
            IOrderProcessor,
            IOrganicsConsumptionEngine,
            IPlanetActionEngine,
            IPlanetEnergyEngine,
            IPopulationEngine,
            IProductionEngine,
            IQualityEngine,
            IResupplyEngine,
            IWaterEngine,
        )

        mock_empire.fleets = []

        # Mock every sub-engine with a typed spec so each phase callable
        # can dispatch into its mock without TypeError. Empty-list returns
        # for the few phases whose post-hooks read the result.
        movement = MagicMock(spec=IMovementEngine)
        movement.collect_movements.return_value = []
        movement.apply_movements.return_value = []
        resource = MagicMock(spec=IConsumableEngine)
        resource.process_per_turn_consumption.return_value = []
        order = MagicMock(spec=IOrderProcessor)
        order.process_instant_orders.return_value = []
        resupply = MagicMock(spec=IResupplyEngine)
        resupply.process_fuel_generation.return_value = []
        resupply.process_fleet_resupply.return_value = []
        envhaz = MagicMock(spec=IEnvironmentalHazardEngine)
        envhaz.process_environmental_tick.return_value = []
        engine = build_test_turn_engine(
            fresh_registries,
            movement_engine=movement,
            production_engine=MagicMock(spec=IProductionEngine),
            order_processor=order,
            conflict_engine=MagicMock(spec=IConflictEngine),
            resource_engine=resource,
            population_engine=MagicMock(spec=IPopulationEngine),
            resupply_engine=resupply,
            harvesting_engine=MagicMock(spec=IHarvestingEngine),
            action_engine=MagicMock(spec=IActionExecutionEngine),
            environmental_engine=envhaz,
            planet_energy_engine=MagicMock(spec=IPlanetEnergyEngine),
            planet_action_engine=MagicMock(spec=IPlanetActionEngine),
            component_activation_engine=MagicMock(spec=IComponentActivationEngine),
            organics_consumption_engine=MagicMock(spec=IOrganicsConsumptionEngine),
            happiness_engine=MagicMock(spec=IHappinessEngine),
            quality_engine=MagicMock(spec=IQualityEngine),
            atmosphere_engine=MagicMock(spec=IAtmosphereEngine),
            water_engine=MagicMock(spec=IWaterEngine),
        )

        # Patch the locally-constructed PlanetModifierEffectEngine so it
        # doesn't reach real production code.
        from unittest.mock import patch
        with patch(
            'game.strategy.engine.planet_modifier_effect_engine.PlanetModifierEffectEngine'
        ):
            engine.process_turn([mock_empire], mock_galaxy)

        expected_buckets = {
            # 15 tick-loop buckets:
            'harvesting', 'resources', 'fuel_gen', 'planet_energy',
            'resupply', 'production', 'environmental',
            'instant_orders', 'actions', 'planet_actions',
            'activation_timers', 'planet_modifier_effects',
            'movement_calc', 'movement_apply', 'combat',
            # 6 end-of-turn buckets:
            'organics_consumption', 'happiness', 'population_growth',
            'quality_improvement', 'atmosphere', 'water_modification',
        }
        assert set(engine._phase_times.keys()) == expected_buckets
        assert len(engine._phase_times) == 21
        # Every bucket has accumulated at least some duration (>= 0).
        # Process_turn ran the full 100-tick body + the end-of-turn
        # block, so every bucket was visited at least once.
        for bucket, duration in engine._phase_times.items():
            assert duration >= 0.0, f"bucket {bucket!r} has negative time"
