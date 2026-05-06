from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from game.core.constants import AttackType
from game.core.math import Vector2
from game.simulation.combat.attack_contract import (
    AttackRequest,
    BeamResolution,
    ProjectileResolution,
    WeaponFamily,
)
from game.simulation.combat.families._beam_common import build_beam_resolution
from game.simulation.combat.families.pdc import PDCHandler
from game.simulation.combat.families.seeker import SeekerHandler


def _request(
    *,
    family: WeaponFamily,
    source: object | None = None,
    component: object | None = None,
    weapon_ability: object | None = None,
    target: object | None = None,
    aim_vec: Vector2 | None = None,
) -> AttackRequest:
    return AttackRequest(
        source=source or _ship(),
        component=component or MagicMock(),
        weapon_ability=weapon_ability or _weapon_ability(),
        target=target,
        aim_pos=Vector2(0, 0),
        aim_vec=aim_vec if aim_vec is not None else Vector2(1, 0),
        family=family,
    )


def _ship(*, angle: float = 0.0, velocity: Vector2 | None = None) -> SimpleNamespace:
    return SimpleNamespace(
        position=Vector2(0, 0),
        velocity=velocity if velocity is not None else Vector2(0, 0),
        angle=angle,
        team_id=0,
    )


def _target(x: float, y: float) -> SimpleNamespace:
    return SimpleNamespace(
        position=Vector2(x, y),
        velocity=Vector2(0, 0),
        is_alive=True,
        team_id=1,
    )


def _weapon_ability(
    *,
    damage: float = 25.0,
    range: float = 500.0,
    firing_arc: float = 90.0,
    facing_angle: float = 0.0,
) -> SimpleNamespace:
    return SimpleNamespace(
        damage=damage,
        range=range,
        firing_arc=firing_arc,
        facing_angle=facing_angle,
    )


def _seeker_ability() -> SimpleNamespace:
    return SimpleNamespace(
        projectile_speed=300.0,
        endurance=2.0,
        turn_rate=15.0,
        to_hit_defense=3.0,
        projectile_damage=40.0,
        projectile_hp=7.0,
    )


def _seeker_component(seeker_ability: object | None = None) -> MagicMock:
    comp = MagicMock()
    comp.get_ability = lambda name: (
        seeker_ability or _seeker_ability()
        if name == "SeekerWeaponAbility"
        else None
    )
    return comp


def _assert_vector(vector: Vector2, expected_x: float, expected_y: float) -> None:
    assert vector.x == pytest.approx(expected_x)
    assert vector.y == pytest.approx(expected_y)


class TestBeamResolutionBuilder:
    def test_zero_aim_vector_falls_back_to_positive_x_direction(self) -> None:
        request = _request(
            family=WeaponFamily.BEAM,
            source=_ship(),
            weapon_ability=_weapon_ability(damage=12.0, range=345.0),
            target=_target(0, 100),
            aim_vec=Vector2(0, 0),
        )

        resolution = build_beam_resolution(request)

        assert isinstance(resolution, BeamResolution)
        _assert_vector(resolution.direction, 1.0, 0.0)
        assert resolution.type is AttackType.BEAM
        assert resolution.damage == 12.0
        assert resolution.range == 345.0


class TestPDCHandler:
    def test_fire_delegates_to_shared_beam_resolution_builder(self) -> None:
        request = _request(family=WeaponFamily.PDC)
        sentinel = MagicMock()

        with patch(
            "game.simulation.combat.families.pdc.build_beam_resolution",
            return_value=sentinel,
        ) as build:
            result = PDCHandler().fire(request)

        build.assert_called_once_with(request)
        assert result is sentinel

    def test_fire_returns_beam_shaped_resolution_for_pdc_family(self) -> None:
        request = _request(
            family=WeaponFamily.PDC,
            source=_ship(),
            weapon_ability=_weapon_ability(damage=8.0, range=250.0),
            target=_target(100, 0),
            aim_vec=Vector2(4, 0),
        )

        resolution = PDCHandler().fire(request)

        assert isinstance(resolution, BeamResolution)
        assert request.family is WeaponFamily.PDC
        assert resolution.type is AttackType.BEAM
        assert resolution.hit is True
        assert resolution.damage == 8.0
        assert resolution.range == 250.0


class TestSeekerHandler:
    def test_target_none_launches_along_component_facing(self) -> None:
        request = _request(
            family=WeaponFamily.SEEKER,
            source=_ship(angle=90.0),
            component=_seeker_component(),
            weapon_ability=_weapon_ability(facing_angle=0.0),
            target=None,
            aim_vec=Vector2(1, 0),
        )

        resolution = SeekerHandler().fire(request)

        assert isinstance(resolution, ProjectileResolution)
        assert resolution.projectile.target is None
        assert resolution.projectile.type is AttackType.MISSILE
        _assert_vector(resolution.projectile.velocity, 0.0, 3.0)

    def test_out_of_arc_target_launches_along_component_facing(self) -> None:
        request = _request(
            family=WeaponFamily.SEEKER,
            source=_ship(angle=0.0),
            component=_seeker_component(),
            weapon_ability=_weapon_ability(firing_arc=60.0, facing_angle=0.0),
            target=_target(0, 100),
            aim_vec=Vector2(0, 1),
        )

        resolution = SeekerHandler().fire(request)

        assert isinstance(resolution, ProjectileResolution)
        assert resolution.projectile.target is request.target
        _assert_vector(resolution.projectile.velocity, 3.0, 0.0)

    def test_in_arc_target_uses_normalized_aim_vector(self) -> None:
        request = _request(
            family=WeaponFamily.SEEKER,
            source=_ship(angle=0.0),
            component=_seeker_component(),
            weapon_ability=_weapon_ability(firing_arc=90.0, facing_angle=0.0),
            target=_target(100, 0),
            aim_vec=Vector2(3, 4),
        )

        resolution = SeekerHandler().fire(request)

        assert isinstance(resolution, ProjectileResolution)
        _assert_vector(resolution.projectile.velocity, 1.8, 2.4)

    def test_in_arc_zero_aim_vector_keeps_component_facing(self) -> None:
        request = _request(
            family=WeaponFamily.SEEKER,
            source=_ship(angle=0.0),
            component=_seeker_component(),
            weapon_ability=_weapon_ability(firing_arc=90.0, facing_angle=0.0),
            target=_target(100, 0),
            aim_vec=Vector2(0, 0),
        )

        resolution = SeekerHandler().fire(request)

        assert isinstance(resolution, ProjectileResolution)
        _assert_vector(resolution.projectile.velocity, 3.0, 0.0)
        assert resolution.projectile.damage == 40.0
        assert resolution.projectile.max_range == 600.0
        assert resolution.projectile.endurance == 2.0
        assert resolution.projectile.turn_rate == 15.0
        assert resolution.projectile.hp == 7.0
        assert resolution.projectile.total_defense_score == 3.0
