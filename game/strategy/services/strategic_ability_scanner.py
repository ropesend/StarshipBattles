"""Strategic Ability Scanner — scoped ability queries for the strategy layer.

Finds active instances of strategic abilities (harvest boosters, build rate
boosters, geologic stabilizers) across spatial scopes (planet, sector, system,
empire). Provides aggregation using two-phase stacking (intra-group MAX,
inter-group MULTIPLY).

Used by HarvestingEngine, ProductionEngine, and SuperweaponOrderProcessor.
"""
import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from game.core.patterns.layer_iterator import iter_components
from game.strategy.services.component_inspector import get_component_abilities

if TYPE_CHECKING:
    from game.strategy.data.planet import Planet
    from game.strategy.data.galaxy import Galaxy
    from game.strategy.data.empire import Empire

logger = logging.getLogger(__name__)


def find_abilities_at_planet(
    ability_key: str,
    planet: 'Planet',
    registries=None,
) -> List[Dict[str, Any]]:
    """Find all instances of an ability on a planet's operational facilities.

    Args:
        ability_key: Ability registry key (e.g., 'ResourceHarvestBooster').
        planet: Planet whose facilities to scan.
        registries: Optional GameRegistries for component lookup.

    Returns:
        List of ability data dicts found.
    """
    results = []
    facilities = getattr(planet, 'facilities', [])
    if not isinstance(facilities, list):
        return results
    for facility in facilities:
        if not getattr(facility, 'is_operational', True):
            continue
        for comp in iter_components(facility.design_data):
            ability_data = _extract_ability(comp, ability_key, registries)
            if ability_data is not None:
                if isinstance(ability_data, list):
                    results.extend(ability_data)
                else:
                    results.append(ability_data)
    return results


def find_abilities_in_scope(
    ability_key: str,
    target_planet: 'Planet',
    galaxy: 'Galaxy',
    empire: 'Empire',
    scope: str,
    registries=None,
) -> List[Dict[str, Any]]:
    """Find all instances of an ability affecting a planet at a given scope.

    Args:
        ability_key: Ability registry key.
        target_planet: The planet being affected.
        galaxy: Galaxy for spatial queries.
        empire: Empire that owns the abilities.
        scope: Scope string ('planet', 'sector', 'system', 'empire', 'allied_empire').
        registries: Optional GameRegistries.

    Returns:
        List of ability data dicts with their scope metadata.
    """
    planets_to_scan = _resolve_planets_for_scope(
        target_planet, galaxy, empire, scope
    )

    results = []
    for planet in planets_to_scan:
        results.extend(find_abilities_at_planet(ability_key, planet, registries))

    return results


def aggregate_multipliers(entries: List[Dict[str, Any]]) -> float:
    """Aggregate multipliers using two-phase stacking.

    Phase 1 (intra-group): MAX within the same stack_group.
    Phase 2 (inter-group): MULTIPLY across different groups.

    Entries without a stack_group each form their own group (so they multiply).

    Args:
        entries: List of dicts, each with 'multiplier' and optional 'stack_group'.

    Returns:
        Combined multiplier (1.0 if no entries).
    """
    if not entries:
        return 1.0

    # Group by stack_group
    groups: Dict[Any, float] = {}
    ungrouped_id = 0

    for entry in entries:
        multiplier = entry.get('multiplier', 1.0)
        group = entry.get('stack_group')

        if group is None:
            # Each ungrouped entry is its own group
            group = f"__ungrouped_{ungrouped_id}"
            ungrouped_id += 1

        # Intra-group: MAX
        if group in groups:
            groups[group] = max(groups[group], multiplier)
        else:
            groups[group] = multiplier

    # Inter-group: MULTIPLY
    result = 1.0
    for group_max in groups.values():
        result *= group_max

    return result


def _resolve_planets_for_scope(
    target_planet: 'Planet',
    galaxy: 'Galaxy',
    empire: 'Empire',
    scope: str,
) -> List['Planet']:
    """Determine which planets to scan based on scope.

    Args:
        target_planet: The planet being affected.
        galaxy: Galaxy for spatial queries.
        empire: Empire owning the abilities.
        scope: Scope string.

    Returns:
        List of planets to scan for abilities.
    """
    empire_id = getattr(empire, 'id', 0)

    if scope == 'planet' or scope == 'self':
        return [target_planet]

    if scope == 'sector' or scope == 'allied_sector':
        location = getattr(target_planet, 'location', None)
        get_planets = getattr(galaxy, 'get_planets_at_global_hex', None) if galaxy else None
        if location is None or get_planets is None:
            return [target_planet]
        all_planets = get_planets(location)
        if not isinstance(all_planets, list):
            return [target_planet]
        return [p for p in all_planets if getattr(p, 'owner_id', -1) == empire_id]

    if scope == 'system' or scope == 'allied_system':
        if galaxy is None:
            return [target_planet]
        location = getattr(target_planet, 'location', None)
        get_system = getattr(galaxy, 'get_system_at_location', None)
        if get_system is None or location is None:
            return [target_planet]
        system = get_system(location)
        if system is None:
            return [target_planet]
        planets = getattr(system, 'planets', [])
        if not isinstance(planets, list):
            return [target_planet]
        return [p for p in planets if getattr(p, 'owner_id', -1) == empire_id]

    if scope == 'empire':
        return list(getattr(empire, 'colonies', []))

    if scope == 'allied_empire':
        # Stub: for now, same as empire. Alliance system TBD.
        return list(getattr(empire, 'colonies', []))

    return [target_planet]


def _extract_ability(
    comp: Any,
    ability_key: str,
    registries=None,
) -> Optional[Dict[str, Any]]:
    """Extract a specific ability's data from a component entry.

    Supports inline abilities and registry lookup.

    Args:
        comp: Component entry from design_data layers (dict or str).
        ability_key: Ability registry key to look for.
        registries: Optional GameRegistries for component lookup.

    Returns:
        Ability data dict, list of dicts, or None.
    """
    if isinstance(comp, dict):
        abilities = comp.get('abilities', {})
        data = abilities.get(ability_key)
        if isinstance(data, (dict, list)):
            return data
        # Check registry
        comp_id = comp.get('id')
        if comp_id and registries is not None:
            return _extract_from_registry(comp_id, ability_key, registries)
    elif isinstance(comp, str) and registries is not None:
        return _extract_from_registry(comp, ability_key, registries)
    return None


def _extract_from_registry(
    comp_id: str,
    ability_key: str,
    registries,
) -> Optional[Dict[str, Any]]:
    """Look up ability from component registry."""
    comp_def = registries.components.get(comp_id)
    if comp_def is None:
        return None
    # comp_def may be a Component object or raw dict
    if hasattr(comp_def, 'data'):
        abilities = get_component_abilities(comp_def.data)
    else:
        abilities = get_component_abilities(comp_def)
    data = abilities.get(ability_key)
    if isinstance(data, (dict, list)):
        return data
    return None
