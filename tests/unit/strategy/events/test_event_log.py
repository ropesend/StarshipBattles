"""Tests for Event dataclass and EventLog class."""

import pytest

from game.strategy.events.event_log import Event, EventLog
from game.strategy.events.event_types import EventCategory, EventType


# --- Fixtures ---

def _make_event(
    event_type: str = EventType.SHIP_BUILT,
    category: str = EventCategory.PRODUCTION,
    turn: int = 1,
    empire_id: int = 0,
    message: str = "Built Scout at Earth",
    details: dict | None = None,
) -> Event:
    """Helper to create an Event with sensible defaults."""
    return Event(
        event_type=event_type,
        category=category,
        turn=turn,
        empire_id=empire_id,
        message=message,
        details=details if details is not None else {},
    )


# --- Event Dataclass Tests ---

class TestEvent:
    """Tests for the Event dataclass."""

    def test_create_with_all_fields(self) -> None:
        event = Event(
            event_type=EventType.SHIP_BUILT,
            category=EventCategory.PRODUCTION,
            turn=5,
            empire_id=1,
            message="Built Frigate at Luna",
            details={"design_id": "frigate_01", "planet_id": 3},
        )
        assert event.event_type == "ship_built"
        assert event.category == "production"
        assert event.turn == 5
        assert event.empire_id == 1
        assert event.message == "Built Frigate at Luna"
        assert event.details == {"design_id": "frigate_01", "planet_id": 3}

    def test_details_defaults_to_empty_dict(self) -> None:
        event = Event(
            event_type=EventType.COMBAT_RESOLVED,
            category=EventCategory.COMBAT,
            turn=3,
            empire_id=0,
            message="Battle resolved",
        )
        assert event.details == {}

    def test_to_dict_produces_correct_structure(self) -> None:
        event = _make_event(
            turn=7,
            empire_id=2,
            message="Built Scout at Mars",
            details={"design_id": "scout_01"},
        )
        result = event.to_dict()
        assert result == {
            "event_type": "ship_built",
            "category": "production",
            "turn": 7,
            "empire_id": 2,
            "message": "Built Scout at Mars",
            "details": {"design_id": "scout_01"},
        }

    def test_from_dict_reconstructs_event(self) -> None:
        data = {
            "event_type": "colony_founded",
            "category": "colonies",
            "turn": 4,
            "empire_id": 1,
            "message": "Founded colony on Mars",
            "details": {"planet_id": 5},
        }
        event = Event.from_dict(data)
        assert event.event_type == "colony_founded"
        assert event.category == "colonies"
        assert event.turn == 4
        assert event.empire_id == 1
        assert event.message == "Founded colony on Mars"
        assert event.details == {"planet_id": 5}

    def test_serialization_roundtrip(self) -> None:
        original = _make_event(
            event_type=EventType.COMBAT_RESOLVED,
            category=EventCategory.COMBAT,
            turn=10,
            empire_id=3,
            message="Battle at (5,3): 2 fleets engaged",
            details={
                "location": [5, 3],
                "participating_fleet_ids": [7, 12],
                "surviving_fleet_ids": [7],
                "destroyed_fleet_ids": [12],
            },
        )
        restored = Event.from_dict(original.to_dict())
        assert restored.event_type == original.event_type
        assert restored.category == original.category
        assert restored.turn == original.turn
        assert restored.empire_id == original.empire_id
        assert restored.message == original.message
        assert restored.details == original.details

    def test_from_dict_missing_details_defaults_empty(self) -> None:
        data = {
            "event_type": "ship_built",
            "category": "production",
            "turn": 1,
            "empire_id": 0,
            "message": "Built ship",
        }
        event = Event.from_dict(data)
        assert event.details == {}


# --- EventLog Tests ---

