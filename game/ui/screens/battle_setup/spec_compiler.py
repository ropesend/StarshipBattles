"""Battle Setup spec compiler — BattleSetupState → BattleSpec.

Introduced by PROJ-269 Phase 1 Task 1.8. Translates the fleet-based
Battle Setup UI state into a `BattleSpec` that `run_battle(spec)` can
execute.

Phase 1 scope:
  - Walks `ui_state.side_N.fleets` → ships, producing one
    `TaskForceSpec`-per-fleet with a single `SquadronSpec` underneath.
    Phase 4 refines this once TaskForce.formation is wired.
  - Complex toggles (`side.system_complexes`, `side.sector_complexes`)
    flow into `ModifierStack.per_team`. PROJ-271 Phase 2.4 replaced the
    placeholder emission with real stat_keys by loading the complex's
    design JSON, walking its components, and mapping each non-SELF
    scoped ability class to a stat_key (ShieldProjection →
    `shield_bonus_add`; ShieldModifier → `shield_capacity_mult`;
    DamageModifier → `damage_mult`). Scope-driven team routing
    (`enemy_*` → opponent team, else → owner team) is applied at
    compile time per PROJ-271 decisions.md 2026-04-13.
  - `telemetry_level` defaults to NORMAL.
  - `boundary` defaults to `UnboundedRegion` (the existing Battle Setup
    behavior); Phase 3 adds UI for user-configurable boundaries.
  - `end_condition`: caller may pass a pre-built condition (the screen
    already builds one via `_build_end_condition`). If None, we default
    to `TeamEliminatedCondition()` with a tick ceiling.

Critically: the compiler does NOT mutate the input `ShipInstance`
objects. Modifier logic lives in the returned ModifierStack; the engine
applies it at start-of-battle. This is the layer fix for the
"ships pre-mutated before the engine sees them" irregularity.
"""
from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from game.core.json_utils import load_json_required
from game.core.math import Vector2
from game.core.paths import Paths
from game.simulation.battle_spec import (
    BattleSpec,
    CombatPolicies,
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
from game.simulation.combat.ability_stat_registry import (
    ABILITY_STAT_REGISTRY,
    emit_entries_for_ability,
)
from game.simulation.combat.modifier_stack import ModifierEntry, ModifierStack
from game.simulation.combat.telemetry import TelemetryLevel
from game.simulation.systems.battle_end_conditions import (
    AnyCondition,
    TeamEliminatedCondition,
    TickLimitCondition,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.core.registry import GameRegistries
    from game.simulation.systems.battle_end_conditions import IEndCondition
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.ship_instance import ShipInstance
    from game.ui.screens.battle_setup_state import BattleSetupSide, BattleSetupState


# Default safety ceiling — matches the existing Battle Setup default.
_DEFAULT_TICK_LIMIT = 10_000


# PROJ-275 Phase 4: `_NUM_TEAMS` removed. `build_manual_battle_spec` now
# computes `num_teams = len(ui_state.sides)` and emits one `TeamSpec` per
# side. Ring-based entry vectors (`resolve_team_entry_vectors`) replace
# the old hardcoded west/east defaults. 2-side behavior is preserved
# byte-identically.


def build_manual_battle_spec(
    ui_state: "BattleSetupState",
    registries: Optional["GameRegistries"],
    *,
    seed: Optional[int] = None,
    end_condition: Optional["IEndCondition"] = None,
    tick_limit: int = _DEFAULT_TICK_LIMIT,
) -> BattleSpec:
    """Compile `BattleSetupState` into a `BattleSpec`.

    Args:
        ui_state: The current Battle Setup UI state (N sides' fleets
            + system/sector complex toggles).
        registries: GameRegistries for stats access. Accepted for signature
            parity with other compilers; Phase 1 doesn't actively consume
            it (ship materialization happens in the ship_builder at
            `run_battle` time).
        seed: Optional deterministic seed. `None` = engine defaults
            (uses `random.Random()` without a seed, which matches today's
            Battle Setup behavior when the user hasn't specified one).
        end_condition: Pre-built end condition (the existing Battle Setup
            screen constructs one via `_build_end_condition`). If None,
            defaults to `AnyCondition([TickLimitCondition(tick_limit),
            TeamEliminatedCondition()])`.
        tick_limit: Tick ceiling used when `end_condition is None`.

    Returns:
        A populated `BattleSpec`. The caller supplies a `ship_builder`
        closure to `run_battle` that materializes each `ShipSpec` via
        `ShipInstance.to_ship(registries)` (or equivalent).

    PROJ-275 Phase 4: N-team support. Accepts any number of sides in
    `[2, 8]`; raises `ValueError` otherwise.
    """
    num_teams = len(ui_state.sides)
    if num_teams < 2 or num_teams > 8:
        raise ValueError(
            f"build_manual_battle_spec: BattleSetupState must have 2..8 sides; "
            f"got {num_teams}"
        )

    entry_vectors = resolve_team_entry_vectors(team_count=num_teams)

    teams: List[TeamSpec] = []
    for team_id, side in enumerate(ui_state.sides):
        teams.append(
            _build_team_spec(
                side,
                team_id=team_id,
                name=f"Side {team_id}",
                entry_vector=entry_vectors[team_id],
            )
        )

    modifier_stack = _build_modifier_stack(ui_state, registries, num_teams=num_teams)

    effective_end_condition: "IEndCondition"
    if end_condition is not None:
        effective_end_condition = end_condition
    else:
        effective_end_condition = AnyCondition(
            [TickLimitCondition(tick_limit), TeamEliminatedCondition()]
        )

    # Absolute safety ceiling = 2x the tick limit as a last-resort stop.
    absolute_max = max(tick_limit * 2, 1000)

    return BattleSpec(
        seed=seed if seed is not None else 0,
        telemetry_level=TelemetryLevel.NORMAL,
        boundary=UnboundedRegion(),
        end_condition=effective_end_condition,
        absolute_max_ticks=absolute_max,
        teams=tuple(teams),
        modifier_stack=modifier_stack,
        post_battle_hook=None,
    )


# ---------------------------------------------------------------------------
# Team / fleet translation
# ---------------------------------------------------------------------------


# PROJ-275 Phase 4: entry vectors resolved from `resolve_team_entry_vectors`
# based on the team count at compile time. The old hardcoded
# `_SIDE_ENTRY_VECTORS = {0: (-500, 0), 1: (+500, 0)}` is gone — N-team
# ring layout preserves the 2-team west/east defaults byte-identically
# (PROJ-275 Phase 2 ring formula starts at angle 180° so team 0 is always
# at west).


def _build_team_spec(
    side: "BattleSetupSide",
    *,
    team_id: int,
    name: str,
    entry_vector: EntryVector,
) -> TeamSpec:
    task_forces: List[TaskForceSpec] = []
    for fleet in side.fleets:
        task_forces.append(
            _task_force_for_fleet(fleet, team_id=team_id, entry_vector=entry_vector)
        )

    return TeamSpec(
        team_id=team_id,
        name=name,
        entry_vector=entry_vector,
        fleet_hierarchy=tuple(task_forces),
    )


def _task_force_for_fleet(
    fleet: "Fleet",
    *,
    team_id: int,
    entry_vector: EntryVector,
) -> TaskForceSpec:
    """PROJ-269 Phase 4: one TaskForceSpec per Fleet with a single squadron
    whose ships are placed by `FormationResolver` from the team's
    entry_vector + a design-role default (or explicit TF.formation)."""
    formation = _pick_formation_for_fleet(fleet)
    poses = FormationResolver.resolve(
        formation=formation,
        entry_vector=entry_vector,
        boundary=None,
        ships=fleet.ships,
    )
    ships_specs: Tuple[ShipSpec, ...] = tuple(
        _ship_spec_from_instance(ship, poses.get(ship.instance_id))
        for ship in fleet.ships
    )
    return TaskForceSpec(
        task_force_id=f"tf-{team_id}-{fleet.id}",
        formation=formation,
        policies=CombatPolicies(),
        squadrons=(
            SquadronSpec(
                squadron_id=f"sq-{team_id}-{fleet.id}",
                policies=CombatPolicies(),
                ships=ships_specs,
            ),
        ),
    )


def _pick_formation_for_fleet(fleet: "Fleet") -> FormationSpec:
    """Explicit `TaskForce.formation` (first TF with one set) or
    design-role default based on `fleet.ships`."""
    for tf in getattr(fleet, "task_forces", []) or []:
        if getattr(tf, "formation", None) is not None:
            return tf.formation
    return resolve_default_for_task_force(fleet.ships)


def _ship_spec_from_instance(
    ship: "ShipInstance",
    pose: Optional[Tuple[Vector2, float]] = None,
) -> ShipSpec:
    """Build a ShipSpec from a ShipInstance WITHOUT mutating the instance.

    Pose is supplied by `FormationResolver` at compile time (Phase 4).
    Falls back to origin+facing 0 when no pose is available (empty fleet).
    """
    theme_id = "Federation"
    if hasattr(ship, "design_data") and isinstance(ship.design_data, dict):
        theme_id = ship.design_data.get("theme_id", theme_id)

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
        components=(),  # Phase 2 wires ShipInstance.components round-trip.
        # PROJ-274: InstanceBackedMaterializer reads this via duck typing
        # to call `ship.to_ship(position, team_id, registries=...)`.
        instance_ref=ship,
    )


# ---------------------------------------------------------------------------
# Modifier translation — complexes -> ModifierStack entries.
# ---------------------------------------------------------------------------


def _build_modifier_stack(
    ui_state: "BattleSetupState",
    registries: Optional["GameRegistries"],
    *,
    num_teams: int,
) -> ModifierStack:
    """Assemble the ModifierStack from all sides' complex toggles.

    PROJ-271 Phase 2.4: each complex's design JSON is loaded; its
    non-SELF scoped abilities become `ModifierEntry` entries. Scope
    drives team routing — `enemy_*` scopes route to ALL opponent teams,
    everything else to the owner team.

    PROJ-275 Phase 4: iterates `ui_state.sides` (N teams). Enemy-scope
    fan-out goes to every non-owner team via the registry helper.
    """
    per_team: Dict[int, List[ModifierEntry]] = {
        team_id: [] for team_id in range(num_teams)
    }
    for team_id, side in enumerate(ui_state.sides):
        for complex_data in side.system_complexes:
            for route_team, entry in _complex_to_entries(
                complex_data, scope_prefix="system", owner_team=team_id,
                registries=registries, num_teams=num_teams,
            ):
                per_team.setdefault(route_team, []).append(entry)
        for complex_data in side.sector_complexes:
            for route_team, entry in _complex_to_entries(
                complex_data, scope_prefix="sector", owner_team=team_id,
                registries=registries, num_teams=num_teams,
            ):
                per_team.setdefault(route_team, []).append(entry)

    # Trim empty teams so `spec.modifier_stack.per_team` only carries
    # entries that actually matter.
    per_team_tuple: Dict[int, Tuple[ModifierEntry, ...]] = {
        tid: tuple(entries) for tid, entries in per_team.items() if entries
    }
    return ModifierStack(per_team=per_team_tuple, global_=())


def _complex_to_entries(
    complex_data: Dict[str, Any],
    *,
    scope_prefix: str,
    owner_team: int,
    registries: Optional["GameRegistries"],
    num_teams: int,
) -> List[Tuple[int, ModifierEntry]]:
    """Translate one complex toggle into (team_id, ModifierEntry) pairs.

    Loads the complex's design JSON, walks its component list, looks up
    each component's abilities in `registries.components`, and delegates
    to the shared `emit_entries_for_ability` helper for each ability in
    `ABILITY_STAT_REGISTRY` whose scope is non-SELF.

    Returns an empty list if the design file is missing, the registries
    are None, or none of the components carry a mapped ability.
    """
    design_id = complex_data.get("design_id")
    if not design_id:
        return []
    design_data = _load_complex_design(design_id)
    if design_data is None:
        logger.warning(
            "Battle Setup spec compiler: complex design '%s' not found at "
            "%s/%s.json — skipping", design_id, Paths.STARTER_DESIGNS_DIR, design_id,
        )
        return []
    components_registry = registries.get_components() if registries is not None else None
    if not components_registry:
        return []

    display = complex_data.get("display_name", design_id)
    out: List[Tuple[int, ModifierEntry]] = []
    for component_data in _iter_components(design_data):
        comp_id = component_data.get("id")
        if not comp_id:
            continue
        comp_def = components_registry.get(comp_id)
        if comp_def is None:
            continue
        # The registry may hand back either raw dicts (from JSON load)
        # or `Component` instances (whose `.abilities` attribute is the
        # same data). Support both shapes without importing Component
        # (layer boundary: UI should not depend on simulation internals).
        if isinstance(comp_def, dict):
            abilities = comp_def.get("abilities") or {}
        else:
            abilities = getattr(comp_def, "abilities", None) or {}
        for ability_name, ability_data in abilities.items():
            if ability_name not in ABILITY_STAT_REGISTRY:
                continue
            scope_str = _extract_scope(ability_name, ability_data)
            if scope_str == "self":
                # SELF-scoped abilities are component-local, not team-scoped —
                # the engine handles them via the normal ability stack, not
                # the ModifierStack external-bridge.
                continue
            stack_group = (
                ability_data.get("stack_group")
                if isinstance(ability_data, dict)
                else None
            )
            out.extend(
                emit_entries_for_ability(
                    ability_name,
                    ability_data,
                    scope=scope_str,
                    owner_team=owner_team,
                    num_teams=num_teams,
                    source=f"{scope_prefix}:complex:{design_id}:{ability_name}",
                    source_modifier_id=design_id,
                    source_modifier_name=display,
                    stack_group=stack_group,
                )
            )
    return out


def _load_complex_design(design_id: str) -> Optional[Dict[str, Any]]:
    """Load a complex design JSON from `data/designs/<design_id>.json`."""
    filepath = os.path.join(Paths.STARTER_DESIGNS_DIR, f"{design_id}.json")
    if not os.path.exists(filepath):
        return None
    try:
        return load_json_required(filepath)
    except (OSError, ValueError) as e:
        logger.warning(
            "Battle Setup spec compiler: failed to load design '%s': %s",
            design_id, e,
        )
        return None


def _iter_components(design_data: Dict[str, Any]):
    """Yield every `{id: ..., modifiers: ...}` component dict across all layers."""
    layers = design_data.get("layers") or {}
    for layer_components in layers.values():
        if not layer_components:
            continue
        for comp in layer_components:
            if isinstance(comp, dict):
                yield comp


def _extract_scope(ability_name: str, ability_data: Any) -> str:
    """Extract the scope string from an ability's component-JSON entry.

    Abilities in components.json are either primitives (e.g., `10`) or
    dicts. Primitives imply SELF scope. Dicts carry an explicit `scope`
    field. When `scope` is MISSING from the dict, the compiler must
    resolve the ability class's `default_scope` to match runtime behavior —
    `Ability._parse_scope` falls back to `cls.default_scope` when JSON
    omits scope. Hardcoding 'self' silently disagreed with the runtime
    (e.g., `ShieldModifierAbility.default_scope = ALLIED_SYSTEM`), which
    silently dropped complexes whose author forgot to specify scope.

    PROJ-272 Phase 1: resolve class default from `ABILITY_REGISTRY`.
    """
    # Primitive: no scope field possible → SELF (matches runtime's
    # `_parse_scope` behavior on non-dict data).
    if not isinstance(ability_data, dict):
        return "self"

    # Explicit scope in dict takes precedence.
    scope = ability_data.get("scope")
    if scope is not None:
        return scope

    # Missing scope: resolve class-level default to match runtime behavior.
    from game.simulation.components.abilities import get_ability_default_scope
    return get_ability_default_scope(ability_name)


# PROJ-275 Phase 3: `_route_team_for_scope` DELETED.
# Team routing is now handled by `emit_entries_for_ability` in the
# ability-stat registry (PROJ-273) — `num_teams` kwarg + return list of
# `(team_id, entry)` tuples. N-team fan-out (enemy_* scopes → all
# opponents) happens inside the registry helper. The former local wrapper
# hardcoded 2-team routing via `_NUM_TEAMS`.


__all__ = ["build_manual_battle_spec"]
