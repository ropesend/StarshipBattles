"""
UI-level wrapper for component modifier logic.
Delegates core logic to ModifierService in the simulation layer.

PROJ-42: Updated to use ModifierService instance methods.
"""
from game.simulation.services.modifier_service import ModifierService


# Cached service instance for UI use
_modifier_service = None


def _get_service() -> ModifierService:
    """Get or create a cached ModifierService instance."""
    global _modifier_service
    if _modifier_service is None:
        _modifier_service = ModifierService()
    return _modifier_service


class ModifierLogic:
    """
    UI wrapper for modifier operations.
    Provides backward compatibility while delegating to ModifierService.

    PROJ-42: Updated to use instance methods on a cached service.
    """

    # Expose MANDATORY_MODIFIERS for backward compatibility
    MANDATORY_MODIFIERS = ModifierService.MANDATORY_MODIFIERS

    @staticmethod
    def is_modifier_allowed(mod_id, component):
        """Check if a modifier is allowed for the given component."""
        return _get_service().is_modifier_allowed(mod_id, component)

    @staticmethod
    def get_mandatory_modifiers(component):
        """Returns a list of modifier IDs that are mandatory for this component."""
        return _get_service().get_mandatory_modifiers(component)

    @staticmethod
    def is_modifier_mandatory(mod_id, component):
        """Check if a specific modifier is mandatory for this component."""
        return _get_service().is_modifier_mandatory(mod_id, component)

    @staticmethod
    def get_initial_value(mod_id, component):
        """Get the initial value for a newly applied modifier."""
        return _get_service().get_initial_value(mod_id, component)

    @staticmethod
    def ensure_mandatory_modifiers(component):
        """Ensures all mandatory modifiers are present on the component."""
        return _get_service().ensure_mandatory_modifiers(component)

    @staticmethod
    def get_local_min_max(mod_id, component):
        """Returns (min, max) for a modifier, accounting for component-specific constraints."""
        return _get_service().get_local_min_max(mod_id, component)

    @staticmethod
    def calculate_snap_value(current, step, direction, min_val, max_val, smart_floor=False):
        """Calculates value for snap buttons. UI-specific logic."""
        # Smart floor logic (Size Mount special behavior)
        if smart_floor and direction < 0 and current <= step:
            return max(min_val, 1)

        if direction < 0:
            # Decrement
            remainder = current % step
            if abs(remainder) < 0.001:
                target = current - step
            else:
                target = current - remainder
            return max(min_val, target)
        else:
            # Increment
            remainder = current % step
            dist = step - remainder
            if abs(remainder) < 0.001:
                target = current + step
            else:
                target = current + dist
            return min(max_val, target)
