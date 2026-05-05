"""
Launch / hangar stat contributor — fighter capacity, wave size, launch cycle.

Reads typed VehicleLaunchAbility (with ``max_launch_mass``) and
VehicleStorageAbility, fills ``ship.fighter_capacity``,
``fighters_per_wave``, ``fighter_size_cap``, ``launch_cycle``.

PROJ-360 Phase 2: extracted from ``ShipStatsCalculator
._aggregate_hangar_abilities``. PROJ-367 Phase 1: typed-ability migration.
PROJ-367 Phase 2: registered as a default Phase-3 contributor at module
import via ``stat_contributors.registry._seed_builtin_contributors``.

Decision (Task 2.4): VehicleStorage stays gated under VehicleLaunch — the
single ``contribute_vehicle_launch`` reads BOTH abilities. Storage without a
launch bay is meaningless; modders who want to track storage independently
can register their own contributor for ``VehicleStorage``.
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
    """Sum hangar capacity, wave width, max fighter mass, and longest launch cycle.

    Direct mutations on ``ship`` (NOT ``acc`` — the hangar fields live
    directly on ``ship`` as a Phase-3 side-channel):

    - ``fighter_capacity`` (sum)
    - ``fighters_per_wave`` (sum)
    - ``fighter_size_cap`` (max)
    - ``launch_cycle`` (max)

    Reads both VehicleLaunchAbility (capacity / cycle_time / max_launch_mass)
    and VehicleStorageAbility (capacity) on the same component.
    """
    if not comp.has_ability("VehicleLaunch"):
        return

    vl = comp.get_abilities("VehicleLaunch")[0]

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
