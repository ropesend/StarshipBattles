"""
Modifier V1 to V2 Format Converter - Phase 2 Task 2.2

Converts modifiers from the old special-handler format to the new formula-based format.
Each special handler's logic is captured as formula strings.
"""
from typing import Dict, Any, List, Optional
from .modifier_schema import convert_v1_param_to_v2, convert_v1_restrictions_to_v2


# Formula mappings for each special handler
# These formulas exactly match the logic in modifiers.py handlers
SPECIAL_HANDLER_FORMULAS = {
    'hardened_mount': [
        {'stat': 'mass_mult', 'formula': 'param'},
        {'stat': 'hp_mult', 'formula': 'param ^ 2'},
        {'stat': 'cost_mult', 'formula': 'param'},
    ],

    'range_mount': [
        {'stat': 'range_mult', 'formula': '2 ^ param'},
        {'stat': 'mass_mult', 'formula': '3.5 ^ param'},
        {'stat': 'hp_mult', 'formula': '3.5 ^ param'},
        {'stat': 'cost_mult', 'formula': '3.5 ^ param'},
    ],

    'turret_mount': [
        {'stat': 'mass_mult', 'formula': '1.0 + 0.514 * ln(1.0 + param / 30.0)'},
        {'stat': 'arc_set', 'formula': 'param', 'operation': 'set'},
    ],

    'rapid_fire': [
        {'stat': 'reload_mult', 'formula': '1.0 / param'},
        # V1 does mass_mult += (param - 1.0) * 2.0, which ADDS to the multiplier
        # We use 'add_to_mult' operation for this special case (add to existing multiplier)
        {'stat': 'mass_mult', 'formula': '(param - 1.0) * 2.0', 'operation': 'add_to_mult'},
        {'stat': 'cost_mult', 'formula': 'sqrt(param)'},
    ],

    'precision_mount': [
        {'stat': 'accuracy_add', 'formula': 'param * 0.5', 'operation': 'add'},
        {'stat': 'mass_mult', 'formula': '1.0 + param * 0.5'},
        {'stat': 'cost_mult', 'formula': '1.5 ^ param'},
    ],

    'simple_size': [
        {'stat': 'mass_mult', 'formula': 'param'},
        {'stat': 'hp_mult', 'formula': 'param'},
        {'stat': 'damage_mult', 'formula': 'param'},
        {'stat': 'cost_mult', 'formula': 'param'},
        {'stat': 'thrust_mult', 'formula': 'param'},
        {'stat': 'turn_mult', 'formula': 'param'},
        {'stat': 'strategic_mult', 'formula': 'param'},
        {'stat': 'energy_gen_mult', 'formula': 'param'},
        {'stat': 'capacity_mult', 'formula': 'param'},
        {'stat': 'crew_capacity_mult', 'formula': 'param'},
        {'stat': 'life_support_capacity_mult', 'formula': 'param'},
        {'stat': 'consumption_mult', 'formula': 'param'},
    ],

    'seeker_endurance': [
        {'stat': 'endurance_mult', 'formula': 'param'},
        {'stat': 'mass_mult', 'formula': '1.0 + (param - 1.0) * 0.5'},
        {'stat': 'cost_mult', 'formula': 'param'},
    ],

    'seeker_damage': [
        {'stat': 'projectile_damage_mult', 'formula': 'param'},
        {'stat': 'mass_mult', 'formula': '1.0 + (param - 1.0) * 0.75'},
        {'stat': 'cost_mult', 'formula': 'sqrt(param)'},
    ],

    'seeker_armored': [
        {'stat': 'projectile_hp_mult', 'formula': 'param'},
        {'stat': 'mass_mult', 'formula': '1.0 + (param - 1.0) * 0.75'},
        {'stat': 'cost_mult', 'formula': 'sqrt(param)'},
    ],

    'seeker_stealth': [
        {'stat': 'projectile_stealth_add', 'formula': 'param', 'operation': 'add'},
        {'stat': 'mass_mult', 'formula': '1.0 + param * 2.0'},
        {'stat': 'cost_mult', 'formula': '2.0 ^ param'},
    ],

    'automation': [
        {'stat': 'crew_req_mult', 'formula': '1.0 - param'},
        {'stat': 'mass_mult', 'formula': '1.0 + param'},
        {'stat': 'cost_mult', 'formula': '1.0 + param'},
    ],

    'efficiency_mount': [
        {'stat': 'consumption_mult', 'formula': 'param'},
        {'stat': 'mass_mult', 'formula': '1.0 / param'},
        {'stat': 'cost_mult', 'formula': '1.0 / param'},
    ],

    'facing': [
        {'stat': 'facing_angle', 'formula': 'param', 'operation': 'set'},
    ],
}


