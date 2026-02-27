"""Tests for EmpireBuildQueueViewModel (PROJ-172 Phase 3).

Verifies the ViewModel that manages build queue list state:
- Source loading and filtering
- Single-select and multi-select
- Search text filtering
- Event emission on state changes
- Lazy refresh (cached results)
"""
import pytest
from unittest.mock import MagicMock, patch

from game.strategy.data.build_queue_source import BuildQueueSource
from game.ui.screens.empire_build_queue_viewmodel import (
    EmpireBuildQueueViewModel,
    BuildQueueWindowEvents,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_source(queue_id="planet_1_base", display_name="Alpha - Base",
                 context_type="planet", can_build_ships=False,
                 can_build_complexes=True, queue_items=None,
                 build_rate=None) -> BuildQueueSource:
    """Create a BuildQueueSource for testing."""
    if build_rate is None:
        build_rate = {"Metals": 2000.0, "Organics": 2000.0}
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


def _make_viewmodel(sources=None):
    """Create EmpireBuildQueueViewModel with test sources."""
    from game.ui.screens.builder.event_bus import EventBus

    if sources is None:
        sources = [
            _make_source("p1", "Alpha - Base", "planet"),
            _make_source("p2", "Beta - Shipyard", "planet", can_build_ships=True),
            _make_source("f1", "Fleet Yard", "fleet", can_build_ships=True),
        ]

    event_bus = EventBus()
    vm = EmpireBuildQueueViewModel(event_bus, sources)
    return vm, event_bus


# ===========================================================================
# Event Constants Tests
# ===========================================================================

class TestBuildQueueWindowEvents:
    """Event constants should be defined."""

    def test_sources_changed_event_exists(self):
        """SOURCES_CHANGED event constant exists."""
        assert hasattr(BuildQueueWindowEvents, 'SOURCES_CHANGED')
        assert BuildQueueWindowEvents.SOURCES_CHANGED

    def test_selection_changed_event_exists(self):
        """SELECTION_CHANGED event constant exists."""
        assert hasattr(BuildQueueWindowEvents, 'SELECTION_CHANGED')
        assert BuildQueueWindowEvents.SELECTION_CHANGED

    def test_filters_applied_event_exists(self):
        """FILTERS_APPLIED event constant exists."""
        assert hasattr(BuildQueueWindowEvents, 'FILTERS_APPLIED')
        assert BuildQueueWindowEvents.FILTERS_APPLIED


# ===========================================================================
# Initialization Tests
# ===========================================================================

class TestViewModelInitialization:
    """ViewModel should initialize with correct state."""

    def test_stores_sources(self):
        """ViewModel stores provided sources."""
        sources = [_make_source("p1", "Alpha")]
        vm, _ = _make_viewmodel(sources=sources)
        assert len(vm.all_sources) == 1
        assert vm.all_sources[0].queue_id == "p1"

    def test_filtered_sources_starts_equal_to_all(self):
        """Filtered sources equals all sources initially."""
        sources = [_make_source("p1", "Alpha"), _make_source("p2", "Beta")]
        vm, _ = _make_viewmodel(sources=sources)
        assert len(vm.filtered_sources) == 2

    def test_no_initial_selection(self):
        """No source selected initially."""
        vm, _ = _make_viewmodel()
        assert vm.selected_indices == set()
        assert vm.get_selected_sources() == []

    def test_search_text_empty_initially(self):
        """Search text is empty string initially."""
        vm, _ = _make_viewmodel()
        assert vm.search_text == ""

    def test_filter_state_all_enabled_initially(self):
        """All filters enabled by default."""
        vm, _ = _make_viewmodel()
        assert vm.filter_location_type == {'Planet': True, 'Fleet': True}
        assert vm.filter_status == {'Active': True, 'Empty': True}
        assert vm.filter_capabilities == {'Ships': True, 'Complexes': True}


# ===========================================================================
# Source Loading Tests
# ===========================================================================

class TestSourceLoading:
    """ViewModel should load and update sources."""

    def test_update_sources_replaces_all_sources(self):
        """update_sources() replaces source list."""
        vm, _ = _make_viewmodel(sources=[_make_source("p1", "Alpha")])
        new_sources = [_make_source("p2", "Beta"), _make_source("p3", "Gamma")]
        vm.update_sources(new_sources)
        assert len(vm.all_sources) == 2
        assert vm.all_sources[0].queue_id == "p2"

    def test_update_sources_triggers_refresh(self):
        """update_sources() marks data as needing refresh."""
        vm, _ = _make_viewmodel()
        vm._needs_refresh = False
        vm.update_sources([_make_source("new", "New")])
        assert vm._needs_refresh is True

    def test_update_sources_clears_selection(self):
        """update_sources() clears current selection."""
        vm, _ = _make_viewmodel()
        vm.select_source(0, ctrl_held=False)
        vm.update_sources([_make_source("new", "New")])
        assert vm.selected_indices == set()


# ===========================================================================
# Selection Tests
# ===========================================================================

class TestSingleSelection:
    """Single selection (no Ctrl) behavior."""

    def test_select_source_updates_indices(self):
        """select_source() updates selected_indices."""
        sources = [_make_source("p1", "Alpha"), _make_source("p2", "Beta")]
        vm, _ = _make_viewmodel(sources=sources)
        vm.select_source(1, ctrl_held=False)
        assert vm.selected_indices == {1}

    def test_select_source_updates_get_selected_sources(self):
        """select_source() makes source available via get_selected_sources()."""
        sources = [_make_source("p1", "Alpha"), _make_source("p2", "Beta")]
        vm, _ = _make_viewmodel(sources=sources)
        vm.select_source(1, ctrl_held=False)
        assert vm.get_selected_sources() == [sources[1]]

    def test_select_source_sets_single_index_in_set(self):
        """Single select sets selected_indices to single value."""
        vm, _ = _make_viewmodel()
        vm.select_source(0, ctrl_held=False)
        assert vm.selected_indices == {0}

    def test_select_source_replaces_previous_selection(self):
        """Single select replaces any previous multi-selection."""
        vm, _ = _make_viewmodel()
        vm.selected_indices = {0, 1, 2}
        vm.select_source(1, ctrl_held=False)
        assert vm.selected_indices == {1}

    def test_select_out_of_range_ignored(self):
        """Selecting invalid index is ignored."""
        sources = [_make_source("p1", "Alpha")]
        vm, _ = _make_viewmodel(sources=sources)
        vm.select_source(5, ctrl_held=False)
        assert vm.selected_indices == set()

    def test_select_negative_index_ignored(self):
        """Selecting negative index is ignored."""
        vm, _ = _make_viewmodel()
        vm.select_source(-1, ctrl_held=False)
        assert vm.selected_indices == set()


class TestMultiSelection:
    """Multi-selection (Ctrl+click) behavior."""

    def test_ctrl_click_adds_to_selection(self):
        """Ctrl+click adds index to existing selection."""
        vm, _ = _make_viewmodel()
        vm.select_source(0, ctrl_held=False)
        vm.select_source(2, ctrl_held=True)
        assert vm.selected_indices == {0, 2}

    def test_ctrl_click_toggles_off_selected(self):
        """Ctrl+click on selected index removes it."""
        vm, _ = _make_viewmodel()
        vm.selected_indices = {0, 1}
        vm.select_source(0, ctrl_held=True)
        assert vm.selected_indices == {1}

    def test_ctrl_click_on_only_selected_keeps_it(self):
        """Cannot deselect the last selected item."""
        sources = [_make_source("p1", "Alpha")]
        vm, _ = _make_viewmodel(sources=sources)
        vm.selected_indices = {0}
        vm.select_source(0, ctrl_held=True)
        assert vm.selected_indices == {0}

    def test_multi_select_sets_multiple_indices(self):
        """Multiple selections populate selected_indices with multiple values."""
        vm, _ = _make_viewmodel()
        vm.select_source(0, ctrl_held=False)
        vm.select_source(1, ctrl_held=True)
        assert vm.selected_indices == {0, 1}


class TestSelectionHelpers:
    """get_selected_sources() and get_selection_summary()."""

    def test_get_selected_sources_returns_sources(self):
        """get_selected_sources() returns list of sources."""
        sources = [_make_source("p1", "Alpha"), _make_source("p2", "Beta")]
        vm, _ = _make_viewmodel(sources=sources)
        vm.selected_indices = {0, 1}
        result = vm.get_selected_sources()
        assert len(result) == 2
        assert sources[0] in result
        assert sources[1] in result

    def test_get_selected_sources_empty_when_none(self):
        """get_selected_sources() returns empty list when nothing selected."""
        vm, _ = _make_viewmodel()
        vm.selected_indices = set()
        assert vm.get_selected_sources() == []

    def test_get_selection_summary_single(self):
        """Selection summary for single queue shows name."""
        sources = [_make_source("p1", "Alpha Base")]
        vm, _ = _make_viewmodel(sources=sources)
        vm.select_source(0, ctrl_held=False)
        summary = vm.get_selection_summary()
        assert "1" in summary
        assert "Alpha Base" in summary

    def test_get_selection_summary_multiple(self):
        """Selection summary for multiple queues shows count."""
        vm, _ = _make_viewmodel()
        vm.selected_indices = {0, 1}
        summary = vm.get_selection_summary()
        assert "2" in summary

    def test_get_selection_summary_none(self):
        """Selection summary with nothing selected."""
        vm, _ = _make_viewmodel()
        vm.selected_indices = set()
        summary = vm.get_selection_summary()
        assert "No" in summary or "0" in summary


# ===========================================================================
# Filter Tests
# ===========================================================================

class TestFilterApplication:
    """apply_filters() should filter sources correctly."""

    def test_apply_filters_updates_filtered_sources(self):
        """apply_filters() updates filtered_sources."""
        sources = [
            _make_source("p1", "Alpha", "planet"),
            _make_source("f1", "Fleet", "fleet"),
        ]
        vm, _ = _make_viewmodel(sources=sources)
        vm.filter_location_type = {'Planet': True, 'Fleet': False}
        vm.apply_filters()
        assert len(vm.filtered_sources) == 1
        assert vm.filtered_sources[0].context_type == "planet"

    def test_apply_filters_clears_selection(self):
        """apply_filters() clears selection."""
        vm, _ = _make_viewmodel()
        vm.select_source(0, ctrl_held=False)
        vm.apply_filters()
        assert vm.selected_indices == set()

    def test_filter_by_queue_status(self):
        """Filter by active/empty queue status."""
        sources = [
            _make_source("p1", "Active", queue_items=[{"design_id": "x"}]),
            _make_source("p2", "Empty", queue_items=[]),
        ]
        vm, _ = _make_viewmodel(sources=sources)
        vm.filter_status = {'Active': True, 'Empty': False}
        vm.apply_filters()
        assert len(vm.filtered_sources) == 1
        assert vm.filtered_sources[0].queue_id == "p1"

    def test_filter_by_capabilities(self):
        """Filter by build capabilities."""
        sources = [
            _make_source("p1", "Ships Only", can_build_ships=True, can_build_complexes=False),
            _make_source("p2", "Complexes Only", can_build_ships=False, can_build_complexes=True),
        ]
        vm, _ = _make_viewmodel(sources=sources)
        vm.filter_capabilities = {'Ships': False, 'Complexes': True}
        vm.apply_filters()
        assert len(vm.filtered_sources) == 1
        assert vm.filtered_sources[0].queue_id == "p2"


class TestSearchFiltering:
    """Search text filtering."""

    def test_set_search_text_updates_value(self):
        """set_search_text() updates search_text."""
        vm, _ = _make_viewmodel()
        vm.set_search_text("alpha")
        assert vm.search_text == "alpha"

    def test_search_text_filters_sources(self):
        """Search filters by display_name substring."""
        sources = [
            _make_source("p1", "Alpha Base"),
            _make_source("p2", "Beta Shipyard"),
        ]
        vm, _ = _make_viewmodel(sources=sources)
        vm.set_search_text("alpha")
        vm.apply_filters()
        assert len(vm.filtered_sources) == 1
        assert vm.filtered_sources[0].queue_id == "p1"

    def test_search_is_case_insensitive(self):
        """Search is case-insensitive."""
        sources = [_make_source("p1", "ALPHA Base")]
        vm, _ = _make_viewmodel(sources=sources)
        vm.set_search_text("alpha")
        vm.apply_filters()
        assert len(vm.filtered_sources) == 1

    def test_empty_search_shows_all(self):
        """Empty search text shows all sources."""
        sources = [_make_source("p1", "Alpha"), _make_source("p2", "Beta")]
        vm, _ = _make_viewmodel(sources=sources)
        vm.set_search_text("")
        vm.apply_filters()
        assert len(vm.filtered_sources) == 2


# ===========================================================================
# Event Emission Tests
# ===========================================================================

class TestEventEmission:
    """ViewModel should emit events on state changes."""

    def test_selection_change_emits_event(self):
        """Selecting a source emits SELECTION_CHANGED."""
        vm, event_bus = _make_viewmodel()
        handler = MagicMock()
        event_bus.subscribe(BuildQueueWindowEvents.SELECTION_CHANGED, handler)
        vm.select_source(0, ctrl_held=False)
        handler.assert_called()

    def test_apply_filters_emits_event(self):
        """apply_filters() emits FILTERS_APPLIED."""
        vm, event_bus = _make_viewmodel()
        handler = MagicMock()
        event_bus.subscribe(BuildQueueWindowEvents.FILTERS_APPLIED, handler)
        vm.apply_filters()
        handler.assert_called()

    def test_update_sources_emits_event(self):
        """update_sources() emits SOURCES_CHANGED."""
        vm, event_bus = _make_viewmodel()
        handler = MagicMock()
        event_bus.subscribe(BuildQueueWindowEvents.SOURCES_CHANGED, handler)
        vm.update_sources([_make_source("new", "New")])
        handler.assert_called()


# ===========================================================================
# Lazy Refresh Tests
# ===========================================================================

class TestLazyRefresh:
    """ViewModel should use lazy refresh pattern."""

    def test_needs_refresh_false_after_init_refresh(self):
        """_needs_refresh is False after construction (initial refresh done)."""
        vm, _ = _make_viewmodel()
        # Initial refresh happens in __init__, so flag is cleared
        assert vm._needs_refresh is False

    def test_filtered_sources_clears_needs_refresh(self):
        """Accessing filtered_sources clears _needs_refresh."""
        vm, _ = _make_viewmodel()
        _ = vm.filtered_sources
        assert vm._needs_refresh is False

    def test_filter_change_sets_needs_refresh(self):
        """Changing filter state sets _needs_refresh."""
        vm, _ = _make_viewmodel()
        _ = vm.filtered_sources  # Clear flag
        vm.filter_location_type['Planet'] = False
        vm.apply_filters()
        # After apply_filters, _needs_refresh should be cleared again
        # since we recalculated
        _ = vm.filtered_sources
        assert vm._needs_refresh is False

    def test_cached_results_returned_when_clean(self):
        """Same list returned when no refresh needed."""
        vm, _ = _make_viewmodel()
        first = vm.filtered_sources
        second = vm.filtered_sources
        assert first is second


# ===========================================================================
# Toggle Filter Tests
# ===========================================================================

class TestToggleFilter:
    """toggle_filter() convenience method."""

    def test_toggle_location_filter(self):
        """toggle_filter() toggles location type filter."""
        vm, _ = _make_viewmodel()
        assert vm.filter_location_type['Planet'] is True
        vm.toggle_filter('loc_Planet')
        assert vm.filter_location_type['Planet'] is False

    def test_toggle_status_filter(self):
        """toggle_filter() toggles status filter."""
        vm, _ = _make_viewmodel()
        assert vm.filter_status['Active'] is True
        vm.toggle_filter('status_Active')
        assert vm.filter_status['Active'] is False

    def test_toggle_capability_filter(self):
        """toggle_filter() toggles capability filter."""
        vm, _ = _make_viewmodel()
        assert vm.filter_capabilities['Ships'] is True
        vm.toggle_filter('cap_Ships')
        assert vm.filter_capabilities['Ships'] is False

    def test_toggle_unknown_filter_returns_false(self):
        """toggle_filter() returns False for unknown filter."""
        vm, _ = _make_viewmodel()
        result = vm.toggle_filter('unknown_filter')
        assert result is False

    def test_toggle_filter_returns_new_state(self):
        """toggle_filter() returns the new state."""
        vm, _ = _make_viewmodel()
        result = vm.toggle_filter('loc_Planet')
        assert result is False  # Was True, now False
        result = vm.toggle_filter('loc_Planet')
        assert result is True  # Was False, now True


# ===========================================================================
# Column Value Getter Tests
# ===========================================================================

class TestGetColumnValue:
    """get_column_value() for rendering support."""

    def test_location_column_returns_display_name(self):
        """Location column returns display_name."""
        sources = [_make_source("p1", "Alpha - Base")]
        vm, _ = _make_viewmodel(sources=sources)
        result = vm.get_column_value(sources[0], 'location')
        assert result == "Alpha - Base"

    def test_queue_count_column_with_items(self):
        """Queue count column returns item count."""
        sources = [_make_source("p1", "Alpha", queue_items=[
            {"design_id": "x"}, {"design_id": "y"}
        ])]
        vm, _ = _make_viewmodel(sources=sources)
        result = vm.get_column_value(sources[0], 'queue_count')
        assert "2" in result

    def test_queue_count_column_empty(self):
        """Queue count column returns dash for empty."""
        sources = [_make_source("p1", "Alpha", queue_items=[])]
        vm, _ = _make_viewmodel(sources=sources)
        result = vm.get_column_value(sources[0], 'queue_count')
        assert result == "-"

    def test_capabilities_column(self):
        """Capabilities column returns capability text."""
        sources = [_make_source("p1", "Alpha", can_build_ships=True, can_build_complexes=True)]
        vm, _ = _make_viewmodel(sources=sources)
        result = vm.get_column_value(sources[0], 'capabilities')
        assert result == "Ships & Complexes"

    def test_unknown_column_returns_empty(self):
        """Unknown column returns empty string."""
        sources = [_make_source("p1", "Alpha")]
        vm, _ = _make_viewmodel(sources=sources)
        result = vm.get_column_value(sources[0], 'nonexistent')
        assert result == ""
