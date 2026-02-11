"""Tests for EmpireBuildQueueWindow (PROJ-76 Phase 2).

Verifies the empire-wide build queue window foundation:
- Window initialization and layout
- Source list population
- Row rendering and selection
- Close callback behavior
- Empty empire handling
"""
import pytest
from unittest.mock import MagicMock, patch, call

from game.strategy.data.build_queue_source import BuildQueueSource
from game.ui.screens.empire_build_queue_window import BatchAddResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_source(queue_id="planet_1_base", display_name="Alpha - Base",
                 context_type="planet", can_build_ships=False,
                 can_build_complexes=True, queue_items=None,
                 build_rate=None) -> BuildQueueSource:
    """Create a BuildQueueSource for testing."""
    # Default to standard per-resource rates for testing
    if build_rate is None:
        build_rate = {"Metals": 2000.0, "Organics": 2000.0, "Radioactives": 2000.0, "Vapors": 2000.0, "Exotics": 2000.0}
    return BuildQueueSource(
        queue_id=queue_id,
        display_name=display_name,
        owner_entity=MagicMock(),
        construction_queue=queue_items or [],
        can_build_ships=can_build_ships,
        can_build_complexes=can_build_complexes,
        context_type=context_type,
        build_rate=build_rate,
    )


def _make_window(sources=None, on_close=None, on_navigate=None):
    """Create an EmpireBuildQueueWindow with mocked pygame_gui.

    Bypasses UIWindow.__init__ to avoid needing real pygame display.
    Sets up minimal state for testing business logic.
    """
    from game.ui.screens.empire_build_queue_window import EmpireBuildQueueWindow

    if sources is None:
        sources = [
            _make_source("planet_1_base", "Alpha - Base", "planet"),
            _make_source("yard-001", "Alpha - Shipyard 1", "planet",
                         can_build_ships=True),
            _make_source("fleet_5", "Explorer Fleet - Space Yard", "fleet",
                         can_build_ships=True),
        ]

    mock_empire = MagicMock()
    mock_galaxy = MagicMock()

    with patch.object(EmpireBuildQueueWindow, '__init__',
                      lambda self, *a, **kw: None):
        win = EmpireBuildQueueWindow.__new__(EmpireBuildQueueWindow)

    # Set up minimal state matching constructor
    win.empire = mock_empire
    win.galaxy = mock_galaxy
    win.on_close_callback = on_close
    win.on_navigate_to_hex = on_navigate
    win.all_sources = list(sources)
    win.filtered_sources = list(sources)
    win.selected_source = None
    win.selected_index = -1
    win.row_height = 50
    win.header_height = 40
    win.sidebar_width = 300
    win.ui_manager = MagicMock()

    # Filter manager (owns columns and filter state)
    from game.ui.screens.empire_build_queue_filter_manager import BuildQueueFilterManager
    win._filter_mgr = BuildQueueFilterManager()
    # Expose as direct references for compatibility
    win.columns = win._filter_mgr.columns
    win.filter_location_type = win._filter_mgr.filter_location_type
    win.filter_status = win._filter_mgr.filter_status
    win.filter_capabilities = win._filter_mgr.filter_capabilities
    win.search_text = ""
    win.column_toggle_buttons = {}
    win.filter_toggle_buttons = {}
    win.search_entry = None

    # Multi-select state (Phase 6)
    win.selected_indices = set()

    # Mock UI elements
    win.scroll_bar = MagicMock()
    win.scroll_bar.start_percentage = 0.0
    win.scroll_bar.visible_percentage = 1.0
    win.list_panel = MagicMock()
    win.list_view_rect = MagicMock()
    win.list_view_rect.height = 500
    win.main_panel = MagicMock()
    win.header_container = MagicMock()
    win.sidebar_panel = MagicMock()
    win.row_elements = []
    win._header_labels = []

    return win


# =======================================================================
# Initialization Tests
# =======================================================================

class TestWindowInitialization:
    """EmpireBuildQueueWindow should initialize with correct state."""

    def test_window_stores_empire(self):
        """Window stores empire reference."""
        win = _make_window()
        assert win.empire is not None

    def test_window_stores_galaxy(self):
        """Window stores galaxy reference."""
        win = _make_window()
        assert win.galaxy is not None

    def test_window_stores_sources(self):
        """Window collects and stores build queue sources."""
        sources = [
            _make_source("p1", "Planet 1"),
            _make_source("p2", "Planet 2"),
        ]
        win = _make_window(sources=sources)
        assert len(win.all_sources) == 2
        assert win.all_sources[0].queue_id == "p1"
        assert win.all_sources[1].queue_id == "p2"

    def test_window_no_initial_selection(self):
        """Window starts with no row selected."""
        win = _make_window()
        assert win.selected_source is None
        assert win.selected_index == -1

    def test_window_stores_close_callback(self):
        """Window stores close callback."""
        cb = MagicMock()
        win = _make_window(on_close=cb)
        assert win.on_close_callback is cb

    def test_window_stores_navigate_callback(self):
        """Window stores navigate-to-hex callback."""
        cb = MagicMock()
        win = _make_window(on_navigate=cb)
        assert win.on_navigate_to_hex is cb


# =======================================================================
# Source Display Tests
# =======================================================================

class TestSourceDisplay:
    """Window should display build queue sources correctly."""

    def test_displays_all_sources(self):
        """All sources appear in filtered list initially."""
        sources = [
            _make_source("p1", "Alpha - Base"),
            _make_source("p2", "Beta - Shipyard 1"),
            _make_source("f1", "Fleet - Yard", "fleet"),
        ]
        win = _make_window(sources=sources)
        assert len(win.filtered_sources) == 3

    def test_source_names_accessible(self):
        """Display names are accessible from filtered sources."""
        sources = [_make_source("p1", "Alpha - Base")]
        win = _make_window(sources=sources)
        assert win.filtered_sources[0].display_name == "Alpha - Base"

    def test_empty_empire_shows_no_sources(self):
        """Window handles empire with no build queues gracefully."""
        win = _make_window(sources=[])
        assert len(win.all_sources) == 0
        assert len(win.filtered_sources) == 0


# =======================================================================
# Row Selection Tests
# =======================================================================

