"""Tests for StrategySessionFacade event query methods (PROJ-77 Phase 2)."""

import pytest
from unittest.mock import MagicMock

from game.strategy.events import Event, EventLog, EventType, EventCategory
from game.strategy.facade.strategy_session_facade import StrategySessionFacade


def _make_facade_with_events(events: list[Event], turn_number: int = 1) -> StrategySessionFacade:
    """Create a facade with a mock session containing the given events."""
    event_log = EventLog()
    for event in events:
        event_log.append(event)

    mock_session = MagicMock()
    mock_session.event_log = event_log
    mock_session.turn_number = turn_number
    mock_session.empires = []

    return StrategySessionFacade(mock_session)


class TestFacadeGetTurnEvents:
    """Tests for get_turn_events()."""

    def test_returns_events_for_specified_turn(self):
        """get_turn_events(turn) returns events from that turn."""
        events = [
            Event(EventType.SHIP_BUILT, EventCategory.PRODUCTION, turn=1, empire_id=0, message="Turn 1 event"),
            Event(EventType.SHIP_BUILT, EventCategory.PRODUCTION, turn=2, empire_id=0, message="Turn 2 event"),
            Event(EventType.COMBAT_RESOLVED, EventCategory.COMBAT, turn=1, empire_id=1, message="Turn 1 combat"),
        ]
        facade = _make_facade_with_events(events, turn_number=2)

        result = facade.get_turn_events(turn=1)
        assert len(result) == 2
        assert all(e["turn"] == 1 for e in result)

    def test_defaults_to_current_turn(self):
        """get_turn_events() with no arg returns current turn events."""
        events = [
            Event(EventType.SHIP_BUILT, EventCategory.PRODUCTION, turn=3, empire_id=0, message="Current"),
            Event(EventType.SHIP_BUILT, EventCategory.PRODUCTION, turn=2, empire_id=0, message="Previous"),
        ]
        facade = _make_facade_with_events(events, turn_number=3)

        result = facade.get_turn_events()
        assert len(result) == 1
        assert result[0]["message"] == "Current"

    def test_returns_empty_list_for_turn_with_no_events(self):
        """get_turn_events() returns [] when no events exist for that turn."""
        facade = _make_facade_with_events([], turn_number=1)
        assert facade.get_turn_events(turn=5) == []

    def test_returns_dicts_not_event_objects(self):
        """get_turn_events() returns list of dicts (immutable for UI)."""
        events = [
            Event(EventType.SHIP_BUILT, EventCategory.PRODUCTION, turn=1, empire_id=0, message="Test"),
        ]
        facade = _make_facade_with_events(events, turn_number=1)

        result = facade.get_turn_events(turn=1)
        assert len(result) == 1
        assert isinstance(result[0], dict)
        assert result[0]["event_type"] == EventType.SHIP_BUILT
        assert result[0]["message"] == "Test"


class TestFacadeGetAllEvents:
    """Tests for get_all_events()."""

    def test_returns_all_events(self):
        """get_all_events() returns all events across all turns."""
        events = [
            Event(EventType.SHIP_BUILT, EventCategory.PRODUCTION, turn=1, empire_id=0, message="E1"),
            Event(EventType.COLONY_FOUNDED, EventCategory.COLONIES, turn=2, empire_id=0, message="E2"),
            Event(EventType.COMBAT_RESOLVED, EventCategory.COMBAT, turn=3, empire_id=1, message="E3"),
        ]
        facade = _make_facade_with_events(events)

        result = facade.get_all_events()
        assert len(result) == 3

    def test_returns_empty_list_when_no_events(self):
        """get_all_events() returns [] when log is empty."""
        facade = _make_facade_with_events([])
        assert facade.get_all_events() == []

    def test_returns_dicts_not_event_objects(self):
        """get_all_events() returns list of dicts."""
        events = [
            Event(EventType.SHIP_BUILT, EventCategory.PRODUCTION, turn=1, empire_id=0, message="Test"),
        ]
        facade = _make_facade_with_events(events)

        result = facade.get_all_events()
        assert isinstance(result[0], dict)


