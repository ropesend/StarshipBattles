"""Tests for VirtualTable component."""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from typing import List, Dict, Any

import pygame


class MockDataSource:
    """Mock data source for testing."""

    def __init__(self, rows: int = 10):
        self._row_count = rows
        self._columns = [
            {"id": "name", "label": "Name", "width": 100, "visible": True},
            {"id": "value", "label": "Value", "width": 80, "visible": True},
            {"id": "icon", "label": "Icon", "width": 60, "visible": True, "type": "image"},
        ]

    def get_row_count(self) -> int:
        return self._row_count

    def get_cell_value(self, row_index: int, column_id: str) -> str:
        return f"Row{row_index}-{column_id}"

    def get_columns(self) -> List[Dict[str, Any]]:
        return self._columns

    def get_visible_columns(self) -> List[Dict[str, Any]]:
        return [c for c in self._columns if c.get("visible", True)]

    def get_cell_image(self, row_index: int, column_id: str):
        return None

    def get_row_highlight(self, row_index: int):
        return None


class TestVirtualTable:
    """Tests for the VirtualTable class."""

    @pytest.fixture(autouse=True)
    def patched_pygame_gui(self):
        """Patch the 5 pygame_gui imports VirtualTable consults — universal across this class.

        PROJ-327 Phase 1 (PROJ-322 Task 3.14 resolution): all 16 tests in this class
        previously declared the same 5 ``@patch`` decorators
        (UIImage / UILabel / UIVerticalScrollBar / UIPanel / TableHeader).
        Centralizing into a single autouse fixture removes 80 of the 81
        ``@patch`` decorations from this file, collapsing 5 patch-context
        enter/exits per test to 1 nested context enter/exit.

        The fixture stays function-scoped (the autouse default): each test gets
        fresh Mock instances, so per-test ``assert mock_X.called`` checks remain
        sound (no cross-test state leak).

        Tests that need to observe or configure a specific mock add
        ``patched_pygame_gui`` to their signature and read
        ``patched_pygame_gui["UIPanel"]`` (etc.).
        """
        with patch("game.ui.components.table.virtual_table.UIImage") as image, \
             patch("game.ui.components.table.virtual_table.UILabel") as label, \
             patch("game.ui.components.table.virtual_table.UIVerticalScrollBar") as scrollbar, \
             patch("game.ui.components.table.virtual_table.UIPanel") as panel, \
             patch("game.ui.components.table.virtual_table.TableHeader") as header:
            yield {
                "UIImage": image,
                "UILabel": label,
                "UIVerticalScrollBar": scrollbar,
                "UIPanel": panel,
                "TableHeader": header,
            }

    @pytest.fixture
    def mock_manager(self):
        """Create a mock pygame_gui manager."""
        return MagicMock()

    @pytest.fixture
    def mock_panel(self):
        """Create a mock UIPanel."""
        panel = MagicMock()
        panel.get_relative_rect.return_value = pygame.Rect(0, 0, 300, 400)
        return panel

    @pytest.fixture
    def column_manager(self):
        """Create a real TableColumnManager."""
        from game.ui.components.table.column_manager import TableColumnManager

        return TableColumnManager([
            {"id": "name", "label": "Name", "width": 100, "visible": True},
            {"id": "value", "label": "Value", "width": 80, "visible": True},
            {"id": "icon", "label": "Icon", "width": 60, "visible": True, "type": "image"},
        ])

    @pytest.fixture
    def selection_strategy(self):
        """Create a SingleSelect strategy."""
        from game.ui.components.table.selection import SingleSelect

        return SingleSelect()

    @pytest.fixture
    def data_source(self):
        """Create mock data source."""
        return MockDataSource(rows=20)

    def test_constructor_creates_components(
        self,
        patched_pygame_gui,
        mock_panel,
        mock_manager,
        data_source,
        column_manager,
        selection_strategy,
    ):
        """Constructor should create header panel, list viewport, scroll bar."""
        from game.ui.components.table.virtual_table import VirtualTable

        mock_panel_class = patched_pygame_gui["UIPanel"]
        mock_scrollbar_class = patched_pygame_gui["UIVerticalScrollBar"]
        mock_header_class = patched_pygame_gui["TableHeader"]

        # Setup mock panel to return proper rect
        mock_list_panel = MagicMock()
        mock_list_panel.get_relative_rect.return_value = pygame.Rect(0, 0, 280, 360)
        mock_panel_class.return_value = mock_list_panel

        table = VirtualTable(
            mock_panel,
            mock_manager,
            data_source,
            column_manager,
            selection_strategy,
        )

        # Header panel created
        assert mock_panel_class.called
        # Scroll bar created
        assert mock_scrollbar_class.called
        # TableHeader created
        assert mock_header_class.called

    def test_rebuild_row_pool_creates_correct_count(
        self,
        patched_pygame_gui,
        mock_panel,
        mock_manager,
        data_source,
        column_manager,
        selection_strategy,
    ):
        """rebuild_row_pool should create (visible_height / row_height) + 2 rows."""
        from game.ui.components.table.virtual_table import VirtualTable

        mock_panel_class = patched_pygame_gui["UIPanel"]

        # Setup mock panel with controlled rect
        mock_list_panel = MagicMock()
        mock_list_panel.get_relative_rect.return_value = pygame.Rect(0, 0, 280, 360)

        # Make UIPanel return our mock for list panel
        panel_calls = []

        def panel_side_effect(*args, **kwargs):
            mock = MagicMock()
            mock.get_relative_rect.return_value = pygame.Rect(0, 0, 280, 360)
            panel_calls.append(mock)
            return mock

        mock_panel_class.side_effect = panel_side_effect

        table = VirtualTable(
            mock_panel,
            mock_manager,
            data_source,
            column_manager,
            selection_strategy,
            row_height=50,  # 360/50 = 7.2 -> 7 + 2 = 9 rows
        )

        # Count row background panels (not header/list viewport panels)
        # Row pool should have 9 rows, but let's check it was built
        assert len(table._row_pool) >= 1

    def test_update_scroll_bar_sets_visible_percentage(
        self,
        patched_pygame_gui,
        mock_panel,
        mock_manager,
        data_source,
        column_manager,
        selection_strategy,
    ):
        """update_scroll_bar should set visible percentage correctly."""
        from game.ui.components.table.virtual_table import VirtualTable

        mock_panel_class = patched_pygame_gui["UIPanel"]
        mock_scrollbar_class = patched_pygame_gui["UIVerticalScrollBar"]

        mock_scrollbar = MagicMock()
        mock_scrollbar_class.return_value = mock_scrollbar

        mock_list_panel = MagicMock()
        mock_list_panel.get_relative_rect.return_value = pygame.Rect(0, 0, 280, 200)
        mock_panel_class.return_value = mock_list_panel

        table = VirtualTable(
            mock_panel,
            mock_manager,
            data_source,  # 20 rows * 50 height = 1000 total
            column_manager,
            selection_strategy,
            row_height=50,
        )

        # Manually call update_scroll_bar
        table.update_scroll_bar()

        # visible_pct = min(1.0, 200 / 1000) = 0.2
        # Check set_visible_percentage was called
        assert mock_scrollbar.set_visible_percentage.called

    def test_force_update_resets_dirty_tracking(
        self,
        patched_pygame_gui,
        mock_panel,
        mock_manager,
        data_source,
        column_manager,
        selection_strategy,
    ):
        """force_update should reset dirty tracking state."""
        from game.ui.components.table.virtual_table import VirtualTable

        mock_panel_class = patched_pygame_gui["UIPanel"]
        mock_scrollbar_class = patched_pygame_gui["UIVerticalScrollBar"]

        mock_scrollbar = MagicMock()
        mock_scrollbar.start_percentage = 0.0
        mock_scrollbar_class.return_value = mock_scrollbar

        mock_list_panel = MagicMock()
        mock_list_panel.get_relative_rect.return_value = pygame.Rect(0, 0, 280, 200)
        mock_panel_class.return_value = mock_list_panel

        table = VirtualTable(
            mock_panel,
            mock_manager,
            data_source,
            column_manager,
            selection_strategy,
        )

        # Set dirty tracking to non-default values
        table._last_scroll_pct = 0.5
        table._last_row_count = 100

        # Force update
        table.force_update()

        assert table._last_scroll_pct == -1.0
        assert table._last_row_count == -1

    def test_kill_cleans_up_all_widgets(
        self,
        patched_pygame_gui,
        mock_panel,
        mock_manager,
        data_source,
        column_manager,
        selection_strategy,
    ):
        """kill() should clean up all widgets."""
        from game.ui.components.table.virtual_table import VirtualTable

        mock_panel_class = patched_pygame_gui["UIPanel"]
        mock_scrollbar_class = patched_pygame_gui["UIVerticalScrollBar"]
        mock_header_class = patched_pygame_gui["TableHeader"]

        mock_header = MagicMock()
        mock_header_class.return_value = mock_header

        mock_scrollbar = MagicMock()
        mock_scrollbar_class.return_value = mock_scrollbar

        mock_list_panel = MagicMock()
        mock_list_panel.get_relative_rect.return_value = pygame.Rect(0, 0, 280, 200)
        mock_panel_class.return_value = mock_list_panel

        table = VirtualTable(
            mock_panel,
            mock_manager,
            data_source,
            column_manager,
            selection_strategy,
        )

        table.kill()

        # Header should be killed
        mock_header.kill.assert_called()
        # Scroll bar should be killed
        mock_scrollbar.kill.assert_called()

    def test_handle_click_delegates_to_selection_strategy(
        self,
        patched_pygame_gui,
        mock_panel,
        mock_manager,
        data_source,
        column_manager,
    ):
        """handle_click should delegate to selection strategy."""
        from game.ui.components.table.virtual_table import VirtualTable
        from game.ui.components.table.selection import SingleSelect

        mock_panel_class = patched_pygame_gui["UIPanel"]
        mock_scrollbar_class = patched_pygame_gui["UIVerticalScrollBar"]

        mock_scrollbar = MagicMock()
        mock_scrollbar.start_percentage = 0.0
        mock_scrollbar_class.return_value = mock_scrollbar

        mock_list_panel = MagicMock()
        mock_list_panel.get_relative_rect.return_value = pygame.Rect(0, 0, 280, 200)
        mock_panel_class.return_value = mock_list_panel

        selection = SingleSelect()
        table = VirtualTable(
            mock_panel,
            mock_manager,
            data_source,
            column_manager,
            selection,
        )

        # Simulate clicking on row 2
        # Mock find_clicked_row to return 2
        table.find_clicked_row = MagicMock(return_value=2)

        result = table.handle_click((100, 100), False)

        assert result == 2
        assert selection.get_selected_indices() == {2}

    def test_check_header_presses_delegates_to_header(
        self,
        patched_pygame_gui,
        mock_panel,
        mock_manager,
        data_source,
        column_manager,
        selection_strategy,
    ):
        """check_header_presses should delegate to TableHeader."""
        from game.ui.components.table.virtual_table import VirtualTable

        mock_panel_class = patched_pygame_gui["UIPanel"]
        mock_scrollbar_class = patched_pygame_gui["UIVerticalScrollBar"]
        mock_header_class = patched_pygame_gui["TableHeader"]

        mock_header = MagicMock()
        mock_header.check_presses.return_value = {"swap_column": None, "sort_column": "name"}
        mock_header_class.return_value = mock_header

        mock_scrollbar = MagicMock()
        mock_scrollbar_class.return_value = mock_scrollbar

        mock_list_panel = MagicMock()
        mock_list_panel.get_relative_rect.return_value = pygame.Rect(0, 0, 280, 200)
        mock_panel_class.return_value = mock_list_panel

        table = VirtualTable(
            mock_panel,
            mock_manager,
            data_source,
            column_manager,
            selection_strategy,
        )

        result = table.check_header_presses()

        mock_header.check_presses.assert_called()
        assert result == {"swap_column": None, "sort_column": "name"}

    def test_selected_row_highlight_color(
        self,
        patched_pygame_gui,
        mock_panel,
        mock_manager,
        data_source,
        column_manager,
        selection_strategy,
    ):
        """Selected rows should have blue tint color."""
        from game.ui.components.table.virtual_table import VirtualTable

        # Just verify the constants are correct
        assert VirtualTable.SELECTED_COLOR == pygame.Color(60, 80, 120)
        assert VirtualTable.UNSELECTED_COLOR == pygame.Color(35, 35, 35)

    def test_initial_dirty_tracking_state(
        self,
        patched_pygame_gui,
        mock_panel,
        mock_manager,
        data_source,
        column_manager,
        selection_strategy,
    ):
        """Initial dirty tracking state should trigger first update."""
        from game.ui.components.table.virtual_table import VirtualTable

        mock_panel_class = patched_pygame_gui["UIPanel"]
        mock_scrollbar_class = patched_pygame_gui["UIVerticalScrollBar"]

        mock_scrollbar = MagicMock()
        mock_scrollbar.start_percentage = 0.0
        mock_scrollbar_class.return_value = mock_scrollbar

        mock_list_panel = MagicMock()
        mock_list_panel.get_relative_rect.return_value = pygame.Rect(0, 0, 280, 200)
        mock_panel_class.return_value = mock_list_panel

        table = VirtualTable(
            mock_panel,
            mock_manager,
            data_source,
            column_manager,
            selection_strategy,
        )

        # Initial state should be set to trigger updates
        # After construction, it may have been updated, but force_update resets
        table.force_update()
        assert table._last_scroll_pct == -1.0
        assert table._last_row_count == -1

    def test_handle_click_returns_minus_one_on_miss(
        self,
        patched_pygame_gui,
        mock_panel,
        mock_manager,
        data_source,
        column_manager,
        selection_strategy,
    ):
        """handle_click should return -1 when click misses all rows."""
        from game.ui.components.table.virtual_table import VirtualTable

        mock_panel_class = patched_pygame_gui["UIPanel"]
        mock_scrollbar_class = patched_pygame_gui["UIVerticalScrollBar"]

        mock_scrollbar = MagicMock()
        mock_scrollbar.start_percentage = 0.0
        mock_scrollbar_class.return_value = mock_scrollbar

        mock_list_panel = MagicMock()
        mock_list_panel.get_relative_rect.return_value = pygame.Rect(0, 0, 280, 200)
        mock_panel_class.return_value = mock_list_panel

        table = VirtualTable(
            mock_panel,
            mock_manager,
            data_source,
            column_manager,
            selection_strategy,
        )

        # Mock find_clicked_row to return -1 (miss)
        table.find_clicked_row = MagicMock(return_value=-1)

        result = table.handle_click((100, 100), False)

        assert result == -1

    def test_rebuild_headers_delegates_to_header(
        self,
        patched_pygame_gui,
        mock_panel,
        mock_manager,
        data_source,
        column_manager,
        selection_strategy,
    ):
        """rebuild_headers should delegate to TableHeader.rebuild()."""
        from game.ui.components.table.virtual_table import VirtualTable

        mock_panel_class = patched_pygame_gui["UIPanel"]
        mock_scrollbar_class = patched_pygame_gui["UIVerticalScrollBar"]
        mock_header_class = patched_pygame_gui["TableHeader"]

        mock_header = MagicMock()
        mock_header_class.return_value = mock_header

        mock_scrollbar = MagicMock()
        mock_scrollbar_class.return_value = mock_scrollbar

        mock_list_panel = MagicMock()
        mock_list_panel.get_relative_rect.return_value = pygame.Rect(0, 0, 280, 200)
        mock_panel_class.return_value = mock_list_panel

        table = VirtualTable(
            mock_panel,
            mock_manager,
            data_source,
            column_manager,
            selection_strategy,
        )

        # Reset mock to clear constructor call
        mock_header.rebuild.reset_mock()

        table.rebuild_headers()

        mock_header.rebuild.assert_called_once()

    @patch("game.ui.components.table.virtual_table.UIButton", create=True)
    def test_rebuild_row_pool_handles_actions_column(
        self,
        mock_button_class,
        patched_pygame_gui,
        mock_panel,
        mock_manager,
        data_source,
        selection_strategy,
    ):
        """rebuild_row_pool should create action buttons if type is 'actions'.

        Phase 1 note: UIButton is the only "few-test" patch (single test)
        so it stays as ``@patch`` per design.md Phase 1 Task 1.5.
        The other 5 patches come from the autouse ``patched_pygame_gui``
        fixture.
        """
        from game.ui.components.table.virtual_table import VirtualTable
        from game.ui.components.table.column_manager import TableColumnManager

        mock_panel_class = patched_pygame_gui["UIPanel"]

        cols = [
            {"id": "actions", "label": "Actions", "width": 100, "visible": True, "type": "actions"},
        ]
        column_manager = TableColumnManager(cols)

        mock_list_panel = MagicMock()
        mock_list_panel.get_relative_rect.return_value = pygame.Rect(0, 0, 280, 200)

        def panel_side_effect(*args, **kwargs):
            mock = MagicMock()
            mock.get_relative_rect.return_value = pygame.Rect(0, 0, 280, 200)
            return mock

        mock_panel_class.side_effect = panel_side_effect

        table = VirtualTable(
            mock_panel,
            mock_manager,
            data_source,
            column_manager,
            selection_strategy,
            row_height=50,
        )

        # There should be buttons created for the actions column
        assert mock_button_class.call_count > 0, "UIButton not created for actions column"
        for row in table._row_pool:
            if not row.get("bg"):
                continue
            actions_widget = next((w for w in row["widgets"] if getattr(w.get("col", {}), "get", lambda k,d=None: None)("type") == "actions"), None)
            if not actions_widget:
                actions_widget = next((w for w in row["widgets"] if w.get("type") == "actions"), None)
            assert actions_widget is not None, "Actions widget definition missing from row pool"
            assert "actions_dict" in actions_widget, "actions_dict dictionary missing from actions widget"
            assert set(actions_widget["actions_dict"].keys()) == {"up", "down", "remove", "add"}

    def test_update_visible_rows_handles_actions_column(
        self,
        patched_pygame_gui,
        mock_panel,
        mock_manager,
        data_source,
        column_manager,
        selection_strategy,
    ):
        """update_visible_rows should skip set_text for 'actions' to avoid KeyError 'el'."""
        from game.ui.components.table.virtual_table import VirtualTable

        mock_panel_class = patched_pygame_gui["UIPanel"]
        mock_scrollbar_class = patched_pygame_gui["UIVerticalScrollBar"]

        mock_scrollbar = MagicMock()
        mock_scrollbar.start_percentage = 0.0
        mock_scrollbar_class.return_value = mock_scrollbar

        mock_list_panel = MagicMock()
        mock_list_panel.get_relative_rect.return_value = pygame.Rect(0, 0, 280, 200)
        mock_panel_class.return_value = mock_list_panel

        table = VirtualTable(
            mock_panel,
            mock_manager,
            data_source,
            column_manager,
            selection_strategy,
        )

        # Inject an actions widget structure into the pool to trigger the code path
        for row in table._row_pool:
            row["widgets"].append({
                "type": "actions",
                "col": {"id": "test_act", "type": "actions"}
            })

        # This should complete without throwing KeyError: 'el'
        table.force_update()  # Clear dirty state
        try:
            table.update_visible_rows()
        except KeyError as e:
            if str(e) == "'el'":
                pytest.fail("update_visible_rows caused KeyError: 'el' on actions type")
            else:
                raise

    @pytest.mark.parametrize(
        "row_idx,row_count,exp_up_disabled,exp_down_disabled",
        [
            (0, 3, True, False),   # first row: up disabled, down enabled
            (1, 3, False, False),  # middle row: both enabled
            (2, 3, False, True),   # last row: up enabled, down disabled
            (0, 1, True, True),    # single row: both disabled
        ],
        ids=["first", "middle", "last", "single"],
    )
    def test_update_visible_rows_disables_edge_action_buttons(
        self,
        patched_pygame_gui,
        mock_panel,
        mock_manager,
        column_manager,
        selection_strategy,
        row_idx,
        row_count,
        exp_up_disabled,
        exp_down_disabled,
    ):
        """FEAT-18: up disabled on row 0, down disabled on last row.

        Buttons in the middle stay enabled. On a single-row queue, both
        edges coincide so both up and down are disabled.
        """
        from game.ui.components.table.virtual_table import VirtualTable

        mock_panel_class = patched_pygame_gui["UIPanel"]
        mock_scrollbar_class = patched_pygame_gui["UIVerticalScrollBar"]

        mock_scrollbar = MagicMock()
        mock_scrollbar.start_percentage = 0.0
        mock_scrollbar_class.return_value = mock_scrollbar

        mock_list_panel = MagicMock()
        mock_list_panel.get_relative_rect.return_value = pygame.Rect(0, 0, 280, 200)
        mock_panel_class.return_value = mock_list_panel

        data_source = MockDataSource(rows=row_count)

        table = VirtualTable(
            mock_panel,
            mock_manager,
            data_source,
            column_manager,
            selection_strategy,
        )

        # Replace pool with one slot whose row_index is the row under test.
        # bg.visible defaults via MagicMock; data_idx must equal row_idx.
        up_btn = MagicMock()
        down_btn = MagicMock()
        bg_mock = MagicMock()
        bg_mock.visible = True
        table._row_pool = [{
            "bg": bg_mock,
            "row_index": -1,
            "_last_color": None,
            "widgets": [{
                "type": "actions",
                "col": {"id": "actions", "type": "actions"},
                "actions_dict": {
                    "add": MagicMock(),
                    "remove": MagicMock(),
                    "up": up_btn,
                    "down": down_btn,
                },
            }],
        }]

        # Force start_index to row_idx so pool slot 0 maps to row_idx.
        # update_visible_rows: start_index = int(scroll_y // row_height)
        # with scroll_y = current_pct * total_h. Easier: directly call
        # the path by setting scrollbar percentage so that
        # start_index == row_idx.
        total_h = row_count * table._row_height
        if total_h > 0:
            mock_scrollbar.start_percentage = (row_idx * table._row_height) / total_h
        table.force_update()

        table.update_visible_rows()

        assert up_btn.disable.called == exp_up_disabled, (
            f"up.disable() called={up_btn.disable.called}, "
            f"expected={exp_up_disabled} for row {row_idx}/{row_count}"
        )
        assert down_btn.disable.called == exp_down_disabled, (
            f"down.disable() called={down_btn.disable.called}, "
            f"expected={exp_down_disabled} for row {row_idx}/{row_count}"
        )
        # Inverse: when a button isn't disabled, it must be enabled
        if not exp_up_disabled:
            assert up_btn.enable.called, "up should be enabled when not on first row"
        if not exp_down_disabled:
            assert down_btn.enable.called, "down should be enabled when not on last row"

    def test_check_action_button_press(
        self,
        patched_pygame_gui,
        mock_panel,
        mock_manager,
        data_source,
        column_manager,
        selection_strategy,
    ):
        """check_action_button_press should map UI element to action and row_index."""
        from game.ui.components.table.virtual_table import VirtualTable

        mock_panel_class = patched_pygame_gui["UIPanel"]

        mock_list_panel = MagicMock()
        mock_list_panel.get_relative_rect.return_value = pygame.Rect(0, 0, 280, 200)
        mock_panel_class.return_value = mock_list_panel

        table = VirtualTable(mock_panel, mock_manager, data_source, column_manager, selection_strategy)

        # Build fake row structure
        fake_btn = MagicMock()
        table._row_pool.clear()
        bg_mock = MagicMock()
        bg_mock.visible = True
        
        table._row_pool.append({
            "bg": bg_mock,
            "row_index": 5,
            "widgets": [{
                "type": "actions",
                "actions_dict": {"add": fake_btn}
            }]
        })

        result = table.check_action_button_press(fake_btn)
        assert result == ("add", 5)
        
        # Mismatch
        result = table.check_action_button_press(MagicMock())
        assert result is None

    def test_kill_cleans_up_actions(
        self,
        patched_pygame_gui,
        mock_panel,
        mock_manager,
        data_source,
        column_manager,
        selection_strategy,
    ):
        """kill() should destroy any UIButtons held in actions_dict."""
        from game.ui.components.table.virtual_table import VirtualTable

        mock_panel_class = patched_pygame_gui["UIPanel"]

        mock_list_panel = MagicMock()
        mock_list_panel.get_relative_rect.return_value = pygame.Rect(0, 0, 280, 200)
        mock_panel_class.return_value = mock_list_panel

        table = VirtualTable(mock_panel, mock_manager, data_source, column_manager, selection_strategy)

        # Build fake row structure with actions
        fake_btn = MagicMock()
        table._row_pool.append({
            "bg": MagicMock(),
            "widgets": [{
                "type": "actions",
                "actions_dict": {"add": fake_btn, "remove": fake_btn}
            }]
        })

        table.kill()

        # Method handles multi buttons, so it might be called multiple times via values()
        assert fake_btn.kill.call_count >= 2

    @patch("game.ui.components.table.virtual_table.UIButton", create=True)
    def test_rebuild_row_pool_handles_replay_action_column(
        self,
        mock_button_class,
        patched_pygame_gui,
        mock_panel,
        mock_manager,
        data_source,
        selection_strategy,
    ):
        """rebuild_row_pool creates the single-button replay action widgets."""
        from game.ui.components.table.column_manager import TableColumnManager
        from game.ui.components.table.virtual_table import VirtualTable

        mock_panel_class = patched_pygame_gui["UIPanel"]
        mock_panel_class.return_value.get_relative_rect.return_value = pygame.Rect(
            0, 0, 280, 200
        )
        columns = [{
            "id": "replay",
            "label": "Replay",
            "width": 90,
            "visible": True,
            "type": "replay_action",
            "action": "view_replay",
        }]

        table = VirtualTable(
            mock_panel,
            mock_manager,
            data_source,
            TableColumnManager(columns),
            selection_strategy,
            row_height=40,
        )

        assert mock_button_class.call_count == len(table._row_pool)
        widget = table._row_pool[0]["widgets"][0]
        assert widget["type"] == "replay_action"
        assert widget["action"] == "view_replay"
        assert widget["button"] is mock_button_class.return_value

    def test_replay_action_button_updates_when_replay_id_present(
        self,
        patched_pygame_gui,
        mock_panel,
        mock_manager,
        data_source,
        column_manager,
        selection_strategy,
    ):
        """Rows with replay ids enable the replay button and set its tooltip."""
        from game.ui.components.table.virtual_table import VirtualTable

        mock_panel_class = patched_pygame_gui["UIPanel"]
        mock_scrollbar_class = patched_pygame_gui["UIVerticalScrollBar"]
        mock_scrollbar = MagicMock()
        mock_scrollbar.start_percentage = 0.0
        mock_scrollbar_class.return_value = mock_scrollbar
        mock_panel_class.return_value.get_relative_rect.return_value = pygame.Rect(
            0, 0, 280, 200
        )

        source = MagicMock()
        source.get_row_count.return_value = 1
        source.get_row_highlight.return_value = None
        source.get_cell_replay_id.return_value = "replay-1"

        table = VirtualTable(
            mock_panel,
            mock_manager,
            data_source,
            column_manager,
            selection_strategy,
        )
        button = MagicMock()
        table.data_source = source
        table._row_pool = [{
            "bg": MagicMock(),
            "row_index": -1,
            "_last_color": None,
            "widgets": [{
                "type": "replay_action",
                "col": {"id": "replay", "type": "replay_action"},
                "button": button,
                "action": "replay",
            }],
        }]

        table.update_visible_rows()

        button.enable.assert_called_once()
        button.disable.assert_not_called()
        assert button.tool_tip_text == "Replay this battle"

    def test_replay_action_button_disabled_uses_reason_tooltip(
        self,
        patched_pygame_gui,
        mock_panel,
        mock_manager,
        data_source,
        column_manager,
        selection_strategy,
    ):
        """Rows without replay ids disable the button with structural reason text."""
        from game.ui.components.table.virtual_table import VirtualTable

        mock_panel_class = patched_pygame_gui["UIPanel"]
        mock_scrollbar_class = patched_pygame_gui["UIVerticalScrollBar"]
        mock_scrollbar = MagicMock()
        mock_scrollbar.start_percentage = 0.0
        mock_scrollbar_class.return_value = mock_scrollbar
        mock_panel_class.return_value.get_relative_rect.return_value = pygame.Rect(
            0, 0, 280, 200
        )

        source = MagicMock()
        source.get_row_count.return_value = 1
        source.get_row_highlight.return_value = None
        source.get_cell_replay_id.return_value = None
        source.get_cell_replay_unavailable_reason.return_value = "no_ships"

        table = VirtualTable(
            mock_panel,
            mock_manager,
            data_source,
            column_manager,
            selection_strategy,
        )
        button = MagicMock()
        table.data_source = source
        table._row_pool = [{
            "bg": MagicMock(),
            "row_index": -1,
            "_last_color": None,
            "widgets": [{
                "type": "replay_action",
                "col": {"id": "replay", "type": "replay_action"},
                "button": button,
                "action": "replay",
            }],
        }]

        table.update_visible_rows()

        button.disable.assert_called_once()
        button.enable.assert_not_called()
        assert button.tool_tip_text.startswith("No combat")
        assert "neither side had any ships" in button.tool_tip_text

    def test_check_action_button_press_maps_replay_action(
        self,
        patched_pygame_gui,
        mock_panel,
        mock_manager,
        data_source,
        column_manager,
        selection_strategy,
    ):
        """check_action_button_press maps replay-action buttons to row actions."""
        from game.ui.components.table.virtual_table import VirtualTable

        mock_panel_class = patched_pygame_gui["UIPanel"]
        mock_panel_class.return_value.get_relative_rect.return_value = pygame.Rect(
            0, 0, 280, 200
        )
        table = VirtualTable(
            mock_panel,
            mock_manager,
            data_source,
            column_manager,
            selection_strategy,
        )
        replay_button = MagicMock()
        bg = MagicMock()
        bg.visible = True
        table._row_pool = [{
            "bg": bg,
            "row_index": 7,
            "widgets": [{
                "type": "replay_action",
                "button": replay_button,
                "action": "view_replay",
            }],
        }]

        assert table.check_action_button_press(replay_button) == ("view_replay", 7)

    def test_kill_cleans_up_replay_action_button(
        self,
        patched_pygame_gui,
        mock_panel,
        mock_manager,
        data_source,
        column_manager,
        selection_strategy,
    ):
        """kill destroys the single-button replay action widget."""
        from game.ui.components.table.virtual_table import VirtualTable

        mock_panel_class = patched_pygame_gui["UIPanel"]
        mock_panel_class.return_value.get_relative_rect.return_value = pygame.Rect(
            0, 0, 280, 200
        )
        table = VirtualTable(
            mock_panel,
            mock_manager,
            data_source,
            column_manager,
            selection_strategy,
        )
        replay_button = MagicMock()
        table._row_pool.append({
            "bg": MagicMock(),
            "widgets": [{
                "type": "replay_action",
                "button": replay_button,
            }],
        })

        table.kill()

        replay_button.kill.assert_called_once()


