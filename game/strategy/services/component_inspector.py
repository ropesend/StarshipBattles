"""
ComponentInspector - Utility for inspecting ship/facility design components.

PROJ-108 Phase 3: Consolidates duplicated component/ability iteration patterns
from ColonizeValidator, SuperweaponValidator, and other strategy layer code.

PROJ-425 Phase 2 (TD-06): adds per-instance layer-view helpers that join
design layers with ``ComponentState`` from a ``ShipInstance``.
"""
from typing import Any, Dict, Iterator, List, Optional, Tuple, TYPE_CHECKING

from game.core.component_state import ComponentInstanceView, component_state_key

if TYPE_CHECKING:
    from game.strategy.data.ship_instance import ShipInstance


__all__ = [
    "get_component_abilities",
    "extract_abilities_from_component",
    "get_component_type",
    "get_component_threshold",
    "iterate_design_components",
    "iter_facility_ability_entries",
    "ship_has_ability",
    "find_ship_with_ability",
    "count_ability",
    "list_ship_abilities",
    "get_ability_list",
    "has_warp_capability",
    "iter_components_by_layer",
    "damaged_components_by_layer",
    "count_damaged_components",
    "lookup_design_max_hp",
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


def extract_abilities_from_component(comp: Any, registries=None) -> Dict[str, Any]:
    """Extract the abilities dict from a design_data component entry.

    Handles both inline abilities and registry lookup by component ID.
    This is the single source of truth for extracting abilities from
    component entries in design_data dicts.

    Args:
        comp: Component entry from design_data layers (dict or str).
        registries: Optional - either GameRegistries (with .components attr)
                    or a plain dict acting as component registry.

    Returns:
        Dict of abilities keyed by ability name (empty dict if none found).
    """
    if isinstance(comp, dict):
        abilities = comp.get('abilities', {})
        if abilities:
            return abilities
        comp_id = comp.get('id')
        if comp_id and registries is not None:
            comp_reg = _get_component_registry(registries)
            comp_def = comp_reg.get(comp_id) if comp_reg else None
            if comp_def is not None:
                return get_component_abilities(comp_def)
    elif isinstance(comp, str) and registries is not None:
        comp_reg = _get_component_registry(registries)
        comp_def = comp_reg.get(comp) if comp_reg else None
        if comp_def is not None:
            return get_component_abilities(comp_def)
    return {}


def _get_component_registry(registries) -> Optional[Dict]:
    """Get the component registry dict from a registries parameter.

    Handles both GameRegistries objects (with .components) and plain dicts
    used as component registries directly.
    """
    if hasattr(registries, 'components'):
        return registries.components
    if isinstance(registries, dict):
        return registries
    return None


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


def list_ship_abilities(
    ship: 'ShipInstance',
    component_registry: Dict[str, Any]
) -> List[str]:
    """Get all unique ability names from a ship's components.

    Args:
        ship: Ship object with design_data attribute
        component_registry: Component registry for ability lookup

    Returns:
        List of unique ability names found on the ship
    """
    abilities_set: set = set()

    for _comp_entry, _comp_def, abilities in iterate_design_components(
        ship.design_data, component_registry
    ):
        abilities_set.update(abilities.keys())

    return list(abilities_set)


def get_ability_list(
    abilities: Dict[str, Any],
    ability_name: str
) -> List[Dict[str, Any]]:
    """Get ability data as a list (handles both single and multiple abilities).

    Normalizes ability data formats: single dicts become one-element lists,
    scalar values become [{'value': val}], lists pass through unchanged.

    Args:
        abilities: Dict of all abilities on a component
        ability_name: Name of the ability to extract

    Returns:
        List of ability data dicts for the given ability name.
    """
    val = abilities.get(ability_name)
    if val is None:
        return []
    if isinstance(val, list):
        return val
    if isinstance(val, dict):
        return [val]
    return [{'value': val}]


def iter_facility_ability_entries(
    facility: Any,
    ability_name: str,
    registries: Any = None,
) -> Iterator[Tuple[Any, Dict[str, Any]]]:
    """Iterate (component, ability_entry) pairs for one ability on a facility.

    PROJ-375 Task 2.1: consolidates the iterate→extract→read-field pattern that
    was hand-rolled in 8+ engines. Walks the facility's design_data layers via
    `iter_components`, resolves each component's abilities (inline OR via
    registry lookup), and yields one normalized dict entry per ability instance.

    Normalization rules for the ability data shape:
    - dict        -> yielded once as-is.
    - list[dict]  -> yielded once per element.
    - list of non-dicts (rare) -> each element wrapped as `{"value": x}`.
    - scalar      -> wrapped as `{"value": x}` and yielded once.
    - missing / None -> yields nothing for that component.

    The component is yielded alongside the entry so callers that need
    component-level metadata (e.g. `resolve_size_multiplier(comp)`) get it
    without a second lookup.

    Args:
        facility: Object exposing a `design_data` dict (PlanetaryFacility,
            ShipDesign, or any test mock with `design_data`).
        ability_name: Ability key to extract (e.g. "WaterModifier",
            "ResourceHarvester", "PlanetaryShield").
        registries: Optional `GameRegistries` (with `.components`) or a
            plain dict acting as the component registry — passed through
            to `extract_abilities_from_component` for ID-based lookups.

    Yields:
        Tuples of `(component_entry, ability_entry_dict)`.
    """
    # Local import keeps this module free of strategy-engine imports.
    from game.core.patterns.layer_iterator import iter_components

    for comp in iter_components(facility.design_data):
        abilities = extract_abilities_from_component(comp, registries)
        data = abilities.get(ability_name)
        if data is None:
            continue
        if isinstance(data, dict):
            yield comp, data
        elif isinstance(data, list):
            for entry in data:
                if isinstance(entry, dict):
                    yield comp, entry
                else:
                    yield comp, {"value": entry}
        else:
            yield comp, {"value": data}


def lookup_design_max_hp(
    ship: 'ShipInstance', comp_id: str
) -> Optional[int]:
    """Look up a component's design max HP from available registries.

    PROJ-425 Phase 2: extracted from ``ShipInstance._lookup_design_max_hp``.

    Returns None when the registry is unavailable, the component is
    unknown, or the registry stores a formula instead of a concrete
    numeric value. This is only a legacy/missing-state fallback; normal
    ship creation persists computed per-instance ``ComponentState.max_hp``.
    """
    components = None
    if ship._registries is not None:
        components = ship._registries.get_components()
    else:
        try:
            from game.core.registry import get_default_registry_provider
            components = get_default_registry_provider().get_components()
        except Exception:  # Intentional broad catch: registry may be absent in legacy save context
            return None

    comp = components.get(comp_id)
    if comp is None:
        return None
    if isinstance(comp, dict):
        raw = comp.get('max_hp', comp.get('hp'))
    else:
        raw = getattr(comp, 'max_hp', None) or getattr(comp, 'hp', None)
    if raw is None:
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def iter_components_by_layer(
    ship: 'ShipInstance',
) -> Dict[str, List[ComponentInstanceView]]:
    """Return every component on a ship grouped by layer.

    PROJ-425 Phase 2: extracted from ``ShipInstance.iter_all_components_by_layer``.

    Walks ``ship.design_data['layers']`` in source order; joins each entry
    with ``ship.components`` via ``component_state_key(component_id,
    instance_index)``. When the key is missing, looks up max HP from the
    component registry and emits a full-HP active view. If the registry
    is unavailable or the component is unknown, the instance is skipped.

    The HULL layer is filtered out — the Fleet Report panel does not
    display it. Other unrecognised layer names pass through.
    """
    result: Dict[str, List[ComponentInstanceView]] = {}
    per_id_index: Dict[str, int] = {}
    for layer_name, components in ship.design_data.get('layers', {}).items():
        if layer_name == 'HULL':
            continue
        views: List[ComponentInstanceView] = []
        for entry in components:
            comp_id = entry.get('id') if isinstance(entry, dict) else entry
            if not comp_id:
                continue
            idx = per_id_index.get(comp_id, 0)
            per_id_index[comp_id] = idx + 1
            key = component_state_key(comp_id, idx)
            state = ship.components.get(key)
            if state is not None:
                max_hp = int(state.max_hp)
                current_hp = int(state.current_hp)
                is_active = bool(state.is_active)
            else:
                fallback_max_hp = lookup_design_max_hp(ship, comp_id)
                if fallback_max_hp is None:
                    continue
                max_hp = fallback_max_hp
                current_hp = fallback_max_hp
                is_active = True
            views.append(
                ComponentInstanceView(
                    component_id=comp_id,
                    instance_index=idx,
                    current_hp=current_hp,
                    max_hp=max_hp,
                    is_active=is_active,
                )
            )
        result[layer_name] = views
    return result


def damaged_components_by_layer(
    ship: 'ShipInstance',
) -> Dict[str, List[Tuple[str, int]]]:
    """Return damaged component instances grouped by layer.

    PROJ-425 Phase 2: extracted from ``ShipInstance.get_damaged_components_by_layer``.

    Walks the design's layers to map each ``component_id`` to its layer,
    then iterates per-instance ``ship.components`` picking out the ones
    whose ``current_hp`` is below ``max_hp``.

    Returns a dict mapping layer name to a list of
    ``(component_state_key, current_hp)`` tuples for each damaged instance.
    """
    damaged_states = [
        (key, cs) for key, cs in ship.components.items() if cs.is_damaged
    ]
    if not damaged_states:
        return {}

    comp_id_to_layer: Dict[str, str] = {}
    for layer_name, components in ship.design_data.get('layers', {}).items():
        for comp_entry in components:
            comp_id = (
                comp_entry.get('id') if isinstance(comp_entry, dict)
                else comp_entry
            )
            if comp_id:
                comp_id_to_layer[comp_id] = layer_name

    result: Dict[str, List[Tuple[str, int]]] = {}
    for key, cs in damaged_states:
        layer_name = comp_id_to_layer.get(cs.component_id, 'UNKNOWN')
        result.setdefault(layer_name, []).append((key, int(cs.current_hp)))

    return result


def count_damaged_components(ship: 'ShipInstance') -> int:
    """Count damaged component instances on a ship.

    PROJ-425 Phase 2: extracted from ``ShipInstance.get_damaged_component_count``.
    """
    return sum(1 for cs in ship.components.values() if cs.is_damaged)


def has_warp_capability(ship: Any) -> bool:
    """Check if a ship has functional warp capability.

    A ship is warp-capable if:
    1. It has a WarpJump ability with max_tonnage >= ship's mass
    2. The warp drive is undamaged (warp_max_tonnage will be 0 if damaged)
    3. The ship has enough resource storage capacity for at least one warp jump

    Args:
        ship: Object with get_calculated_stats() method (e.g., ShipInstance)

    Returns:
        True if ship can use warp points, False otherwise
    """
    calculated_stats = ship.get_calculated_stats()

    ship_mass = calculated_stats.get('mass', 0)
    if ship_mass <= 0:
        return False

    warp_max_tonnage = calculated_stats.get('warp_max_tonnage', 0)
    if warp_max_tonnage < ship_mass:
        return False

    warp_resource_costs = calculated_stats.get('warp_resource_costs', {})
    resource_storage = calculated_stats.get('resource_storage', {})

    for resource_type, cost in warp_resource_costs.items():
        if cost > 0:
            capacity = resource_storage.get(resource_type, 0)
            if capacity < cost:
                return False

    return True
