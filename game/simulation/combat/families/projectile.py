"""PROJ-359 Phase 3.2: Projectile (non-seeking) weapon family handler.

Constructs a `Projectile` entity from a `ProjectileWeaponAbility` weapon and
returns it wrapped in a `ProjectileResolution`.
"""
from __future__ import annotations

from game.core.constants import AttackType, SimulationConstants
from game.core.math import Vector2
from game.simulation.combat.attack_contract import (
    AttackRequest,
    AttackResolution,
    ProjectileResolution,
    WeaponFamily,
)
from game.simulation.combat.weapon_registry import WEAPON_REGISTRY
from game.simulation.entities.projectile import Projectile


class ProjectileHandler:
    """Standard (non-seeking) projectile family handler."""

    def fire(self, request: AttackRequest) -> AttackResolution:
        ship = request.source
        comp = request.component
        target = request.target
        aim_vec = request.aim_vec

        projectile_ab = comp.get_ability('ProjectileWeaponAbility')
        speed = projectile_ab.projectile_speed / SimulationConstants.PROJECTILE_SPEED_SCALE
        p_vel = aim_vec.normalize() * speed + ship.velocity

        projectile = Projectile(
            owner=ship,
            position=Vector2(ship.position),
            velocity=p_vel,
            damage=projectile_ab.damage,
            range_val=projectile_ab.range,
            endurance=None,
            proj_type=AttackType.PROJECTILE,
            source_weapon=comp,
            target=target,
        )
        return ProjectileResolution(projectile=projectile)


WEAPON_REGISTRY.register(WeaponFamily.PROJECTILE, ProjectileHandler())