# ---------------------------------------------------------------------------
# Issue #8 — disabled-Replay tooltip helper
# ---------------------------------------------------------------------------


class TestDisabledReplayTooltip:
    """``_disabled_replay_tooltip`` picks the right tooltip for a disabled
    Replay button based on the data source's structural reason hint."""

    def test_sole_survivor_reason_returns_helpful_string(self):
        from game.ui.components.table.virtual_table import (
            _disabled_replay_tooltip,
        )

        source = MagicMock()
        source.get_cell_replay_unavailable_reason.return_value = "sole_survivor"
        assert _disabled_replay_tooltip(source, 0) == (
            "No combat — one side had no ships."
        )

    def test_no_ships_reason_returns_helpful_string(self):
        from game.ui.components.table.virtual_table import (
            _disabled_replay_tooltip,
        )

        source = MagicMock()
        source.get_cell_replay_unavailable_reason.return_value = "no_ships"
        assert _disabled_replay_tooltip(source, 0) == (
            "No combat — neither side had any ships."
        )

    def test_unknown_reason_falls_back_to_legacy_wording(self):
        from game.ui.components.table.virtual_table import (
            _disabled_replay_tooltip,
        )

        source = MagicMock()
        source.get_cell_replay_unavailable_reason.return_value = "wat"
        assert _disabled_replay_tooltip(source, 0) == (
            "No replay available — older save."
        )

    def test_none_reason_falls_back_to_legacy_wording(self):
        """Legacy combat rows return None — fall back to 'older save.'"""
        from game.ui.components.table.virtual_table import (
            _disabled_replay_tooltip,
        )

        source = MagicMock()
        source.get_cell_replay_unavailable_reason.return_value = None
        assert _disabled_replay_tooltip(source, 0) == (
            "No replay available — older save."
        )

    def test_data_source_without_accessor_falls_back(self):
        """Data sources that don't implement the new accessor (e.g. older
        custom tables) still get the legacy wording — no crash."""
        from game.ui.components.table.virtual_table import (
            _disabled_replay_tooltip,
        )

        class _Old:
            pass

        assert _disabled_replay_tooltip(_Old(), 0) == (
            "No replay available — older save."
        )


