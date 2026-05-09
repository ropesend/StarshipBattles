"""
Game logic for component modifiers.
Handles validation, mandatory checks, and default value calculations.

ModifierLogicService is the instance-based service following the codebase's
constructor injection pattern (like VehicleClassService, ComponentService).
"""
from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING

from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode

if TYPE_CHECKING:
    from game.core.protocols import IRegistryProvider


# Dispatch table: modifier_id -> initial value (or callable(service, component, mod_def) -> float)
_INITIAL_VALUE_DEFAULTS = {
    'simple_size_mount': 1.0,
    'range_mount': 0.0,
    'facing': 0.0,
    'precision_mount': 0.0,
}

# Ability type names to search for nested firing_arc values
_WEAPON_ABILITY_TYPES = (
    'ProjectileWeaponAbility', 'BeamWeaponAbility',
    'SeekerWeaponAbility', 'WeaponAbility',
)


class ModifierLogicService:
    """Instance-based service for component modifier validation and calculations.

    Provides logic for:
    - Determining which modifiers are allowed for a component type
    - Identifying mandatory modifiers that cannot be removed
    - Calculating initial values for newly applied modifiers
    - Computing component-specific min/max value constraints
    - Snap calculations for step buttons

    Uses constructor injection for the registry provider, following the
    codebase's established DI pattern.
    """

    def __init__(self, registry_provider: 'IRegistryProvider'):
        """Initialize with a registry provider (strict DI).

        Args:
            registry_provider: Registry provider for component/modifier access.

        Raises:
            ValidationException: If registry_provider is None.
        """
        if registry_provider is None:
            raise ValidationException(
                "registry_provider is required",
                code=ErrorCode.MISSING_DEPENDENCY.value,
                context={"service": "ModifierLogicService", "parameter": "registry_provider"}
            )
        from game.ui.services.component_service import ComponentService
        self._component_service = ComponentService(registry_provider)

    def is_modifier_allowed(self, mod_id: str, component) -> bool:
        """Check if a modifier is allowed for the given component."""
        return self._component_service.is_modifier_allowed(mod_id, component)

    def get_mandatory_modifiers(self, component) -> list:
        """Returns a list of modifier IDs that are mandatory for this component.

        All applicable modifiers are mandatory — they are auto-applied at their
        default value and cannot be toggled off. Users can only adjust values.
        """
        modifiers = self._component_service.get_modifier_registry()
        return [mod_id for mod_id in modifiers
                if self._component_service.is_modifier_allowed(mod_id, component)]

    def is_modifier_mandatory(self, mod_id: str, component) -> bool:
        """Check if a specific modifier is mandatory for this component."""
        return mod_id in self.get_mandatory_modifiers(component)

    def get_initial_value(self, mod_id: str, component) -> float:
        """Get the initial value for a newly applied modifier.

        Uses a dispatch table for known modifier defaults. Unknown modifiers
        fall back to the definition's default_val.
        """
        mod_def = self._component_service.get_modifier_definition(mod_id)
        if not mod_def:
            return 0

        # Check static defaults first
        if mod_id in _INITIAL_VALUE_DEFAULTS:
            return float(_INITIAL_VALUE_DEFAULTS[mod_id])

        # turret_mount: default to component's base firing arc
        if mod_id == 'turret_mount':
            arc = self._get_base_firing_arc(component)
            return arc if arc is not None else float(mod_def.min_val)

        return mod_def.default_val

    def get_local_min_max(self, mod_id: str, component) -> tuple:
        """Returns (min, max) for a modifier, accounting for component-specific constraints."""
        mod_def = self._component_service.get_modifier_definition(mod_id)
        if not mod_def:
            return (0, 100)

        local_min = float(mod_def.min_val)
        local_max = float(mod_def.max_val)

        if mod_id == 'turret_mount':
            arc = self._get_base_firing_arc(component)
            if arc is not None:
                local_min = arc

        return (local_min, local_max)

    def ensure_mandatory_modifiers(self, component) -> None:
        """Ensures all mandatory modifiers are present on the component."""
        mandatory = self.get_mandatory_modifiers(component)
        for mod_id in mandatory:
            if not component.get_modifier(mod_id):
                component.add_modifier(mod_id)
                m = component.get_modifier(mod_id)
                if m:
                    m.value = self.get_initial_value(mod_id, component)

    def _get_base_firing_arc(self, component) -> Optional[float]:
        """Extract base firing arc from component data.

        Checks root-level 'firing_arc' first, then falls back to searching
        inside weapon ability dictionaries.
        """
        base_arc = component.data.get('firing_arc')
        if base_arc is not None:
            return float(base_arc)

        abilities = component.data.get('abilities', {})
        for ab_name in _WEAPON_ABILITY_TYPES:
            ab_data = abilities.get(ab_name, {})
            if isinstance(ab_data, dict) and 'firing_arc' in ab_data:
                return float(ab_data['firing_arc'])

        return None

    @staticmethod
    def calculate_snap_value(current, step, direction, min_val, max_val, smart_floor=False) -> Any:
        """Calculates value for snap buttons. Pure function — no dependencies."""

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
