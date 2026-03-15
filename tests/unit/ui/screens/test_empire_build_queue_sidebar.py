"""Tests for EmpireBuildQueueSidebar tri-state filter integration.

PROJ-220 Phase 4 Task 4.3: Verify sidebar creates TriStateFilterWidget instances
instead of paired toggle buttons, and returns filter_state_changed actions.
"""
from unittest.mock import Mock, patch

from game.ui.filters.filter_state import FilterState


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_viewmodel():
    """Create a mock viewmodel with the new FilterState API."""
    vm = Mock()
    vm.get_filter_state = Mock(return_value=FilterState.IGNORE)
    vm.set_filter_state = Mock()
    vm.apply_filters = Mock()
    vm.set_search_text = Mock()
    return vm


def _make_sidebar(viewmodel=None):
    """Create sidebar with mocked pygame_gui dependencies."""
    from game.ui.screens.empire_build_queue_sidebar import EmpireBuildQueueSidebar

    vm = viewmodel or _make_mock_viewmodel()
    event_bus = Mock()
    columns = [
        {'id': 'location', 'width': 180, 'title': 'Location', 'visible': True},
        {'id': 'system', 'width': 120, 'title': 'System', 'visible': True},
    ]

    with patch('game.ui.screens.empire_build_queue_sidebar.UILabel'):
        with patch('game.ui.screens.empire_build_queue_sidebar.UIButton') as MockBtn:
            # Ensure mock buttons have check_pressed returning False
            MockBtn.return_value = Mock(check_pressed=Mock(return_value=False))
            with patch('game.ui.screens.empire_build_queue_sidebar.UITextEntryLine'):
                with patch('game.ui.screens.empire_build_queue_sidebar.TriStateFilterWidget') as MockWidget:
                    # Each call creates a distinct mock widget
                    def _make_widget(**kwargs):
                        return Mock(
                            check_pressed=Mock(return_value=None),
                            set_state=Mock(),
                        )
                    MockWidget.side_effect = _make_widget
                    sidebar = EmpireBuildQueueSidebar(
                        ui_manager=Mock(),
                        parent_container=Mock(),
                        viewmodel=vm,
                        event_bus=event_bus,
                        columns=columns,
                    )
    return sidebar, vm


# ---------------------------------------------------------------------------
# Tests: Widget Creation
# ---------------------------------------------------------------------------

class TestSidebarTriStateWidgets:
    """Verify sidebar creates TriStateFilterWidget instances."""

    def test_has_tri_state_widgets_dict(self):
        """Sidebar should have a tri_state_widgets attribute."""
        sidebar, _ = _make_sidebar()
        assert hasattr(sidebar, 'tri_state_widgets')
        assert isinstance(sidebar.tri_state_widgets, dict)

    def test_six_tri_state_widgets_created(self):
        """Should create 6 tri-state widgets (2 location + 2 status + 2 capabilities)."""
        sidebar, _ = _make_sidebar()
        assert len(sidebar.tri_state_widgets) == 6

    def test_tri_state_widget_keys(self):
        """Widget keys should match the filter keys."""
        sidebar, _ = _make_sidebar()
        expected_keys = {
            'loc_Planet', 'loc_Fleet',
            'status_Active', 'status_Empty',
            'cap_Ships', 'cap_Complexes',
        }
        assert set(sidebar.tri_state_widgets.keys()) == expected_keys

    def test_no_filter_toggle_buttons(self):
        """Old filter_toggle_buttons dict should be empty or not exist."""
        sidebar, _ = _make_sidebar()
        # Either empty dict or not present
        toggle_buttons = getattr(sidebar, 'filter_toggle_buttons', {})
        assert len(toggle_buttons) == 0


# ---------------------------------------------------------------------------
# Tests: check_tri_state_presses
# ---------------------------------------------------------------------------

class TestSidebarCheckTriStatePresses:
    """Verify check_tri_state_presses returns correct actions."""

    def test_returns_none_when_no_press(self):
        """Should return None when no widget was pressed."""
        sidebar, _ = _make_sidebar()
        result = sidebar.check_tri_state_presses()
        assert result is None

    def test_returns_tuple_on_press(self):
        """Should return (key, FilterState) when a widget is pressed."""
        sidebar, _ = _make_sidebar()
        # Simulate a widget press
        sidebar.tri_state_widgets['loc_Planet'].check_pressed.return_value = FilterState.YES
        result = sidebar.check_tri_state_presses()
        assert result == ('loc_Planet', FilterState.YES)

    def test_sets_widget_state_on_press(self):
        """Should call set_state on the widget when pressed."""
        sidebar, _ = _make_sidebar()
        sidebar.tri_state_widgets['status_Active'].check_pressed.return_value = FilterState.NO
        sidebar.check_tri_state_presses()
        sidebar.tri_state_widgets['status_Active'].set_state.assert_called_once_with(FilterState.NO)

    def test_calls_viewmodel_set_filter_state(self):
        """Should call viewmodel.set_filter_state with key and state."""
        sidebar, vm = _make_sidebar()
        # Reset all widgets to no press, then set only cap_Ships
        for w in sidebar.tri_state_widgets.values():
            w.check_pressed.return_value = None
        sidebar.tri_state_widgets['cap_Ships'].check_pressed.return_value = FilterState.YES
        sidebar.check_tri_state_presses()
        vm.set_filter_state.assert_called_once_with('cap_Ships', FilterState.YES)

    def test_calls_viewmodel_apply_filters(self):
        """Should call viewmodel.apply_filters after state change."""
        sidebar, vm = _make_sidebar()
        # Reset all widgets to no press, then set only loc_Fleet
        for w in sidebar.tri_state_widgets.values():
            w.check_pressed.return_value = None
        sidebar.tri_state_widgets['loc_Fleet'].check_pressed.return_value = FilterState.NO
        sidebar.check_tri_state_presses()
        vm.apply_filters.assert_called_once()

    def test_only_first_press_handled(self):
        """If multiple widgets pressed, only the first one is handled."""
        sidebar, vm = _make_sidebar()
        sidebar.tri_state_widgets['loc_Planet'].check_pressed.return_value = FilterState.YES
        sidebar.tri_state_widgets['loc_Fleet'].check_pressed.return_value = FilterState.NO
        result = sidebar.check_tri_state_presses()
        # Should handle exactly one
        assert result is not None
        assert vm.set_filter_state.call_count == 1


# ---------------------------------------------------------------------------
# Tests: handle_button_click still works for columns and apply
# ---------------------------------------------------------------------------

class TestSidebarHandleButtonClick:
    """Verify handle_button_click works for non-filter buttons."""

    def test_apply_button_still_works(self):
        """Apply button click should call viewmodel.apply_filters."""
        sidebar, vm = _make_sidebar()
        sidebar._handle_apply_click()
        vm.apply_filters.assert_called_once()

    def test_column_toggle_still_works(self):
        """Column toggle should update column visibility."""
        sidebar, _ = _make_sidebar()
        # Initially visible
        assert sidebar.columns[0]['visible'] is True
        sidebar._handle_column_toggle('location')
        assert sidebar.columns[0]['visible'] is False

    def test_handle_button_click_returns_false_for_unknown(self):
        """Unknown buttons should return False."""
        sidebar, _ = _make_sidebar()
        result = sidebar.handle_button_click(Mock())
        assert result is False
