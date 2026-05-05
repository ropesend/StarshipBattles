"""
Command / control stat contributor — priority sort + multiplex tracking + crew alloc.

Command-and-control concerns:

- Component priority for crew allocation (CommandAndControl > engines >
  weapons > everything else).
- ``MultiplexTracking`` ability — sets ``ship.max_targets`` to the highest
  multiplex value across active components.
- Crew + life-support allocation across components (deactivates components
  that can't be staffed).

PROJ-360 Phase 2: extracted verbatim from ``ShipStatsCalculator
._priority_sort_key``, the inline multiplex block in
``_phase_stats_aggregation``, and ``_phase_resource_allocation``. No
semantic change — golden snapshot guards bit-equality.
"""
from __future__ import annotations

from typing import List, TYPE_CHECKING

from game.core.constants import CombatConstants
from game.simulation.components.component_constants import ComponentStatus
from game.simulation.physics_constants import DEFAULT_MAX_MASS

if TYPE_CHECKING:
    from game.simulation.components.component import Component
    from game.simulation.entities.ship import Ship


def priority_sort_key(c: "Component") -> int:
    """Sort key for the resource-allocation phase.

    Lower = higher priority. Bridge first, then movement, then weapons,
    then everything else.
    """
    if c.has_ability("CommandAndControl"):
        return 0  # Bridge (Command)
    if c.has_ability("CombatPropulsion") or c.has_ability("ManeuveringThruster"):
        return 1  # Engines (Movement)
    if c.has_ability("WeaponAbility"):
        return 2  # Weapons (Offense)
    return 3  # Others


def track_multiplex(ship: "Ship", comp: "Component") -> None:
    """Bump ``ship.max_targets`` if this component's MultiplexTracking exceeds it.

    Uses the raw ``abilities`` dict (legacy semantics) — a 0 value means no
    contribution and is filtered out.
    """
    mt = comp.abilities.get("MultiplexTracking", 0)
    if mt > 0 and mt > ship.max_targets:
        ship.max_targets = mt


def allocate_crew_and_life_support(
    ship: "Ship",
    component_pool: List["Component"],
    available_crew: int,
    available_life_support: int,
    vehicle_classes: dict,
) -> None:
    """Phase 2 of the calculator: allocate crew/life support across components.

    Mutations:

    - ``ship.crew_onboard`` / ``ship.crew_required`` / ``ship.max_targets``
    - ``ship.max_mass_budget``
    - Sorts ``component_pool`` in place by ``priority_sort_key``
    - Deactivates components that can't be crewed (sets
      ``ComponentStatus.NO_CREW``)
    """
    ship.crew_onboard = available_crew
    ship.crew_required = 0
    ship.max_targets = CombatConstants.DEFAULT_MAX_TARGETS  # Reset to default

    # Centralize mass budget lookup
    ship.max_mass_budget = vehicle_classes.get(ship.ship_class, {}).get(
        "max_mass", DEFAULT_MAX_MASS
    )

    # Effective Crew is limited by Life Support
    effective_crew = min(available_crew, available_life_support)

    # Priority sort using helper
    component_pool.sort(key=priority_sort_key)

    for comp in component_pool:
        if not comp.is_active:
            continue  # Already damaged

        # Check Crew Requirement
        req_crew = 0
        for ab in comp.get_abilities("CrewRequired"):
            req_crew += ab.amount

        ship.crew_required += req_crew

        if req_crew > 0:
            if effective_crew >= req_crew:
                effective_crew -= req_crew
            else:
                comp.is_active = False
                comp.status = ComponentStatus.NO_CREW
