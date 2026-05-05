"""Focused tests for ShipStatsCalculator branches not covered by snapshots."""
from unittest.mock import MagicMock

from game.simulation.entities.ship_stats import ShipStatsCalculator


class _HangarComponent:
    is_active = True
    is_operational = True
    ability_instances = ()
    abilities = {
        "VehicleLaunch": {"max_launch_mass": 750.0, "cycle_time": 9.0},
        "VehicleStorage": 3,
    }

    def has_ability(self, name: str) -> bool:
        return name in self.abilities

    def get_abilities(self, name: str) -> list:
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
