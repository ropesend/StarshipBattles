"""
ComponentInspector - Utility for inspecting ship/facility design components.

PROJ-108 Phase 3: Consolidates duplicated component/ability iteration patterns
from ColonizeValidator, SuperweaponValidator, and other strategy layer code.
"""
from typing import Any, Dict, Iterator, List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.data.ship_instance import ShipInstance


__all__ = [
    "get_component_abilities",
    "get_component_type",
    "get_component_threshold",
    "iterate_design_components",
    "ship_has_ability",
    "find_ship_with_ability",
    "count_ability",
]


def get_component_abilities(comp_def: Any) -> Dict[str, Any]:
    """Extract abilities from a component definition.

    Handles both dict format (test mocks, raw JSON) and Component objects (production).

    Args:
        comp_def: Either a dict with 'abilities' key or Component object, or None

    Returns:
        Dict of abilities keyed by ability name (empty dict if None or no abilities)
    """
    if comp_def is None:
        return {}

    # comp_def may be dict (JSON registry, test mocks) or Component object
    if isinstance(comp_def, dict):
        return comp_def.get('abilities', {})
    return getattr(comp_def, 'abilities', {})


def get_component_type(comp_def: Any) -> str:
    """Extract component type string from a component definition.

    Handles both dict format ('type' key) and Component objects ('type_str' attr).

    Args:
        comp_def: Either a dict with 'type' key or Component object, or None

    Returns:
        Component type string (empty string if None or no type)
    """
    if comp_def is None:
        return ''
    if isinstance(comp_def, dict):
        return comp_def.get('type', '')
    return getattr(comp_def, 'type_str', '')


def get_component_threshold(comp_def: Any, default: float) -> float:
    """Extract damage threshold from a component definition.

    Handles both dict format ('damage_threshold' key) and Component objects.

    Args:
        comp_def: Either a dict with 'damage_threshold' key or Component object, or None
        default: Default value to return if threshold not found

    Returns:
        Damage threshold value, or default if not found
    """
    if comp_def is None:
        return default
    if isinstance(comp_def, dict):
        return comp_def.get('damage_threshold', default)
    return getattr(comp_def, 'damage_threshold', default)


def iterate_design_components(
    design_data: Dict[str, Any],
    component_registry: Dict[str, Any]
) -> Iterator[Tuple[Dict[str, Any], Any, Dict[str, Any]]]:
    """Iterate through all components in a design, yielding component details.

    This is the canonical way to iterate over design components with their
    definitions and abilities. Handles various layer formats.

    Supports both patterns:
    1. Component ID lookup: comp_entry has 'id' field, abilities from registry
    2. Inline abilities: comp_entry has 'abilities' field directly (test mocks)

    Args:
        design_data: Ship/facility design data dict with 'layers' key
        component_registry: Component registry for looking up definitions

    Yields:
        Tuple of (comp_entry, comp_def, abilities):
        - comp_entry: The raw component entry dict from design_data
        - comp_def: The component definition from registry (may be None)
        - abilities: Dict of abilities from component definition OR inline
    """
    layers = design_data.get('layers', {})

    for layer_components in layers.values():
        # Skip layers that aren't lists (handles both formats)
        if not isinstance(layer_components, list):
            continue

        for comp_entry in layer_components:
            # Extract component ID from entry
            if isinstance(comp_entry, dict):
                comp_id = comp_entry.get('id', '')
            else:
                # Handle string-only entries if they exist
                comp_id = str(comp_entry) if comp_entry else ''

            # Look up component definition from registry
            comp_def = component_registry.get(comp_id) if comp_id else None

            # Get abilities from registry definition first
            abilities = get_component_abilities(comp_def)

            # Fallback: check for inline abilities in comp_entry (test mocks)
            if not abilities and isinstance(comp_entry, dict):
                abilities = comp_entry.get('abilities', {})

            yield comp_entry, comp_def, abilities


def ship_has_ability(
    ship: 'ShipInstance',
    ability_name: str,
    component_registry: Dict[str, Any]
) -> bool:
    """Check if a ship has a component with a specific ability.

    Args:
        ship: Ship object with design_data attribute
        ability_name: Name of ability to check for (e.g., "ColonyPod", "DestroyPlanet")
        component_registry: Component registry for ability lookup

    Returns:
        True if any component on the ship has the specified ability
    """
    for _comp_entry, _comp_def, abilities in iterate_design_components(
        ship.design_data, component_registry
    ):
        if ability_name in abilities:
            return True

    return False


def find_ship_with_ability(
    fleet_ships: List['ShipInstance'],
    ability_name: str,
    component_registry: Dict[str, Any]
) -> Optional['ShipInstance']:
    """Find the first ship in a list that has a specific ability.

    Args:
        fleet_ships: List of ship objects to search
        ability_name: Name of ability to find (e.g., "DestroyPlanet")
        component_registry: Component registry for ability lookup

    Returns:
        The first ship with the ability, or None if not found
    """
    for ship in fleet_ships:
        if ship_has_ability(ship, ability_name, component_registry):
            return ship
    return None


def count_ability(
    ship: 'ShipInstance',
    ability_name: str,
    component_registry: Dict[str, Any]
) -> int:
    """Count how many components on a ship have a specific ability.

    Args:
        ship: Ship object with design_data attribute
        ability_name: Name of ability to count
        component_registry: Component registry for ability lookup

    Returns:
        Number of components with the specified ability
    """
    count = 0

    for _comp_entry, _comp_def, abilities in iterate_design_components(
        ship.design_data, component_registry
    ):
        if ability_name in abilities:
            count += 1

    return count
