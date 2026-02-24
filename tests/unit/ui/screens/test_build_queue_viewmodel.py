"""Unit tests for BuildQueueScreenViewModel.

Tests UI state management for BuildQueueScreen including:
- Queue source selection (single and multi-select)
- Queue item selection
- Category filter
- Event emission

PROJ-172 Phase 4.
"""
import pytest
from unittest.mock import MagicMock

from game.ui.screens.build_queue_viewmodel import (
    BuildQueueScreenViewModel,
    BuildQueueScreenEvents,
)
from game.ui.screens.builder.event_bus import EventBus


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def event_bus():
    """Create a fresh EventBus for each test."""
    return EventBus()


@pytest.fixture
def mock_queue_source():
    """Create a mock BuildQueueSource."""
    source = MagicMock()
    source.display_name = "Test Planet"
    source.context_type = "planet"
    source.construction_queue = []
    source.can_build_ships = True
    source.can_build_complexes = True
    source.build_rate = {"Metals": 10, "Organics": 5}
    return source


@pytest.fixture
def mock_queue_sources(mock_queue_source):
    """Create a list of mock queue sources."""
    source1 = mock_queue_source
    source1.display_name = "Planet Alpha"

    source2 = MagicMock()
    source2.display_name = "Fleet Beta"
    source2.context_type = "fleet"
    source2.construction_queue = []
    source2.can_build_ships = True
    source2.can_build_complexes = False
    source2.build_rate = {"Metals": 20, "Organics": 10}

    source3 = MagicMock()
    source3.display_name = "Planet Gamma"
    source3.context_type = "planet"
    source3.construction_queue = []
    source3.can_build_ships = True
    source3.can_build_complexes = True
    source3.build_rate = {"Metals": 15, "Organics": 8}

    return [source1, source2, source3]


@pytest.fixture
def viewmodel(event_bus, mock_queue_sources):
    """Create a ViewModel with mock sources."""
    return BuildQueueScreenViewModel(event_bus, mock_queue_sources)


@pytest.fixture
def empty_viewmodel(event_bus):
    """Create a ViewModel with no sources."""
    return BuildQueueScreenViewModel(event_bus, [])


# ---------------------------------------------------------------------------
# Initialization Tests
# ---------------------------------------------------------------------------

class TestBuildQueueScreenViewModelInit:
    """Test ViewModel initialization."""

    def test_init_with_sources(self, viewmodel, mock_queue_sources):
        """ViewModel initializes with sources and selects first."""
        assert viewmodel.queue_source_count == 3
        assert viewmodel.active_queue_source == mock_queue_sources[0]
        assert viewmodel.selected_queue_indices == {0}
        assert not viewmodel.is_multi_select

    def test_init_empty(self, empty_viewmodel):
        """ViewModel initializes correctly with no sources."""
        assert empty_viewmodel.queue_source_count == 0
        assert empty_viewmodel.active_queue_source is None
        assert empty_viewmodel.selected_queue_indices == set()

    def test_init_default_category(self, viewmodel):
        """ViewModel defaults to 'complex' category."""
        assert viewmodel.selected_category == "complex"

    def test_init_no_item_selected(self, viewmodel):
        """ViewModel starts with no queue item selected."""
        assert viewmodel.selected_queue_index is None


# ---------------------------------------------------------------------------
# Queue Source Selection Tests
# ---------------------------------------------------------------------------

