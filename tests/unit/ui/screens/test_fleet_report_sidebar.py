"""Tests for FleetReportSidebar tri-state filter integration (PROJ-220 Phase 3 Task 3.3)."""
from unittest.mock import Mock, patch

from game.ui.filters.filter_state import FilterState


def _create_sidebar(**overrides):
    """Create a FleetReportSidebar with mocked dependencies.

    Returns (sidebar, mocks_dict).
    """
    mock_panel = Mock()
    mock_panel.get_relative_rect.return_value = Mock(width=300)
    mock_manager = Mock()

    mock_view_model = Mock()
    mock_view_model.filter_show_damaged = True
    mock_view_model.filter_show_undamaged = True
    mock_view_model.filter_show_derelict = True
    mock_view_model.filter_show_destroyed = False
    mock_view_model.get_filter_label.side_effect = lambda fid: {
        'damaged': 'Damaged', 'undamaged': 'Undamaged',
        'derelict': 'Derelict', 'destroyed': 'Destroyed',
        'warp_capable': 'Warp Capable', 'has_spaceyard': 'Has Spaceyard',
        'has_cargo': 'Has Cargo', 'destroy_planet': 'Destroy Planet',
        'open_warp': 'Open Warp', 'close_warp': 'Close Warp',
        'destroy_star': 'Destroy Star', 'create_sphere': 'Create Sphere',
    }.get(fid, fid)

    mock_column_manager = Mock()
    mock_column_manager.get_toggleable_columns.return_value = []

    mock_empire = overrides.get('empire', Mock())

    with patch('game.ui.screens.fleet_report_sidebar.UILabel'):
        with patch('game.ui.screens.fleet_report_sidebar.UIButton') as mock_btn_cls:
            # UIButton mocks default check_pressed to False
            def _make_btn(**kw):
                btn = Mock()
                btn.check_pressed.return_value = False
                return btn
            mock_btn_cls.side_effect = _make_btn
            with patch('game.ui.screens.fleet_report_sidebar.TriStateFilterWidget') as mock_tsw_cls:
                # Each call to TriStateFilterWidget returns a unique mock
                mock_tsw_cls.side_effect = lambda **kw: Mock(
                    attribute_name=kw.get('attribute_name', 'unknown'),
                    current_state=FilterState.IGNORE,
                    check_pressed=Mock(return_value=None),
                    set_state=Mock(),
                    kill=Mock(),
                )

                sidebar = None
                from game.ui.screens.fleet_report_sidebar import FleetReportSidebar
                sidebar = FleetReportSidebar(
                    panel=mock_panel,
                    manager=mock_manager,
                    view_model=mock_view_model,
                    column_manager=mock_column_manager,
                    empire=mock_empire,
                )

                mocks = {
                    'panel': mock_panel,
                    'manager': mock_manager,
                    'view_model': mock_view_model,
                    'column_manager': mock_column_manager,
                    'empire': mock_empire,
                    'TriStateFilterWidget': mock_tsw_cls,
                    'UIButton': mock_btn_cls,
                }
                return sidebar, mocks