class TestFacadeGetEventsByCategory:
    """Tests for get_events_by_category()."""

    def test_filters_by_category(self):
        """get_events_by_category() returns only events in the specified category."""
        events = [
            Event(EventType.SHIP_BUILT, EventCategory.PRODUCTION, turn=1, empire_id=0, message="Ship"),
            Event(EventType.COLONY_FOUNDED, EventCategory.COLONIES, turn=1, empire_id=0, message="Colony"),
            Event(EventType.COMPLEX_BUILT, EventCategory.PRODUCTION, turn=1, empire_id=0, message="Complex"),
        ]
        facade = _make_facade_with_events(events)

        result = facade.get_events_by_category(EventCategory.PRODUCTION)
        assert len(result) == 2
        assert all(e["category"] == EventCategory.PRODUCTION for e in result)

    def test_all_category_returns_everything(self):
        """get_events_by_category('all') returns all events."""
        events = [
            Event(EventType.SHIP_BUILT, EventCategory.PRODUCTION, turn=1, empire_id=0, message="Ship"),
            Event(EventType.COMBAT_RESOLVED, EventCategory.COMBAT, turn=1, empire_id=1, message="Battle"),
        ]
        facade = _make_facade_with_events(events)

        result = facade.get_events_by_category(EventCategory.ALL)
        assert len(result) == 2

    def test_returns_empty_for_unmatched_category(self):
        """get_events_by_category() returns [] when no events match."""
        events = [
            Event(EventType.SHIP_BUILT, EventCategory.PRODUCTION, turn=1, empire_id=0, message="Ship"),
        ]
        facade = _make_facade_with_events(events)

        result = facade.get_events_by_category(EventCategory.COMBAT)
        assert result == []

    def test_returns_dicts(self):
        """get_events_by_category() returns list of dicts."""
        events = [
            Event(EventType.COMBAT_RESOLVED, EventCategory.COMBAT, turn=1, empire_id=0, message="Test"),
        ]
        facade = _make_facade_with_events(events)

        result = facade.get_events_by_category(EventCategory.COMBAT)
        assert isinstance(result[0], dict)

    def test_accepts_string_category(self):
        """get_events_by_category() also works with plain string."""
        events = [
            Event(EventType.COLONY_FOUNDED, EventCategory.COLONIES, turn=1, empire_id=0, message="Colony"),
        ]
        facade = _make_facade_with_events(events)

        result = facade.get_events_by_category("colonies")
        assert len(result) == 1


class TestFacadeEventQueriesEmpireScoping:
    """BUG-123: ``empire_id`` kwarg passes through facade -> slice -> EventLog."""

    def _events_for_three_empires(self) -> list:
        return [
            Event(EventType.SHIP_BUILT, EventCategory.PRODUCTION, turn=1, empire_id=0, message="E0"),
            Event(EventType.SHIP_BUILT, EventCategory.PRODUCTION, turn=1, empire_id=1, message="E1"),
            Event(EventType.SHIP_BUILT, EventCategory.PRODUCTION, turn=2, empire_id=0, message="E0t2"),
            Event(EventType.STAR_DESTROYED, EventCategory.SUPERWEAPONS, turn=1, empire_id=-1, message="Global"),
        ]

    def test_get_all_events_scopes_to_empire(self):
        facade = _make_facade_with_events(self._events_for_three_empires())
        result = facade.get_all_events(empire_id=0)
        messages = {e["message"] for e in result}
        assert messages == {"E0", "E0t2", "Global"}
        assert "E1" not in messages

    def test_get_all_events_unscoped_returns_everything(self):
        """Default (no empire_id) preserves prior behaviour."""
        facade = _make_facade_with_events(self._events_for_three_empires())
        result = facade.get_all_events()
        assert len(result) == 4

    def test_get_turn_events_scopes_to_empire(self):
        facade = _make_facade_with_events(self._events_for_three_empires(), turn_number=1)
        result = facade.get_turn_events(turn=1, empire_id=1)
        messages = {e["message"] for e in result}
        assert messages == {"E1", "Global"}

    def test_get_events_by_category_scopes_to_empire(self):
        facade = _make_facade_with_events(self._events_for_three_empires())
        result = facade.get_events_by_category(EventCategory.PRODUCTION, empire_id=0)
        messages = {e["message"] for e in result}
        assert messages == {"E0", "E0t2"}  # Global is SUPERWEAPONS, not PRODUCTION
        assert "E1" not in messages
