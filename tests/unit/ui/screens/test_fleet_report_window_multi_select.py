"""
Tests for FleetReportWindow multi-select and ship removal features.

PROJ-101 Phase 4: Multi-select + Remove Ships functionality.
PROJ-188 Phase 2: Updated for VirtualTable migration (selection -> MultiSelect).
PROJ-208 Phase 1: SplitFleetCommand callback dispatch pattern.
PROJ-328 Phase A Task A.4: Migrated from the legacy nested-patch
construction pattern to the two-stage construction pattern (PROJ-322
Tasks 5.7 + 3.20). Window is now built via ``bypass_init`` +
``MockFleetReportUiBuilder``; the cheap-state ``view_model`` /
``column_manager`` / ``selection`` delegates are real instances
created by Stage-1 of the constructor.
"""

import pytest
from unittest.mock import Mock, patch
import pygame

from game.ui.screens.fleet_report_window import FleetReportWindow
from tests.fixtures.fleet_report_ui_builder import (
    MockFleetReportUiBuilder,
    NullFleetReportUiBuilder,
)
from tests.fixtures.ui_widget_factory import bypass_init


def create_mock_ship(instance_id: str, name: str, serial: int = 1):
    """Create a mock ship for testing."""
    ship = Mock()
    ship.instance_id = instance_id
    ship.name = name
    ship.serial = serial
    ship.design_id = f"design-{instance_id}"
    ship.design_data = {'name': name, 'theme_id': 'Federation', 'ship_class': 'Frigate'}
    ship.is_alive = True
    ship.is_derelict = False
    ship.is_damaged = Mock(return_value=False)
    ship.get_hp_percentage = Mock(return_value=1.0)
    ship._display_fmt.get_display_id = Mock(return_value=f"SN-{serial:04d}")
    return ship


def create_mock_fleet(ships, fleet_id=1, owner_id=0):
    """Create a mock fleet for testing."""
    fleet = Mock()
    fleet.id = fleet_id
    fleet.owner_id = owner_id
    fleet.location = (0, 0)
    fleet.ships = list(ships)
    fleet.speed = 5.0
    fleet.orders = []
    fleet.remove_ship = Mock(side_effect=lambda s: fleet.ships.remove(s) or True if s in fleet.ships else False)
    fleet.add_ship = Mock(side_effect=lambda s: fleet.ships.append(s))
    fleet.get_capability_summary = Mock(return_value={
        'can_warp': True, 'warp_limiting_ship': None,
        'fuel_endurance': 10, 'warp_jumps': 5,
    })
    return fleet


def create_mock_empire(empire_id=0, next_fleet_id=100):
    """Create a mock empire for testing."""
    empire = Mock()
    empire.id = empire_id
    empire.fleets = []
    empire._next_fleet_id = next_fleet_id
    empire.get_next_fleet_id = Mock(side_effect=lambda: (
        setattr(empire, '_next_fleet_id', empire._next_fleet_id + 1)
        or empire._next_fleet_id - 1
    ))
    empire.add_fleet = Mock(side_effect=lambda f: empire.fleets.append(f))
    return empire


def _make_window(fleet, empire=None, *, split_fleet_callback=None,
                 ui_builder=None):
    """Construct a real FleetReportWindow under bypass_init."""
    if ui_builder is None:
        ui_builder = MockFleetReportUiBuilder()
    with bypass_init(FleetReportWindow):
        return FleetReportWindow(
            pygame.Rect(0, 0, 1600, 900),
            Mock(name="ui_manager"),
            fleet,
            empire=empire,
            window_manager=None,
            split_fleet_callback=split_fleet_callback,
            ui_builder=ui_builder,
        )


