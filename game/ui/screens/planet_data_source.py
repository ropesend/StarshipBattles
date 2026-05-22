"""Planet data source for VirtualTable.

PROJ-188 Phase 3: PlanetDataSource provides planet data for the planet list table.
Ports value extraction from planet_list_filters.get_column_value() and
icon caching from planet_list_renderer.VirtualListRenderer.

PROJ-319 (DUP-X-14): generic plumbing moved to `ListDataSource` base.
"""

from typing import Any, Dict, List, Optional

import pygame

from game.assets.asset_manager import get_default_asset_manager
from game.ui.screens.list_data_source_base import ListDataSource


class PlanetDataSource(ListDataSource):
    """Data source providing planet data for VirtualTable.

    Handles planet-specific icon rendering (with rotation support) on top of
    the generic plumbing in `ListDataSource`.
    """

    def __init__(
        self,
        columns: List[Dict[str, Any]],
        world,
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
            world: Scene.world live seam for context (PROJ-477; currently
                unused for traversal — owner lookup uses the columns' empires).
            empire: Current player's empire for context.
        """
        super().__init__(columns)
        self._world = world
        self._empire = empire

    # Backwards-compatible alias for callers that still use the planet-specific
    # name. The base class exposes `_entity_at` / `update_data(rows)`.
    def get_planet_at_index(self, row_index: int) -> Optional[Any]:
        """Get planet at given row index (alias for `_entity_at`)."""
        return self._entity_at(row_index)

    @property
    def _planets(self) -> List[Any]:
        """Planet list (alias for `_rows`, retained for legacy access)."""
        return self._rows

    def _render_icon(self, entity: Any) -> pygame.Surface:
        return self._get_planet_icon(entity)

    def _get_planet_icon(self, planet) -> pygame.Surface:
        """Get planet icon surface with caching.

        Ported from planet_list_renderer.VirtualListRenderer.

        Args:
            planet: Planet object.

        Returns:
            40x40 pygame Surface.
        """
        if not planet.image_id:
            return self._get_blank_icon()

        rotation = planet.image_rotation or 0
        cache_key = f"icon_{planet.image_id}_{rotation}"

        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]

        am = get_default_asset_manager()
        img = am.load_planet_image(planet.image_id, requested_size=128)

        if img and img != am.get_missing_texture():
            if rotation and rotation != 0.0:
                img = pygame.transform.rotate(img, rotation)
            scaled = pygame.transform.smoothscale(img, (40, 40))
            self._icon_cache[cache_key] = scaled
            return scaled

        return self._get_blank_icon()

    def _get_blank_icon(self) -> pygame.Surface:
        """Get blank fallback icon surface."""
        if "_blank_icon" not in self._icon_cache:
            self._icon_cache["_blank_icon"] = pygame.Surface((40, 40))
        return self._icon_cache["_blank_icon"]
