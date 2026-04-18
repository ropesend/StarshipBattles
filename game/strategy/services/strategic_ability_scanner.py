"""Strategic Ability Scanner — scoped ability queries for the strategy layer.

Finds active instances of strategic abilities (harvest boosters, build rate
boosters, geologic stabilizers) across spatial scopes (planet, sector, system,
empire). Provides aggregation using two-phase stacking (intra-group MAX,
inter-group MULTIPLY).

Used by HarvestingEngine, ProductionEngine, and SuperweaponOrderProcessor.
"""
import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from game.core.patterns.layer_iterator import iter_keyed_components
from game.strategy.services.component_inspector import extract_abilities_from_component

if TYPE_CHECKING:
    from game.strategy.data.planet import Planet
    from game.strategy.data.galaxy import Galaxy
    from game.strategy.data.empire import Empire

logger = logging.getLogger(__name__)


def find_abilities_at_planet(
    ability_key: str,
    planet: 'Planet',
    registries=None,
    require_active: bool = False,
) -> List[Dict[str, Any]]:
    """Find all instances of an ability on a planet's operational facilities.

    Args:
        ability_key: Ability registry key (e.g., 'ResourceHarvestBooster').
        planet: Planet whose facilities to scan.
        registries: Optional GameRegistries for component lookup.
        require_active: If True, only include abilities whose component is in
            the ACTIVE activation phase. Defaults to False for backward
            compatibility (always-on abilities like harvest boosters).

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
        for comp_key, _layer, comp in iter_keyed_components(facility.design_data):
            ability_data = _extract_ability(comp, ability_key, registries)
            if ability_data is not None:
                if require_active and not _is_component_functionally_active(
                    facility, comp_key
                ):
                    continue
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
    require_active: bool = False,
) -> List[Dict[str, Any]]:
    """Find all instances of an ability affecting a planet at a given scope.

    Args:
        ability_key: Ability registry key.
        target_planet: The planet being affected.
        galaxy: Galaxy for spatial queries.
        empire: Empire that owns the abilities.
        scope: Scope string ('planet', 'sector', 'system', 'empire', 'allied_empire',
               'player_sector', 'player_system', 'enemy_sector', 'enemy_system').
        registries: Optional GameRegistries.
        require_active: If True, only include abilities whose component is in
            the ACTIVE activation phase.

    Returns:
        List of ability data dicts with their scope metadata.
    """
    planets_to_scan = _resolve_planets_for_scope(
        target_planet, galaxy, empire, scope
    )

    results = []
    for planet in planets_to_scan:
        results.extend(find_abilities_at_planet(
            ability_key, planet, registries, require_active=require_active
        ))

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

    if scope in ('sector', 'allied_sector', 'player_sector', 'enemy_sector'):
        get_global_hex = getattr(galaxy, 'get_planet_global_hex', None) if galaxy else None
        get_planets = getattr(galaxy, 'get_planets_at_global_hex', None) if galaxy else None
        if get_global_hex is None or get_planets is None:
            return [target_planet]
        global_hex = get_global_hex(target_planet)
        if global_hex is None:
            return [target_planet]
        all_planets = get_planets(global_hex)
        if not isinstance(all_planets, list):
            return [target_planet]
        if scope == 'enemy_sector':
            return [p for p in all_planets if getattr(p, 'owner_id', -1) != empire_id]
        return [p for p in all_planets if getattr(p, 'owner_id', -1) == empire_id]

    if scope in ('system', 'allied_system', 'player_system', 'enemy_system'):
        if galaxy is None:
            return [target_planet]
        get_system = getattr(galaxy, 'get_system_of_planet', None)
        if get_system is None:
            return [target_planet]
        system = get_system(target_planet)
        if system is None:
            return [target_planet]
        planets = getattr(system, 'planets', [])
        if not isinstance(planets, list):
            return [target_planet]
        if scope == 'enemy_system':
            return [p for p in planets if getattr(p, 'owner_id', -1) != empire_id]
        return [p for p in planets if getattr(p, 'owner_id', -1) == empire_id]

    if scope == 'empire':
        return list(getattr(empire, 'colonies', []))

    if scope == 'allied_empire':
        # Stub: for now, same as empire. Alliance system TBD.
        return list(getattr(empire, 'colonies', []))

    return [target_planet]


def _is_component_functionally_active(facility, comp_key: str) -> bool:
    """Check if a component is in the ACTIVE activation phase.

    Uses the facility's get_activation_state method to look up the
    ComponentActivationState for the given component key.

    Args:
        facility: Facility object (PlanetaryFacility or compatible).
        comp_key: Composite component key (e.g., "CORE:0:geologic_stabilizer_system").

    Returns:
        True if the component is in the ACTIVE phase, False otherwise.
        Returns False if the facility does not support activation state.
    """
    get_state = getattr(facility, 'get_activation_state', None)
    if get_state is None:
        return False
    state = get_state(comp_key)
    return state.is_functionally_active


def _extract_ability(
    comp: Any,
    ability_key: str,
    registries=None,
) -> Optional[Dict[str, Any]]:
    """Extract a specific ability's data from a component entry.

    Delegates to `component_inspector.extract_abilities_from_component`, which
    is the single source of truth for ability extraction and accepts either a
    `GameRegistries` (with `.components` attr) or a plain components dict as
    `registries`. Previously the scanner had its own registry walker that
    required the `GameRegistries` shape — callers that passed only the
    components dict silently got no abilities back (see PROJ-277).

    Args:
        comp: Component entry from design_data layers (dict or str).
        ability_key: Ability registry key to look for.
        registries: Optional `GameRegistries` or plain components dict.

    Returns:
        Ability data dict, list of dicts, or None.
    """
    abilities = extract_abilities_from_component(comp, registries)
    data = abilities.get(ability_key)
    if isinstance(data, (dict, list)):
        return data
    return None