class TestFleetReportWindowInit:
    """Test FleetReportWindow initialization with empire parameter."""

    @pytest.fixture
    def mock_ships(self):
        return [create_mock_ship(f"ship-{i}", f"Ship {i}", i + 1) for i in range(5)]

    @pytest.fixture
    def mock_fleet(self, mock_ships):
        return create_mock_fleet(mock_ships)

    @pytest.fixture
    def mock_empire(self):
        return create_mock_empire()

    def test_init_stores_empire_reference(self, mock_fleet, mock_empire):
        window = _make_window(mock_fleet, mock_empire)
        assert window.empire is mock_empire

    def test_init_empire_defaults_to_none(self, mock_fleet):
        window = _make_window(mock_fleet)
        assert window.empire is None

    def test_init_creates_selection_strategy(self, mock_fleet, mock_empire):
        from game.ui.components.table import MultiSelect

        window = _make_window(mock_fleet, mock_empire)
        assert isinstance(window.selection, MultiSelect)
        assert len(window.selection.get_selected_indices()) == 0

    def test_window_init_bypassed_flag_set(self, mock_fleet):
        window = _make_window(mock_fleet)
        assert window._window_init_bypassed is True

    def test_null_builder_leaves_widget_slots_unset(self, mock_fleet):
        window = _make_window(mock_fleet, ui_builder=NullFleetReportUiBuilder())
        assert window.sidebar is None
        assert window.virtual_table is None
        assert window.ship_detail_panel is None

    def test_view_model_constructed_with_fleet_ships(self, mock_fleet):
        window = _make_window(mock_fleet)
        # FleetListViewModel is real Stage-1; should have the ships.
        assert len(window.view_model.get_filtered_ships()) == len(mock_fleet.ships)


class TestMultiSelectBehavior:
    """Test Ctrl+click multi-select behavior."""

    @pytest.fixture
    def window_with_ships(self):
        ships = [create_mock_ship(f"ship-{i}", f"Ship {i}", i + 1) for i in range(5)]
        fleet = create_mock_fleet(ships)
        empire = create_mock_empire()
        window = _make_window(fleet, empire)
        return window, ships

    def test_normal_click_replaces_selection(self, window_with_ships):
        window, ships = window_with_ships
        window.selection.handle_click(0, ctrl_held=False)
        window.selection.handle_click(1, ctrl_held=False)
        # Normal click replaces, so only 1 is selected.
        assert window.selection.get_selected_indices() == {1}

    def test_ctrl_click_adds_to_selection(self, window_with_ships):
        window, ships = window_with_ships
        window.selection.handle_click(0, ctrl_held=False)
        window.selection.handle_click(1, ctrl_held=True)
        assert 0 in window.selection.get_selected_indices()
        assert 1 in window.selection.get_selected_indices()

    def test_ctrl_click_removes_from_selection_when_multiple(self, window_with_ships):
        window, ships = window_with_ships
        window.selection.handle_click(0, ctrl_held=False)
        window.selection.handle_click(1, ctrl_held=True)
        window.selection.handle_click(2, ctrl_held=True)
        # Now ctrl-click on 1 to remove it.
        window.selection.handle_click(1, ctrl_held=True)
        selected = window.selection.get_selected_indices()
        assert 0 in selected
        assert 1 not in selected
        assert 2 in selected


class TestShipRemoval:
    """Test ship removal to new fleet functionality.

    PROJ-208: window calls split_fleet_callback(fleet_id, ship_instance_ids)
    instead of directly manipulating fleets.
    """

    @pytest.fixture
    def window_with_ships_and_empire(self):
        ships = [create_mock_ship(f"ship-{i}", f"Ship {i}", i + 1) for i in range(5)]
        fleet = create_mock_fleet(ships)
        empire = create_mock_empire()
        callback = Mock()
        window = _make_window(fleet, empire, split_fleet_callback=callback)

        # Patch refresh helpers that hit the (mock) sidebar / virtual_table.
        window._update_detail_panel = Mock()
        window.refresh_list = Mock()
        # view_model is real Stage-1 — replace its filtered ships getter
        # so we can drive selection by index without rebuilding the view.
        window.view_model.get_filtered_ships = Mock(return_value=list(ships))
        window.view_model.update_ships = Mock()
        # sidebar is a MagicMock from MockFleetReportUiBuilder; replace
        # update_remove_button so we can assert calls.
        window.sidebar.update_remove_button = Mock()
        window.sidebar.update_summary = Mock()
        return window, fleet, empire, ships, callback

    def test_remove_dispatches_command_with_correct_fleet_id(self, window_with_ships_and_empire):
        window, fleet, empire, ships, callback = window_with_ships_and_empire
        window.selection._selected = {1, 2}

        window._on_remove_selected_ships()

        callback.assert_called_once()
        assert callback.call_args[0][0] == fleet.id

    def test_remove_dispatches_command_with_selected_ship_ids(self, window_with_ships_and_empire):
        window, fleet, empire, ships, callback = window_with_ships_and_empire
        window.selection._selected = {0, 2}

        window._on_remove_selected_ships()

        ship_ids = callback.call_args[0][1]
        assert ships[0].instance_id in ship_ids
        assert ships[2].instance_id in ship_ids
        assert len(ship_ids) == 2

    def test_remove_dispatches_single_ship_removal(self, window_with_ships_and_empire):
        window, fleet, empire, ships, callback = window_with_ships_and_empire
        window.selection._selected = {3}

        window._on_remove_selected_ships()

        ship_ids = callback.call_args[0][1]
        assert ship_ids == [ships[3].instance_id]

    def test_selection_cleared_after_removal(self, window_with_ships_and_empire):
        window, fleet, empire, ships, callback = window_with_ships_and_empire
        window.selection._selected = {0, 1, 2}

        window._on_remove_selected_ships()

        assert len(window.selection.get_selected_indices()) == 0

    # PROJ-494 T3.2: 3 null-guard tests collapsed into 1 parametrized test.
    @pytest.mark.parametrize(
        "guard_name,apply_guard",
        [
            pytest.param(
                'no_empire',
                lambda w: (setattr(w, 'empire', None),
                          w.selection._selected.update({0, 1})),
                id='no_empire',
            ),
            pytest.param(
                'no_callback',
                lambda w: (setattr(w, '_split_fleet_callback', None),
                          w.selection._selected.update({0, 1})),
                id='no_callback',
            ),
            pytest.param(
                'empty_selection',
                lambda w: w.selection.clear(),
                id='empty_selection',
            ),
        ],
    )
    def test_remove_does_nothing_when_guarded(
        self, window_with_ships_and_empire, guard_name, apply_guard,
    ):
        window, fleet, empire, ships, callback = window_with_ships_and_empire
        apply_guard(window)

        window._on_remove_selected_ships()

        callback.assert_not_called()

    def test_ui_refreshed_after_removal(self, window_with_ships_and_empire):
        window, fleet, empire, ships, callback = window_with_ships_and_empire
        window.selection._selected = {0}

        window._on_remove_selected_ships()

        assert window._update_detail_panel.called
        assert window.refresh_list.called
        assert window.sidebar.update_remove_button.called


