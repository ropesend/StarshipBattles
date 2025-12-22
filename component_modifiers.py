"""
Component Modifier Logic Registry.
Handles specific logic for complex modifiers to avoid hardcoding them in the Component class.
"""
import math

class ModifierEffects:
    """Namespace for modifier effect logic functions."""

    @staticmethod
    def simple_size(val, stats):
        """Applies a simple scalar multiplier to most stats."""
        scale = val
        stats['mass_mult'] *= scale
        stats['hp_mult'] *= scale
        stats['damage_mult'] *= scale
        stats['cost_mult'] *= scale
        stats['thrust_mult'] *= scale
        stats['turn_mult'] *= scale
        stats['energy_gen_mult'] *= scale
        stats['capacity_mult'] *= scale

    @staticmethod
    def range_mount(val, stats):
        """
        Increases range by 2^val.
        Increases mass/hp/cost by 3.5^val.
        """
        level = val
        stats['range_mult'] *= 2.0 ** level
        cost_mult_increase = 3.5 ** level
        stats['mass_mult'] *= cost_mult_increase
        stats['hp_mult'] *= cost_mult_increase
        # Note: Cost usually scales with mass implicitly if cost is mass-based, 
        # but if cost is separate, we might want to scale it too. 
        # The original code didn't explicitly scale cost_mult here, but did scale 'mass_mult' and 'hp_mult'.
        # Let's check the original code... 
        # Original: mass_mult *= cost_mult_increase; hp_mult *= cost_mult_increase
        # It did NOT scale cost_mult directly, assuming cost might be derived or it was an oversight.
        # However, to match EXTACT behavior:
        pass 

    @staticmethod
    def turret_mount(val, stats):
        """
        Logarithmic scaling for turret mass based on arc.
        mult = 1.0 + 0.514 * ln(1 + arc/30)
        """
        arc = val
        if arc > 0:
            turret_mult = 1.0 + 0.514 * math.log(1.0 + arc / 30.0)
            stats['mass_mult'] *= turret_mult
            # Turret mount sets the arc capability (value is Total Arc in degrees, so +/- is half)
            stats['arc_set'] = float(arc) / 2.0

    @staticmethod
    def facing(val, stats):
        """Sets the facing angle property."""
        # This is a direct property set, handled slightly differently usually,
        # but the stats dict can hold property overrides if the component knows how to look for them.
        # Alternatively, we can return specific property overrides.
        stats['properties']['facing_angle'] = val

# Registry mapping 'special' string to handler function
SPECIAL_EFFECT_HANDLERS = {
    'simple_size': ModifierEffects.simple_size,
    'range_mount': ModifierEffects.range_mount,
    'turret_mount': ModifierEffects.turret_mount,
    'facing': ModifierEffects.facing,
}

def apply_modifier_effects(modifier_def, value, stats):
    """
    Applies the effects of a single modifier to the stats dictionary.
    
    Args:
        modifier_def: The definition object of the modifier.
        value: The current value of the modifier application.
        stats: Dictionary containing accumulated multipliers and properties.
    """
    eff = modifier_def.effects
    val = value

    # 1. Simple additive effects
    if 'mass_mult' in eff:
        stats['mass_mult'] *= (1.0 + eff['mass_mult'])
    if 'hp_mult' in eff:
        stats['hp_mult'] *= (1.0 + eff['hp_mult'])
        
    # 2. Mass add per unit
    if 'mass_add_per_unit' in eff:
        stats['mass_add'] += val * eff['mass_add_per_unit']
        
    # 3. Arc effects
    if 'arc_add' in eff:
        stats['arc_add'] += val
    if 'arc_set' in eff:
        # If multiple modifiers set arc, last one wins (or we could flag it)
        stats['arc_set'] = val
            
    # 4. Special logic handlers
    if 'special' in eff:
        special_type = eff['special']
        if special_type in SPECIAL_EFFECT_HANDLERS:
            SPECIAL_EFFECT_HANDLERS[special_type](val, stats)
