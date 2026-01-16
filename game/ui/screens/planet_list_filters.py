"""Planet list filtering logic.

This module contains the filtering and sorting logic for the planet list,
separated from the UI rendering code.
"""


def gather_planets(galaxy, empire):
    """Collect all planets from the galaxy with pre-computed filter values.

    Args:
        galaxy: The galaxy object containing systems and planets
        empire: The current player's empire for context

    Returns:
        List of planets with cached filter values attached
    """
    planets = []
    m_earth_const = 5.97e24
    g_const = 9.81

    if galaxy and galaxy.systems:
        for s in galaxy.systems.values():
            for p in s.planets:
                # Attach system ref for cached access
                p._temp_system_ref = s

                # Pre-compute expensive filter values (avoids per-filter-iteration cost)
                p._cached_gravity_g = p.surface_gravity / g_const
                p._cached_mass_earth = p.mass / m_earth_const
                p._cached_name_lower = p.name.lower()

                # Pre-compute type category
                tn = p.planet_type.name.lower()
                if 'gas' in tn:
                    p._cached_type_category = 'Gas'
                elif 'ice' in tn:
                    p._cached_type_category = 'Ice'
                elif 'desert' in tn or 'hot' in tn:
                    p._cached_type_category = 'Desert'
                elif 'moon' in tn:
                    p._cached_type_category = 'Moon'
                else:
                    p._cached_type_category = 'Terran'

                planets.append(p)
    return planets


def filter_planets(planets, search_lower, filter_types, min_g, max_g, min_t, max_t, min_m, max_m):
    """Filter planets based on search criteria.

    Args:
        planets: List of all planets with cached values
        search_lower: Lowercase search string for name matching
        filter_types: Dict of type -> bool for type filtering
        min_g, max_g: Gravity range in g
        min_t, max_t: Temperature range in K
        min_m, max_m: Mass range in Earth masses

    Returns:
        List of filtered planets
    """
    def matches_filter(p):
        # Name (use cached lowercase)
        if search_lower and search_lower not in p._cached_name_lower:
            return False

        # Type (use cached category)
        if not filter_types.get(p._cached_type_category, True):
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


def sort_planets(planets, sort_column_id, sort_descending, columns):
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
        def sort_key(p):
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


def get_column_value(planet, col):
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
