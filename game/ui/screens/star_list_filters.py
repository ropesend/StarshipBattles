"""Star list filtering and sorting logic.

This module contains the filtering and sorting logic for the star list,
separated from the UI rendering code. Mirrors planet_list_filters.py.

PROJ-231: Star List Panel.
"""
from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING

from game.core.profiling import profile_action
from game.ui.screens.list_filter_utils import make_attr_sort_key

if TYPE_CHECKING:
    from game.strategy.facade.slices._facade_state import FacadeSessionState


@profile_action("Panel: StarRegistry.gather_stars")
def gather_stars(
    galaxy,
    *,
    facade_state: "Optional[FacadeSessionState]" = None,
) -> Any:
    """Collect all stars from the galaxy with pre-computed filter values.

    Args:
        galaxy: The galaxy object containing systems and stars
        facade_state: PROJ-411 Phase 1. Optional reference to the session's
            ``FacadeSessionState``. When supplied, the resulting list is
            cached at ``facade_state.stars_cache_new`` for the rest of
            the turn and returned by identity on subsequent calls.
            Cleared by ``FacadeSessionState.invalidate_all()`` at each
            turn boundary. Engine-side or test callers may omit this
            kwarg and get the legacy uncached behaviour.

    Returns:
        List of stars with cached filter values attached
    """
    if facade_state is not None and facade_state.stars_cache_new is not None:
        return facade_state.stars_cache_new

    stars = []

    if not galaxy or not galaxy.systems:
        return stars

    for system in galaxy.systems.values():
        star_count = len(system.stars)
        planet_count = len(system.planets)

        for star in system.stars:
            star._cached_name_lower = star.name.lower()
            star._cached_type_category = star.star_type.name.replace('_', ' ').title()
            star._cached_system_name = system.name
            star._cached_system_global_location = system.global_location
            star._cached_planet_count = planet_count
            star._cached_companion_count = star_count - 1

            stars.append(star)

    if facade_state is not None:
        facade_state.stars_cache_new = stars
    return stars


def filter_stars(stars, search_lower, filter_types,
                 min_mass, max_mass, min_temp, max_temp,
                 min_lum, max_lum, min_age, max_age,
                 min_radius, max_radius) -> Any:
    """Filter stars based on search criteria.

    Args:
        stars: List of all stars with cached values
        search_lower: Lowercase search string for name matching
        filter_types: Dict of type -> bool for type filtering
        min_mass, max_mass: Mass range in solar masses
        min_temp, max_temp: Temperature range in Kelvin
        min_lum, max_lum: Luminosity range in solar luminosities
        min_age, max_age: Age range in years
        min_radius, max_radius: Radius range in hexes

    Returns:
        List of filtered stars
    """

    def matches_filter(s) -> bool:
        # Name (use cached lowercase)
        if search_lower and search_lower not in s._cached_name_lower:
            return False

        # Type (use cached category)
        if not filter_types.get(s._cached_type_category, True):
            return False

        # Mass range
        if s.mass < min_mass or s.mass > max_mass:
            return False

        # Temperature range
        if s.temperature < min_temp or s.temperature > max_temp:
            return False

        # Luminosity range
        if s.luminosity < min_lum or s.luminosity > max_lum:
            return False

        # Age range
        if s.age < min_age or s.age > max_age:
            return False

        # Radius range
        if s.radius_hexes < min_radius or s.radius_hexes > max_radius:
            return False

        return True

    return [s for s in stars if matches_filter(s)]


def sort_stars(stars, sort_column_id, sort_descending, columns) -> Any:
    """Sort stars by the specified column.

    Args:
        stars: List of stars to sort (modified in place)
        sort_column_id: ID of column to sort by, or None for no sort
        sort_descending: Whether to sort in descending order
        columns: List of column definitions for fallback sorting

    Returns:
        The sorted list (same reference as input)
    """
    if not sort_column_id:
        return stars

    col = next((c for c in columns if c['id'] == sort_column_id), None)
    if not col:
        return stars

    # Use direct attribute access for known numeric columns
    if col['id'] == 'mass':
        stars.sort(key=lambda s: s.mass, reverse=sort_descending)
    elif col['id'] == 'temp':
        stars.sort(key=lambda s: s.temperature, reverse=sort_descending)
    elif col['id'] == 'luminosity':
        stars.sort(key=lambda s: s.luminosity, reverse=sort_descending)
    elif col['id'] == 'age':
        stars.sort(key=lambda s: s.age, reverse=sort_descending)
    elif col['id'] == 'radius':
        stars.sort(key=lambda s: s.radius_hexes, reverse=sort_descending)
    elif col['id'] == 'name':
        stars.sort(key=lambda s: s._cached_name_lower, reverse=sort_descending)
    elif col['id'] == 'type':
        stars.sort(key=lambda s: s._cached_type_category, reverse=sort_descending)
    else:
        # Fallback for other columns — shared with planet_list_filters via list_filter_utils.
        stars.sort(key=make_attr_sort_key(col), reverse=sort_descending)

    return stars


@profile_action("Panel: StarRegistry.compute_ranges")
def compute_star_ranges(all_stars) -> Any:
    """Compute min/max ranges for filter sliders from actual star data.

    Args:
        all_stars: List of all stars to compute ranges from

    Returns:
        Dict with range keys, each containing (min, max) tuple
    """
    ranges = {
        'mass': (0.0, 100.0),
        'temperature': (0.0, 1000000.0),
        'luminosity': (0.0, 10000.0),
        'age': (0.0, 1.5e10),
        'radius_hexes': (1.0, 6.0),
    }

    if not all_stars:
        return ranges

    masses = [s.mass for s in all_stars]
    temps = [s.temperature for s in all_stars]
    lums = [s.luminosity for s in all_stars]
    ages = [s.age for s in all_stars]
    radii = [float(s.radius_hexes) for s in all_stars]

    def padded_range(values, min_floor=0.0) -> tuple:
        v_min, v_max = min(values), max(values)
        v_range = v_max - v_min if v_max > v_min else max(abs(v_min) * 0.1, 1.0)
        return (max(min_floor, v_min - v_range * 0.05), v_max + v_range * 0.05)

    ranges['mass'] = padded_range(masses)
    ranges['temperature'] = padded_range(temps)
    ranges['luminosity'] = padded_range(lums)
    ranges['age'] = padded_range(ages)
    ranges['radius_hexes'] = padded_range(radii, min_floor=1.0)

    return ranges


def get_system_name(star) -> Any:
    """Get the system name for a star.

    Uses cached system name attached during gather_stars().

    Args:
        star: Star object with _cached_system_name from gather_stars()

    Returns:
        System name string or "?" if not available
    """
    return getattr(star, '_cached_system_name', "?")


def get_star_type_display(star) -> Any:
    """Get human-readable display name for a star's type.

    Args:
        star: Star object

    Returns:
        Title-cased type name (e.g., "Main Sequence", "Red Giant")
    """
    return star.star_type.name.replace('_', ' ').title()