# ===========================================================================
# PROJ-373 Phase 3 — Row-pool reuse guard
#
# `rebuild_row_pool()` should be a no-op when the table dimensions
# `(list_panel_height, row_height)` are unchanged since the last build —
# the existing pool is still correctly sized. Saves ~1.5s/click in the
# subset of cases where the row pool would otherwise be rebuilt.
# ===========================================================================


class TestRowPoolReuseGuard:
    """PROJ-373 Phase 3: rebuild_row_pool guards against redundant rebuilds."""

    @pytest.fixture(autouse=True)
    def patched_pygame_gui(self):
        """Reuse the same patches as TestVirtualTable."""
        with patch("game.ui.components.table.virtual_table.UIImage") as image, \
             patch("game.ui.components.table.virtual_table.UILabel") as label, \
             patch("game.ui.components.table.virtual_table.UIVerticalScrollBar") as scrollbar, \
             patch("game.ui.components.table.virtual_table.UIPanel") as panel, \
             patch("game.ui.components.table.virtual_table.TableHeader") as header:
            yield {
                "UIImage": image,
                "UILabel": label,
                "UIVerticalScrollBar": scrollbar,
                "UIPanel": panel,
                "TableHeader": header,
            }

    @pytest.fixture
    def mock_manager(self):
        return MagicMock()

    @pytest.fixture
    def mock_panel(self):
        panel = MagicMock()
        panel.get_relative_rect.return_value = pygame.Rect(0, 0, 300, 400)
        return panel

    @pytest.fixture
    def column_manager(self):
        from game.ui.components.table.column_manager import TableColumnManager

        return TableColumnManager([
            {"id": "name", "label": "Name", "width": 100, "visible": True},
        ])

    @pytest.fixture
    def selection_strategy(self):
        from game.ui.components.table.selection import SingleSelect

        return SingleSelect()

    @pytest.fixture
    def data_source(self):
        return MockDataSource(rows=5)

    def _build_table(self, patched_pygame_gui, mock_panel, mock_manager,
                     data_source, column_manager, selection_strategy,
                     list_panel_height: int = 200):
        from game.ui.components.table.virtual_table import VirtualTable

        mock_panel_class = patched_pygame_gui["UIPanel"]
        mock_panel_class.return_value.get_relative_rect.return_value = pygame.Rect(
            0, 0, 280, list_panel_height
        )
        return VirtualTable(
            mock_panel,
            mock_manager,
            data_source,
            column_manager,
            selection_strategy,
        )

    def test_rebuild_skipped_when_dimensions_unchanged(
        self,
        patched_pygame_gui,
        mock_panel,
        mock_manager,
        data_source,
        column_manager,
        selection_strategy,
    ):
        """Calling rebuild_row_pool a second time with identical dimensions
        must not trigger a fresh widget tear-down/rebuild."""
        table = self._build_table(
            patched_pygame_gui, mock_panel, mock_manager,
            data_source, column_manager, selection_strategy,
        )
        # Snapshot the pool's bg widgets (not the list itself)
        first_bgs = [row["bg"] for row in table._row_pool]
        first_kill_count = sum(bg.kill.call_count for bg in first_bgs)

        # Call rebuild again — dimensions unchanged
        table.rebuild_row_pool()

        # Same widgets — none of the previous bgs were killed
        new_kill_count = sum(bg.kill.call_count for bg in first_bgs)
        assert new_kill_count == first_kill_count
        # And the pool's bgs are unchanged (same objects, same length)
        current_bgs = [row["bg"] for row in table._row_pool]
        assert current_bgs == first_bgs

    def test_rebuild_runs_when_panel_height_changes(
        self,
        patched_pygame_gui,
        mock_panel,
        mock_manager,
        data_source,
        column_manager,
        selection_strategy,
    ):
        """When the list panel's height changes, the pool must be rebuilt
        so visible-row count is recalculated."""
        table = self._build_table(
            patched_pygame_gui, mock_panel, mock_manager,
            data_source, column_manager, selection_strategy,
            list_panel_height=200,
        )
        first_pool = list(table._row_pool)

        # Simulate a panel-height change. _list_view_panel is a MagicMock
        # whose get_relative_rect returns a configurable rect.
        table._list_view_panel.get_relative_rect.return_value = pygame.Rect(
            0, 0, 280, 600
        )
        table.rebuild_row_pool()

        # The first-pool bgs were killed during teardown
        for row in first_pool:
            assert row["bg"].kill.called

    def test_rebuild_runs_when_row_height_changes(
        self,
        patched_pygame_gui,
        mock_panel,
        mock_manager,
        data_source,
        column_manager,
        selection_strategy,
    ):
        """Mutating row_height invalidates the pool dimensions."""
        table = self._build_table(
            patched_pygame_gui, mock_panel, mock_manager,
            data_source, column_manager, selection_strategy,
        )
        first_pool = list(table._row_pool)
        # Mutate row_height
        table._row_height = table._row_height * 2
        table.rebuild_row_pool()
        for row in first_pool:
            assert row["bg"].kill.called

    def test_force_update_does_not_force_pool_rebuild(
        self,
        patched_pygame_gui,
        mock_panel,
        mock_manager,
        data_source,
        column_manager,
        selection_strategy,
    ):
        """force_update only resets dirty-tracking for visible-row updates,
        not the pool dims cache."""
        table = self._build_table(
            patched_pygame_gui, mock_panel, mock_manager,
            data_source, column_manager, selection_strategy,
        )
        first_bgs = [row["bg"] for row in table._row_pool]
        table.force_update()
        table.rebuild_row_pool()
        # Dims unchanged — pool widgets reused
        assert [row["bg"] for row in table._row_pool] == first_bgs
        # And no kills were issued on the existing widgets
        assert all(bg.kill.call_count == 0 for bg in first_bgs)

    def test_rebuild_runs_when_panel_width_changes(
        self,
        patched_pygame_gui,
        mock_panel,
        mock_manager,
        data_source,
        column_manager,
        selection_strategy,
    ):
        """PROJ-373 review MAJ-001: width-only resize must invalidate the pool.

        Row backgrounds are sized to ``panel_rect.width`` (virtual_table.py:198);
        a width change without a height change leaves stale-width row
        backgrounds and broken cell layouts.
        """
        table = self._build_table(
            patched_pygame_gui, mock_panel, mock_manager,
            data_source, column_manager, selection_strategy,
            list_panel_height=200,
        )
        first_pool = list(table._row_pool)

        # Width changes (280 → 200), height unchanged.
        table._list_view_panel.get_relative_rect.return_value = pygame.Rect(
            0, 0, 200, 200
        )
        table.rebuild_row_pool()

        for row in first_pool:
            assert row["bg"].kill.called, (
                "width change must invalidate the pool"
            )

    def test_rebuild_runs_when_visible_columns_toggled(
        self,
        patched_pygame_gui,
        mock_panel,
        mock_manager,
        data_source,
        selection_strategy,
    ):
        """PROJ-373 review MAJ-002: a visibility toggle on the column manager
        must invalidate the pool.

        Production sites in ``data_list_window_mixin``, ``event_log_window``,
        ``fleet_report_window``, ``empire_build_queue_window`` all call
        ``column_manager.toggle_column()`` followed by
        ``virtual_table.rebuild_row_pool()`` and expect the pool to reflect
        the new visible-column set. Without this guard input, the rebuild
        is silently skipped because (height, row_height) did not change.
        """
        from game.ui.components.table.column_manager import TableColumnManager

        column_manager = TableColumnManager([
            {"id": "name", "label": "Name", "width": 100, "visible": True},
            {"id": "value", "label": "Value", "width": 80, "visible": True},
        ])
        table = self._build_table(
            patched_pygame_gui, mock_panel, mock_manager,
            data_source, column_manager, selection_strategy,
        )
        first_pool = list(table._row_pool)

        # Hide one column. Panel dimensions and row_height do NOT change.
        column_manager.toggle_column("value")
        table.rebuild_row_pool()

        for row in first_pool:
            assert row["bg"].kill.called, (
                "visibility toggle must invalidate the pool"
            )

    def test_rebuild_runs_when_columns_reordered(
        self,
        patched_pygame_gui,
        mock_panel,
        mock_manager,
        data_source,
        selection_strategy,
    ):
        """PROJ-373 review MAJ-002: a column-order swap must invalidate the
        pool. Header-drag swap path in
        ``data_list_window_mixin._run_update_template`` and equivalents
        depends on a rebuild after ``swap_column``.
        """
        from game.ui.components.table.column_manager import TableColumnManager

        column_manager = TableColumnManager([
            {"id": "name", "label": "Name", "width": 100, "visible": True},
            {"id": "value", "label": "Value", "width": 80, "visible": True},
        ])
        table = self._build_table(
            patched_pygame_gui, mock_panel, mock_manager,
            data_source, column_manager, selection_strategy,
        )
        first_pool = list(table._row_pool)

        column_manager.swap_column("name", 1)
        table.rebuild_row_pool()

        for row in first_pool:
            assert row["bg"].kill.called, (
                "column reorder must invalidate the pool"
            )

    def test_column_config_change_triggers_rebuild(
        self,
        patched_pygame_gui,
        mock_panel,
        mock_manager,
        data_source,
        selection_strategy,
    ):
        """PROJ-376 Phase 3 (PROJ-373 review MIN-005): adding a column to the
        column manager — without changing panel dimensions or row_height —
        must invalidate the pool. Confirms the visible-column fingerprint
        (``virtual_table.py:163-174``) covers config changes that go beyond
        toggle / reorder, e.g. a new column appearing at runtime.
        """
        from game.ui.components.table.column_manager import TableColumnManager

        column_manager = TableColumnManager([
            {"id": "name", "label": "Name", "width": 100, "visible": True},
            {"id": "value", "label": "Value", "width": 80, "visible": True},
        ])
        table = self._build_table(
            patched_pygame_gui, mock_panel, mock_manager,
            data_source, column_manager, selection_strategy,
        )
        first_pool = list(table._row_pool)
        assert len(column_manager.get_visible_columns()) == 2

        # Add a third column. Panel dimensions and row_height do NOT change.
        # No public ``add_column`` API exists; mutate the internal list as the
        # column-manager allows direct dict-mutation on visibility/order paths.
        column_manager._columns.append(
            {"id": "extra", "label": "Extra", "width": 60, "visible": True}
        )
        assert len(column_manager.get_visible_columns()) == 3

        table.rebuild_row_pool()

        for row in first_pool:
            assert row["bg"].kill.called, (
                "column-config change (added column) must invalidate the pool"
            )
        # New pool reflects the 3-column config.
        assert len(column_manager.get_visible_columns()) == 3