def convert_modifier_v1_to_v2(v1_modifier: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a V1 modifier definition to V2 format.

    Args:
        v1_modifier: The V1 modifier dict

    Returns:
        V2 modifier dict with formula-based effects
    """
    v2_modifier = {
        'id': v1_modifier['id'],
    }

    # Copy optional fields
    if 'name' in v1_modifier:
        v2_modifier['name'] = v1_modifier['name']
    if 'description' in v1_modifier:
        v2_modifier['description'] = v1_modifier['description']

    # Convert param definition
    param = convert_v1_param_to_v2(v1_modifier)
    if param:
        v2_modifier['param'] = param

    # Convert effects
    v1_effects = v1_modifier.get('effects', {})

    if isinstance(v1_effects, dict):
        special_handler = v1_effects.get('special')

        if special_handler and special_handler in SPECIAL_HANDLER_FORMULAS:
            # Use predefined formulas for special handlers
            v2_modifier['effects'] = [dict(e) for e in SPECIAL_HANDLER_FORMULAS[special_handler]]
        else:
            # Convert direct stat effects (like efficient_engines)
            v2_modifier['effects'] = _convert_direct_effects(v1_effects)
    else:
        # Already a list (shouldn't happen in V1, but handle gracefully)
        v2_modifier['effects'] = v1_effects

    # Convert restrictions
    restrictions = convert_v1_restrictions_to_v2(v1_modifier)
    if restrictions:
        v2_modifier['restrictions'] = restrictions

    return v2_modifier


def _convert_direct_effects(v1_effects: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Convert V1 direct stat effects (like consumption_mult: -0.2) to V2 format.

    V1 interpretation: stats[key] *= (1.0 + value)
    V2 interpretation: stats[key] *= evaluated_formula

    So V1 value -0.2 becomes V2 formula "1.0 + -0.2" = 0.8

    Args:
        v1_effects: Dict of stat key -> value

    Returns:
        List of V2 effect dicts
    """
    effects = []

    for key, value in v1_effects.items():
        # Skip non-stat keys
        if key in ('special',):
            continue

        # Skip boolean flags like 'arc_set: true'
        if isinstance(value, bool):
            continue

        # Convert V1 value to V2 formula
        # V1: stats[key] *= (1.0 + value)
        # V2: stats[key] *= formula_result
        # Therefore: formula = "1.0 + value"
        if isinstance(value, (int, float)):
            formula = f"1.0 + {value}"
        else:
            formula = str(value)

        effects.append({
            'stat': key,
            'formula': formula,
        })

    return effects


def convert_all_modifiers(v1_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert all modifiers in a V1 modifiers file to V2 format.

    Args:
        v1_data: Dict with 'modifiers' key containing list of V1 modifiers

    Returns:
        Dict with 'modifiers' key containing list of V2 modifiers
    """
    v1_modifiers = v1_data.get('modifiers', [])

    v2_modifiers = []
    for v1_mod in v1_modifiers:
        v2_mod = convert_modifier_v1_to_v2(v1_mod)
        v2_modifiers.append(v2_mod)

    return {'modifiers': v2_modifiers}


def save_v2_modifiers(v2_data: Dict[str, Any], filepath: str) -> None:
    """
    Save V2 modifier data to a JSON file.

    Args:
        v2_data: V2 modifier data dict
        filepath: Output file path
    """
    import json
    with open(filepath, 'w') as f:
        json.dump(v2_data, f, indent=4)
