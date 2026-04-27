"""Planet list filtering logic.

This module contains the filtering and sorting logic for the planet list,
separated from the UI rendering code.
"""
from __future__ import annotations

from typing import Any
from game.core.constants import EARTH_MASS
from game.ui.utils.formatters import format_compact_number


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


def filter_planets(planets, search_lower, filter_types, min_g, max_g, min_t, max_t, min_m, max_m, filter_owner=None, empire=None) -> Any:
    """Filter planets based on search criteria.

    Args:
        planets: List of all planets with cached values
        search_lower: Lowercase search string for name matching
        filter_types: Dict of type -> bool for type filtering
        min_g, max_g: Gravity range in g
        min_t, max_t: Temperature range in K
        min_m, max_m: Mass range in Earth masses
        filter_owner: Dict of owner category -> bool for owner filtering (BUG-27)
        empire: Current player's empire for determining ownership

    Returns:
        List of filtered planets
    """
    empire_id = empire.id if empire else -1

    def matches_filter(p) -> bool:
        # Name (use cached lowercase)
        if search_lower and search_lower not in p._cached_name_lower:
            return False

        # Type (use cached category)
        if not filter_types.get(p._cached_type_category, True):
            return False

        # Owner filtering (BUG-27)
        if filter_owner is not None:
            owner_id = p.owner_id

            if owner_id is None:
                owner_cat = 'Unowned'
            elif owner_id == empire_id:
                owner_cat = 'Player'
            else:
                owner_cat = 'Enemy'

            if not filter_owner.get(owner_cat, True):
                return False

        # Ranges (use cached gravity_g and mass_earth)
        if p._cached_gravity_g < min_g or p._cached_gravity_g > max_g:
            return False

        if p.surface_temperature < min_t or p.surface_temperature > max_t:
            return False

        if p._cached_mass_earth < min_m or p._cached_mass_earth > max_m:
            return False

        return True

    return [p for p in planets if matches_filter(p)]


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
        # Fallback for other columns
        def sort_key(p) -> Any:
            if 'func' in col:
                return col['func'](p)
            elif 'attr' in col:
                attrs = col['attr'].split('.')
                obj = p
                for a in attrs:
                    if hasattr(obj, a):
                        obj = getattr(obj, a)
                    else:
                        return ""
                return obj
            return ""
        planets.sort(key=sort_key, reverse=sort_descending)

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
