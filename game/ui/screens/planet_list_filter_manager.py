"""Filter state management for the Planet List Window.

Manages filter state for planet type, owner, range, and search filters.
Includes a FilterStateManager for future binary/tri-state filters.

Created as part of PROJ-220 Phase 5.
"""
from __future__ import annotations

from typing import Any, Dict, List

from game.ui.filters.filter_state import FilterState
from game.ui.filters.filter_state_manager import FilterStateManager


# All 11 planet type categories
PLANET_TYPES = [
    'Continental', 'Arid', 'Pelagic', 'Magma', 'Cryoplanet',
    'Barren', 'Jovian', 'Ice Giant', 'Chthonian', 'Ice Dwarf',
    'Planetoid',
]

# Owner categories
OWNER_CATEGORIES = ['Player', 'Enemy', 'Unowned']

# Default range values (used when no planets exist)
DEFAULT_RANGES = {
    'gravity': [0.0, 10.0],
    'temp': [0, 2000],
    'mass': [0.0, 500.0],
}


class PlanetListFilterManager:
    """Manages filter state for the Planet List Window.

    Handles:
    - Planet type multi-select (11 types, all True by default)
    - Owner category multi-select (3 categories, all True by default)
    - Range filters (gravity, temperature, mass)
    - Text search
    - FilterStateManager for future binary/tri-state filters

    No Pygame imports — independently testable.
    """

    def __init__(self) -> None:
        # Multi-select type filters (all enabled by default)
        self.filter_types: Dict[str, bool] = {t: True for t in PLANET_TYPES}

        # Multi-select owner filters (all enabled by default)
        self.filter_owner: Dict[str, bool] = {o: True for o in OWNER_CATEGORIES}

        # Range filters (min/max pairs)
        self.filter_ranges: Dict[str, List[float]] = {
            k: list(v) for k, v in DEFAULT_RANGES.items()
        }

        # Text search
        self.search_text: str = ""

        # Tri-state manager for future binary filters
        self._tri_state_mgr = FilterStateManager({})

    @property
    def tri_state_manager(self) -> FilterStateManager:
        """Access the tri-state FilterStateManager for future filters."""
        return self._tri_state_mgr

    def toggle_type(self, type_name: str) -> bool:
        """Toggle a planet type filter.

        Args:
            type_name: Planet type to toggle.

        Returns:
            New state, or False if type not recognized.
        """
        if type_name not in self.filter_types:
            return False
        self.filter_types[type_name] = not self.filter_types[type_name]
        return self.filter_types[type_name]

    def toggle_owner(self, owner_cat: str) -> bool:
        """Toggle an owner category filter.

        Args:
            owner_cat: Owner category to toggle.

        Returns:
            New state, or False if category not recognized.
        """
        if owner_cat not in self.filter_owner:
            return False
        self.filter_owner[owner_cat] = not self.filter_owner[owner_cat]
        return self.filter_owner[owner_cat]

    def set_all_types(self, enabled: bool) -> None:
        """Set all planet type filters to the same state.

        Args:
            enabled: True to enable all, False to disable all.
        """
        for key in self.filter_types:
            self.filter_types[key] = enabled

    def set_all_owners(self, enabled: bool) -> None:
        """Set all owner category filters to the same state.

        Args:
            enabled: True to enable all, False to disable all.
        """
        for key in self.filter_owner:
            self.filter_owner[key] = enabled

    def get_filter_state(self) -> Dict[str, Any]:
        """Return complete filter state as a dict.

        Returns:
            Dict with 'types', 'owner', 'search_text', 'ranges' keys.
        """
        return {
            'types': dict(self.filter_types),
            'owner': dict(self.filter_owner),
            'search_text': self.search_text,
            'ranges': {k: list(v) for k, v in self.filter_ranges.items()},
        }
