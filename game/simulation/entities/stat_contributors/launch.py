"""
Launch / hangar stat contributor — fighter capacity, wave size, launch cycle.

Reads :class:`TacticalFighterLaunchAbility` (PROJ-FMS-A Phase 5) and
:class:`VehicleStorageAbility`, fills ``ship.fighter_capacity``,
``fighters_per_wave``, ``fighter_size_cap``, ``launch_cycle``.

PROJ-360 Phase 2: extracted from ``ShipStatsCalculator
._aggregate_hangar_abilities``. PROJ-367 Phase 1: typed-ability migration.
PROJ-367 Phase 2: registered as a default Phase-3 contributor at module
import via ``stat_contributors.registry._seed_builtin_contributors``.

PROJ-FMS-C audit Fix 1: removed the legacy ``VehicleLaunchAbility`` path.
``TacticalFighterLaunchAbility`` is the only supported tactical-launch
shape; the production caller is :class:`CarrierAIController` (auto-launch)
or a player UI action through :meth:`BattleEngine.launch_fighters_in_battle`.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from game.simulation.entities.stat_contributors.accumulator import StatAccumulator

if TYPE_CHECKING:
    from game.simulation.components.component import Component
    from game.simulation.entities.ship import Ship


def contribute_vehicle_launch(
    ship: "Ship", comp: "Component", acc: StatAccumulator
) -> None:
    """Sum hangar capacity, wave width, and longest launch cycle.

    Direct mutations on ``ship`` (NOT ``acc`` — the hangar fields live
    directly on ``ship`` as a Phase-3 side-channel):

    - ``fighters_per_wave`` (sum of ``capacity_per_action``)
    - ``launch_cycle`` (max of ``cycle_time``)
    - ``fighter_capacity`` (sum of co-located VehicleStorage capacity —
      only counted when at least one TacticalFighterLaunch is present so
      ``VehicleStorage`` on non-launch components stays out)

    PROJ-FMS-C audit Fix 1: the legacy ``VehicleLaunchAbility`` branch
    (with ``max_launch_mass`` and a per-bay wave-of-one assumption) was
    removed. Component designs that previously mounted ``VehicleLaunch``
    must migrate to ``TacticalFighterLaunch`` (+ ``StrategicFighterLaunch``
    for strategic-layer actions) and an explicit ``VehicleBay`` for mass-
    based storage capacity.
    """
    if not comp.has_ability("TacticalFighterLaunch"):
        return

    # Co-located VehicleStorage contributes to fighter_capacity. Storage
    # without a launch bay still rolls up via TacticalFighterLaunch presence
    # on the same component — matches the pre-audit gating shape.
    ship.fighter_capacity += sum(
        getattr(ab, "capacity", 0) for ab in comp.get_abilities("VehicleStorage")
    )

    for tl in comp.get_abilities("TacticalFighterLaunch"):
        cap = int(getattr(tl, "capacity_per_action", 0) or 0)
        if cap > 0:
            ship.fighters_per_wave += cap
        cycle = float(getattr(tl, "cycle_time", 0.0) or 0.0)
        if cycle > ship.launch_cycle:
            ship.launch_cycle = cycle


def contribute_tactical_satellite_launch(
    ship: "Ship", comp: "Component", acc: StatAccumulator
) -> None:
    """PROJ-FMS-D Phase 1: satellite-specific tactical-launch aggregation.

    Mirrors :func:`contribute_vehicle_launch` but writes to a separate
    set of ship fields (``satellites_per_wave``, ``satellite_launch_cycle``,
    ``satellite_capacity``) so a carrier mounting both fighter and
    satellite tactical bays exposes both stat sets independently.
    """
    if not comp.has_ability("TacticalSatelliteLaunch"):
        return

    # Co-located VehicleStorage contributes to satellite_capacity. Mirrors
    # the fighter gating shape: storage on a non-launch component does
    # not roll up unless a TacticalSatelliteLaunch is present on the
    # same component.
    ship.satellite_capacity += sum(
        getattr(ab, "capacity", 0) for ab in comp.get_abilities("VehicleStorage")
    )

    for tl in comp.get_abilities("TacticalSatelliteLaunch"):
        cap = int(getattr(tl, "capacity_per_action", 0) or 0)
        if cap > 0:
            ship.satellites_per_wave += cap
        cycle = float(getattr(tl, "cycle_time", 0.0) or 0.0)
        if cycle > ship.satellite_launch_cycle:
            ship.satellite_launch_cycle = cycle


def contribute_vehicle_bay(
    ship: "Ship", comp: "Component", acc: StatAccumulator
) -> None:
    """PROJ-FMS-A Phase 3 contributor for ``VehicleBay`` abilities.

    Sums ``capacity_mass`` across all active ``VehicleBay`` components
    into ``ship.bay_capacity_mass``. ``bay_current_mass`` is *not* set
    here — it is a strategy-layer property (depends on what's actually
    loaded into ``ShipInstance.carried_items``) and is computed via
    ``ShipCargoManager.get_vehicle_bay_capacity()``. Mirrors
    ``contribute_vehicle_launch`` above.
    """
    if not comp.has_ability("VehicleBay"):
        return
    for ab in comp.get_abilities("VehicleBay"):
        ship.bay_capacity_mass += getattr(ab, "capacity_mass", 0.0)
