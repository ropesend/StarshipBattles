"""
Planet naming utilities for system body generation.

Functions for converting numbers to Roman numerals and generating
planet/moon names following astronomical naming conventions.
"""
import string
from typing import List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.data.planet import Planet


# Roman numeral conversion values and symbols
_ROMAN_VALUES = [10, 9, 5, 4, 1]
_ROMAN_SYMBOLS = ["X", "IX", "V", "IV", "I"]


def to_roman(n: int) -> str:
    """
    Convert an integer to Roman numeral representation.

    Args:
        n: Integer to convert (1-39 supported)

    Returns:
        Roman numeral string (e.g., 1 -> "I", 4 -> "IV", 9 -> "IX")
    """
    roman_num = ''
    i = 0
    while n > 0:
        for _ in range(n // _ROMAN_VALUES[i]):
            roman_num += _ROMAN_SYMBOLS[i]
            n -= _ROMAN_VALUES[i]
        i += 1
    return roman_num


def assign_body_names(bodies: List['Planet'], system_name: str) -> None:
    """
    Assign names to planetary bodies based on distance and mass.

    Naming convention:
    - Primary bodies at each location get Roman numerals by distance (I, II, III...)
    - Secondary bodies (moons) get lowercase suffixes (a, b, c...)

    Args:
        bodies: List of Planet objects to name (modified in-place)
        system_name: Base name for the system (e.g., "Alpha Centauri")
    """
    # Group bodies by location
    bodies_by_loc: Dict = {}
    for b in bodies:
        if b.location not in bodies_by_loc:
            bodies_by_loc[b.location] = []
        bodies_by_loc[b.location].append(b)

    # Sort locations by distance from center
    sorted_locs = sorted(
        bodies_by_loc.keys(),
        key=lambda loc: max(abs(loc.q), abs(loc.r), abs(-loc.q - loc.r))
    )

    moon_suffixes = list(string.ascii_lowercase)
    planet_idx = 1

    for loc in sorted_locs:
        group = bodies_by_loc[loc]
        # Sort group by mass descending (largest is primary, others are moons)
        group.sort(key=lambda x: x.mass, reverse=True)

        roman = to_roman(planet_idx)
        base_name = f"{system_name} {roman}"

        # Primary body
        group[0].name = base_name

        # Moons/secondary bodies
        for i in range(1, len(group)):
            if i - 1 < len(moon_suffixes):
                suffix = moon_suffixes[i - 1]
            else:
                suffix = f"z{i - 1}"  # Fallback for extreme counts
            group[i].name = f"{base_name}{suffix}"

        planet_idx += 1
