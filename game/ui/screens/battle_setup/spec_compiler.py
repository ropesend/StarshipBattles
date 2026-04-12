"""Battle Setup spec compiler — BattleSetupState → BattleSpec.

Introduced by PROJ-269 Phase 1 Task 1.8. Translates the fleet-based
Battle Setup UI state into a `BattleSpec` that `run_battle(spec)` can
execute.

Phase 1 scope:
  - Walks `ui_state.side_N.fleets` → ships, producing one
    `TaskForceSpec`-per-fleet with a single `SquadronSpec` underneath.
    Phase 4 refines this once TaskForce.formation is wired.
  - Complex toggles (`side.system_complexes`, `side.sector_complexes`)
    flow into `ModifierStack.per_team` as placeholder entries tagged
    with `source="complex:<design_id>"`. Full effect evaluation replaces
    today's `FleetBattleSetupScreen._apply_complex_modifiers` ship-
    mutation in Phase 5.
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

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from game.core.math import Vector2
from game.simulation.battle_spec import (
    AIPolicy,
    BattleSpec,
    CombatPolicies,
    EntryVector,
    ShipSpec,
    SquadronSpec,
    TaskForceSpec,
    TeamSpec,
)
from game.simulation.combat.boundary import UnboundedRegion
from game.simulation.combat.modifier_stack import ModifierEntry, ModifierStack
from game.simulation.combat.telemetry import TelemetryLevel
from game.simulation.components.modifier_effects import ModifierEffect
from game.simulation.systems.battle_end_conditions import (
    AnyCondition,
    TeamEliminatedCondition,
    TickLimitCondition,
)

if TYPE_CHECKING:
    from game.core.registry import GameRegistries
    from game.simulation.systems.battle_end_conditions import IEndCondition
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.ship_instance import ShipInstance
    from game.ui.screens.battle_setup_state import BattleSetupSide, BattleSetupState


# Default safety ceiling — matches the existing Battle Setup default.
_DEFAULT_TICK_LIMIT = 10_000


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
        ui_state: The current Battle Setup UI state (both sides' fleets
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
    """
    _ = registries  # Phase 1: signature parity only.

    team0 = _build_team_spec(ui_state.side_0, team_id=0, name="Side 0")
    team1 = _build_team_spec(ui_state.side_1, team_id=1, name="Side 1")

    modifier_stack = _build_modifier_stack(ui_state)

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
        teams=(team0, team1),
        modifier_stack=modifier_stack,
        post_battle_hook=None,
    )


# ---------------------------------------------------------------------------
# Team / fleet translation
# ---------------------------------------------------------------------------


def _build_team_spec(
    side: "BattleSetupSide", *, team_id: int, name: str
) -> TeamSpec:
    task_forces: List[TaskForceSpec] = []
    for fleet in side.fleets:
        task_forces.append(_task_force_for_fleet(fleet, team_id=team_id))

    return TeamSpec(
        team_id=team_id,
        name=name,
        entry_vector=EntryVector(origin=Vector2(0.0, 0.0), facing=0.0),
        fleet_hierarchy=tuple(task_forces),
        ai_policy=AIPolicy(),
    )


def _task_force_for_fleet(fleet: "Fleet", *, team_id: int) -> TaskForceSpec:
    """Phase 1 wrapper: one TaskForceSpec per Fleet with a single squadron
    holding every ship. Phase 4 consults `fleet.task_forces` for the real
    hierarchy once formations are wired in."""
    ships_specs: Tuple[ShipSpec, ...] = tuple(
        _ship_spec_from_instance(ship) for ship in fleet.ships
    )
    tf_label = getattr(fleet, "_battle_setup_name", f"fleet-{fleet.id}")
    return TaskForceSpec(
        task_force_id=f"tf-{team_id}-{fleet.id}",
        formation=None,
        policies=CombatPolicies(),
        squadrons=(
            SquadronSpec(
                squadron_id=f"sq-{team_id}-{fleet.id}",
                policies=CombatPolicies(),
                ships=ships_specs,
            ),
        ),
    )


def _ship_spec_from_instance(ship: "ShipInstance") -> ShipSpec:
    """Build a ShipSpec from a ShipInstance WITHOUT mutating the instance.

    Pose fields are placeholders — `run_battle`'s `ship_builder` sets the
    real pose from the spec, and Phase 4's FormationResolver will produce
    the positions at compile time.
    """
    # Pull theme_id from the design data if present; default to Federation.
    theme_id = "Federation"
    if hasattr(ship, "design_data") and isinstance(ship.design_data, dict):
        theme_id = ship.design_data.get("theme_id", theme_id)

    return ShipSpec(
        instance_id=ship.instance_id,
        design_id=ship.design_id,
        theme_id=theme_id,
        name=ship.name,
        position=Vector2(0.0, 0.0),
        angle=0.0,
        velocity=Vector2(0.0, 0.0),
        components=(),  # Phase 2 wires ShipInstance.components round-trip.
    )


# ---------------------------------------------------------------------------
# Modifier translation — complexes -> ModifierStack entries.
# ---------------------------------------------------------------------------


def _build_modifier_stack(ui_state: "BattleSetupState") -> ModifierStack:
    per_team: Dict[int, Tuple[ModifierEntry, ...]] = {}
    for team_id, side in ((0, ui_state.side_0), (1, ui_state.side_1)):
        entries: List[ModifierEntry] = []
        entries.extend(
            _complex_entries(side.system_complexes, scope="system")
        )
        entries.extend(
            _complex_entries(side.sector_complexes, scope="sector")
        )
        if entries:
            per_team[team_id] = tuple(entries)

    return ModifierStack(per_team=per_team, global_=())


def _complex_entries(
    complexes: List[Dict[str, Any]], *, scope: str
) -> List[ModifierEntry]:
    """Translate a list of complex toggles into ModifierEntry objects.

    Phase 1 produces a placeholder `ModifierEffect` for each complex —
    the engine does not yet consume these entries, but their presence
    plus their `source` string is enough for the Phase 1 contract ("no
    ship mutation; modifier presence is recorded").

    Phase 5 replaces this stub with full effect evaluation driven by
    `data/modifiers.json`, replacing `_apply_complex_modifiers`.
    """
    entries: List[ModifierEntry] = []
    for complex_data in complexes:
        design_id = complex_data.get("design_id")
        if not design_id:
            continue
        display = complex_data.get("display_name", design_id)
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
                source=f"{scope}:complex:{design_id}",
                stack_group=None,
                effect=placeholder_effect,
            )
        )
    return entries


__all__ = ["build_manual_battle_spec"]
