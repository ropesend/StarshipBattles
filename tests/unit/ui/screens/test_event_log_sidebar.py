"""Tests for EventLogSidebar - Column toggle sidebar for Event Log.

PROJ-215 Phase 3: Tests for the sidebar component that provides
column visibility toggles following the FleetReportSidebar pattern.
"""
import pytest
from unittest.mock import MagicMock, patch

import pygame


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_manager():
    """Create a mock pygame_gui UI manager."""
    return MagicMock()


@pytest.fixture
def sample_columns():
    """Return sample column definitions for testing."""
    return [
        {"id": "category", "width": 90, "title": "Category", "visible": True, "sortable": True},
        {"id": "turn", "width": 60, "title": "Turn", "visible": True, "sortable": True},
        {"id": "system", "width": 120, "title": "System", "visible": True, "sortable": True},
        {"id": "planet", "width": 120, "title": "Planet", "visible": True, "sortable": True},
        {"id": "local_hex", "width": 80, "title": "Local Hex", "visible": False, "sortable": True},
        {"id": "galaxy_hex", "width": 80, "title": "Galaxy Hex", "visible": False, "sortable": True},
        {"id": "message", "width": 500, "title": "Message", "visible": True, "sortable": True},
    ]


@pytest.fixture
def mock_column_manager(sample_columns):
    """Create a mock TableColumnManager with sample columns."""
    manager = MagicMock()
    manager.get_toggleable_columns.return_value = sample_columns
    return manager


@pytest.fixture
def mock_panel():
    """Create a mock UIPanel container."""
    panel = MagicMock()
    panel.get_relative_rect.return_value = pygame.Rect(0, 0, 180, 600)
    return panel


def _make_sidebar(panel, manager, column_manager, on_toggle=None):
    """Create an EventLogSidebar with mocked pygame_gui elements."""
    from game.ui.screens.event_log_sidebar import EventLogSidebar

    # Patch UILabel and UIButton in the shared column-toggle helper
    # (PROJ-319 DUP-X-08: column-toggle widgets moved to game.ui.widgets.column_toggle_section)
    with patch('game.ui.widgets.column_toggle_section.UILabel'), \
         patch('game.ui.widgets.column_toggle_section.UIButton') as mock_btn_class:
        # Make UIButton return new mock instances each time
        mock_btn_class.side_effect = lambda **kwargs: MagicMock(**kwargs)
        sidebar = EventLogSidebar(
            panel=panel,
            manager=manager,
            column_manager=column_manager,
            on_column_toggle=on_toggle
        )
    return sidebar


# ---------------------------------------------------------------------------
# EventLogSidebar Class Tests
# ---------------------------------------------------------------------------

class TestEventLogSidebarInit:
    """Test EventLogSidebar initialization."""

    # PROJ-480 Task 3.41: parametrize the 3 attribute-storage tests on
    # (sidebar_attr, source_fixture_name). The 4th test (`test_stores_callback`)
    # is kept separate because it threads an extra constructor arg
    # (`on_toggle=cb`) and so is not byte-identical to the others.
    @pytest.mark.parametrize(
        "sidebar_attr, source_attr",
        [
            ("panel", "panel"),
            ("manager", "manager"),
            ("column_manager", "column_manager"),
        ],
        ids=["panel_reference", "manager_reference", "column_manager_reference"],
    )
    def test_stores_reference(
        self, mock_panel, mock_manager, mock_column_manager,
        sidebar_attr, source_attr,
    ):
        sidebar = _make_sidebar(mock_panel, mock_manager, mock_column_manager)
        sources = {
            "panel": mock_panel,
            "manager": mock_manager,
            "column_manager": mock_column_manager,
        }
        assert getattr(sidebar, sidebar_attr) is sources[source_attr]

    def test_stores_callback(self, mock_panel, mock_manager, mock_column_manager):
        """Sidebar should store on_column_toggle callback."""
        cb = MagicMock()
        sidebar = _make_sidebar(mock_panel, mock_manager, mock_column_manager, on_toggle=cb)
        assert sidebar.on_column_toggle is cb


