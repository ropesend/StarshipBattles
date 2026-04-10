"""Tests for EventType and EventCategory enums."""

from game.strategy.events.event_types import EventCategory, EventType


class TestEventType:
    """Tests for the EventType enum."""

    def test_all_values_are_strings(self) -> None:
        for member in EventType:
            assert isinstance(member.value, str)


class TestEventCategory:
    """Tests for the EventCategory enum."""

    def test_all_values_are_strings(self) -> None:
        for member in EventCategory:
            assert isinstance(member.value, str)