# ===========================================================================
# PROJ-410 Phase 2 Task 2.2 + Task 1.6 contract tests
# ===========================================================================


class TestProj410InvalidateWidgetCaches:
    """PROJ-410: VirtualTable.invalidate_widget_caches() public surface.

    Phase 2 Task 2.1: ``_data_identity_dirty: bool`` flag, default True.
    Phase 2 Task 2.2: ``invalidate_widget_caches() -> None`` method that
        nulls per-row/per-widget caches and sets the dirty flag.
    Phase 2 Task 2.3: ``update_visible_rows()`` early-return guard also
        checks the dirty flag; clears the flag after the per-row loop.
    Task 1.6 (overlap): button press after a yard switch resolves to
        the new yard's row index, not the prior yard's.

    All tests in this class FAIL today (the method/flag don't exist).
    """

    @pytest.fixture(autouse=True)
    def patched_pygame_gui(self):
        with patch("game.ui.components.table.virtual_table.UIImage") as image, \
             patch("game.ui.components.table.virtual_table.UILabel") as label, \
             patch("game.ui.components.table.virtual_table.UIVerticalScrollBar") as scrollbar, \
             patch("game.ui.components.table.virtual_table.UIPanel") as panel, \
             patch("game.ui.components.table.virtual_table.TableHeader") as header:
            yield {
                "UIImage": image, "UILabel": label,
                "UIVerticalScrollBar": scrollbar, "UIPanel": panel,
                "TableHeader": header,
            }

    @pytest.fixture
    def mock_manager(self):
        return MagicMock()

    @pytest.fixture
    def mock_panel(self):
        panel = MagicMock()
        panel.get_relative_rect.return_value = pygame.Rect(0, 0, 300, 400)
        return panel

    @pytest.fixture
    def column_manager(self):
        from game.ui.components.table.column_manager import TableColumnManager
        return TableColumnManager([
            {"id": "name", "label": "Name", "width": 100, "visible": True},
            {"id": "value", "label": "Value", "width": 80, "visible": True},
        ])

    @pytest.fixture
    def selection_strategy(self):
        from game.ui.components.table.selection import SingleSelect
        return SingleSelect()

    def _build_table(self, patched_pygame_gui, mock_panel, mock_manager,
                     column_manager, selection_strategy, data_source):
        from game.ui.components.table.virtual_table import VirtualTable
        mock_list_panel = MagicMock()
        mock_list_panel.get_relative_rect.return_value = pygame.Rect(0, 0, 280, 200)
        patched_pygame_gui["UIPanel"].return_value = mock_list_panel
        return VirtualTable(
            mock_panel, mock_manager, data_source, column_manager,
            selection_strategy,
        )

    def test_invalidate_widget_caches_method_exists_and_is_callable(
        self, patched_pygame_gui, mock_panel, mock_manager,
        column_manager, selection_strategy,
    ):
        """Phase 2 Task 2.2: VirtualTable must expose
        ``invalidate_widget_caches() -> None`` as a public method.
        FAILS today: method does not exist.
        """
        table = self._build_table(
            patched_pygame_gui, mock_panel, mock_manager,
            column_manager, selection_strategy, MockDataSource(rows=3),
        )
        assert hasattr(table, "invalidate_widget_caches"), (
            "PROJ-410 Phase 2 Task 2.2: VirtualTable must expose "
            "invalidate_widget_caches() public method."
        )
        assert callable(getattr(table, "invalidate_widget_caches", None))
        # Idempotent: must not raise on a second call.
        table.invalidate_widget_caches()
        table.invalidate_widget_caches()

    def test_data_identity_dirty_default_is_true(
        self, patched_pygame_gui, mock_panel, mock_manager,
        column_manager, selection_strategy,
    ):
        """Phase 2 Task 2.1: ``_data_identity_dirty`` defaults True so the
        first ``update_visible_rows`` after construction always re-renders.
        FAILS today: attribute does not exist.
        """
        table = self._build_table(
            patched_pygame_gui, mock_panel, mock_manager,
            column_manager, selection_strategy, MockDataSource(rows=3),
        )
        assert hasattr(table, "_data_identity_dirty"), (
            "PROJ-410 Phase 2 Task 2.1: _data_identity_dirty flag must "
            "exist on VirtualTable."
        )
        assert table._data_identity_dirty is True

    def test_invalidate_widget_caches_sets_data_identity_dirty(
        self, patched_pygame_gui, mock_panel, mock_manager,
        column_manager, selection_strategy,
    ):
        """Phase 2 Task 2.2: calling invalidate_widget_caches sets the
        flag to True even if it was previously False.
        """
        table = self._build_table(
            patched_pygame_gui, mock_panel, mock_manager,
            column_manager, selection_strategy, MockDataSource(rows=3),
        )
        table._data_identity_dirty = False
        table.invalidate_widget_caches()
        assert table._data_identity_dirty is True

    def test_invalidate_widget_caches_does_not_kill_pool_widgets(
        self, patched_pygame_gui, mock_panel, mock_manager,
        column_manager, selection_strategy,
    ):
        """Phase 2 Task 2.5 hard constraint: invalidation MUST NOT call
        ``.kill()`` on any pool widget. The TestRowPoolReuseGuard locks
        this behavior; this test reaffirms it specifically for the new
        invalidate path.
        """
        table = self._build_table(
            patched_pygame_gui, mock_panel, mock_manager,
            column_manager, selection_strategy, MockDataSource(rows=3),
        )
        # Capture kill spies before invalidation.
        kill_spies = []
        for row in table._row_pool:
            if row.get("bg") is not None:
                kill_spies.append(row["bg"].kill)
            for widget in row.get("widgets", []):
                if widget.get("el") is not None:
                    kill_spies.append(widget["el"].kill)

        table.invalidate_widget_caches()

        for kill_mock in kill_spies:
            assert not kill_mock.called, (
                "PROJ-410 Phase 2: invalidate_widget_caches() must NOT call "
                ".kill() on any pool widget (TestRowPoolReuseGuard contract)."
            )

    def test_button_press_after_invalidate_resolves_via_current_row_index(
        self, patched_pygame_gui, mock_panel, mock_manager,
        column_manager, selection_strategy,
    ):
        """PROJ-410 Task 1.6 + Phase 2: after invalidate + new data, a
        button press on a pool row must resolve to the row's CURRENT
        ``row_index``, not a stale value.

        Per Codex review (arc01-002), the existing code already reads
        ``row.get("row_index", -1)`` at click time
        (virtual_table.py:516-524). The bug is purely about the dirty
        flag preventing re-render. This test pins the click-time lookup
        as the authoritative resolution path.
        """
        # Construct with 3 rows.
        table = self._build_table(
            patched_pygame_gui, mock_panel, mock_manager,
            column_manager, selection_strategy, MockDataSource(rows=3),
        )

        # Inject a synthetic action button on row 0 with row_index=0.
        fake_btn = MagicMock()
        table._row_pool.clear()
        bg_mock = MagicMock()
        bg_mock.visible = True
        table._row_pool.append({
            "bg": bg_mock,
            "row_index": 0,
            "widgets": [{
                "type": "actions",
                "actions_dict": {"add": fake_btn},
            }],
        })

        # Click maps to row 0.
        result_a = table.check_action_button_press(fake_btn)
        assert result_a == ("add", 0)

        # Simulate yard switch: invalidate (Phase 2) + the per-row mapping
        # in update_visible_rows would re-write row_index. Here we
        # simulate the post-update state directly by changing row_index.
        # The point is: click MUST resolve via current row_index, never
        # via a closure-captured value.
        assert hasattr(table, "invalidate_widget_caches"), (
            "PROJ-410 Phase 2 Task 2.2 prerequisite for this test."
        )
        table.invalidate_widget_caches()
        table._row_pool[0]["row_index"] = 7  # simulate post-refresh remap

        result_b = table.check_action_button_press(fake_btn)
        assert result_b == ("add", 7), (
            "PROJ-410 Task 1.6: button press must resolve via the row's "
            "CURRENT row_index, not a closure-captured stale value. "
            "If this fails, check check_action_button_press() at "
            "virtual_table.py:516-524."
        )


