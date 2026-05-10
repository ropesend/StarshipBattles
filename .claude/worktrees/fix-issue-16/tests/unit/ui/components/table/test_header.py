"""Tests for TableHeader component."""

import pytest
from unittest.mock import MagicMock, patch


class TestTableHeader:
    """Tests for the TableHeader class."""

    def _sample_columns(self):
        """Return sample column definitions for testing."""
        return [
            {"id": "name", "label": "Name", "width": 100, "visible": True},
            {"id": "status", "label": "Status", "width": 80, "visible": True},
            {"id": "icon", "label": "Icon", "width": 60, "visible": True},
        ]

    @pytest.fixture
    def mock_manager(self):
        """Create a mock pygame_gui manager."""
        return MagicMock()

    @pytest.fixture
    def mock_panel(self):
        """Create a mock UIPanel."""
        import pygame

        panel = MagicMock()
        panel.get_relative_rect.return_value = pygame.Rect(0, 0, 300, 400)
        return panel

    @pytest.fixture
    def column_manager(self):
        """Create a real TableColumnManager."""
        from game.ui.components.table.column_manager import TableColumnManager

        return TableColumnManager(self._sample_columns())

    @patch("game.ui.components.table.header.UIButton")
    def test_rebuild_creates_buttons_per_visible_column(
        self, mock_button_class, mock_panel, mock_manager, column_manager
    ):
        """rebuild should create 3 buttons per visible column."""
        from game.ui.components.table.header import TableHeader

        # Setup mock
        mock_button_class.return_value = MagicMock()

        header = TableHeader(mock_panel, mock_manager, column_manager)

        # 3 visible columns * 3 buttons each = 9 buttons
        # But first column has no left arrow, last has no right arrow
        # So: 2 for first + 3 for middle + 2 for last = 7 buttons
        assert mock_button_class.call_count == 7

    @patch("game.ui.components.table.header.UIButton")
    def test_sort_indicator_shows_on_sorted_column(
        self, mock_button_class, mock_panel, mock_manager, column_manager
    ):
        """Sort indicator should appear on sorted column."""
        from game.ui.components.table.header import TableHeader

        mock_button_instance = MagicMock()
        mock_button_class.return_value = mock_button_instance

        column_manager.set_sort("name")
        header = TableHeader(mock_panel, mock_manager, column_manager)

        # Find the call for the name column title button
        # The title button text should include ▲
        calls = mock_button_class.call_args_list
        name_title_call = None
        for call in calls:
            _, kwargs = call
            text = kwargs.get("text", "")
            if "Name" in text:
                name_title_call = call
                break

        assert name_title_call is not None
        _, kwargs = name_title_call
        assert "▲" in kwargs["text"]

    @patch("game.ui.components.table.header.UIButton")
    def test_sort_indicator_descending(
        self, mock_button_class, mock_panel, mock_manager, column_manager
    ):
        """Descending sort should show ▼."""
        from game.ui.components.table.header import TableHeader

        mock_button_instance = MagicMock()
        mock_button_class.return_value = mock_button_instance

        column_manager.set_sort("status")
        column_manager.set_sort("status")  # Toggle to descending
        header = TableHeader(mock_panel, mock_manager, column_manager)

        # Find the status column title
        calls = mock_button_class.call_args_list
        status_call = None
        for call in calls:
            _, kwargs = call
            text = kwargs.get("text", "")
            if "Status" in text:
                status_call = call
                break

        assert status_call is not None
        _, kwargs = status_call
        assert "▼" in kwargs["text"]

    @patch("game.ui.components.table.header.UIButton")
    def test_first_column_has_no_left_arrow(
        self, mock_button_class, mock_panel, mock_manager, column_manager
    ):
        """First visible column should not have left arrow button."""
        from game.ui.components.table.header import TableHeader

        mock_button_instance = MagicMock()
        mock_button_class.return_value = mock_button_instance

        header = TableHeader(mock_panel, mock_manager, column_manager)

        # Check that no left arrow exists at x=0
        calls = mock_button_class.call_args_list
        left_arrow_at_zero = None
        for call in calls:
            _, kwargs = call
            text = kwargs.get("text", "")
            rect = kwargs.get("relative_rect")
            if text == "<" and rect and rect.x == 0:
                left_arrow_at_zero = call
                break

        assert left_arrow_at_zero is None

    @patch("game.ui.components.table.header.UIButton")
    def test_last_column_has_no_right_arrow(
        self, mock_button_class, mock_panel, mock_manager, column_manager
    ):
        """Last visible column should not have right arrow button."""
        from game.ui.components.table.header import TableHeader

        mock_button_instance = MagicMock()
        mock_button_class.return_value = mock_button_instance

        header = TableHeader(mock_panel, mock_manager, column_manager)

        # The last column starts at x=180 (100+80), width 60
        # A right arrow would be at x=180+60-20=220
        # With 3 columns: name(100)+status(80)+icon(60)
        # icon's right arrow would be at 180+60-20=220
        calls = mock_button_class.call_args_list
        right_arrow_at_end = None
        for call in calls:
            _, kwargs = call
            text = kwargs.get("text", "")
            rect = kwargs.get("relative_rect")
            if text == ">" and rect and rect.x == 220:
                right_arrow_at_end = call
                break

        assert right_arrow_at_end is None

    @patch("game.ui.components.table.header.UIButton")
    def test_check_presses_no_press(
        self, mock_button_class, mock_panel, mock_manager, column_manager
    ):
        """check_presses returns None values when no button pressed."""
        from game.ui.components.table.header import TableHeader

        mock_button_instance = MagicMock()
        mock_button_instance.check_pressed.return_value = False
        mock_button_class.return_value = mock_button_instance

        header = TableHeader(mock_panel, mock_manager, column_manager)
        result = header.check_presses()

        assert result == {"swap_column": None, "sort_column": None}

    @patch("game.ui.components.table.header.UIButton")
    def test_kill_cleans_up_widgets(
        self, mock_button_class, mock_panel, mock_manager, column_manager
    ):
        """kill() should kill all header widgets."""
        from game.ui.components.table.header import TableHeader

        mock_button_instance = MagicMock()
        mock_button_class.return_value = mock_button_instance

        header = TableHeader(mock_panel, mock_manager, column_manager)
        header.kill()

        # All button instances should have kill() called
        assert mock_button_instance.kill.called

    @patch("game.ui.components.table.header.UIButton")
    def test_rebuild_clears_existing_widgets(
        self, mock_button_class, mock_panel, mock_manager, column_manager
    ):
        """rebuild() should clear existing widgets first."""
        from game.ui.components.table.header import TableHeader

        mock_button_instance = MagicMock()
        mock_button_class.return_value = mock_button_instance

        header = TableHeader(mock_panel, mock_manager, column_manager)
        initial_call_count = mock_button_class.call_count

        # Rebuild
        header.rebuild()

        # Old widgets should have been killed
        assert mock_button_instance.kill.called

    @patch("game.ui.components.table.header.UIButton")
    def test_arrow_button_width_is_20(
        self, mock_button_class, mock_panel, mock_manager, column_manager
    ):
        """Arrow buttons should be 20 pixels wide."""
        from game.ui.components.table.header import TableHeader

        mock_button_instance = MagicMock()
        mock_button_class.return_value = mock_button_instance

        header = TableHeader(mock_panel, mock_manager, column_manager)

        # Find arrow button calls
        calls = mock_button_class.call_args_list
        for call in calls:
            _, kwargs = call
            text = kwargs.get("text", "")
            rect = kwargs.get("relative_rect")
            if text in ("<", ">"):
                assert rect.width == 20

    @patch("game.ui.components.table.header.UIButton")
    def test_title_button_width_is_column_minus_40(
        self, mock_button_class, mock_panel, mock_manager, column_manager
    ):
        """Title buttons should be column width minus 40 (2 arrows)."""
        from game.ui.components.table.header import TableHeader

        mock_button_instance = MagicMock()
        mock_button_class.return_value = mock_button_instance

        header = TableHeader(mock_panel, mock_manager, column_manager)

        # Find title button for 'name' column (width 100 -> title 60)
        calls = mock_button_class.call_args_list
        for call in calls:
            _, kwargs = call
            text = kwargs.get("text", "")
            rect = kwargs.get("relative_rect")
            if "Name" in text:
                assert rect.width == 60  # 100 - 40
                break
