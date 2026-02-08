"""
Game logic for component modifiers.
Handles validation, mandatory checks, and default value calculations.

PROJ-43: Now uses ComponentService for modifier registry access instead of
direct MODIFIER_REGISTRY import. Uses class-level service injection.
"""


class ModifierLogic:
    """Static utility class for component modifier validation and calculations.

    Provides logic for:
    - Determining which modifiers are allowed for a component type
    - Identifying mandatory modifiers that cannot be removed
    - Calculating initial values for newly applied modifiers
    - Computing component-specific min/max value constraints
    - Snap calculations for step buttons

    This class has no instance state and all methods are static or class methods.
    It acts as a bridge between UI controls and the underlying ModifierService,
    adding builder-specific business logic on top.

    PROJ-43: Uses a class-level ComponentService for registry access.
    Service is lazily initialized on first use. Use set_service() for testing.
    """

    # Class-level service instance (lazily initialized)
    _component_service = None

    # Modifiers that cannot be removed by the user
    MANDATORY_MODIFIERS = ['simple_size_mount', 'range_mount', 'facing', 'turret_mount']

    @classmethod
    def _get_service(cls):
        """Get or create the ComponentService instance."""
        if cls._component_service is None:
            from game.ui.services.component_service import ComponentService
            cls._component_service = ComponentService()
        return cls._component_service

    @classmethod
    def set_service(cls, service):
        """Set the ComponentService instance (for testing)."""
        cls._component_service = service

    @staticmethod
    def is_modifier_allowed(mod_id, component):
        """Check if a modifier is allowed for the given component.

        PROJ-43: Delegates to ComponentService.
        """
        return ModifierLogic._get_service().is_modifier_allowed(mod_id, component)

    @staticmethod
    def get_mandatory_modifiers(component):
        """Returns a list of modifier IDs that are mandatory for this component.

        All applicable modifiers are mandatory - they are auto-applied at their
        default value and cannot be toggled off. Users can only adjust values.
        """
        mandatory = []
        modifiers = ModifierLogic._get_service().get_modifier_registry()
        for mod_id in modifiers:
            if ModifierLogic.is_modifier_allowed(mod_id, component):
                mandatory.append(mod_id)
        return mandatory

    @staticmethod
    def is_modifier_mandatory(mod_id, component):
        """Check if a specific modifier is mandatory for this component."""
        return mod_id in ModifierLogic.get_mandatory_modifiers(component)

    @staticmethod
    def get_initial_value(mod_id, component):
        """Get the initial value for a newly applied modifier.

        PROJ-43: Uses ComponentService for modifier lookup.
        """
        mod_def = ModifierLogic._get_service().get_modifier_definition(mod_id)
        if not mod_def:
            return 0

        if mod_id == 'simple_size_mount':
            return 1.0
        elif mod_id == 'range_mount':
            return 0.0
        elif mod_id == 'facing':
            return 0.0
        elif mod_id == 'precision_mount':
            return 0.0
        elif mod_id == 'turret_mount':
            # Default to base firing arc
            # Use comp.data to get the TRUE base value, ignoring any current runtime modifications
            base_arc = component.data.get('firing_arc')
            # Phase 6: Check inside ability dicts if not at root level
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
    def ensure_mandatory_modifiers(component):
        """Ensures all mandatory modifiers are present on the component."""
        mandatory = ModifierLogic.get_mandatory_modifiers(component)
        for mod_id in mandatory:
            if not component.get_modifier(mod_id):
                component.add_modifier(mod_id)
                m = component.get_modifier(mod_id)
                if m:
                    m.value = ModifierLogic.get_initial_value(mod_id, component)

    @staticmethod
    def get_local_min_max(mod_id, component):
        """Returns (min, max) for a modifier, accounting for component-specific constraints.

        PROJ-43: Uses ComponentService for modifier lookup.
        """
        mod_def = ModifierLogic._get_service().get_modifier_definition(mod_id)
        if not mod_def:
            return (0, 100)
        
        local_min = float(mod_def.min_val)
        local_max = float(mod_def.max_val)
        
        if mod_id == 'turret_mount':
            # Min value cannot be less than the component's base fixed arc
            # Use comp.data to get the TRUE base value, ignoring any current runtime modifications
            base_arc = component.data.get('firing_arc')
            # Phase 6: Check inside ability dicts if not at root level
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

    @staticmethod
    def calculate_snap_value(current, step, direction, min_val, max_val, smart_floor=False):
        """Calculates value for snap buttons."""
        
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
