"""Tests for the event logging system (set_event_handler, log_event)."""
import pytest
from unittest.mock import MagicMock


class TestEventLogging:
    """Tests for the event logging system (set_event_handler, log_event)."""

    def test_set_event_handler_exists(self):
        """set_event_handler function should exist."""
        from game.core.logger import set_event_handler

        assert callable(set_event_handler)

    def test_log_event_exists(self):
        """log_event function should exist."""
        from game.core.logger import log_event

        assert callable(log_event)

    def test_log_event_calls_handler_when_set(self):
        """log_event should call the registered handler with event type and kwargs."""
        from game.core.logger import set_event_handler, log_event

        mock_handler = MagicMock()
        set_event_handler(mock_handler)

        log_event("test_event", value=42, name="test")

        mock_handler.assert_called_once_with("test_event", value=42, name="test")

    def test_log_event_does_nothing_without_handler(self):
        """log_event should silently do nothing when no handler is set."""
        from game.core.logger import set_event_handler, log_event

        set_event_handler(None)

        # Should not raise
        log_event("test_event", value=42)

    def test_set_event_handler_replaces_previous(self):
        """set_event_handler should replace the previous handler."""
        from game.core.logger import set_event_handler, log_event

        mock_handler1 = MagicMock()
        mock_handler2 = MagicMock()

        set_event_handler(mock_handler1)
        set_event_handler(mock_handler2)

        log_event("test_event")

        mock_handler1.assert_not_called()
        mock_handler2.assert_called_once_with("test_event")

    def test_log_event_with_no_kwargs(self):
        """log_event should work with just event type."""
        from game.core.logger import set_event_handler, log_event

        mock_handler = MagicMock()
        set_event_handler(mock_handler)

        log_event("simple_event")

        mock_handler.assert_called_once_with("simple_event")

    def test_log_event_with_many_kwargs(self):
        """log_event should pass through all kwargs."""
        from game.core.logger import set_event_handler, log_event

        mock_handler = MagicMock()
        set_event_handler(mock_handler)

        log_event(
            "complex_event",
            source="ship_1",
            target="ship_2",
            damage=100,
            weapon="laser",
            hit=True
        )

        mock_handler.assert_called_once_with(
            "complex_event",
            source="ship_1",
            target="ship_2",
            damage=100,
            weapon="laser",
            hit=True
        )

    def test_event_handler_can_be_cleared(self):
        """Setting handler to None should clear it."""
        from game.core.logger import set_event_handler, log_event

        mock_handler = MagicMock()
        set_event_handler(mock_handler)
        set_event_handler(None)

        # Should not raise, handler is cleared
        log_event("test_event")

        mock_handler.assert_not_called()
