"""Target evaluation for AI decision making.

This module provides the TargetEvaluator class which scores potential targets
based on configurable rules from combat strategies.
"""
import pygame
from game.simulation.components.component import LayerType
from game.core.constants import AttackType


class TargetEvaluator:
    """Helper to evaluate targets based on rules."""

    @staticmethod
    def evaluate(ship, candidate, rules, stat_helpers=None):
        """Evaluate a candidate target based on targeting rules.

        Args:
            ship: The ship doing the targeting
            candidate: The potential target to evaluate
            rules: List of targeting rules from strategy
            stat_helpers: Optional dict with 'get_hp_percent' and 'is_in_pdc_arc' functions
                         If not provided, uses default implementations

        Returns:
            Score for this target (higher is better), or -inf if required rule fails
        """
        score = 0

        # Use provided helpers or defaults
        if stat_helpers is None:
            stat_helpers = {
                'get_hp_percent': TargetEvaluator._default_get_hp_percent,
                'is_in_pdc_arc': TargetEvaluator._default_is_in_pdc_arc
            }

        for rule in rules:
            r_type = rule.get('type')
            weight = rule.get('weight', 0)
            factor = rule.get('factor', 1)  # Multiplier for continuous values
            required = rule.get('required', False)

            val = 0
            match = True

            if r_type == 'nearest':
                dist = ship.position.distance_to(candidate.position)
                # 'nearest' usually implies closer is better (higher score).
                # Existing logic: score -= dist * weight.
                # If we use weight > 0, we can do score -= dist * weight
                # Or if using factor: score += dist * factor (where factor is negative)
                if weight > 0:
                    val = -dist * weight
                else:
                    val = dist * factor

            elif r_type == 'farthest':
                dist = ship.position.distance_to(candidate.position)
                if weight > 0:
                    val = dist * weight
                else:
                    val = dist * factor

            elif r_type == 'distance':
                # Generic distance rule
                dist = ship.position.distance_to(candidate.position)
                val = dist * factor

            elif r_type == 'mass' or r_type == 'largest':
                mass = getattr(candidate, 'mass', 100)
                if weight > 0:
                    val = mass * weight
                else:
                    val = mass * factor

            elif r_type == 'smallest':
                mass = getattr(candidate, 'mass', 100)
                # Smallest means lower mass is better
                if weight > 0:
                    val = -mass * weight
                else:
                    val = mass * factor  # factor should be negative

            elif r_type == 'fastest':
                speed = getattr(candidate, 'velocity', pygame.math.Vector2(0, 0)).length()
                val = speed * (weight if weight > 0 else factor)

            elif r_type == 'slowest':
                speed = getattr(candidate, 'velocity', pygame.math.Vector2(0, 0)).length()
                val = -speed * (weight if weight > 0 else -factor)

            elif r_type == 'most_damaged':
                hp_pct = stat_helpers['get_hp_percent'](candidate)
                # Lower HP % is better
                # Existing: score -= hp_pct * weight * 100
                if weight > 0:
                    val = -hp_pct * weight * 100
                else:
                    val = hp_pct * factor

            elif r_type == 'least_damaged':
                hp_pct = stat_helpers['get_hp_percent'](candidate)
                # Higher HP % is better
                if weight > 0:
                    val = hp_pct * weight * 100
                else:
                    val = hp_pct * factor

            elif r_type == 'strongest':
                # Usually alias for mass/weapons?
                # Existing uses mass
                mass = getattr(candidate, 'mass', 100)
                val = mass * (weight if weight > 0 else factor)

            elif r_type == 'weakest':
                mass = getattr(candidate, 'mass', 100)
                val = -mass * (weight if weight > 0 else -factor)

            elif r_type == 'has_weapons':
                # Use Ship helper method if available
                if hasattr(candidate, 'get_components_by_ability'):
                    has_wpns = len(candidate.get_components_by_ability('WeaponAbility', operational_only=False)) > 0
                else:
                    has_wpns = any(c.has_ability('WeaponAbility') for layer in getattr(candidate, 'layers', {}).values()
                                   for c in layer.get('components', []))
                if has_wpns:
                    val = weight if weight > 0 else 1000
                else:
                    if required:
                        match = False

            elif r_type == 'least_armor':
                armor_hp = getattr(candidate, 'layers', {}).get(LayerType.ARMOR, {}).get('hp_pool', 0)
                params = -armor_hp * (weight if weight > 0 else -factor)
                val = params

            elif r_type == 'pdc_arc' or r_type == 'missiles_in_pdc_arc':
                e_type = getattr(candidate, 'type', '')
                is_missile = e_type == 'missile' or e_type == AttackType.MISSILE
                if is_missile:
                    in_arc = stat_helpers['is_in_pdc_arc'](ship, candidate)
                    if in_arc:
                        val = weight if weight > 0 else 2000
                    else:
                        if required:
                            match = False
                        else:
                            # Strong penalty if not required but logic implies we want it?
                            # Actually typical behavior: if rule exists, we prioritize it.
                            val = -999999
                            match = False
                else:
                    # If rule is specific to missiles (pdc_arc), and target is NOT missile,
                    # pass
                    pass

            if required and not match:
                return -float('inf')

            score += val

        return score

    @staticmethod
    def _default_get_hp_percent(ship):
        """Default HP percent calculation."""
        total_max = sum(layer.get('max_hp_pool', 0) for layer in getattr(ship, 'layers', {}).values())
        total_current = sum(layer.get('hp_pool', 0) for layer in getattr(ship, 'layers', {}).values())

        if total_max == 0:
            # Use Ship helper method if available
            if hasattr(ship, 'get_all_components'):
                for comp in ship.get_all_components():
                    total_max += getattr(comp, 'max_hp', 0)
                    total_current += getattr(comp, 'current_hp', getattr(comp, 'max_hp', 0))
            else:
                for layer in getattr(ship, 'layers', {}).values():
                    for comp in layer.get('components', []):
                        total_max += getattr(comp, 'max_hp', 0)
                        total_current += getattr(comp, 'current_hp', getattr(comp, 'max_hp', 0))

        return total_current / total_max if total_max > 0 else 1.0

    @staticmethod
    def _default_is_in_pdc_arc(ship, target):
        """Default PDC arc check."""
        import math

        for comp in ship.get_components_by_ability('WeaponAbility', operational_only=True):
            if comp.has_pdc_ability():
                weapon_ab = comp.get_ability('WeaponAbility')
                dist = ship.position.distance_to(target.position)
                if dist > weapon_ab.range:
                    continue

                vec_to_target = target.position - ship.position
                if vec_to_target.length_squared() == 0:
                    continue

                angle_to_target = math.degrees(math.atan2(vec_to_target.y, vec_to_target.x)) % 360

                ship_angle = ship.angle
                comp_facing = (ship_angle + weapon_ab.facing_angle) % 360
                diff = (angle_to_target - comp_facing + 180) % 360 - 180

                if abs(diff) <= (weapon_ab.firing_arc / 2):
                    return True
        return False
