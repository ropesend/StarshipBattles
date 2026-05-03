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

from typing import TYPE_CHECKING, Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from game.core.math import Vector2
from game.simulation.battle_spec import (
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
    resolve_team_entry_vectors,
)
from game.simulation.combat.ability_stat_registry import emit_entries_for_ability
from game.simulation.combat.modifier_stack import ModifierEntry, ModifierStack
from game.simulation.combat.telemetry import TelemetryLevel
from game.simulation.systems.battle_end_conditions import (
    TeamEliminatedCondition,
    TickLimitCondition,
)

if TYPE_CHECKING:
    from game.core.registry import GameRegistries
    from game.simulation.systems.battle_end_conditions import IEndCondition
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.ship_instance import ShipInstance


_DEFAULT_ABSOLUTE_MAX_TICKS = 20_000

# Issue #8: budget for the truncated `run_battle` call invoked by
# `SimulationBattleResolver` when both fleets have ships but neither has
# any combat-capable weapons. 1/10 of the normal strategy ceiling.
_BRIEF_RUN_TICK_BUDGET = _DEFAULT_ABSOLUTE_MAX_TICKS // 10


_MIN_TEAMS = 2
_MAX_TEAMS = 8


def build_strategy_battle_spec(
    fleets: List["Fleet"],
    *,
    empires: Optional[Mapping[Any, Any]] = None,
    settings: Any = None,
    registries: "GameRegistries",
    seed: Optional[int] = None,
    end_condition: Optional["IEndCondition"] = None,
    post_battle_hook: Optional[Any] = None,
    environmental_effects: Any = None,
    team_modifiers: Optional[Mapping[int, Any]] = None,
    max_ticks: Optional[int] = None,
) -> BattleSpec:
    """Compile fleets-on-hex + environment into a `BattleSpec`.

    Args:
        fleets: The fleets clashing on the hex. One team per fleet in
            Phase 1 (N-team support lands in Phase 3).
        empires: Optional mapping of team_id -> empire. Used by the
            post-battle hook to remove destroyed fleets from the owning
            empire's fleet list. Does NOT inject any modifier-stack
            entries (PROJ-271 Phase 9 deleted the old empire-modifier
            path). Production callers may pass `None`.
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
            shield interference). Translated to global ModifierStack entries.
        team_modifiers: Optional mapping `{team_id: FleetCombatModifiers}`
            carrying per-team strategic modifiers (shield/damage
            multipliers, flat shield bonus). Translated to per-team
            ModifierStack entries via `_entries_from_fleet_combat_modifiers`.
        max_ticks: Issue #8 — when supplied, overrides BOTH
            `absolute_max_ticks` AND replaces the default
            `TeamEliminatedCondition` end_condition with
            `TickLimitCondition(max_ticks=max_ticks)`. Both are required:
            `TeamEliminatedCondition` would never fire in a no-weapons
            battle (neither team can be eliminated), so without the
            swap the spec would tick to the safety ceiling. Used by
            `SimulationBattleResolver` for the truncated run that
            captures a real (brief) replay when both fleets have ships
            but no combat-capable weapons.

    Returns:
        Populated `BattleSpec`. The caller (`SimulationBattleResolver`)
        passes this to `run_battle` along with a `ship_builder` closure
        that calls `ShipInstance.to_ship`.

    PROJ-272 Phase 7: removed vestigial `sector`/`system`/`modifiers`-on-
    `empires` kwargs that fed the deleted `_entries_from_modifier_source`
    helper (PROJ-271 Phase 9). `empires` kwarg KEPT because the
    post-battle hook still uses it to prune destroyed fleets.
    """
    _ = registries  # Phase 1: parity; Phase 2 uses this for ship construction.

    if empires is None:
        empires = {}

    # PROJ-320 Phase 3: group fleets by `owner_id` so allied fleets
    # share a team rather than fighting each other (the engine has no
    # alliances — every non-self team is hostile by default). Pre-PROJ-320
    # the spec compiler emitted one team per fleet, which was harmless
    # only because `_resolve_combat_at_hex` silently dropped extra fleets
    # per empire.
    #
    # Determinism: rely on insertion order (Python 3.7+ guaranteed) rather
    # than `sorted(...)`. Owner ids may not be sortable in tests
    # (MagicMock fleets), and the canonical caller
    # (`_resolve_combat_at_hex`) already sorts fleets by `(empire_id,
    # fleet_id)` before passing them in — so insertion order here is
    # already the (sorted-empire-id) order for production.
    fleets_by_owner: Dict[Any, List["Fleet"]] = {}
    for fleet in fleets:
        fleets_by_owner.setdefault(fleet.owner_id, []).append(fleet)
    owner_order: List[Any] = list(fleets_by_owner.keys())

    num_teams = len(owner_order)
    if num_teams < _MIN_TEAMS or num_teams > _MAX_TEAMS:
        raise ValueError(
            f"build_strategy_battle_spec: requires {_MIN_TEAMS}..{_MAX_TEAMS} "
            f"unique fleet owners; got {num_teams} from {len(fleets)} fleets"
        )

    entry_vectors = resolve_team_entry_vectors(team_count=num_teams)

    teams: List[TeamSpec] = []
    for team_id, owner_id in enumerate(owner_order):
        owner_fleets = list(fleets_by_owner[owner_id])
        teams.append(
            _team_spec_for_fleet_group(
                owner_fleets,
                team_id=team_id,
                entry_vector=entry_vectors[team_id],
            )
        )

    modifier_stack = _build_modifier_stack(
        team_count=len(teams),
        environmental_effects=environmental_effects,
        team_modifiers=team_modifiers,
    )

    boundary = None
    if settings is not None:
        boundary = getattr(settings, "combat_boundary_default", None)
    if boundary is None:
        boundary = UnboundedRegion()

    if max_ticks is not None:
        # Issue #8: explicit caller cap (e.g. truncated no_capable run).
        # Force both fields together — see the `max_ticks` argdoc.
        effective_end_condition: "IEndCondition" = TickLimitCondition(
            max_ticks=max_ticks
        )
        effective_absolute_max_ticks = max_ticks
    else:
        effective_end_condition = (
            end_condition if end_condition is not None else TeamEliminatedCondition()
        )
        effective_absolute_max_ticks = _DEFAULT_ABSOLUTE_MAX_TICKS

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
        absolute_max_ticks=effective_absolute_max_ticks,
        teams=tuple(teams),
        modifier_stack=modifier_stack,
        post_battle_hook=effective_hook,
    )


