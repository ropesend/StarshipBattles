"""Strategy PostBattleHook — writes BattleOutcome back to ShipInstance / Fleet / Empire.

Introduced by PROJ-269 Phase 2 Task 2.5. Replaces the legacy
`FleetBattleAdapter.update_from_battle_results` side-channel with a
first-class `BattleSpec.post_battle_hook` callable that
`run_battle` invokes with the final outcome.

Semantics per `ShipStatus`:
  - **SURVIVED** / **DERELICT**: update `ShipInstance.components` from
    `ShipOutcome.components` (per-instance HP round-trip); keep the
    ship in its fleet; flip `is_alive` / `is_derelict` flags.
  - **DESTROYED**: remove from parent `Fleet.ships`. Legacy
    `component_damage` is cleared.
  - **RETREATED**: remove from parent `Fleet.ships` (MVP — see
    PROJ-269 decisions.md entry for the "retreated ships disperse"
    choice). Later projects may introduce a scattered-remnant fleet.

Empty `Fleet`s are pruned from `Empire.fleets` when an empires dict is
passed. Task-force / squadron hierarchy pruning is a later concern;
Phase 1 compilers wrap fleets in a single TF/squadron that's not
authoritatively used by strategy data today.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional

from game.strategy.data.component_state import (
    ComponentState,
    component_state_key,
)

if TYPE_CHECKING:
    from game.simulation.battle_outcome import BattleOutcome, ShipOutcome
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.ship_instance import ShipInstance

logger = logging.getLogger(__name__)


def apply_outcome_to_fleets(
    outcome: "BattleOutcome",
    *,
    fleets_by_team_id: Mapping[int, List["Fleet"]],
    empires: Optional[Mapping[int, Any]] = None,
) -> None:
    """Apply a `BattleOutcome` to its originating fleets.

    Args:
        outcome: The `BattleOutcome` returned by `run_battle`.
        fleets_by_team_id: The fleets that participated, keyed by the
            team_id they were assigned during compilation. The compiler
            (`build_strategy_battle_spec`) closes over this mapping
            when it builds the hook.
        empires: Optional team_id -> Empire mapping. When provided,
            fleets that end the battle with zero ships are removed
            from the owning empire's `fleets` list.

    Notes:
        - Iterates through each TeamOutcome's ships once, dispatching
          on ShipStatus. Looks up the ShipInstance by `instance_id`
          via a single linear scan of the team's fleets — fleet sizes
          are small so this is fine.
        - Missing ShipInstance (orphan outcome entry) is logged and
          skipped rather than raised — outcome correctness is the
          engine's job; the hook must not die mid-update.
    """
    for team in outcome.teams:
        fleets = fleets_by_team_id.get(team.team_id, [])
        if not fleets:
            continue
        for ship_outcome in team.ships:
            instance, owning_fleet = _find_instance_by_id(
                ship_outcome.instance_id, fleets
            )
            if instance is None or owning_fleet is None:
                logger.warning(
                    "apply_outcome_to_fleets: no ShipInstance matches "
                    f"instance_id={ship_outcome.instance_id!r} on team {team.team_id}. "
                    "Dropping this outcome entry."
                )
                continue
            _apply_single_outcome(ship_outcome, instance, owning_fleet)

    # Prune empty fleets.
    if empires is not None:
        _prune_empty_fleets(fleets_by_team_id, empires)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _find_instance_by_id(
    instance_id: str, fleets: List["Fleet"]
) -> "tuple[Optional[ShipInstance], Optional[Fleet]]":
    for fleet in fleets:
        for ship in fleet.ships:
            if ship.instance_id == instance_id:
                return ship, fleet
    return None, None


def _apply_single_outcome(
    ship_outcome: "ShipOutcome",
    instance: "ShipInstance",
    owning_fleet: "Fleet",
) -> None:
    # Late import — the outcome dataclass has an enum we need by value,
    # but avoiding a top-level sim import keeps strategy→simulation deps
    # explicit (the hook is run from the simulation layer already — this
    # import is effectively downstream of the spec carrier).
    from game.simulation.battle_outcome import ShipStatus

    status = ship_outcome.status
    if status in (ShipStatus.SURVIVED, ShipStatus.DERELICT):
        _apply_survivor_outcome(ship_outcome, instance, status == ShipStatus.DERELICT)
        return
    if status == ShipStatus.DESTROYED:
        _remove_ship(owning_fleet, instance)
        instance.is_alive = False
        instance.current_hp = 0
        return
    if status == ShipStatus.RETREATED:
        # PROJ-269 Phase 2 decision: retreat = remove from fleet (MVP).
        _remove_ship(owning_fleet, instance)
        return
    # Unknown status — log and skip.
    logger.warning(
        f"apply_outcome_to_fleets: unknown ShipStatus {status!r} for "
        f"instance_id={ship_outcome.instance_id!r}; skipping."
    )


def _apply_survivor_outcome(
    ship_outcome: "ShipOutcome",
    instance: "ShipInstance",
    is_derelict: bool,
) -> None:
    """Write outcome per-component HP into instance.components + flags."""
    # Build a fresh components dict from the outcome — authoritative.
    new_components: Dict[str, ComponentState] = {}
    for cs in ship_outcome.components:
        key = component_state_key(cs.component_id, cs.instance_index)
        new_components[key] = ComponentState(
            component_id=cs.component_id,
            instance_index=cs.instance_index,
            current_hp=float(cs.current_hp),
            is_active=bool(cs.is_active),
        )
    instance.components = new_components
    # Mirror legacy `component_damage` (first-instance granularity) for
    # backwards-compat stat-calc code paths. Reset and rebuild.
    instance.component_damage = {}
    for cs in ship_outcome.components:
        # Only record damage (< full HP would normally be inferred from
        # the design max; we record any non-zero outcome HP keyed by id
        # without recomputing max_hp here — callers of component_damage
        # accept any current_hp value).
        if cs.component_id not in instance.component_damage:
            instance.component_damage[cs.component_id] = int(cs.current_hp)

    # Status flags.
    instance.is_alive = True
    instance.is_derelict = bool(is_derelict)
    # current_hp (ship-level summary) — leave at None (full) unless we
    # have evidence otherwise. The engine-side summary HP propagates
    # through the legacy `ShipInstanceBridge.update_from_ship` path when
    # the caller uses that; for the PROJ-269 hook path we rely on
    # per-component state for truth.
    instance.battles_survived += 1
    instance.invalidate_stats_cache()


def _remove_ship(fleet: "Fleet", instance: "ShipInstance") -> None:
    try:
        fleet.remove_ship(instance)
    except (ValueError, AttributeError) as e:
        logger.warning(
            f"Could not remove ship {instance.instance_id!r} from fleet "
            f"{fleet.id}: {e}"
        )


def _prune_empty_fleets(
    fleets_by_team_id: Mapping[int, List["Fleet"]],
    empires: Mapping[int, Any],
) -> None:
    for team_id, fleets in fleets_by_team_id.items():
        empire = empires.get(team_id)
        if empire is None:
            continue
        empire_fleets = getattr(empire, "fleets", None)
        if empire_fleets is None:
            continue
        for fleet in list(fleets):
            if not fleet.ships and fleet in empire_fleets:
                try:
                    empire_fleets.remove(fleet)
                except ValueError:
                    logger.warning(
                        f"Fleet {fleet.id} not found on empire while pruning."
                    )


__all__ = ["apply_outcome_to_fleets"]
