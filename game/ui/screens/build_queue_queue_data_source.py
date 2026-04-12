"""Build queue data source for per-planet VirtualTable.

PROJ-221 Phase 3: Provides queue item data for the per-planet build queue
VirtualTable. Implements ITableDataSource with columns for order, item name,
turns remaining, per-turn spend, and remaining cost.
"""

from typing import Any, Dict, List, Optional

import pygame

from game.ui.components.table.data_source import ITableDataSource
from game.ui.screens.build_queue_helpers import calculate_queue_turn_spend

# Resource key to column ID mapping
_RESOURCE_RATE_COLUMNS = {
    "metals": "met_rate",
    "organics": "org_rate",
    "vapors": "vap_rate",
    "radioactives": "rad_rate",
    "exotics": "exo_rate",
}

_RESOURCE_REM_COLUMNS = {
    "metals": "met_rem",
    "organics": "org_rem",
    "vapors": "vap_rem",
    "radioactives": "rad_rem",
    "exotics": "exo_rem",
}

# Reverse mappings: column ID -> resource name
_RATE_COL_TO_RESOURCE = {v: k for k, v in _RESOURCE_RATE_COLUMNS.items()}
_REM_COL_TO_RESOURCE = {v: k for k, v in _RESOURCE_REM_COLUMNS.items()}

# Portrait size for queue items (pixels)
_PORTRAIT_SIZE = 40

BUILD_QUEUE_COLUMNS: List[Dict[str, Any]] = [
    {"id": "actions",  "title": "",      "width": 100,  "visible": True, "type": "actions"},
    {"id": "portrait", "title": "",      "width": 50,  "visible": True, "type": "image"},
    {"id": "item",     "title": "Item",  "width": 200, "visible": True},
    {"id": "turns",    "title": "Turns", "width": 60,  "visible": True},
    {"id": "met_rate", "title": "Met/t", "width": 65,  "visible": True},
    {"id": "org_rate", "title": "Org/t", "width": 65,  "visible": True},
    {"id": "vap_rate", "title": "Vap/t", "width": 65,  "visible": True},
    {"id": "rad_rate", "title": "Rad/t", "width": 65,  "visible": True},
    {"id": "exo_rate", "title": "Exo/t", "width": 65,  "visible": True},
    {"id": "met_rem",  "title": "Met",   "width": 65,  "visible": True},
    {"id": "org_rem",  "title": "Org",   "width": 65,  "visible": True},
    {"id": "vap_rem",  "title": "Vap",   "width": 65,  "visible": True},
    {"id": "rad_rem",  "title": "Rad",   "width": 65,  "visible": True},
    {"id": "exo_rem",  "title": "Exo",   "width": 65,  "visible": True},
]


def _format_int(value: float) -> str:
    """Format a number as an integer with comma separators, or '-' if zero."""
    rounded = int(round(value))
    if rounded == 0:
        return "-"
    return f"{rounded:,}"


class BuildQueueQueueDataSource(ITableDataSource):
    """Data source for per-planet build queue VirtualTable.

    Provides cell values for queue items including order position,
    item name, turns remaining, per-turn resource spend, and
    remaining resource cost.
    """

    def __init__(
        self,
        columns: List[Dict[str, Any]],
        portrait_loader,
        build_rate: Dict[str, float],
    ) -> None:
        """Initialize with column definitions and portrait loader.

        Args:
            columns: Column definition list (BUILD_QUEUE_COLUMNS).
            portrait_loader: BuildQueuePortraitLoader for item portraits.
            build_rate: Production rate per turn for each resource.
        """
        self._columns = columns
        self._portrait_loader = portrait_loader
        self._queue: List[Dict] = []
        self._build_rate = build_rate
        self._per_turn_cache: List[Dict[str, float]] = []

    def set_queue(self, queue: List[Dict], build_rate: Dict[str, float]) -> None:
        """Update the active queue and build rate.

        Pre-computes per-turn spend distribution across the entire queue
        so that production capacity is allocated sequentially (BUG-98).

        Args:
            queue: List of queue item dicts.
            build_rate: Updated production rate per turn.
        """
        self._queue = queue
        self._build_rate = build_rate
        self._per_turn_cache = calculate_queue_turn_spend(queue, build_rate)

    def get_row_count(self) -> int:
        """Return number of items in the active queue."""
        return len(self._queue)

    def get_columns(self) -> List[Dict[str, Any]]:
        """Return deep copy of column definitions."""
        return [dict(c) for c in self._columns]

    def get_cell_value(self, row_index: int, column_id: str) -> str:
        """Return formatted string value for a cell.

        Args:
            row_index: Zero-based row index.
            column_id: Column identifier.

        Returns:
            Formatted string for display.
        """
        if row_index < 0 or row_index >= len(self._queue):
            return ""

        item = self._queue[row_index]

        if column_id == "order":
            return str(row_index + 1)

        if column_id == "item":
            design_id = item.get("design_id", "Unknown")
            item_type = item.get("type", "ship")
            return f"{design_id} ({item_type})"

        if column_id == "turns":
            turns = item.get("turns_remaining", 0)
            if isinstance(turns, float) and turns != int(turns):
                return f"{turns:.1f}"
            return str(int(turns))

        # Per-turn spend columns (BUG-98: use pre-computed queue distribution)
        if column_id in _RATE_COL_TO_RESOURCE:
            resource = _RATE_COL_TO_RESOURCE[column_id]
            if row_index < len(self._per_turn_cache):
                return _format_int(self._per_turn_cache[row_index].get(resource, 0.0))
            return "-"

        # Remaining cost columns
        if column_id in _REM_COL_TO_RESOURCE:
            resource = _REM_COL_TO_RESOURCE[column_id]
            total = item.get("total_cost", {}).get(resource, 0.0)
            consumed = item.get("resources_consumed", {}).get(resource, 0.0)
            remaining = max(0.0, total - consumed)
            return _format_int(remaining)

        return ""

    def get_cell_image(
        self, row_index: int, column_id: str
    ) -> Optional[pygame.Surface]:
        """Return portrait image for the portrait column.

        Args:
            row_index: Zero-based row index.
            column_id: Column identifier.

        Returns:
            Pygame Surface for portrait column, None for others.
        """
        if column_id != "portrait":
            return None

        if row_index < 0 or row_index >= len(self._queue):
            return None

        item = self._queue[row_index]
        design_id = item.get("design_id", "")
        item_type = item.get("type", "ship")

        return self._portrait_loader.load_queue_item_portrait(
            design_id, item_type, _PORTRAIT_SIZE
        )
