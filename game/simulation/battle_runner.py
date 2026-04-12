"""`run_battle(spec) -> BattleOutcome` — unified battle simulator entry.

Introduced by PROJ-269 Phase 1 Task 1.6. The single entry into the
simulator. All three contexts (Combat Lab, Battle Setup, Strategy) build
a `BattleSpec` via their own compiler and hand it here. The engine is
context-blind.

PROJ-269 Phase 6 Tasks 6.1-6.3: `run_battle` now constructs and drives
`BattleEngine` directly. The legacy `BattleController` + `BattleConfig` +
`BattleMode` chain is bypassed entirely — those types are slated for
deletion in the same phase. Operational concerns (`headless`,
`per_tick_callback`, `pre_tick_loop_callback`) remain function arguments.

What `run_battle` enforces:
  - spec → engine: teams added in spec order, team_id preserved
  - end_condition / absolute_max_ticks forwarded to the engine
  - seed forwarded (deterministic RNG)
  - boundary + modifier_stack threaded onto the engine
  - per_tick_callback called each tick with the engine
  - pre_tick_loop_callback fired once after engine.start, before tick 1
  - post_battle_hook called once with the final outcome
  - telemetry aggregators (Phase 5) attached per `spec.telemetry_level`
  - outcome is a `BattleOutcome` with:
      - teams in input order
      - every `ShipSpec.instance_id` has exactly one `ShipOutcome`
      - `end_reason` derived from the end-condition type that fired
      - `seed` echoed
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable, Dict, List, Optional

from game.core.math import Vector2
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
from game.simulation.combat.telemetry import (
    HitLogRecorder,
    ShipStatsAggregator,
    TelemetryLevel,
    WeaponSummaryAggregator,
)
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
from game.simulation.systems.battle_engine import BattleEngine, BattleLogger

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.simulation.interfaces.ai_controller import IAIControllerFactory

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


def materialize_spec_ships(
    spec: BattleSpec,
    *,
    ship_builder: Callable[[ShipSpec], "Ship"],
) -> "tuple[Dict[int, List[Ship]], Dict[str, Ship]]":
    """Materialize every `ShipSpec` in `spec.teams` into a `Ship`.

    Shared by `run_battle` (which calls `engine.start_teams` with the
    result) and visual-mode callers (which go through
    `BattleController.add_ships` + `controller.start` instead). The
    function applies the spec pose, velocity, instance_id, and
    per-component HP — everything that's purely spec-driven, before
    any engine participation.

    Returns:
        `(teams_by_id, ships_by_role)`:
        - `teams_by_id`: `{team_id: [Ship, ...]}` — bucketed the way
          `BattleEngine.start_teams` expects.
        - `ships_by_role`: role-suffix (text after the last ':' in
          `ShipSpec.instance_id`) → materialized Ship. Callers that
          don't use role tagging can ignore the second value.
    """
    teams_by_id: Dict[int, List["Ship"]] = {}
    ships_by_role: Dict[str, "Ship"] = {}
    for team_spec in spec.teams:
        team_ships: List["Ship"] = []
        for task_force in team_spec.fleet_hierarchy:
            for squadron in task_force.squadrons:
                for ship_spec in squadron.ships:
                    ship = ship_builder(ship_spec)
                    ship.x = ship_spec.position.x
                    ship.y = ship_spec.position.y
                    ship.angle = ship_spec.angle
                    ship.velocity = Vector2(ship_spec.velocity)
                    ship.instance_id = ship_spec.instance_id
                    _apply_spec_components_to_ship(ship_spec, ship)
                    team_ships.append(ship)
                    if ship_spec.instance_id and ":" in ship_spec.instance_id:
                        role = ship_spec.instance_id.rsplit(":", 1)[1]
                        ships_by_role[role] = ship
        teams_by_id[team_spec.team_id] = team_ships
    return teams_by_id, ships_by_role


def start_engine_from_spec(
    spec: BattleSpec,
    *,
    ai_factory: "IAIControllerFactory",
    ship_builder: Callable[[ShipSpec], "Ship"],
) -> "tuple[BattleEngine, Dict[str, Ship]]":
    """Construct and start a `BattleEngine` from a `BattleSpec`.

    Thin wrapper around `materialize_spec_ships` + `BattleEngine` setup
    + `engine.start_teams()`. Returns `(engine, ships_by_role)`.
    """
    engine = BattleEngine(
        logger=BattleLogger(enabled=False),
        ai_factory=ai_factory,
    )
    if spec.boundary is not None:
        engine.boundary = spec.boundary
    engine.modifier_stack = spec.modifier_stack

    teams_by_id, ships_by_role = materialize_spec_ships(
        spec, ship_builder=ship_builder,
    )
    engine.start_teams(
        teams_by_id,
        seed=spec.seed,
        end_condition=spec.end_condition,
        absolute_max_ticks=spec.absolute_max_ticks,
    )
    return engine, ships_by_role


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
            Each compiler supplies the builder appropriate for its inputs
            (Combat Lab loads JSON; strategy invokes `ShipInstance.to_ship`;
            Battle Setup pre-builds via the design library).
        headless: Whether to run without rendering. Reserved for future
            visual-mode integration; today the engine ticks synchronously
            until `is_battle_over()` regardless. Visual callers drive
            their own per-frame loop and won't go through `run_battle`
            until Task 6.9's UI migration.
        per_tick_callback: Optional callable invoked each tick with the
            engine. Used by Combat Lab scenarios for per-tick observation
            and position tracking.
        pre_tick_loop_callback: Optional one-shot hook fired AFTER
            `engine.start_teams()` completes and BEFORE the first tick.
            Used by Combat Lab to invoke `scenario.custom_setup(engine)`
            without introducing a dedicated setup-phase.

    Returns:
        A populated `BattleOutcome`. Invariants:
            - `outcome.teams[i].team_id == spec.teams[i].team_id`
            - every `ShipSpec.instance_id` maps to exactly one `ShipOutcome`
            - `outcome.seed == spec.seed`
    """
    _ = headless  # Reserved for Task 6.9's visual-mode integration.

    engine, _ships_by_role = start_engine_from_spec(
        spec, ai_factory=ai_factory, ship_builder=ship_builder,
    )

    # PROJ-269 Phase 5: attach telemetry subscribers based on spec level.
    weapon_aggregator, stats_aggregator, hit_log_recorder = _attach_telemetry(
        engine, spec
    )

    # One-shot pre-tick-loop hook — runs after engine.start() but before
    # the first update. Combat Lab scenarios use this to invoke
    # `custom_setup(engine)` without introducing a dedicated setup-phase.
    if pre_tick_loop_callback is not None:
        pre_tick_loop_callback(engine)

    while not engine.is_battle_over():
        engine.update()
        if stats_aggregator is not None:
            stats_aggregator.sample_tick(engine)
        if per_tick_callback is not None:
            per_tick_callback(engine)

    outcome = extract_outcome(
        engine,
        spec,
        weapon_aggregator=weapon_aggregator,
        stats_aggregator=stats_aggregator,
        hit_log_recorder=hit_log_recorder,
    )

    if spec.post_battle_hook is not None:
        spec.post_battle_hook(outcome)

    return outcome


