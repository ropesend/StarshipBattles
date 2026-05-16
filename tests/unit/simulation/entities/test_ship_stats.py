"""Focused tests for ShipStatsCalculator branches not covered by snapshots."""
from types import SimpleNamespace
from unittest.mock import MagicMock

from game.simulation.entities.ship_stats import ShipStatsCalculator


# PROJ-FMS-C audit Fix 1: migrated off the legacy ``VehicleLaunch`` ability
# to ``TacticalFighterLaunch`` (PROJ-FMS-A Phase 5). The contributor
# now reads ``capacity_per_action`` (additive) and ``cycle_time`` (max)
# plus co-located ``VehicleStorage`` (additive into ``fighter_capacity``).
_TL_ABILITY = SimpleNamespace(capacity_per_action=2, cycle_time=9.0)
_VS_ABILITY = SimpleNamespace(capacity=3)


class _HangarComponent:
    is_active = True
    is_operational = True
    ability_instances = ()

    def has_ability(self, name: str) -> bool:
        return name in {"TacticalFighterLaunch", "VehicleStorage"}

    def get_abilities(self, name: str) -> list:
        if name == "TacticalFighterLaunch":
            return [_TL_ABILITY]
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
    assert ship.fighters_per_wave == 2
    assert ship.launch_cycle == 9.0
