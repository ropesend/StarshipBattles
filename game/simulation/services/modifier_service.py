"""
Modifier service for managing component modifiers at the simulation layer.
This provides domain logic that was previously in the UI layer.

PROJ-27: Added registry injection for testability.
PROJ-38: Added constructor-based DI with GameRegistries support.
"""
from typing import Optional, Dict, Any, TYPE_CHECKING
from game.core.registry import get_default_registry_provider, get_default_registries

if TYPE_CHECKING:
    from game.core.protocols import IRegistryProvider


class ModifierService:
    """Service for component modifier operations.

    PROJ-38: Supports constructor-based dependency injection.

    Usage:
        # New DI pattern (preferred)
        service = ModifierService(modifier_registry=registries.modifiers)
        service.is_modifier_allowed('turret_mount', component)

        # Transitional pattern (uses default registries)
        service = ModifierService()
        service.is_modifier_allowed('turret_mount', component)

        # Legacy static pattern (backward compatible)
        ModifierService.is_modifier_allowed('turret_mount', component)
    """

    # Modifiers that cannot be removed by the user
    MANDATORY_MODIFIERS = ['simple_size_mount', 'range_mount', 'facing', 'turret_mount']

    def __init__(self, modifier_registry: Optional[Dict[str, Any]] = None):
        """
        Initialize ModifierService with optional modifier registry.

        Args:
            modifier_registry: Dictionary of Modifier objects keyed by ID.
                              If None, falls back to get_default_registries().modifiers.
        """
        if modifier_registry is not None:
            self._modifiers = modifier_registry
        else:
            # Transitional fallback to default registries
            try:
                self._modifiers = get_default_registries().modifiers
            except RuntimeError:
                # Default registries not set yet - use provider
                self._modifiers = get_default_registry_provider().get_modifiers()

    def is_modifier_allowed(
        self_or_mod_id,
        mod_id_or_component,
        component_or_registry=None,
        registry: Optional['IRegistryProvider'] = None
    ) -> bool:
        """
        Check if a modifier is allowed for the given component.

        PROJ-38: Supports both instance and static calling patterns.

        Instance usage (preferred):
            service = ModifierService(modifier_registry=...)
            service.is_modifier_allowed('mod_id', component)

        Static usage (legacy, backward compatible):
            ModifierService.is_modifier_allowed('mod_id', component)
            ModifierService.is_modifier_allowed('mod_id', component, registry=provider)

        Args:
            mod_id: The modifier ID to check
            component: The component to check against
            registry: Optional IRegistryProvider for dependency injection (legacy pattern)

        Returns:
            True if the modifier is allowed for this component
        """
        # PROJ-38: Detect calling pattern - instance vs static
        if isinstance(self_or_mod_id, ModifierService):
            # Instance method call: service.is_modifier_allowed(mod_id, component)
            self = self_or_mod_id
            mod_id = mod_id_or_component
            component = component_or_registry
            modifier_registry = self._modifiers
        else:
            # Static-style call: ModifierService.is_modifier_allowed(mod_id, component, ...)
            mod_id = self_or_mod_id
            component = mod_id_or_component
            # PROJ-27: Use injected registry if provided, else use original function
            if component_or_registry is not None and hasattr(component_or_registry, 'get_modifiers'):
                modifier_registry = component_or_registry.get_modifiers()
            elif registry is not None:
                modifier_registry = registry.get_modifiers()
            else:
                modifier_registry = get_default_registry_provider().get_modifiers()

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

    def get_mandatory_modifiers(
        self_or_component,
        component_or_registry=None,
        registry: Optional['IRegistryProvider'] = None
    ) -> list:
        """
        Returns a list of modifier IDs that are mandatory for this component.

        PROJ-38: Supports both instance and static calling patterns.

        Args:
            component: The component to check
            registry: Optional IRegistryProvider for dependency injection (legacy pattern)

        Returns:
            List of mandatory modifier IDs for this component
        """
        # PROJ-38: Detect calling pattern - instance vs static
        if isinstance(self_or_component, ModifierService):
            # Instance method call: service.get_mandatory_modifiers(component)
            self = self_or_component
            component = component_or_registry
            # For recursive is_modifier_allowed calls, use self
            check_allowed = lambda mod_id: self.is_modifier_allowed(mod_id, component)
        else:
            # Static-style call: ModifierService.get_mandatory_modifiers(component, registry)
            component = self_or_component
            reg = component_or_registry if component_or_registry is not None else registry
            # For recursive is_modifier_allowed calls, use static pattern
            check_allowed = lambda mod_id: ModifierService.is_modifier_allowed(mod_id, component, reg)

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

    def is_modifier_mandatory(
        self_or_mod_id,
        mod_id_or_component,
        component_or_registry=None,
        registry: Optional['IRegistryProvider'] = None
    ) -> bool:
        """
        Check if a specific modifier is mandatory for this component.

        PROJ-38: Supports both instance and static calling patterns.

        Args:
            mod_id: The modifier ID to check
            component: The component to check
            registry: Optional IRegistryProvider for dependency injection (legacy pattern)

        Returns:
            True if the modifier is mandatory for this component
        """
        # PROJ-38: Detect calling pattern - instance vs static
        if isinstance(self_or_mod_id, ModifierService):
            # Instance method call: service.is_modifier_mandatory(mod_id, component)
            self = self_or_mod_id
            mod_id = mod_id_or_component
            component = component_or_registry
            return mod_id in self.get_mandatory_modifiers(component)
        else:
            # Static-style call: ModifierService.is_modifier_mandatory(mod_id, component, ...)
            mod_id = self_or_mod_id
            component = mod_id_or_component
            reg = component_or_registry if component_or_registry is not None else registry
            return mod_id in ModifierService.get_mandatory_modifiers(component, reg)

    def get_initial_value(
        self_or_mod_id,
        mod_id_or_component,
        component_or_registry=None,
        registry: Optional['IRegistryProvider'] = None
    ) -> float:
        """
        Get the initial value for a newly applied modifier.

        PROJ-38: Supports both instance and static calling patterns.

        Args:
            mod_id: The modifier ID
            component: The component the modifier is being applied to
            registry: Optional IRegistryProvider for dependency injection (legacy pattern)

        Returns:
            The initial value for the modifier
        """
        # PROJ-38: Detect calling pattern - instance vs static
        if isinstance(self_or_mod_id, ModifierService):
            # Instance method call: service.get_initial_value(mod_id, component)
            self = self_or_mod_id
            mod_id = mod_id_or_component
            component = component_or_registry
            modifier_registry = self._modifiers
        else:
            # Static-style call: ModifierService.get_initial_value(mod_id, component, ...)
            mod_id = self_or_mod_id
            component = mod_id_or_component
            if component_or_registry is not None and hasattr(component_or_registry, 'get_modifiers'):
                modifier_registry = component_or_registry.get_modifiers()
            elif registry is not None:
                modifier_registry = registry.get_modifiers()
            else:
                modifier_registry = get_default_registry_provider().get_modifiers()

        mod_def = modifier_registry.get(mod_id)
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

    def ensure_mandatory_modifiers(
        self_or_component,
        component_or_registry=None,
        registry: Optional['IRegistryProvider'] = None
    ) -> None:
        """
        Ensures all mandatory modifiers are present on the component.

        PROJ-38: Supports both instance and static calling patterns.

        Args:
            component: The component to ensure modifiers on
            registry: Optional IRegistryProvider for dependency injection (legacy pattern)
        """
        # PROJ-38: Detect calling pattern - instance vs static
        if isinstance(self_or_component, ModifierService):
            # Instance method call: service.ensure_mandatory_modifiers(component)
            self = self_or_component
            component = component_or_registry
            mandatory = self.get_mandatory_modifiers(component)
            for mod_id in mandatory:
                if not component.get_modifier(mod_id):
                    component.add_modifier(mod_id)
                    m = component.get_modifier(mod_id)
                    if m:
                        m.value = self.get_initial_value(mod_id, component)
        else:
            # Static-style call: ModifierService.ensure_mandatory_modifiers(component, registry)
            component = self_or_component
            reg = component_or_registry if component_or_registry is not None else registry
            mandatory = ModifierService.get_mandatory_modifiers(component, reg)
            for mod_id in mandatory:
                if not component.get_modifier(mod_id):
                    component.add_modifier(mod_id)
                    m = component.get_modifier(mod_id)
                    if m:
                        m.value = ModifierService.get_initial_value(mod_id, component, reg)

    def get_local_min_max(
        self_or_mod_id,
        mod_id_or_component,
        component_or_registry=None,
        registry: Optional['IRegistryProvider'] = None
    ) -> tuple:
        """
        Returns (min, max) for a modifier, accounting for component-specific constraints.

        PROJ-38: Supports both instance and static calling patterns.

        Args:
            mod_id: The modifier ID
            component: The component context
            registry: Optional IRegistryProvider for dependency injection (legacy pattern)

        Returns:
            Tuple of (min_value, max_value) for this modifier
        """
        # PROJ-38: Detect calling pattern - instance vs static
        if isinstance(self_or_mod_id, ModifierService):
            # Instance method call: service.get_local_min_max(mod_id, component)
            self = self_or_mod_id
            mod_id = mod_id_or_component
            component = component_or_registry
            modifier_registry = self._modifiers
        else:
            # Static-style call: ModifierService.get_local_min_max(mod_id, component, ...)
            mod_id = self_or_mod_id
            component = mod_id_or_component
            if component_or_registry is not None and hasattr(component_or_registry, 'get_modifiers'):
                modifier_registry = component_or_registry.get_modifiers()
            elif registry is not None:
                modifier_registry = registry.get_modifiers()
            else:
                modifier_registry = get_default_registry_provider().get_modifiers()

        mod_def = modifier_registry.get(mod_id)
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
