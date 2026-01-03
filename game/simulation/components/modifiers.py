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
        stats['crew_capacity_mult'] *= scale
        stats['life_support_capacity_mult'] *= scale
        # Consumptions options
        stats['consumption_mult'] *= scale

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
            stats['arc_set'] = float(arc)

    @staticmethod
    def facing(val, stats):
        """Sets the facing angle property."""
        # This is a direct property set, handled slightly differently usually,
        # but the stats dict can hold property overrides if the component knows how to look for them.
        # Alternatively, we can return specific property overrides.
        stats['properties']['facing_angle'] = val

    @staticmethod
    def precision_mount(val, stats):
        """
        Increases Base Accuracy Score.
        val: Level (0-5).
        Effect: +0.5 Score per level.
        Mass: Increases by 50% per level (1.5x, 2.0x, etc).
        """
        level = val
        score_boost = level * 0.5
        
        # Add to 'properties' override for base_accuracy
        # We need to know the original base accuracy? 
        # Actually, `_apply_base_stats` doesn't support "adding" to a property easily unless we do it here.
        # But `stats` dict has `properties`.
        # We can use a special key `base_accuracy_add` if we supported it, 
        # OR we can assume `base_accuracy` is 2.0 and override it? No, that breaks different weapons.
        
        # Solution: Use `arc_add` pattern but for accuracy.
        # Let's add `accuracy_add` to stats dict.
        if 'accuracy_add' not in stats:
            stats['accuracy_add'] = 0.0
        stats['accuracy_add'] += score_boost
        
        # Mass increase: 1.0 + (0.5 * level)
        mass_factor = 1.0 + (level * 0.5)
        stats['mass_mult'] *= mass_factor

    @staticmethod
    def rapid_fire(val, stats):
        """
        Reduces reload time.
        val is percentage multiplier of fire rate (e.g., 2.0 = 2x fire rate -> 0.5x reload).
        Range 1.0 to 100.0 (though UI might clamp differently).
        Mass scales with fire rate delta: 2x rate -> 3x mass.
        Formula: mass_mult += (rate_mult - 1.0) * 2.0
        """
        rate_mult = val
        if rate_mult < 1.0: rate_mult = 1.0
        
        # Reload time is inverse of fire rate
        stats['reload_mult'] *= (1.0 / rate_mult)
        
        # Mass scaling
        # "It the firing rate is doubled the mass should be tripled."
        # Base mass = 1. New mass = 3. Delta = +2.
        # Rate delta = +1 (from 1->2).
        # So mass added = rate_delta * 2.
        mass_increase = (rate_mult - 1.0) * 2.0
        stats['mass_mult'] += mass_increase

    @staticmethod
    def seeker_endurance(val, stats):
        """
        Increases seeker endurance.
        val: multiplier (1.0 to 10.0).
        2x endurance -> 1.5x mass.
        Formula: mass_mult *= (1.0 + (mult - 1.0) * 0.5) ?
        Wait: "2x endurance should result in 1.5x mass". 
        Base: 1.0. New: 1.5. Delta: 0.5. Endurance Delta: 1.0.
        So mass factor = 1.0 + (val - 1.0) * 0.5
        """
        mult = val
        stats['endurance_mult'] *= mult
        
        mass_factor = 1.0 + (mult - 1.0) * 0.5
        stats['mass_mult'] *= mass_factor

    @staticmethod
    def seeker_damage(val, stats):
        """
        Increases seeker damage.
        val: multiplier (1.0 to 1000.0).
        2x damage -> 1.75x mass.
        Base: 1.0. New: 1.75. Delta: 0.75. Dmg Delta: 1.0.
        So mass factor = 1.0 + (val - 1.0) * 0.75
        """
        mult = val
        stats['projectile_damage_mult'] *= mult
        
        mass_factor = 1.0 + (mult - 1.0) * 0.75
        stats['mass_mult'] *= mass_factor

    @staticmethod
    def seeker_armored(val, stats):
        """
        Increases seeker HP.
        val: multiplier (1.0 to 1000.0).
        2x HP -> 1.75x mass.
        """
        mult = val
        stats['projectile_hp_mult'] *= mult
        
        mass_factor = 1.0 + (mult - 1.0) * 0.75
        stats['mass_mult'] *= mass_factor

    @staticmethod
    def seeker_stealth(val, stats):
        """
        Makes seeker harder to hit.
        val: stealth level/factor.
        Mass rises dramatically.
        Let's assume val is arbitrary scale.
        "dramatically" -> Exponential? Or high linear?
        Let's try linear factor 2x per unit?
        stats['mass_mult'] *= (1 + val * 2.0)
        """
        level = val
        stats['projectile_stealth_level'] += level
        
        # Mass increase
        stats['mass_mult'] *= (1.0 + level * 2.0)

    @staticmethod
    def automation(val, stats):
        """
        Reduces crew requirements.
        val: Reduction percentage (0.0 to 0.99).
        Mass increases with degree of automation.
        Let's say 100% automation (0 crew) -> 2x mass.
        stats['crew_req_mult'] = 1.0 - val
        stats['mass_mult'] *= (1.0 + val)
        """
        reduction = val
        if reduction > 0.99: reduction = 0.99
        if reduction < 0.0: reduction = 0.0
        
        stats['crew_req_mult'] *= (1.0 - reduction)
        
        # Mass increase
        stats['mass_mult'] *= (1.0 + reduction)