class TestQueueSourceSelection:
    """Test queue source selection behavior."""

    def test_select_single_source(self, viewmodel, mock_queue_sources):
        """Single click selects only that source."""
        viewmodel.select_queue_source(1)

        assert viewmodel.selected_queue_indices == {1}
        assert viewmodel.active_queue_source == mock_queue_sources[1]
        assert not viewmodel.is_multi_select

    def test_select_source_clears_previous(self, viewmodel, mock_queue_sources):
        """Single click clears previous selection."""
        viewmodel.select_queue_source(0)
        viewmodel.select_queue_source(2)

        assert viewmodel.selected_queue_indices == {2}
        assert viewmodel.active_queue_source == mock_queue_sources[2]

    def test_ctrl_click_adds_to_selection(self, viewmodel, mock_queue_sources):
        """Ctrl+click adds to selection set."""
        viewmodel.select_queue_source(0)
        viewmodel.select_queue_source(2, ctrl_held=True)

        assert viewmodel.selected_queue_indices == {0, 2}
        assert viewmodel.active_queue_source is None  # Multi-select mode
        assert viewmodel.is_multi_select

    def test_ctrl_click_removes_from_selection(self, viewmodel):
        """Ctrl+click on selected item removes it."""
        viewmodel.select_queue_source(0)
        viewmodel.select_queue_source(1, ctrl_held=True)  # Add
        viewmodel.select_queue_source(0, ctrl_held=True)  # Remove

        assert viewmodel.selected_queue_indices == {1}
        assert viewmodel.is_multi_select is False

    def test_cannot_deselect_last_item(self, viewmodel):
        """Cannot Ctrl+click deselect the last item."""
        viewmodel.select_queue_source(1)
        viewmodel.select_queue_source(1, ctrl_held=True)  # Try to deselect

        assert viewmodel.selected_queue_indices == {1}
        assert viewmodel.active_queue_source is not None

    def test_invalid_index_ignored(self, viewmodel):
        """Invalid index is silently ignored."""
        viewmodel.select_queue_source(99)
        viewmodel.select_queue_source(-1)

        # Initial selection unchanged
        assert viewmodel.selected_queue_indices == {0}

    def test_selection_clears_item_selection(self, viewmodel):
        """Changing queue source clears item selection."""
        viewmodel.select_queue_item(2)
        viewmodel.select_queue_source(1)

        assert viewmodel.selected_queue_index is None

    def test_get_selected_sources(self, viewmodel, mock_queue_sources):
        """get_selected_sources returns sources in index order."""
        viewmodel.select_queue_source(2)
        viewmodel.select_queue_source(0, ctrl_held=True)

        sources = viewmodel.get_selected_sources()
        assert len(sources) == 2
        assert sources[0] == mock_queue_sources[0]
        assert sources[1] == mock_queue_sources[2]


# ---------------------------------------------------------------------------
# Queue Item Selection Tests
# ---------------------------------------------------------------------------

class TestQueueItemSelection:
    """Test queue item selection behavior."""

    def test_select_queue_item(self, viewmodel):
        """Can select a queue item by index."""
        viewmodel.select_queue_item(3)
        assert viewmodel.selected_queue_index == 3

    def test_deselect_queue_item(self, viewmodel):
        """Can deselect queue item with None."""
        viewmodel.select_queue_item(3)
        viewmodel.select_queue_item(None)
        assert viewmodel.selected_queue_index is None

    def test_clear_item_selection(self, viewmodel):
        """clear_item_selection sets index to None."""
        viewmodel.select_queue_item(5)
        viewmodel.clear_item_selection()
        assert viewmodel.selected_queue_index is None

    def test_get_selected_queue_item_none(self, viewmodel):
        """get_selected_queue_item returns None when nothing selected."""
        assert viewmodel.get_selected_queue_item() is None

    def test_get_selected_queue_item_valid(self, viewmodel, mock_queue_sources):
        """get_selected_queue_item returns the item when valid."""
        mock_queue_sources[0].construction_queue = [
            {"design_id": "test_design", "type": "ship", "turns_remaining": 5}
        ]
        viewmodel.select_queue_item(0)

        item = viewmodel.get_selected_queue_item()
        assert item is not None
        assert item["design_id"] == "test_design"


# ---------------------------------------------------------------------------
# Category Filter Tests
# ---------------------------------------------------------------------------

class TestCategoryFilter:
    """Test category filter behavior."""

    def test_set_category(self, viewmodel):
        """Can set category filter."""
        viewmodel.set_category("ship")
        assert viewmodel.selected_category == "ship"

    def test_set_category_all_types(self, viewmodel):
        """All category types are valid."""
        for category in ["complex", "ship", "satellite", "fighter"]:
            viewmodel.set_category(category)
            assert viewmodel.selected_category == category


# ---------------------------------------------------------------------------
# Queue Data Access Tests
# ---------------------------------------------------------------------------

class TestQueueDataAccess:
    """Test queue data access methods."""

    def test_get_active_queue_with_source(self, viewmodel, mock_queue_sources):
        """get_active_queue returns source's construction_queue."""
        mock_queue_sources[0].construction_queue = [{"design_id": "test"}]

        queue = viewmodel.get_active_queue()
        assert len(queue) == 1
        assert queue[0]["design_id"] == "test"

    def test_get_active_queue_empty_viewmodel(self, empty_viewmodel):
        """get_active_queue returns empty list when no source."""
        assert empty_viewmodel.get_active_queue() == []

    def test_get_queue_item_valid(self, viewmodel, mock_queue_sources):
        """get_queue_item returns item at index."""
        mock_queue_sources[0].construction_queue = [
            {"design_id": "item0"},
            {"design_id": "item1"},
        ]

        item = viewmodel.get_queue_item(1)
        assert item["design_id"] == "item1"

    def test_get_queue_item_invalid_index(self, viewmodel, mock_queue_sources):
        """get_queue_item returns None for invalid index."""
        mock_queue_sources[0].construction_queue = [{"design_id": "item0"}]

        assert viewmodel.get_queue_item(5) is None
        assert viewmodel.get_queue_item(-1) is None


