"""Unit tests for empire_build_queue_filter_manager.py.

Tests the BuildQueueFilterManager class which manages filter state,
column visibility, and filter predicates for the Empire Build Queue Window.

Created as part of PROJ-89 Phase 3.
"""
import pytest
from unittest.mock import MagicMock

from game.ui.screens.empire_build_queue_filter_manager import (
    BuildQueueFilterManager,
    DEFAULT_COLUMNS,
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

    def test_default_filter_state_all_types_enabled(self):
        """Default filter state has all location types enabled."""
        mgr = BuildQueueFilterManager()
        assert mgr.filter_location_type == {'Planet': True, 'Fleet': True}
        assert mgr.filter_status == {'Active': True, 'Empty': True}
        assert mgr.filter_capabilities == {'Ships': True, 'Complexes': True}

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


class TestGetVisibleColumns:
    """Tests for get_visible_columns method."""

    def test_returns_only_visible_columns(self):
        """Returns only columns where visible is True."""
        mgr = BuildQueueFilterManager()
        # All default columns are visible except build_rate by some tests
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
        # 'location' is visible by default
        result = mgr.toggle_column_visibility('location')
        assert result is True
        loc_col = next(c for c in mgr.columns if c['id'] == 'location')
        assert loc_col['visible'] is False

    def test_toggle_hidden_column_makes_visible(self):
        """Toggling a hidden column makes it visible."""
        mgr = BuildQueueFilterManager()
        # First hide it
        for col in mgr.columns:
            if col['id'] == 'system':
                col['visible'] = False
        # Now toggle it back
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

    def test_all_filters_enabled_shows_all_sources(self):
        """With all filters enabled, all sources are shown."""
        mgr = BuildQueueFilterManager()
        sources = [
            _make_source("Planet 1", "planet", []),
            _make_source("Fleet 1", "fleet", [{'id': 'item'}]),
        ]
        result = mgr.filter_sources(sources)
        assert len(result) == 2

    def test_hide_fleet_sources_filters_correctly(self):
        """Disabling Fleet filter hides fleet sources."""
        mgr = BuildQueueFilterManager()
        mgr.filter_location_type['Fleet'] = False
        sources = [
            _make_source("Planet 1", "planet"),
            _make_source("Fleet 1", "fleet"),
        ]
        result = mgr.filter_sources(sources)
        assert len(result) == 1
        assert result[0].display_name == "Planet 1"

    def test_hide_planet_sources_filters_correctly(self):
        """Disabling Planet filter hides planet sources."""
        mgr = BuildQueueFilterManager()
        mgr.filter_location_type['Planet'] = False
        sources = [
            _make_source("Planet 1", "planet"),
            _make_source("Fleet 1", "fleet"),
        ]
        result = mgr.filter_sources(sources)
        assert len(result) == 1
        assert result[0].display_name == "Fleet 1"

    def test_hide_empty_queues_filters_correctly(self):
        """Disabling Empty filter hides sources with empty queues."""
        mgr = BuildQueueFilterManager()
        mgr.filter_status['Empty'] = False
        sources = [
            _make_source("Active Queue", "planet", [{'id': 'item'}]),
            _make_source("Empty Queue", "planet", []),
        ]
        result = mgr.filter_sources(sources)
        assert len(result) == 1
        assert result[0].display_name == "Active Queue"

    def test_hide_active_queues_filters_correctly(self):
        """Disabling Active filter hides sources with items in queue."""
        mgr = BuildQueueFilterManager()
        mgr.filter_status['Active'] = False
        sources = [
            _make_source("Active Queue", "planet", [{'id': 'item'}]),
            _make_source("Empty Queue", "planet", []),
        ]
        result = mgr.filter_sources(sources)
        assert len(result) == 1
        assert result[0].display_name == "Empty Queue"

    def test_capabilities_filter_ships_only(self):
        """Showing only Ships capability filters correctly."""
        mgr = BuildQueueFilterManager()
        mgr.filter_capabilities['Complexes'] = False
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

    def test_capabilities_filter_complexes_only(self):
        """Showing only Complexes capability filters correctly."""
        mgr = BuildQueueFilterManager()
        mgr.filter_capabilities['Ships'] = False
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
        mgr.filter_location_type['Fleet'] = False
        mgr.filter_status['Empty'] = False
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