# Registry mapping 'special' string to handler function
SPECIAL_EFFECT_HANDLERS = {
    'simple_size': ModifierEffects.simple_size,
    'range_mount': ModifierEffects.range_mount,
    'turret_mount': ModifierEffects.turret_mount,
    'facing': ModifierEffects.facing,
    'precision_mount': ModifierEffects.precision_mount,
    'rapid_fire': ModifierEffects.rapid_fire,
    'seeker_endurance': ModifierEffects.seeker_endurance,
    'seeker_damage': ModifierEffects.seeker_damage,
    'seeker_armored': ModifierEffects.seeker_armored,
    'seeker_stealth': ModifierEffects.seeker_stealth,
    'automation': ModifierEffects.automation,

}

def apply_modifier_effects(modifier_def, value, stats, component=None):
    """
    Applies the effects of a single modifier to the stats dictionary.
    
    Args:
        modifier_def: The definition object of the modifier.
        value: The current value of the modifier application.
        stats: Dictionary containing accumulated multipliers and properties.
        component: Optional reference to the component applying this modifier (for context).
    """
    eff = modifier_def.effects
    val = value

    # 1. Simple additive effects
    if 'mass_mult' in eff:
        stats['mass_mult'] *= (1.0 + eff['mass_mult'])
    if 'hp_mult' in eff:
        stats['hp_mult'] *= (1.0 + eff['hp_mult'])
    if 'damage_mult' in eff:
        stats['damage_mult'] *= (1.0 + eff['damage_mult'])
    if 'range_mult' in eff:
        stats['range_mult'] *= (1.0 + eff['range_mult'])
    if 'cost_mult' in eff:
        stats['cost_mult'] *= (1.0 + eff['cost_mult'])
    if 'thrust_mult' in eff:
        stats['thrust_mult'] *= (1.0 + eff['thrust_mult'])
    if 'turn_mult' in eff:
        stats['turn_mult'] *= (1.0 + eff['turn_mult'])
    if 'energy_gen_mult' in eff:
        stats['energy_gen_mult'] *= (1.0 + eff['energy_gen_mult'])
    if 'capacity_mult' in eff:
        stats['capacity_mult'] *= (1.0 + eff['capacity_mult'])
    if 'consumption_mult' in eff:
        stats['consumption_mult'] *= (1.0 + eff['consumption_mult'])
    if 'reload_mult' in eff:
        stats['reload_mult'] *= (1.0 + eff['reload_mult'])
        
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
            handler = SPECIAL_EFFECT_HANDLERS[special_type]
            # Inspect argument count to see if it accepts component
            import inspect
            sig = inspect.signature(handler)
            if 'component' in sig.parameters:
                handler(val, stats, component=component)
            else:
                handler(val, stats)
