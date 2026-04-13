"""Shared spec-driven scenario runner for headless Combat Lab execution.

Extracted during PROJ-270 Phase 1.1 so that both
`combat_lab.services.test_execution_service.run_headless` and
`game.ui.screens.test_lab.test_executor._run_scenario_via_run_battle`
share a single implementation.

Each scenario is materialized via its `to_spec(...)` compiler and driven
through `run_battle(spec, ...)`. There is no legacy `scenario.setup(engine)`
fallback — that entry point is deleted by PROJ-270 Phase 1.3.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Any, Callable, Dict, Optional, Tuple

from combat_lab.runner import _role_from_instance_id, _snapshot_ship_state
from game.ai.ai_factory import AIControllerFactory
from game.simulation.battle_runner import run_battle


def run_scenario_via_run_battle(
    scenario: Any,
    *,
    seed_override: Optional[int] = None,
    pre_tick_loop_hook: Optional[Callable[[Any], None]] = None,
    per_tick_hook: Optional[Callable[[Any], None]] = None,
) -> Tuple[Any, Any]:
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
        `(engine, outcome)` — the engine captured from the pre-tick-loop
        callback (still needed by the PROJ-270 Phase 1 validator contract;
        Phase 2 migrates validators to consume the outcome), and the
        `BattleOutcome` produced by `run_battle`.
    """
    spec = scenario.to_spec(registries=None)
    if seed_override is not None and seed_override != spec.seed:
        spec = replace(spec, seed=seed_override)

    scenario.before_run_battle(spec)

    ships_by_role: Dict[str, Any] = {}
    initial_state_by_role: Dict[str, Any] = {}

    def ship_builder(ship_spec):
        ship = scenario._load_ship(ship_spec.design_id)
        role = _role_from_instance_id(ship_spec.instance_id)
        if role is not None:
            ships_by_role[role] = ship
            initial_state_by_role[role] = _snapshot_ship_state(ship)
        return ship

    engine_ref: Dict[str, Any] = {"engine": None}

    def pre_tick_loop(engine):
        engine_ref["engine"] = engine
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

    outcome = run_battle(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=ship_builder,
        pre_tick_loop_callback=pre_tick_loop,
        per_tick_callback=per_tick,
    )

    return engine_ref["engine"], outcome


__all__ = ["run_scenario_via_run_battle"]
