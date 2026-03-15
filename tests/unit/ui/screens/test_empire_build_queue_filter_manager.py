"""Unit tests for empire_build_queue_filter_manager.py.

Tests the BuildQueueFilterManager class which manages filter state,
column visibility, and filter predicates for the Empire Build Queue Window.

Created as part of PROJ-89 Phase 3.
PROJ-220 Phase 4: Updated for tri-state FilterState API.
"""
import pytest
from unittest.mock import MagicMock

from game.ui.filters.filter_state import FilterState
from game.ui.screens.empire_build_queue_filter_manager import (
    BuildQueueFilterManager,
    DEFAULT_COLUMNS,
    NUMERIC_COLUMNS,
)


def _make_source(
    display_name: str = "Test Source",
    context_type: str = "planet",
    construction_queue: list | None = None,
    can_build_ships: bool = True,
    can_build_complexes: bool = True,
) -> MagicMock:
    """Create a mock BuildQueueSource for testing.

    Args:
        display_name: Name shown in the queue list.
        context_type: 'planet' or 'fleet'.
        construction_queue: Queue contents (empty list by default).
        can_build_ships: Whether source can build ships.
        can_build_complexes: Whether source can build complexes.

    Returns:
        Mock BuildQueueSource with specified attributes.
    """
    source = MagicMock()
    source.display_name = display_name
    source.context_type = context_type
    source.construction_queue = construction_queue if construction_queue is not None else []
    source.can_build_ships = can_build_ships
    source.can_build_complexes = can_build_complexes
    return source


class TestFilterManagerInit:
    """Tests for BuildQueueFilterManager initialization."""

    def test_default_filter_state_all_ignore(self):
        """Default filter state has all filters at IGNORE (show everything)."""
        mgr = BuildQueueFilterManager()
        assert mgr.get_filter_state('loc_Planet') is FilterState.IGNORE
        assert mgr.get_filter_state('loc_Fleet') is FilterState.IGNORE
        assert mgr.get_filter_state('status_Active') is FilterState.IGNORE
        assert mgr.get_filter_state('status_Empty') is FilterState.IGNORE
        assert mgr.get_filter_state('cap_Ships') is FilterState.IGNORE
        assert mgr.get_filter_state('cap_Complexes') is FilterState.IGNORE

    def test_default_search_text_empty(self):
        """Default search_text is empty string."""
        mgr = BuildQueueFilterManager()
        assert mgr.search_text == ""

    def test_columns_list_populated_with_expected_ids(self):
        """Columns list is populated with expected column IDs."""
        mgr = BuildQueueFilterManager()
        col_ids = [c['id'] for c in mgr.columns]
        expected = [
            'location', 'system', 'sector', 'queue_count',
            'first_item', 'turns_left', 'capabilities', 'build_rate',
            # Resource rate columns
            'res_metals_rate', 'res_organics_rate', 'res_vapors_rate',
            'res_radioactives_rate', 'res_exotics_rate',
            # Resource total columns
            'res_metals_total', 'res_organics_total', 'res_vapors_total',
            'res_radioactives_total', 'res_exotics_total',
        ]
        assert col_ids == expected

    def test_columns_are_deep_copied(self):
        """Columns are deep copied so modifications don't affect defaults."""
        mgr = BuildQueueFilterManager()
        mgr.columns[0]['visible'] = False
        # Check that DEFAULT_COLUMNS was not modified
        assert DEFAULT_COLUMNS[0]['visible'] is True

    def test_custom_columns_accepted(self):
        """Custom columns can be passed at init."""
        custom = [{'id': 'custom', 'width': 100, 'title': 'Custom', 'visible': True}]
        mgr = BuildQueueFilterManager(columns=custom)
        assert len(mgr.columns) == 1
        assert mgr.columns[0]['id'] == 'custom'


