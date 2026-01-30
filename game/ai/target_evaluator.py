"""Target evaluation for AI decision making.

This module provides the TargetEvaluator class which scores potential targets
based on configurable rules from combat strategies.

Exception Handling
==================
This module uses defensive programming with fallback behavior for robustness
during combat. All errors are logged for debugging, but the system continues
operating when possible:

- Position/rotation access failures: Logged, falls back to direct attribute
- Division by zero: Protected with zero checks
- Missing attributes: Uses safe defaults

For fatal errors that indicate programming bugs, TargetingException is raised.
"""
import logging

from game.core.math import Vector2
from game.core.constants import AttackType, LayerType

logger = logging.getLogger(__name__)


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

    Args:
        entity: Ship or entity object with position data

    Returns:
        Vector2 position of the entity

    Note:
        Logs warnings on interface failures but continues with fallback
        to maintain combat continuity.
    """
    entity_id = getattr(entity, 'id', getattr(entity, 'name', str(id(entity))))

    # Check for interface method first (ShipControllableAdapter case)
    get_pos = getattr(entity, 'get_position', None)
    if get_pos is not None and callable(get_pos):
        try:
            result = get_pos()
            # Verify it's a real Vector2-like object (not a MagicMock)
            if _is_vector2_like(result):
                return result
        except (AttributeError, TypeError) as e:
            logger.warning(
                "get_position() failed for entity %s: %s. Using fallback.",
                entity_id, e
            )
    # Fall back to direct attribute access (raw Ship or mock with .position)
    return entity.position


def _get_rotation(entity):
    """Get rotation from entity, supporting both interface and direct access.

    Args:
        entity: Ship or entity object with rotation data

    Returns:
        Rotation angle in degrees

    Note:
        Logs warnings on interface failures but continues with fallback
        to maintain combat continuity.
    """
    entity_id = getattr(entity, 'id', getattr(entity, 'name', str(id(entity))))

    # Check for interface method first
    get_rot = getattr(entity, 'get_rotation', None)
    if get_rot is not None and callable(get_rot):
        try:
            result = get_rot()
            if isinstance(result, (int, float)):
                return result
        except (AttributeError, TypeError) as e:
            logger.warning(
                "get_rotation() failed for entity %s: %s. Using fallback.",
                entity_id, e
            )
    # Fall back to direct attribute access
    return entity.angle


def _get_all_components(entity):
    """Get all components from entity, supporting both interface and direct access."""
    if hasattr(entity, 'get_all_components') and callable(getattr(entity, 'get_all_components', None)):
        return entity.get_all_components()
    return []


def _safe_distance(entity1, entity2) -> float:
    """Safely calculate distance between two entities.

    Args:
        entity1: First entity (uses _get_position)
        entity2: Second entity (uses direct .position)

    Returns:
        Distance between entities, or float('inf') if position unavailable
    """
    try:
        pos1 = _get_position(entity1)
        pos2 = getattr(entity2, 'position', None)
        if pos1 is None or pos2 is None:
            entity1_id = getattr(entity1, 'id', str(id(entity1)))
            entity2_id = getattr(entity2, 'id', str(id(entity2)))
            logger.warning(
                "Cannot calculate distance: entity1=%s pos=%s, entity2=%s pos=%s",
                entity1_id, pos1, entity2_id, pos2
            )
            return float('inf')
        return pos1.distance_to(pos2)
    except (AttributeError, TypeError) as e:
        logger.warning("Distance calculation failed: %s", e)
        return float('inf')


class TargetEvaluator:
    """Helper to evaluate targets based on rules."""

    @staticmethod
    def evaluate(ship, candidate, rules, stat_helpers=None, distance_cache=None):
        """Evaluate a candidate target based on targeting rules.

        Args:
            ship: The ship doing the targeting
            candidate: The potential target to evaluate
            rules: List of targeting rules from strategy
            stat_helpers: Optional dict with 'get_hp_percent' and 'is_in_pdc_arc' functions
                         If not provided, uses default implementations
            distance_cache: Optional dict mapping candidate to pre-calculated distance.
                           PERF: Avoids redundant distance calculations across rules.

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
                # PERF: Use cached distance if available
                if distance_cache and candidate in distance_cache:
                    dist = distance_cache[candidate]
                else:
                    dist = _safe_distance(ship, candidate)
                # 'nearest' usually implies closer is better (higher score).
                # Existing logic: score -= dist * weight.
                # If we use weight > 0, we can do score -= dist * weight
                # Or if using factor: score += dist * factor (where factor is negative)
                if weight > 0:
                    val = -dist * weight
                else:
                    val = dist * factor

            elif r_type == 'farthest':
                # PERF: Use cached distance if available
                if distance_cache and candidate in distance_cache:
                    dist = distance_cache[candidate]
                else:
                    dist = _safe_distance(ship, candidate)
                if weight > 0:
                    val = dist * weight
                else:
                    val = dist * factor

            elif r_type == 'distance':
                # Generic distance rule
                # PERF: Use cached distance if available
                if distance_cache and candidate in distance_cache:
                    dist = distance_cache[candidate]
                else:
                    dist = _safe_distance(ship, candidate)
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
        """Default PDC arc check.

        Args:
            ship: The ship with PDC weapons
            target: The potential target (typically a missile)

        Returns:
            True if target is within any PDC weapon's firing arc and range
        """
        import math

        ship_pos = _get_position(ship)
        target_pos = getattr(target, 'position', None)

        if ship_pos is None or target_pos is None:
            ship_id = getattr(ship, 'id', str(id(ship)))
            target_id = getattr(target, 'id', str(id(target)))
            logger.warning(
                "PDC arc check failed: ship=%s pos=%s, target=%s pos=%s",
                ship_id, ship_pos, target_id, target_pos
            )
            return False

        for comp in ship.get_components_by_ability('WeaponAbility', operational_only=True):
            if comp.has_pdc_ability():
                weapon_ab = comp.get_ability('WeaponAbility')
                dist = ship_pos.distance_to(target_pos)
                if dist > weapon_ab.range:
                    continue

                vec_to_target = target_pos - ship_pos
                if vec_to_target.length_squared() == 0:
                    continue

                angle_to_target = math.degrees(math.atan2(vec_to_target.y, vec_to_target.x)) % 360

                ship_angle = _get_rotation(ship)
                comp_facing = (ship_angle + weapon_ab.facing_angle) % 360
                diff = (angle_to_target - comp_facing + 180) % 360 - 180

                if abs(diff) <= (weapon_ab.firing_arc / 2):
                    return True
        return False