def _build_strategy_post_battle_hook(
    fleets: List["Fleet"],
    empires: Mapping[Any, Any],
) -> Callable[[Any], None]:
    """Create a post-battle hook closure for a specific set of fleets.

    PROJ-320 Phase 3: groups fleets by `owner_id` to match the spec
    compiler's per-owner team assignment. The post-battle hook then
    receives `{team_id: [list of allied fleets]}` so the
    `apply_outcome_to_fleets` instance-id lookup can find each ship in
    its originating fleet.

    Captures (team_id -> fleets) by owner — the compiler assigns
    team_ids by sorted owner order, mirrored here.
    """
    from game.strategy.combat.post_battle_hook import apply_outcome_to_fleets

    # PROJ-320: mirror the spec compiler's per-owner grouping. Use
    # insertion order (not `sorted`) for owner_ids so the hook works
    # with MagicMock fleets in tests; the canonical caller
    # (`_resolve_combat_at_hex`) sorts fleets by `(empire_id, fleet_id)`
    # before invoking the resolver, so insertion order IS sorted order
    # for production. Within an owner, sort by fleet.id (always int).
    owner_to_fleets: Dict[Any, List["Fleet"]] = {}
    for fleet in fleets:
        owner_to_fleets.setdefault(fleet.owner_id, []).append(fleet)
    owner_order: List[Any] = list(owner_to_fleets.keys())

    fleets_by_team_id: Dict[int, List["Fleet"]] = {
        team_id: list(owner_to_fleets[owner_id])
        for team_id, owner_id in enumerate(owner_order)
    }
    # Translate the empires mapping from arbitrary keys to the same
    # team_id basis used by the compiler.
    empires_by_team_id: Dict[int, Any] = {}
    for team_id, owner_id in enumerate(owner_order):
        # Prefer explicit team_id key, fall back to owner_id — callers
        # may pass empires keyed either way.
        empire = empires.get(team_id)
        if empire is None:
            empire = empires.get(owner_id)
        if empire is not None:
            empires_by_team_id[team_id] = empire

    def _hook(outcome) -> None:
        apply_outcome_to_fleets(
            outcome,
            fleets_by_team_id=fleets_by_team_id,
            empires=empires_by_team_id or None,
        )

    return _hook


