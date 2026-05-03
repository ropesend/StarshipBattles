"""Planet list filtering logic.

This module contains the filtering and sorting logic for the planet list,
separated from the UI rendering code.

FEAT-25 — Effects filter semantics (tri-state)
==============================================
The Effects filter is per-effect tri-state using `FilterState` values:

    - `FilterState.YES`    → planet MUST have this effect
    - `FilterState.NO`     → planet MUST NOT have this effect
    - `FilterState.IGNORE` → this effect does not constrain the result

Multiple non-IGNORE effects compose as **AND**. The only no-op state is
"all effects IGNORE" (or empty dict). This replaces the FEAT-16 OR-within-
Effects contract end-to-end — there is no compatibility layer.

Tests in `test_planet_list_filters.py::TestEffectsPredicate` pin this
contract. Internally `filter_planets` is implemented as a predicate-list
pipeline so each category gates planets independently and new categories
compose without growing the function signature.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List
from game.core.constants import EARTH_MASS
from game.ui.filters.filter_state import FilterState
from game.ui.utils.formatters import format_compact_number
from game.strategy.services.system_effects_collector import make_group_key
from game.ui.screens.list_filter_utils import make_attr_sort_key


def gather_planets(galaxy, empire) -> Any:
    """Collect all planets from the galaxy with pre-computed filter values.

    Args:
        galaxy: The galaxy object containing systems and planets
        empire: The current player's empire for context

    Returns:
        List of planets with cached filter values attached
    """
    planets = []
    m_earth_const = EARTH_MASS
    g_const = 9.81

    if galaxy and galaxy.systems:
        for s in galaxy.systems.values():
            for p in s.planets:
                # Pre-compute expensive filter values (avoids per-filter-iteration cost)
                p._cached_gravity_g = p.surface_gravity / g_const
                p._cached_mass_earth = p.mass / m_earth_const
                p._cached_name_lower = p.name.lower()
                # Cache system name and location for display and navigation
                p._cached_system_name = s.name
                p._cached_system_global_location = s.global_location

                # Pre-compute type category
                # Use title case of the enum name (e.g. "Ice Giant", "Continental")
                p._cached_type_category = p.planet_type.name.title().replace('_', ' ')

                planets.append(p)
    return planets


# ---------------------------------------------------------------------------
# FEAT-16: Predicate-list pipeline. Each category contributes a predicate;
# `filter_planets` ANDs them. Public function signature preserved for
# backward-compat with existing call sites and tests; the predicate
# builders below are internal helpers.
# ---------------------------------------------------------------------------


def _name_predicate(search_lower: str) -> Callable[[Any], bool]:
    if not search_lower:
        return lambda p: True
    return lambda p: search_lower in p._cached_name_lower


def _type_predicate(filter_types: Dict[str, bool]) -> Callable[[Any], bool]:
    return lambda p: filter_types.get(p._cached_type_category, True)


def _owner_predicate(filter_owner: Dict[str, bool] | None, empire) -> Callable[[Any], bool]:
    if filter_owner is None:
        return lambda p: True
    empire_id = empire.id if empire else -1

    def predicate(p) -> bool:
        owner_id = p.owner_id
        if owner_id is None:
            owner_cat = 'Unowned'
        elif owner_id == empire_id:
            owner_cat = 'Player'
        else:
            owner_cat = 'Enemy'
        return filter_owner.get(owner_cat, True)

    return predicate


def _range_predicate(attr_name: str, min_v: float, max_v: float) -> Callable[[Any], bool]:
    return lambda p: min_v <= getattr(p, attr_name) <= max_v


def effects_predicate(filter_effects: Dict[str, FilterState] | None) -> Callable[[Any], bool]:
    """Predicate for the FEAT-25 tri-state Effects filter.

    - All-IGNORE (or empty): no-op, every planet passes.
    - For each non-IGNORE effect: AND. YES requires presence,
      NO requires absence.
    """
    if not filter_effects:
        return lambda p: True
    active = [(k, s) for k, s in filter_effects.items() if s is not FilterState.IGNORE]
    if not active:
        return lambda p: True

    def predicate(p) -> bool:
        abilities = getattr(p, 'intrinsic_abilities', None) or {}
        present = {make_group_key(name, data) for name, data in abilities.items()}
        for key, state in active:
            has = key in present
            if state is FilterState.YES and not has:
                return False
            if state is FilterState.NO and has:
                return False
        return True

    return predicate


def compute_planet_effect_keys(all_planets) -> List[str]:
    """Return sorted, de-duplicated list of effect group-keys present on any
    planet in the supplied list.

    FEAT-16: drives the Effects sidebar chips and per-effect column set.
    Group-keys are produced via `make_group_key` so EnvironmentalDamage is
    discriminated by `damage_type` (e.g. `EnvironmentalDamage:thermal`).
    """
    keys: set[str] = set()
    for p in all_planets:
        abilities = getattr(p, 'intrinsic_abilities', None) or {}
        for ability_name, ability_data in abilities.items():
            keys.add(make_group_key(ability_name, ability_data))
    return sorted(keys)


def filter_planets(
    planets,
    search_lower,
    filter_types,
    min_g, max_g,
    min_t, max_t,
    min_m, max_m,
    filter_owner=None,
    empire=None,
    *,
    filter_effects: Dict[str, FilterState] | None = None,
) -> Any:
    """Filter planets via the predicate-list pipeline.

    Args:
        planets: List of all planets with cached values.
        search_lower: Lowercase search string for name matching.
        filter_types: Dict of type -> bool for type filtering.
        min_g, max_g: Gravity range in g.
        min_t, max_t: Temperature range in K.
        min_m, max_m: Mass range in Earth masses.
        filter_owner: Dict of owner category -> bool (BUG-27).
        empire: Current player's empire for ownership categorization.
        filter_effects: Dict of effect group-key -> FilterState (FEAT-25).
            All-IGNORE or empty → no-op (see module docstring).

    Returns:
        List of filtered planets.
    """
    predicates: List[Callable[[Any], bool]] = [
        _name_predicate(search_lower),
        _type_predicate(filter_types),
        _owner_predicate(filter_owner, empire),
        _range_predicate('_cached_gravity_g', min_g, max_g),
        _range_predicate('surface_temperature', min_t, max_t),
        _range_predicate('_cached_mass_earth', min_m, max_m),
        effects_predicate(filter_effects),
    ]
    return [p for p in planets if all(pred(p) for pred in predicates)]


def sort_planets(planets, sort_column_id, sort_descending, columns) -> Any:
    """Sort planets by the specified column.

    Args:
        planets: List of planets to sort (modified in place)
        sort_column_id: ID of column to sort by, or None for no sort
        sort_descending: Whether to sort in descending order
        columns: List of column definitions for fallback sorting

    Returns:
        The sorted list (same reference as input)
    """
    if not sort_column_id:
        return planets

    col = next((c for c in columns if c['id'] == sort_column_id), None)
    if not col:
        return planets

    # Use cached values for known numeric columns
    if col['id'] == 'mass':
        planets.sort(key=lambda p: p.mass, reverse=sort_descending)
    elif col['id'] == 'grav':
        planets.sort(key=lambda p: p.surface_gravity, reverse=sort_descending)
    elif col['id'] == 'temp':
        planets.sort(key=lambda p: p.surface_temperature, reverse=sort_descending)
    elif col['id'] == 'name':
        planets.sort(key=lambda p: p._cached_name_lower, reverse=sort_descending)
    elif col['id'] == 'type':
        planets.sort(key=lambda p: p._cached_type_category, reverse=sort_descending)
    else:
        # Fallback for other columns — shared with star_list_filters via list_filter_utils.
        planets.sort(key=make_attr_sort_key(col), reverse=sort_descending)

    return planets


def get_column_value(planet, col) -> Any:
    """Get the display value for a planet in a given column.

    Args:
        planet: The planet to get value from
        col: Column definition dict

    Returns:
        String value for display
    """
    if 'func' in col:
        return col['func'](planet)
    elif 'attr' in col:
        attrs = col['attr'].split('.')
        obj = planet
        for a in attrs:
            if hasattr(obj, a):
                obj = getattr(obj, a)
            else:
                return "?"

        fmt = col.get('fmt')
        if fmt and isinstance(obj, (int, float)):
            return fmt.format(obj)
        return str(obj)
    return ""


def compute_planet_ranges(all_planets) -> Any:
    """Compute min/max ranges for filter sliders from actual planet data.

    Args:
        all_planets: List of all planets to compute ranges from

    Returns:
        Dict with 'gravity', 'temp', 'mass' keys, each containing (min, max) tuple
    """
    m_earth = EARTH_MASS

    # Default fallbacks if no planets exist
    ranges = {
        'gravity': (0.0, 10.0),
        'temp': (0, 2000),
        'mass': (0.0, 500.0)
    }

    if not all_planets:
        return ranges

    gravities = []
    temps = []
    masses = []

    for p in all_planets:
        # Gravity in g (Earth = 9.81 m/s^2)
        gravities.append(p.surface_gravity / 9.81)
        # Temperature in Kelvin
        temps.append(p.surface_temperature)
        # Mass in Earth masses
        masses.append(p.mass / m_earth)

    # Compute ranges with small padding
    if gravities:
        g_min, g_max = min(gravities), max(gravities)
        # Add 5% padding and round nicely
        g_range = g_max - g_min if g_max > g_min else 1.0
        ranges['gravity'] = (max(0.0, g_min - g_range * 0.05), g_max + g_range * 0.05)

    if temps:
        t_min, t_max = min(temps), max(temps)
        t_range = t_max - t_min if t_max > t_min else 100
        ranges['temp'] = (max(0, int(t_min - t_range * 0.05)), int(t_max + t_range * 0.05))

    if masses:
        m_min, m_max = min(masses), max(masses)
        m_range = m_max - m_min if m_max > m_min else 1.0
        ranges['mass'] = (max(0.0, m_min - m_range * 0.05), m_max + m_range * 0.05)

    return ranges


def get_system_name(planet) -> Any:
    """Get the system name for a planet.

    Uses cached system name attached during gather_planets().

    Args:
        planet: Planet object with _cached_system_name from gather_planets()

    Returns:
        System name string or "?" if not available
    """
    # PROJ-198 Phase 4: Use cached string directly instead of object reference
    return getattr(planet, '_cached_system_name', "?")


def get_owner_name(planet, empires, empire) -> Any:
    """Get the owner name for a planet, with proper empire lookup.

    PROJ-198 Phase 4: Changed signature from (planet, galaxy, empire) to (planet, empires, empire)
    since Galaxy does not have an 'empires' attribute - empires come from session.empires.

    Args:
        planet: Planet object
        empires: List of all Empire objects for name lookup
        empire: Current player's empire for context

    Returns:
        Owner name string with star indicator for player-owned planets
    """
    if planet.owner_id is None:
        return "— None —"

    # Look up empire name from empires list
    if empires:
        for emp in empires:
            if emp.id == planet.owner_id:
                # Add indicator if it's the player's empire
                if planet.owner_id == empire.id:
                    return f"★ {emp.name}"
                return emp.name

    # Fallback to simple labels (when empires list not available)
    if planet.owner_id == empire.id:
        return "★ Player"
    return "Enemy"


def get_mass_earth(planet) -> str:
    """Get the mass of a planet in Earth masses.

    Args:
        planet: Planet object with mass attribute

    Returns:
        Formatted string with mass in Earth masses
    """
    m_earth = EARTH_MASS
    return f"{planet.mass/m_earth:.2f}"


def get_resource_str(planet, resource_name) -> str:
    """Get formatted resource string for a planet.

    Args:
        planet: Planet object with resources dict
        resource_name: Name of the resource to get

    Returns:
        Formatted string like "100k (Q80)" or "-" if no resource
    """
    if resource_name in planet.deposits:
        resource = planet.deposits[resource_name]
        quantity = resource['quantity']
        quantity_str = format_compact_number(quantity)

        quality = resource['quality']
        return f"{quantity_str} (Q{quality:.1f})"
    return "-"
