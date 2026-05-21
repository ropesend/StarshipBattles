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


def _contribute_launch(
    ship: "Ship",
    comp: "Component",
    *,
    launch_ability: str,
    capacity_field: str,
    per_wave_field: str,
    cycle_field: str,
    rate_field: str,
) -> None:
    """Cluster 19 (PROJ-465): shared tactical-launch aggregation body.

    The fighter and satellite contributors are structurally identical,
    differing only in the gating ability name and the four ship fields
    they accumulate into. Behaviour, arithmetic, gating, and iteration
    order are preserved exactly — the only change is reading/writing the
    target fields by name via ``getattr``/``setattr``.
    """
    if not comp.has_ability(launch_ability):
        return

    # Co-located VehicleStorage contributes to the capacity field. Storage
    # without a launch bay still rolls up via launch-ability presence on
    # the same component — matches the pre-audit gating shape.
    setattr(
        ship,
        capacity_field,
        getattr(ship, capacity_field)
        + sum(
            getattr(ab, "capacity", 0)
            for ab in comp.get_abilities("VehicleStorage")
        ),
    )

    for tl in comp.get_abilities(launch_ability):
        cap = int(getattr(tl, "capacity_per_action", 0) or 0)
        if cap > 0:
            setattr(ship, per_wave_field, getattr(ship, per_wave_field) + cap)
        cycle = float(getattr(tl, "cycle_time", 0.0) or 0.0)
        if cycle > getattr(ship, cycle_field):
            setattr(ship, cycle_field, cycle)
        rate = float(getattr(tl, "launch_rate_tons_per_sec", 0.0) or 0.0)
        if rate > 0:
            setattr(ship, rate_field, getattr(ship, rate_field) + rate)


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
    _contribute_launch(
        ship,
        comp,
        launch_ability="TacticalFighterLaunch",
        capacity_field="fighter_capacity",
        per_wave_field="fighters_per_wave",
        cycle_field="launch_cycle",
        rate_field="fighter_launch_rate_tons_per_sec",
    )


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
    _contribute_launch(
        ship,
        comp,
        launch_ability="TacticalSatelliteLaunch",
        capacity_field="satellite_capacity",
        per_wave_field="satellites_per_wave",
        cycle_field="satellite_launch_cycle",
        rate_field="satellite_launch_rate_tons_per_sec",
    )


def contribute_vehicle_bay(
    ship: "Ship", comp: "Component", acc: StatAccumulator
) -> None:
    """PROJ-FMS-A Phase 3 contributor for ``VehicleBay`` abilities.

    Sums ``capacity_mass`` across all active ``VehicleBay`` components
    into ``ship.bay_capacity_mass``. ``bay_current_mass`` is *not* set
    here — it is a strategy-layer property (depends on what's actually
    loaded into ``ShipInstance.bay_inventory.bay``) and is computed via
    ``ShipCargoManager.get_vehicle_bay_capacity()``. Mirrors
    ``contribute_vehicle_launch`` above.
    """
    if not comp.has_ability("VehicleBay"):
        return
    for ab in comp.get_abilities("VehicleBay"):
        ship.bay_capacity_mass += getattr(ab, "capacity_mass", 0.0)
