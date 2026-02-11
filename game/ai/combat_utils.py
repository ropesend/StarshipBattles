"""
AI Combat Utilities - Shared helper functions for AI combat logic.

PROJ-108 Phase 3: Consolidated from TargetEvaluator to reduce duplication and
provide a clean public API for position, rotation, distance, and component access.

Exception Handling
==================
This module uses defensive programming with fallback behavior for robustness
during combat. All errors are logged for debugging, but the system continues
operating when possible.
"""
import logging
import math
from typing import Any, List, Optional

from game.core.math import Vector2

logger = logging.getLogger(__name__)


__all__ = [
    "is_vector2_like",
    "get_position",
    "get_rotation",
    "get_all_components",
    "safe_distance",
    "get_hp_percent",
    "is_in_pdc_arc",
]


def is_vector2_like(obj: Any) -> bool:
    """Check if object is a real Vector2-like object (not a MagicMock).

    Args:
        obj: Object to check

    Returns:
        True if obj has Vector2 interface (x, y, distance_to) and is not a mock
    """
    # Check for MagicMock by looking for tell-tale attributes
    if hasattr(obj, '_mock_name') or hasattr(obj, 'assert_called'):
        return False
    # Check for Vector2-like interface
    return hasattr(obj, 'x') and hasattr(obj, 'y') and hasattr(obj, 'distance_to')


def get_position(entity: Any) -> Optional[Vector2]:
    """Get position from entity, supporting both interface and direct access.

    Uses interface method get_position() if available and returns a real Vector2,
    otherwise falls back to direct .position attribute.

    Args:
        entity: Ship or entity object with position data

    Returns:
        Vector2 position of the entity, or None if unavailable

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
            if is_vector2_like(result):
                return result
        except (AttributeError, TypeError) as e:
            logger.warning(
                "get_position() failed for entity %s: %s. Using fallback.",
                entity_id, e
            )
    # Fall back to direct attribute access (raw Ship or mock with .position)
    return getattr(entity, 'position', None)


def get_rotation(entity: Any) -> float:
    """Get rotation from entity, supporting both interface and direct access.

    Args:
        entity: Ship or entity object with rotation data

    Returns:
        Rotation angle in degrees (defaults to 0.0 if unavailable)

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
                return float(result)
        except (AttributeError, TypeError) as e:
            logger.warning(
                "get_rotation() failed for entity %s: %s. Using fallback.",
                entity_id, e
            )
    # Fall back to direct attribute access
    return float(getattr(entity, 'angle', 0.0))


def get_all_components(entity: Any) -> List[Any]:
    """Get all components from entity, supporting both interface and direct access.

    Args:
        entity: Ship or entity object with components

    Returns:
        List of components, or empty list if unavailable
    """
    if hasattr(entity, 'get_all_components') and callable(getattr(entity, 'get_all_components', None)):
        return entity.get_all_components()
    return []


def safe_distance(entity1: Any, entity2: Any) -> float:
    """Safely calculate distance between two entities.

    Args:
        entity1: First entity (uses get_position)
        entity2: Second entity (uses get_position)

    Returns:
        Distance between entities, or float('inf') if position unavailable
    """
    try:
        pos1 = get_position(entity1)
        pos2 = get_position(entity2)
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


def get_hp_percent(ship: Any) -> float:
    """Calculate HP percentage for a ship based on all components.

    Args:
        ship: Ship object with components

    Returns:
        HP percentage (0.0 to 1.0), or 1.0 if no components
    """
    components = get_all_components(ship)
    if not components:
        return 1.0

    total_max = sum(getattr(c, 'max_hp', 0) for c in components)
    total_current = sum(getattr(c, 'current_hp', getattr(c, 'max_hp', 0)) for c in components)

    return total_current / total_max if total_max > 0 else 1.0


def is_in_pdc_arc(ship: Any, target: Any) -> bool:
    """Check if target is within any PDC weapon's firing arc and range.

    Args:
        ship: The ship with PDC weapons
        target: The potential target (typically a missile)

    Returns:
        True if target is within any PDC weapon's firing arc and range
    """
    ship_pos = get_position(ship)
    target_pos = get_position(target)

    if ship_pos is None or target_pos is None:
        ship_id = getattr(ship, 'id', str(id(ship)))
        target_id = getattr(target, 'id', str(id(target)))
        logger.warning(
            "PDC arc check failed: ship=%s pos=%s, target=%s pos=%s",
            ship_id, ship_pos, target_id, target_pos
        )
        return False

    # Get PDC components
    get_by_ability = getattr(ship, 'get_components_by_ability', None)
    if get_by_ability is None or not callable(get_by_ability):
        return False

    for comp in get_by_ability('WeaponAbility', operational_only=True):
        has_pdc = getattr(comp, 'has_pdc_ability', None)
        if has_pdc is None or not callable(has_pdc) or not has_pdc():
            continue

        weapon_ab = comp.get_ability('WeaponAbility')
        if weapon_ab is None:
            continue

        dist = ship_pos.distance_to(target_pos)
        if dist > weapon_ab.range:
            continue

        vec_to_target = target_pos - ship_pos
        if vec_to_target.length_squared() == 0:
            continue

        angle_to_target = math.degrees(math.atan2(vec_to_target.y, vec_to_target.x)) % 360

        ship_angle = get_rotation(ship)
        comp_facing = (ship_angle + weapon_ab.facing_angle) % 360
        diff = (angle_to_target - comp_facing + 180) % 360 - 180

        if abs(diff) <= (weapon_ab.firing_arc / 2):
            return True

    return False
