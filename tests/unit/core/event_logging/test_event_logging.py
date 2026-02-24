"""Tests for game.core.event_logging module."""
import pytest


class TestEventHandler:
    """Tests for event handler registration and retrieval."""

    def test_set_and_get_event_handler(self):
        """set_event_handler registers handler, get_event_handler retrieves it."""
        from game.core.event_logging import set_event_handler, get_event_handler

        def my_handler(event_type, **kwargs):
            pass

        set_event_handler(my_handler)
        assert get_event_handler() is my_handler

    def test_clear_event_handler(self):
        """set_event_handler(None) clears the handler."""
        from game.core.event_logging import set_event_handler, get_event_handler

        set_event_handler(lambda t, **k: None)
        set_event_handler(None)
        assert get_event_handler() is None

    def test_default_handler_is_none(self):
        """Default state has no handler."""
        from game.core.event_logging import set_event_handler, get_event_handler

        # Clear any existing handler first
        set_event_handler(None)
        assert get_event_handler() is None


class TestLogEvent:
    """Tests for log_event function."""

    def test_log_event_calls_handler(self):
        """log_event invokes registered handler with event_type and kwargs."""
        from game.core.event_logging import set_event_handler, log_event

        received = []

        def handler(event_type, **kwargs):
            received.append((event_type, kwargs))

        set_event_handler(handler)
        log_event("damage", ship_id=42, amount=100)

        assert len(received) == 1
        assert received[0] == ("damage", {"ship_id": 42, "amount": 100})

    def test_log_event_no_handler_does_nothing(self):
        """log_event with no handler should not raise."""
        from game.core.event_logging import set_event_handler, log_event

        set_event_handler(None)
        # Should not raise
        log_event("movement", ship_id=1, x=10, y=20)

    def test_log_event_handler_exception_isolated(self, caplog):
        """Handler exceptions don't crash caller and are logged."""
        from game.core.event_logging import set_event_handler, log_event
        import logging

        def bad_handler(event_type, **kwargs):
            raise ValueError("Handler bug")

        set_event_handler(bad_handler)

        # Should NOT raise
        with caplog.at_level(logging.ERROR, logger="game.core.event_logging"):
            log_event("test_event", data=123)

        # Exception should be logged
        assert "Event handler error for test_event" in caplog.text
        assert "ValueError" in caplog.text

    def test_log_event_multiple_calls(self):
        """Multiple log_event calls are all forwarded."""
        from game.core.event_logging import set_event_handler, log_event

        events = []
        set_event_handler(lambda t, **k: events.append(t))

        log_event("event1")
        log_event("event2")
        log_event("event3")

        assert events == ["event1", "event2", "event3"]


@pytest.fixture(autouse=True)
def cleanup_event_handler():
    """Ensure event handler is cleaned up after each test."""
    from game.core.event_logging import set_event_handler

    yield
    set_event_handler(None)
