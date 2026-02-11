"""
ComponentInspector - Utility for inspecting ship/facility design components.

PROJ-108 Phase 3: Consolidates duplicated component/ability iteration patterns
from ColonizeValidator, SuperweaponValidator, and other strategy layer code.
"""
from typing import Any, Dict, Iterator, List, Optional, Tuple


__all__ = [
    "get_component_abilities",
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

    # Try dict access first (test mocks, raw JSON)
    if isinstance(comp_def, dict):
        return comp_def.get('abilities', {})

    # Try Component object access
    return getattr(comp_def, 'abilities', {})


def iterate_design_components(
    design_data: Dict[str, Any],
    component_registry: Dict[str, Any]
) -> Iterator[Tuple[Dict[str, Any], Any, Dict[str, Any]]]:
    """Iterate through all components in a design, yielding component details.

    This is the canonical way to iterate over design components with their
    definitions and abilities. Handles various layer formats.

    Args:
        design_data: Ship/facility design data dict with 'layers' key
        component_registry: Component registry for looking up definitions

    Yields:
        Tuple of (comp_entry, comp_def, abilities):
        - comp_entry: The raw component entry dict from design_data
        - comp_def: The component definition from registry (may be None)
        - abilities: Dict of abilities from the component definition
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

            # Look up component definition
            comp_def = component_registry.get(comp_id) if comp_id else None

            # Get abilities from definition
            abilities = get_component_abilities(comp_def)

            yield comp_entry, comp_def, abilities


def ship_has_ability(
    ship: Any,
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
    design_data = getattr(ship, 'design_data', {})

    for _comp_entry, _comp_def, abilities in iterate_design_components(
        design_data, component_registry
    ):
        if ability_name in abilities:
            return True

    return False


def find_ship_with_ability(
    fleet_ships: List[Any],
    ability_name: str,
    component_registry: Dict[str, Any]
) -> Optional[Any]:
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
    ship: Any,
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
    design_data = getattr(ship, 'design_data', {})
    count = 0

    for _comp_entry, _comp_def, abilities in iterate_design_components(
        design_data, component_registry
    ):
        if ability_name in abilities:
            count += 1

    return count
