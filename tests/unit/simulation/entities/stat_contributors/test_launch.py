"""
Unit tests for the launch / hangar stat contributor.

PROJ-367 Phase 1: migrated to use the typed VehicleLaunchAbility (extended
with ``max_launch_mass``) and VehicleStorageAbility classes via
``comp.get_abilities(...)`` rather than raw ``comp.abilities`` dict reads.
"""
from __future__ import annotations

from types import SimpleNamespace
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


def _make_hangar_component(
    *,
    vehicle_launch: dict | None,
    vehicle_storage: int = 0,
):
    """Component with typed VehicleLaunchAbility / VehicleStorageAbility shims.

    PROJ-367 Phase 1: typed ability instances are SimpleNamespace fakes that
    expose the same attributes (``capacity``, ``cycle_time``,
    ``max_launch_mass``) the real ability classes do. ``get_abilities``
    returns the matching list; ``has_ability`` reports presence.
    """
    comp = MagicMock()
    typed: dict[str, list] = {}
    if vehicle_launch is not None:
        if isinstance(vehicle_launch, dict):
            ab = SimpleNamespace(
                capacity=vehicle_launch.get("capacity", 0),
                cycle_time=vehicle_launch.get("cycle_time", 5.0),
                max_launch_mass=vehicle_launch.get("max_launch_mass", 0),
                fighter_class=vehicle_launch.get("fighter_class", "Fighter (Small)"),
            )
        else:
            # Legacy non-dict guard — defaults match VehicleLaunchAbility._parse_attrs.
            ab = SimpleNamespace(
                capacity=0,
                cycle_time=5.0,
                max_launch_mass=0.0,
                fighter_class="Fighter (Small)",
            )
        typed["VehicleLaunch"] = [ab]
    if vehicle_storage:
        typed["VehicleStorage"] = [SimpleNamespace(capacity=vehicle_storage)]
    comp.has_ability = lambda name: name in typed
    comp.get_abilities = lambda name: typed.get(name, [])
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