def _attach_telemetry(engine: "BattleEngine", spec: BattleSpec):
    """Instantiate + subscribe telemetry aggregators per `spec.telemetry_level`.

    Returns a `(weapon, stats, hit_log)` tuple with each element set to
    its aggregator instance or None. MINIMAL = (None, None, None).
    """
    level = spec.telemetry_level
    # Be tolerant of placeholder objects from early-phase tests.
    if not isinstance(level, TelemetryLevel):
        return None, None, None

    weapon_aggregator = None
    stats_aggregator = None
    hit_log_recorder = None

    # Raise event-bus detail so the subscribers actually see their events.
    # NORMAL bus emits shield/component-destroyed; DETAILED emits everything.
    from game.simulation.combat.combat_events import EventDetailLevel

    if level >= TelemetryLevel.NORMAL:
        engine.combat_events.detail_level = EventDetailLevel.NORMAL
        weapon_aggregator = WeaponSummaryAggregator()
        stats_aggregator = ShipStatsAggregator(engine.combat_events)

    if level >= TelemetryLevel.DETAILED:
        engine.combat_events.detail_level = EventDetailLevel.DETAILED
        hit_log_recorder = HitLogRecorder(
            engine.combat_events,
            tick_provider=lambda: engine.tick_counter,
            modifier_stack=spec.modifier_stack,
        )

    return weapon_aggregator, stats_aggregator, hit_log_recorder


