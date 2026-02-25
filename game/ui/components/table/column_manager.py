"""Column management for table components.

Manages column definitions, visibility, ordering, and sort state.
"""

from typing import Any, Dict, List, Optional


class TableColumnManager:
    """Manages table column configuration and sort state.

    Handles:
    - Column visibility toggling
    - Column reordering
    - Sort column and direction tracking
    - Total width calculation
    - Image column detection
    """

    def __init__(self, columns: List[Dict[str, Any]]) -> None:
        """Initialize the column manager.

        Args:
            columns: List of column definitions. Each dict should have:
                - id: str - unique identifier
                - label: str - display name
                - width: int - pixel width
                - visible: bool - whether column is shown (default True)
                - type: str (optional) - 'image' for image columns
        """
        # Deep copy to prevent external mutation
        self._columns = [dict(c) for c in columns]
        self.sort_column_id: Optional[str] = None
        self.sort_descending: bool = False

    def get_columns(self) -> List[Dict[str, Any]]:
        """Return all column definitions.

        Returns:
            List of all column dicts (including hidden).
        """
        return self._columns

    def get_visible_columns(self) -> List[Dict[str, Any]]:
        """Return only visible column definitions.

        Returns:
            List of columns where visible=True.
        """
        return [c for c in self._columns if c.get("visible", True)]

    def get_column(self, column_id: str) -> Optional[Dict[str, Any]]:
        """Get a column by its ID.

        Args:
            column_id: The column identifier.

        Returns:
            Column dict or None if not found.
        """
        for col in self._columns:
            if col["id"] == column_id:
                return col
        return None

    def toggle_column(self, column_id: str) -> Optional[bool]:
        """Toggle column visibility.

        Args:
            column_id: The column identifier.

        Returns:
            New visible state, or None if column not found.
        """
        col = self.get_column(column_id)
        if col is None:
            return None
        col["visible"] = not col.get("visible", True)
        return col["visible"]

    def swap_column(self, column_id: str, direction: int) -> bool:
        """Swap column position with adjacent visible column.

        Args:
            column_id: The column identifier.
            direction: 1 to move right, -1 to move left.

        Returns:
            True if swap succeeded, False if at edge or column not found.
        """
        visible = self.get_visible_columns()
        visible_ids = [c["id"] for c in visible]

        if column_id not in visible_ids:
            return False

        idx = visible_ids.index(column_id)
        target_idx = idx + direction

        # Check bounds
        if target_idx < 0 or target_idx >= len(visible_ids):
            return False

        # Find actual positions in master list and swap
        col_a = self.get_column(column_id)
        col_b = self.get_column(visible_ids[target_idx])

        idx_a = self._columns.index(col_a)
        idx_b = self._columns.index(col_b)

        self._columns[idx_a], self._columns[idx_b] = (
            self._columns[idx_b],
            self._columns[idx_a],
        )
        return True

    def get_total_visible_width(self) -> int:
        """Calculate total width of visible columns.

        Returns:
            Sum of all visible column widths.
        """
        return sum(c.get("width", 0) for c in self.get_visible_columns())

    def is_image_column(self, column_id: str) -> bool:
        """Check if a column is an image column.

        Args:
            column_id: The column identifier.

        Returns:
            True if column type is 'image'.
        """
        col = self.get_column(column_id)
        if col is None:
            return False
        return col.get("type") == "image"

    def set_sort(self, column_id: str) -> None:
        """Set the sort column.

        If already sorting by this column, toggles direction.
        Otherwise, sets new column with ascending order.

        Args:
            column_id: The column identifier to sort by.
        """
        if self.sort_column_id == column_id:
            self.sort_descending = not self.sort_descending
        else:
            self.sort_column_id = column_id
            self.sort_descending = False