class TestRemoveButtonState:
    """Test Remove Selected button enable/disable behavior via sidebar."""

    @pytest.fixture
    def sidebar_with_button(self):
        from game.ui.screens.fleet_report_sidebar import FleetReportSidebar

        mock_panel = Mock()
        mock_panel.get_relative_rect.return_value = Mock(width=300)
        mock_manager = Mock()
        mock_view_model = Mock()
        mock_view_model.is_filter_enabled.return_value = True
        mock_view_model.get_filter_label.return_value = "Test"
        mock_column_manager = Mock()
        mock_column_manager.get_toggleable_columns.return_value = []
        mock_empire = Mock()

        # PROJ-319 DUP-X-08: column toggles moved to game.ui.widgets.column_toggle_section.
        with patch('game.ui.screens.fleet_report_sidebar.UIPanel'):
            with patch('game.ui.screens.fleet_report_sidebar.UILabel'), \
                 patch('game.ui.widgets.column_toggle_section.UILabel'):
                with patch('game.ui.screens.fleet_report_sidebar.UIButton'), \
                     patch('game.ui.widgets.column_toggle_section.UIButton'):
                    with patch('game.ui.screens.fleet_report_sidebar.TriStateFilterWidget'):
                        sidebar = FleetReportSidebar(
                            panel=mock_panel,
                            manager=mock_manager,
                            view_model=mock_view_model,
                            column_manager=mock_column_manager,
                            empire=mock_empire,
                        )
                        sidebar.btn_remove_selected = Mock()
                        sidebar.btn_remove_selected.enable = Mock()
                        sidebar.btn_remove_selected.disable = Mock()
                        sidebar.btn_remove_selected.set_text = Mock()

                        return sidebar

    def test_button_enabled_with_selection_and_empire(self, sidebar_with_button):
        sidebar = sidebar_with_button
        sidebar.update_remove_button(2)

        sidebar.btn_remove_selected.enable.assert_called_once()
        sidebar.btn_remove_selected.set_text.assert_called_with("Remove Selected (2)")

    def test_button_disabled_without_selection(self, sidebar_with_button):
        sidebar = sidebar_with_button
        sidebar.update_remove_button(0)

        sidebar.btn_remove_selected.disable.assert_called_once()

    def test_button_disabled_without_empire(self, sidebar_with_button):
        sidebar = sidebar_with_button
        sidebar.empire = None

        sidebar.update_remove_button(1)

        sidebar.btn_remove_selected.disable.assert_called_once()

    def test_button_text_shows_selection_count(self, sidebar_with_button):
        sidebar = sidebar_with_button
        sidebar.update_remove_button(3)

        sidebar.btn_remove_selected.set_text.assert_called_with("Remove Selected (3)")
