"""
Launch / hangar stat contributor — fighter capacity, wave size, launch cycle.

Reads VehicleLaunch / VehicleStorage abilities (still raw-dict-shaped in
the data model — there is no `VehicleLaunchAbility` class) and fills
``ship.fighter_capacity``, ``fighters_per_wave``, ``fighter_size_cap``,
``launch_cycle``.

PROJ-360 Phase 2: extracted verbatim from ``ShipStatsCalculator
._aggregate_hangar_abilities``. No semantic change — golden snapshot
guards bit-equality.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

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
    """
    if not (comp.has_ability("VehicleLaunch") or "VehicleLaunch" in comp.abilities):
        return

    vl = comp.abilities.get("VehicleLaunch", {})
    ship.fighter_capacity += comp.abilities.get("VehicleStorage", 0)
    ship.fighters_per_wave += 1

    max_mass = vl.get("max_launch_mass", 0) if isinstance(vl, dict) else 0
    if max_mass > ship.fighter_size_cap:
        ship.fighter_size_cap = max_mass

    cycle = vl.get("cycle_time", 5.0) if isinstance(vl, dict) else 5.0
    if cycle > ship.launch_cycle:
        ship.launch_cycle = cycle
