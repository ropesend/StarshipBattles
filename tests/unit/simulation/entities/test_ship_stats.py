"""Focused tests for ShipStatsCalculator branches not covered by snapshots."""
from types import SimpleNamespace
from unittest.mock import MagicMock

from game.simulation.entities.ship_stats import ShipStatsCalculator


# PROJ-367 Phase 1: VehicleLaunch / VehicleStorage are now typed abilities.
# The fixture mirrors the typed-ability access path used by
# `launch.aggregate_hangar` (no more raw `comp.abilities` dict reads).
_VL_ABILITY = SimpleNamespace(
    capacity=0,
    cycle_time=9.0,
    max_launch_mass=750.0,
    fighter_class="Fighter (Small)",
)
_VS_ABILITY = SimpleNamespace(capacity=3)


class _HangarComponent:
    is_active = True
    is_operational = True
    ability_instances = ()

    def has_ability(self, name: str) -> bool:
        return name in {"VehicleLaunch", "VehicleStorage"}

    def get_abilities(self, name: str) -> list:
        if name == "VehicleLaunch":
            return [_VL_ABILITY]
        if name == "VehicleStorage":
            return [_VS_ABILITY]
        return []


def test_stats_aggregation_routes_hangar_abilities_to_launch_contributor() -> None:
    ship = MagicMock()
    ship.fighter_capacity = 0
    ship.fighters_per_wave = 0
    ship.fighter_size_cap = 0
    ship.launch_cycle = 0
    ship.max_targets = 1
    ship.resources = MagicMock()
    ship.external_stats = {}

    ShipStatsCalculator({}, planetary_resource_ids=[])._phase_stats_aggregation(
        ship,
        [_HangarComponent()],
    )

    assert ship.fighter_capacity == 3
    assert ship.fighters_per_wave == 1
    assert ship.fighter_size_cap == 750.0
    assert ship.launch_cycle == 9.0
