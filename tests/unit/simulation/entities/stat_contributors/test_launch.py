"""
Unit tests for the launch / hangar stat contributor.

PROJ-FMS-C audit Fix 1: migrated off the legacy ``VehicleLaunchAbility`` to
the PROJ-FMS-A Phase 5 ``TacticalFighterLaunchAbility``. The contributor
now reads ``capacity_per_action`` (additive) and ``cycle_time`` (max)
plus co-located ``VehicleStorageAbility`` (additive into
``fighter_capacity``).
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from game.simulation.entities.stat_contributors import launch


def _make_ship():
    ship = MagicMock()
    ship.fighter_capacity = 0
    ship.fighters_per_wave = 0
    ship.fighter_size_cap = 0
    ship.launch_cycle = 0
    ship.fighter_launch_rate_tons_per_sec = 0.0
    return ship


def _make_hangar_component(
    *,
    tactical_launch: dict | None,
    vehicle_storage: int = 0,
):
    """Component with TacticalFighterLaunchAbility / VehicleStorageAbility shims.

    The typed ability instances are :class:`SimpleNamespace` fakes
    exposing the same attribute surface the real ability classes do.
    ``get_abilities`` returns the matching list; ``has_ability`` reports
    presence.
    """
    comp = MagicMock()
    typed: dict[str, list] = {}
    if tactical_launch is not None:
        ab = SimpleNamespace(
            capacity_per_action=tactical_launch.get("capacity_per_action", 1),
            cycle_time=tactical_launch.get("cycle_time", 5.0),
            launch_rate_tons_per_sec=tactical_launch.get(
                "launch_rate_tons_per_sec", 0.0,
            ),
        )
        typed["TacticalFighterLaunch"] = [ab]
    if vehicle_storage:
        typed["VehicleStorage"] = [SimpleNamespace(capacity=vehicle_storage)]
    comp.has_ability = lambda name: name in typed
    comp.get_abilities = lambda name: typed.get(name, [])
    return comp


class TestAggregateHangar:
    def test_no_hangar_ability_is_noop(self):
        ship = _make_ship()
        comp = _make_hangar_component(tactical_launch=None)
        launch.contribute_vehicle_launch(ship, comp, {})
        assert ship.fighter_capacity == 0
        assert ship.fighters_per_wave == 0
        assert ship.fighter_size_cap == 0
        assert ship.launch_cycle == 0

    def test_single_hangar_populates_capacity_wave_cycle(self):
        ship = _make_ship()
        comp = _make_hangar_component(
            tactical_launch={"capacity_per_action": 2, "cycle_time": 8.0},
            vehicle_storage=4,
        )
        launch.contribute_vehicle_launch(ship, comp, {})
        assert ship.fighter_capacity == 4
        assert ship.fighters_per_wave == 2
        assert ship.launch_cycle == 8.0

    def test_capacity_and_wave_size_sum_across_calls(self):
        ship = _make_ship()
        comp_a = _make_hangar_component(
            tactical_launch={"capacity_per_action": 1, "cycle_time": 6.0},
            vehicle_storage=2,
        )
        comp_b = _make_hangar_component(
            tactical_launch={"capacity_per_action": 2, "cycle_time": 4.0},
            vehicle_storage=3,
        )
        launch.contribute_vehicle_launch(ship, comp_a, {})
        launch.contribute_vehicle_launch(ship, comp_b, {})
        assert ship.fighter_capacity == 5
        assert ship.fighters_per_wave == 3

    def test_launch_cycle_takes_max_not_sum(self):
        """Slower bay dictates the wave gating — max wins."""
        ship = _make_ship()
        comp_a = _make_hangar_component(
            tactical_launch={"capacity_per_action": 1, "cycle_time": 6.0},
        )
        comp_b = _make_hangar_component(
            tactical_launch={"capacity_per_action": 1, "cycle_time": 9.5},
        )
        launch.contribute_vehicle_launch(ship, comp_a, {})
        launch.contribute_vehicle_launch(ship, comp_b, {})
        assert ship.launch_cycle == 9.5

    def test_storage_without_tactical_launch_is_ignored(self):
        """VehicleStorage on a component without TacticalFighterLaunch is skipped.

        PROJ-FMS-C audit Fix 1 keeps the prior gating shape: launch
        capacity is only rolled up when the same component also exposes
        the tactical launch ability. Modders wanting independent storage
        roll-up register a separate contributor for ``VehicleStorage``.
        """
        ship = _make_ship()
        comp = _make_hangar_component(tactical_launch=None, vehicle_storage=10)
        launch.contribute_vehicle_launch(ship, comp, {})
        assert ship.fighter_capacity == 0
        assert ship.launch_cycle == 0


def _make_satellite_ship():
    ship = MagicMock()
    ship.satellite_capacity = 0
    ship.satellites_per_wave = 0
    ship.satellite_launch_cycle = 0
    ship.satellite_launch_rate_tons_per_sec = 0.0
    return ship


def _make_satellite_component(
    *,
    tactical_launch: dict | None,
    vehicle_storage: int = 0,
):
    """Component exposing TacticalSatelliteLaunch / VehicleStorage shims."""
    comp = MagicMock()
    typed: dict[str, list] = {}
    if tactical_launch is not None:
        ab = SimpleNamespace(
            capacity_per_action=tactical_launch.get("capacity_per_action", 1),
            cycle_time=tactical_launch.get("cycle_time", 5.0),
            launch_rate_tons_per_sec=tactical_launch.get(
                "launch_rate_tons_per_sec", 0.0,
            ),
        )
        typed["TacticalSatelliteLaunch"] = [ab]
    if vehicle_storage:
        typed["VehicleStorage"] = [SimpleNamespace(capacity=vehicle_storage)]
    comp.has_ability = lambda name: name in typed
    comp.get_abilities = lambda name: typed.get(name, [])
    return comp


class TestAggregateSatelliteHangar:
    """Cluster 19 (PROJ-465): characterize the satellite half of the shared
    ``_contribute_launch`` helper — gating ability ``TacticalSatelliteLaunch``
    and the satellite-specific ship fields. Mirrors the fighter coverage so
    the string-parameterized refactor is pinned on both sides.
    """

    def test_no_satellite_ability_is_noop(self):
        ship = _make_satellite_ship()
        comp = _make_satellite_component(tactical_launch=None)
        launch.contribute_tactical_satellite_launch(ship, comp, {})
        assert ship.satellite_capacity == 0
        assert ship.satellites_per_wave == 0
        assert ship.satellite_launch_cycle == 0
        assert ship.satellite_launch_rate_tons_per_sec == 0.0

    def test_single_satellite_bay_populates_fields(self):
        ship = _make_satellite_ship()
        comp = _make_satellite_component(
            tactical_launch={
                "capacity_per_action": 3,
                "cycle_time": 7.0,
                "launch_rate_tons_per_sec": 1.5,
            },
            vehicle_storage=6,
        )
        launch.contribute_tactical_satellite_launch(ship, comp, {})
        assert ship.satellite_capacity == 6
        assert ship.satellites_per_wave == 3
        assert ship.satellite_launch_cycle == 7.0
        assert ship.satellite_launch_rate_tons_per_sec == 1.5

    def test_satellite_fields_sum_and_cycle_takes_max(self):
        ship = _make_satellite_ship()
        comp_a = _make_satellite_component(
            tactical_launch={
                "capacity_per_action": 1, "cycle_time": 6.0,
                "launch_rate_tons_per_sec": 0.5,
            },
            vehicle_storage=2,
        )
        comp_b = _make_satellite_component(
            tactical_launch={
                "capacity_per_action": 2, "cycle_time": 9.5,
                "launch_rate_tons_per_sec": 0.25,
            },
            vehicle_storage=3,
        )
        launch.contribute_tactical_satellite_launch(ship, comp_a, {})
        launch.contribute_tactical_satellite_launch(ship, comp_b, {})
        assert ship.satellite_capacity == 5
        assert ship.satellites_per_wave == 3
        assert ship.satellite_launch_cycle == 9.5  # max, not sum
        assert ship.satellite_launch_rate_tons_per_sec == 0.75  # sum

    def test_satellite_storage_without_launch_is_ignored(self):
        ship = _make_satellite_ship()
        comp = _make_satellite_component(tactical_launch=None, vehicle_storage=10)
        launch.contribute_tactical_satellite_launch(ship, comp, {})
        assert ship.satellite_capacity == 0
        assert ship.satellite_launch_cycle == 0

    def test_fighter_and_satellite_paths_are_independent(self):
        """A component exposing only the fighter ability must not touch the
        satellite fields, and vice versa — the two parameterizations write
        disjoint field sets."""
        sat_ship = _make_satellite_ship()
        sat_ship.fighter_capacity = 0
        fighter_comp = _make_hangar_component(
            tactical_launch={"capacity_per_action": 2, "cycle_time": 5.0},
            vehicle_storage=4,
        )
        launch.contribute_tactical_satellite_launch(sat_ship, fighter_comp, {})
        # Satellite contributor gated on TacticalSatelliteLaunch — no-op here.
        assert sat_ship.satellite_capacity == 0
        assert sat_ship.satellites_per_wave == 0