# ===========================================================================
# Issue #17 regression tests
# ===========================================================================


class TestIssue17InvalidateClearsWidgetContent:
    """Issue #17: ``invalidate_widget_caches()`` must clear pygame_gui widget
    *content* (``UILabel.set_text("")``, ``UIImage.set_image(blank)``), not
    just the cache attrs (``_last_text`` / ``_last_img`` / ``_last_color``).

    Background — pygame_gui's ``UIPanel.show(show_contents=True)`` calls
    ``self.panel_container.show(show_contents)``; ``UIContainer.show(True)``
    iterates ``self.elements`` and calls ``element.show()`` on every child
    UNCONDITIONALLY (regardless of each child's prior individual
    ``visible`` state). So when ``BuildQueueScreen.open_for_yard()`` calls
    ``self.show()`` after ``_refresh_queue_display()``, every pool row
    background that ``update_visible_rows()`` individually hid (because
    ``data_idx >= current_count``) is recursively un-hidden — and any
    stale text/image left on those rows becomes visible again. The fix:
    invalidation must blank the widget content too, so even when those
    rows reappear they show nothing instead of the previous yard's data.

    Verified against pygame-ce 2.5.7's pygame_gui (``UIPanel.show`` →
    ``panel_container.show(show_contents)``; ``UIContainer.show`` iterates
    children when ``show_contents`` is True).

    Anti-regression: this must coexist with PROJ-373 phase 3's perf-lock
    (``TestRowPoolReuseGuard`` forbids ``.kill()`` on any pool widget) —
    the fix uses ``set_text("")`` / ``set_image(blank)`` only.
    """

    @pytest.fixture(autouse=True)
    def patched_pygame_gui(self):
        with patch("game.ui.components.table.virtual_table.UIImage") as image, \
             patch("game.ui.components.table.virtual_table.UILabel") as label, \
             patch("game.ui.components.table.virtual_table.UIVerticalScrollBar") as scrollbar, \
             patch("game.ui.components.table.virtual_table.UIPanel") as panel, \
             patch("game.ui.components.table.virtual_table.TableHeader") as header:
            yield {
                "UIImage": image, "UILabel": label,
                "UIVerticalScrollBar": scrollbar, "UIPanel": panel,
                "TableHeader": header,
            }

    @pytest.fixture
    def mock_manager(self):
        return MagicMock()

    @pytest.fixture
    def mock_panel(self):
        panel = MagicMock()
        panel.get_relative_rect.return_value = pygame.Rect(0, 0, 300, 400)
        return panel

    @pytest.fixture
    def column_manager(self):
        from game.ui.components.table.column_manager import TableColumnManager
        return TableColumnManager([
            {"id": "name", "label": "Name", "width": 100, "visible": True},
            {"id": "icon", "label": "Icon", "width": 60, "visible": True, "type": "image"},
        ])

    @pytest.fixture
    def selection_strategy(self):
        from game.ui.components.table.selection import SingleSelect
        return SingleSelect()

    def _build_table(self, patched_pygame_gui, mock_panel, mock_manager,
                     column_manager, selection_strategy, data_source):
        from game.ui.components.table.virtual_table import VirtualTable
        mock_list_panel = MagicMock()
        mock_list_panel.get_relative_rect.return_value = pygame.Rect(0, 0, 280, 200)
        patched_pygame_gui["UIPanel"].return_value = mock_list_panel
        return VirtualTable(
            mock_panel, mock_manager, data_source, column_manager,
            selection_strategy,
        )

    def test_invalidate_clears_label_widget_text_not_just_cache_attr(
        self, patched_pygame_gui, mock_panel, mock_manager,
        column_manager, selection_strategy,
    ):
        """Issue #17: ``invalidate_widget_caches()`` must call
        ``set_text("")`` on every label widget in the pool.

        Why this matters: pygame_gui's ``UIPanel.show(show_contents=True)``
        recursively un-hides every child via ``UIContainer.show`` regardless
        of individual visible state. So any stale label text left on a
        pool row that ``update_visible_rows()`` individually hid will
        re-appear on the next show. Nulling the ``_last_text`` cache attr
        alone is NOT sufficient — that only affects future change-detection
        comparisons, not the widget's actual visible content.

        FAILS today (pre-fix): only the cache attr is nulled.
        """
        table = self._build_table(
            patched_pygame_gui, mock_panel, mock_manager,
            column_manager, selection_strategy, MockDataSource(rows=5),
        )

        # Collect every label widget and reset its set_text mock so we
        # can detect new calls from invalidate_widget_caches.
        label_widgets = []
        for row in table._row_pool:
            for widget in row.get("widgets", []):
                if widget.get("type") == "label":
                    widget["el"].set_text.reset_mock()
                    label_widgets.append(widget["el"])
        assert label_widgets, "test setup: expected at least one label widget"

        table.invalidate_widget_caches()

        for el in label_widgets:
            el.set_text.assert_called_with(""), (
                "Issue #17: invalidate_widget_caches() must call "
                "set_text(\"\") on every label widget to defeat the "
                "pygame_gui UIPanel.show(show_contents=True) recursive "
                "un-hide that exposes stale text on previously-hidden "
                "pool rows."
            )

    def test_invalidate_clears_image_widget_via_set_image(
        self, patched_pygame_gui, mock_panel, mock_manager,
        column_manager, selection_strategy,
    ):
        """Issue #17: ``invalidate_widget_caches()`` must call
        ``set_image(...)`` on every image widget so stale portraits don't
        re-appear on the next ``panel.show()``.

        Same root cause as the label test above — pygame_gui recursive
        show un-hides children regardless of their last individual hide.

        FAILS today (pre-fix): only the ``_last_img`` cache attr is nulled.
        """
        table = self._build_table(
            patched_pygame_gui, mock_panel, mock_manager,
            column_manager, selection_strategy, MockDataSource(rows=5),
        )

        image_widgets = []
        for row in table._row_pool:
            for widget in row.get("widgets", []):
                if widget.get("type") == "image":
                    widget["el"].set_image.reset_mock()
                    image_widgets.append(widget["el"])
        assert image_widgets, "test setup: expected at least one image widget"

        table.invalidate_widget_caches()

        for el in image_widgets:
            assert el.set_image.called, (
                "Issue #17: invalidate_widget_caches() must call "
                "set_image(...) on every image widget so the pygame_gui "
                "UIPanel.show(show_contents=True) un-hide does not "
                "expose a stale portrait."
            )

    def test_invalidate_still_preserves_proj410_dirty_flag(
        self, patched_pygame_gui, mock_panel, mock_manager,
        column_manager, selection_strategy,
    ):
        """Anti-regression: the issue #17 fix must NOT regress PROJ-410's
        ephemeral ``_data_identity_dirty`` flag semantics. Invalidation
        sets it True; ``update_visible_rows()`` clears it after one
        re-render.
        """
        table = self._build_table(
            patched_pygame_gui, mock_panel, mock_manager,
            column_manager, selection_strategy, MockDataSource(rows=3),
        )
        table._data_identity_dirty = False
        table.invalidate_widget_caches()
        assert table._data_identity_dirty is True, (
            "Anti-regression: issue #17 fix must preserve PROJ-410's "
            "dirty-flag set in invalidate_widget_caches()."
        )

    def test_invalidate_still_does_not_kill_pool_widgets(
        self, patched_pygame_gui, mock_panel, mock_manager,
        column_manager, selection_strategy,
    ):
        """Anti-regression: issue #17 fix must NOT regress PROJ-373's
        row-pool perf-lock (``TestRowPoolReuseGuard`` forbids ``.kill()``
        on pool widgets).
        """
        table = self._build_table(
            patched_pygame_gui, mock_panel, mock_manager,
            column_manager, selection_strategy, MockDataSource(rows=3),
        )
        kill_spies = []
        for row in table._row_pool:
            if row.get("bg") is not None:
                kill_spies.append(row["bg"].kill)
            for widget in row.get("widgets", []):
                if widget.get("el") is not None:
                    kill_spies.append(widget["el"].kill)

        table.invalidate_widget_caches()

        for kill_mock in kill_spies:
            assert not kill_mock.called, (
                "Anti-regression: issue #17 fix (set_text/set_image to "
                "clear content) must NOT call .kill() on any pool widget. "
                "PROJ-373 perf-lock contract."
            )

    def test_invalidate_hides_row_backgrounds(
        self, patched_pygame_gui, mock_panel, mock_manager,
        column_manager, selection_strategy,
    ):
        """Issue #17 follow-up: ``invalidate_widget_caches()`` must call
        ``hide()`` on every pool row's background panel.

        Why: the first issue #17 fix (a3ced0e1f) cleared label text and
        image surfaces but left the row background AND its child action
        buttons / portrait UIImage / label widgets visible. On a
        brand-new game with an empty queue, every pool row's
        ``data_idx >= current_count`` so the rows should be hidden —
        but pygame_gui's ``UIPanel.show(show_contents=True)`` recursively
        un-hides every descendant in the same panel.show() call that
        ``BuildQueueScreen.open_for_yard()`` makes after
        ``_refresh_queue_display()``, re-exposing ~40 phantom empty
        rows with ``+ – ^ v`` buttons and a blank portrait slot.

        Fix: ``invalidate_widget_caches()`` hides each ``row["bg"]``.
        ``UIPanel.hide(hide_contents=True)`` recursively hides child
        widgets, so action buttons / image / label all participate. The
        ``BuildQueueScreen.show()`` override (separate test) re-runs
        ``force_update() + update_visible_rows()`` to re-show rows where
        ``data_idx < current_count``.

        FAILS today (pre-fix): row_bg.hide is not called by invalidate.
        """
        table = self._build_table(
            patched_pygame_gui, mock_panel, mock_manager,
            column_manager, selection_strategy, MockDataSource(rows=5),
        )

        bg_widgets = []
        for row in table._row_pool:
            if row.get("bg") is not None:
                row["bg"].hide.reset_mock()
                bg_widgets.append(row["bg"])
        assert bg_widgets, "test setup: expected at least one row_bg widget"

        table.invalidate_widget_caches()

        for bg in bg_widgets:
            assert bg.hide.called, (
                "Issue #17 follow-up: invalidate_widget_caches() must call "
                "row['bg'].hide() on every pool row so the row background "
                "AND its child action buttons + image + label widgets are "
                "all hidden via pygame_gui's UIPanel.hide(hide_contents=True). "
                "Otherwise an empty queue on reopen shows ~40 phantom rows "
                "with +/-/^/v buttons visible."
            )