class TestEventLog:
    """Tests for the EventLog collection class."""

    def test_empty_log_has_no_events(self) -> None:
        log = EventLog()
        assert log.get_all_events() == []

    def test_append_adds_event(self) -> None:
        log = EventLog()
        event = _make_event()
        log.append(event)
        assert len(log.get_all_events()) == 1
        assert log.get_all_events()[0] is event

    def test_append_multiple_events(self) -> None:
        log = EventLog()
        e1 = _make_event(turn=1, message="First")
        e2 = _make_event(turn=2, message="Second")
        e3 = _make_event(turn=3, message="Third")
        log.append(e1)
        log.append(e2)
        log.append(e3)
        assert len(log.get_all_events()) == 3

    def test_get_events_for_turn_filters_correctly(self) -> None:
        log = EventLog()
        log.append(_make_event(turn=1, message="Turn 1 event A"))
        log.append(_make_event(turn=2, message="Turn 2 event"))
        log.append(_make_event(turn=1, message="Turn 1 event B"))
        log.append(_make_event(turn=3, message="Turn 3 event"))

        turn_1_events = log.get_events_for_turn(1)
        assert len(turn_1_events) == 2
        assert all(e.turn == 1 for e in turn_1_events)

    def test_get_events_for_turn_returns_empty_for_no_match(self) -> None:
        log = EventLog()
        log.append(_make_event(turn=1))
        assert log.get_events_for_turn(99) == []

    def test_get_events_by_category_filters_correctly(self) -> None:
        log = EventLog()
        log.append(_make_event(category=EventCategory.PRODUCTION, message="Prod 1"))
        log.append(_make_event(category=EventCategory.COMBAT, message="Combat 1"))
        log.append(_make_event(category=EventCategory.PRODUCTION, message="Prod 2"))
        log.append(_make_event(category=EventCategory.COLONIES, message="Colony 1"))

        production_events = log.get_events_by_category(EventCategory.PRODUCTION)
        assert len(production_events) == 2
        assert all(e.category == "production" for e in production_events)

    def test_get_events_by_category_all_returns_everything(self) -> None:
        log = EventLog()
        log.append(_make_event(category=EventCategory.PRODUCTION))
        log.append(_make_event(category=EventCategory.COMBAT))
        log.append(_make_event(category=EventCategory.COLONIES))

        all_events = log.get_events_by_category(EventCategory.ALL)
        assert len(all_events) == 3

    def test_get_events_by_category_string_value(self) -> None:
        """Category filtering also works with raw string values."""
        log = EventLog()
        log.append(_make_event(category=EventCategory.COMBAT))
        log.append(_make_event(category=EventCategory.PRODUCTION))

        combat_events = log.get_events_by_category("combat")
        assert len(combat_events) == 1

    def test_get_events_by_category_all_string_value(self) -> None:
        """Filtering with 'all' string also returns everything."""
        log = EventLog()
        log.append(_make_event(category=EventCategory.COMBAT))
        log.append(_make_event(category=EventCategory.PRODUCTION))

        all_events = log.get_events_by_category("all")
        assert len(all_events) == 2

    def test_to_dict_serializes_all_events(self) -> None:
        log = EventLog()
        log.append(_make_event(turn=1, message="Event A"))
        log.append(_make_event(turn=2, message="Event B"))

        data = log.to_dict()
        assert "events" in data
        assert len(data["events"]) == 2
        assert data["events"][0]["message"] == "Event A"
        assert data["events"][1]["message"] == "Event B"

    def test_from_dict_restores_all_events(self) -> None:
        data = {
            "events": [
                {
                    "event_type": "ship_built",
                    "category": "production",
                    "turn": 1,
                    "empire_id": 0,
                    "message": "Built Scout",
                    "details": {},
                },
                {
                    "event_type": "combat_resolved",
                    "category": "combat",
                    "turn": 2,
                    "empire_id": 1,
                    "message": "Battle resolved",
                    "details": {"winner": 7},
                },
            ]
        }
        log = EventLog.from_dict(data)
        events = log.get_all_events()
        assert len(events) == 2
        assert events[0].event_type == "ship_built"
        assert events[1].event_type == "combat_resolved"
        assert events[1].details == {"winner": 7}

    def test_from_dict_empty_events(self) -> None:
        data = {"events": []}
        log = EventLog.from_dict(data)
        assert log.get_all_events() == []

    def test_serialization_roundtrip(self) -> None:
        log = EventLog()
        log.append(_make_event(
            event_type=EventType.SHIP_BUILT,
            category=EventCategory.PRODUCTION,
            turn=5,
            empire_id=0,
            message="Built Scout at Earth",
            details={"design_id": "scout_01"},
        ))
        log.append(_make_event(
            event_type=EventType.COMBAT_RESOLVED,
            category=EventCategory.COMBAT,
            turn=5,
            empire_id=1,
            message="Battle at (3,4)",
            details={"location": [3, 4]},
        ))
        log.append(_make_event(
            event_type=EventType.COLONY_FOUNDED,
            category=EventCategory.COLONIES,
            turn=4,
            empire_id=0,
            message="Founded colony on Mars",
            details={"planet_id": 7},
        ))

        restored = EventLog.from_dict(log.to_dict())
        restored_events = restored.get_all_events()
        original_events = log.get_all_events()
        assert len(restored_events) == len(original_events)
        for orig, rest in zip(original_events, restored_events):
            assert orig.event_type == rest.event_type
            assert orig.category == rest.category
            assert orig.turn == rest.turn
            assert orig.empire_id == rest.empire_id
            assert orig.message == rest.message
            assert orig.details == rest.details


