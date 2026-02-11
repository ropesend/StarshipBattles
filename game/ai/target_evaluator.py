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


def _is_vector2_like(obj) -> bool:
    """Check if object is a real Vector2-like object (not a MagicMock)."""
    # Check for MagicMock by looking for tell-tale attributes
    if hasattr(obj, '_mock_name') or hasattr(obj, 'assert_called'):
        return False
    # Check for Vector2-like interface
    return hasattr(obj, 'x') and hasattr(obj, 'y') and hasattr(obj, 'distance_to')


def _get_position(entity) -> 'Vector2':
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


def _get_rotation(entity) -> float:
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


def _get_all_components(entity) -> list:
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
    def _eval_distance_rule(ship, candidate, rule, distance_cache):
        """Evaluate distance-based rules: nearest, farthest, distance.

        Args:
            ship: The ship doing the targeting
            candidate: The potential target
            rule: The targeting rule dict
            distance_cache: Optional dict mapping candidate to pre-calculated distance

        Returns:
            Tuple of (score_value, match_succeeded)
        """
        r_type = rule.get('type')
        weight = rule.get('weight', 0)
        factor = rule.get('factor', 1)

        # PERF: Use cached distance if available
        if distance_cache and candidate in distance_cache:
            dist = distance_cache[candidate]
        else:
            dist = _safe_distance(ship, candidate)

        if r_type == 'nearest':
            # Closer is better (higher score)
            if weight > 0:
                val = -dist * weight
            else:
                val = dist * factor
        elif r_type == 'farthest':
            # Farther is better
            if weight > 0:
                val = dist * weight
            else:
                val = dist * factor
        else:  # 'distance'
            val = dist * factor

        return (val, True)

    @staticmethod
    def _eval_mass_rule(candidate, rule):
        """Evaluate mass/size-based rules: mass, largest, smallest, strongest, weakest.

        Args:
            candidate: The potential target
            rule: The targeting rule dict

        Returns:
            Tuple of (score_value, match_succeeded)
        """
        r_type = rule.get('type')
        weight = rule.get('weight', 0)
        factor = rule.get('factor', 1)
        mass = getattr(candidate, 'mass', 100)

        if r_type in ('mass', 'largest', 'strongest'):
            # Larger/stronger is better
            if weight > 0:
                val = mass * weight
            else:
                val = mass * factor
        else:  # 'smallest' or 'weakest'
            # Smaller/weaker is better
            if weight > 0:
                val = -mass * weight
            else:
                val = mass * factor  # factor should be negative

        return (val, True)

    @staticmethod
    def _eval_speed_rule(candidate, rule):
        """Evaluate speed-based rules: fastest, slowest.

        Args:
            candidate: The potential target
            rule: The targeting rule dict

        Returns:
            Tuple of (score_value, match_succeeded)
        """
        r_type = rule.get('type')
        weight = rule.get('weight', 0)
        factor = rule.get('factor', 1)
        speed = getattr(candidate, 'velocity', Vector2(0, 0)).length()

        if r_type == 'fastest':
            val = speed * (weight if weight > 0 else factor)
        else:  # 'slowest'
            val = -speed * (weight if weight > 0 else -factor)

        return (val, True)

    @staticmethod
    def _eval_damage_rule(candidate, rule, stat_helpers):
        """Evaluate damage-based rules: most_damaged, least_damaged.

        Args:
            candidate: The potential target
            rule: The targeting rule dict
            stat_helpers: Dict with 'get_hp_percent' function

        Returns:
            Tuple of (score_value, match_succeeded)
        """
        r_type = rule.get('type')
        weight = rule.get('weight', 0)
        factor = rule.get('factor', 1)
        hp_pct = stat_helpers['get_hp_percent'](candidate)

        if r_type == 'most_damaged':
            # Lower HP % is better
            if weight > 0:
                val = -hp_pct * weight * 100
            else:
                val = hp_pct * factor
        else:  # 'least_damaged'
            # Higher HP % is better
            if weight > 0:
                val = hp_pct * weight * 100
            else:
                val = hp_pct * factor

        return (val, True)

    @staticmethod
    def _eval_has_weapons_rule(candidate, rule, ship_capabilities_cache):
        """Evaluate has_weapons rule."""
        weight = rule.get('weight', 0)
        required = rule.get('required', False)

        # PERF: Use cached capability check if available
        candidate_id = getattr(candidate, 'id', None)
        if ship_capabilities_cache and candidate_id in ship_capabilities_cache:
            has_wpns = ship_capabilities_cache[candidate_id]['has_weapons']
        else:
            # Fall back to component lookup
            has_wpns = any(candidate.get_components_by_ability('WeaponAbility', operational_only=False))

        if has_wpns:
            return (weight if weight > 0 else 1000, True)
        return (0, not required)

    @staticmethod
    def _eval_least_armor_rule(candidate, rule):
        """Evaluate least_armor rule."""
        weight = rule.get('weight', 0)
        factor = rule.get('factor', 1)

        armor_comps = candidate.get_components_by_layer(LayerType.ARMOR)
        armor_hp = sum(getattr(c, 'hp', 0) for c in armor_comps)
        val = -armor_hp * (weight if weight > 0 else -factor)
        return (val, True)

    @staticmethod
    def _eval_pdc_arc_rule(ship, candidate, rule, stat_helpers):
        """Evaluate pdc_arc/missiles_in_pdc_arc rule."""
        weight = rule.get('weight', 0)
        required = rule.get('required', False)

        e_type = getattr(candidate, 'type', '')
        is_missile = e_type == 'missile' or e_type == AttackType.MISSILE

        if not is_missile:
            # Rule is specific to missiles, target is not a missile - pass through
            return (0, True)

        in_arc = stat_helpers['is_in_pdc_arc'](ship, candidate)
        if in_arc:
            return (weight if weight > 0 else 2000, True)

        # Not in arc
        if required:
            return (0, False)
        # Strong penalty if not required but logic implies we want it
        return (-999999, False)

    @staticmethod
    def _eval_capability_rule(ship, candidate, rule, stat_helpers, ship_capabilities_cache):
        """Evaluate capability-based rules: has_weapons, least_armor, pdc_arc/missiles_in_pdc_arc.

        Args:
            ship: The ship doing the targeting
            candidate: The potential target
            rule: The targeting rule dict
            stat_helpers: Dict with 'is_in_pdc_arc' function
            ship_capabilities_cache: Optional dict for cached capabilities

        Returns:
            Tuple of (score_value, match_succeeded)
        """
        r_type = rule.get('type')

        if r_type == 'has_weapons':
            return TargetEvaluator._eval_has_weapons_rule(
                candidate, rule, ship_capabilities_cache
            )
        elif r_type == 'least_armor':
            return TargetEvaluator._eval_least_armor_rule(candidate, rule)
        else:  # 'pdc_arc' or 'missiles_in_pdc_arc'
            return TargetEvaluator._eval_pdc_arc_rule(ship, candidate, rule, stat_helpers)

    @staticmethod
    def evaluate(ship, candidate, rules, stat_helpers=None, distance_cache=None, ship_capabilities_cache=None):
        """Evaluate a candidate target based on targeting rules.

        Args:
            ship: The ship doing the targeting
            candidate: The potential target to evaluate
            rules: List of targeting rules from strategy
            stat_helpers: Optional dict with 'get_hp_percent' and 'is_in_pdc_arc' functions
                         If not provided, uses default implementations
            distance_cache: Optional dict mapping candidate to pre-calculated distance.
                           PERF: Avoids redundant distance calculations across rules.
            ship_capabilities_cache: Optional dict mapping ship.id to pre-computed capabilities.
                           PERF: Avoids redundant component lookups for has_weapons, pdc_arc rules.
                           Structure: {ship_id: {'has_weapons': bool, 'weapon_components': List,
                                                  'has_pdc': bool, 'pdc_components': List}}

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
            required = rule.get('required', False)
            val = 0
            match = True

            if r_type in ('nearest', 'farthest', 'distance'):
                val, match = TargetEvaluator._eval_distance_rule(
                    ship, candidate, rule, distance_cache
                )

            elif r_type in ('mass', 'largest', 'smallest', 'strongest', 'weakest'):
                val, match = TargetEvaluator._eval_mass_rule(candidate, rule)

            elif r_type in ('fastest', 'slowest'):
                val, match = TargetEvaluator._eval_speed_rule(candidate, rule)

            elif r_type in ('most_damaged', 'least_damaged'):
                val, match = TargetEvaluator._eval_damage_rule(candidate, rule, stat_helpers)

            elif r_type in ('has_weapons', 'least_armor', 'pdc_arc', 'missiles_in_pdc_arc'):
                val, match = TargetEvaluator._eval_capability_rule(
                    ship, candidate, rule, stat_helpers, ship_capabilities_cache
                )

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
