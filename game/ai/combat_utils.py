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
from typing import Any, List, Optional, TYPE_CHECKING

from game.core.math import Vector2
from game.ai.interfaces.controllable import IControllable

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship

logger = logging.getLogger(__name__)


__all__ = [
    "is_vector2_like",
    "get_entity_id",
    "get_position",
    "get_rotation",
    "get_all_components",
    "safe_distance",
    "get_hp_percent",
    "is_in_pdc_arc",
]


def is_vector2_like(obj: Any) -> bool:
    """Check if object is a real Vector2 (not a MagicMock).

    Args:
        obj: Object to check

    Returns:
        True if obj is a Vector2 instance, False if mock or other type
    """
    # Check for MagicMock by looking for tell-tale attributes
    if hasattr(obj, '_mock_name') or hasattr(obj, 'assert_called'):
        return False
    # Check for actual Vector2 type (codebase always uses game.core.math.Vector2)
    return isinstance(obj, Vector2)


def get_entity_id(entity: Any) -> str:
    """Get a string identifier for an entity for logging purposes.

    Ships have .name, Projectiles don't have .id or .name, so we fall back
    to the Python object id for those cases.

    Args:
        entity: Any entity object (ship, projectile, etc.)

    Returns:
        String identifier: entity.name if present, else str(id(entity))
    """
    # Ships have .name attribute; Projectiles and other entities may not
    if hasattr(entity, 'name'):
        return entity.name
    return str(id(entity))


def get_position(entity: Any) -> Optional[Vector2]:
    """Get position from entity, supporting both IControllable and direct access.

    Uses interface method get_position() for IControllable entities,
    otherwise accesses .position attribute directly.

    Args:
        entity: Ship, IControllable adapter, or entity with position

    Returns:
        Vector2 position of the entity, or None if unavailable
    """
    # IControllable interface provides get_position() method
    if isinstance(entity, IControllable):
        result = entity.get_position()
        # Verify it's a real Vector2 (not a MagicMock in tests)
        if is_vector2_like(result):
            return result
        # Fall through to try .position if get_position returned mock
    # Direct attribute access for Ships, Projectiles, and test mocks
    return getattr(entity, 'position', None)


def get_rotation(entity: Any) -> float:
    """Get rotation from entity, supporting both IControllable and direct access.

    Args:
        entity: Ship, IControllable adapter, or entity with angle

    Returns:
        Rotation angle in degrees (defaults to 0.0 if unavailable)
    """
    # IControllable interface provides get_rotation() method
    if isinstance(entity, IControllable):
        return float(entity.get_rotation())
    # Direct attribute access for Ships and test mocks
    return float(getattr(entity, 'angle', 0.0))


def get_all_components(entity: Any) -> List[Any]:
    """Get all components from entity (Ship or IControllable).

    Args:
        entity: Ship or IControllable adapter with components

    Returns:
        List of components, or empty list if method unavailable
    """
    # IControllable adapters and Ships both have get_all_components()
    if isinstance(entity, IControllable):
        return entity.get_all_components()
    # Raw Ship: method check required (can't import Ship at runtime due to circular deps)
    # This is acceptable - we're checking for a specific method, not duck typing properties
    method = getattr(entity, 'get_all_components', None)
    if callable(method):
        return method()
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
            logger.warning(
                "Cannot calculate distance: entity1=%s pos=%s, entity2=%s pos=%s",
                get_entity_id(entity1), pos1, get_entity_id(entity2), pos2
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

    # All components have max_hp and current_hp attributes
    total_max = sum(c.max_hp for c in components)
    total_current = sum(c.current_hp for c in components)

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
        logger.warning(
            "PDC arc check failed: ship=%s pos=%s, target=%s pos=%s",
            get_entity_id(ship), ship_pos, get_entity_id(target), target_pos
        )
        return False

    # Get PDC components - Ships and IControllable adapters have get_components_by_ability
    if isinstance(ship, IControllable):
        pdc_components = ship.get_components_by_ability('WeaponAbility', operational_only=True)
    else:
        # Raw Ship: method check (can't import Ship at runtime due to circular deps)
        method = getattr(ship, 'get_components_by_ability', None)
        if not callable(method):
            return False
        pdc_components = method('WeaponAbility', operational_only=True)

    # Guard: can't determine firing arc for target at same position
    vec_to_target = target_pos - ship_pos
    if vec_to_target.length_squared() == 0:
        return False

    ship_angle = get_rotation(ship)

    for comp in pdc_components:
        # Components always have has_pdc_ability method
        if not comp.has_pdc_ability():
            continue

        weapon_ab = comp.get_ability('WeaponAbility')
        if weapon_ab is None:
            continue

        # PROJ-225: Delegate to WeaponAbility.check_firing_solution (single source of truth)
        if weapon_ab.check_firing_solution(ship_pos, ship_angle, target_pos):
            return True

    return False
