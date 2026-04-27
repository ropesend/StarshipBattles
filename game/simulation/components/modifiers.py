"""
Component Modifier Logic - V2 Format Only.

This module provides effect application for the V2 modifier format
which uses formula-based effects defined in JSON.

V1 handler functions were removed in Phase 7 cleanup.
All modifier behavior is now defined via formulas in data/modifiers.json.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def _apply_effect_to_dict(stat_key, effect_value, operation, target_dict) -> None:
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
    else:
        # Unknown operation - log warning and ignore
        logger.warning(f"Unknown operation '{operation}' for stat '{stat_key}', effect ignored")


def apply_modifier_effects(modifier_def, value, stats, component=None) -> None:
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

        # PROJ-225: Pre-process special key mappings, then delegate to _apply_effect_to_dict
        # Special case: 'projectile_stealth_add' maps to 'projectile_stealth_level'
        if stat_key == 'projectile_stealth_add' and operation == 'add':
            stat_key = 'projectile_stealth_level'

        # Special case: 'facing_angle' set goes into nested 'properties' dict
        if stat_key == 'facing_angle' and operation == 'set':
            if 'properties' not in stats:
                stats['properties'] = {}
            stats['properties']['facing_angle'] = effect_value
            continue

        # For multiply/add_to_mult on global stats, guard against non-numeric values
        if operation in ('multiply', 'add_to_mult'):
            if stat_key not in stats or not isinstance(stats[stat_key], (int, float)):
                continue

        _apply_effect_to_dict(stat_key, effect_value, operation, stats)


def get_default_stat_multipliers() -> Dict[str, Any]:
    """
    Return default stat multipliers dictionary.

    Delegates to StatKey.create_default_stats_dict() as the single source of truth.
    Used by both Component and ShipStatsCalculator for consistency.

    PROJ-225: Unified to use StatKey enum as canonical source (DUP-CMP-004).

    Returns:
        Dict with all stat keys initialized to neutral values
        (1.0 for multipliers, 0.0 for additive, None for set operations)
    """
    from game.simulation.components.abilities.stat_keys import StatKey
    return StatKey.create_default_stats_dict()


def calculate_stat_multipliers(modifier_entries: List[Dict[str, Any]], modifier_registry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate stat multipliers from a list of modifier entries.

    Pure function - no side effects, no object state needed.
    Used by both Component and ShipStatsCalculator for consistent modifier handling.

    Args:
        modifier_entries: List of dicts with 'id' and 'value' keys
                         e.g., [{'id': 'simple_size_mount', 'value': 20.0}]
        modifier_registry: Dict mapping modifier IDs to Modifier definitions

    Returns:
        Dict of stat_key -> value (multipliers, additive values, etc.)
    """
    stats = get_default_stat_multipliers()

    for mod_entry in modifier_entries:
        mod_id = mod_entry.get('id')
        mod_value = mod_entry.get('value')

        mod_def = modifier_registry.get(mod_id)
        if mod_def:
            apply_modifier_effects(mod_def, mod_value, stats)

    return stats
