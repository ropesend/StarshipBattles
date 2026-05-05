"""
Launch / hangar stat contributor — fighter capacity, wave size, launch cycle.

Reads typed VehicleLaunch / VehicleStorage abilities and fills
``ship.fighter_capacity``, ``fighters_per_wave``, ``fighter_size_cap``,
``launch_cycle``.

PROJ-360 Phase 2: extracted verbatim from ``ShipStatsCalculator
._aggregate_hangar_abilities``. PROJ-367 Phase 1 (closes EXT-07): replaces
``comp.abilities.get("VehicleLaunch"/"VehicleStorage", ...)`` raw-dict
reads with typed ``comp.get_abilities(...)`` access against
``VehicleLaunchAbility`` (extended with ``max_launch_mass``) and
``VehicleStorageAbility``. No semantic change — golden snapshot guards
bit-equality.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from game.simulation.entities.stat_contributors.registry import (
    is_builtin_suppressed_for,
)

if TYPE_CHECKING:
    from game.simulation.components.component import Component
    from game.simulation.entities.ship import Ship


def aggregate_hangar(ship: "Ship", comp: "Component") -> None:
    """Sum hangar capacity, wave width, max fighter mass, and longest launch cycle.

    Direct mutations on ``ship``:

    - ``fighter_capacity`` (sum)
    - ``fighters_per_wave`` (sum)
    - ``fighter_size_cap`` (max)
    - ``launch_cycle`` (max)

    PROJ-360 audit EXT-02: respects ``is_builtin_suppressed_for`` so a
    registered contributor for ``VehicleLaunch`` fully replaces the
    built-in handler.
    """
    if is_builtin_suppressed_for("VehicleLaunch"):
        return
    if not comp.has_ability("VehicleLaunch"):
        return

    # PROJ-367 Phase 1: typed access to VehicleLaunchAbility (extended with
    # ``max_launch_mass``) and VehicleStorageAbility (additive capacity).
    vehicle_launches = comp.get_abilities("VehicleLaunch")
    vl = vehicle_launches[0]

    ship.fighter_capacity += sum(
        getattr(ab, "capacity", 0) for ab in comp.get_abilities("VehicleStorage")
    )
    ship.fighters_per_wave += 1

    max_mass = getattr(vl, "max_launch_mass", 0)
    if max_mass > ship.fighter_size_cap:
        ship.fighter_size_cap = max_mass

    cycle = getattr(vl, "cycle_time", 5.0)
    if cycle > ship.launch_cycle:
        ship.launch_cycle = cycle
