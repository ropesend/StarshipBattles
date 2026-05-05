"""
Movement stat contributor — propulsion, turn rate, warp, strategic movement.

Owns the per-component aggregation that yields:

- thrust (CombatPropulsion)
- strategic movement (StrategicMovement)
- warp tonnage / warp energy cost (WarpJump)
- turn speed and maneuver points (ManeuveringThruster)

PROJ-360 Phase 2: extracted from `ShipStatsCalculator
._aggregate_propulsion_abilities`. PROJ-367 Phase 2: split into per-ability
``contribute_*`` functions that the registry seeds as default Phase-3
contributors at module import.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from game.simulation.entities.stat_contributors.accumulator import StatAccumulator
from game.simulation.interfaces import is_warp_jump

if TYPE_CHECKING:
    from game.simulation.components.component import Component
    from game.simulation.entities.ship import Ship


# ---------------------------------------------------------------------------
# Per-ability contributors (registered as Phase-3 defaults at import via
# ``stat_contributors.registry._seed_builtin_contributors``). The
# ``ship`` parameter is unused by movement contributors but kept for
# signature uniformity across the registry.
#
# PROJ-367 Phase 3: ``acc`` is a typed ``StatAccumulator`` dataclass.
# Misspelled scalar/map fields raise ``AttributeError`` at runtime
# (``slots=True`` semantics) instead of silently producing zero.
# ---------------------------------------------------------------------------


def contribute_combat_propulsion(
    ship: "Ship", comp: "Component", acc: StatAccumulator
) -> None:
    """Sum CombatPropulsion thrust into ``acc.thrust``."""
    for ab in comp.get_abilities("CombatPropulsion"):
        acc.thrust += ab.thrust_force


def contribute_strategic_movement(
    ship: "Ship", comp: "Component", acc: StatAccumulator
) -> None:
    """Sum StrategicMovement points into ``acc.strategic_movement``."""
    for ab in comp.get_abilities("StrategicMovement"):
        acc.strategic_movement += ab.movement_points


def contribute_warp_jump(
    ship: "Ship", comp: "Component", acc: StatAccumulator
) -> None:
    """Track warp tonnage (max) + warp energy cost (sum) for WarpJump abilities."""
    for ab in comp.get_abilities("WarpJump"):
        if is_warp_jump(ab):
            if ab.max_tonnage > acc.warp_max_tonnage:
                acc.warp_max_tonnage = ab.max_tonnage
            acc.warp_energy_cost += ab.energy_cost


def contribute_maneuvering_thruster(
    ship: "Ship", comp: "Component", acc: StatAccumulator
) -> None:
    """Sum ManeuveringThruster turn rate into ``acc.turn_speed`` + ``maneuver_points``."""
    for ab in comp.get_abilities("ManeuveringThruster"):
        acc.turn_speed += ab.turn_rate
        acc.maneuver_points += ab.turn_rate
