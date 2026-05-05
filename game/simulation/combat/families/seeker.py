"""PROJ-359 Phase 3.3: Seeker / Missile weapon family handler.

Constructs a seeker `Projectile` (turn_rate, max_speed, target, hp,
to_hit_defense, endurance) and applies the firing-arc launch-vector adjustment
that the legacy `_create_seeker_projectile` did.
"""
from __future__ import annotations

import math

from game.core.constants import AttackType, SimulationConstants
from game.core.math import Vector2, angle_from_vector
from game.simulation.combat.attack_contract import (
    AttackRequest,
    AttackResolution,
    ProjectileResolution,
    WeaponFamily,
)
from game.simulation.combat.weapon_registry import WEAPON_REGISTRY
from game.simulation.entities.projectile import Projectile


class SeekerHandler:
    """Seeker / missile family handler.

    The launch vector defaults to the component's facing direction; if the
    target is inside the firing arc, it switches to the lead-corrected aim
    vector. This matches the legacy behavior bit-for-bit.
    """

    def fire(self, request: AttackRequest) -> AttackResolution:
        ship = request.source
        comp = request.component
        weapon_ab = request.weapon_ability
        target = request.target
        aim_vec = request.aim_vec

        seeker_ab = comp.get_ability('SeekerWeaponAbility')

        comp_facing = ship.angle + weapon_ab.facing_angle
        rad = math.radians(comp_facing)
        launch_vec = Vector2(math.cos(rad), math.sin(rad))

        # Arc check — if target is in arc, use the (lead-corrected) aim vector
        if target:
            rel_pos = target.position - ship.position
            target_angle = angle_from_vector(rel_pos.x, rel_pos.y)
            diff = (target_angle - comp_facing + 180) % 360 - 180
            if abs(diff) <= (weapon_ab.firing_arc / 2):
                launch_vec = aim_vec.normalize() if aim_vec.length() > 0 else launch_vec

        speed = seeker_ab.projectile_speed / SimulationConstants.PROJECTILE_SPEED_SCALE
        p_vel = launch_vec * speed + ship.velocity

        projectile = Projectile(
            owner=ship,
            position=Vector2(ship.position),
            velocity=p_vel,
            damage=seeker_ab.projectile_damage,
            range_val=seeker_ab.projectile_speed * seeker_ab.endurance,
            endurance=seeker_ab.endurance,
            proj_type=AttackType.MISSILE,
            turn_rate=seeker_ab.turn_rate,
            max_speed=speed,
            target=target,
            hp=seeker_ab.projectile_hp,
            to_hit_defense=seeker_ab.to_hit_defense,
            source_weapon=comp,
        )
        return ProjectileResolution(projectile=projectile)


WEAPON_REGISTRY.register(WeaponFamily.SEEKER, SeekerHandler())
