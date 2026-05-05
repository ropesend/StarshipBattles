"""
Movement stat contributor — propulsion, turn rate, warp, strategic movement.

Owns the per-component aggregation that yields:

- thrust (CombatPropulsion)
- strategic movement (StrategicMovement)
- warp tonnage / warp energy cost (WarpJump)
- turn speed and maneuver points (ManeuveringThruster)

PROJ-360 Phase 2: extracted verbatim from `ShipStatsCalculator
._aggregate_propulsion_abilities`. No semantic change — golden snapshot
guards bit-equality.
"""
from __future__ import annotations

from typing import Any, Dict, TYPE_CHECKING

from game.simulation.entities.stat_contributors.registry import (
    is_builtin_suppressed_for,
)
from game.simulation.interfaces import is_warp_jump

if TYPE_CHECKING:
    from game.simulation.components.component import Component


def aggregate_propulsion(comp: "Component", acc: Dict[str, Any]) -> None:
    """Aggregate CombatPropulsion, StrategicMovement, WarpJump, ManeuveringThruster.

    Caller passes the shared accumulator from
    ``ShipStatsCalculator._phase_stats_aggregation``. Mutations:

    - ``acc['thrust']`` — sum of CombatPropulsion.thrust_force
    - ``acc['strategic_movement']`` — sum of StrategicMovement.movement_points
    - ``acc['warp_max_tonnage']`` — max over WarpJump.max_tonnage
    - ``acc['warp_energy_cost']`` — sum of WarpJump.energy_cost
    - ``acc['turn_speed']`` — sum of ManeuveringThruster.turn_rate
    - ``acc['maneuver_points']`` — sum of ManeuveringThruster.turn_rate

    PROJ-360 audit EXT-02: each ability block respects
    ``is_builtin_suppressed_for`` so a registered contributor can fully
    take over an ability without double-counting.
    """
    # Thrust from CombatPropulsion abilities
    if not is_builtin_suppressed_for("CombatPropulsion"):
        for ab in comp.get_abilities("CombatPropulsion"):
            acc["thrust"] += ab.thrust_force

    # Strategic movement from StrategicMovement abilities
    if not is_builtin_suppressed_for("StrategicMovement"):
        for ab in comp.get_abilities("StrategicMovement"):
            acc["strategic_movement"] += ab.movement_points

    # WarpJump capability — use the largest warp drive
    if not is_builtin_suppressed_for("WarpJump"):
        for ab in comp.get_abilities("WarpJump"):
            if is_warp_jump(ab):
                if ab.max_tonnage > acc["warp_max_tonnage"]:
                    acc["warp_max_tonnage"] = ab.max_tonnage
                # Accumulate energy costs from all warp drives
                acc["warp_energy_cost"] += ab.energy_cost

    # Turn speed from ManeuveringThruster abilities
    if not is_builtin_suppressed_for("ManeuveringThruster"):
        for ab in comp.get_abilities("ManeuveringThruster"):
            acc["turn_speed"] += ab.turn_rate
            acc["maneuver_points"] += ab.turn_rate