# --- Phase 5: Additional Edge Case Tests ---


class TestEventLogFilteringEdgeCases:
    """Phase 5 Task 5.1: Edge case tests for EventLog filtering."""

    def test_filter_by_category_with_all_four_types(self) -> None:
        """Filtering returns correct counts across all event types."""
        log = EventLog()
        log.append(_make_event(event_type=EventType.SHIP_BUILT, category=EventCategory.PRODUCTION, turn=1))
        log.append(_make_event(event_type=EventType.COMPLEX_BUILT, category=EventCategory.PRODUCTION, turn=1))
        log.append(_make_event(event_type=EventType.COLONY_FOUNDED, category=EventCategory.COLONIES, turn=2))
        log.append(_make_event(event_type=EventType.COMBAT_RESOLVED, category=EventCategory.COMBAT, turn=2))

        assert len(log.get_events_by_category(EventCategory.PRODUCTION)) == 2
        assert len(log.get_events_by_category(EventCategory.COLONIES)) == 1
        assert len(log.get_events_by_category(EventCategory.COMBAT)) == 1
        assert len(log.get_events_by_category(EventCategory.ALL)) == 4

    def test_filter_by_turn_with_events_from_different_turns(self) -> None:
        """get_events_for_turn returns only events from the requested turn."""
        log = EventLog()
        for turn in range(1, 6):
            log.append(_make_event(turn=turn, message=f"Turn {turn} event A"))
            log.append(_make_event(turn=turn, message=f"Turn {turn} event B"))

        for turn in range(1, 6):
            turn_events = log.get_events_for_turn(turn)
            assert len(turn_events) == 2
            assert all(e.turn == turn for e in turn_events)

    def test_filter_by_turn_returns_empty_for_nonexistent_turn(self) -> None:
        """get_events_for_turn returns [] for a turn with no events."""
        log = EventLog()
        log.append(_make_event(turn=3))
        assert log.get_events_for_turn(99) == []

    def test_filter_by_category_returns_empty_for_unused_category(self) -> None:
        """get_events_by_category returns [] for categories with no events."""
        log = EventLog()
        log.append(_make_event(category=EventCategory.PRODUCTION))
        assert log.get_events_by_category(EventCategory.COMBAT) == []
        assert log.get_events_by_category(EventCategory.COLONIES) == []

    def test_serialization_roundtrip_all_event_types(self) -> None:
        """Save/load preserves events of every EventType."""
        log = EventLog()
        log.append(_make_event(event_type=EventType.SHIP_BUILT, category=EventCategory.PRODUCTION,
                               message="Ship", details={"design_id": "scout"}))
        log.append(_make_event(event_type=EventType.COMPLEX_BUILT, category=EventCategory.PRODUCTION,
                               message="Complex", details={"design_id": "mine"}))
        log.append(_make_event(event_type=EventType.COLONY_FOUNDED, category=EventCategory.COLONIES,
                               message="Colony", details={"planet_id": 5}))
        log.append(_make_event(event_type=EventType.COMBAT_RESOLVED, category=EventCategory.COMBAT,
                               message="Combat", details={"surviving_fleet_ids": [1]}))

        restored = EventLog.from_dict(log.to_dict())
        restored_events = restored.get_all_events()
        assert len(restored_events) == 4
        assert restored_events[0].event_type == EventType.SHIP_BUILT.value
        assert restored_events[1].event_type == EventType.COMPLEX_BUILT.value
        assert restored_events[2].event_type == EventType.COLONY_FOUNDED.value
        assert restored_events[3].event_type == EventType.COMBAT_RESOLVED.value

    def test_empty_eventlog_to_dict_and_from_dict(self) -> None:
        """Empty EventLog serializes and deserializes cleanly."""
        log = EventLog()
        data = log.to_dict()
        assert data == {"events": []}
        restored = EventLog.from_dict(data)
        assert restored.get_all_events() == []

    def test_large_eventlog_performance(self) -> None:
        """EventLog handles 200+ events without issues."""
        log = EventLog()
        for i in range(200):
            category = [EventCategory.PRODUCTION, EventCategory.COMBAT, EventCategory.COLONIES][i % 3]
            log.append(_make_event(
                turn=i // 10 + 1,
                empire_id=i % 2,
                category=category,
                message=f"Event {i}",
            ))

        assert len(log.get_all_events()) == 200

        # Filter by turn
        turn_1_events = log.get_events_for_turn(1)
        assert len(turn_1_events) == 10

        # Filter by category
        production = log.get_events_by_category(EventCategory.PRODUCTION)
        # Events 0,3,6,9... are production (every 3rd starting from 0)
        expected_count = len([i for i in range(200) if i % 3 == 0])
        assert len(production) == expected_count

        # Roundtrip
        restored = EventLog.from_dict(log.to_dict())
        assert len(restored.get_all_events()) == 200

    def test_from_dict_missing_events_key(self) -> None:
        """from_dict with empty dict creates empty EventLog."""
        log = EventLog.from_dict({})
        assert log.get_all_events() == []

    def test_get_all_events_returns_copy(self) -> None:
        """get_all_events should return a copy, not the internal list."""
        log = EventLog()
        event = _make_event()
        log.append(event)
        events = log.get_all_events()
        events.clear()  # Mutate the returned list
        assert len(log.get_all_events()) == 1  # Internal list unaffected


