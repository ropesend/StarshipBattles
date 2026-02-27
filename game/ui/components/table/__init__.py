"""Generic table components for list/grid displays.

This package provides reusable table components for building scrollable,
sortable lists with virtual scrolling support.

Components:
    VirtualTable: Main table component with virtual scrolling
    TableHeader: Column headers with sort/reorder buttons
    TableColumnManager: Column configuration and sort state
    ITableDataSource: Base class for table data providers
    ISelectionStrategy: Base class for selection behavior
    SingleSelect: Single row selection
    MultiSelect: Multiple row selection with Ctrl+click
    NoSelect: No selection allowed
"""

from game.ui.components.table.column_manager import TableColumnManager
from game.ui.components.table.data_source import ITableDataSource
from game.ui.components.table.header import TableHeader
from game.ui.components.table.selection import (
    ISelectionStrategy,
    MultiSelect,
    NoSelect,
    SingleSelect,
)
from game.ui.components.table.virtual_table import VirtualTable

__all__ = [
    "VirtualTable",
    "TableHeader",
    "TableColumnManager",
    "ITableDataSource",
    "ISelectionStrategy",
    "SingleSelect",
    "MultiSelect",
    "NoSelect",
]
