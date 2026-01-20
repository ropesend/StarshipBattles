"""
Component Modifier Logic - V2 Format Only.

This module provides effect application for the V2 modifier format
which uses formula-based effects defined in JSON.

V1 handler functions were removed in Phase 7 cleanup.
All modifier behavior is now defined via formulas in data/modifiers.json.
"""


def _apply_effect_to_dict(stat_key, effect_value, operation, target_dict):
    """
    Apply a single effect to a stats dictionary.

    Args:
        stat_key: The stat key to modify
        effect_value: The value to apply
        operation: 'multiply', 'add', 'add_to_mult', or 'set'
        target_dict: The dictionary to modify
    """
    if operation == 'multiply':
        # Multiplicative stats: dict[key] *= value
        if stat_key in target_dict:
            target_dict[stat_key] *= effect_value
        else:
            target_dict[stat_key] = effect_value
    elif operation == 'add_to_mult':
        # Add to multiplier (e.g. rapid_fire mass scaling)
        if stat_key in target_dict:
            target_dict[stat_key] += effect_value
        else:
            target_dict[stat_key] = 1.0 + effect_value
    elif operation == 'add':
        # Additive stats: dict[key] += value
        if stat_key in target_dict:
            target_dict[stat_key] += effect_value
        else:
            target_dict[stat_key] = effect_value
    elif operation == 'set':
        # Set stats: dict[key] = value
        target_dict[stat_key] = effect_value


def apply_modifier_effects(modifier_def, value, stats, component=None):
    """
    Applies the effects of a single modifier to the stats dictionary.

    All modifiers use V2 format with formula-based effects.

    Args:
        modifier_def: The definition object of the modifier.
        value: The current value of the modifier application.
        stats: Dictionary containing accumulated multipliers and properties.
        component: Optional reference to the component applying this modifier.
    """
    effects = modifier_def.evaluate_effects(value)
    if effects is None:
        return

    for effect in effects:
        stat_key = effect.stat_key
        effect_value = effect.value
        operation = effect.operation

        # Handle targeted effects (multi-ability support)
        if effect.is_targeted() and component is not None:
            target_ability = effect.target_ability
            # Initialize ability_stats sub-dict if needed
            if target_ability not in component.ability_stats:
                component.ability_stats[target_ability] = {}
            ability_stat_dict = component.ability_stats[target_ability]

            # Apply to ability-specific stats dict
            _apply_effect_to_dict(stat_key, effect_value, operation, ability_stat_dict)
            continue  # Don't apply to global stats

        # Apply based on operation type
        if operation == 'multiply':
            # Multiplicative stats: stats[key] *= value
            if stat_key in stats and isinstance(stats[stat_key], (int, float)):
                stats[stat_key] *= effect_value
        elif operation == 'add_to_mult':
            # Add to multiplier (e.g. rapid_fire mass scaling)
            if stat_key in stats and isinstance(stats[stat_key], (int, float)):
                stats[stat_key] += effect_value
        elif operation == 'add':
            # Additive stats: stats[key] += value
            if stat_key in stats:
                stats[stat_key] += effect_value
            elif stat_key == 'mass_add':
                stats['mass_add'] += effect_value
            elif stat_key == 'arc_add':
                stats['arc_add'] += effect_value
            elif stat_key == 'accuracy_add':
                stats['accuracy_add'] += effect_value
            elif stat_key == 'projectile_stealth_add':
                stats['projectile_stealth_level'] += effect_value
        elif operation == 'set':
            # Set stats: stats[key] = value
            if stat_key == 'arc_set':
                stats['arc_set'] = effect_value
            elif stat_key == 'facing_angle':
                if 'properties' not in stats:
                    stats['properties'] = {}
                stats['properties']['facing_angle'] = effect_value
            else:
                stats[stat_key] = effect_value
