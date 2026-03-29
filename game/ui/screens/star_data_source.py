"""Star data source for VirtualTable.

PROJ-231: StarDataSource provides star data for the star list table.
Mirrors PlanetDataSource (PROJ-188) for stars.
"""
from typing import Any, Dict, List, Optional

import pygame

from game.assets.asset_manager import AssetManager
from game.ui.components.table.data_source import ITableDataSource

# Icon size for table display
_ICON_SIZE = 40


class StarDataSource(ITableDataSource):
    """Data source providing star data for VirtualTable.

    Handles:
    - Column definitions with func/attr/fmt extraction patterns
    - Star icon rendering and caching
    - Star data list management
    """

    def __init__(self, columns: List[Dict[str, Any]]) -> None:
        self._columns = columns
        self._stars: List = []
        self._icon_cache: Dict[str, pygame.Surface] = {}

    def get_row_count(self) -> int:
        return len(self._stars)

    def get_columns(self) -> List[Dict[str, Any]]:
        return self._columns

    def get_cell_value(self, row_index: int, column_id: str) -> str:
        star = self.get_star_at_index(row_index)
        if star is None:
            return ""
        col = self._get_column(column_id)
        if col is None:
            return ""
        return self._extract_value(star, col)

    def get_cell_image(
        self, row_index: int, column_id: str
    ) -> Optional[pygame.Surface]:
        """Return star icon for image columns."""
        col = self._get_column(column_id)
        if col is None or col.get("type") != "image":
            return None

        star = self.get_star_at_index(row_index)
        if star is None:
            return None

        return self._get_star_icon(star)

    def get_star_at_index(self, row_index: int) -> Optional[Any]:
        if 0 <= row_index < len(self._stars):
            return self._stars[row_index]
        return None

    def update_data(self, stars: List) -> None:
        self._stars = stars

    def _get_column(self, column_id: str) -> Optional[Dict[str, Any]]:
        for col in self._columns:
            if col["id"] == column_id:
                return col
        return None

    def _extract_value(self, star, col: Dict[str, Any]) -> str:
        if "func" in col:
            return str(col["func"](star))
        if "attr" in col:
            attrs = col["attr"].split(".")
            obj = star
            for a in attrs:
                if hasattr(obj, a):
                    obj = getattr(obj, a)
                else:
                    return "?"
            fmt = col.get("fmt")
            if fmt and isinstance(obj, (int, float)):
                return fmt.format(obj)
            return str(obj)
        return ""

    def _get_star_icon(self, star) -> pygame.Surface:
        """Get star icon with caching. Uses star.image_id with fallback to colored circles.

        Args:
            star: Star object with image_id and color attributes.

        Returns:
            40x40 pygame Surface.
        """
        # Use image_id for per-variant caching when available
        image_id = getattr(star, 'image_id', '')
        if image_id:
            cache_key = f"star_{image_id}"
            if cache_key in self._icon_cache:
                return self._icon_cache[cache_key]

            am = AssetManager.instance()
            img = am.load_star_image(image_id, 128)
            if img and img != am.get_missing_texture():
                scaled = pygame.transform.smoothscale(img, (_ICON_SIZE, _ICON_SIZE))
                self._icon_cache[cache_key] = scaled
                return scaled

        # Fallback: colored circle
        cache_key = f"star_circle_{star.color[0]}_{star.color[1]}_{star.color[2]}"
        return self._make_circle_icon(star.color, cache_key)

    def _make_circle_icon(self, color: tuple, cache_key: str) -> pygame.Surface:
        """Create a colored circle icon as fallback."""
        surf = pygame.Surface((_ICON_SIZE, _ICON_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (_ICON_SIZE // 2, _ICON_SIZE // 2), _ICON_SIZE // 2 - 2)
        self._icon_cache[cache_key] = surf
        return surf
