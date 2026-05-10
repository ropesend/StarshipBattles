"""Tests for FleetReportWindow (PROJ-111 Phase 6).

Tests initialization, ship list, filtering, sorting, multi-select,
and close behavior.

PROJ-328 Phase A Task A.4 (PROJ-322 Task 5.6): Migrated from the
legacy ``__new__`` + manual-attribute-wiring helper to the two-stage
construction pattern. Window is built via ``bypass_init`` +
``MockFleetReportUiBuilder`` so the cheap-state delegates
(``view_model``, ``column_manager``, ``selection``) are real
instances and the widget slots are populated by a single shared
helper instead of ~80 lines of per-test wiring.
"""

from unittest.mock import MagicMock, patch
import pygame

from game.ui.screens.fleet_report_window import FleetReportWindow
from tests.fixtures.fleet_report_ui_builder import MockFleetReportUiBuilder
from tests.fixtures.ui_widget_factory import bypass_init


# --- Helpers ---


def _make_ship_mock(name="Test Ship", ship_class="Cruiser",
                    hp_current=80, hp_max=100, instance_id=None,
                    serial=1):
    ship = MagicMock()
    ship.name = name
    ship.ship_class = ship_class
    ship.design_class = ship_class
    ship.hp_current = hp_current
    ship.hp_max = hp_max
    ship.is_alive = hp_current > 0
    ship.is_derelict = False
    ship.is_damaged = MagicMock(return_value=hp_current < hp_max)
    ship.get_hp_percentage = MagicMock(
        return_value=(hp_current / hp_max) if hp_max else 0)
    ship.design_data = {'name': name, 'class': ship_class}
    ship.instance_id = instance_id or f"id-{name}"
    # FleetListViewModel default sort is 'serial' — make it sortable.
    ship.serial = serial
    return ship


def _make_fleet_mock(num_ships=3):
    fleet = MagicMock()
    fleet.id = "Fleet_1"
    fleet.owner_id = 0
    fleet.location = MagicMock()
    fleet.ships = [
        _make_ship_mock(
            name=f"Ship_{i}",
            ship_class="Cruiser" if i % 2 == 0 else "Escort",
            hp_current=100 - (i * 10),
            hp_max=100,
            serial=i + 1,
        )
        for i in range(num_ships)
    ]
    return fleet


def _make_fleet_report_window(num_ships=3, *, ui_builder=None,
                              with_split_callback=False):
    """Construct a real FleetReportWindow under bypass_init.

    Returns ``(window, fleet)``. The cheap-state delegates
    (view_model, column_manager, selection) are real; widget slots
    (sidebar, virtual_table, ship_detail_panel) are MagicMocks
    populated by ``MockFleetReportUiBuilder``.
    """
    if ui_builder is None:
        ui_builder = MockFleetReportUiBuilder()
    fleet = _make_fleet_mock(num_ships)
    callback = MagicMock() if with_split_callback else None
    with bypass_init(FleetReportWindow):
        window = FleetReportWindow(
            pygame.Rect(0, 0, 1600, 900),
            MagicMock(name="ui_manager"),
            fleet,
            empire=MagicMock(),
            window_manager=None,
            on_close_callback=MagicMock(),
            split_fleet_callback=callback,
            ui_builder=ui_builder,
        )
    return window, fleet


# ===========================================================================
# Initialization
# ===========================================================================


class TestFleetReportWindowInitialization:
    def test_init_with_fleet_data(self):
        window, fleet = _make_fleet_report_window()
        assert window.fleet is fleet
        assert len(fleet.ships) == 3

    def test_window_title_uses_fleet_id(self):
        window, fleet = _make_fleet_report_window()
        assert fleet.id == "Fleet_1"

    def test_panel_layout_three_sections(self):
        window, _ = _make_fleet_report_window()
        assert window.sidebar_panel is not None
        assert window.list_panel is not None
        assert window.detail_panel is not None

    def test_view_model_constructed_with_ships(self):
        window, fleet = _make_fleet_report_window()
        # view_model is real Stage-1; should have the ships.
        assert len(window.view_model.get_filtered_ships()) == 3

    def test_window_init_bypassed_flag_set(self):
        window, _ = _make_fleet_report_window()
        assert window._window_init_bypassed is True


# ===========================================================================
# Ship list / view-model integration
# ===========================================================================


class TestFleetReportShipList:
    def test_ship_list_populates_with_fleet_ships(self):
        window, fleet = _make_fleet_report_window()
        assert len(window.view_model.get_filtered_ships()) == 3

    def test_ship_list_empty_fleet_handled_gracefully(self):
        window, _ = _make_fleet_report_window(num_ships=0)
        assert window.view_model.get_filtered_ships() == []


