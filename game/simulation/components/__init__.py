"""
Component System - building blocks of ships.

Components are the building blocks of ships. Each component has:
- Base stats (mass, hp, cost)
- Abilities (weapons, propulsion, defense, etc.)
- Modifiers (stat adjustments)

Key exports:
- Component: The main component class
- ComponentStatus: Enum (ACTIVE, DAMAGED, DESTROYED)
- LayerType: Enum (CORE, INNER, OUTER)
- Modifier, ApplicationModifier: Modifier system classes
"""

from .component_constants import (
    ComponentStatus,
    LayerType,
    Modifier,
    ApplicationModifier,
)

from .component import (
    Component,
    ComponentCacheManager,
    create_component,
    load_components,
    load_modifiers,
    get_all_components,
    reset_component_caches,
)

__all__ = [
    # Constants/Enums
    'ComponentStatus',
    'LayerType',
    'Modifier',
    'ApplicationModifier',
    # Component class and functions
    'Component',
    'ComponentCacheManager',
    'create_component',
    'load_components',
    'load_modifiers',
    'get_all_components',
    'reset_component_caches',
]