# --- BUG-123: Per-empire filtering ---


class TestEventLogPerEmpireFilter:
    """BUG-123: Event Log scopes events to a single empire's view.

    The ``-1`` empire_id is the existing sentinel used by
    ``GameSession._create_event_handler`` for events whose owner is
    "the world" (environmental hazards, star destruction, etc.).
    Default contract: those events broadcast to every empire.
    """

    def test_get_events_for_empire_filters_by_empire_id(self) -> None:
        log = EventLog()
        log.append(_make_event(empire_id=0, message="Empire 0 build"))
        log.append(_make_event(empire_id=1, message="Empire 1 build"))
        log.append(_make_event(empire_id=0, message="Empire 0 colony"))
        log.append(_make_event(empire_id=2, message="Empire 2 stuff"))

        empire_0 = log.get_events_for_empire(0)
        assert len(empire_0) == 2
        assert all(e.empire_id == 0 for e in empire_0)
        assert {e.message for e in empire_0} == {"Empire 0 build", "Empire 0 colony"}

    def test_get_events_for_empire_returns_empty_for_unknown_empire(self) -> None:
        log = EventLog()
        log.append(_make_event(empire_id=0))
        assert log.get_events_for_empire(99) == []

    def test_get_events_for_empire_includes_global_events_by_default(self) -> None:
        """empire_id=-1 events are visible to every empire (broadcast)."""
        log = EventLog()
        log.append(_make_event(empire_id=0, message="Empire 0"))
        log.append(_make_event(empire_id=1, message="Empire 1"))
        log.append(_make_event(empire_id=-1, message="Star destroyed"))

        for filter_empire in (0, 1):
            scoped = log.get_events_for_empire(filter_empire)
            messages = {e.message for e in scoped}
            assert "Star destroyed" in messages, (
                f"Empire {filter_empire} should see global events"
            )

    def test_get_events_for_empire_excludes_globals_when_opted_out(self) -> None:
        """include_global=False suppresses the empire_id=-1 broadcast."""
        log = EventLog()
        log.append(_make_event(empire_id=0, message="Mine"))
        log.append(_make_event(empire_id=-1, message="Star destroyed"))

        scoped = log.get_events_for_empire(0, include_global=False)
        assert len(scoped) == 1
        assert scoped[0].message == "Mine"

    def test_get_events_for_empire_does_not_leak_other_empires(self) -> None:
        """No event with empire_id != active_empire ever crosses the filter."""
        log = EventLog()
        log.append(_make_event(empire_id=0, message="Mine"))
        log.append(_make_event(empire_id=1, message="Theirs"))
        log.append(_make_event(empire_id=2, message="Also theirs"))

        scoped = log.get_events_for_empire(0)
        assert all(e.empire_id in (0, -1) for e in scoped)
        assert "Theirs" not in {e.message for e in scoped}
        assert "Also theirs" not in {e.message for e in scoped}

    def test_get_events_for_turn_with_empire_id_kwarg(self) -> None:
        """Optional empire_id kwarg combines with turn filtering."""
        log = EventLog()
        log.append(_make_event(turn=1, empire_id=0, message="T1 mine"))
        log.append(_make_event(turn=1, empire_id=1, message="T1 theirs"))
        log.append(_make_event(turn=2, empire_id=0, message="T2 mine"))
        log.append(_make_event(turn=1, empire_id=-1, message="T1 global"))

        scoped = log.get_events_for_turn(1, empire_id=0)
        messages = {e.message for e in scoped}
        assert messages == {"T1 mine", "T1 global"}

    def test_get_events_for_turn_without_empire_id_unchanged(self) -> None:
        """Existing get_events_for_turn callers unaffected by the new kwarg."""
        log = EventLog()
        log.append(_make_event(turn=1, empire_id=0))
        log.append(_make_event(turn=1, empire_id=1))
        log.append(_make_event(turn=2, empire_id=0))

        assert len(log.get_events_for_turn(1)) == 2  # both empires

    def test_get_events_by_category_with_empire_id_kwarg(self) -> None:
        """Category filter composes with the empire_id kwarg."""
        log = EventLog()
        log.append(_make_event(category=EventCategory.PRODUCTION, empire_id=0, message="P0"))
        log.append(_make_event(category=EventCategory.PRODUCTION, empire_id=1, message="P1"))
        log.append(_make_event(category=EventCategory.COMBAT, empire_id=0, message="C0"))
        log.append(_make_event(category=EventCategory.PRODUCTION, empire_id=-1, message="Pglobal"))

        scoped = log.get_events_by_category(EventCategory.PRODUCTION, empire_id=0)
        assert {e.message for e in scoped} == {"P0", "Pglobal"}

    def test_get_events_by_category_all_with_empire_id_kwarg(self) -> None:
        """ALL category + empire_id returns every event scoped to that empire."""
        log = EventLog()
        log.append(_make_event(category=EventCategory.PRODUCTION, empire_id=0))
        log.append(_make_event(category=EventCategory.COMBAT, empire_id=0))
        log.append(_make_event(category=EventCategory.PRODUCTION, empire_id=1))

        scoped = log.get_events_by_category(EventCategory.ALL, empire_id=0)
        assert len(scoped) == 2
        assert all(e.empire_id == 0 for e in scoped)

    def test_get_events_by_category_without_empire_id_unchanged(self) -> None:
        """Existing category callers unaffected."""
        log = EventLog()
        log.append(_make_event(category=EventCategory.PRODUCTION, empire_id=0))
        log.append(_make_event(category=EventCategory.PRODUCTION, empire_id=1))

        assert len(log.get_events_by_category(EventCategory.PRODUCTION)) == 2
