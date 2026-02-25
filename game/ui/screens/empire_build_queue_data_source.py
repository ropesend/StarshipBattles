"""Build queue data source for VirtualTable.

PROJ-188 Phase 4: BuildQueueDataSource provides build queue data for the
empire build queue table. Wraps EmpireBuildQueueViewModel and delegates
value extraction to the viewmodel and formatter modules.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from game.ui.components.table.data_source import ITableDataSource
from game.ui.screens.empire_build_queue_formatter import (
    get_system_name,
    get_sector_text,
)

if TYPE_CHECKING:
    from game.ui.screens.empire_build_queue_viewmodel import EmpireBuildQueueViewModel
    from game.ui.screens.empire_build_queue_filter_manager import BuildQueueFilterManager
    from game.strategy.data.build_queue_source import BuildQueueSource


class BuildQueueDataSource(ITableDataSource):
    """Data source providing build queue data for VirtualTable.

    Wraps EmpireBuildQueueViewModel and provides cell values and column config.
    Delegates most value extraction to the viewmodel's get_column_value method,
    with special handling for system and sector columns that need galaxy reference.
    """

    def __init__(
        self,
        viewmodel: "EmpireBuildQueueViewModel",
        filter_mgr: "BuildQueueFilterManager",
        galaxy,
    ) -> None:
        """Initialize with viewmodel, filter manager, and galaxy.

        Args:
            viewmodel: EmpireBuildQueueViewModel for filtered source access.
            filter_mgr: BuildQueueFilterManager for column definitions.
            galaxy: Galaxy instance for system name lookups.
        """
        self._viewmodel = viewmodel
        self._filter_mgr = filter_mgr
        self._galaxy = galaxy

    def get_row_count(self) -> int:
        """Return number of filtered sources.

        Returns:
            Number of build queue sources after filtering.
        """
        return len(self._viewmodel.filtered_sources)

    def get_columns(self) -> List[Dict[str, Any]]:
        """Return column definitions (deep copy).

        Returns:
            List of column definition dicts.
        """
        return [dict(col) for col in self._filter_mgr.columns]

    def get_cell_value(self, row_index: int, column_id: str) -> str:
        """Return string value for a cell.

        Args:
            row_index: Zero-based row index.
            column_id: Column identifier.

        Returns:
            String representation of cell value.
        """
        source = self.get_source_at_index(row_index)
        if source is None:
            return ""

        return self._get_column_value(source, column_id)

    def get_source_at_index(self, row_index: int) -> Optional["BuildQueueSource"]:
        """Get build queue source at given row index.

        Args:
            row_index: Zero-based row index.

        Returns:
            BuildQueueSource or None if out of bounds.
        """
        sources = self._viewmodel.filtered_sources
        if 0 <= row_index < len(sources):
            return sources[row_index]
        return None

    def _get_column_value(self, source: "BuildQueueSource", col_id: str) -> str:
        """Get display value for a column.

        Handles system and sector columns specially (need galaxy reference),
        delegates all others to viewmodel.get_column_value().

        Args:
            source: Build queue source.
            col_id: Column identifier.

        Returns:
            String value to display.
        """
        # System and sector need galaxy reference
        if col_id == "system":
            return get_system_name(source, self._galaxy)

        if col_id == "sector":
            return get_sector_text(source)

        # Delegate everything else to ViewModel
        return self._viewmodel.get_column_value(source, col_id)
