"""
Modifier service for managing component modifiers at the simulation layer.
This provides domain logic that was previously in the UI layer.
"""
from game.core.registry import RegistryManager


class ModifierService:
    """Service for component modifier operations."""

    # Modifiers that cannot be removed by the user
    MANDATORY_MODIFIERS = ['simple_size_mount', 'range_mount', 'facing', 'turret_mount']

    @staticmethod
    def is_modifier_allowed(mod_id: str, component) -> bool:
        """Check if a modifier is allowed for the given component."""
        if mod_id not in RegistryManager.instance().modifiers:
            return False

        mod_def = RegistryManager.instance().modifiers[mod_id]
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
    def get_mandatory_modifiers(component) -> list:
        """Returns a list of modifier IDs that are mandatory for this component."""
        mandatory = ['simple_size_mount']  # Everyone gets size

        # Use ability-based weapon detection
        is_weapon = component.has_ability('WeaponAbility')
        is_seeker = component.has_ability('SeekerWeaponAbility')

        if is_weapon:
            # Range Mount: For Projectile/Beam
            if ModifierService.is_modifier_allowed('range_mount', component):
                mandatory.append('range_mount')

            # Precision Targeting: For BeamWeapon
            if component.has_ability('BeamWeaponAbility') and ModifierService.is_modifier_allowed('precision_mount', component):
                mandatory.append('precision_mount')

            # Facing: For all weapons
            if ModifierService.is_modifier_allowed('facing', component):
                mandatory.append('facing')

            # Turret: For all weapons
            if ModifierService.is_modifier_allowed('turret_mount', component):
                mandatory.append('turret_mount')

            # Rapid Fire: For all weapons
            if ModifierService.is_modifier_allowed('rapid_fire', component):
                mandatory.append('rapid_fire')

        if is_seeker:
            # Seeker specific variants
            if ModifierService.is_modifier_allowed('seeker_endurance', component):
                mandatory.append('seeker_endurance')
            if ModifierService.is_modifier_allowed('seeker_damage', component):
                mandatory.append('seeker_damage')
            if ModifierService.is_modifier_allowed('seeker_armored', component):
                mandatory.append('seeker_armored')
            if ModifierService.is_modifier_allowed('seeker_stealth', component):
                mandatory.append('seeker_stealth')

        # Automation: For any component with CrewRequired ability
        if 'CrewRequired' in component.data.get('abilities', {}) or 'CrewRequired' in component.abilities:
            if ModifierService.is_modifier_allowed('automation', component):
                mandatory.append('automation')

        return mandatory

    @staticmethod
    def is_modifier_mandatory(mod_id: str, component) -> bool:
        """Check if a specific modifier is mandatory for this component."""
        return mod_id in ModifierService.get_mandatory_modifiers(component)

    @staticmethod
    def get_initial_value(mod_id: str, component) -> float:
        """Get the initial value for a newly applied modifier."""
        mod_def = RegistryManager.instance().modifiers.get(mod_id)
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
    def ensure_mandatory_modifiers(component) -> None:
        """Ensures all mandatory modifiers are present on the component."""
        mandatory = ModifierService.get_mandatory_modifiers(component)
        for mod_id in mandatory:
            if not component.get_modifier(mod_id):
                component.add_modifier(mod_id)
                m = component.get_modifier(mod_id)
                if m:
                    m.value = ModifierService.get_initial_value(mod_id, component)

    @staticmethod
    def get_local_min_max(mod_id: str, component) -> tuple:
        """Returns (min, max) for a modifier, accounting for component-specific constraints."""
        mod_def = RegistryManager.instance().modifiers.get(mod_id)
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