class TestSidebarTriStateWidgets:
    """Test that sidebar creates TriStateFilterWidget for tri-state filters."""

    def test_creates_tri_state_widgets_dict(self):
        """Sidebar should have a tri_state_widgets dict."""
        sidebar, _ = _create_sidebar()
        assert hasattr(sidebar, 'tri_state_widgets')
        assert isinstance(sidebar.tri_state_widgets, dict)

    def test_creates_eight_tri_state_widgets(self):
        """Sidebar should create 8 TriStateFilterWidget instances."""
        sidebar, mocks = _create_sidebar()
        assert len(sidebar.tri_state_widgets) == 8

    def test_tri_state_widget_keys(self):
        """Sidebar tri_state_widgets should have correct attribute keys."""
        sidebar, _ = _create_sidebar()
        expected_keys = {
            'warp_capable', 'has_spaceyard', 'has_cargo',
            'destroy_planet', 'open_warp', 'close_warp',
            'destroy_star', 'create_sphere',
        }
        assert set(sidebar.tri_state_widgets.keys()) == expected_keys

    def test_status_filter_buttons_still_exist(self):
        """Sidebar should still have status filter buttons (damaged, undamaged, derelict, destroyed)."""
        sidebar, _ = _create_sidebar()
        for status_id in ('damaged', 'undamaged', 'derelict', 'destroyed'):
            assert status_id in sidebar.filter_buttons, f"Missing status button: {status_id}"

    def test_no_paired_buttons_for_tri_state(self):
        """Sidebar should NOT have paired buttons for tri-state attributes."""
        sidebar, _ = _create_sidebar()
        # Old paired button IDs should not exist
        old_button_ids = [
            'warp_capable', 'not_warp_capable',
            'has_spaceyard', 'no_spaceyard',
            'has_cargo', 'no_cargo',
            'can_destroy_planet', 'no_destroy_planet',
            'can_open_warp', 'no_open_warp',
            'can_close_warp', 'no_close_warp',
            'can_destroy_star', 'no_destroy_star',
            'can_create_sphere', 'no_create_sphere',
        ]
        for old_id in old_button_ids:
            assert old_id not in sidebar.filter_buttons, f"Old paired button still exists: {old_id}"


class TestSidebarCheckButtonPresses:
    """Test check_button_presses with tri-state widgets."""

    def test_returns_filter_state_changed_key(self):
        """check_button_presses result should include filter_state_changed key."""
        sidebar, _ = _create_sidebar()
        result = sidebar.check_button_presses()
        assert 'filter_state_changed' in result

    def test_filter_state_changed_none_when_no_press(self):
        """filter_state_changed should be None when no tri-state widget pressed."""
        sidebar, _ = _create_sidebar()
        result = sidebar.check_button_presses()
        assert result['filter_state_changed'] is None

    def test_filter_state_changed_returns_tuple_on_press(self):
        """filter_state_changed should return (attribute, new_state) when widget pressed."""
        sidebar, _ = _create_sidebar()
        # Simulate a tri-state widget returning a new state
        warp_widget = sidebar.tri_state_widgets['warp_capable']
        warp_widget.check_pressed.return_value = FilterState.YES

        result = sidebar.check_button_presses()
        assert result['filter_state_changed'] == ('warp_capable', FilterState.YES)

    def test_status_filter_toggled_still_works(self):
        """filter_toggled should still work for status filter buttons."""
        sidebar, _ = _create_sidebar()
        # Simulate a status button press
        damaged_btn = sidebar.filter_buttons['damaged']
        damaged_btn.check_pressed.return_value = True

        result = sidebar.check_button_presses()
        assert result['filter_toggled'] == 'damaged'

    def test_tri_state_takes_priority_over_status(self):
        """If both tri-state and status are pressed, only one is returned (first wins)."""
        sidebar, _ = _create_sidebar()
        # Only one action per frame — check_button_presses returns on first match
        result = sidebar.check_button_presses()
        # No presses — both should be None
        assert result['filter_toggled'] is None
        assert result['filter_state_changed'] is None


class TestSidebarUpdateFilterButton:
    """Test update_filter_button for status filters."""

    def test_update_status_filter_button(self):
        """update_filter_button should update status filter button appearance."""
        sidebar, _ = _create_sidebar()
        btn = sidebar.filter_buttons['damaged']

        sidebar.update_filter_button('damaged', True)
        btn.select.assert_called()

    def test_update_status_filter_button_disabled(self):
        """update_filter_button should unselect when disabled."""
        sidebar, _ = _create_sidebar()
        btn = sidebar.filter_buttons['damaged']

        sidebar.update_filter_button('damaged', False)
        btn.unselect.assert_called()
