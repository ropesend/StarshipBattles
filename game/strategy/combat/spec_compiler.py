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
        sector=sector, system=system, empires=empires, team_count=len(teams)
    )

    boundary = None
    if settings is not None:
        boundary = getattr(settings, "combat_boundary_default", None)
    if boundary is None:
        boundary = UnboundedRegion()

    effective_end_condition: "IEndCondition" = (
        end_condition if end_condition is not None else TeamEliminatedCondition()
    )

    return BattleSpec(
        seed=seed if seed is not None else 0,
        telemetry_level=TelemetryLevel.NORMAL,
        boundary=boundary,
        end_condition=effective_end_condition,
        absolute_max_ticks=_DEFAULT_ABSOLUTE_MAX_TICKS,
        teams=tuple(teams),
        modifier_stack=modifier_stack,
        post_battle_hook=_noop_hook,
    )


# ---------------------------------------------------------------------------
# Fleet translation
# ---------------------------------------------------------------------------


def _team_spec_for_fleet(fleet: "Fleet", *, team_id: int) -> TeamSpec:
    ships: Tuple[ShipSpec, ...] = tuple(
        _ship_spec_from_instance(ship) for ship in fleet.ships
    )
    task_force = TaskForceSpec(
        task_force_id=f"tf-fleet-{fleet.id}",
        formation=None,
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
        entry_vector=EntryVector(origin=Vector2(0.0, 0.0), facing=0.0),
        fleet_hierarchy=(task_force,),
        ai_policy=AIPolicy(),
    )


def _ship_spec_from_instance(ship: "ShipInstance") -> ShipSpec:
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
        components=(),  # Phase 2 wires ShipInstance.components persistence.
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

    per_team: Dict[int, Tuple[ModifierEntry, ...]] = {}
    # Empire modifiers — empires is keyed by team_id (or empire id).
    # Phase 1 matches them positionally.
    for team_id in range(team_count):
        empire = empires.get(team_id)
        if empire is None:
            continue
        empire_entries = list(
            _entries_from_modifier_source(
                empire, source_prefix="empire", attr_name="combat_modifiers"
            )
        )
        if empire_entries:
            per_team[team_id] = tuple(empire_entries)

    return ModifierStack(per_team=per_team, global_=tuple(global_entries))


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
