"""Planet data source for VirtualTable.

PROJ-188 Phase 3: PlanetDataSource provides planet data for the planet list table.
Ports value extraction from planet_list_filters.get_column_value() and
icon caching from planet_list_renderer.VirtualListRenderer.
"""

from typing import Any, Dict, List, Optional

import pygame

from game.assets.asset_manager import get_default_asset_manager
from game.ui.components.table.data_source import ITableDataSource


class PlanetDataSource(ITableDataSource):
    """Data source providing planet data for VirtualTable.

    Handles:
    - Column definitions with func/attr/fmt extraction patterns
    - Icon caching with rotation support
    - Planet data list management
    """

    def __init__(
        self,
        columns: List[Dict[str, Any]],
        galaxy,
        empire,
    ) -> None:
        """Initialize with column definitions and context references.

        Args:
            columns: List of column definition dicts. Each may have:
                - id: str - unique identifier
                - width: int - pixel width
                - title: str - display name
                - visible: bool - whether column is shown
                - type: str (optional) - 'image' for image columns
                - attr: str (optional) - attribute path for value extraction
                - func: callable (optional) - function(planet) for value extraction
                - fmt: str (optional) - format string for numeric values
            galaxy: Galaxy object for context (owner lookup, etc.)
            empire: Current player's empire for context.
        """
        self._columns = columns
        self._galaxy = galaxy
        self._empire = empire
        self._planets: List = []
        self._icon_cache: Dict[str, pygame.Surface] = {}

    def get_row_count(self) -> int:
        """Return number of filtered planets."""
        return len(self._planets)

    def get_columns(self) -> List[Dict[str, Any]]:
        """Return column definitions."""
        return self._columns

    def get_cell_value(self, row_index: int, column_id: str) -> str:
        """Return string value for a cell.

        Args:
            row_index: Zero-based row index.
            column_id: Column identifier.

        Returns:
            String representation of cell value.
        """
        planet = self.get_planet_at_index(row_index)
        if planet is None:
            return ""

        # Find column definition
        col = self._get_column(column_id)
        if col is None:
            return ""

        return self._extract_value(planet, col)

    def get_cell_image(
        self, row_index: int, column_id: str
    ) -> Optional[pygame.Surface]:
        """Return image surface for image columns.

        Args:
            row_index: Zero-based row index.
            column_id: Column identifier.

        Returns:
            Pygame surface or None.
        """
        # Only handle icon column
        col = self._get_column(column_id)
        if col is None or col.get("type") != "image":
            return None

        planet = self.get_planet_at_index(row_index)
        if planet is None:
            return None

        return self._get_planet_icon(planet)

    def get_planet_at_index(self, row_index: int) -> Optional[Any]:
        """Get planet at given row index.

        Args:
            row_index: Zero-based row index.

        Returns:
            Planet object or None if out of bounds.
        """
        if 0 <= row_index < len(self._planets):
            return self._planets[row_index]
        return None

    def update_data(self, planets: List) -> None:
        """Update the planet data list.

        Args:
            planets: List of filtered planet objects.
        """
        self._planets = planets

    def _get_column(self, column_id: str) -> Optional[Dict[str, Any]]:
        """Get column definition by ID.

        Args:
            column_id: Column identifier.

        Returns:
            Column dict or None if not found.
        """
        for col in self._columns:
            if col["id"] == column_id:
                return col
        return None

    def _extract_value(self, planet, col: Dict[str, Any]) -> str:
        """Extract display value from planet for a column.

        Ported from planet_list_filters.get_column_value().

        Args:
            planet: Planet object.
            col: Column definition dict.

        Returns:
            String value for display.
        """
        # Function-based extraction
        if "func" in col:
            return str(col["func"](planet))

        # Attribute-based extraction with dotted path support
        if "attr" in col:
            attrs = col["attr"].split(".")
            obj = planet
            for a in attrs:
                if hasattr(obj, a):
                    obj = getattr(obj, a)
                else:
                    return "?"

            # Apply format string if present and value is numeric
            fmt = col.get("fmt")
            if fmt and isinstance(obj, (int, float)):
                return fmt.format(obj)
            return str(obj)

        return ""

    def _get_planet_icon(self, planet) -> pygame.Surface:
        """Get planet icon surface with caching.

        Ported from planet_list_renderer.VirtualListRenderer.

        Args:
            planet: Planet object.

        Returns:
            40x40 pygame Surface.
        """
        # Check for image_id
        if not planet.image_id:
            return self._get_blank_icon()

        # Build cache key with rotation
        rotation = planet.image_rotation or 0
        cache_key = f"icon_{planet.image_id}_{rotation}"

        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]

        # Load image from AssetManager
        am = get_default_asset_manager()
        img = am.load_planet_image(planet.image_id, requested_size=128)

        if img and img != am.get_missing_texture():
            # Apply rotation if specified
            if rotation and rotation != 0.0:
                img = pygame.transform.rotate(img, rotation)

            # Scale to 40x40 and cache
            scaled = pygame.transform.smoothscale(img, (40, 40))
            self._icon_cache[cache_key] = scaled
            return scaled

        # Fallback to blank icon
        return self._get_blank_icon()

    def _get_blank_icon(self) -> pygame.Surface:
        """Get blank fallback icon surface.

        Returns:
            40x40 blank pygame Surface.
        """
        if "_blank_icon" not in self._icon_cache:
            self._icon_cache["_blank_icon"] = pygame.Surface((40, 40))
        return self._icon_cache["_blank_icon"]
