"""Star data source for VirtualTable.

PROJ-231: StarDataSource provides star data for the star list table.
Mirrors PlanetDataSource (PROJ-188) for stars.
"""
from typing import Any, Dict, List, Optional

from game.ui.components.table.data_source import ITableDataSource


class StarDataSource(ITableDataSource):
    """Data source providing star data for VirtualTable.

    Handles:
    - Column definitions with func/attr/fmt extraction patterns
    - Star data list management
    """

    def __init__(self, columns: List[Dict[str, Any]]) -> None:
        """Initialize with column definitions.

        Args:
            columns: List of column definition dicts. Each may have:
                - id: str - unique identifier
                - width: int - pixel width
                - title: str - display name
                - visible: bool - whether column is shown
                - attr: str (optional) - attribute path for value extraction
                - func: callable (optional) - function(star) for value extraction
                - fmt: str (optional) - format string for numeric values
        """
        self._columns = columns
        self._stars: List = []

    def get_row_count(self) -> int:
        """Return number of filtered stars."""
        return len(self._stars)

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
        star = self.get_star_at_index(row_index)
        if star is None:
            return ""

        col = self._get_column(column_id)
        if col is None:
            return ""

        return self._extract_value(star, col)

    def get_cell_image(
        self, row_index: int, column_id: str
    ) -> None:
        """Stars have no icon column. Always returns None."""
        return None

    def get_star_at_index(self, row_index: int) -> Optional[Any]:
        """Get star at given row index.

        Args:
            row_index: Zero-based row index.

        Returns:
            Star object or None if out of bounds.
        """
        if 0 <= row_index < len(self._stars):
            return self._stars[row_index]
        return None

    def update_data(self, stars: List) -> None:
        """Update the star data list.

        Args:
            stars: List of filtered star objects.
        """
        self._stars = stars

    def _get_column(self, column_id: str) -> Optional[Dict[str, Any]]:
        """Get column definition by ID."""
        for col in self._columns:
            if col["id"] == column_id:
                return col
        return None

    def _extract_value(self, star, col: Dict[str, Any]) -> str:
        """Extract display value from star for a column.

        Args:
            star: Star object.
            col: Column definition dict.

        Returns:
            String value for display.
        """
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