class TestRowSelection:
    """Window should handle row click selection."""

    def test_select_source_updates_selected(self):
        """Clicking a source row updates selected_source."""
        sources = [
            _make_source("p1", "Alpha - Base"),
            _make_source("p2", "Beta - Shipyard"),
        ]
        win = _make_window(sources=sources)
        win._select_source(1)
        assert win.selected_source is sources[1]
        assert win.selected_index == 1

    def test_select_first_source(self):
        """Can select the first source."""
        sources = [_make_source("p1", "Alpha")]
        win = _make_window(sources=sources)
        win._select_source(0)
        assert win.selected_source is sources[0]
        assert win.selected_index == 0

    def test_select_out_of_range_ignored(self):
        """Selecting an invalid index does not crash."""
        sources = [_make_source("p1", "Alpha")]
        win = _make_window(sources=sources)
        win._select_source(5)
        assert win.selected_source is None
        assert win.selected_index == -1

    def test_select_negative_index_ignored(self):
        """Selecting a negative index does not crash."""
        sources = [_make_source("p1", "Alpha")]
        win = _make_window(sources=sources)
        win._select_source(-1)
        assert win.selected_source is None
        assert win.selected_index == -1

    def test_reselect_same_source(self):
        """Selecting the same source again keeps selection."""
        sources = [_make_source("p1", "Alpha")]
        win = _make_window(sources=sources)
        win._select_source(0)
        win._select_source(0)
        assert win.selected_index == 0


# =======================================================================
# Close Callback Tests
# =======================================================================

class TestCloseCallback:
    """Window close should invoke callback."""

    def test_close_calls_callback(self):
        """kill() invokes on_close_callback."""
        cb = MagicMock()
        win = _make_window(on_close=cb)
        # Mock the parent kill to avoid real UIWindow teardown
        with patch('pygame_gui.elements.UIWindow.kill'):
            win.kill()
        cb.assert_called_once()

    def test_close_without_callback_no_crash(self):
        """kill() works when no callback is provided."""
        win = _make_window(on_close=None)
        with patch('pygame_gui.elements.UIWindow.kill'):
            win.kill()
        # No exception = success


# =======================================================================
# Queue Info Display Tests
# =======================================================================

class TestQueueInfoDisplay:
    """Window should format queue info for display."""

    def test_get_queue_summary_empty_queue(self):
        """Empty queue shows dash placeholder."""
        source = _make_source("p1", "Alpha", queue_items=[])
        win = _make_window(sources=[source])
        summary = win._get_queue_summary(source)
        assert summary == "-"

    def test_get_queue_summary_with_items(self):
        """Queue with items shows count."""
        items = [
            {"design_id": "frigate", "turns_remaining": 3},
            {"design_id": "destroyer", "turns_remaining": 5},
        ]
        source = _make_source("p1", "Alpha", queue_items=items)
        win = _make_window(sources=[source])
        summary = win._get_queue_summary(source)
        assert "2" in summary

    def test_get_capabilities_text_complexes_only(self):
        """Source that can only build complexes shows 'Complexes'."""
        source = _make_source(can_build_ships=False, can_build_complexes=True)
        win = _make_window(sources=[source])
        text = win._get_capabilities_text(source)
        assert text == "Complexes"

    def test_get_capabilities_text_ships_and_complexes(self):
        """Source that can build both shows 'Ships & Complexes'."""
        source = _make_source(can_build_ships=True, can_build_complexes=True)
        win = _make_window(sources=[source])
        text = win._get_capabilities_text(source)
        assert text == "Ships & Complexes"

    def test_get_capabilities_text_ships_only(self):
        """Source that can only build ships shows 'Ships'."""
        source = _make_source(can_build_ships=True, can_build_complexes=False)
        win = _make_window(sources=[source])
        text = win._get_capabilities_text(source)
        assert text == "Ships"

    def test_get_capabilities_text_none(self):
        """Source that can build neither shows 'None'."""
        source = _make_source(can_build_ships=False, can_build_complexes=False)
        win = _make_window(sources=[source])
        text = win._get_capabilities_text(source)
        assert text == "None"

    def test_get_first_item_text_empty_queue(self):
        """Empty queue returns dash."""
        source = _make_source(queue_items=[])
        win = _make_window(sources=[source])
        text = win._get_first_item_text(source)
        assert text == "-"

    def test_get_first_item_text_with_item(self):
        """Queue with items shows first design and turns."""
        items = [{"design_id": "frigate", "turns_remaining": 3}]
        source = _make_source(queue_items=items)
        win = _make_window(sources=[source])
        text = win._get_first_item_text(source)
        assert "frigate" in text
        assert "3" in text

    def test_get_queue_summary_single_item(self):
        """Queue with 1 item shows '1 item' (no plural)."""
        items = [{"design_id": "frigate", "turns_remaining": 3}]
        source = _make_source(queue_items=items)
        win = _make_window(sources=[source])
        summary = win._get_queue_summary(source)
        assert summary == "1 item"


# =======================================================================
# Column Configuration Tests (Phase 3)
# =======================================================================

class TestColumnConfiguration:
    """Column system should define configurable columns."""

    def test_columns_list_exists(self):
        """Window should have a columns list."""
        win = _make_window()
        assert hasattr(win, 'columns')
        assert isinstance(win.columns, list)
        assert len(win.columns) > 0

    def test_each_column_has_required_fields(self):
        """Each column must have id, width, title, visible."""
        win = _make_window()
        for col in win.columns:
            assert 'id' in col, f"Column missing 'id': {col}"
            assert 'width' in col, f"Column missing 'width': {col}"
            assert 'title' in col, f"Column missing 'title': {col}"
            assert 'visible' in col, f"Column missing 'visible': {col}"

    def test_expected_column_ids(self):
        """Columns should include all expected IDs."""
        win = _make_window()
        col_ids = {c['id'] for c in win.columns}
        expected = {
            'location', 'system', 'sector', 'queue_count',
            'first_item', 'turns_left', 'capabilities', 'build_rate',
            # Resource rate columns
            'res_metals_rate', 'res_organics_rate', 'res_vapors_rate',
            'res_radioactives_rate', 'res_exotics_rate',
            # Resource total columns
            'res_metals_total', 'res_organics_total', 'res_vapors_total',
            'res_radioactives_total', 'res_exotics_total',
        }
        assert expected.issubset(col_ids), f"Missing columns: {expected - col_ids}"

    def test_build_rate_visible_by_default(self):
        """Build rate column should be visible by default."""
        win = _make_window()
        col = next(c for c in win.columns if c['id'] == 'build_rate')
        assert col['visible'] is True

    def test_location_visible_by_default(self):
        """Location column should be visible by default."""
        win = _make_window()
        col = next(c for c in win.columns if c['id'] == 'location')
        assert col['visible'] is True