# ---------------------------------------------------------------------------
# Fleet translation
# ---------------------------------------------------------------------------


def _team_spec_for_fleet_group(
    owner_fleets: List["Fleet"], *, team_id: int, entry_vector: EntryVector
) -> TeamSpec:
    """PROJ-320 Phase 3: build a TeamSpec for one or more allied fleets.

    Each fleet contributes its own TaskForce inside the team — preserves
    fleet identity for the post-battle hook (which dispatches outcomes
    back into the originating Fleet's ships list). Formation resolution
    is per-fleet (each fleet keeps its own arrangement); team-level
    placement comes from `entry_vector` (one entry vector per team).

    For the single-fleet case (every existing PROJ-275 caller), this
    behaves identically to the deleted `_team_spec_for_fleet`: one
    TaskForce, one Squadron, one team.
    """
    if not owner_fleets:
        raise ValueError(
            "_team_spec_for_fleet_group: owner_fleets must be non-empty"
        )

    task_forces: List[TaskForceSpec] = []
    for fleet in owner_fleets:
        # PROJ-269 Phase 4: invoke FormationResolver to compute per-ship poses.
        # PROJ-275 Phase 6: entry_vector is supplied by the caller from the
        # ring-layout helper (`resolve_team_entry_vectors`); all of an
        # owner's fleets share the same team-level entry vector.
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
        task_forces.append(
            TaskForceSpec(
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
        )
    name = (
        f"Fleet {owner_fleets[0].id}"
        if len(owner_fleets) == 1
        else f"Empire {owner_fleets[0].owner_id} ({len(owner_fleets)} fleets)"
    )
    return TeamSpec(
        team_id=team_id,
        name=name,
        entry_vector=entry_vector,
        fleet_hierarchy=tuple(task_forces),
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
        # PROJ-274: InstanceBackedMaterializer reads this via duck typing
        # to call `ship.to_ship(position, team_id, registries=...)`. Ship
        # materialization no longer requires caller-provided ship_builder
        # closures in production.
        instance_ref=ship,
    )


# ---------------------------------------------------------------------------
# Modifier translation
# ---------------------------------------------------------------------------


def _build_modifier_stack(
    *,
    team_count: int,
    environmental_effects: Any = None,
    team_modifiers: Optional[Mapping[int, Any]] = None,
) -> ModifierStack:
    # PROJ-271 Phase 9 + PROJ-272 Phase 7: `sector`/`system`/`empires`
    # kwargs removed. The old `_entries_from_modifier_source` helper
    # (deleted Phase 9) emitted placeholder entries for ad-hoc
    # `sector.modifiers` / `system.modifiers` / `empire.combat_modifiers`
    # attributes; no production code populated them, and callers were
    # silently discarding the results. Real strategic modifiers flow via
    # `environmental_effects` (global) and `team_modifiers` (per-team).
    global_entries: List[ModifierEntry] = []
    if environmental_effects is not None:
        # PROJ-300 Phase 7: only the new sector-effects list shape is accepted.
        # Legacy EnvironmentalEffects path was deleted alongside AreaEffectManager.
        global_entries.extend(
            _entries_from_sector_effects(environmental_effects)
        )

    per_team: Dict[int, Tuple[ModifierEntry, ...]] = {}
    for team_id in range(team_count):
        entries: List[ModifierEntry] = []
        if team_modifiers is not None and team_id in team_modifiers:
            entries.extend(
                _entries_from_fleet_combat_modifiers(
                    team_modifiers[team_id], team_id=team_id
                )
            )
        if entries:
            per_team[team_id] = tuple(entries)

    return ModifierStack(per_team=per_team, global_=tuple(global_entries))


def _emit_entries_team_scoped(
    ability_name: str,
    value: float,
    *,
    team_id: int,
    source: str,
    display_name: str,
    design_id: str,
    stack_group: Optional[str] = None,
) -> List[ModifierEntry]:
    """Strategy-side wrapper around `emit_entries_for_ability`.

    Strategy's fleet/empire modifiers always route to a single team
    (no enemy fan-out — those are ship-mounted abilities, not
    caller-supplied strategic modifiers). Uses the primitive-numeric
    path of the registry helper (value passed directly), and strips
    the team_id from the returned (team_id, entry) tuples since the
    caller places these entries in a specific per-team bucket it
    already knows.
    """
    team_entries = emit_entries_for_ability(
        ability_name,
        value,
        scope="self",
        owner_team=team_id,
        num_teams=team_id + 1,  # arbitrary; "self" routes to owner regardless
        source=source,
        source_modifier_id=design_id,
        source_modifier_name=display_name,
        stack_group=stack_group,
    )
    return [entry for _, entry in team_entries]


def _entries_from_sector_effects(sector_effects: Sequence[Dict[str, Any]]) -> List[ModifierEntry]:
    """Translate a PROJ-300 sector-effects list into `ModifierEntry` entries.

    For each combat-relevant ability (`ShieldModifier`, `DamageModifier`,
    `ThrustModifier` per D14), emit one entry per ACTIVE provider so
    overlapping storms/facilities multiply naturally (no shared stack_group).
    Per decisions.md D6, storm stacking goes from MAX (legacy) to MULTIPLY
    (new) — two ion storms now apply 0.25x shields, not 0.5x.
    """
    combat_ability_names = {"ShieldModifier", "DamageModifier", "ThrustModifier"}
    entries: List[ModifierEntry] = []
    for effect in sector_effects:
        ability_name = effect.get('ability_name')
        if ability_name not in combat_ability_names:
            continue
        for provider in effect.get('providers', []):
            if not provider.get('is_active', True):
                continue
            ability_data = provider.get('ability_data') or {}
            mult = ability_data.get('multiplier', 1.0)
            if mult == 1.0:
                continue
            source_kind = provider.get('source_kind', 'unknown')
            source_id = provider.get('source_id', 'unknown')
            source_label = provider.get('source_label', source_id)
            stack_group = ability_data.get('stack_group')  # None on storms
            team_entries = emit_entries_for_ability(
                ability_name,
                mult,
                scope="self",
                owner_team=0,
                num_teams=1,
                source=f"sector:{source_kind}",
                source_modifier_id=source_id,
                source_modifier_name=source_label,
                stack_group=stack_group,
            )
            entries.extend(entry for _, entry in team_entries)
    return entries


def _entries_from_fleet_combat_modifiers(
    modifiers: Any, *, team_id: int
) -> List[ModifierEntry]:
    """Translate a `FleetCombatModifiers` value into `ModifierEntry` entries.

    PROJ-270/271 emit REAL stat_keys:
      - `shield_mult` → `shield_capacity_mult` (via ShieldModifier)
      - `damage_mult` → `damage_mult` (via DamageModifier)
      - `flat_shield_bonus` → `shield_bonus_add` (via ShieldProjection)

    Ship-level plumbing in `ship_stats.py::_apply_aggregated_stats`
    consumes the shield pair as `(base + flat) × shield_capacity_mult`.

    PROJ-273 Phase 3: all three emissions now route through the shared
    `ability_stat_registry` helper. Caller places returned entries in
    `ModifierStack.per_team[team_id]`.
    """
    entries: List[ModifierEntry] = []
    shield_mult = getattr(modifiers, "shield_mult", 1.0)
    damage_mult = getattr(modifiers, "damage_mult", 1.0)
    flat_shield = getattr(modifiers, "flat_shield_bonus", 0.0)
    if shield_mult != 1.0:
        entries.extend(
            _emit_entries_team_scoped(
                "ShieldModifier",
                shield_mult,
                team_id=team_id,
                source=f"team{team_id}:shield_mult",
                display_name=f"Shield x{shield_mult:.2f}",
                design_id="team_shield_mult",
                # PROJ-272 Phase 2: per-team shield multipliers MAX within team.
                # Collector-aggregated; one entry per team — still grouped for
                # future source expansion (e.g., multi-empire fleet bonuses).
                stack_group=f"team{team_id}_shield_mult",
            )
        )
    if damage_mult != 1.0:
        entries.extend(
            _emit_entries_team_scoped(
                "DamageModifier",
                damage_mult,
                team_id=team_id,
                source=f"team{team_id}:damage_mult",
                display_name=f"Damage x{damage_mult:.2f}",
                design_id="team_damage_mult",
                stack_group=f"team{team_id}_damage_mult",
            )
        )
    if flat_shield:
        entries.extend(
            _emit_entries_team_scoped(
                "ShieldProjection",
                flat_shield,
                team_id=team_id,
                source=f"team{team_id}:flat_shield_bonus",
                display_name=f"Shield +{flat_shield}",
                design_id="team_flat_shield_bonus",
                stack_group=f"team{team_id}_flat_shield",
            )
        )
    return entries


__all__ = ["build_strategy_battle_spec"]
