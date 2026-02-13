"""
TargetingSystem - Extracted targeting logic from ShipCombatEngine.

This class handles all targeting-related operations:
- Lead/intercept calculation for projectiles
- Target selection from candidates
- Finding valid targets for weapons
- Calculating firing solutions

Part of PROJ-44 Phase 5: ShipCombatEngine Decomposition.
"""
import math
from typing import TYPE_CHECKING, List, Optional, Tuple, Any

from game.core.math import Vector2
from game.core.constants import AttackType, SimulationConstants

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.simulation.components.component import Component


class TargetingSystem:
    """
    Handles all targeting-related logic for combat.

    Extracted from ShipCombatEngine to focus on single responsibility:
    determining what to shoot at and where to aim.
    """

    def solve_lead(
        self,
        pos: Vector2,
        vel: Vector2,
        t_pos: Vector2,
        t_vel: Vector2,
        p_speed: float
    ) -> float:
        """
        Calculate interception time for a projectile.

        Uses quadratic formula to find the time at which a projectile
        fired from pos at speed p_speed will intercept a target at
        t_pos moving with velocity t_vel.

        Args:
            pos: Shooter position
            vel: Shooter velocity
            t_pos: Target position
            t_vel: Target velocity
            p_speed: Projectile speed (per tick if vel is per tick)

        Returns:
            Interception time t > 0 if solution exists, else 0
        """
        D = t_pos - pos
        V = t_vel - vel

        a = V.dot(V) - p_speed**2
        b = 2 * V.dot(D)
        c = D.dot(D)

        if a == 0:
            if b == 0:
                return 0
            t = -c / b
            return t if t > 0 else 0

        disc = b * b - 4 * a * c
        if disc < 0:
            return 0

        sqrt_disc = math.sqrt(disc)
        t1 = (-b + sqrt_disc) / (2 * a)
        t2 = (-b - sqrt_disc) / (2 * a)

        ts = [x for x in [t1, t2] if x > 0]
        return min(ts) if ts else 0

    def select_target(
        self,
        ship: 'Ship',
        candidates: List[Any]
    ) -> Optional[Any]:
        """
        Select the best target from a list of candidates.

        Filters out friendlies and dead ships, returns closest valid enemy.

        Args:
            ship: The ship doing the targeting
            candidates: List of potential targets

        Returns:
            Best target or None if no valid targets
        """
        valid_targets = []

        for candidate in candidates:
            # Skip dead ships
            if not getattr(candidate, 'is_alive', True):
                continue
            # Skip friendlies
            if getattr(candidate, 'team_id', -1) == ship.team_id:
                continue
            valid_targets.append(candidate)

        if not valid_targets:
            return None

        # Sort by distance, return closest
        valid_targets.sort(
            key=lambda t: ship.position.distance_to(t.position)
        )
        return valid_targets[0]

    def find_valid_target(
        self,
        ship: 'Ship',
        primary_target: Optional[Any],
        secondary_targets: List[Any],
        comp: 'Component',
        weapon_ab: Any
    ) -> Optional[Any]:
        """
        Find a valid target for the weapon.

        Checks primary target and secondary targets, validates each
        against weapon constraints (range, arc, type restrictions).

        Args:
            ship: The ship doing the targeting
            primary_target: Ship's current primary target
            secondary_targets: List of secondary targets
            comp: Weapon component
            weapon_ab: Weapon ability instance

        Returns:
            Valid target or None
        """
        # Build candidate list
        potential_targets = []
        if primary_target:
            potential_targets.append(primary_target)
        potential_targets.extend(secondary_targets)

        for candidate in potential_targets:
            if not candidate:
                continue

            # Skip dead or friendly
            if not getattr(candidate, 'is_alive', True):
                continue
            if getattr(candidate, 'team_id', -1) == ship.team_id:
                continue

            # PDC check - non-PDC weapons should not fire at missiles
            is_pdc = comp.has_pdc_ability()
            t_type = getattr(candidate, 'type', None)
            if t_type == AttackType.MISSILE and not is_pdc:
                continue

            # Validate firing solution
            if comp.has_ability('SeekerWeaponAbility'):
                seeker_ab = comp.get_ability('SeekerWeaponAbility')
                dist = ship.position.distance_to(candidate.position)
                max_range = seeker_ab.projectile_speed * seeker_ab.endurance * SimulationConstants.SEEKER_MAX_RANGE_MULTIPLIER
                if dist <= max_range:
                    return candidate
            else:
                aim_pos, aim_vec = self.calculate_firing_solution(ship, comp, candidate)
                if weapon_ab.check_firing_solution(ship.position, ship.angle, aim_pos):
                    return candidate

        return None

    def calculate_firing_solution(
        self,
        ship: 'Ship',
        comp: 'Component',
        target: Any
    ) -> Tuple[Vector2, Vector2]:
        """
        Calculate aim position and vector for firing at a target.

        For beam weapons: aims directly at target
        For projectile weapons: leads the target based on projectile speed

        Args:
            ship: The ship firing
            comp: The weapon component
            target: The target to fire at

        Returns:
            Tuple of (aim_position, aim_vector)
        """
        aim_pos = target.position

        # Determine target velocity
        t_vel = getattr(target, 'velocity', Vector2(0, 0))

        if comp.has_ability('ProjectileWeaponAbility') or comp.has_ability('SeekerWeaponAbility'):
            # Get projectile speed from the appropriate ability
            if comp.has_ability('SeekerWeaponAbility'):
                proj_ab = comp.get_ability('SeekerWeaponAbility')
            else:
                proj_ab = comp.get_ability('ProjectileWeaponAbility')

            projectile_speed = proj_ab.projectile_speed if proj_ab else 500
            t = self.solve_lead(
                ship.position, ship.velocity,
                target.position, t_vel,
                projectile_speed / SimulationConstants.PROJECTILE_SPEED_SCALE
            )

            if t > 0:
                aim_pos = target.position + t_vel * t
                # Correct for our own velocity (Relative Intercept)
                intercept_vec = aim_pos - ship.position
                aim_vec = intercept_vec - ship.velocity * t
            else:
                # No solution, aim at target
                aim_pos = target.position
                aim_vec = aim_pos - ship.position
        else:
            # Beam weapon - aim directly
            aim_pos = target.position
            aim_vec = aim_pos - ship.position

        return aim_pos, aim_vec
