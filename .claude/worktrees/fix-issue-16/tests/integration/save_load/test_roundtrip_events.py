"""Round-trip tests for Event and EventLog serialization (PROJ-223 Phase 2)."""

import pytest

from game.strategy.events.event_log import Event, EventLog
from tests.fixtures.strategy_entities import create_test_event, create_test_event_log
from tests.integration.save_load.conftest import assert_round_trip_fidelity


class TestEventRoundTrip:
    """Event round-trip serialization tests."""

    def test_to_dict_includes_all_6_fields(self):
        e = create_test_event()
        d = e.to_dict()
        expected = ['event_type', 'category', 'turn', 'empire_id', 'message', 'details']
        for key in expected:
            assert key in d, f"Missing key: {key}"

    def test_from_dict_restores_all_fields(self):
        original = create_test_event()
        d = original.to_dict()
        restored = Event.from_dict(d)
        assert restored.event_type == original.event_type
        assert restored.category == original.category
        assert restored.turn == original.turn
        assert restored.empire_id == original.empire_id
        assert restored.message == original.message
        assert restored.details == original.details

    def test_round_trip_field_level(self):
        assert_round_trip_fidelity(create_test_event(), Event)

    def test_event_with_complex_details(self):
        e = create_test_event(details={
            "ships_destroyed": 3,
            "damage_dealt": 450.5,
            "participants": ["fleet_1", "fleet_2"],
        })
        restored = assert_round_trip_fidelity(e, Event)
        assert restored.details["ships_destroyed"] == 3
        assert restored.details["damage_dealt"] == 450.5


class TestEventLogRoundTrip:
    """EventLog round-trip serialization tests."""

    def test_to_dict_includes_events_array(self):
        log = create_test_event_log()
        d = log.to_dict()
        assert 'events' in d
        assert isinstance(d['events'], list)
        assert len(d['events']) == 3

    def test_from_dict_restores_all_events(self):
        original = create_test_event_log(num_events=5)
        d = original.to_dict()
        restored = EventLog.from_dict(d)
        assert len(restored.get_all_events()) == 5
        for orig, rest in zip(original.get_all_events(), restored.get_all_events()):
            assert rest.event_type == orig.event_type
            assert rest.turn == orig.turn

    def test_round_trip_field_level(self):
        assert_round_trip_fidelity(create_test_event_log(), EventLog)

    def test_empty_event_log_round_trip(self):
        log = EventLog()
        d = log.to_dict()
        restored = EventLog.from_dict(d)
        assert len(restored.get_all_events()) == 0

    def test_multiple_event_types(self):
        log = create_test_event_log(num_events=6)
        restored = assert_round_trip_fidelity(log, EventLog)
        events = restored.get_all_events()
        categories = {e.category for e in events}
        assert len(categories) >= 2  # Should have multiple categories