class TestFilterStateAPI:
    """Tests for get/set filter state API (PROJ-220)."""

    def test_set_filter_state_changes_value(self):
        """set_filter_state changes the filter value."""
        mgr = BuildQueueFilterManager()
        mgr.set_filter_state('loc_Planet', FilterState.YES)
        assert mgr.get_filter_state('loc_Planet') is FilterState.YES

    def test_set_filter_state_no(self):
        """set_filter_state can set to NO."""
        mgr = BuildQueueFilterManager()
        mgr.set_filter_state('cap_Ships', FilterState.NO)
        assert mgr.get_filter_state('cap_Ships') is FilterState.NO

    def test_set_filter_state_back_to_ignore(self):
        """set_filter_state can return to IGNORE."""
        mgr = BuildQueueFilterManager()
        mgr.set_filter_state('status_Active', FilterState.YES)
        mgr.set_filter_state('status_Active', FilterState.IGNORE)
        assert mgr.get_filter_state('status_Active') is FilterState.IGNORE

    def test_filter_manager_property_exposed(self):
        """filter_manager property provides access to FilterStateManager."""
        mgr = BuildQueueFilterManager()
        fm = mgr.filter_manager
        assert fm.get_state('loc_Planet') is FilterState.IGNORE


class TestGetVisibleColumns:
    """Tests for get_visible_columns method."""

    def test_returns_only_visible_columns(self):
        """Returns only columns where visible is True."""
        mgr = BuildQueueFilterManager()
        visible = mgr.get_visible_columns()
        assert all(c['visible'] for c in visible)

    def test_hidden_columns_excluded(self):
        """Hidden columns are excluded from result."""
        mgr = BuildQueueFilterManager()
        # Hide the 'location' column
        for col in mgr.columns:
            if col['id'] == 'location':
                col['visible'] = False
        visible = mgr.get_visible_columns()
        visible_ids = [c['id'] for c in visible]
        assert 'location' not in visible_ids

    def test_all_columns_visible_by_default(self):
        """All default columns are visible by default."""
        mgr = BuildQueueFilterManager()
        visible = mgr.get_visible_columns()
        assert len(visible) == len(DEFAULT_COLUMNS)


class TestToggleColumnVisibility:
    """Tests for toggle_column_visibility method."""

    def test_toggle_visible_column_makes_invisible(self):
        """Toggling a visible column makes it invisible."""
        mgr = BuildQueueFilterManager()
        result = mgr.toggle_column_visibility('location')
        assert result is True
        loc_col = next(c for c in mgr.columns if c['id'] == 'location')
        assert loc_col['visible'] is False

    def test_toggle_hidden_column_makes_visible(self):
        """Toggling a hidden column makes it visible."""
        mgr = BuildQueueFilterManager()
        for col in mgr.columns:
            if col['id'] == 'system':
                col['visible'] = False
        result = mgr.toggle_column_visibility('system')
        assert result is True
        sys_col = next(c for c in mgr.columns if c['id'] == 'system')
        assert sys_col['visible'] is True

    def test_toggle_unknown_column_returns_false(self):
        """Toggling unknown column ID returns False."""
        mgr = BuildQueueFilterManager()
        result = mgr.toggle_column_visibility('nonexistent_column')
        assert result is False


