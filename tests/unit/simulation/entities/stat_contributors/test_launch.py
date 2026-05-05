"""
Unit tests for the launch / hangar stat contributor.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.simulation.entities.stat_contributors import launch


def _make_ship():
    ship = MagicMock()
    ship.fighter_capacity = 0
    ship.fighters_per_wave = 0
    ship.fighter_size_cap = 0
    ship.launch_cycle = 0
    return ship


def _make_hangar_component(*, vehicle_launch: dict | None, vehicle_storage: int = 0):
    """Component with VehicleLaunch dict ability + VehicleStorage int ability."""
    comp = MagicMock()
    abilities = {}
    if vehicle_launch is not None:
        abilities["VehicleLaunch"] = vehicle_launch
    if vehicle_storage:
        abilities["VehicleStorage"] = vehicle_storage
    comp.abilities = abilities
    comp.has_ability = lambda name: name in abilities
    return comp


class TestAggregateHangar:
    def test_no_hangar_ability_is_noop(self):
        ship = _make_ship()
        comp = _make_hangar_component(vehicle_launch=None)
        launch.aggregate_hangar(ship, comp)
        assert ship.fighter_capacity == 0
        assert ship.fighters_per_wave == 0
        assert ship.fighter_size_cap == 0
        assert ship.launch_cycle == 0

    def test_single_hangar_populates_all_fields(self):
        ship = _make_ship()
        comp = _make_hangar_component(
            vehicle_launch={"max_launch_mass": 500, "cycle_time": 8.0},
            vehicle_storage=4,
        )
        launch.aggregate_hangar(ship, comp)
        assert ship.fighter_capacity == 4
        assert ship.fighters_per_wave == 1
        assert ship.fighter_size_cap == 500
        assert ship.launch_cycle == 8.0

    def test_capacity_and_wave_size_sum_across_calls(self):
        ship = _make_ship()
        comp_a = _make_hangar_component(
            vehicle_launch={"max_launch_mass": 300, "cycle_time": 6.0},
            vehicle_storage=2,
        )
        comp_b = _make_hangar_component(
            vehicle_launch={"max_launch_mass": 600, "cycle_time": 4.0},
            vehicle_storage=3,
        )
        launch.aggregate_hangar(ship, comp_a)
        launch.aggregate_hangar(ship, comp_b)
        assert ship.fighter_capacity == 5
        assert ship.fighters_per_wave == 2

    def test_size_cap_takes_max_not_sum(self):
        ship = _make_ship()
        comp_a = _make_hangar_component(
            vehicle_launch={"max_launch_mass": 300, "cycle_time": 6.0},
        )
        comp_b = _make_hangar_component(
            vehicle_launch={"max_launch_mass": 800, "cycle_time": 4.0},
        )
        launch.aggregate_hangar(ship, comp_a)
        launch.aggregate_hangar(ship, comp_b)
        assert ship.fighter_size_cap == 800  # max, not 300+800

    def test_launch_cycle_takes_max_not_sum(self):
        """Slower bay dictates the wave gating — max wins."""
        ship = _make_ship()
        comp_a = _make_hangar_component(
            vehicle_launch={"max_launch_mass": 300, "cycle_time": 6.0},
        )
        comp_b = _make_hangar_component(
            vehicle_launch={"max_launch_mass": 300, "cycle_time": 9.5},
        )
        launch.aggregate_hangar(ship, comp_a)
        launch.aggregate_hangar(ship, comp_b)
        assert ship.launch_cycle == 9.5

    def test_non_dict_vehicle_launch_uses_defaults(self):
        """Legacy guard: if VehicleLaunch is not a dict, max_mass=0 and cycle=5.0."""
        ship = _make_ship()
        comp = _make_hangar_component(vehicle_launch=True, vehicle_storage=2)
        # has_ability check still returns True via the abilities dict membership
        launch.aggregate_hangar(ship, comp)
        assert ship.fighter_capacity == 2
        assert ship.fighters_per_wave == 1
        assert ship.fighter_size_cap == 0
        assert ship.launch_cycle == 5.0
