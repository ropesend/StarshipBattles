"""Shared base class for VirtualTable data sources.

Extracted in PROJ-319 (DUP-X-14) to remove the duplicated infrastructure
that previously lived in `PlanetDataSource` and `StarDataSource` (column
lookup, value extraction, icon caching, row-count plumbing).

Subclasses provide entity-specific icon rendering by overriding
`_render_icon`. The base class owns the column / row / value plumbing.
"""
from typing import Any, Dict, List, Optional

import pygame

from game.ui.components.table.data_source import ITableDataSource


class ListDataSource(ITableDataSource):
    """Generic VirtualTable data source.

    Subclasses must implement `_render_icon(entity)` to produce the cell
    image for image columns. The base class handles:
      - Column definition storage and lookup (`_get_column`).
      - Row data via `update_data(rows)` / `get_row_count()`.
      - Cell text extraction via `_extract_value(entity, col)` (function /
        attribute / format-string patterns).
      - Image cache shared between rendered icons.
    """

    def __init__(self, columns: List[Dict[str, Any]]) -> None:
        self._columns = columns
        self._rows: List[Any] = []
        self._icon_cache: Dict[str, pygame.Surface] = {}

    # --- ITableDataSource ---

    def get_row_count(self) -> int:
        return len(self._rows)

    def get_columns(self) -> List[Dict[str, Any]]:
        return self._columns

    def get_cell_value(self, row_index: int, column_id: str) -> str:
        entity = self._entity_at(row_index)
        if entity is None:
            return ""
        col = self._get_column(column_id)
        if col is None:
            return ""
        return self._extract_value(entity, col)

    def get_cell_image(
        self, row_index: int, column_id: str
    ) -> Optional[pygame.Surface]:
        col = self._get_column(column_id)
        if col is None or col.get("type") != "image":
            return None
        entity = self._entity_at(row_index)
        if entity is None:
            return None
        return self._render_icon(entity)

    def update_data(self, rows: List[Any]) -> None:
        self._rows = rows

    # --- Internals available to subclasses ---

    def _entity_at(self, row_index: int) -> Optional[Any]:
        if 0 <= row_index < len(self._rows):
            return self._rows[row_index]
        return None

    def _get_column(self, column_id: str) -> Optional[Dict[str, Any]]:
        for col in self._columns:
            if col["id"] == column_id:
                return col
        return None

    def _extract_value(self, entity: Any, col: Dict[str, Any]) -> str:
        if "func" in col:
            return str(col["func"](entity))
        if "attr" in col:
            attrs = col["attr"].split(".")
            obj: Any = entity
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

    # --- Hook for subclasses ---

    def _render_icon(self, entity: Any) -> Optional[pygame.Surface]:
        """Return the icon surface for an entity, or None.

        Default: no icon. Subclasses with image columns should override.
        """
        return None