class TestColumnToggleButtons:
    """Test column toggle button creation and management."""

    def test_creates_button_for_each_column(self, mock_panel, mock_manager, mock_column_manager, sample_columns):
        """Sidebar should create a button for each toggleable column."""
        sidebar = _make_sidebar(mock_panel, mock_manager, mock_column_manager)
        assert len(sidebar.column_buttons) == len(sample_columns)

    def test_button_stored_by_column_id(self, mock_panel, mock_manager, mock_column_manager):
        """Column buttons should be stored by column ID."""
        sidebar = _make_sidebar(mock_panel, mock_manager, mock_column_manager)
        assert "category" in sidebar.column_buttons
        assert "turn" in sidebar.column_buttons
        assert "system" in sidebar.column_buttons
        assert "message" in sidebar.column_buttons

    def test_button_has_col_ref_attribute(self, mock_panel, mock_manager, mock_column_manager):
        """Each button should have col_ref attribute pointing to column config."""
        sidebar = _make_sidebar(mock_panel, mock_manager, mock_column_manager)
        for col_id, btn in sidebar.column_buttons.items():
            assert hasattr(btn, 'col_ref')


class TestHandleButtonClick:
    """Test handle_button_click method."""

    def test_returns_column_id_for_column_button(self, mock_panel, mock_manager, mock_column_manager):
        """handle_button_click should return column_id for column toggle buttons."""
        sidebar = _make_sidebar(mock_panel, mock_manager, mock_column_manager)

        # Simulate clicking the "system" column button
        system_btn = sidebar.column_buttons["system"]
        result = sidebar.handle_button_click(system_btn)
        assert result == "system"

    def test_returns_none_for_non_column_button(self, mock_panel, mock_manager, mock_column_manager):
        """handle_button_click should return None for non-column buttons."""
        sidebar = _make_sidebar(mock_panel, mock_manager, mock_column_manager)

        # Create a random mock button not in column_buttons
        random_btn = MagicMock()
        result = sidebar.handle_button_click(random_btn)
        assert result is None

    def test_returns_none_for_none_element(self, mock_panel, mock_manager, mock_column_manager):
        """handle_button_click should return None for None element."""
        sidebar = _make_sidebar(mock_panel, mock_manager, mock_column_manager)
        result = sidebar.handle_button_click(None)
        assert result is None


class TestRefreshButtonLabels:
    """Test refresh_button_labels method."""

    def test_updates_visible_column_text(self, mock_panel, mock_manager, mock_column_manager, sample_columns):
        """refresh_button_labels should update text for visible columns to '[x] Title'."""
        sidebar = _make_sidebar(mock_panel, mock_manager, mock_column_manager)

        # Mock column manager to report category as visible
        mock_column_manager.is_column_visible.side_effect = lambda col_id: col_id == "category"

        sidebar.refresh_button_labels()

        # The category button should have been updated with visible text
        # Check that set_text was called on category button
        category_btn = sidebar.column_buttons["category"]
        category_btn.set_text.assert_called()
        call_args = category_btn.set_text.call_args[0][0]
        assert "[x]" in call_args

    def test_updates_hidden_column_text(self, mock_panel, mock_manager, mock_column_manager, sample_columns):
        """refresh_button_labels should update text for hidden columns to '[ ] Title'."""
        sidebar = _make_sidebar(mock_panel, mock_manager, mock_column_manager)

        # Mock column manager to report local_hex as hidden
        mock_column_manager.is_column_visible.side_effect = lambda col_id: col_id != "local_hex"

        sidebar.refresh_button_labels()

        # The local_hex button should have been updated with hidden text
        local_hex_btn = sidebar.column_buttons["local_hex"]
        local_hex_btn.set_text.assert_called()
        call_args = local_hex_btn.set_text.call_args[0][0]
        assert "[ ]" in call_args


class TestSidebarWidth:
    """Test sidebar width calculation."""

    def test_uses_panel_width(self, mock_panel, mock_manager, mock_column_manager):
        """Sidebar should use panel width for layout."""
        mock_panel.get_relative_rect.return_value = pygame.Rect(0, 0, 200, 600)
        sidebar = _make_sidebar(mock_panel, mock_manager, mock_column_manager)
        assert sidebar.sidebar_width == 200