class TestGetVisibleColumns:
    """_get_visible_columns() should filter by visibility."""

    def test_returns_only_visible_columns(self):
        """Only columns with visible=True should be returned."""
        win = _make_window()
        visible = win._get_visible_columns()
        assert all(c['visible'] for c in visible)

    def test_hidden_columns_excluded(self):
        """Hidden columns should not appear in visible list."""
        win = _make_window()
        # Hide a column
        for c in win.columns:
            if c['id'] == 'capabilities':
                c['visible'] = False
        visible = win._get_visible_columns()
        visible_ids = {c['id'] for c in visible}
        assert 'capabilities' not in visible_ids

    def test_all_columns_visible_by_default(self):
        """All columns should be visible by default."""
        win = _make_window()
        visible = win._get_visible_columns()
        visible_ids = {c['id'] for c in visible}
        # All columns visible by default
        assert 'build_rate' in visible_ids
        assert 'location' in visible_ids
        assert 'queue_count' in visible_ids
        assert len(visible) == 18  # All 18 columns (8 original + 10 resource)


class TestGetColumnValue:
    """_get_column_value() should return correct display values."""

    def test_location_column(self):
        """Location column returns display_name."""
        source = _make_source(display_name="Alpha - Base")
        win = _make_window(sources=[source])
        assert win._get_column_value(source, 'location') == "Alpha - Base"

    def test_queue_count_column_empty(self):
        """Queue count column returns dash for empty queue."""
        source = _make_source(queue_items=[])
        win = _make_window(sources=[source])
        assert win._get_column_value(source, 'queue_count') == "-"

    def test_queue_count_column_with_items(self):
        """Queue count column returns count string."""
        items = [
            {"design_id": "frigate", "turns_remaining": 3},
            {"design_id": "destroyer", "turns_remaining": 5},
        ]
        source = _make_source(queue_items=items)
        win = _make_window(sources=[source])
        result = win._get_column_value(source, 'queue_count')
        assert "2" in result

    def test_first_item_column_empty(self):
        """First item column returns dash for empty queue."""
        source = _make_source(queue_items=[])
        win = _make_window(sources=[source])
        assert win._get_column_value(source, 'first_item') == "-"

    def test_first_item_column_with_item(self):
        """First item column returns design name."""
        items = [{"design_id": "cruiser", "turns_remaining": 8}]
        source = _make_source(queue_items=items)
        win = _make_window(sources=[source])
        result = win._get_column_value(source, 'first_item')
        assert "cruiser" in result

    def test_turns_left_column_empty(self):
        """Turns left column returns dash for empty queue."""
        source = _make_source(queue_items=[])
        win = _make_window(sources=[source])
        assert win._get_column_value(source, 'turns_left') == "-"

    def test_turns_left_column_with_item(self):
        """Turns left column returns turns remaining string."""
        items = [{"design_id": "frigate", "turns_remaining": 5}]
        source = _make_source(queue_items=items)
        win = _make_window(sources=[source])
        result = win._get_column_value(source, 'turns_left')
        assert "5" in result

    def test_capabilities_column(self):
        """Capabilities column returns correct text."""
        source = _make_source(can_build_ships=True, can_build_complexes=True)
        win = _make_window(sources=[source])
        assert win._get_column_value(source, 'capabilities') == "Ships & Complexes"

    def test_build_rate_column(self):
        """Build rate column returns rate string from source.build_rate."""
        source = _make_source()
        win = _make_window(sources=[source])
        result = win._get_column_value(source, 'build_rate')
        # Default build_rate is 2000, should display "2000/turn"
        assert result == "2000/turn"

    def test_unknown_column_returns_empty(self):
        """Unknown column ID returns empty string."""
        source = _make_source()
        win = _make_window(sources=[source])
        assert win._get_column_value(source, 'nonexistent') == ""

    def test_resource_rate_column_with_cost_per_tick(self):
        """Resource rate columns return formatted per-turn consumption."""
        items = [{"design_id": "cruiser", "cost_per_tick": {"Metals": 20.0}}]
        source = _make_source(queue_items=items)
        win = _make_window(sources=[source])
        # 20 per tick * 100 = 2000 per turn
        assert win._get_column_value(source, 'res_metals_rate') == "2,000"

    def test_resource_rate_column_empty_queue(self):
        """Resource rate column returns dash for empty queue."""
        source = _make_source(queue_items=[])
        win = _make_window(sources=[source])
        assert win._get_column_value(source, 'res_metals_rate') == "-"

    def test_resource_total_column_with_total_cost(self):
        """Resource total columns return formatted total cost."""
        items = [{"design_id": "cruiser", "total_cost": {"Organics": 5000}}]
        source = _make_source(queue_items=items)
        win = _make_window(sources=[source])
        assert win._get_column_value(source, 'res_organics_total') == "5k"

    def test_resource_total_column_empty_queue(self):
        """Resource total column returns dash for empty queue."""
        source = _make_source(queue_items=[])
        win = _make_window(sources=[source])
        assert win._get_column_value(source, 'res_vapors_total') == "-"


class TestColumnToggle:
    """Column visibility toggle should work correctly."""

    def test_toggle_column_hides_visible_column(self):
        """Toggling a visible column makes it invisible."""
        win = _make_window()
        # Verify location starts visible
        loc_col = next(c for c in win.columns if c['id'] == 'location')
        assert loc_col['visible'] is True

        result = win.toggle_column_visibility('location')
        assert result is True
        assert loc_col['visible'] is False

    def test_toggle_column_hides_visible_column(self):
        """Toggling a visible column makes it hidden."""
        win = _make_window()
        rate_col = next(c for c in win.columns if c['id'] == 'build_rate')
        assert rate_col['visible'] is True

        result = win.toggle_column_visibility('build_rate')
        assert result is True
        assert rate_col['visible'] is False

    def test_toggle_unknown_column_returns_false(self):
        """Toggling an unknown column ID returns False."""
        win = _make_window()
        result = win.toggle_column_visibility('nonexistent_column')
        assert result is False

    def test_toggle_affects_get_visible_columns(self):
        """Toggling a column changes _get_visible_columns() output."""
        win = _make_window()
        before = {c['id'] for c in win._get_visible_columns()}
        assert 'capabilities' in before

        win.toggle_column_visibility('capabilities')
        after = {c['id'] for c in win._get_visible_columns()}
        assert 'capabilities' not in after


# =======================================================================
# Filter State Tests (Phase 4)
# =======================================================================

class TestFilterState:
    """Window should initialize filter state correctly."""

    def test_filter_location_type_initialized(self):
        """Window has location type filter dict with both types True."""
        win = _make_window()
        assert hasattr(win, 'filter_location_type')
        assert win.filter_location_type == {'Planet': True, 'Fleet': True}

    def test_filter_status_initialized(self):
        """Window has queue status filter dict with both types True."""
        win = _make_window()
        assert hasattr(win, 'filter_status')
        assert win.filter_status == {'Active': True, 'Empty': True}

    def test_filter_capabilities_initialized(self):
        """Window has capabilities filter dict with both types True."""
        win = _make_window()
        assert hasattr(win, 'filter_capabilities')
        assert win.filter_capabilities == {'Ships': True, 'Complexes': True}

    def test_search_text_initialized(self):
        """Window has search_text initialized to empty string."""
        win = _make_window()
        assert hasattr(win, 'search_text')
        assert win.search_text == ""


