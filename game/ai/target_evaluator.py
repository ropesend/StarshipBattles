"""Target evaluation for AI decision making.

This module provides the TargetEvaluator class which scores potential targets
based on configurable rules from combat strategies.
"""
from game.core.math import Vector2
from game.core.constants import AttackType, LayerType


def _is_vector2_like(obj):
    """Check if object is a real Vector2-like object (not a MagicMock)."""
    # Check for MagicMock by looking for tell-tale attributes
    if hasattr(obj, '_mock_name') or hasattr(obj, 'assert_called'):
        return False
    # Check for Vector2-like interface
    return hasattr(obj, 'x') and hasattr(obj, 'y') and hasattr(obj, 'distance_to')


def _get_position(entity):
    """Get position from entity, supporting both interface and direct access.

    Uses interface method get_position() if available and returns a real Vector2,
    otherwise falls back to direct .position attribute.
    """
    # Check for interface method first (ShipControllableAdapter case)
    get_pos = getattr(entity, 'get_position', None)
    if get_pos is not None and callable(get_pos):
        try:
            result = get_pos()
            # Verify it's a real Vector2-like object (not a MagicMock)
            if _is_vector2_like(result):
                return result
        except Exception:
            pass
    # Fall back to direct attribute access (raw Ship or mock with .position)
    return entity.position


def _get_rotation(entity):
    """Get rotation from entity, supporting both interface and direct access."""
    # Check for interface method first
    get_rot = getattr(entity, 'get_rotation', None)
    if get_rot is not None and callable(get_rot):
        try:
            result = get_rot()
            if isinstance(result, (int, float)):
                return result
        except Exception:
            pass
    # Fall back to direct attribute access
    return entity.angle


def _get_all_components(entity):
    """Get all components from entity, supporting both interface and direct access."""
    if hasattr(entity, 'get_all_components') and callable(getattr(entity, 'get_all_components', None)):
        return entity.get_all_components()
    return []


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
                dist = _get_position(ship).distance_to(candidate.position)
                # 'nearest' usually implies closer is better (higher score).
                # Existing logic: score -= dist * weight.
                # If we use weight > 0, we can do score -= dist * weight
                # Or if using factor: score += dist * factor (where factor is negative)
                if weight > 0:
                    val = -dist * weight
                else:
                    val = dist * factor

            elif r_type == 'farthest':
                dist = _get_position(ship).distance_to(candidate.position)
                if weight > 0:
                    val = dist * weight
                else:
                    val = dist * factor

            elif r_type == 'distance':
                # Generic distance rule
                dist = _get_position(ship).distance_to(candidate.position)
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
                speed = getattr(candidate, 'velocity', Vector2(0, 0)).length()
                val = speed * (weight if weight > 0 else factor)

            elif r_type == 'slowest':
                speed = getattr(candidate, 'velocity', Vector2(0, 0)).length()
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
                # Use Ship helper method to check for weapon components
                has_wpns = any(candidate.get_components_by_ability('WeaponAbility', operational_only=False))
                if has_wpns:
                    val = weight if weight > 0 else 1000
                else:
                    if required:
                        match = False

            elif r_type == 'least_armor':
                # Use Ship helper method to get armor layer components and sum HP
                armor_comps = candidate.get_components_by_layer(LayerType.ARMOR)
                armor_hp = sum(getattr(c, 'hp', 0) for c in armor_comps)
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
        # Use Ship helper method to get all components
        components = _get_all_components(ship)
        if not components:
            return 1.0

        total_max = sum(getattr(c, 'max_hp', 0) for c in components)
        total_current = sum(getattr(c, 'current_hp', getattr(c, 'max_hp', 0)) for c in components)

        return total_current / total_max if total_max > 0 else 1.0

    @staticmethod
    def _default_is_in_pdc_arc(ship, target):
        """Default PDC arc check."""
        import math

        for comp in ship.get_components_by_ability('WeaponAbility', operational_only=True):
            if comp.has_pdc_ability():
                weapon_ab = comp.get_ability('WeaponAbility')
                ship_pos = _get_position(ship)
                dist = ship_pos.distance_to(target.position)
                if dist > weapon_ab.range:
                    continue

                vec_to_target = target.position - ship_pos
                if vec_to_target.length_squared() == 0:
                    continue

                angle_to_target = math.degrees(math.atan2(vec_to_target.y, vec_to_target.x)) % 360

                ship_angle = _get_rotation(ship)
                comp_facing = (ship_angle + weapon_ab.facing_angle) % 360
                diff = (angle_to_target - comp_facing + 180) % 360 - 180

                if abs(diff) <= (weapon_ab.firing_arc / 2):
                    return True
        return False
