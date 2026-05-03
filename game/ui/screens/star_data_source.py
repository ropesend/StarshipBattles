"""Star data source for VirtualTable.

PROJ-231: StarDataSource provides star data for the star list table.
Mirrors PlanetDataSource (PROJ-188) for stars.

PROJ-319 (DUP-X-14): generic plumbing moved to `ListDataSource` base.
"""
from typing import Any, Dict, List, Optional

import pygame

from game.assets.asset_manager import get_default_asset_manager
from game.ui.screens.list_data_source_base import ListDataSource

# Icon size for table display
_ICON_SIZE = 40


class StarDataSource(ListDataSource):
    """Data source providing star data for VirtualTable.

    Handles star-specific icon rendering (image_id lookup with fallback to a
    colored circle) on top of the generic plumbing in `ListDataSource`.
    """

    def __init__(self, columns: List[Dict[str, Any]]) -> None:
        super().__init__(columns)

    def get_star_at_index(self, row_index: int) -> Optional[Any]:
        """Get star at given row index (alias for `_entity_at`)."""
        return self._entity_at(row_index)

    @property
    def _stars(self) -> List[Any]:
        """Star list (alias for `_rows`, retained for legacy access)."""
        return self._rows

    def _render_icon(self, entity: Any) -> pygame.Surface:
        return self._get_star_icon(entity)

    def _get_star_icon(self, star) -> pygame.Surface:
        """Get star icon with caching. Uses star.image_id with fallback to colored circles.

        Args:
            star: Star object with image_id and color attributes.

        Returns:
            40x40 pygame Surface.
        """
        image_id = getattr(star, 'image_id', '')
        if image_id:
            cache_key = f"star_{image_id}"
            if cache_key in self._icon_cache:
                return self._icon_cache[cache_key]

            am = get_default_asset_manager()
            img = am.load_star_image(image_id, 128)
            if img and img != am.get_missing_texture():
                scaled = pygame.transform.smoothscale(img, (_ICON_SIZE, _ICON_SIZE))
                self._icon_cache[cache_key] = scaled
                return scaled

        cache_key = f"star_circle_{star.color[0]}_{star.color[1]}_{star.color[2]}"
        return self._make_circle_icon(star.color, cache_key)

    def _make_circle_icon(self, color: tuple, cache_key: str) -> pygame.Surface:
        """Create a colored circle icon as fallback."""
        surf = pygame.Surface((_ICON_SIZE, _ICON_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (_ICON_SIZE // 2, _ICON_SIZE // 2), _ICON_SIZE // 2 - 2)
        self._icon_cache[cache_key] = surf
        return surf