# =======================================================================
# Location Type Filter Tests (Phase 4)
# =======================================================================

class TestLocationTypeFilter:
    """_filter_sources() should filter by location type."""

    def test_show_all_locations(self):
        """All sources shown when both types enabled."""
        sources = [
            _make_source("p1", "Planet Base", "planet"),
            _make_source("f1", "Fleet Yard", "fleet"),
        ]
        win = _make_window(sources=sources)
        win.filter_location_type = {'Planet': True, 'Fleet': True}
        result = win._filter_sources(sources)
        assert len(result) == 2

    def test_hide_fleet_sources(self):
        """Fleet sources hidden when Fleet filter disabled."""
        sources = [
            _make_source("p1", "Planet Base", "planet"),
            _make_source("f1", "Fleet Yard", "fleet"),
        ]
        win = _make_window(sources=sources)
        win.filter_location_type = {'Planet': True, 'Fleet': False}
        result = win._filter_sources(sources)
        assert len(result) == 1
        assert result[0].context_type == "planet"

    def test_hide_planet_sources(self):
        """Planet sources hidden when Planet filter disabled."""
        sources = [
            _make_source("p1", "Planet Base", "planet"),
            _make_source("f1", "Fleet Yard", "fleet"),
        ]
        win = _make_window(sources=sources)
        win.filter_location_type = {'Planet': False, 'Fleet': True}
        result = win._filter_sources(sources)
        assert len(result) == 1
        assert result[0].context_type == "fleet"

    def test_hide_all_locations_shows_empty(self):
        """Empty result when both location types disabled."""
        sources = [
            _make_source("p1", "Planet Base", "planet"),
            _make_source("f1", "Fleet Yard", "fleet"),
        ]
        win = _make_window(sources=sources)
        win.filter_location_type = {'Planet': False, 'Fleet': False}
        result = win._filter_sources(sources)
        assert len(result) == 0


# =======================================================================
# Queue Status Filter Tests (Phase 4)
# =======================================================================

class TestQueueStatusFilter:
    """_filter_sources() should filter by queue status."""

    def test_show_all_statuses(self):
        """All sources shown when both statuses enabled."""
        sources = [
            _make_source("p1", "Active Queue", queue_items=[
                {"design_id": "frigate", "turns_remaining": 3}
            ]),
            _make_source("p2", "Empty Queue", queue_items=[]),
        ]
        win = _make_window(sources=sources)
        win.filter_status = {'Active': True, 'Empty': True}
        result = win._filter_sources(sources)
        assert len(result) == 2

    def test_hide_empty_queues(self):
        """Empty queues hidden when Empty filter disabled."""
        sources = [
            _make_source("p1", "Active Queue", queue_items=[
                {"design_id": "frigate", "turns_remaining": 3}
            ]),
            _make_source("p2", "Empty Queue", queue_items=[]),
        ]
        win = _make_window(sources=sources)
        win.filter_status = {'Active': True, 'Empty': False}
        result = win._filter_sources(sources)
        assert len(result) == 1
        assert result[0].queue_id == "p1"

    def test_hide_active_queues(self):
        """Active queues hidden when Active filter disabled."""
        sources = [
            _make_source("p1", "Active Queue", queue_items=[
                {"design_id": "frigate", "turns_remaining": 3}
            ]),
            _make_source("p2", "Empty Queue", queue_items=[]),
        ]
        win = _make_window(sources=sources)
        win.filter_status = {'Active': False, 'Empty': True}
        result = win._filter_sources(sources)
        assert len(result) == 1
        assert result[0].queue_id == "p2"


# =======================================================================
# Capabilities Filter Tests (Phase 4)
# =======================================================================

class TestCapabilitiesFilter:
    """_filter_sources() should filter by build capabilities."""

    def test_show_all_capabilities(self):
        """All sources shown when both capabilities enabled."""
        sources = [
            _make_source("p1", "Ships Only", can_build_ships=True,
                         can_build_complexes=False),
            _make_source("p2", "Complexes Only", can_build_ships=False,
                         can_build_complexes=True),
        ]
        win = _make_window(sources=sources)
        win.filter_capabilities = {'Ships': True, 'Complexes': True}
        result = win._filter_sources(sources)
        assert len(result) == 2

    def test_hide_ship_builders(self):
        """Ship builders hidden when Ships filter disabled."""
        sources = [
            _make_source("p1", "Ships Only", can_build_ships=True,
                         can_build_complexes=False),
            _make_source("p2", "Complexes Only", can_build_ships=False,
                         can_build_complexes=True),
        ]
        win = _make_window(sources=sources)
        win.filter_capabilities = {'Ships': False, 'Complexes': True}
        result = win._filter_sources(sources)
        assert len(result) == 1
        assert result[0].queue_id == "p2"

    def test_hide_complex_builders(self):
        """Complex builders hidden when Complexes filter disabled."""
        sources = [
            _make_source("p1", "Ships Only", can_build_ships=True,
                         can_build_complexes=False),
            _make_source("p2", "Complexes Only", can_build_ships=False,
                         can_build_complexes=True),
        ]
        win = _make_window(sources=sources)
        win.filter_capabilities = {'Ships': True, 'Complexes': False}
        result = win._filter_sources(sources)
        assert len(result) == 1
        assert result[0].queue_id == "p1"

    def test_both_capabilities_source_shown_when_either_enabled(self):
        """Source building both ships+complexes is shown if either filter on."""
        sources = [
            _make_source("p1", "Both", can_build_ships=True,
                         can_build_complexes=True),
        ]
        win = _make_window(sources=sources)
        win.filter_capabilities = {'Ships': True, 'Complexes': False}
        result = win._filter_sources(sources)
        assert len(result) == 1

    def test_neither_capability_source_hidden_when_both_off(self):
        """Source with no capabilities hidden when both filters off."""
        sources = [
            _make_source("p1", "None", can_build_ships=False,
                         can_build_complexes=False),
        ]
        win = _make_window(sources=sources)
        win.filter_capabilities = {'Ships': False, 'Complexes': False}
        result = win._filter_sources(sources)
        assert len(result) == 0

    def test_neither_capability_source_shown_when_both_on(self):
        """Source with no capabilities is still shown when all filters enabled.

        A source that can build neither should appear when the user has all
        capability filters turned on (no filtering desired).
        """
        sources = [
            _make_source("p1", "None", can_build_ships=False,
                         can_build_complexes=False),
        ]
        win = _make_window(sources=sources)
        win.filter_capabilities = {'Ships': True, 'Complexes': True}
        result = win._filter_sources(sources)
        assert len(result) == 1


