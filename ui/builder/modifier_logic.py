"""
UI-level wrapper for component modifier logic.
Delegates core logic to ModifierService in the simulation layer.
"""
from game.simulation.services.modifier_service import ModifierService


class ModifierLogic:
    """
    UI wrapper for modifier operations.
    Provides backward compatibility while delegating to ModifierService.
    """

    # Expose MANDATORY_MODIFIERS for backward compatibility
    MANDATORY_MODIFIERS = ModifierService.MANDATORY_MODIFIERS

    @staticmethod
    def is_modifier_allowed(mod_id, component):
        """Check if a modifier is allowed for the given component."""
        return ModifierService.is_modifier_allowed(mod_id, component)

    @staticmethod
    def get_mandatory_modifiers(component):
        """Returns a list of modifier IDs that are mandatory for this component."""
        return ModifierService.get_mandatory_modifiers(component)

    @staticmethod
    def is_modifier_mandatory(mod_id, component):
        """Check if a specific modifier is mandatory for this component."""
        return ModifierService.is_modifier_mandatory(mod_id, component)

    @staticmethod
    def get_initial_value(mod_id, component):
        """Get the initial value for a newly applied modifier."""
        return ModifierService.get_initial_value(mod_id, component)

    @staticmethod
    def ensure_mandatory_modifiers(component):
        """Ensures all mandatory modifiers are present on the component."""
        return ModifierService.ensure_mandatory_modifiers(component)

    @staticmethod
    def get_local_min_max(mod_id, component):
        """Returns (min, max) for a modifier, accounting for component-specific constraints."""
        return ModifierService.get_local_min_max(mod_id, component)

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