class TestFilterSources:
    """Tests for filter_sources method."""

    def test_all_filters_ignore_shows_all_sources(self):
        """With all filters at IGNORE, all sources are shown."""
        mgr = BuildQueueFilterManager()
        sources = [
            _make_source("Planet 1", "planet", []),
            _make_source("Fleet 1", "fleet", [{'id': 'item'}]),
        ]
        result = mgr.filter_sources(sources)
        assert len(result) == 2

    def test_loc_planet_yes_shows_only_planets(self):
        """loc_Planet=YES shows only planet sources."""
        mgr = BuildQueueFilterManager()
        mgr.set_filter_state('loc_Planet', FilterState.YES)
        sources = [
            _make_source("Planet 1", "planet"),
            _make_source("Fleet 1", "fleet"),
        ]
        result = mgr.filter_sources(sources)
        assert len(result) == 1
        assert result[0].display_name == "Planet 1"

    def test_loc_planet_no_excludes_planets(self):
        """loc_Planet=NO excludes planet sources (shows fleets)."""
        mgr = BuildQueueFilterManager()
        mgr.set_filter_state('loc_Planet', FilterState.NO)
        sources = [
            _make_source("Planet 1", "planet"),
            _make_source("Fleet 1", "fleet"),
        ]
        result = mgr.filter_sources(sources)
        assert len(result) == 1
        assert result[0].display_name == "Fleet 1"

    def test_loc_fleet_yes_shows_only_fleets(self):
        """loc_Fleet=YES shows only fleet sources."""
        mgr = BuildQueueFilterManager()
        mgr.set_filter_state('loc_Fleet', FilterState.YES)
        sources = [
            _make_source("Planet 1", "planet"),
            _make_source("Fleet 1", "fleet"),
        ]
        result = mgr.filter_sources(sources)
        assert len(result) == 1
        assert result[0].display_name == "Fleet 1"

    def test_status_active_yes_shows_only_active(self):
        """status_Active=YES shows only sources with items in queue."""
        mgr = BuildQueueFilterManager()
        mgr.set_filter_state('status_Active', FilterState.YES)
        sources = [
            _make_source("Active Queue", "planet", [{'id': 'item'}]),
            _make_source("Empty Queue", "planet", []),
        ]
        result = mgr.filter_sources(sources)
        assert len(result) == 1
        assert result[0].display_name == "Active Queue"

    def test_status_empty_yes_shows_only_empty(self):
        """status_Empty=YES shows only sources with empty queues."""
        mgr = BuildQueueFilterManager()
        mgr.set_filter_state('status_Empty', FilterState.YES)
        sources = [
            _make_source("Active Queue", "planet", [{'id': 'item'}]),
            _make_source("Empty Queue", "planet", []),
        ]
        result = mgr.filter_sources(sources)
        assert len(result) == 1
        assert result[0].display_name == "Empty Queue"

    def test_status_active_no_excludes_active(self):
        """status_Active=NO excludes active queues (shows empty)."""
        mgr = BuildQueueFilterManager()
        mgr.set_filter_state('status_Active', FilterState.NO)
        sources = [
            _make_source("Active Queue", "planet", [{'id': 'item'}]),
            _make_source("Empty Queue", "planet", []),
        ]
        result = mgr.filter_sources(sources)
        assert len(result) == 1
        assert result[0].display_name == "Empty Queue"

    def test_cap_ships_yes_shows_only_ship_builders(self):
        """cap_Ships=YES shows only sources that can build ships."""
        mgr = BuildQueueFilterManager()
        mgr.set_filter_state('cap_Ships', FilterState.YES)
        sources = [
            _make_source("Shipyard", "planet", can_build_ships=True, can_build_complexes=False),
            _make_source("Factory", "planet", can_build_ships=False, can_build_complexes=True),
            _make_source("Both", "planet", can_build_ships=True, can_build_complexes=True),
        ]
        result = mgr.filter_sources(sources)
        names = [s.display_name for s in result]
        assert "Shipyard" in names
        assert "Both" in names
        assert "Factory" not in names

    def test_cap_complexes_yes_shows_only_complex_builders(self):
        """cap_Complexes=YES shows only sources that can build complexes."""
        mgr = BuildQueueFilterManager()
        mgr.set_filter_state('cap_Complexes', FilterState.YES)
        sources = [
            _make_source("Shipyard", "planet", can_build_ships=True, can_build_complexes=False),
            _make_source("Factory", "planet", can_build_ships=False, can_build_complexes=True),
            _make_source("Both", "planet", can_build_ships=True, can_build_complexes=True),
        ]
        result = mgr.filter_sources(sources)
        names = [s.display_name for s in result]
        assert "Factory" in names
        assert "Both" in names
        assert "Shipyard" not in names

    def test_cap_ships_no_excludes_ship_builders(self):
        """cap_Ships=NO excludes sources that can build ships."""
        mgr = BuildQueueFilterManager()
        mgr.set_filter_state('cap_Ships', FilterState.NO)
        sources = [
            _make_source("Shipyard", "planet", can_build_ships=True, can_build_complexes=False),
            _make_source("Factory", "planet", can_build_ships=False, can_build_complexes=True),
        ]
        result = mgr.filter_sources(sources)
        names = [s.display_name for s in result]
        assert "Factory" in names
        assert "Shipyard" not in names

    def test_text_search_filters_by_display_name(self):
        """Text search filters sources by display_name."""
        mgr = BuildQueueFilterManager()
        mgr.search_text = "Alpha"
        sources = [
            _make_source("Alpha Base", "planet"),
            _make_source("Beta Station", "planet"),
            _make_source("Alpha Fleet", "fleet"),
        ]
        result = mgr.filter_sources(sources)
        names = [s.display_name for s in result]
        assert "Alpha Base" in names
        assert "Alpha Fleet" in names
        assert "Beta Station" not in names

    def test_text_search_is_case_insensitive(self):
        """Text search is case-insensitive."""
        mgr = BuildQueueFilterManager()
        mgr.search_text = "ALPHA"
        sources = [
            _make_source("alpha base", "planet"),
            _make_source("ALPHA STATION", "planet"),
            _make_source("AlPhA Fleet", "fleet"),
        ]
        result = mgr.filter_sources(sources)
        assert len(result) == 3

    def test_combined_filters_and_logic(self):
        """Multiple filters combine with AND logic."""
        mgr = BuildQueueFilterManager()
        mgr.set_filter_state('loc_Fleet', FilterState.NO)
        mgr.set_filter_state('status_Empty', FilterState.NO)
        mgr.search_text = "Ship"
        sources = [
            _make_source("Shipyard Alpha", "planet", [{'id': 'item'}]),
            _make_source("Shipyard Beta", "planet", []),  # Empty, excluded
            _make_source("Shipyard Fleet", "fleet", [{'id': 'item'}]),  # Fleet, excluded
            _make_source("Factory", "planet", [{'id': 'item'}]),  # No "Ship", excluded
        ]
        result = mgr.filter_sources(sources)
        assert len(result) == 1
        assert result[0].display_name == "Shipyard Alpha"

    def test_empty_search_text_not_filtered(self):
        """Empty search text doesn't filter anything."""
        mgr = BuildQueueFilterManager()
        mgr.search_text = "   "  # Whitespace only
        sources = [_make_source("Test", "planet")]
        result = mgr.filter_sources(sources)
        assert len(result) == 1


