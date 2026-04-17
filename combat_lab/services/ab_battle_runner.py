"""First-class A/B battle runner for Combat Lab comparison scenarios.

Introduced by PROJ-277. Replaces the embedded `run_battle()` call inside
`ComparisonScenario._run_baseline_battle` + the `_baseline_*` attribute
stashing + the telemetry role-remapping hack. Instead, scenarios are
passive inputs: they describe two `BattleSpec` transformations (baseline
and variant), and the runner owns both executions.

Usage::

    runner = ABBattleRunner(ai_factory=AIControllerFactory())
    ab = runner.run(baseline_spec, variant_spec)
    results = scenario.validate(ab)

The runner calls `run_battle(spec, ...)` exactly twice in order
(baseline first, variant second) and packages both outcomes and
telemetry bundles into a single `ABBattleOutcome`.
"""
from __future__ import annotations

from typing import Any, Callable, Optional, Tuple

from combat_lab.scenarios.ab_outcome import ABBattleOutcome
from combat_lab.telemetry import CombatLabTelemetry
from game.simulation.battle_outcome import BattleOutcome
from game.simulation.battle_runner import run_battle
from game.simulation.battle_spec import BattleSpec


class ABBattleRunner:
    """Orchestrates two sequential `run_battle` calls for A/B comparison.

    The runner is STATELESS across `run()` invocations — each call produces
    a self-contained `ABBattleOutcome`. Callers pass any ship-building
    or per-tick role-tracking closures via the constructor; the runner
    forwards them identically to both runs so telemetry keys (roles)
    match across baseline and variant.
    """

    def __init__(
        self,
        *,
        ai_factory: Any,
        ship_builder: Optional[Callable[..., Any]] = None,
        pre_tick_loop_callback: Optional[Callable[[Any], None]] = None,
        per_tick_callback: Optional[Callable[[Any], None]] = None,
    ) -> None:
        self._ai_factory = ai_factory
        self._ship_builder = ship_builder
        self._pre_tick_loop_callback = pre_tick_loop_callback
        self._per_tick_callback = per_tick_callback

    def run(
        self,
        baseline_spec: BattleSpec,
        variant_spec: BattleSpec,
    ) -> ABBattleOutcome:
        """Run baseline then variant and return both paired outcomes.

        The two runs are independent — no state leaks between them. The
        baseline runs to completion (produces `baseline_outcome` +
        `baseline_telemetry`) before the variant starts.
        """
        baseline_outcome, baseline_telemetry = self._run_one(baseline_spec)
        variant_outcome, variant_telemetry = self._run_one(variant_spec)
        return ABBattleOutcome(
            baseline_outcome=baseline_outcome,
            baseline_telemetry=baseline_telemetry,
            variant_outcome=variant_outcome,
            variant_telemetry=variant_telemetry,
        )

    def _run_one(
        self,
        spec: BattleSpec,
    ) -> Tuple[BattleOutcome, CombatLabTelemetry]:
        """Execute a single `run_battle` and capture its telemetry.

        Private helper shared by `run()` for baseline + variant. Keeps
        one entry point for `per_tick_callback` / `ship_builder` wiring
        so the two runs follow identical plumbing.

        The stored callbacks (`ship_builder`, `pre_tick_loop_callback`,
        `per_tick_callback`) are forwarded verbatim. Telemetry capture
        (the role-keyed forensic bundle in `CombatLabTelemetry`) is
        the caller's responsibility — callers who need it install a
        `per_tick_callback` that populates their own role map and then
        build the `CombatLabTelemetry` outside this runner. For now
        `_run_one` returns an empty `CombatLabTelemetry`; Phase 3's
        integration with `ComparisonScenario` fills it in via a
        scenario-supplied ship_builder + per_tick pair that tracks
        `ships_by_role` / `in_flight_by_role`.
        """
        kwargs = {"ai_factory": self._ai_factory}
        if self._ship_builder is not None:
            kwargs["ship_builder"] = self._ship_builder
        if self._pre_tick_loop_callback is not None:
            kwargs["pre_tick_loop_callback"] = self._pre_tick_loop_callback
        if self._per_tick_callback is not None:
            kwargs["per_tick_callback"] = self._per_tick_callback

        outcome = run_battle(spec, **kwargs)
        return outcome, CombatLabTelemetry()


__all__ = ["ABBattleRunner"]
