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

from game.core.math import Vector2
from game.core.constants import AttackType, CombatConstants, SimulationConstants
from game.simulation.entities.projectile import Projectile

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
            if comp.has_ability('VehicleLaunch') and comp.is_active:
                attack = self._process_hangar_launch(ship, comp)
                if attack:
                    attacks.append(attack)
                continue

            # Handle Weapons
            if comp.has_ability('WeaponAbility') and comp.is_active:
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

        # Find valid target
        target = self._find_valid_target(ship, comp, weapon_ab)
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
        weapon_ab: Any
    ) -> Optional[Any]:
        """
        Find a valid target for the weapon.

        Args:
            ship: The ship targeting
            comp: Weapon component
            weapon_ab: Weapon ability instance

        Returns:
            Valid target or None
        """
        # Build secondary targets list
        secondary_targets = []
        if ship.max_targets > CombatConstants.DEFAULT_MAX_TARGETS:
            secondary_targets = ship.secondary_targets

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

        if comp.has_ability('BeamWeaponAbility'):
            # Beam attack - instant hit (shots_hit initialized in Component.__init__)
            comp.shots_hit += 1

            attacks.append({
                'type': AttackType.BEAM,
                'source': ship,
                'target': target,
                'damage': weapon_ab.damage,
                'range': weapon_ab.range,
                'origin': ship.position,
                'component': comp,
                'direction': aim_vec.normalize() if aim_vec.length() > 0 else Vector2(1, 0),
                'hit': True
            })
        else:
            # Projectile attack
            if comp.has_ability('SeekerWeaponAbility'):
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
            target_angle = math.degrees(math.atan2(rel_pos.y, rel_pos.x))
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
            damage=seeker_ab.damage,
            range_val=seeker_ab.projectile_speed * seeker_ab.endurance,
            endurance=seeker_ab.endurance,
            proj_type=AttackType.MISSILE,
            turn_rate=seeker_ab.turn_rate,
            max_speed=speed,
            target=target,
            hp=seeker_ab.projectile_hp,
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
