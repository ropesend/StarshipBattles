"""
Game logic for component modifiers.
Handles validation, mandatory checks, and default value calculations.

PROJ-489: ``ModifierLogicService`` is now a thin UI facade that delegates
all shared modifier-validation logic to the canonical simulation-layer
``ModifierService``. Only ``calculate_snap_value`` (a pure UI ergonomics
helper with no simulation equivalent) remains implemented here.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode

if TYPE_CHECKING:
    from game.simulation.services.modifier_service import ModifierService


class ModifierLogicService:
    """Instance-based UI facade for component modifier validation and calculations.

    PROJ-489: collapsed onto ``ModifierService``. Public method bodies are
    one-line delegations. Constructor injection takes a ``ModifierService``
    directly (the previous registry-provider/ComponentService round-trip is
    eliminated).

    Provides UI access to:
    - Determining which modifiers are allowed for a component type
    - Identifying mandatory modifiers that cannot be removed
    - Calculating initial values for newly applied modifiers
    - Computing component-specific min/max value constraints
    - Snap calculations for step buttons (UI-only, retained locally)
    """

    def __init__(self, modifier_service: 'ModifierService'):
        """Initialize with a ``ModifierService`` (strict DI).

        Args:
            modifier_service: Canonical simulation-layer modifier service.

        Raises:
            ValidationException: If ``modifier_service`` is None.
        """
        if modifier_service is None:
            raise ValidationException(
                "modifier_service is required",
                code=ErrorCode.MISSING_DEPENDENCY.value,
                context={"service": "ModifierLogicService", "parameter": "modifier_service"}
            )
        self._modifier_service = modifier_service

    def is_modifier_allowed(self, mod_id: str, component) -> bool:
        """Check if a modifier is allowed for the given component."""
        return self._modifier_service.is_modifier_allowed(mod_id, component)

    def get_mandatory_modifiers(self, component) -> list:
        """Returns a list of modifier IDs that are mandatory for this component."""
        return self._modifier_service.get_mandatory_modifiers(component)

    def is_modifier_mandatory(self, mod_id: str, component) -> bool:
        """Check if a specific modifier is mandatory for this component."""
        return self._modifier_service.is_modifier_mandatory(mod_id, component)

    def get_initial_value(self, mod_id: str, component) -> float:
        """Get the initial value for a newly applied modifier."""
        return self._modifier_service.get_initial_value(mod_id, component)

    def get_local_min_max(self, mod_id: str, component) -> tuple:
        """Returns (min, max) for a modifier, accounting for component-specific constraints."""
        return self._modifier_service.get_local_min_max(mod_id, component)

    def ensure_mandatory_modifiers(self, component) -> None:
        """Ensures all mandatory modifiers are present on the component."""
        self._modifier_service.ensure_mandatory_modifiers(component)

    @staticmethod
    def calculate_snap_value(current, step, direction, min_val, max_val, smart_floor=False) -> float:
        """Calculates value for snap buttons. Pure function — no dependencies.

        PROJ-489: retained on ``ModifierLogicService`` because it is a UI-only
        ergonomics helper with no simulation equivalent.
        """

        # Smart floor logic (Size Mount special behavior)
        if smart_floor and direction < 0 and current <= step:
            return min_val

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
