"""Modifier resolver for strategy-layer ability scaling.

Extracts modifier values (especially size_mount) from design_data component
entries and evaluates their stat effects. Used by HarvestingEngine and
ProductionEngine to scale base ability values at runtime.
"""
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.core.registry import GameRegistries


def resolve_size_multiplier(comp_entry: Any) -> float:
    """Extract the simple_size_mount value from a component entry.

    Args:
        comp_entry: Component entry from design_data layers.
            Can be a dict with 'modifiers' list, or a plain string ID.

    Returns:
        The size_mount parameter value, or 1.0 if not present.
    """
    if not isinstance(comp_entry, dict):
        return 1.0

    modifiers = comp_entry.get('modifiers', [])
    if not isinstance(modifiers, list):
        return 1.0

    for mod in modifiers:
        if isinstance(mod, dict) and mod.get('id') == 'simple_size_mount':
            return float(mod.get('value', 1.0))

    return 1.0


def resolve_stat_from_size_mount(
    comp_entry: Any,
    stat_key: str,
    registries: 'GameRegistries',
) -> float:
    """Evaluate a specific stat effect from the size_mount modifier.

    Looks up the size_mount modifier definition from registries, finds the
    effect for the requested stat_key, and evaluates its formula with the
    component's size_mount parameter value.

    Args:
        comp_entry: Component entry from design_data layers.
        stat_key: The stat key to resolve (e.g., 'harvest_rate_mult').
        registries: GameRegistries for modifier definition lookup.

    Returns:
        The evaluated stat value, or 1.0 if not applicable.
    """
    size_value = resolve_size_multiplier(comp_entry)
    if size_value == 1.0:
        return 1.0

    mod_def = registries.modifiers.get('simple_size_mount')
    if mod_def is None:
        return 1.0

    effects = mod_def.evaluate_effects(size_value)
    for effect in effects:
        if effect.stat_key == stat_key:
            return effect.value

    return 1.0