class TestFleetReportFilteringAndSorting:
    def test_set_sort_updates_view_model(self):
        window, _ = _make_fleet_report_window()
        window.view_model.set_sort('class')
        assert window.view_model.sort_column_id == 'class'


# ===========================================================================
# Multi-select
# ===========================================================================


class TestFleetReportMultiSelect:
    def test_normal_click_replaces_selection(self):
        window, _ = _make_fleet_report_window()
        window.selection.handle_click(0, ctrl_held=False)
        window.selection.handle_click(2, ctrl_held=False)
        assert window.selection.get_selected_indices() == {2}

    def test_ctrl_click_adds_to_selection(self):
        window, _ = _make_fleet_report_window()
        window.selection.handle_click(0, ctrl_held=False)
        window.selection.handle_click(1, ctrl_held=True)
        assert {0, 1} == window.selection.get_selected_indices()


# ===========================================================================
# Detail panel
# ===========================================================================


class TestFleetReportDetailPanel:
    def test_detail_panel_shows_ship_info(self):
        window, fleet = _make_fleet_report_window()
        ship = fleet.ships[0]
        window.selected_ship = ship

        window._update_detail_panel()
        window.ship_detail_panel.update_ship.assert_called_once_with(ship)

    def test_detail_panel_placeholder_when_no_selection(self):
        window, _ = _make_fleet_report_window()
        window.selected_ship = None

        window._update_detail_panel()
        window.ship_detail_panel.update_ship.assert_called_once_with(None)


# ===========================================================================
# Close behavior
# ===========================================================================


class TestFleetReportCloseBehavior:
    def test_close_callback_invoked_on_kill(self):
        window, _ = _make_fleet_report_window()
        callback = window.on_close_callback

        with patch('pygame_gui.elements.UIWindow.kill'):
            window.kill()

        callback.assert_called_once()

    def test_kill_cleans_up_virtual_table_and_detail_panel(self):
        window, _ = _make_fleet_report_window()
        vt = window.virtual_table
        sd = window.ship_detail_panel

        with patch('pygame_gui.elements.UIWindow.kill'):
            window.kill()

        vt.kill.assert_called_once()
        sd.kill.assert_called_once()


# ===========================================================================
# Tri-state filter wiring (PROJ-220 Task 3.4 retained)
# ===========================================================================


class TestFleetReportTriStateWiring:
    """Test FleetReportWindow handles tri-state filter changes from sidebar (PROJ-220)."""

    def _setup_window(self, sidebar_actions):
        window, _ = _make_fleet_report_window()
        window.sidebar = MagicMock()
        window.sidebar.check_button_presses.return_value = sidebar_actions
        window.virtual_table = MagicMock()
        window.virtual_table.check_header_presses.return_value = {
            'swap_column': None, 'sort_column': None
        }
        # view_model is real Stage-1; replace toggle/set hooks for assertions.
        window.view_model = MagicMock()
        window.selection = MagicMock()
        window._update_detail_panel = MagicMock()
        window.refresh_list = MagicMock()
        return window

    @patch('pygame_gui.elements.UIWindow.update')
    def test_filter_state_changed_calls_set_filter_state(self, _mock_super):
        from game.ui.filters.filter_state import FilterState

        window = self._setup_window({
            'filter_toggled': None,
            'filter_state_changed': ('warp_capable', FilterState.YES),
            'column_toggled': None,
            'remove_selected': False,
        })
        window.update(0.016)
        window.view_model.set_filter_state.assert_called_once_with(
            'warp_capable', FilterState.YES)

    @patch('pygame_gui.elements.UIWindow.update')
    def test_filter_state_changed_refreshes_list(self, _mock_super):
        from game.ui.filters.filter_state import FilterState

        window = self._setup_window({
            'filter_toggled': None,
            'filter_state_changed': ('has_cargo', FilterState.NO),
            'column_toggled': None,
            'remove_selected': False,
        })
        window.update(0.016)
        window.refresh_list.assert_called_once()

    @patch('pygame_gui.elements.UIWindow.update')
    def test_filter_state_changed_clears_selection(self, _mock_super):
        from game.ui.filters.filter_state import FilterState

        window = self._setup_window({
            'filter_toggled': None,
            'filter_state_changed': ('destroy_planet', FilterState.YES),
            'column_toggled': None,
            'remove_selected': False,
        })
        window.update(0.016)
        window.selection.clear.assert_called()

    @patch('pygame_gui.elements.UIWindow.update')
    def test_status_filter_toggle_still_works(self, _mock_super):
        window = self._setup_window({
            'filter_toggled': 'damaged',
            'filter_state_changed': None,
            'column_toggled': None,
            'remove_selected': False,
        })
        window.update(0.016)
        window.view_model.toggle_filter.assert_called_once_with('damaged')
