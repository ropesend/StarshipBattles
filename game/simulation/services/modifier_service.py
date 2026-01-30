"""
Modifier service for managing component modifiers at the simulation layer.
This provides domain logic that was previously in the UI layer.

PROJ-27: Added registry injection for testability.
PROJ-38: Added constructor-based DI with GameRegistries support.
PROJ-42: Simplified DI pattern with _get_modifiers_fallback().
"""
from typing import Optional, Dict, Any, TYPE_CHECKING
from game.core.registry import get_default_registry_provider, get_default_registries

if TYPE_CHECKING:
    from game.core.protocols import IRegistryProvider


class ModifierService:
    """Service for component modifier operations.

    Manages modifier validation, mandatory modifier application, and value constraints
    for ship components. Modifiers customize component behavior (damage, range, firing arc, etc.).

    PROJ-42: Simplified to instance-only methods (removed static calling patterns).

    Usage Patterns:
        # Instance pattern (preferred for new code):
        service = ModifierService(modifier_registry=registries.modifiers)
        if service.is_modifier_allowed('turret_mount', component):
            service.ensure_mandatory_modifiers(component)

        # With default registries (uses fallback via get_default_registries):
        service = ModifierService()
        mandatory = service.get_mandatory_modifiers(component)

    Common Methods:
        - is_modifier_allowed(mod_id, component): Check if modifier can be applied
        - get_mandatory_modifiers(component): Get list of required modifiers
        - ensure_mandatory_modifiers(component): Auto-apply required modifiers
        - get_initial_value(mod_id, component): Get default value for modifier
        - get_local_min_max(mod_id, component): Get value constraints
    """

    # Modifiers that cannot be removed by the user
    MANDATORY_MODIFIERS = ['simple_size_mount', 'range_mount', 'facing', 'turret_mount']

    def __init__(self, modifier_registry: Optional[Dict[str, Any]] = None):
        """
        Initialize ModifierService with optional modifier registry.

        Args:
            modifier_registry: Dictionary of Modifier objects keyed by ID.
                              If None, falls back via _get_modifiers_fallback().
        """
        # PROJ-42: Simplified DI pattern with fallback
        self._modifiers = modifier_registry if modifier_registry is not None else ModifierService._get_modifiers_fallback()

    @staticmethod
    def _get_modifiers_fallback() -> Dict[str, Any]:
        """
        Get modifiers registry for when none are explicitly provided.

        PROJ-42: Tries get_default_registries() first, falls back to provider
        (which shares mutable dict refs) for backward compatibility.
        PROJ-45: Also catches StateException for new exception hierarchy.
        """
        from game.core.exceptions import StateException
        try:
            return get_default_registries().modifiers
        except (RuntimeError, StateException):
            return get_default_registry_provider().get_modifiers()

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

        PROJ-42: Simplified to instance-only method.

        Args:
            component: The component to check

        Returns:
            List of mandatory modifier IDs for this component
        """
        check_allowed = lambda mod_id: self.is_modifier_allowed(mod_id, component)

        mandatory = ['simple_size_mount']  # Everyone gets size

        # Hardened Mount: For all components except Armor
        if check_allowed('hardened_mount'):
            mandatory.append('hardened_mount')

        # Efficiency Mount: For any component with resource consumption
        if check_allowed('efficiency_mount'):
            mandatory.append('efficiency_mount')

        # Use ability-based weapon detection
        is_weapon = component.has_ability('WeaponAbility')
        is_seeker = component.has_ability('SeekerWeaponAbility')

        if is_weapon:
            # Range Mount: For Projectile/Beam
            if check_allowed('range_mount'):
                mandatory.append('range_mount')

            # Precision Targeting: For BeamWeapon
            if component.has_ability('BeamWeaponAbility') and check_allowed('precision_mount'):
                mandatory.append('precision_mount')

            # Facing: For all weapons
            if check_allowed('facing'):
                mandatory.append('facing')

            # Turret: For all weapons
            if check_allowed('turret_mount'):
                mandatory.append('turret_mount')

            # Rapid Fire: For all weapons
            if check_allowed('rapid_fire'):
                mandatory.append('rapid_fire')

        if is_seeker:
            # Seeker specific variants
            if check_allowed('seeker_endurance'):
                mandatory.append('seeker_endurance')
            if check_allowed('seeker_damage'):
                mandatory.append('seeker_damage')
            if check_allowed('seeker_armored'):
                mandatory.append('seeker_armored')
            if check_allowed('seeker_stealth'):
                mandatory.append('seeker_stealth')

        # Automation: For any component with CrewRequired ability
        if 'CrewRequired' in component.data.get('abilities', {}) or 'CrewRequired' in component.abilities:
            if check_allowed('automation'):
                mandatory.append('automation')

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
