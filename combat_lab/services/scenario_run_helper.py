"""Shared spec-driven scenario runner for headless Combat Lab execution.

Extracted during PROJ-270 Phase 1.1 and extended in Phase 2.5 so that both
`combat_lab.services.test_execution_service.run_headless` and
`game.ui.screens.test_lab.test_executor._run_scenario_via_run_battle`
share a single implementation.

Each scenario is materialized via its `to_spec(...)` compiler and driven
through `run_battle(spec, ...)`. There is no legacy `scenario.setup(engine)`
fallback — that entry point is deleted by PROJ-270 Phase 1.3.

PROJ-270 Phase 2.5: the `engine_ref["engine"] = engine` closure trick that
used to escape the engine from `run_battle` for consumption by live-engine
validators is GONE. The helper now captures Combat-Lab-specific forensic
telemetry (`CombatLabTelemetry`) during the run and returns it alongside
the `BattleOutcome`. Validators consume `(outcome, telemetry)` only.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Any, Callable, Dict, Optional, Tuple

from combat_lab.runner import _snapshot_ship_state
from combat_lab.spec_compiler import build_test_battle_spec
from combat_lab.telemetry import CombatLabTelemetry
from game.ai.ai_factory import AIControllerFactory
from game.simulation.battle_outcome import BattleOutcome
from game.simulation.battle_runner import run_battle


def run_scenario_via_run_battle(
    scenario: Any,
    *,
    seed_override: Optional[int] = None,
    pre_tick_loop_hook: Optional[Callable[[Any], None]] = None,
    per_tick_hook: Optional[Callable[[Any], None]] = None,
) -> Tuple[BattleOutcome, CombatLabTelemetry]:
    """Drive a scenario through `run_battle(spec)` with role-keyed ships.

    Args:
        scenario: TestScenario-like instance exposing `to_spec`,
            `before_run_battle`, `wire_ships`, `custom_setup`, `update`,
            and `_load_ship`.
        seed_override: optional seed applied via `dataclasses.replace(spec, seed=...)`.
        pre_tick_loop_hook: additional one-shot hook fired after
            `wire_ships` + `custom_setup`. Used by the UI caller to
            attach `BattleStateCapture` manually.
        per_tick_hook: additional per-tick hook fired after
            `scenario.update(engine)`. Used by the UI caller to bridge
            rendering / progress updates.

    Returns:
        `(outcome, telemetry)` — the `BattleOutcome` produced by
        `run_battle`, and a `CombatLabTelemetry` bundle with forensic
        data (in-flight projectile counts by role) captured just before
        the engine was torn down. No engine reference is exposed —
        validators must consume outcome + telemetry only.
    """
    # PROJ-279: explicit composition — spec construction is the runner's
    # responsibility, not a method on the scenario object.
    spec = build_test_battle_spec(scenario, registries=None)
    if seed_override is not None and seed_override != spec.seed:
        spec = replace(spec, seed=seed_override)

    scenario.before_run_battle(spec)

    # PROJ-274: route materialization through the context materializer
    # (Combat Lab sets this to DesignOnlyMaterializer in TestExecutionService.__init__).
    # The closure keeps its role-tagging bookkeeping — that's orthogonal
    # to the ship-building pipeline and would otherwise need to be
    # replicated via post-hoc lookup on the outcome.
    # PROJ-306: pass `registry_provider` explicitly — Combat Lab services
    # are outside the Simulation layer and are allowed to call
    # `get_default_registry_provider()`.
    from game.core.registry import get_default_registry_provider
    from game.simulation.battle_runner import build_context_ship_builder
    ships_by_role: Dict[str, Any] = {}
    initial_state_by_role: Dict[str, Any] = {}
    _context_builder = build_context_ship_builder(
        registry_provider=get_default_registry_provider(),
    )

    def ship_builder(ship_spec, team_id):
        ship = _context_builder(ship_spec, team_id)
        # PROJ-278 Phase 4: read scenario_role field instead of parsing instance_id
        role = ship_spec.scenario_role
        if role is not None:
            ships_by_role[role] = ship
            initial_state_by_role[role] = _snapshot_ship_state(ship)
        return ship

    in_flight_by_role: Dict[str, int] = {}

    def pre_tick_loop(engine):
        scenario._effective_seed = spec.seed
        scenario.wire_ships(
            ships_by_role, engine=engine, initial_state=initial_state_by_role,
        )
        scenario.custom_setup(engine)
        if pre_tick_loop_hook is not None:
            pre_tick_loop_hook(engine)

    def per_tick(engine):
        scenario.update(engine)
        if per_tick_hook is not None:
            per_tick_hook(engine)
        # Capture in-flight projectile counts each tick; only the final
        # tick's snapshot is kept (overwrites per-role entries). This is
        # cheap (N ships * M projectiles is tiny) and avoids needing a
        # post-run engine reference.
        for role, ship in ships_by_role.items():
            in_flight_by_role[role] = sum(
                1 for p in engine.projectiles
                if p.is_alive and p.owner is ship
            )

    outcome = run_battle(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=ship_builder,
        pre_tick_loop_callback=pre_tick_loop,
        per_tick_callback=per_tick,
    )

    telemetry = CombatLabTelemetry(in_flight_by_role=dict(in_flight_by_role))
    return outcome, telemetry


__all__ = ["run_scenario_via_run_battle"]
