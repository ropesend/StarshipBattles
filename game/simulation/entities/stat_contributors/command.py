"""
Command / control stat contributor — priority sort + multiplex tracking + maintenance alloc.

Command-and-control concerns:

- Component priority for maintenance allocation (CommandAndControl > engines >
  weapons > everything else).
- ``MultiplexTracking`` ability — sets ``ship.max_targets`` to the highest
  multiplex value across active components.
- Maintenance allocation across components (deactivates components that
  can't be maintained).

PROJ-360 Phase 2: extracted from ``ShipStatsCalculator
._priority_sort_key`` + ``_phase_resource_allocation`` + the inline
multiplex block. PROJ-367 Phase 1: typed MultiplexTrackingAbility access.
PROJ-367 Phase 2: ``contribute_multiplex_tracking`` registered as a
default Phase-3 contributor at module import. QA Observation 5
maintenance abstraction: per-component requirement now comes from
``RequiresMaintenance``; per-ship supply now comes from
``ProvidesMaintenance``. Crew and life support are reported but no
longer silently clamp each other at runtime — the validator rejects
crew-without-life-support designs at design time.
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
    available_maintenance: int,
    vehicle_classes: dict,
) -> None:
    """Phase 2 of the calculator: allocate maintenance across components.

    Records crew, life-support, and maintenance supply on the ship for UI
    consumption, then allocates maintenance per-component in priority
    order. Components that can't be maintained are deactivated with
    ``ComponentStatus.NO_CREW``.

    Mutations:

    - ``ship.crew_onboard`` / ``ship.crew_required`` / ``ship.max_targets``
    - ``ship.max_mass_budget``
    - Sorts ``component_pool`` in place by ``lookup_crew_priority``
    - Deactivates components that can't be maintained (sets
      ``ComponentStatus.NO_CREW``)

    Note: ``ship.crew_required`` historically stored "crew the ship needs
    to run"; after QA Observation 5 it stores the total maintenance
    demand (sum of ``RequiresMaintenance`` across active components).
    The field name is retained to limit UI/test ripple while the
    semantic change percolates.
    """
    ship.crew_onboard = available_crew
    ship.crew_required = 0
    ship.max_targets = CombatConstants.DEFAULT_MAX_TARGETS

    ship.max_mass_budget = vehicle_classes.get(ship.ship_class, {}).get(
        "max_mass", DEFAULT_MAX_MASS
    )

    # QA Observation 5: no silent runtime degradation by life-support shortage.
    # The validator rejects designs where CrewCapacity > LifeSupportCapacity
    # at design time, so available_life_support is informational here.
    _ = available_life_support
    remaining_maintenance = available_maintenance

    component_pool.sort(key=lookup_crew_priority)

    for comp in component_pool:
        if not comp.is_active:
            continue

        req_maint = 0
        for ab in comp.get_abilities("RequiresMaintenance"):
            req_maint += ab.amount

        ship.crew_required += req_maint

        if req_maint > 0:
            if remaining_maintenance >= req_maint:
                remaining_maintenance -= req_maint
            else:
                comp.is_active = False
                comp.status = ComponentStatus.NO_CREW
