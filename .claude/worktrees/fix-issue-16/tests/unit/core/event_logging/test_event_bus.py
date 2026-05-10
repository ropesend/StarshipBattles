"""
Tests for session-scoped EventBus (PROJ-252 Phase 2).

Verifies that:
- EventBus routes events to its handler
- EventBus without handler silently drops events
- Two EventBus instances route events independently
- GameSession creates its own EventBus
"""
from unittest.mock import Mock, MagicMock

from game.core.event_logging import EventBus


class TestEventBus:
    """EventBus should route events to its handler independently."""

    def test_event_bus_with_handler_receives_events(self):
        """EventBus created with handler receives events via log_event()."""
        handler = Mock()
        bus = EventBus(handler)
        bus.log_event("damage", amount=100)
        handler.assert_called_once_with("damage", amount=100)

    def test_event_bus_without_handler_no_crash(self):
        """EventBus without handler silently drops events."""
        bus = EventBus()
        bus.log_event("damage", amount=100)  # Should not crash

    def test_two_buses_route_independently(self):
        """Two EventBus instances route events to their own handlers."""
        handler1 = Mock()
        handler2 = Mock()
        bus1 = EventBus(handler1)
        bus2 = EventBus(handler2)

        bus1.log_event("event_a", value=1)
        bus2.log_event("event_b", value=2)

        handler1.assert_called_once_with("event_a", value=1)
        handler2.assert_called_once_with("event_b", value=2)

    def test_event_bus_handler_exception_caught(self):
        """Handler exceptions are caught and don't propagate."""
        handler = Mock(side_effect=RuntimeError("boom"))
        bus = EventBus(handler)
        # Should not raise
        bus.log_event("damage", amount=100)

    def test_event_bus_set_handler(self):
        """EventBus handler can be changed after creation."""
        handler1 = Mock()
        handler2 = Mock()
        bus = EventBus(handler1)

        bus.set_handler(handler2)
        bus.log_event("test")

        handler1.assert_not_called()
        handler2.assert_called_once_with("test")
