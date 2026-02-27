"""Base class for table data sources.

A DataSource provides all the data needed to render a VirtualTable:
- Row count and cell values
- Column definitions (id, label, width, visibility)
- Optional: cell images and row highlight colors
"""

from typing import Any, Dict, List, Optional, Tuple

import pygame


class ITableDataSource:
    """Base class for table data sources.

    Subclasses must implement:
        - get_row_count() -> int
        - get_cell_value(row_index, column_id) -> str
        - get_columns() -> List[Dict[str, Any]]

    Optional overrides:
        - get_cell_image(row_index, column_id) -> Optional[pygame.Surface]
        - get_row_highlight(row_index) -> Optional[Tuple[int, int, int]]
    """

    def get_row_count(self) -> int:
        """Return the total number of rows.

        Returns:
            Number of data rows.

        Raises:
            NotImplementedError: Must be overridden by subclass.
        """
        raise NotImplementedError

    def get_cell_value(self, row_index: int, column_id: str) -> str:
        """Return the string value for a cell.

        Args:
            row_index: Zero-based row index.
            column_id: Column identifier string.

        Returns:
            String representation of the cell value.

        Raises:
            NotImplementedError: Must be overridden by subclass.
        """
        raise NotImplementedError

    def get_columns(self) -> List[Dict[str, Any]]:
        """Return all column definitions.

        Each column dict should have:
            - id: str - unique identifier
            - label: str - display name
            - width: int - pixel width
            - visible: bool - whether column is shown (default True)
            - type: str (optional) - 'image' for image columns

        Returns:
            List of column definition dicts.

        Raises:
            NotImplementedError: Must be overridden by subclass.
        """
        raise NotImplementedError

    def get_visible_columns(self) -> List[Dict[str, Any]]:
        """Return only visible column definitions.

        Filters columns by visible=True (defaults to True if key missing).

        Returns:
            List of visible column definition dicts.
        """
        return [c for c in self.get_columns() if c.get("visible", True)]

    def get_cell_image(
        self, row_index: int, column_id: str
    ) -> Optional[pygame.Surface]:
        """Return an image surface for an image-type cell.

        Override this for columns with type='image'.

        Args:
            row_index: Zero-based row index.
            column_id: Column identifier string.

        Returns:
            Pygame Surface to display, or None.
        """
        return None

    def get_row_highlight(
        self, row_index: int
    ) -> Optional[Tuple[int, int, int]]:
        """Return a custom highlight color for a row.

        Used for domain-specific highlighting (e.g., low morale ships).
        Selection highlighting is handled by VirtualTable.

        Args:
            row_index: Zero-based row index.

        Returns:
            RGB tuple for highlight color, or None for default.
        """
        return None
