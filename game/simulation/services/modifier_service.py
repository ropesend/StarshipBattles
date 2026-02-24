"""
Modifier service for managing component modifiers at the simulation layer.
This provides domain logic that was previously in the UI layer.

PROJ-27: Added registry injection for testability.
PROJ-38: Added constructor-based DI with GameRegistries support.
PROJ-42: Simplified DI pattern with _get_modifiers_fallback().
PROJ-50: Removed fallback pattern - strict DI required.
"""
from typing import Dict, Any

from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode


class ModifierService:
    """Service for component modifier operations.

    Manages modifier validation, mandatory modifier application, and value constraints
    for ship components. Modifiers customize component behavior (damage, range, firing arc, etc.).

    PROJ-42: Simplified to instance-only methods (removed static calling patterns).
    PROJ-50: Strict DI - modifier_registry is now required (no fallback).

    Usage Pattern:
        service = ModifierService(modifier_registry=registries.modifiers)
        if service.is_modifier_allowed('turret_mount', component):
            service.ensure_mandatory_modifiers(component)

    Common Methods:
        - is_modifier_allowed(mod_id, component): Check if modifier can be applied
        - get_mandatory_modifiers(component): Get list of required modifiers
        - ensure_mandatory_modifiers(component): Auto-apply required modifiers
        - get_initial_value(mod_id, component): Get default value for modifier
        - get_local_min_max(mod_id, component): Get value constraints
    """

    # Modifiers that cannot be removed by the user
    MANDATORY_MODIFIERS = ['simple_size_mount', 'range_mount', 'facing', 'turret_mount']

    def __init__(self, modifier_registry: Dict[str, Any]):
        """
        Initialize ModifierService with modifier registry.

        PROJ-50: modifier_registry is now required (strict DI).

        Args:
            modifier_registry: Dictionary of Modifier objects keyed by ID.

        Raises:
            ValidationException: If modifier_registry is None.
        """
        if modifier_registry is None:
            raise ValidationException(
                "modifier_registry is required for ModifierService",
                code=ErrorCode.MISSING_DEPENDENCY.value,
                context={"class": "ModifierService", "parameter": "modifier_registry"}
            )
        self._modifiers = modifier_registry

    def is_modifier_allowed(self, mod_id: str, component) -> bool:
        """
        Check if a modifier is allowed for the given component.

        PROJ-42: Simplified to instance-only method.

        Usage:
            service = ModifierService(modifier_registry=...)
            service.is_modifier_allowed('mod_id', component)

        Args:
            mod_id: The modifier ID to check
            component: The component to check against

        Returns:
            True if the modifier is allowed for this component
        """
        modifier_registry = self._modifiers

        if mod_id not in modifier_registry:
            return False

        mod_def = modifier_registry[mod_id]
        if not mod_def.restrictions:
            return True

        if 'allow_types' in mod_def.restrictions:
            if component.type_str not in mod_def.restrictions['allow_types']:
                return False

        if 'deny_types' in mod_def.restrictions:
            if component.type_str in mod_def.restrictions['deny_types']:
                return False

        if 'allow_abilities' in mod_def.restrictions:
            required = mod_def.restrictions['allow_abilities']
            has_ability = False
            for abil in required:
                if abil in component.abilities or abil in component.data.get('abilities', {}):
                    has_ability = True
                    break
            if not has_ability:
                return False

        return True

    def get_mandatory_modifiers(self, component) -> list:
        """
        Returns a list of modifier IDs that are mandatory for this component.

        All applicable modifiers are mandatory - they are auto-applied at their
        default value and cannot be toggled off. Users can only adjust values.

        Args:
            component: The component to check

        Returns:
            List of mandatory modifier IDs for this component
        """
        mandatory = []
        for mod_id in self._modifiers:
            if self.is_modifier_allowed(mod_id, component):
                mandatory.append(mod_id)
        return mandatory

    def is_modifier_mandatory(self, mod_id: str, component) -> bool:
        """
        Check if a specific modifier is mandatory for this component.

        PROJ-42: Simplified to instance-only method.

        Args:
            mod_id: The modifier ID to check
            component: The component to check

        Returns:
            True if the modifier is mandatory for this component
        """
        return mod_id in self.get_mandatory_modifiers(component)

    def get_initial_value(self, mod_id: str, component) -> float:
        """
        Get the initial value for a newly applied modifier.

        PROJ-42: Simplified to instance-only method.

        Args:
            mod_id: The modifier ID
            component: The component the modifier is being applied to

        Returns:
            The initial value for the modifier
        """
        mod_def = self._modifiers.get(mod_id)
        if not mod_def:
            return 0

        if mod_id == 'simple_size_mount':
            return 1.0
        elif mod_id == 'hardened_mount':
            return 1.0  # 1x mass, 1x HP (no change)
        elif mod_id == 'efficiency_mount':
            return 1.0  # 1x consumption, 1x mass (no change)
        elif mod_id == 'range_mount':
            return 0.0
        elif mod_id == 'facing':
            return 0.0
        elif mod_id == 'precision_mount':
            return 0.0
        elif mod_id == 'turret_mount':
            # Default to base firing arc
            base_arc = component.data.get('firing_arc')
            # Check inside ability dicts if not at root level
            if base_arc is None:
                abilities = component.data.get('abilities', {})
                for ab_name in ['ProjectileWeaponAbility', 'BeamWeaponAbility', 'SeekerWeaponAbility', 'WeaponAbility']:
                    ab_data = abilities.get(ab_name, {})
                    if isinstance(ab_data, dict) and 'firing_arc' in ab_data:
                        base_arc = ab_data['firing_arc']
                        break
            if base_arc is None:
                base_arc = mod_def.min_val
            return float(base_arc)

        return mod_def.default_val

    def ensure_mandatory_modifiers(self, component) -> None:
        """
        Ensures all mandatory modifiers are present on the component.

        PROJ-42: Simplified to instance-only method.

        Args:
            component: The component to ensure modifiers on
        """
        mandatory = self.get_mandatory_modifiers(component)
        for mod_id in mandatory:
            if not component.get_modifier(mod_id):
                component.add_modifier(mod_id)
                m = component.get_modifier(mod_id)
                if m:
                    m.value = self.get_initial_value(mod_id, component)

    def get_local_min_max(self, mod_id: str, component) -> tuple:
        """
        Returns (min, max) for a modifier, accounting for component-specific constraints.

        PROJ-42: Simplified to instance-only method.

        Args:
            mod_id: The modifier ID
            component: The component context

        Returns:
            Tuple of (min_value, max_value) for this modifier
        """
        mod_def = self._modifiers.get(mod_id)
        if not mod_def:
            return (0, 100)

        local_min = float(mod_def.min_val)
        local_max = float(mod_def.max_val)

        if mod_id == 'turret_mount':
            # Min value cannot be less than the component's base fixed arc
            base_arc = component.data.get('firing_arc')
            # Check inside ability dicts if not at root level
            if base_arc is None:
                abilities = component.data.get('abilities', {})
                for ab_name in ['ProjectileWeaponAbility', 'BeamWeaponAbility', 'SeekerWeaponAbility', 'WeaponAbility']:
                    ab_data = abilities.get(ab_name, {})
                    if isinstance(ab_data, dict) and 'firing_arc' in ab_data:
                        base_arc = ab_data['firing_arc']
                        break
            if base_arc is None:
                base_arc = local_min
            local_min = float(base_arc)

        return (local_min, local_max)
