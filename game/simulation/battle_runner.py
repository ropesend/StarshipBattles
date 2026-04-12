"""`run_battle(spec) -> BattleOutcome` — unified battle simulator entry.

Introduced by PROJ-269 Phase 1 Task 1.6. The single entry into the
simulator. All three contexts (Combat Lab, Battle Setup, Strategy) build
a `BattleSpec` via their own compiler and hand it here. The engine is
context-blind.

Phase 1 scope:
  - Boundary, modifier_stack, telemetry_level are accepted on the spec
    but not yet enforced. Phase 3 wires boundary; Phase 5 wires telemetry
    subscribers; Phase 5 + engine hooks wire the ModifierStack.
  - Per-component HP from `ComponentStateSpec` is NOT yet routed into
    Ship construction. Phase 2 wires `Ship.from_spec` / bridge through
    `ShipInstance.components`.
  - Ship materialization is delegated to an injected `ship_builder`
    callable — Phase-1 transitional contract. Each compiler in Tasks
    1.7-1.9 supplies the builder most appropriate for its inputs.

What IS enforced in Phase 1:
  - spec → engine: teams added in order, `team_id` matches spec
  - end_condition / absolute_max_ticks forwarded to the engine
  - seed forwarded (deterministic RNG)
  - per_tick_callback called each tick with the engine
  - post_battle_hook called once with the final outcome
  - outcome is a `BattleOutcome` with:
      - teams in input order
      - every ShipSpec.instance_id has exactly one ShipOutcome
      - `end_reason` derived from the end-condition type that fired
      - `seed` echoed
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable, Dict, List, Optional

from game.core.math import Vector2
from game.simulation.battle_config import BattleConfig, BattleMode
from game.simulation.battle_controller import BattleController
from game.simulation.battle_outcome import (
    BattleOutcome,
    EndReason,
    ShipOutcome,
    ShipStats,
    ShipStatus,
    TaskForceOutcome,
    TeamOutcome,
    WeaponSummary,
)
from game.simulation.battle_spec import BattleSpec, ComponentStateSpec, ShipSpec
from game.simulation.systems.battle_end_conditions import (
    AllCondition,
    AnyCondition,
    EscapeCondition,
    MassRatioCondition,
    NeverCondition,
    ShipDestroyedCondition,
    TeamEliminatedCondition,
    TeamIncapacitatedCondition,
    TickLimitCondition,
)

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.simulation.interfaces.ai_controller import IAIControllerFactory
    from game.simulation.systems.battle_engine import BattleEngine

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# End-condition class → EndReason mapping
# ---------------------------------------------------------------------------
# Composite conditions (Any/All) collapse to their composite EndReason in
# Phase 1; Phase 5 can refine to report which leaf fired if the richer
# telemetry level is enabled.
_END_REASON_BY_CLASS = {
    TickLimitCondition: EndReason.TICK_LIMIT,
    TeamEliminatedCondition: EndReason.TEAM_ELIMINATED,
    TeamIncapacitatedCondition: EndReason.TEAM_INCAPACITATED,
    EscapeCondition: EndReason.ESCAPE,
    ShipDestroyedCondition: EndReason.SHIP_DESTROYED,
    NeverCondition: EndReason.NEVER,
    MassRatioCondition: EndReason.MASS_RATIO,
    AnyCondition: EndReason.ANY,
    AllCondition: EndReason.ALL,
}


def run_battle(
    spec: BattleSpec,
    *,
    ai_factory: "IAIControllerFactory",
    ship_builder: Callable[[ShipSpec], "Ship"],
    headless: bool = True,
    per_tick_callback: Optional[Callable[["BattleEngine"], None]] = None,
    pre_tick_loop_callback: Optional[Callable[["BattleEngine"], None]] = None,
) -> BattleOutcome:
    """Run a fully-specified battle and return its outcome.

    Args:
        spec: The BattleSpec describing initial conditions.
        ai_factory: Injected AI controller factory (UI/strategy owns this).
        ship_builder: Callable that materializes a `Ship` from a `ShipSpec`.
            Phase-1 transitional contract — Phase 2 moves ship construction
            into the engine once `Ship.from_spec` understands
            `ComponentStateSpec` per-component HP.
        headless: Whether to run without rendering. Phase 1 runs the engine
            synchronously regardless; the flag is a no-op at this layer
            but is accepted so downstream callers can request visual mode
            once the Battle Screen migrates in Phase 6.
        per_tick_callback: Optional callable invoked each tick with the
            engine. Used by the Battle Screen for rendering and by Combat
            Lab scenarios for per-tick observation / position tracking.
        pre_tick_loop_callback: Optional one-shot hook fired AFTER
            engine.start() completes and BEFORE the first tick. Used by
            Combat Lab's `_run_scenario_via_battle_runner` to call
            `scenario.custom_setup(engine)` — the Phase 1 smoke-test path.
            Phase 5+ may subsume this into telemetry subscription.

    Returns:
        A populated `BattleOutcome`. Invariants:
            - `outcome.teams[i].team_id == spec.teams[i].team_id`
            - every `ShipSpec.instance_id` maps to exactly one `ShipOutcome`
            - `outcome.seed == spec.seed`
    """
    # Touch headless so linters don't flag it; Phase 1 has no render path here.
    _ = headless

    controller = BattleController(ai_factory=ai_factory)

    config = BattleConfig(
        mode=BattleMode.MANUAL,     # Label only; Phase 6 drops BattleMode.
        seed=spec.seed,
        end_condition=spec.end_condition,
        absolute_max_ticks=spec.absolute_max_ticks,
        headless=True,
        enable_logging=False,
    )
    configure_result = controller.configure(config)
    if not configure_result.success:
        raise RuntimeError(
            f"BattleController.configure failed: {configure_result.errors}"
        )

    # PROJ-269 Phase 3: thread the spec's boundary into the engine.
    # `configure` creates the engine via `BattleService.create_battle`,
    # so by this point the engine exists and we can attach the boundary
    # before ships / start.
    if spec.boundary is not None:
        engine_for_boundary = controller.service.get_engine()
        if engine_for_boundary is not None:
            engine_for_boundary.boundary = spec.boundary

    # Materialize + register each ship, preserving spec pose and instance_id.
    for team_spec in spec.teams:
        team_ships: List["Ship"] = []
        for task_force in team_spec.fleet_hierarchy:
            for squadron in task_force.squadrons:
                for ship_spec in squadron.ships:
                    ship = ship_builder(ship_spec)
                    # Spec pose overrides whatever the builder set.
                    ship.x = ship_spec.position.x
                    ship.y = ship_spec.position.y
                    ship.angle = ship_spec.angle
                    ship.velocity = Vector2(ship_spec.velocity)
                    ship.instance_id = ship_spec.instance_id
                    # PROJ-269 Phase 2: apply per-component HP from spec.
                    _apply_spec_components_to_ship(ship_spec, ship)
                    team_ships.append(ship)
        add_result = controller.add_ships(team_ships, team_id=team_spec.team_id)
        if not add_result.success:
            raise RuntimeError(
                f"BattleController.add_ships failed for team "
                f"{team_spec.team_id}: {add_result.errors}"
            )

    start_result = controller.start()
    if not start_result.success:
        raise RuntimeError(
            f"BattleController.start failed: {start_result.errors}"
        )

    # Tick loop with optional per-tick observer.
    engine = controller.service.get_engine()
    if engine is None:
        raise RuntimeError("Engine missing after controller.start()")

    # One-shot pre-tick-loop hook — runs after engine.start() but before
    # the first update. Combat Lab scenarios use this to invoke
    # `custom_setup(engine)` without introducing a dedicated setup-phase.
    if pre_tick_loop_callback is not None:
        pre_tick_loop_callback(engine)

    while not engine.is_battle_over():
        engine.update()
        if per_tick_callback is not None:
            per_tick_callback(engine)

    outcome = extract_outcome(engine, spec)

    if spec.post_battle_hook is not None:
        spec.post_battle_hook(outcome)

    return outcome


def extract_outcome(engine: "BattleEngine", spec: BattleSpec) -> BattleOutcome:
    """Build a `BattleOutcome` from the engine's final state.

    Phase 1 version:
      - Uses instance_id to match engine ships back to spec ships.
      - Populates pose, status, and per-weapon summaries.
      - Leaves `hits_taken` empty (DETAILED telemetry lands in Phase 5).
      - `components` mirrors the input ShipSpec.components (unchanged
        until Phase 2 wires per-component HP writeback).
    """
    ships_by_instance_id: Dict[str, "Ship"] = {
        ship.instance_id: ship for ship in engine.ships if ship.instance_id
    }
    # PROJ-269 Phase 3: retreated ships were removed from `engine.ships`
    # but tracked separately on `engine.retreated_ships`. Include them in
    # the lookup so `_build_ship_outcome` can mark status=RETREATED.
    retreated_ids: set = set()
    for ship in getattr(engine, "retreated_ships", []):
        if ship.instance_id:
            ships_by_instance_id[ship.instance_id] = ship
            retreated_ids.add(ship.instance_id)

    team_outcomes = []
    for team_spec in spec.teams:
        ship_outcomes = []
        task_force_outcomes = []
        for task_force in team_spec.fleet_hierarchy:
            task_force_outcomes.append(
                TaskForceOutcome(task_force_id=task_force.task_force_id)
            )
            for squadron in task_force.squadrons:
                for ship_spec in squadron.ships:
                    ship_outcomes.append(
                        _build_ship_outcome(
                            ship_spec, ships_by_instance_id, retreated_ids
                        )
                    )
        team_outcomes.append(
            TeamOutcome(
                team_id=team_spec.team_id,
                name=team_spec.name,
                fleet_hierarchy=tuple(task_force_outcomes),
                ships=tuple(ship_outcomes),
            )
        )

    end_reason = _derive_end_reason(engine, spec)

    return BattleOutcome(
        end_reason=end_reason,
        duration_ticks=engine.tick_counter,
        seed=spec.seed,
        teams=tuple(team_outcomes),
        telemetry_level=spec.telemetry_level,
    )


def _build_ship_outcome(
    ship_spec: ShipSpec,
    ships_by_instance_id: Dict[str, "Ship"],
    retreated_ids: Optional[set] = None,
) -> ShipOutcome:
    engine_ship = ships_by_instance_id.get(ship_spec.instance_id)

    if engine_ship is None:
        # Ship was removed mid-battle (retreat / boundary exit). Phase 1
        # treats "missing" as DESTROYED with the spec's original pose.
        return ShipOutcome(
            instance_id=ship_spec.instance_id,
            status=ShipStatus.DESTROYED,
            final_position=ship_spec.position,
            final_angle=ship_spec.angle,
            final_velocity=ship_spec.velocity,
            components=ship_spec.components,
            weapons=(),
            hits_taken=(),
            stats=ShipStats(
                total_damage_taken=0.0,
                peak_speed=0.0,
                ticks_derelict=0,
                ticks_alive=0,
            ),
        )

    # Alive-status resolution
    if retreated_ids and ship_spec.instance_id in retreated_ids:
        status = ShipStatus.RETREATED
    elif not engine_ship.is_alive:
        status = ShipStatus.DESTROYED
    elif engine_ship.is_derelict:
        status = ShipStatus.DERELICT
    else:
        status = ShipStatus.SURVIVED

    return ShipOutcome(
        instance_id=ship_spec.instance_id,
        status=status,
        final_position=Vector2(engine_ship.x, engine_ship.y),
        final_angle=engine_ship.angle,
        final_velocity=Vector2(engine_ship.velocity),
        # PROJ-269 Phase 2: read per-component final HP from engine Ship.
        components=_extract_component_states(engine_ship),
        weapons=tuple(_extract_weapon_summaries(engine_ship)),
        hits_taken=(),  # Phase 5 populates at DETAILED telemetry
        stats=ShipStats(
            total_damage_taken=0.0,       # Phase 5 tracks via ShipStatsAggregator
            peak_speed=0.0,
            ticks_derelict=0,
            ticks_alive=0,
        ),
    )


def _apply_spec_components_to_ship(
    ship_spec: ShipSpec, ship: "Ship"
) -> None:
    """Apply `ShipSpec.components` per-instance HP onto a constructed Ship.

    Walks the Ship's layers in order, tracking per-component-id indices
    to match the keys the compilers emit. Components on the Ship that
    have no matching spec entry are left at their freshly-constructed
    state (typically full HP). Components in the spec that don't map to
    any Ship component are silently ignored (design drift).

    Called by `run_battle` for each ship after `ship_builder` returns.
    """
    if not ship_spec.components:
        return
    # Build (component_id, instance_index) -> ComponentStateSpec lookup.
    spec_by_key: Dict[tuple, ComponentStateSpec] = {
        (c.component_id, c.instance_index): c for c in ship_spec.components
    }
    if not spec_by_key:
        return

    per_id_index: Dict[str, int] = {}
    for layer_data in ship.layers.values():
        for comp in getattr(layer_data, "components", []):
            comp_id = getattr(comp, "id", None)
            if not comp_id:
                continue
            idx = per_id_index.get(comp_id, 0)
            per_id_index[comp_id] = idx + 1
            spec_entry = spec_by_key.get((comp_id, idx))
            if spec_entry is None:
                continue
            target_hp = spec_entry.current_hp
            current = getattr(comp, "current_hp", None)
            if current is None:
                continue
            damage = current - target_hp
            if damage > 0:
                comp.take_damage(int(damage))


def _extract_component_states(engine_ship: "Ship") -> tuple:
    """Emit a tuple of `ComponentStateSpec` reflecting each Ship component's
    final state. Walks layers in order; instance_index resets per component_id.
    """
    out: List[ComponentStateSpec] = []
    per_id_index: Dict[str, int] = {}
    for layer_data in engine_ship.layers.values():
        for comp in getattr(layer_data, "components", []):
            comp_id = getattr(comp, "id", None)
            if not comp_id:
                continue
            idx = per_id_index.get(comp_id, 0)
            per_id_index[comp_id] = idx + 1
            out.append(
                ComponentStateSpec(
                    component_id=comp_id,
                    instance_index=idx,
                    current_hp=float(getattr(comp, "current_hp", 0)),
                    is_active=bool(getattr(comp, "is_active", True)),
                )
            )
    return tuple(out)


def _extract_weapon_summaries(engine_ship: "Ship") -> List[WeaponSummary]:
    """Pull per-weapon shots_fired / shots_hit counters off a ship.

    Same access pattern as `TestScenario._collect_weapon_stats` — we read
    the counters the engine maintains directly on each Component.
    """
    from game.simulation.components.abilities.weapons import WeaponAbility

    summaries: List[WeaponSummary] = []
    if not hasattr(engine_ship, "layers"):
        return summaries
    for layer_data in engine_ship.layers.values():
        for comp in getattr(layer_data, "components", []):
            if not hasattr(comp, "ability_instances"):
                continue
            if any(isinstance(ab, WeaponAbility) for ab in comp.ability_instances):
                summaries.append(
                    WeaponSummary(
                        component_id=comp.id,
                        component_name=comp.name,
                        shots_fired=getattr(comp, "shots_fired", 0),
                        shots_hit=getattr(comp, "shots_hit", 0),
                    )
                )
    return summaries


def _derive_end_reason(engine: "BattleEngine", spec: BattleSpec) -> EndReason:
    """Map the active end-condition type → EndReason.

    The safety ceiling (`absolute_max_ticks`) takes precedence when it
    fires ahead of the end-condition — matches `BattleEngine.is_battle_over`
    semantics.
    """
    # Safety-ceiling check: engine.is_battle_over checks this first, but
    # `tick_counter` may also equal it by the time the end_condition's
    # first satisfying tick lands. Prefer the ABSOLUTE_MAX reason only
    # when the end_condition is NOT a matching TickLimitCondition.
    if engine.tick_counter >= spec.absolute_max_ticks:
        # Disambiguate: if the spec's end_condition is exactly a
        # TickLimitCondition(max_ticks <= absolute_max_ticks), the
        # configured limit fired. Otherwise the safety ceiling saved us.
        if isinstance(spec.end_condition, TickLimitCondition) and (
            spec.end_condition.max_ticks <= spec.absolute_max_ticks
        ):
            return EndReason.TICK_LIMIT
        return EndReason.ABSOLUTE_MAX

    return _END_REASON_BY_CLASS.get(type(spec.end_condition), EndReason.TICK_LIMIT)


__all__ = ["run_battle", "extract_outcome"]
