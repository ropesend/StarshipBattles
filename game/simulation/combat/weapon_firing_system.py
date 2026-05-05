"""
WeaponFiringSystem - Extracted weapon firing logic from ShipCombatEngine.

This class handles all weapon firing operations:
- Processing weapon components for firing
- Creating beam attacks
- Creating projectile attacks
- Creating seeker/missile attacks
- Handling hangar vehicle launches

Part of PROJ-44 Phase 5: ShipCombatEngine Decomposition.
"""
import math
from typing import TYPE_CHECKING, List, Optional, Any, Dict

from game.core.math import Vector2, angle_from_vector
from game.core.constants import AttackType, CombatConstants, SimulationConstants
from game.simulation.entities.projectile import Projectile

# PROJ-359 Phase 3: importing `families` triggers WEAPON_REGISTRY registrations
from game.simulation.combat import families  # noqa: F401
from game.simulation.combat.attack_contract import (
    FAMILY_METADATA,
    AttackRequest,
    BeamResolution,
    ProjectileResolution,
    WeaponFamily,
)
from game.simulation.combat.weapon_registry import WEAPON_REGISTRY, detect_family

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.simulation.components.component import Component
    from game.simulation.combat.targeting_system import TargetingSystem


class WeaponFiringSystem:
    """
    Handles all weapon firing logic for combat.

    Extracted from ShipCombatEngine to focus on single responsibility:
    firing weapons and creating attack objects.
    """

    def __init__(self, targeting_system: 'TargetingSystem'):
        """
        Initialize weapon firing system.

        Args:
            targeting_system: The targeting system to use for aim calculations
        """
        self._targeting = targeting_system

    def fire_weapons(
        self,
        ship: 'Ship',
        context: Optional[dict] = None
    ) -> List[Any]:
        """
        Fire all ready weapons at available targets.

        Iterates through all weapon components, checks firing conditions,
        and creates projectiles or beam attacks as appropriate.

        Args:
            ship: The ship firing weapons
            context: Optional context dict with projectiles list for PDC targeting

        Returns:
            List of attack objects (Projectiles or beam attack dicts)
        """
        attacks = []

        if not ship.is_alive or ship.is_derelict:
            return attacks

        for layer_type, comp in ship.iter_components():
            # Handle Hangar Launch
            if comp.has_ability('VehicleLaunch') and comp.is_operational:
                attack = self._process_hangar_launch(ship, comp)
                if attack:
                    attacks.append(attack)
                continue

            # Handle Weapons (is_operational checks both is_active AND
            # requirement satisfaction like RequiresCommandAndControl)
            if comp.has_ability('WeaponAbility') and comp.is_operational:
                attack_result = self._process_weapon_fire(ship, comp, context)
                if attack_result:
                    if isinstance(attack_result, list):
                        attacks.extend(attack_result)
                    else:
                        attacks.append(attack_result)

        return attacks

    def _process_hangar_launch(
        self,
        ship: 'Ship',
        comp: 'Component'
    ) -> Optional[Dict]:
        """
        Process vehicle launch from hangar component.

        Args:
            ship: The ship launching
            comp: Hangar component with VehicleLaunch ability

        Returns:
            Launch attack dict or None
        """
        vl_ability = comp.get_ability('VehicleLaunch')

        # Auto-launch if we have a target
        if ship.current_target and vl_ability.try_launch():
            return {
                'type': AttackType.LAUNCH,
                'source': ship,
                'origin': ship.position,
                'hangar': comp,
                'fighter_class': vl_ability.fighter_class
            }
        return None

    def _process_weapon_fire(
        self,
        ship: 'Ship',
        comp: 'Component',
        context: Optional[dict] = None
    ) -> Optional[List[Any]]:
        """
        Process firing for a weapon component.

        Validates target, checks firing conditions, and creates attack.

        Args:
            ship: The ship firing
            comp: Weapon component
            context: Optional context dict

        Returns:
            List of attacks or None
        """
        weapon_ab = comp.get_ability('WeaponAbility')

        if not comp.can_afford_activation():
            return None

        if not weapon_ab.can_fire():
            return None

        # Find valid target (pass context for PDC missile targeting)
        target = self._find_valid_target(ship, comp, weapon_ab, context)
        if not target:
            return None

        # Fire the weapon
        if not weapon_ab.fire(target):
            return None

        # Update stats (both fields initialized in __init__)
        ship.total_shots_fired += 1
        comp.shots_fired += 1

        # Create attack based on weapon type
        return self._create_attack(ship, comp, weapon_ab, target)

    def _find_valid_target(
        self,
        ship: 'Ship',
        comp: 'Component',
        weapon_ab: Any,
        context: Optional[dict] = None
    ) -> Optional[Any]:
        """
        Find a valid target for the weapon.

        For PDC weapons, includes enemy missiles from context as candidates.

        Args:
            ship: The ship targeting
            comp: Weapon component
            weapon_ab: Weapon ability instance
            context: Optional context dict with projectiles list

        Returns:
            Valid target or None
        """
        # Build secondary targets list
        secondary_targets = []
        if ship.max_targets > CombatConstants.DEFAULT_MAX_TARGETS:
            secondary_targets = list(ship.secondary_targets)

        # PROJ-359 Phase 3.4: Family-metadata-driven missile injection.
        # Previously: `if comp.has_pdc_ability() and context:` — string lookup.
        # Now: family metadata declares whether this family consumes the
        # PDC missile context. Adding a new family with this behavior is a
        # FAMILY_METADATA edit, not a firing-system edit.
        family = detect_family(comp)
        meta = FAMILY_METADATA.get(family) if family else None
        if meta is not None and meta.consumes_pdc_missile_context and context:
            projectiles = context.get('projectiles', [])
            for p in projectiles:
                if p.is_alive and p.team_id != ship.team_id and p.type == AttackType.MISSILE:
                    secondary_targets.append(p)

        return self._targeting.find_valid_target(
            ship,
            ship.current_target,
            secondary_targets,
            comp,
            weapon_ab
        )

    def _create_attack(
        self,
        ship: 'Ship',
        comp: 'Component',
        weapon_ab: Any,
        target: Any
    ) -> List[Any]:
        """
        Create attack object(s) for a successful weapon fire.

        Args:
            ship: The ship firing
            comp: Weapon component
            weapon_ab: Weapon ability
            target: Target being fired at

        Returns:
            List containing attack object(s)
        """
        attacks = []

        aim_pos, aim_vec = self._targeting.calculate_firing_solution(ship, comp, target)

        # PROJ-359 Phase 3.4: Both Beam and PDC route through the registry.
        # Legacy collision.py still consumes a dict; adapt at the boundary.
        # Phase 4 deletes the adapter.
        if comp.has_ability('BeamWeaponAbility'):
            family = detect_family(comp)
            assert family in (WeaponFamily.BEAM, WeaponFamily.PDC)
            request = AttackRequest(
                source=ship,
                component=comp,
                weapon_ability=weapon_ab,
                target=target,
                aim_pos=aim_pos,
                aim_vec=aim_vec,
                family=family,
            )
            resolution = WEAPON_REGISTRY.dispatch(request)
            assert isinstance(resolution, BeamResolution)
            attacks.append(_beam_resolution_to_legacy_dict(resolution))
        else:
            # Projectile / Seeker attack — both route through the registry.
            if comp.has_ability('SeekerWeaponAbility'):
                family = WeaponFamily.SEEKER
            else:
                family = WeaponFamily.PROJECTILE

            if WEAPON_REGISTRY.has(family):
                request = AttackRequest(
                    source=ship,
                    component=comp,
                    weapon_ability=weapon_ab,
                    target=target,
                    aim_pos=aim_pos,
                    aim_vec=aim_vec,
                    family=family,
                )
                resolution = WEAPON_REGISTRY.dispatch(request)
                assert isinstance(resolution, ProjectileResolution)
                projectile = resolution.projectile
            elif comp.has_ability('SeekerWeaponAbility'):
                projectile = self._create_seeker_projectile(ship, comp, target, weapon_ab, aim_vec)
            else:
                projectile = self._create_standard_projectile(ship, comp, target, aim_vec)

            attacks.append(projectile)

        return attacks

    def _create_seeker_projectile(
        self,
        ship: 'Ship',
        comp: 'Component',
        target: Any,
        weapon_ab: Any,
        aim_vec: Vector2
    ) -> Projectile:
        """Create a seeker/missile projectile."""
        seeker_ab = comp.get_ability('SeekerWeaponAbility')

        # Calculate launch direction - facing_angle is on the weapon ability
        comp_facing = ship.angle + weapon_ab.facing_angle
        rad = math.radians(comp_facing)
        launch_vec = Vector2(math.cos(rad), math.sin(rad))

        # Check if target is in arc
        if target:
            rel_pos = target.position - ship.position
            target_angle = angle_from_vector(rel_pos.x, rel_pos.y)
            diff = (target_angle - comp_facing + 180) % 360 - 180
            if abs(diff) <= (weapon_ab.firing_arc / 2):
                launch_vec = aim_vec.normalize() if aim_vec.length() > 0 else launch_vec

        speed = seeker_ab.projectile_speed / SimulationConstants.PROJECTILE_SPEED_SCALE
        p_vel = launch_vec * speed + ship.velocity

        # PROJ-113: Removed color - visual properties now in UI layer
        return Projectile(
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
            source_weapon=comp
        )

    def _create_standard_projectile(
        self,
        ship: 'Ship',
        comp: 'Component',
        target: Any,
        aim_vec: Vector2
    ) -> Projectile:
        """Create a standard (non-seeking) projectile."""
        projectile_ab = comp.get_ability('ProjectileWeaponAbility')

        speed = projectile_ab.projectile_speed / SimulationConstants.PROJECTILE_SPEED_SCALE
        p_vel = aim_vec.normalize() * speed + ship.velocity

        # PROJ-113: Removed color - visual properties now in UI layer
        return Projectile(
            owner=ship,
            position=Vector2(ship.position),
            velocity=p_vel,
            damage=projectile_ab.damage,
            range_val=projectile_ab.range,
            endurance=None,
            proj_type=AttackType.PROJECTILE,
            source_weapon=comp,
            target=target
        )


def _beam_resolution_to_legacy_dict(resolution: BeamResolution) -> Dict[str, Any]:
    """PROJ-359 Phase 3 adapter: BeamResolution -> legacy dict shape.

    Exists only to bridge `process_beam_attack(attack: dict)` until
    Phase 4 migrates the engine consumer. After Phase 4 this function and
    its caller are deleted.
    """
    return {
        'type': AttackType.BEAM,
        'source': resolution.source,
        'target': resolution.target,
        'damage': resolution.damage,
        'range': resolution.range,
        'origin': resolution.origin,
        'component': resolution.component,
        'direction': resolution.direction,
        'hit': resolution.hit,
    }