# =======================================================================
# Text Search Filter Tests (Phase 4)
# =======================================================================

class TestTextSearchFilter:
    """_filter_sources() should filter by text search on name."""

    def test_empty_search_shows_all(self):
        """Empty search text shows all sources."""
        sources = [
            _make_source("p1", "Alpha Base"),
            _make_source("p2", "Beta Shipyard"),
        ]
        win = _make_window(sources=sources)
        win.search_text = ""
        result = win._filter_sources(sources)
        assert len(result) == 2

    def test_search_by_name_substring(self):
        """Search matches display_name substring (case-insensitive)."""
        sources = [
            _make_source("p1", "Alpha Base"),
            _make_source("p2", "Beta Shipyard"),
        ]
        win = _make_window(sources=sources)
        win.search_text = "alpha"
        result = win._filter_sources(sources)
        assert len(result) == 1
        assert result[0].queue_id == "p1"

    def test_search_case_insensitive(self):
        """Search is case-insensitive."""
        sources = [
            _make_source("p1", "ALPHA Base"),
        ]
        win = _make_window(sources=sources)
        win.search_text = "alpha"
        result = win._filter_sources(sources)
        assert len(result) == 1

    def test_search_no_match(self):
        """Search with no matching sources returns empty."""
        sources = [
            _make_source("p1", "Alpha Base"),
        ]
        win = _make_window(sources=sources)
        win.search_text = "gamma"
        result = win._filter_sources(sources)
        assert len(result) == 0

    def test_search_matches_partial(self):
        """Partial text matches."""
        sources = [
            _make_source("p1", "Alpha Base"),
            _make_source("p2", "Alpha Shipyard"),
            _make_source("p3", "Beta Base"),
        ]
        win = _make_window(sources=sources)
        win.search_text = "alph"
        result = win._filter_sources(sources)
        assert len(result) == 2


# =======================================================================
# Combined Filter Tests (Phase 4)
# =======================================================================

class TestCombinedFilters:
    """Multiple filters should combine (AND logic)."""

    def test_location_and_status_combined(self):
        """Location type AND status filters combine."""
        sources = [
            _make_source("p1", "Planet Active", "planet", queue_items=[
                {"design_id": "frigate", "turns_remaining": 3}
            ]),
            _make_source("p2", "Planet Empty", "planet", queue_items=[]),
            _make_source("f1", "Fleet Active", "fleet", queue_items=[
                {"design_id": "cruiser", "turns_remaining": 5}
            ]),
        ]
        win = _make_window(sources=sources)
        win.filter_location_type = {'Planet': True, 'Fleet': False}
        win.filter_status = {'Active': True, 'Empty': False}
        result = win._filter_sources(sources)
        assert len(result) == 1
        assert result[0].queue_id == "p1"

    def test_all_filters_combined(self):
        """All four filters combine correctly."""
        sources = [
            _make_source("p1", "Alpha Base", "planet",
                         can_build_ships=False, can_build_complexes=True,
                         queue_items=[{"design_id": "mine", "turns_remaining": 2}]),
            _make_source("p2", "Beta Shipyard", "planet",
                         can_build_ships=True, can_build_complexes=True,
                         queue_items=[]),
            _make_source("f1", "Fleet Yard", "fleet",
                         can_build_ships=True, can_build_complexes=False,
                         queue_items=[{"design_id": "scout", "turns_remaining": 1}]),
        ]
        win = _make_window(sources=sources)
        win.filter_location_type = {'Planet': True, 'Fleet': True}
        win.filter_status = {'Active': True, 'Empty': False}
        win.filter_capabilities = {'Ships': False, 'Complexes': True}
        win.search_text = "alpha"
        result = win._filter_sources(sources)
        assert len(result) == 1
        assert result[0].queue_id == "p1"

    def test_apply_filters_updates_filtered_sources(self):
        """apply_filters() updates filtered_sources and refreshes list."""
        sources = [
            _make_source("p1", "Alpha", "planet"),
            _make_source("f1", "Fleet", "fleet"),
        ]
        win = _make_window(sources=sources)
        win._refresh_list = MagicMock()
        win.filter_location_type = {'Planet': True, 'Fleet': False}
        win.apply_filters()
        assert len(win.filtered_sources) == 1
        assert win.filtered_sources[0].context_type == "planet"
        win._refresh_list.assert_called_once()

    def test_apply_filters_resets_selection(self):
        """apply_filters() clears selection when filters change."""
        sources = [
            _make_source("p1", "Alpha", "planet"),
            _make_source("f1", "Fleet", "fleet"),
        ]
        win = _make_window(sources=sources)
        win._refresh_list = MagicMock()
        win._select_source(0)
        win.filter_location_type = {'Planet': True, 'Fleet': False}
        win.apply_filters()
        assert win.selected_source is None
        assert win.selected_index == -1


# =======================================================================
# Navigation Tests (Phase 5)
# =======================================================================

class TestGetHexForSource:
    """get_hex_for_source() should resolve hex coordinates."""

    def test_fleet_source_returns_fleet_location(self):
        """Fleet source returns fleet.location as hex coordinate."""
        from game.core.hex_math import HexCoord
        fleet_entity = MagicMock()
        fleet_entity.location = HexCoord(5, 3)
        source = BuildQueueSource(
            queue_id="fleet_1", display_name="Fleet Yard",
            owner_entity=fleet_entity, construction_queue=[],
            can_build_ships=True, can_build_complexes=True,
            context_type="fleet",
        )
        win = _make_window(sources=[source])
        result = win.get_hex_for_source(source)
        assert result == HexCoord(5, 3)

    def test_planet_source_returns_system_plus_planet_location(self):
        """Planet source returns system.global_location + planet.location."""
        from game.core.hex_math import HexCoord
        planet_entity = MagicMock()
        planet_entity.location = HexCoord(1, 0)
        system = MagicMock()
        system.global_location = HexCoord(10, 20)
        win = _make_window()
        win.galaxy = MagicMock()
        win.galaxy.get_system_of_planet.return_value = system
        source = BuildQueueSource(
            queue_id="planet_1_base", display_name="Alpha - Base",
            owner_entity=planet_entity, construction_queue=[],
            can_build_ships=False, can_build_complexes=True,
            context_type="planet",
        )
        result = win.get_hex_for_source(source)
        assert result == HexCoord(11, 20)

    def test_planet_source_no_system_returns_none(self):
        """Planet source returns None when system not found."""
        planet_entity = MagicMock()
        planet_entity.location = (1, 0)
        win = _make_window()
        win.galaxy = MagicMock()
        win.galaxy.get_system_of_planet.return_value = None
        source = BuildQueueSource(
            queue_id="planet_1_base", display_name="Alpha - Base",
            owner_entity=planet_entity, construction_queue=[],
            can_build_ships=False, can_build_complexes=True,
            context_type="planet",
        )
        result = win.get_hex_for_source(source)
        assert result is None

    def test_fleet_source_no_location_returns_none(self):
        """Fleet source returns None when fleet has no location."""
        fleet_entity = MagicMock(spec=[])
        source = BuildQueueSource(
            queue_id="fleet_1", display_name="Fleet Yard",
            owner_entity=fleet_entity, construction_queue=[],
            can_build_ships=True, can_build_complexes=True,
            context_type="fleet",
        )
        win = _make_window(sources=[source])
        result = win.get_hex_for_source(source)
        assert result is None

    def test_unknown_context_type_returns_none(self):
        """Unknown context_type returns None."""
        source = BuildQueueSource(
            queue_id="other_1", display_name="Other",
            owner_entity=MagicMock(), construction_queue=[],
            can_build_ships=False, can_build_complexes=False,
            context_type="unknown",
        )
        win = _make_window(sources=[source])
        result = win.get_hex_for_source(source)
        assert result is None


