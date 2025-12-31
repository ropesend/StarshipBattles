"""
Game logic for component modifiers.
Handles validation, mandatory checks, and default value calculations.
"""
from components import MODIFIER_REGISTRY

class ModifierLogic:
    
    # Modifiers that cannot be removed by the user
    MANDATORY_MODIFIERS = ['simple_size_mount', 'range_mount', 'facing', 'turret_mount']
    
    @staticmethod
    def is_modifier_allowed(mod_id, component):
        """Check if a modifier is allowed for the given component."""
        if mod_id not in MODIFIER_REGISTRY:
            return False
            
        mod_def = MODIFIER_REGISTRY[mod_id]
        if not mod_def.restrictions:
            return True
            
        if 'allow_types' in mod_def.restrictions:
            if component.type_str not in mod_def.restrictions['allow_types']:
                return False
                
        if 'deny_types' in mod_def.restrictions:
            if component.type_str in mod_def.restrictions['deny_types']:
                return False
                
        if 'allow_abilities' in mod_def.restrictions:
            # Check if component has ANY of the allowed abilities
            # Logic: If 'allow_abilities' is present, component MUST have at least one.
            # Assuming AND logical requirement? Usually "Allow if X OR Y". 
            # But here allow_abilities usually lists required capability.
            # Let's check if component.abilities is used.
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
    def get_mandatory_modifiers(component):
        """Returns a list of modifier IDs that are mandatory for this component."""
        mandatory = ['simple_size_mount'] # Everyone gets size
        
        is_weapon = component.type_str in ['Weapon', 'ProjectileWeapon', 'BeamWeapon', 'SeekerWeapon']
        is_seeker = component.type_str == 'SeekerWeapon'
        
        if is_weapon:
            # Check allowed types for specific mods before enforcing them
            # (e.g. Seeker might adhere to Projectile rules or have specific ones)
            # The Registry is the source of truth for "allowed", but we enforce "mandatory" here.
            
            # Range Mount: For Projectile/Beam 
            if ModifierLogic.is_modifier_allowed('range_mount', component):
                mandatory.append('range_mount')
                
            # Precision Targeting: For BeamWeapon
            if component.type_str == 'BeamWeapon' and ModifierLogic.is_modifier_allowed('precision_mount', component):
                mandatory.append('precision_mount')
                
            # Facing: For all weapons
            if ModifierLogic.is_modifier_allowed('facing', component):
                mandatory.append('facing')
                
            # Turret: For all weapons
            if ModifierLogic.is_modifier_allowed('turret_mount', component):
                mandatory.append('turret_mount')
            
            # Rapid Fire: For all weapons
            if ModifierLogic.is_modifier_allowed('rapid_fire', component):
                mandatory.append('rapid_fire')

        if is_seeker:
             # Seeker specific variants
             if ModifierLogic.is_modifier_allowed('seeker_endurance', component):
                 mandatory.append('seeker_endurance')
             if ModifierLogic.is_modifier_allowed('seeker_damage', component):
                 mandatory.append('seeker_damage')
             if ModifierLogic.is_modifier_allowed('seeker_armored', component):
                 mandatory.append('seeker_armored')
             if ModifierLogic.is_modifier_allowed('seeker_stealth', component):
                 mandatory.append('seeker_stealth')
                 
        # Automation: For any component with CrewRequired ability
        # Need to check if component HAS crew requirement.
        # Check base abilities or current abilities? Base/Data is safer source of truth for "capability"
        if 'CrewRequired' in component.data.get('abilities', {}) or 'CrewRequired' in component.abilities:
             if ModifierLogic.is_modifier_allowed('automation', component):
                 mandatory.append('automation')
                 
        return mandatory

    @staticmethod
    def is_modifier_mandatory(mod_id, component):
        """Check if a specific modifier is mandatory for this component."""
        return mod_id in ModifierLogic.get_mandatory_modifiers(component)

    @staticmethod
    def get_initial_value(mod_id, component):
        """Get the initial value for a newly applied modifier."""
        mod_def = MODIFIER_REGISTRY.get(mod_id)
        if not mod_def: return 0
        
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
            base_arc = component.data.get('firing_arc', mod_def.min_val)
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
        """Returns (min, max) for a modifier, accounting for component-specific constraints."""
        mod_def = MODIFIER_REGISTRY.get(mod_id)
        if not mod_def: return (0, 100)
        
        local_min = float(mod_def.min_val)
        local_max = float(mod_def.max_val)
        
        if mod_id == 'turret_mount':
            # Min value cannot be less than the component's base fixed arc
            # Use comp.data to get the TRUE base value, ignoring any current runtime modifications
            base_arc = component.data.get('firing_arc', local_min)
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
