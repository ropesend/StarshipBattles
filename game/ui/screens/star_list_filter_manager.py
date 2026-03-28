"""Filter state management for the Star List Window.

Manages filter state for star type and range filters.
Mirrors PlanetListFilterManager (PROJ-220) for stars.

PROJ-231: Star List Panel.
"""
from __future__ import annotations

from typing import Any, Dict, List


# All 8 star type categories (display names matching StarType enum)
STAR_TYPES = [
    'Main Sequence', 'Red Giant', 'Blue Giant', 'White Dwarf',
    'Red Dwarf', 'Neutron Star', 'Black Hole', 'Brown Dwarf',
]

# Default range values (used when no stars exist)
DEFAULT_RANGES = {
    'mass': [0.0, 100.0],
    'temperature': [0.0, 1000000.0],
    'luminosity': [0.0, 10000.0],
    'age': [0.0, 1.5e10],
    'radius_hexes': [1.0, 6.0],
}


class StarListFilterManager:
    """Manages filter state for the Star List Window.

    Handles:
    - Star type multi-select (8 types, all True by default)
    - Range filters (mass, temperature, luminosity, age, radius_hexes)
    - Text search

    No Pygame imports — independently testable.
    """

    def __init__(self) -> None:
        # Multi-select type filters (all enabled by default)
        self.filter_types: Dict[str, bool] = {t: True for t in STAR_TYPES}

        # Range filters (min/max pairs)
        self.filter_ranges: Dict[str, List[float]] = {
            k: list(v) for k, v in DEFAULT_RANGES.items()
        }

        # Text search
        self.search_text: str = ""

    def toggle_type(self, type_name: str) -> bool:
        """Toggle a star type filter.

        Args:
            type_name: Star type to toggle.

        Returns:
            New state, or False if type not recognized.
        """
        if type_name not in self.filter_types:
            return False
        self.filter_types[type_name] = not self.filter_types[type_name]
        return self.filter_types[type_name]

    def set_all_types(self, enabled: bool) -> None:
        """Set all star type filters to the same state.

        Args:
            enabled: True to enable all, False to disable all.
        """
        for key in self.filter_types:
            self.filter_types[key] = enabled

    def get_filter_state(self) -> Dict[str, Any]:
        """Return complete filter state as a dict.

        Returns:
            Dict with 'types', 'search_text', 'ranges' keys.
        """
        return {
            'types': dict(self.filter_types),
            'search_text': self.search_text,
            'ranges': {k: list(v) for k, v in self.filter_ranges.items()},
        }