def extract_outcome(
    engine: "BattleEngine",
    spec: BattleSpec,
    *,
    weapon_aggregator=None,
    stats_aggregator=None,
    hit_log_recorder=None,
) -> BattleOutcome:
    """Build a `BattleOutcome` from the engine's final state + telemetry.

    PROJ-269 Phases 1-5:
      - Uses instance_id to match engine ships back to spec ships.
      - Populates pose, status, and per-component HP (Phase 2).
      - `status=RETREATED` for ships in `engine.retreated_ships` (Phase 3).
      - Telemetry fields (`weapons`, `hits_taken`, `stats`) populated
        from the aggregators when supplied (NORMAL+); empty/zero when
        aggregator is None (MINIMAL).
    """
    # Snapshot aggregator output once so per-ship assembly is fast.
    weapon_snapshot = (
        weapon_aggregator.snapshot(engine) if weapon_aggregator is not None else {}
    )
    stats_snapshot = (
        stats_aggregator.snapshot() if stats_aggregator is not None else {}
    )
    hit_snapshot = (
        hit_log_recorder.snapshot() if hit_log_recorder is not None else {}
    )

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
                            ship_spec,
                            ships_by_instance_id,
                            retreated_ids,
                            weapon_snapshot=weapon_snapshot,
                            stats_snapshot=stats_snapshot,
                            hit_snapshot=hit_snapshot,
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


_ZERO_STATS = ShipStats(
    total_damage_taken=0.0,
    peak_speed=0.0,
    ticks_derelict=0,
    ticks_alive=0,
)


def _build_ship_outcome(
    ship_spec: ShipSpec,
    ships_by_instance_id: Dict[str, "Ship"],
    retreated_ids: Optional[set] = None,
    *,
    weapon_snapshot: Optional[Dict] = None,
    stats_snapshot: Optional[Dict] = None,
    hit_snapshot: Optional[Dict] = None,
) -> ShipOutcome:
    weapon_snapshot = weapon_snapshot or {}
    stats_snapshot = stats_snapshot or {}
    hit_snapshot = hit_snapshot or {}

    engine_ship = ships_by_instance_id.get(ship_spec.instance_id)

    # Telemetry-level populated fields — empty/zero when aggregators are
    # None (MINIMAL level) and filled when the snapshots contain the id.
    weapons = weapon_snapshot.get(ship_spec.instance_id, ())
    hits_taken = hit_snapshot.get(ship_spec.instance_id, ())
    stats = stats_snapshot.get(ship_spec.instance_id, _ZERO_STATS)

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
            weapons=weapons,
            hits_taken=hits_taken,
            stats=stats,
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

    # Fall back to direct component scan for weapons if no aggregator
    # supplied — keeps legacy/MINIMAL path compatible with MINIMAL
    # (weapons=()) vs NORMAL+ (weapons from aggregator).
    return ShipOutcome(
        instance_id=ship_spec.instance_id,
        status=status,
        final_position=Vector2(engine_ship.x, engine_ship.y),
        final_angle=engine_ship.angle,
        final_velocity=Vector2(engine_ship.velocity),
        # PROJ-269 Phase 2: read per-component final HP from engine Ship.
        components=_extract_component_states(engine_ship),
        weapons=weapons,
        hits_taken=hits_taken,
        stats=stats,
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


__all__ = [
    "run_battle",
    "extract_outcome",
    "start_engine_from_spec",
    "materialize_spec_ships",
]