class TestResetSelectionState:
    """Tests for reset_selection_state method."""

    def test_returns_default_selection_values(self):
        """Returns dict with default selection values."""
        mgr = BuildQueueFilterManager()
        state = mgr.reset_selection_state()
        assert state['selected_source'] is None
        assert state['selected_index'] == -1
        assert state['selected_indices'] == set()

    def test_returns_new_set_each_time(self):
        """Returns a new set each time (not shared reference)."""
        mgr = BuildQueueFilterManager()
        state1 = mgr.reset_selection_state()
        state2 = mgr.reset_selection_state()
        state1['selected_indices'].add(5)
        assert 5 not in state2['selected_indices']


class TestSortSources:
    """Tests for sort_sources method."""

    def test_sort_by_location_ascending(self):
        """Alphabetical sort A->Z on location column."""
        mgr = BuildQueueFilterManager()
        sources = [
            _make_source("Zeta Base"),
            _make_source("Alpha Station"),
            _make_source("Charlie Yard"),
        ]
        values = {
            "Zeta Base": "Zeta Base",
            "Alpha Station": "Alpha Station",
            "Charlie Yard": "Charlie Yard",
        }
        get_val = lambda s, col: values.get(s.display_name, "-")
        result = mgr.sort_sources(sources, 'location', False, get_val)
        assert [s.display_name for s in result] == ["Alpha Station", "Charlie Yard", "Zeta Base"]

    def test_sort_by_location_descending(self):
        """Alphabetical sort Z->A on location column."""
        mgr = BuildQueueFilterManager()
        sources = [
            _make_source("Alpha Station"),
            _make_source("Zeta Base"),
            _make_source("Charlie Yard"),
        ]
        values = {
            "Zeta Base": "Zeta Base",
            "Alpha Station": "Alpha Station",
            "Charlie Yard": "Charlie Yard",
        }
        get_val = lambda s, col: values.get(s.display_name, "-")
        result = mgr.sort_sources(sources, 'location', True, get_val)
        assert [s.display_name for s in result] == ["Zeta Base", "Charlie Yard", "Alpha Station"]

    def test_sort_by_queue_count_numeric(self):
        """Numeric sort on queue_count column, '-' sorts to bottom."""
        mgr = BuildQueueFilterManager()
        sources = [
            _make_source("Three"),
            _make_source("One"),
            _make_source("Empty"),
            _make_source("Ten"),
        ]
        values = {
            "Three": "3",
            "One": "1",
            "Empty": "-",
            "Ten": "10",
        }
        get_val = lambda s, col: values.get(s.display_name, "-")
        result = mgr.sort_sources(sources, 'queue_count', False, get_val)
        assert [s.display_name for s in result] == ["One", "Three", "Ten", "Empty"]

    def test_sort_by_turns_left_numeric(self):
        """Numeric sort on turns_left column."""
        mgr = BuildQueueFilterManager()
        sources = [
            _make_source("Long"),
            _make_source("Short"),
            _make_source("Medium"),
        ]
        values = {
            "Long": "15",
            "Short": "2",
            "Medium": "7",
        }
        get_val = lambda s, col: values.get(s.display_name, "-")
        result = mgr.sort_sources(sources, 'turns_left', False, get_val)
        assert [s.display_name for s in result] == ["Short", "Medium", "Long"]

    def test_sort_by_resource_rate_numeric(self):
        """Resource rate column sorted numerically."""
        mgr = BuildQueueFilterManager()
        sources = [
            _make_source("High"),
            _make_source("Low"),
            _make_source("Mid"),
        ]
        values = {
            "High": "500",
            "Low": "25",
            "Mid": "100",
        }
        get_val = lambda s, col: values.get(s.display_name, "-")
        result = mgr.sort_sources(sources, 'res_metals_rate', False, get_val)
        assert [s.display_name for s in result] == ["Low", "Mid", "High"]

    def test_sort_no_column_id_unchanged(self):
        """None sort_column_id returns unchanged list."""
        mgr = BuildQueueFilterManager()
        sources = [_make_source("B"), _make_source("A"), _make_source("C")]
        original_order = [s.display_name for s in sources]
        get_val = lambda s, col: s.display_name
        result = mgr.sort_sources(sources, None, False, get_val)
        assert [s.display_name for s in result] == original_order

    def test_sort_unknown_column_unchanged(self):
        """Unknown column ID returns unchanged list."""
        mgr = BuildQueueFilterManager()
        sources = [_make_source("B"), _make_source("A"), _make_source("C")]
        original_order = [s.display_name for s in sources]
        get_val = lambda s, col: s.display_name
        result = mgr.sort_sources(sources, 'nonexistent_column', False, get_val)
        assert [s.display_name for s in result] == original_order

    def test_sort_dash_values_last(self):
        """'-' values sort after real values in both ascending and descending."""
        mgr = BuildQueueFilterManager()
        sources = [
            _make_source("Dash1"),
            _make_source("Alpha"),
            _make_source("Dash2"),
            _make_source("Beta"),
        ]
        values = {
            "Dash1": "-",
            "Alpha": "Alpha",
            "Dash2": "-",
            "Beta": "Beta",
        }
        get_val = lambda s, col: values.get(s.display_name, "-")

        # Ascending: real values sorted, then dashes
        result_asc = mgr.sort_sources(list(sources), 'location', False, get_val)
        names_asc = [s.display_name for s in result_asc]
        assert names_asc.index("Alpha") < names_asc.index("Dash1")
        assert names_asc.index("Beta") < names_asc.index("Dash2")

        # Descending: dashes first (reversed infinity), then real values reversed
        result_desc = mgr.sort_sources(list(sources), 'location', True, get_val)
        names_desc = [s.display_name for s in result_desc]
        assert names_desc[0] in ["Dash1", "Dash2"]
        assert names_desc[1] in ["Dash1", "Dash2"]
