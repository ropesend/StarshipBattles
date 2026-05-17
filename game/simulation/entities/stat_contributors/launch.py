"""
Launch / hangar stat contributor — fighter capacity + tactical mass rate.

QA-C: replaced the legacy aggregated ``fighters_per_wave`` /
``launch_cycle`` headline (count + cooldown) with
``fighter_launch_rate_tons_per_sec`` — the sum of
``TacticalFighterLaunchAbility.launch_rate_tons_per_sec`` across all
launch components on the ship. The same change applies to satellites
via ``satellite_launch_rate_tons_per_sec``.

PROJ-FMS-A Phase 3 ``VehicleBay`` capacity aggregation still rolls up
into ``ship.bay_capacity_mass``.
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
    """Sum tactical fighter-launch rate and co-located VehicleStorage capacity.

    Direct mutations on ``ship`` (NOT ``acc`` — the hangar fields live
    directly on ``ship`` as a Phase-3 side-channel):

    - ``fighter_launch_rate_tons_per_sec`` (sum of
      ``TacticalFighterLaunch.launch_rate_tons_per_sec``)
    - ``fighter_capacity`` (sum of co-located VehicleStorage capacity —
      only counted when at least one TacticalFighterLaunch is present so
      ``VehicleStorage`` on non-launch components stays out)

    QA-C: the legacy count-of-fighters-per-wave + cooldown headline
    fields (``fighters_per_wave`` / ``launch_cycle``) are retained on
    the ship for backwards-compatible UI rendering but they're now
    derived stats — ``fighters_per_wave`` mirrors the sum of
    ``capacity_per_action`` (unchanged), ``launch_cycle`` mirrors the
    max ``cycle_time``. The authoritative tactical-throughput dial is
    ``fighter_launch_rate_tons_per_sec``.
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
        rate = float(getattr(tl, "launch_rate_tons_per_sec", 0.0) or 0.0)
        if rate > 0:
            ship.fighter_launch_rate_tons_per_sec += rate


def contribute_tactical_satellite_launch(
    ship: "Ship", comp: "Component", acc: StatAccumulator
) -> None:
    """Satellite-specific tactical-launch aggregation (mirror of fighter path).

    Mirrors :func:`contribute_vehicle_launch` but writes to a separate
    set of ship fields (``satellites_per_wave``, ``satellite_launch_cycle``,
    ``satellite_capacity``, ``satellite_launch_rate_tons_per_sec``) so
    a carrier mounting both fighter and satellite tactical bays exposes
    both stat sets independently.
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
        rate = float(getattr(tl, "launch_rate_tons_per_sec", 0.0) or 0.0)
        if rate > 0:
            ship.satellite_launch_rate_tons_per_sec += rate


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
