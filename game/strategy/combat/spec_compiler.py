"""Strategy spec compiler — fleets on a hex → BattleSpec.

Introduced by PROJ-269 Phase 1 Task 1.9. Replaces the
`SimulationBattleResolver.resolve_battle` pattern that pre-mutates ship
attributes before handing them to the engine. The new flow:

  build_strategy_battle_spec(...) -> BattleSpec
              |
              v
  run_battle(spec, ai_factory, ship_builder) -> BattleOutcome
              |
              v
  spec.post_battle_hook(outcome) -> updates ShipInstance.components

Phase 1 scope:
  - Walks fleets → ships, producing one `TeamSpec` per fleet.
  - Pulls boundary from `settings.combat_boundary_default`. None falls
    back to `UnboundedRegion`.
  - Translates sector/system modifiers into `ModifierStack.global_`.
  - Translates empire modifiers into `ModifierStack.per_team[team_id]`.
  - Attaches a `post_battle_hook` that is a no-op closure. Phase 2
    replaces it with `apply_outcome_to_fleets`.
  - `ShipSpec.components = ()` — ShipInstance.components field lands
    in Phase 2.
  - Entry vectors: Phase 1 places each team at the hex center with a
    placeholder facing. Phase 4 wires proper hex-edge entry.
  - Telemetry level defaults to NORMAL.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, Tuple

from game.core.math import Vector2
from game.simulation.battle_outcome import BattleOutcome
from game.simulation.battle_spec import (
    AIPolicy,
    BattleSpec,
    CombatPolicies,
    ComponentStateSpec,
    EntryVector,
    ShipSpec,
    SquadronSpec,
    TaskForceSpec,
    TeamSpec,
)
from game.simulation.combat.boundary import UnboundedRegion
from game.simulation.combat.formation import (
    FormationResolver,
    FormationSpec,
    resolve_default_for_task_force,
)
from game.simulation.combat.modifier_stack import ModifierEntry, ModifierStack
from game.simulation.combat.telemetry import TelemetryLevel
from game.simulation.components.modifier_effects import ModifierEffect
from game.simulation.systems.battle_end_conditions import TeamEliminatedCondition

if TYPE_CHECKING:
    from game.core.registry import GameRegistries
    from game.simulation.systems.battle_end_conditions import IEndCondition
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.ship_instance import ShipInstance


_DEFAULT_ABSOLUTE_MAX_TICKS = 20_000


def build_strategy_battle_spec(
    fleets: List["Fleet"],
    *,
    sector: Any = None,
    system: Any = None,
    empires: Optional[Mapping[Any, Any]] = None,
    settings: Any = None,
    registries: "GameRegistries",
    seed: Optional[int] = None,
    end_condition: Optional["IEndCondition"] = None,
    post_battle_hook: Optional[Any] = None,
    environmental_effects: Any = None,
    team_modifiers: Optional[Mapping[int, Any]] = None,
) -> BattleSpec:
    """Compile fleets-on-hex + environment into a `BattleSpec`.

    Args:
        fleets: The fleets clashing on the hex. One team per fleet in
            Phase 1 (N-team support lands in Phase 3).
        sector: Optional sector object. The compiler reads a `modifiers`
            attribute if present (iterable of dicts with `design_id`
            and `display_name`).
        system: Optional star-system object — same `modifiers` contract.
        empires: Optional mapping of team_id -> empire. Each empire may
            expose `combat_modifiers` (iterable of dicts) that flow into
            `ModifierStack.per_team[team_id]`.
        settings: Optional GameSettings. Only `combat_boundary_default`
            is consulted; None falls back to `UnboundedRegion`.
        registries: GameRegistries (required for signature parity and
            for the Phase 2 ship materialization path).
        seed: Optional RNG seed. `None` defaults to 0 — strategy battles
            are reproducible within a turn, and the caller is expected
            to supply a turn-derived seed in practice.
        end_condition: Optional custom end condition. Defaults to
            `TeamEliminatedCondition()` — matches today's strategy combat.
        environmental_effects: Optional `EnvironmentalEffects` object
            carrying per-battle environmental multipliers (e.g. storm
            shield interference). Translated to global ModifierStack
            entries. PROJ-269 Phase 5.5 semantics apply — placeholder
            effects are emitted for the engine's forensic trace; real
            effect evaluation is post-PROJ-269 content work.
        team_modifiers: Optional mapping `{team_id: FleetCombatModifiers}`
            carrying per-team strategic modifiers (shield/damage
            multipliers, flat shield bonus). Translated to per-team
            ModifierStack entries with placeholder effects.

    Returns:
        Populated `BattleSpec`. The caller (`SimulationBattleResolver`
        post-Phase 6) passes this to `run_battle` along with a
        `ship_builder` closure that calls `ShipInstance.to_ship`.
    """
    _ = registries  # Phase 1: parity; Phase 2 uses this for ship construction.

    if empires is None:
        empires = {}

    teams: List[TeamSpec] = []
    for team_id, fleet in enumerate(fleets):
        teams.append(_team_spec_for_fleet(fleet, team_id=team_id))

    modifier_stack = _build_modifier_stack(
        sector=sector,
        system=system,
        empires=empires,
        team_count=len(teams),
        environmental_effects=environmental_effects,
        team_modifiers=team_modifiers,
    )

    boundary = None
    if settings is not None:
        boundary = getattr(settings, "combat_boundary_default", None)
    if boundary is None:
        boundary = UnboundedRegion()

    effective_end_condition: "IEndCondition" = (
        end_condition if end_condition is not None else TeamEliminatedCondition()
    )

    # PROJ-269 Phase 2: attach a real post-battle hook that closes over
    # this battle's fleets + empires and calls `apply_outcome_to_fleets`
    # to persist outcome state. Callers that want a no-op (tests, legacy)
    # can pass an explicit `post_battle_hook=lambda outcome: None`.
    effective_hook = post_battle_hook
    if effective_hook is None:
        effective_hook = _build_strategy_post_battle_hook(fleets, empires)

    return BattleSpec(
        seed=seed if seed is not None else 0,
        telemetry_level=TelemetryLevel.NORMAL,
        boundary=boundary,
        end_condition=effective_end_condition,
        absolute_max_ticks=_DEFAULT_ABSOLUTE_MAX_TICKS,
        teams=tuple(teams),
        modifier_stack=modifier_stack,
        post_battle_hook=effective_hook,
    )


def _build_strategy_post_battle_hook(
    fleets: List["Fleet"],
    empires: Mapping[Any, Any],
):
    """Create a post-battle hook closure for a specific set of fleets.

    Captures (team_id -> fleet) positionally — the compiler assigns
    team_ids in the same order as the input `fleets` list, so hook
    inversion is trivial.
    """
    from game.strategy.combat.post_battle_hook import apply_outcome_to_fleets

    fleets_by_team_id: Dict[int, List["Fleet"]] = {
        team_id: [fleet] for team_id, fleet in enumerate(fleets)
    }
    # Translate the empires mapping from arbitrary keys to the same
    # team_id basis used by the compiler.
    empires_by_team_id: Dict[int, Any] = {}
    for team_id, fleet in enumerate(fleets):
        # Prefer explicit team_id key, fall back to fleet.owner_id, fall
        # back to fleet id — callers may pass empires keyed either way.
        empire = empires.get(team_id)
        if empire is None:
            empire = empires.get(fleet.owner_id)
        if empire is not None:
            empires_by_team_id[team_id] = empire

    def _hook(outcome):
        apply_outcome_to_fleets(
            outcome,
            fleets_by_team_id=fleets_by_team_id,
            empires=empires_by_team_id or None,
        )

    return _hook


# ---------------------------------------------------------------------------
# Fleet translation
# ---------------------------------------------------------------------------


def _team_spec_for_fleet(fleet: "Fleet", *, team_id: int) -> TeamSpec:
    # PROJ-269 Phase 4: invoke FormationResolver to compute per-ship poses.
    entry_vector = EntryVector(origin=Vector2(0.0, 0.0), facing=0.0)
    formation = _pick_formation_for_fleet(fleet)
    poses = FormationResolver.resolve(
        formation=formation,
        entry_vector=entry_vector,
        boundary=None,
        ships=fleet.ships,
    )
    ships: Tuple[ShipSpec, ...] = tuple(
        _ship_spec_from_instance(ship, poses.get(ship.instance_id))
        for ship in fleet.ships
    )
    task_force = TaskForceSpec(
        task_force_id=f"tf-fleet-{fleet.id}",
        formation=formation,
        policies=CombatPolicies(),
        squadrons=(
            SquadronSpec(
                squadron_id=f"sq-fleet-{fleet.id}",
                policies=CombatPolicies(),
                ships=ships,
            ),
        ),
    )
    return TeamSpec(
        team_id=team_id,
        name=f"Fleet {fleet.id}",
        entry_vector=entry_vector,
        fleet_hierarchy=(task_force,),
        ai_policy=AIPolicy(),
    )


def _pick_formation_for_fleet(fleet: "Fleet") -> FormationSpec:
    """Pick the formation for a Fleet.

    Priority:
      1. Explicit `TaskForce.formation` if any TF on the fleet has one
         set (first TF wins — Phase 4 MVP, richer per-TF resolution
         lands with proper TF hierarchy handling).
      2. `resolve_default_for_task_force(fleet.ships)` otherwise.
    """
    for tf in getattr(fleet, "task_forces", []) or []:
        if getattr(tf, "formation", None) is not None:
            return tf.formation
    return resolve_default_for_task_force(fleet.ships)


def _ship_spec_from_instance(
    ship: "ShipInstance",
    pose: Optional[Tuple[Vector2, float]] = None,
) -> ShipSpec:
    theme_id = "Federation"
    if hasattr(ship, "design_data") and isinstance(ship.design_data, dict):
        theme_id = ship.design_data.get("theme_id", theme_id)

    # PROJ-269 Phase 2: translate ShipInstance.components (Dict[str,
    # ComponentState]) into a tuple of ComponentStateSpec. Sort by
    # (component_id, instance_index) so the output is deterministic —
    # downstream tests and outcome comparisons depend on stable order.
    component_specs: Tuple[ComponentStateSpec, ...] = ()
    instance_components = getattr(ship, "components", None) or {}
    if instance_components:
        sorted_states = sorted(
            instance_components.values(),
            key=lambda cs: (cs.component_id, cs.instance_index),
        )
        component_specs = tuple(
            ComponentStateSpec(
                component_id=cs.component_id,
                instance_index=cs.instance_index,
                current_hp=float(cs.current_hp),
                is_active=bool(cs.is_active),
            )
            for cs in sorted_states
        )

    # PROJ-269 Phase 4: FormationResolver supplies the pose.
    if pose is not None:
        position, angle = pose
    else:
        position, angle = Vector2(0.0, 0.0), 0.0

    return ShipSpec(
        instance_id=ship.instance_id,
        design_id=ship.design_id,
        theme_id=theme_id,
        name=ship.name,
        position=position,
        angle=float(angle),
        velocity=Vector2(0.0, 0.0),
        components=component_specs,
    )


# ---------------------------------------------------------------------------
# Modifier translation
# ---------------------------------------------------------------------------


def _build_modifier_stack(
    *,
    sector: Any,
    system: Any,
    empires: Mapping[Any, Any],
    team_count: int,
    environmental_effects: Any = None,
    team_modifiers: Optional[Mapping[int, Any]] = None,
) -> ModifierStack:
    global_entries: List[ModifierEntry] = []
    if system is not None:
        global_entries.extend(
            _entries_from_modifier_source(system, source_prefix="system")
        )
    if sector is not None:
        global_entries.extend(
            _entries_from_modifier_source(sector, source_prefix="sector")
        )
    if environmental_effects is not None:
        global_entries.extend(
            _entries_from_environmental_effects(environmental_effects)
        )

    per_team: Dict[int, Tuple[ModifierEntry, ...]] = {}
    # Empire modifiers — empires is keyed by team_id (or empire id).
    # Phase 1 matches them positionally.
    for team_id in range(team_count):
        empire = empires.get(team_id)
        entries: List[ModifierEntry] = []
        if empire is not None:
            entries.extend(
                _entries_from_modifier_source(
                    empire, source_prefix="empire", attr_name="combat_modifiers"
                )
            )
        if team_modifiers is not None and team_id in team_modifiers:
            entries.extend(
                _entries_from_fleet_combat_modifiers(
                    team_modifiers[team_id], team_id=team_id
                )
            )
        if entries:
            per_team[team_id] = tuple(entries)

    return ModifierStack(per_team=per_team, global_=tuple(global_entries))


def _entries_from_environmental_effects(effects: Any) -> List[ModifierEntry]:
    """Translate an `EnvironmentalEffects` value into `ModifierEntry` entries.

    PROJ-270 Phase 6.1: storm shield interference now emits a REAL
    `stat_key="shield_capacity_mult"` (not `"placeholder"`) so the
    `FleetAuraManager` pipeline applies the effect to ship shield
    capacity during battle. Replaces the PROJ-269 Phase 5.5 placeholder
    semantics for this specific effect.
    """
    entries: List[ModifierEntry] = []
    shield_mult = getattr(effects, "shield_capacity_mult", 1.0)
    if shield_mult is not None and shield_mult != 1.0:
        entries.append(
            _real_entry(
                source="environment:storm_shield_interference",
                display_name=f"Storm Shield x{shield_mult:.2f}",
                design_id="storm_shield_interference",
                stat_key="shield_capacity_mult",
                value=shield_mult,
                operation="multiply",
            )
        )
    return entries


def _entries_from_fleet_combat_modifiers(
    modifiers: Any, *, team_id: int
) -> List[ModifierEntry]:
    """Translate a `FleetCombatModifiers` value into `ModifierEntry` entries.

    PROJ-270 Phase 6.2: `shield_mult` and `damage_mult` now emit REAL
    stat_keys (`shield_capacity_mult`, `damage_mult`) so the
    `FleetAuraManager` pipeline applies them during battle. Replaces
    the Phase 5.5 placeholder semantics for these multipliers.

    `flat_shield_bonus` remains a placeholder pending PROJ-271 scope —
    requires new additive stat_key (`SHIELD_BONUS_ADD`) wiring. See
    decisions.md Decision 1 (scope trim).
    """
    entries: List[ModifierEntry] = []
    shield_mult = getattr(modifiers, "shield_mult", 1.0)
    damage_mult = getattr(modifiers, "damage_mult", 1.0)
    flat_shield = getattr(modifiers, "flat_shield_bonus", 0.0)
    if shield_mult != 1.0:
        entries.append(
            _real_entry(
                source=f"team{team_id}:shield_mult",
                display_name=f"Shield x{shield_mult:.2f}",
                design_id="team_shield_mult",
                stat_key="shield_capacity_mult",
                value=shield_mult,
                operation="multiply",
            )
        )
    if damage_mult != 1.0:
        entries.append(
            _real_entry(
                source=f"team{team_id}:damage_mult",
                display_name=f"Damage x{damage_mult:.2f}",
                design_id="team_damage_mult",
                stat_key="damage_mult",
                value=damage_mult,
                operation="multiply",
            )
        )
    if flat_shield:
        # PROJ-271 deferred: flat_shield_bonus still placeholder until
        # `SHIELD_BONUS_ADD` additive stat_key is wired through.
        entries.append(
            _placeholder_entry(
                source=f"team{team_id}:flat_shield_bonus",
                display_name=f"Shield +{flat_shield}",
                design_id="team_flat_shield_bonus",
            )
        )
    return entries


def _real_entry(
    *,
    source: str,
    display_name: str,
    design_id: str,
    stat_key: str,
    value: float,
    operation: str = "multiply",
) -> ModifierEntry:
    """Build a `ModifierEntry` that the engine will actually apply.

    PROJ-270 Phase 6: used for modifier sources whose real stat_key
    mapping is known. The `FleetAuraManager` translates this into an
    `ExternalModifier` via `ability_name=stat_key` and applies it to
    ship stats at battle start.
    """
    effect = ModifierEffect(
        stat_key=stat_key,
        value=value,
        operation=operation,
        target_ability=None,
        source_modifier_id=design_id,
        source_modifier_name=display_name,
        formula_str="",
        param_value=value,
    )
    return ModifierEntry(source=source, stack_group=None, effect=effect)


def _placeholder_entry(*, source: str, display_name: str, design_id: str) -> ModifierEntry:
    """Build a PROJ-269 Phase 5.5 placeholder `ModifierEntry`.

    The engine filters these out of the effect application pipeline but
    retains them in forensic traces (`HitRecord.modifiers_applied`).
    """
    effect = ModifierEffect(
        stat_key="placeholder",
        value=0.0,
        operation="multiply",
        target_ability=None,
        source_modifier_id=design_id,
        source_modifier_name=display_name,
        formula_str="",
        param_value=0.0,
    )
    return ModifierEntry(source=source, stack_group=None, effect=effect)


def _entries_from_modifier_source(
    source_obj: Any,
    *,
    source_prefix: str,
    attr_name: str = "modifiers",
) -> List[ModifierEntry]:
    """Extract ModifierEntry objects from an attribute on `source_obj`.

    The attribute is expected to be an iterable of dicts with
    `design_id` and `display_name`. Phase 1 produces placeholder effects;
    Phase 5 replaces with real effect evaluation.
    """
    modifier_dicts = getattr(source_obj, attr_name, None)
    if not modifier_dicts:
        return []
    entries: List[ModifierEntry] = []
    for mod in modifier_dicts:
        design_id = mod.get("design_id")
        if not design_id:
            continue
        display = mod.get("display_name", design_id)
        placeholder_effect = ModifierEffect(
            stat_key="placeholder",
            value=0.0,
            operation="multiply",
            target_ability=None,
            source_modifier_id=design_id,
            source_modifier_name=display,
            formula_str="",
            param_value=0.0,
        )
        entries.append(
            ModifierEntry(
                source=f"{source_prefix}:{design_id}",
                stack_group=None,
                effect=placeholder_effect,
            )
        )
    return entries


# ---------------------------------------------------------------------------
# Post-battle hook (Phase 1 placeholder)
# ---------------------------------------------------------------------------


def _noop_hook(outcome: BattleOutcome) -> None:
    """Phase 1 placeholder post-battle hook.

    Phase 2 replaces this with `apply_outcome_to_fleets(outcome, ...)`
    which writes `ShipOutcome.components` back to
    `ShipInstance.components`, removes destroyed ships from fleets,
    and applies empire-level effects.
    """
    _ = outcome


__all__ = ["build_strategy_battle_spec"]
