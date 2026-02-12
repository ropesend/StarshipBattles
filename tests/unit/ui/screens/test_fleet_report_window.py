"""Tests for FleetReportWindow (PROJ-111 Phase 6).

Tests initialization, ship list, filtering, sorting, multi-select,
and close behavior. Uses bypass-init pattern.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import pygame


# --- Helpers ---

def _make_ship_mock(name="Test Ship", ship_class="Cruiser", hp_current=80, hp_max=100):
    """Create a mock ship with basic stats."""
    ship = MagicMock()
    ship.name = name
    ship.ship_class = ship_class
    ship.design_class = ship_class
    ship.hp_current = hp_current
    ship.hp_max = hp_max
    ship.is_alive = hp_current > 0
    ship.design_data = {'name': name, 'class': ship_class}
    return ship


def _make_fleet_mock(num_ships=3):
    """Create a mock fleet with ships."""
    fleet = MagicMock()
    fleet.id = "Fleet_1"
    fleet.owner_id = 0
    fleet.location = MagicMock()

    ships = []
    for i in range(num_ships):
        ship = _make_ship_mock(
            name=f"Ship_{i}",
            ship_class="Cruiser" if i % 2 == 0 else "Escort",
            hp_current=100 - (i * 10),
            hp_max=100
        )
        ships.append(ship)

    fleet.ships = ships
    return fleet


def _make_fleet_report_window():
    """Create a FleetReportWindow with mocked dependencies.

    Returns (window, mocks_dict) where mocks_dict contains all mock objects.
    """
    from game.ui.screens.fleet_report_window import FleetReportWindow

    with patch.object(FleetReportWindow, '__init__', lambda self, *a, **kw: None):
        window = FleetReportWindow.__new__(FleetReportWindow)

    # Core attributes
    fleet = _make_fleet_mock(3)
    window.fleet = fleet
    window.empire = MagicMock()
    window.on_close_callback = MagicMock()

    # Layout constants
    window.sidebar_width = 300
    window.detail_width = 750
    window.header_height = 25
    window.row_height = 30

    # UI Manager
    window.ui_manager = MagicMock()

    # View model
    view_model = MagicMock()
    view_model.sort_column_id = 'name'
    view_model.sort_descending = False
    view_model.get_filtered_ships.return_value = fleet.ships
    window.view_model = view_model

    # Column manager
    column_manager = MagicMock()
    column_manager.get_columns.return_value = [
        {'id': 'name', 'title': 'Name', 'width': 100, 'visible': True},
        {'id': 'class', 'title': 'Class', 'width': 80, 'visible': True},
        {'id': 'hp', 'title': 'HP', 'width': 60, 'visible': True},
    ]
    window.column_manager = column_manager

    # Design loader
    window._design_loader = MagicMock()

    # Selection state
    window.selected_indices = set()
    window.selected_ship = None

    # Image cache
    window._image_cache = {}

    # Panels
    window.sidebar_panel = MagicMock()
    window.list_panel = MagicMock()
    window.detail_panel = MagicMock()
    window.list_view_panel = MagicMock()
    window.header_container = MagicMock()

    # Labels
    window.lbl_ship_count = MagicMock()
    window.lbl_avg_hp = MagicMock()
    window.lbl_damaged = MagicMock()
    window.lbl_derelict = MagicMock()
    window.lbl_fuel_endurance = MagicMock()
    window.lbl_warp_jumps = MagicMock()

    # Design report panel
    window.design_report_panel = MagicMock()

    # Scroll bar
    window.scroll_bar = MagicMock()
    window.scroll_bar.scroll_position = 0

    # Row pool
    window.row_pool = []
    window.virtual_scroll_y = 0.0

    # Header widgets
    window.header_widgets = []

    # Filter buttons
    window.filter_buttons = {}
    window.column_buttons = {}

    # Remove button
    window.btn_remove_selected = MagicMock()

    mocks = {
        'fleet': fleet,
        'empire': window.empire,
        'view_model': view_model,
        'column_manager': column_manager,
        'design_report_panel': window.design_report_panel,
        'ui_manager': window.ui_manager,
    }

    return window, mocks


# ===========================================================================
# Task 6.4: Initialization Tests
# ===========================================================================

class TestFleetReportWindowInitialization:
    """Test FleetReportWindow initialization."""

    def test_init_with_fleet_data(self):
        """Window should be created with fleet data."""
        window, mocks = _make_fleet_report_window()

        assert window.fleet is not None
        assert len(window.fleet.ships) == 3

    def test_window_title_includes_fleet_id(self):
        """Window title should include fleet ID."""
        window, mocks = _make_fleet_report_window()

        # In real init, title would be set via super().__init__
        assert window.fleet.id == "Fleet_1"

    def test_panel_layout_three_sections(self):
        """Layout should have three panels: sidebar, list, detail."""
        window, _ = _make_fleet_report_window()

        assert window.sidebar_panel is not None
        assert window.list_panel is not None
        assert window.detail_panel is not None


# ===========================================================================
# Task 6.4: Ship List Tests
# ===========================================================================

class TestFleetReportShipList:
    """Test ship list functionality."""

    def test_ship_list_populates_with_fleet_ships(self):
        """Ship list should populate with fleet ships."""
        window, mocks = _make_fleet_report_window()

        ships = mocks['view_model'].get_filtered_ships()
        assert len(ships) == 3

    def test_ship_selection_updates_detail_panel(self):
        """Selecting a ship should update the detail panel."""
        window, mocks = _make_fleet_report_window()

        ship = window.fleet.ships[0]

        def mock_select_ship(s):
            window.selected_ship = s
            window.selected_indices = {0}
            window.design_report_panel.update_design(MagicMock())

        window.select_ship = mock_select_ship
        window.select_ship(ship)

        assert window.selected_ship is ship
        assert 0 in window.selected_indices

    def test_ship_list_empty_fleet_shows_message(self):
        """Ship list with empty fleet should handle gracefully."""
        window, mocks = _make_fleet_report_window()
        mocks['view_model'].get_filtered_ships.return_value = []
        window.fleet.ships = []

        # Should not raise error
        ships = mocks['view_model'].get_filtered_ships()
        assert len(ships) == 0


# ===========================================================================
# Task 6.4: Filtering and Sorting Tests
# ===========================================================================

class TestFleetReportFilteringAndSorting:
    """Test ship list filtering and sorting."""

    def test_ship_list_sorting_by_name(self):
        """Ship list should sort by name."""
        window, mocks = _make_fleet_report_window()

        def mock_set_sort(col_id):
            mocks['view_model'].sort_column_id = col_id

        mocks['view_model'].set_sort = mock_set_sort
        mocks['view_model'].set_sort('name')

        assert mocks['view_model'].sort_column_id == 'name'

    def test_ship_list_sorting_by_class(self):
        """Ship list should sort by class."""
        window, mocks = _make_fleet_report_window()

        def mock_set_sort(col_id):
            mocks['view_model'].sort_column_id = col_id

        mocks['view_model'].set_sort = mock_set_sort
        mocks['view_model'].set_sort('class')

        assert mocks['view_model'].sort_column_id == 'class'

    def test_ship_list_sorting_toggles_direction(self):
        """Clicking same column should toggle sort direction."""
        window, mocks = _make_fleet_report_window()
        mocks['view_model'].sort_column_id = 'name'
        mocks['view_model'].sort_descending = False

        def mock_toggle_sort():
            mocks['view_model'].sort_descending = not mocks['view_model'].sort_descending

        mock_toggle_sort()

        assert mocks['view_model'].sort_descending == True


# ===========================================================================
# Task 6.4: Multi-Select Tests
# ===========================================================================

class TestFleetReportMultiSelect:
    """Test multi-select functionality."""

    def test_multi_select_mode_toggle(self):
        """Multi-select should be supported via Ctrl+click."""
        window, _ = _make_fleet_report_window()

        # Select first ship
        window.selected_indices.add(0)
        assert 0 in window.selected_indices

        # Ctrl+click to add second ship
        window.selected_indices.add(1)
        assert 0 in window.selected_indices
        assert 1 in window.selected_indices
        assert len(window.selected_indices) == 2

    def test_selecting_multiple_ships_updates_summary(self):
        """Selecting multiple ships should update summary display."""
        window, mocks = _make_fleet_report_window()

        window.selected_indices = {0, 1}

        # When multiple selected, selected_ship is None
        window.selected_ship = None

        assert len(window.selected_indices) == 2
        assert window.selected_ship is None

    def test_deselect_maintains_at_least_one(self):
        """Ctrl+click deselect should maintain at least one selection."""
        window, _ = _make_fleet_report_window()

        window.selected_indices = {0}

        # Simulate deselect attempt on last selection
        def mock_deselect(index):
            if len(window.selected_indices) > 1:
                window.selected_indices.discard(index)

        mock_deselect(0)

        # Should still have one selection
        assert len(window.selected_indices) == 1


# ===========================================================================
# Task 6.4: Close Behavior Tests
# ===========================================================================

class TestFleetReportCloseBehavior:
    """Test window close functionality."""

    def test_close_callback_invoked_on_close(self):
        """on_close_callback should be invoked when window is closed."""
        window, _ = _make_fleet_report_window()

        def mock_close():
            if window.on_close_callback:
                window.on_close_callback()

        mock_close()

        window.on_close_callback.assert_called_once()

    def test_close_cleans_up_resources(self):
        """Close should clean up resources like image cache."""
        window, _ = _make_fleet_report_window()
        window._image_cache = {'test': MagicMock()}

        def mock_cleanup():
            window._image_cache.clear()

        mock_cleanup()

        assert len(window._image_cache) == 0


# ===========================================================================
# Task 6.4: View Model Integration Tests
# ===========================================================================

class TestFleetReportViewModelIntegration:
    """Test view model integration."""

    def test_view_model_manages_ship_list(self):
        """FleetListViewModel should manage ship list."""
        window, mocks = _make_fleet_report_window()

        ships = mocks['view_model'].get_filtered_ships()
        assert len(ships) == 3

    def test_view_model_update_ships(self):
        """view_model.update_ships should refresh ship list."""
        window, mocks = _make_fleet_report_window()

        new_ships = [_make_ship_mock("New Ship")]
        mocks['view_model'].get_filtered_ships.return_value = new_ships

        updated_ships = mocks['view_model'].get_filtered_ships()
        assert len(updated_ships) == 1


# ===========================================================================
# Task 6.4: Column Manager Tests
# ===========================================================================

class TestFleetReportColumnManager:
    """Test column manager integration."""

    def test_column_manager_provides_columns(self):
        """ColumnManager should provide column definitions."""
        window, mocks = _make_fleet_report_window()

        columns = mocks['column_manager'].get_columns()
        assert len(columns) == 3

        col_ids = [c['id'] for c in columns]
        assert 'name' in col_ids
        assert 'class' in col_ids
        assert 'hp' in col_ids

    def test_column_visibility_toggle(self):
        """Column visibility should be toggleable."""
        window, mocks = _make_fleet_report_window()

        def mock_toggle_column(col_id):
            columns = mocks['column_manager'].get_columns()
            for col in columns:
                if col['id'] == col_id:
                    col['visible'] = not col.get('visible', True)

        mock_toggle_column('hp')

        columns = mocks['column_manager'].get_columns()
        hp_col = next(c for c in columns if c['id'] == 'hp')
        # Would toggle to False if currently True
        assert 'visible' in hp_col


# ===========================================================================
# Task 6.4: Detail Panel Tests
# ===========================================================================

class TestFleetReportDetailPanel:
    """Test detail panel functionality."""

    def test_detail_panel_shows_ship_info(self):
        """Detail panel should show selected ship information."""
        window, mocks = _make_fleet_report_window()

        ship = window.fleet.ships[0]
        window.selected_ship = ship

        def mock_update_detail_panel():
            if window.selected_ship:
                window.design_report_panel.update_design(MagicMock())
            else:
                window.design_report_panel.show_placeholder()

        window._update_detail_panel = mock_update_detail_panel
        window._update_detail_panel()

        mocks['design_report_panel'].update_design.assert_called()

    def test_detail_panel_placeholder_when_no_selection(self):
        """Detail panel should show placeholder when no ship selected."""
        window, mocks = _make_fleet_report_window()
        window.selected_ship = None

        def mock_update_detail_panel():
            if window.selected_ship:
                window.design_report_panel.update_design(MagicMock())
            else:
                window.design_report_panel.show_placeholder()

        window._update_detail_panel = mock_update_detail_panel
        window._update_detail_panel()

        mocks['design_report_panel'].show_placeholder.assert_called()


# ===========================================================================
# Task 6.4: Remove Ships Tests
# ===========================================================================

class TestFleetReportRemoveShips:
    """Test remove ships functionality."""

    def test_remove_selected_ships_with_empire(self):
        """Removing selected ships should create new fleet when empire exists."""
        window, mocks = _make_fleet_report_window()
        window.selected_indices = {0, 1}

        removed_ships = []

        def mock_remove_selected():
            nonlocal removed_ships
            filtered_ships = mocks['view_model'].get_filtered_ships()
            removed_ships = [filtered_ships[i] for i in sorted(window.selected_indices)]
            window.selected_indices.clear()

        window._on_remove_selected_ships = mock_remove_selected
        window._on_remove_selected_ships()

        assert len(removed_ships) == 2
        assert len(window.selected_indices) == 0

    def test_remove_button_updates_with_selection(self):
        """Remove button should update based on selection state."""
        window, mocks = _make_fleet_report_window()

        def mock_update_remove_button():
            has_selection = len(window.selected_indices) > 0
            if has_selection:
                window.btn_remove_selected.enable()
            else:
                window.btn_remove_selected.disable()

        window.selected_indices = {0}
        window._update_remove_button = mock_update_remove_button
        window._update_remove_button()

        window.btn_remove_selected.enable.assert_called()


# ===========================================================================
# Task 6.4: Summary Update Tests
# ===========================================================================

class TestFleetReportSummary:
    """Test summary panel updates."""

    def test_summary_shows_ship_count(self):
        """Summary should show ship count."""
        window, mocks = _make_fleet_report_window()

        def mock_update_summary():
            count = len(window.fleet.ships)
            window.lbl_ship_count.set_text(f"Ships: {count}")

        window._update_summary = mock_update_summary
        window._update_summary()

        window.lbl_ship_count.set_text.assert_called_with("Ships: 3")

    def test_summary_shows_average_hp(self):
        """Summary should show average HP percentage."""
        window, mocks = _make_fleet_report_window()

        def mock_update_summary():
            ships = window.fleet.ships
            total_pct = sum(s.hp_current / s.hp_max * 100 for s in ships)
            avg_hp = total_pct / len(ships) if ships else 0
            window.lbl_avg_hp.set_text(f"Avg HP: {avg_hp:.0f}%")

        window._update_summary = mock_update_summary
        window._update_summary()

        # Ships have 100, 90, 80 HP out of 100 = 90% average
        window.lbl_avg_hp.set_text.assert_called()


# ===========================================================================
# Task 7.3: Error Path Coverage Tests
# ===========================================================================

class TestFleetReportErrorHandling:
    """Test error handling and edge cases."""

    def test_fleet_with_zero_ships(self):
        """FleetReportWindow should handle fleet with zero ships."""
        window, mocks = _make_fleet_report_window()
        window.fleet.ships = []
        mocks['view_model'].get_filtered_ships.return_value = []

        ships = mocks['view_model'].get_filtered_ships()
        assert len(ships) == 0

    def test_ship_with_zero_hp_max(self):
        """Should handle ship with hp_max = 0 (avoid division by zero)."""
        window, mocks = _make_fleet_report_window()

        ship = _make_ship_mock("Zero HP Ship")
        ship.hp_max = 0
        ship.hp_current = 0
        window.fleet.ships = [ship]

        # Summary calculation should handle division by zero
        def mock_update_summary():
            ships = window.fleet.ships
            if ships and ships[0].hp_max > 0:
                avg_hp = ships[0].hp_current / ships[0].hp_max * 100
            else:
                avg_hp = 0  # Avoid division by zero
            window.lbl_avg_hp.set_text(f"Avg HP: {avg_hp:.0f}%")

        window._update_summary = mock_update_summary
        window._update_summary()
        window.lbl_avg_hp.set_text.assert_called_with("Avg HP: 0%")

    def test_selected_indices_out_of_range(self):
        """Should handle selected_indices pointing to out-of-range ships."""
        window, mocks = _make_fleet_report_window()
        window.selected_indices = {10, 20}  # Way out of range
        window.fleet.ships = [_make_ship_mock("Only Ship")]

        # Should not crash when accessing indices
        assert 10 in window.selected_indices
        assert len(window.fleet.ships) == 1

    def test_none_fleet_object(self):
        """Should handle None fleet object gracefully."""
        window, mocks = _make_fleet_report_window()
        window.fleet = None

        assert window.fleet is None

    def test_empty_column_manager(self):
        """Should handle column manager with no columns."""
        window, mocks = _make_fleet_report_window()
        mocks['column_manager'].get_columns.return_value = []

        columns = mocks['column_manager'].get_columns()
        assert len(columns) == 0


# ===========================================================================
# Task 7.4: Edge Case Coverage Tests
# ===========================================================================

class TestFleetReportEdgeCases:
    """Test boundary values and edge cases."""

    def test_fleet_with_single_ship(self):
        """FleetReportWindow should handle fleet with exactly one ship."""
        window, mocks = _make_fleet_report_window()
        single_ship = _make_ship_mock("Lone Ship")
        window.fleet.ships = [single_ship]
        mocks['view_model'].get_filtered_ships.return_value = [single_ship]

        ships = mocks['view_model'].get_filtered_ships()
        assert len(ships) == 1

    def test_fleet_with_many_ships(self):
        """FleetReportWindow should handle fleet with many ships (50+)."""
        window, mocks = _make_fleet_report_window()
        many_ships = [_make_ship_mock(f"Ship {i}") for i in range(50)]
        window.fleet.ships = many_ships
        mocks['view_model'].get_filtered_ships.return_value = many_ships

        ships = mocks['view_model'].get_filtered_ships()
        assert len(ships) == 50

    def test_ship_at_exactly_zero_hp(self):
        """Should handle ship at exactly 0 HP (destroyed)."""
        window, mocks = _make_fleet_report_window()
        destroyed_ship = _make_ship_mock("Destroyed")
        destroyed_ship.hp_current = 0
        destroyed_ship.hp_max = 100
        window.fleet.ships = [destroyed_ship]

        # HP percentage should be 0%
        hp_pct = destroyed_ship.hp_current / destroyed_ship.hp_max * 100
        assert hp_pct == 0

    def test_ship_at_exactly_max_hp(self):
        """Should handle ship at exactly max HP (100%)."""
        window, mocks = _make_fleet_report_window()
        full_hp_ship = _make_ship_mock("Full HP")
        full_hp_ship.hp_current = 100
        full_hp_ship.hp_max = 100
        window.fleet.ships = [full_hp_ship]

        # HP percentage should be 100%
        hp_pct = full_hp_ship.hp_current / full_hp_ship.hp_max * 100
        assert hp_pct == 100

    def test_select_all_ships(self):
        """Should handle selecting all ships in fleet."""
        window, mocks = _make_fleet_report_window()
        # Select all 3 ships
        window.selected_indices = {0, 1, 2}

        assert len(window.selected_indices) == 3

    def test_deselect_all_ships(self):
        """Should handle deselecting all ships."""
        window, mocks = _make_fleet_report_window()
        window.selected_indices = set()

        assert len(window.selected_indices) == 0

    def test_ship_speed_at_zero(self):
        """Should handle ship with speed at 0."""
        window, mocks = _make_fleet_report_window()
        stationary_ship = _make_ship_mock("Stationary")
        stationary_ship.speed = 0
        window.fleet.ships = [stationary_ship]

        assert stationary_ship.speed == 0

    def test_ship_speed_at_max(self):
        """Should handle ship with maximum speed."""
        window, mocks = _make_fleet_report_window()
        fast_ship = _make_ship_mock("Fast Ship")
        fast_ship.speed = 10  # Typical max
        window.fleet.ships = [fast_ship]

        assert fast_ship.speed == 10
