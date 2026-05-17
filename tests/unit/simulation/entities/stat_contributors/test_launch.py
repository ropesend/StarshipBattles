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
