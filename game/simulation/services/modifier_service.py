"""
Modifier service for managing component modifiers at the simulation layer.
This provides domain logic that was previously in the UI layer.

PROJ-27: Added registry injection for testability.
"""
from typing import Optional, TYPE_CHECKING
from game.core.registry import get_modifier_registry, get_default_registry_provider

if TYPE_CHECKING:
    from game.core.protocols import IRegistryProvider


class ModifierService:
    """Service for component modifier operations."""

    # Modifiers that cannot be removed by the user
    MANDATORY_MODIFIERS = ['simple_size_mount', 'range_mount', 'facing', 'turret_mount']

    @staticmethod
    def is_modifier_allowed(
        mod_id: str,
        component,
        registry: Optional['IRegistryProvider'] = None
    ) -> bool:
        """
        Check if a modifier is allowed for the given component.

        Args:
            mod_id: The modifier ID to check
            component: The component to check against
            registry: Optional IRegistryProvider for dependency injection.
                     If None, uses the default singleton-backed provider.

        Returns:
            True if the modifier is allowed for this component
        """
        # PROJ-27: Use injected registry if provided, else use original function
        # for backward compatibility with tests that patch those functions
        if registry is not None:
            modifier_registry = registry.get_modifiers()
        else:
            modifier_registry = get_modifier_registry()

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

    @staticmethod
    def get_mandatory_modifiers(
        component,
        registry: Optional['IRegistryProvider'] = None
    ) -> list:
        """
        Returns a list of modifier IDs that are mandatory for this component.

        Args:
            component: The component to check
            registry: Optional IRegistryProvider for dependency injection.
                     If None, uses the default singleton-backed provider.

        Returns:
            List of mandatory modifier IDs for this component
        """
        mandatory = ['simple_size_mount']  # Everyone gets size

        # Hardened Mount: For all components except Armor
        if ModifierService.is_modifier_allowed('hardened_mount', component, registry):
            mandatory.append('hardened_mount')

        # Efficiency Mount: For any component with resource consumption
        if ModifierService.is_modifier_allowed('efficiency_mount', component, registry):
            mandatory.append('efficiency_mount')

        # Use ability-based weapon detection
        is_weapon = component.has_ability('WeaponAbility')
        is_seeker = component.has_ability('SeekerWeaponAbility')

        if is_weapon:
            # Range Mount: For Projectile/Beam
            if ModifierService.is_modifier_allowed('range_mount', component, registry):
                mandatory.append('range_mount')

            # Precision Targeting: For BeamWeapon
            if component.has_ability('BeamWeaponAbility') and ModifierService.is_modifier_allowed('precision_mount', component, registry):
                mandatory.append('precision_mount')

            # Facing: For all weapons
            if ModifierService.is_modifier_allowed('facing', component, registry):
                mandatory.append('facing')

            # Turret: For all weapons
            if ModifierService.is_modifier_allowed('turret_mount', component, registry):
                mandatory.append('turret_mount')

            # Rapid Fire: For all weapons
            if ModifierService.is_modifier_allowed('rapid_fire', component, registry):
                mandatory.append('rapid_fire')

        if is_seeker:
            # Seeker specific variants
            if ModifierService.is_modifier_allowed('seeker_endurance', component, registry):
                mandatory.append('seeker_endurance')
            if ModifierService.is_modifier_allowed('seeker_damage', component, registry):
                mandatory.append('seeker_damage')
            if ModifierService.is_modifier_allowed('seeker_armored', component, registry):
                mandatory.append('seeker_armored')
            if ModifierService.is_modifier_allowed('seeker_stealth', component, registry):
                mandatory.append('seeker_stealth')

        # Automation: For any component with CrewRequired ability
        if 'CrewRequired' in component.data.get('abilities', {}) or 'CrewRequired' in component.abilities:
            if ModifierService.is_modifier_allowed('automation', component, registry):
                mandatory.append('automation')

        return mandatory

    @staticmethod
    def is_modifier_mandatory(
        mod_id: str,
        component,
        registry: Optional['IRegistryProvider'] = None
    ) -> bool:
        """
        Check if a specific modifier is mandatory for this component.

        Args:
            mod_id: The modifier ID to check
            component: The component to check
            registry: Optional IRegistryProvider for dependency injection.

        Returns:
            True if the modifier is mandatory for this component
        """
        return mod_id in ModifierService.get_mandatory_modifiers(component, registry)

    @staticmethod
    def get_initial_value(
        mod_id: str,
        component,
        registry: Optional['IRegistryProvider'] = None
    ) -> float:
        """
        Get the initial value for a newly applied modifier.

        Args:
            mod_id: The modifier ID
            component: The component the modifier is being applied to
            registry: Optional IRegistryProvider for dependency injection.
                     If None, uses the default singleton-backed provider.

        Returns:
            The initial value for the modifier
        """
        # PROJ-27: Use injected registry if provided, else use original function
        # for backward compatibility with tests that patch those functions
        if registry is not None:
            modifier_registry = registry.get_modifiers()
        else:
            modifier_registry = get_modifier_registry()

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

    @staticmethod
    def ensure_mandatory_modifiers(
        component,
        registry: Optional['IRegistryProvider'] = None
    ) -> None:
        """
        Ensures all mandatory modifiers are present on the component.

        Args:
            component: The component to ensure modifiers on
            registry: Optional IRegistryProvider for dependency injection.
        """
        mandatory = ModifierService.get_mandatory_modifiers(component, registry)
        for mod_id in mandatory:
            if not component.get_modifier(mod_id):
                component.add_modifier(mod_id)
                m = component.get_modifier(mod_id)
                if m:
                    m.value = ModifierService.get_initial_value(mod_id, component, registry)

    @staticmethod
    def get_local_min_max(
        mod_id: str,
        component,
        registry: Optional['IRegistryProvider'] = None
    ) -> tuple:
        """
        Returns (min, max) for a modifier, accounting for component-specific constraints.

        Args:
            mod_id: The modifier ID
            component: The component context
            registry: Optional IRegistryProvider for dependency injection.
                     If None, uses the default singleton-backed provider.

        Returns:
            Tuple of (min_value, max_value) for this modifier
        """
        # PROJ-27: Use injected registry if provided, else use original function
        # for backward compatibility with tests that patch those functions
        if registry is not None:
            modifier_registry = registry.get_modifiers()
        else:
            modifier_registry = get_modifier_registry()

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