# ---------------------------------------------------------------------------
# Event Emission Tests
# ---------------------------------------------------------------------------

class TestEventEmission:
    """Test event emission behavior."""

    def test_source_selection_emits_event(self, viewmodel, event_bus, mock_queue_sources):
        """Selecting source emits ACTIVE_SOURCE_CHANGED event."""
        received = []
        event_bus.subscribe(BuildQueueScreenEvents.ACTIVE_SOURCE_CHANGED, received.append)

        viewmodel.select_queue_source(1)

        assert len(received) == 1
        assert received[0]['active_source'] == mock_queue_sources[1]
        assert received[0]['selected_indices'] == {1}

    def test_item_selection_emits_event(self, viewmodel, event_bus):
        """Selecting item emits SELECTION_CHANGED event."""
        received = []
        event_bus.subscribe(BuildQueueScreenEvents.SELECTION_CHANGED, received.append)

        viewmodel.select_queue_item(3)

        assert len(received) == 1
        assert received[0]['selected_index'] == 3
        assert received[0]['previous_index'] is None

    def test_item_selection_no_event_if_same(self, viewmodel, event_bus):
        """No event emitted if selecting same item."""
        viewmodel.select_queue_item(3)

        received = []
        event_bus.subscribe(BuildQueueScreenEvents.SELECTION_CHANGED, received.append)

        viewmodel.select_queue_item(3)
        assert len(received) == 0

    def test_category_change_emits_event(self, viewmodel, event_bus):
        """Changing category emits CATEGORY_CHANGED event."""
        received = []
        event_bus.subscribe(BuildQueueScreenEvents.CATEGORY_CHANGED, received.append)

        viewmodel.set_category("ship")

        assert len(received) == 1
        assert received[0]['category'] == "ship"
        assert received[0]['previous_category'] == "complex"

    def test_category_no_event_if_same(self, viewmodel, event_bus):
        """No event emitted if setting same category."""
        received = []
        event_bus.subscribe(BuildQueueScreenEvents.CATEGORY_CHANGED, received.append)

        viewmodel.set_category("complex")  # Same as default
        assert len(received) == 0

    def test_notify_queue_refreshed(self, viewmodel, event_bus, mock_queue_sources):
        """notify_queue_refreshed emits QUEUE_REFRESHED event."""
        mock_queue_sources[0].construction_queue = [{"design_id": "x"}, {"design_id": "y"}]

        received = []
        event_bus.subscribe(BuildQueueScreenEvents.QUEUE_REFRESHED, received.append)

        viewmodel.notify_queue_refreshed()

        assert len(received) == 1
        assert received[0]['queue_length'] == 2


# ---------------------------------------------------------------------------
# Multi-Select Mode Tests
# ---------------------------------------------------------------------------

class TestMultiSelectMode:
    """Test multi-select mode behavior."""

    def test_multi_select_clears_active_source(self, viewmodel):
        """Multi-select sets active_source to None."""
        viewmodel.select_queue_source(0)
        viewmodel.select_queue_source(1, ctrl_held=True)

        assert viewmodel.active_queue_source is None
        assert viewmodel.is_multi_select

    def test_single_select_restores_active_source(self, viewmodel, mock_queue_sources):
        """Going from multi to single restores active_source."""
        viewmodel.select_queue_source(0)
        viewmodel.select_queue_source(1, ctrl_held=True)  # Multi
        viewmodel.select_queue_source(2)  # Single

        assert viewmodel.active_queue_source == mock_queue_sources[2]
        assert not viewmodel.is_multi_select

    def test_get_active_queue_in_multi_select(self, viewmodel, mock_queue_sources):
        """get_active_queue returns empty list in multi-select mode."""
        viewmodel.select_queue_source(0)
        viewmodel.select_queue_source(1, ctrl_held=True)

        # active_queue_source is None in multi-select, so empty list
        assert viewmodel.get_active_queue() == []
