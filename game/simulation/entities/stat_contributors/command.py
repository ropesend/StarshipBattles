"""
Command / control stat contributor — priority sort + multiplex tracking + crew alloc.

Command-and-control concerns:

- Component priority for crew allocation (CommandAndControl > engines >
  weapons > everything else).
- ``MultiplexTracking`` ability — sets ``ship.max_targets`` to the highest
  multiplex value across active components.
- Crew + life-support allocation across components (deactivates components
  that can't be staffed).

PROJ-360 Phase 2: extracted from ``ShipStatsCalculator
._priority_sort_key`` + ``_phase_resource_allocation`` + the inline
multiplex block. PROJ-367 Phase 1: typed MultiplexTrackingAbility access.
PROJ-367 Phase 2: ``contribute_multiplex_tracking`` registered as a
default Phase-3 contributor at module import.
"""
from __future__ import annotations

from typing import List, TYPE_CHECKING

from game.core.constants import CombatConstants
from game.simulation.components.component_constants import ComponentStatus
from game.simulation.entities.stat_contributors.accumulator import StatAccumulator
from game.simulation.entities.stat_contributors.registry import (
    lookup_crew_priority,
)
from game.simulation.physics_constants import DEFAULT_MAX_MASS

if TYPE_CHECKING:
    from game.simulation.components.component import Component
    from game.simulation.entities.ship import Ship


def contribute_multiplex_tracking(
    ship: "Ship", comp: "Component", acc: StatAccumulator
) -> None:
    """Bump ``ship.max_targets`` if this component's MultiplexTracking exceeds it.

    PROJ-367 Phase 1: reads slots via the typed
    ``MultiplexTrackingAbility.slots`` attribute (sums across instances on
    the same component, then takes the max against ``ship.max_targets`` —
    legacy semantics: 0 means no contribution).
    """
    mt = sum(getattr(ab, "slots", 0) for ab in comp.get_abilities("MultiplexTracking"))
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
    - Sorts ``component_pool`` in place by ``lookup_crew_priority``
    - Deactivates components that can't be crewed (sets
      ``ComponentStatus.NO_CREW``)
    """
    ship.crew_onboard = available_crew
    ship.crew_required = 0
    ship.max_targets = CombatConstants.DEFAULT_MAX_TARGETS

    ship.max_mass_budget = vehicle_classes.get(ship.ship_class, {}).get(
        "max_mass", DEFAULT_MAX_MASS
    )

    effective_crew = min(available_crew, available_life_support)

    component_pool.sort(key=lookup_crew_priority)

    for comp in component_pool:
        if not comp.is_active:
            continue

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