class TestNavigateToSource:
    """navigate_to_source() should call callback with hex coord and source."""

    def test_navigate_calls_callback_with_hex_and_source(self):
        """navigate_to_source() calls on_navigate_to_hex with (hex, source)."""
        from game.core.hex_math import HexCoord
        nav_cb = MagicMock()
        fleet_entity = MagicMock()
        fleet_entity.location = HexCoord(5, 3)
        source = BuildQueueSource(
            queue_id="fleet_1", display_name="Fleet Yard",
            owner_entity=fleet_entity, construction_queue=[],
            can_build_ships=True, can_build_complexes=True,
            context_type="fleet",
        )
        win = _make_window(sources=[source], on_navigate=nav_cb)
        win.navigate_to_source(source)
        nav_cb.assert_called_once_with(HexCoord(5, 3), source)

    def test_navigate_no_callback_does_not_crash(self):
        """navigate_to_source() is safe when no callback is set."""
        from game.core.hex_math import HexCoord
        fleet_entity = MagicMock()
        fleet_entity.location = HexCoord(5, 3)
        source = BuildQueueSource(
            queue_id="fleet_1", display_name="Fleet Yard",
            owner_entity=fleet_entity, construction_queue=[],
            can_build_ships=True, can_build_complexes=True,
            context_type="fleet",
        )
        win = _make_window(sources=[source], on_navigate=None)
        win.navigate_to_source(source)  # Should not raise

    def test_navigate_no_hex_does_not_call_callback(self):
        """navigate_to_source() does not call callback when hex is None."""
        nav_cb = MagicMock()
        planet_entity = MagicMock()
        planet_entity.location = (1, 0)
        source = BuildQueueSource(
            queue_id="planet_1_base", display_name="Alpha - Base",
            owner_entity=planet_entity, construction_queue=[],
            can_build_ships=False, can_build_complexes=True,
            context_type="planet",
        )
        win = _make_window(sources=[source], on_navigate=nav_cb)
        win.galaxy = MagicMock()
        win.galaxy.get_system_of_planet.return_value = None
        win.navigate_to_source(source)
        nav_cb.assert_not_called()

    def test_navigate_selects_source_before_callback(self):
        """navigate_to_source() selects the source before calling callback."""
        from game.core.hex_math import HexCoord
        nav_cb = MagicMock()
        fleet_entity = MagicMock()
        fleet_entity.location = HexCoord(5, 3)
        source = BuildQueueSource(
            queue_id="fleet_1", display_name="Fleet Yard",
            owner_entity=fleet_entity, construction_queue=[],
            can_build_ships=True, can_build_complexes=True,
            context_type="fleet",
        )
        win = _make_window(sources=[source], on_navigate=nav_cb)
        win.navigate_to_source(source)
        assert win.selected_source is source


class TestDoubleClickNavigation:
    """Double-clicking a row should trigger navigation."""

    def test_double_click_on_row_navigates(self):
        """Double-click on a list row calls navigate_to_source."""
        from game.core.hex_math import HexCoord
        nav_cb = MagicMock()
        fleet_entity = MagicMock()
        fleet_entity.location = HexCoord(5, 3)
        source = BuildQueueSource(
            queue_id="fleet_1", display_name="Fleet Yard",
            owner_entity=fleet_entity, construction_queue=[],
            can_build_ships=True, can_build_complexes=True,
            context_type="fleet",
        )
        win = _make_window(sources=[source], on_navigate=nav_cb)

        # First click selects (already tested in Phase 2)
        win._select_source(0)
        assert win.selected_source is source

        # Second click on same row triggers navigation
        # Simulate by calling navigate_to_source directly (event handler
        # will detect same-row click and call this)
        win.navigate_to_source(source)
        nav_cb.assert_called_once()

    def test_single_click_does_not_navigate(self):
        """Single click only selects, does not navigate."""
        nav_cb = MagicMock()
        source = _make_source("p1", "Alpha Base")
        win = _make_window(sources=[source], on_navigate=nav_cb)
        win._select_source(0)
        nav_cb.assert_not_called()

    def test_double_click_different_rows_does_not_navigate(self):
        """Clicking two different rows does not trigger navigation."""
        nav_cb = MagicMock()
        sources = [
            _make_source("p1", "Alpha Base"),
            _make_source("p2", "Beta Shipyard"),
        ]
        win = _make_window(sources=sources, on_navigate=nav_cb)
        win._select_source(0)
        win._select_source(1)
        nav_cb.assert_not_called()


# =======================================================================
# Multi-Select State Tests (Phase 6)
# =======================================================================

