"""Tests for EventLogDataSource (PROJ-188 Phase 5).

Verifies the EventLogDataSource adapter for VirtualTable:
- Column definitions
- Row count and cell value extraction
- Category filtering (all, combat, production, colonies)
- Newest-first sorting
- Event data update
"""

import pytest

from game.ui.screens.event_log_data_source import (
    EventLogDataSource,
    EVENT_LOG_COLUMNS,
    CATEGORY_ICONS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_event(
    event_type: str = "ship_built",
    category: str = "production",
    turn: int = 1,
    empire_id: int = 0,
    message: str = "A ship was built",
    details: dict = None,
) -> dict:
    """Create an event dict matching facade output format."""
    return {
        "event_type": event_type,
        "category": category,
        "turn": turn,
        "empire_id": empire_id,
        "message": message,
        "details": details or {},
    }


def _sample_events() -> list:
    """Return a list of sample events across categories."""
    return [
        _make_event("ship_built", "production", 1, 0, "Frigate built at Alpha"),
        _make_event("complex_built", "production", 1, 0, "Mine built at Alpha"),
        _make_event("colony_founded", "colonies", 2, 0, "Colony on Beta"),
        _make_event("combat_resolved", "combat", 2, 0, "Battle at Gamma"),
        _make_event("ship_built", "production", 3, 0, "Cruiser built at Delta"),
    ]


# ---------------------------------------------------------------------------
# Column Definitions
# ---------------------------------------------------------------------------

class TestEventLogColumns:
    """Test EVENT_LOG_COLUMNS constant."""

    def test_column_count(self):
        """Should have exactly 7 columns (category, turn, system, planet, local_hex, galaxy_hex, message)."""
        assert len(EVENT_LOG_COLUMNS) == 7

    def test_category_column(self):
        """Category column should have correct definition."""
        col = EVENT_LOG_COLUMNS[0]
        assert col["id"] == "category"
        assert col["title"] == "Category"
        assert col["visible"] is True
        assert col["sortable"] is True
        assert isinstance(col["width"], int)

    def test_turn_column(self):
        """Turn column should have correct definition."""
        col = EVENT_LOG_COLUMNS[1]
        assert col["id"] == "turn"
        assert col["title"] == "Turn"
        assert col["visible"] is True
        assert col["sortable"] is True
        assert isinstance(col["width"], int)

    def test_message_column(self):
        """Message column should have correct definition."""
        # Message is now at index 6 (after 4 location columns)
        col = EVENT_LOG_COLUMNS[6]
        assert col["id"] == "message"
        assert col["title"] == "Message"
        assert col["visible"] is True
        assert col["sortable"] is True
        assert isinstance(col["width"], int)


class TestCategoryIcons:
    """Test CATEGORY_ICONS constant."""

    def test_combat_icon(self):
        """Combat category should have icon."""
        assert "combat" in CATEGORY_ICONS
        assert "[Combat]" in CATEGORY_ICONS["combat"]

    def test_production_icon(self):
        """Production category should have icon."""
        assert "production" in CATEGORY_ICONS
        assert "[Prod]" in CATEGORY_ICONS["production"]

    def test_colonies_icon(self):
        """Colonies category should have icon."""
        assert "colonies" in CATEGORY_ICONS
        assert "[Colony]" in CATEGORY_ICONS["colonies"]


# ---------------------------------------------------------------------------
# DataSource Initialization
# ---------------------------------------------------------------------------

class TestEventLogDataSourceInit:
    """Test EventLogDataSource initialization."""

    def test_empty_events(self):
        """Should handle empty events list."""
        ds = EventLogDataSource([])
        assert ds.get_row_count() == 0

    def test_with_events(self):
        """Should store events on init."""
        events = _sample_events()
        ds = EventLogDataSource(events)
        assert ds.get_row_count() == 5

    def test_default_filter_is_all(self):
        """Default filter should be 'all'."""
        ds = EventLogDataSource(_sample_events())
        assert ds._current_filter == "all"

    def test_custom_initial_filter(self):
        """Should accept custom initial filter."""
        ds = EventLogDataSource(_sample_events(), current_filter="combat")
        assert ds._current_filter == "combat"
        assert ds.get_row_count() == 1


# ---------------------------------------------------------------------------
# get_columns
# ---------------------------------------------------------------------------

class TestGetColumns:
    """Test get_columns method."""

    def test_returns_event_log_columns(self):
        """Should return EVENT_LOG_COLUMNS."""
        ds = EventLogDataSource([])
        cols = ds.get_columns()
        assert cols == EVENT_LOG_COLUMNS

    def test_returns_list_of_dicts(self):
        """Columns should be list of dicts."""
        ds = EventLogDataSource([])
        cols = ds.get_columns()
        assert isinstance(cols, list)
        assert all(isinstance(c, dict) for c in cols)


# ---------------------------------------------------------------------------
# get_row_count
# ---------------------------------------------------------------------------

class TestGetRowCount:
    """Test get_row_count method."""

    def test_empty_events(self):
        """Should return 0 for empty events."""
        ds = EventLogDataSource([])
        assert ds.get_row_count() == 0

    def test_all_filter(self):
        """Should return all events with 'all' filter."""
        ds = EventLogDataSource(_sample_events())
        ds.set_filter("all")
        assert ds.get_row_count() == 5

    def test_combat_filter(self):
        """Should return only combat events with 'combat' filter."""
        ds = EventLogDataSource(_sample_events())
        ds.set_filter("combat")
        assert ds.get_row_count() == 1

    def test_production_filter(self):
        """Should return only production events with 'production' filter."""
        ds = EventLogDataSource(_sample_events())
        ds.set_filter("production")
        assert ds.get_row_count() == 3

    def test_colonies_filter(self):
        """Should return only colonies events with 'colonies' filter."""
        ds = EventLogDataSource(_sample_events())
        ds.set_filter("colonies")
        assert ds.get_row_count() == 1


# ---------------------------------------------------------------------------
# get_cell_value
# ---------------------------------------------------------------------------

class TestGetCellValue:
    """Test get_cell_value method."""

    def test_category_column_combat(self):
        """Category column should show icon + name for combat."""
        events = [_make_event("combat", "combat", 1, 0, "Battle")]
        ds = EventLogDataSource(events)
        value = ds.get_cell_value(0, "category")
        assert "[Combat]" in value

    def test_category_column_production(self):
        """Category column should show icon + name for production."""
        events = [_make_event("ship_built", "production", 1, 0, "Ship")]
        ds = EventLogDataSource(events)
        value = ds.get_cell_value(0, "category")
        assert "[Prod]" in value

    def test_category_column_colonies(self):
        """Category column should show icon + name for colonies."""
        events = [_make_event("colony_founded", "colonies", 1, 0, "Colony")]
        ds = EventLogDataSource(events)
        value = ds.get_cell_value(0, "category")
        assert "[Colony]" in value

    def test_turn_column(self):
        """Turn column should return string turn number."""
        events = [_make_event("ship_built", "production", 42, 0, "Ship")]
        ds = EventLogDataSource(events)
        value = ds.get_cell_value(0, "turn")
        assert value == "42"

    def test_message_column(self):
        """Message column should return message text."""
        events = [_make_event("ship_built", "production", 1, 0, "Frigate at Alpha")]
        ds = EventLogDataSource(events)
        value = ds.get_cell_value(0, "message")
        assert value == "Frigate at Alpha"

    def test_out_of_bounds_row(self):
        """Should return empty string for out of bounds row."""
        ds = EventLogDataSource([_make_event()])
        assert ds.get_cell_value(99, "turn") == ""

    def test_unknown_column(self):
        """Should return empty string for unknown column."""
        ds = EventLogDataSource([_make_event()])
        assert ds.get_cell_value(0, "unknown_col") == ""

    def test_missing_category(self):
        """Should handle event with missing category."""
        events = [{"turn": 1, "message": "Test"}]
        ds = EventLogDataSource(events)
        value = ds.get_cell_value(0, "category")
        # Should return empty or default when category missing
        assert value is not None


# ---------------------------------------------------------------------------
# Sorting (newest first)
# ---------------------------------------------------------------------------

class TestEventSorting:
    """Test events are sorted newest first (descending by turn)."""

    def test_sorted_newest_first(self):
        """Filtered events should be sorted newest first."""
        events = [
            _make_event("a", "production", 1, 0, "First"),
            _make_event("b", "production", 3, 0, "Third"),
            _make_event("c", "production", 2, 0, "Second"),
        ]
        ds = EventLogDataSource(events)
        # With production filter, should get 3 events sorted by turn desc
        ds.set_filter("production")
        assert ds.get_row_count() == 3
        # First row should be turn 3 (newest)
        assert ds.get_cell_value(0, "turn") == "3"
        # Second row should be turn 2
        assert ds.get_cell_value(1, "turn") == "2"
        # Third row should be turn 1
        assert ds.get_cell_value(2, "turn") == "1"

    def test_sorting_with_all_filter(self):
        """Sorting should work with 'all' filter too."""
        events = _sample_events()
        ds = EventLogDataSource(events)
        ds.set_filter("all")
        # First event should be turn 3 (highest)
        assert ds.get_cell_value(0, "turn") == "3"


# ---------------------------------------------------------------------------
# set_filter
# ---------------------------------------------------------------------------

class TestSetFilter:
    """Test set_filter method."""

    def test_filter_all(self):
        """set_filter('all') should show all events."""
        ds = EventLogDataSource(_sample_events())
        ds.set_filter("all")
        assert ds.get_row_count() == 5

    def test_filter_combat(self):
        """set_filter('combat') should show only combat events."""
        ds = EventLogDataSource(_sample_events())
        ds.set_filter("combat")
        assert ds.get_row_count() == 1
        assert ds.get_cell_value(0, "message") == "Battle at Gamma"

    def test_filter_production(self):
        """set_filter('production') should show only production events."""
        ds = EventLogDataSource(_sample_events())
        ds.set_filter("production")
        assert ds.get_row_count() == 3

    def test_filter_colonies(self):
        """set_filter('colonies') should show only colonies events."""
        ds = EventLogDataSource(_sample_events())
        ds.set_filter("colonies")
        assert ds.get_row_count() == 1
        assert ds.get_cell_value(0, "message") == "Colony on Beta"

    def test_filter_empty_category(self):
        """Filter for category with no events should return 0 rows."""
        events = [_make_event("ship", "production", 1, 0, "Ship")]
        ds = EventLogDataSource(events)
        ds.set_filter("combat")
        assert ds.get_row_count() == 0


# ---------------------------------------------------------------------------
# update_events
# ---------------------------------------------------------------------------

class TestUpdateEvents:
    """Test update_events method."""

    def test_update_replaces_data(self):
        """update_events should replace all event data."""
        ds = EventLogDataSource([_make_event()])
        assert ds.get_row_count() == 1

        new_events = [
            _make_event("a", "combat", 1, 0, "A"),
            _make_event("b", "combat", 2, 0, "B"),
        ]
        ds.update_events(new_events)
        assert ds.get_row_count() == 2

    def test_update_reapplies_filter(self):
        """update_events should reapply current filter."""
        events = [_make_event("ship", "production", 1, 0, "Ship")]
        ds = EventLogDataSource(events)
        ds.set_filter("combat")
        assert ds.get_row_count() == 0  # No combat events

        # Add combat event
        new_events = [
            _make_event("ship", "production", 1, 0, "Ship"),
            _make_event("battle", "combat", 2, 0, "Battle"),
        ]
        ds.update_events(new_events)
        # Combat filter still applied, now shows 1
        assert ds.get_row_count() == 1

    def test_update_to_empty(self):
        """update_events with empty list should clear data."""
        ds = EventLogDataSource(_sample_events())
        assert ds.get_row_count() == 5
        ds.update_events([])
        assert ds.get_row_count() == 0


# ---------------------------------------------------------------------------
# get_event_at_index
# ---------------------------------------------------------------------------

class TestGetEventAtIndex:
    """Test get_event_at_index method."""

    def test_valid_index(self):
        """Should return event dict at valid index."""
        events = _sample_events()
        ds = EventLogDataSource(events)
        # After sorting, first event is turn 3
        event = ds.get_event_at_index(0)
        assert event is not None
        assert event["turn"] == 3

    def test_out_of_bounds(self):
        """Should return None for out of bounds index."""
        ds = EventLogDataSource([_make_event()])
        assert ds.get_event_at_index(99) is None

    def test_negative_index(self):
        """Should return None for negative index."""
        ds = EventLogDataSource([_make_event()])
        assert ds.get_event_at_index(-1) is None

    def test_respects_filter(self):
        """Should return filtered event at index."""
        ds = EventLogDataSource(_sample_events())
        ds.set_filter("combat")
        event = ds.get_event_at_index(0)
        assert event is not None
        assert event["category"] == "combat"


# ---------------------------------------------------------------------------
# PROJ-215: Granular Location Columns (System, Planet, Local Hex, Galaxy Hex)
# ---------------------------------------------------------------------------

class TestGranularLocationColumns:
    """Test granular location columns replacing single Location column."""

    def test_column_count(self):
        """EVENT_LOG_COLUMNS should have 7 columns."""
        assert len(EVENT_LOG_COLUMNS) == 7

    def test_system_column_definition(self):
        """System column should exist with correct definition."""
        col = next((c for c in EVENT_LOG_COLUMNS if c["id"] == "system"), None)
        assert col is not None
        assert col["title"] == "System"
        assert col["visible"] is True
        assert col["sortable"] is True
        assert isinstance(col["width"], int)

    def test_planet_column_definition(self):
        """Planet column should exist with correct definition."""
        col = next((c for c in EVENT_LOG_COLUMNS if c["id"] == "planet"), None)
        assert col is not None
        assert col["title"] == "Planet"
        assert col["visible"] is True
        assert col["sortable"] is True
        assert isinstance(col["width"], int)

    def test_local_hex_column_definition(self):
        """Local Hex column should exist with correct definition (hidden by default)."""
        col = next((c for c in EVENT_LOG_COLUMNS if c["id"] == "local_hex"), None)
        assert col is not None
        assert col["title"] == "Local Hex"
        assert col["visible"] is False  # Hidden by default
        assert col["sortable"] is True
        assert isinstance(col["width"], int)

    def test_galaxy_hex_column_definition(self):
        """Galaxy Hex column should exist with correct definition (hidden by default)."""
        col = next((c for c in EVENT_LOG_COLUMNS if c["id"] == "galaxy_hex"), None)
        assert col is not None
        assert col["title"] == "Galaxy Hex"
        assert col["visible"] is False  # Hidden by default
        assert col["sortable"] is True
        assert isinstance(col["width"], int)

    def test_system_cell_value(self):
        """System column should display system_name from event details."""
        events = [_make_event(details={"system_name": "Lincoln"})]
        ds = EventLogDataSource(events)
        value = ds.get_cell_value(0, "system")
        assert value == "Lincoln"

    def test_system_cell_value_empty(self):
        """System column should return empty string when no system_name."""
        events = [_make_event(details={})]
        ds = EventLogDataSource(events)
        value = ds.get_cell_value(0, "system")
        assert value == ""

    def test_planet_cell_value(self):
        """Planet column should display location_name from event details."""
        events = [_make_event(details={"location_name": "Lincoln I"})]
        ds = EventLogDataSource(events)
        value = ds.get_cell_value(0, "planet")
        assert value == "Lincoln I"

    def test_planet_cell_value_empty(self):
        """Planet column should return empty string when no location_name."""
        events = [_make_event(details={})]
        ds = EventLogDataSource(events)
        value = ds.get_cell_value(0, "planet")
        assert value == ""

    def test_local_hex_cell_value(self):
        """Local Hex column should format local_hex as (q, r)."""
        events = [_make_event(details={"local_hex": [2, -1]})]
        ds = EventLogDataSource(events)
        value = ds.get_cell_value(0, "local_hex")
        assert value == "(2, -1)"

    def test_local_hex_cell_value_empty(self):
        """Local Hex column should return empty string when no local_hex."""
        events = [_make_event(details={})]
        ds = EventLogDataSource(events)
        value = ds.get_cell_value(0, "local_hex")
        assert value == ""

    def test_galaxy_hex_cell_value(self):
        """Galaxy Hex column should format location_hex as (q, r)."""
        events = [_make_event(details={"location_hex": [5, 3]})]
        ds = EventLogDataSource(events)
        value = ds.get_cell_value(0, "galaxy_hex")
        assert value == "(5, 3)"

    def test_galaxy_hex_cell_value_empty(self):
        """Galaxy Hex column should return empty string when no location_hex."""
        events = [_make_event(details={})]
        ds = EventLogDataSource(events)
        value = ds.get_cell_value(0, "galaxy_hex")
        assert value == ""

    def test_location_column_removed(self):
        """Old location column should no longer exist."""
        col = next((c for c in EVENT_LOG_COLUMNS if c["id"] == "location"), None)
        assert col is None
