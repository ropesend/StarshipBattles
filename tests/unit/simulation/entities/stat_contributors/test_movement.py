"""
Unit tests for the movement stat contributor.

Verifies in isolation that ``aggregate_propulsion`` correctly accumulates
thrust, strategic movement, warp tonnage/cost, and turn speed from a single
component's abilities. Golden-output tests already pin the integrated
behavior; these tests guard against accidental contributor-internal regressions.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.simulation.entities.stat_contributors import movement


def _make_thruster_ability(turn_rate: float):
    ab = MagicMock()
    ab.turn_rate = turn_rate
    return ab


def _make_combat_propulsion_ability(thrust: float):
    ab = MagicMock()
    ab.thrust_force = thrust
    return ab


def _make_strategic_movement_ability(points: float):
    ab = MagicMock()
    ab.movement_points = points
    return ab


def _make_warp_jump_ability(*, max_tonnage: int, energy_cost: float):
    """Build a MagicMock that satisfies ``is_warp_jump`` via duck typing.

    ``is_warp_jump`` checks for the attributes the protocol exposes
    (max_tonnage + energy_cost). MagicMock auto-attribute lookup is fine for
    other reads, but specifying the named attrs gives explicit values.
    """
    ab = MagicMock()
    ab.max_tonnage = max_tonnage
    ab.energy_cost = energy_cost
    return ab


def _make_component(*, abilities_by_name: dict):
    comp = MagicMock()
    comp.get_abilities = lambda name: abilities_by_name.get(name, [])
    return comp


def _empty_acc() -> dict:
    return {
        "thrust": 0,
        "strategic_movement": 0,
        "turn_speed": 0,
        "maneuver_points": 0,
        "warp_max_tonnage": 0,
        "warp_energy_cost": 0,
    }


class TestAggregatePropulsionThrust:
    def test_combat_propulsion_sums_thrust(self):
        acc = _empty_acc()
        comp = _make_component(
            abilities_by_name={
                "CombatPropulsion": [
                    _make_combat_propulsion_ability(100.0),
                    _make_combat_propulsion_ability(50.0),
                ]
            }
        )
        movement.aggregate_propulsion(comp, acc)
        assert acc["thrust"] == 150.0

    def test_no_combat_propulsion_leaves_thrust_zero(self):
        acc = _empty_acc()
        comp = _make_component(abilities_by_name={})
        movement.aggregate_propulsion(comp, acc)
        assert acc["thrust"] == 0


class TestAggregatePropulsionStrategicMovement:
    def test_strategic_movement_points_sum(self):
        acc = _empty_acc()
        comp = _make_component(
            abilities_by_name={
                "StrategicMovement": [
                    _make_strategic_movement_ability(2.0),
                    _make_strategic_movement_ability(1.5),
                ]
            }
        )
        movement.aggregate_propulsion(comp, acc)
        assert acc["strategic_movement"] == 3.5


class TestAggregatePropulsionTurning:
    def test_maneuvering_thruster_doubles_into_turn_speed_and_points(self):
        """Each ManeuveringThruster.turn_rate adds to BOTH turn_speed and maneuver_points.

        Legacy semantic: maneuver_points tracks the raw turning capability
        (mass-independent); turn_speed gets divided by mass^1.5 in physics
        phase but the accumulator holds the same value pre-physics.
        """
        acc = _empty_acc()
        comp = _make_component(
            abilities_by_name={
                "ManeuveringThruster": [
                    _make_thruster_ability(40.0),
                    _make_thruster_ability(60.0),
                ]
            }
        )
        movement.aggregate_propulsion(comp, acc)
        assert acc["turn_speed"] == 100.0
        assert acc["maneuver_points"] == 100.0


class TestAggregatePropulsionWarp:
    def test_warp_max_tonnage_takes_max_not_sum(self):
        acc = _empty_acc()
        comp = _make_component(
            abilities_by_name={
                "WarpJump": [
                    _make_warp_jump_ability(max_tonnage=1000, energy_cost=100.0),
                    _make_warp_jump_ability(max_tonnage=500, energy_cost=80.0),
                ]
            }
        )
        movement.aggregate_propulsion(comp, acc)
        assert acc["warp_max_tonnage"] == 1000

    def test_warp_energy_cost_sums_across_drives(self):
        acc = _empty_acc()
        comp = _make_component(
            abilities_by_name={
                "WarpJump": [
                    _make_warp_jump_ability(max_tonnage=1000, energy_cost=100.0),
                    _make_warp_jump_ability(max_tonnage=500, energy_cost=80.0),
                ]
            }
        )
        movement.aggregate_propulsion(comp, acc)
        assert acc["warp_energy_cost"] == 180.0


class TestAggregatePropulsionMixed:
    def test_all_categories_accumulate_independently(self):
        acc = _empty_acc()
        comp = _make_component(
            abilities_by_name={
                "CombatPropulsion": [_make_combat_propulsion_ability(200.0)],
                "ManeuveringThruster": [_make_thruster_ability(45.0)],
                "StrategicMovement": [_make_strategic_movement_ability(1.0)],
                "WarpJump": [
                    _make_warp_jump_ability(max_tonnage=750, energy_cost=60.0)
                ],
            }
        )
        movement.aggregate_propulsion(comp, acc)
        assert acc["thrust"] == 200.0
        assert acc["turn_speed"] == 45.0
        assert acc["maneuver_points"] == 45.0
        assert acc["strategic_movement"] == 1.0
        assert acc["warp_max_tonnage"] == 750
        assert acc["warp_energy_cost"] == 60.0