class TestMultiSelectState:
    """Multi-select should track a set of selected indices."""

    def test_selected_indices_initialized_empty(self):
        """Window starts with empty selected_indices set."""
        win = _make_window()
        assert hasattr(win, 'selected_indices')
        assert isinstance(win.selected_indices, set)
        assert len(win.selected_indices) == 0

    def test_single_click_sets_single_selection(self):
        """Single click sets selected_indices to just that index."""
        sources = [
            _make_source("p1", "Alpha"),
            _make_source("p2", "Beta"),
        ]
        win = _make_window(sources=sources)
        win.handle_row_click(1, ctrl_held=False)
        assert win.selected_indices == {1}

    def test_single_click_replaces_previous_selection(self):
        """Single click replaces any previous multi-selection."""
        sources = [
            _make_source("p1", "Alpha"),
            _make_source("p2", "Beta"),
            _make_source("p3", "Gamma"),
        ]
        win = _make_window(sources=sources)
        win.selected_indices = {0, 1}
        win.handle_row_click(2, ctrl_held=False)
        assert win.selected_indices == {2}

    def test_ctrl_click_adds_to_selection(self):
        """Ctrl+click adds index to existing selection."""
        sources = [
            _make_source("p1", "Alpha"),
            _make_source("p2", "Beta"),
            _make_source("p3", "Gamma"),
        ]
        win = _make_window(sources=sources)
        win.handle_row_click(0, ctrl_held=False)
        win.handle_row_click(2, ctrl_held=True)
        assert win.selected_indices == {0, 2}

    def test_ctrl_click_toggles_off_selected(self):
        """Ctrl+click on already-selected index removes it."""
        sources = [
            _make_source("p1", "Alpha"),
            _make_source("p2", "Beta"),
        ]
        win = _make_window(sources=sources)
        win.selected_indices = {0, 1}
        win.handle_row_click(0, ctrl_held=True)
        assert win.selected_indices == {1}

    def test_ctrl_click_on_only_selected_keeps_it(self):
        """Ctrl+click on the only selected item keeps it (prevent empty selection)."""
        sources = [_make_source("p1", "Alpha")]
        win = _make_window(sources=sources)
        win.selected_indices = {0}
        win.handle_row_click(0, ctrl_held=True)
        assert win.selected_indices == {0}

    def test_single_click_updates_selected_source(self):
        """Single click updates selected_source for backward compat."""
        sources = [
            _make_source("p1", "Alpha"),
            _make_source("p2", "Beta"),
        ]
        win = _make_window(sources=sources)
        win.handle_row_click(1, ctrl_held=False)
        assert win.selected_source is sources[1]
        assert win.selected_index == 1

    def test_multi_select_clears_selected_source(self):
        """Multiple selections clear single selected_source."""
        sources = [
            _make_source("p1", "Alpha"),
            _make_source("p2", "Beta"),
        ]
        win = _make_window(sources=sources)
        win.handle_row_click(0, ctrl_held=False)
        win.handle_row_click(1, ctrl_held=True)
        assert win.selected_source is None

    def test_handle_row_click_out_of_range_ignored(self):
        """Clicking out of range does nothing."""
        sources = [_make_source("p1", "Alpha")]
        win = _make_window(sources=sources)
        win.handle_row_click(5, ctrl_held=False)
        assert win.selected_indices == set()

    def test_get_selected_sources_returns_correct_sources(self):
        """get_selected_sources() returns BuildQueueSource list."""
        sources = [
            _make_source("p1", "Alpha"),
            _make_source("p2", "Beta"),
            _make_source("p3", "Gamma"),
        ]
        win = _make_window(sources=sources)
        win.selected_indices = {0, 2}
        result = win.get_selected_sources()
        assert len(result) == 2
        assert sources[0] in result
        assert sources[2] in result

    def test_get_selected_sources_empty_when_none_selected(self):
        """get_selected_sources() returns empty list when nothing selected."""
        win = _make_window()
        win.selected_indices = set()
        result = win.get_selected_sources()
        assert result == []

    def test_apply_filters_clears_selected_indices(self):
        """apply_filters() should clear the multi-select set."""
        sources = [
            _make_source("p1", "Alpha", "planet"),
            _make_source("f1", "Fleet", "fleet"),
        ]
        win = _make_window(sources=sources)
        win._refresh_list = MagicMock()
        win.selected_indices = {0, 1}
        win.apply_filters()
        assert win.selected_indices == set()


# =======================================================================
# Batch Add Tests (Phase 6)
# =======================================================================

class TestBatchAdd:
    """batch_add_to_selected() should add items to multiple queues."""

    def test_batch_add_to_single_selected_queue(self):
        """Adding an item to a single selected queue appends it."""
        source = _make_source("p1", "Alpha", can_build_ships=True,
                              can_build_complexes=True, queue_items=[])
        win = _make_window(sources=[source])
        win._refresh_list = MagicMock()
        win.selected_indices = {0}
        item = {"design_id": "frigate", "turns_remaining": 5}
        result = win.batch_add_to_selected(item, item_type="ship")
        assert result.added == 1
        assert result.skipped == 0
        assert len(source.construction_queue) == 1
        assert source.construction_queue[0]["design_id"] == "frigate"

    def test_batch_add_to_multiple_queues(self):
        """Adding an item to multiple selected queues adds to all."""
        sources = [
            _make_source("p1", "Alpha", can_build_ships=True, queue_items=[]),
            _make_source("p2", "Beta", can_build_ships=True, queue_items=[]),
            _make_source("p3", "Gamma", can_build_ships=True, queue_items=[]),
        ]
        win = _make_window(sources=sources)
        win._refresh_list = MagicMock()
        win.selected_indices = {0, 1, 2}
        item = {"design_id": "cruiser", "turns_remaining": 8}
        result = win.batch_add_to_selected(item, item_type="ship")
        assert result.added == 3
        assert result.skipped == 0

    def test_batch_add_skips_incompatible_queues_ships(self):
        """Queues that can't build ships are skipped for ship items."""
        sources = [
            _make_source("p1", "Alpha", can_build_ships=True, queue_items=[]),
            _make_source("p2", "Beta", can_build_ships=False,
                         can_build_complexes=True, queue_items=[]),
        ]
        win = _make_window(sources=sources)
        win._refresh_list = MagicMock()
        win.selected_indices = {0, 1}
        item = {"design_id": "frigate", "turns_remaining": 5}
        result = win.batch_add_to_selected(item, item_type="ship")
        assert result.added == 1
        assert result.skipped == 1
        assert len(sources[0].construction_queue) == 1
        assert len(sources[1].construction_queue) == 0

    def test_batch_add_skips_incompatible_queues_complexes(self):
        """Queues that can't build complexes are skipped for complex items."""
        sources = [
            _make_source("p1", "Alpha", can_build_ships=True,
                         can_build_complexes=False, queue_items=[]),
            _make_source("p2", "Beta", can_build_ships=False,
                         can_build_complexes=True, queue_items=[]),
        ]
        win = _make_window(sources=sources)
        win._refresh_list = MagicMock()
        win.selected_indices = {0, 1}
        item = {"design_id": "mining_station", "turns_remaining": 3}
        result = win.batch_add_to_selected(item, item_type="complex")
        assert result.added == 1
        assert result.skipped == 1
        assert len(sources[0].construction_queue) == 0
        assert len(sources[1].construction_queue) == 1

    def test_batch_add_no_selection_returns_zero(self):
        """Batch add with no selection adds nothing."""
        sources = [_make_source("p1", "Alpha", can_build_ships=True, queue_items=[])]
        win = _make_window(sources=sources)
        win._refresh_list = MagicMock()
        win.selected_indices = set()
        item = {"design_id": "frigate", "turns_remaining": 5}
        result = win.batch_add_to_selected(item, item_type="ship")
        assert result.added == 0
        assert result.skipped == 0

    def test_batch_add_preserves_existing_queue_items(self):
        """Batch add appends to existing queue, doesn't replace."""
        existing = [{"design_id": "scout", "turns_remaining": 2}]
        source = _make_source("p1", "Alpha", can_build_ships=True,
                              queue_items=existing)
        win = _make_window(sources=[source])
        win._refresh_list = MagicMock()
        win.selected_indices = {0}
        item = {"design_id": "frigate", "turns_remaining": 5}
        win.batch_add_to_selected(item, item_type="ship")
        assert len(source.construction_queue) == 2
        assert source.construction_queue[0]["design_id"] == "scout"
        assert source.construction_queue[1]["design_id"] == "frigate"

    def test_batch_add_unknown_type_skips_all(self):
        """Unknown item_type is treated as incompatible with all queues."""
        source = _make_source("p1", "Alpha", can_build_ships=True,
                              can_build_complexes=True, queue_items=[])
        win = _make_window(sources=[source])
        win._refresh_list = MagicMock()
        win.selected_indices = {0}
        item = {"design_id": "frigate", "turns_remaining": 5}
        result = win.batch_add_to_selected(item, item_type="unknown")
        assert result.added == 0
        assert result.skipped == 1

    def test_get_selection_summary_single(self):
        """Selection summary for single queue shows name."""
        sources = [_make_source("p1", "Alpha Base")]
        win = _make_window(sources=sources)
        win.selected_indices = {0}
        summary = win.get_selection_summary()
        assert "1" in summary
        assert "Alpha Base" in summary

    def test_get_selection_summary_multiple(self):
        """Selection summary for multiple queues shows count."""
        sources = [
            _make_source("p1", "Alpha"),
            _make_source("p2", "Beta"),
        ]
        win = _make_window(sources=sources)
        win.selected_indices = {0, 1}
        summary = win.get_selection_summary()
        assert "2" in summary

    def test_get_selection_summary_none(self):
        """Selection summary with nothing selected."""
        win = _make_window()
        win.selected_indices = set()
        summary = win.get_selection_summary()
        assert "0" in summary or "No" in summary or "none" in summary.lower()


