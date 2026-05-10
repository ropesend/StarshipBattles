"""Tests for ITableDataSource base class."""

from typing import List, Dict, Any, Optional
import pygame


class TestITableDataSource:
    """Test the ITableDataSource base class interface."""

    def test_get_cell_image_returns_none_by_default(self):
        """Optional get_cell_image should return None by default."""
        from game.ui.components.table.data_source import ITableDataSource

        source = ITableDataSource()
        assert source.get_cell_image(0, "icon") is None

    def test_get_row_highlight_returns_none_by_default(self):
        """Optional get_row_highlight should return None by default."""
        from game.ui.components.table.data_source import ITableDataSource

        source = ITableDataSource()
        assert source.get_row_highlight(0) is None

    def test_get_visible_columns_filters_by_visible_key(self):
        """get_visible_columns should filter columns by visible=True."""
        from game.ui.components.table.data_source import ITableDataSource

        class TestSource(ITableDataSource):
            def get_row_count(self) -> int:
                return 0

            def get_cell_value(self, row_index: int, column_id: str) -> str:
                return ""

            def get_columns(self) -> List[Dict[str, Any]]:
                return [
                    {"id": "name", "label": "Name", "width": 100, "visible": True},
                    {"id": "hidden", "label": "Hidden", "width": 50, "visible": False},
                    {"id": "status", "label": "Status", "width": 80},  # No 'visible' key, defaults to True
                ]

        source = TestSource()
        visible = source.get_visible_columns()

        assert len(visible) == 2
        assert visible[0]["id"] == "name"
        assert visible[1]["id"] == "status"

    def test_concrete_implementation_works(self):
        """Test with a mock subclass implementing required methods."""
        from game.ui.components.table.data_source import ITableDataSource

        class MockDataSource(ITableDataSource):
            def __init__(self, data: List[Dict[str, str]]):
                self._data = data
                self._columns = [
                    {"id": "name", "label": "Name", "width": 100, "visible": True},
                    {"id": "value", "label": "Value", "width": 80, "visible": True},
                ]

            def get_row_count(self) -> int:
                return len(self._data)

            def get_cell_value(self, row_index: int, column_id: str) -> str:
                if 0 <= row_index < len(self._data):
                    return self._data[row_index].get(column_id, "")
                return ""

            def get_columns(self) -> List[Dict[str, Any]]:
                return self._columns

        source = MockDataSource([
            {"name": "Alpha", "value": "100"},
            {"name": "Beta", "value": "200"},
        ])

        assert source.get_row_count() == 2
        assert source.get_cell_value(0, "name") == "Alpha"
        assert source.get_cell_value(1, "value") == "200"
        assert len(source.get_columns()) == 2
        assert len(source.get_visible_columns()) == 2

    def test_get_visible_columns_all_hidden(self):
        """get_visible_columns returns empty list when all columns hidden."""
        from game.ui.components.table.data_source import ITableDataSource

        class AllHiddenSource(ITableDataSource):
            def get_row_count(self) -> int:
                return 0

            def get_cell_value(self, row_index: int, column_id: str) -> str:
                return ""

            def get_columns(self) -> List[Dict[str, Any]]:
                return [
                    {"id": "a", "label": "A", "width": 50, "visible": False},
                    {"id": "b", "label": "B", "width": 50, "visible": False},
                ]

        source = AllHiddenSource()
        assert source.get_visible_columns() == []

    def test_get_visible_columns_all_visible(self):
        """get_visible_columns returns all columns when all visible."""
        from game.ui.components.table.data_source import ITableDataSource

        class AllVisibleSource(ITableDataSource):
            def get_row_count(self) -> int:
                return 0

            def get_cell_value(self, row_index: int, column_id: str) -> str:
                return ""

            def get_columns(self) -> List[Dict[str, Any]]:
                return [
                    {"id": "a", "label": "A", "width": 50, "visible": True},
                    {"id": "b", "label": "B", "width": 50, "visible": True},
                ]

        source = AllVisibleSource()
        visible = source.get_visible_columns()
        assert len(visible) == 2