# =======================================================================
# Process Event Tests (PROJ-98 Phase 1)
# =======================================================================

class TestProcessEvent:
    """process_event() should dispatch pygame_gui button events correctly."""

    def test_column_toggle_button_click_toggles_visibility(self):
        """Clicking a column toggle button toggles that column's visibility."""
        import pygame_gui
        from pygame_gui.elements import UIWindow

        win = _make_window()
        # Create mock column toggle button
        mock_btn = MagicMock()
        mock_btn.set_text = MagicMock()
        win.column_toggle_buttons = {'location': mock_btn}
        # Initially visible
        for col in win.columns:
            if col['id'] == 'location':
                col['visible'] = True
                break
        # Mock UI rebuild methods
        win._build_header_labels = MagicMock()
        win._refresh_list = MagicMock()

        # Create pygame_gui UI_BUTTON_PRESSED event
        event = MagicMock()
        event.type = pygame_gui.UI_BUTTON_PRESSED
        event.ui_element = mock_btn

        # Mock parent process_event to avoid UIWindow attribute errors
        with patch.object(UIWindow, 'process_event', return_value=False):
            win.process_event(event)

        # Column should now be invisible
        col = next(c for c in win.columns if c['id'] == 'location')
        assert col['visible'] is False
        # Button text should be updated
        mock_btn.set_text.assert_called()
        # Display should be rebuilt
        win._build_header_labels.assert_called()
        win._refresh_list.assert_called()

    def test_filter_toggle_button_click_toggles_filter(self):
        """Clicking a filter toggle button toggles that filter's state."""
        import pygame_gui
        from pygame_gui.elements import UIWindow

        win = _make_window()
        # Create mock filter toggle button
        mock_btn = MagicMock()
        mock_btn.set_text = MagicMock()
        win.filter_toggle_buttons = {'loc_Planet': mock_btn}
        win.filter_location_type = {'Planet': True, 'Fleet': True}
        # Mock apply_filters
        win.apply_filters = MagicMock()

        event = MagicMock()
        event.type = pygame_gui.UI_BUTTON_PRESSED
        event.ui_element = mock_btn

        # Mock parent process_event to avoid UIWindow attribute errors
        with patch.object(UIWindow, 'process_event', return_value=False):
            win.process_event(event)

        # Filter should now be False
        assert win.filter_location_type['Planet'] is False
        # Button text should be updated
        mock_btn.set_text.assert_called()
        # Filters should be re-applied
        win.apply_filters.assert_called()

    def test_apply_filters_button_click_reads_search_and_applies(self):
        """Clicking Apply Filters button reads search text and applies filters."""
        import pygame_gui
        from pygame_gui.elements import UIWindow

        win = _make_window()
        # Create mock apply button
        mock_btn = MagicMock()
        win.btn_apply_filters = mock_btn
        # Create mock search entry
        win.search_entry = MagicMock()
        win.search_entry.get_text = MagicMock(return_value="frigate")
        win.apply_filters = MagicMock()

        event = MagicMock()
        event.type = pygame_gui.UI_BUTTON_PRESSED
        event.ui_element = mock_btn

        # Mock parent process_event to avoid UIWindow attribute errors
        with patch.object(UIWindow, 'process_event', return_value=False):
            result = win.process_event(event)

        # Search text should be read
        assert win.search_text == "frigate"
        # Filters should be applied
        win.apply_filters.assert_called()
        # Should return True (event handled)
        assert result is True

    def test_unrecognized_button_click_does_not_crash(self):
        """Clicking an unrecognized button doesn't crash or throw errors."""
        import pygame_gui
        from pygame_gui.elements import UIWindow

        win = _make_window()
        win.column_toggle_buttons = {}
        win.filter_toggle_buttons = {}
        win._build_header_labels = MagicMock()
        win._refresh_list = MagicMock()

        # Create event with unknown button
        unknown_btn = MagicMock()
        event = MagicMock()
        event.type = pygame_gui.UI_BUTTON_PRESSED
        event.ui_element = unknown_btn

        # Mock parent process_event to avoid UIWindow attribute errors
        with patch.object(UIWindow, 'process_event', return_value=False):
            # Should not crash
            win.process_event(event)
