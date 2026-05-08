"""Tests for the WorkshopEventBus class."""
import pytest
from unittest.mock import patch, MagicMock
from game.ui.screens.builder.event_bus import WorkshopEventBus


class TestEventBus:
    """Core event bus functionality tests."""

    def test_subprocess_communication(self):
        """Basic subscribe and emit works."""
        bus = WorkshopEventBus()
        received = []

        def handler(data):
            received.append(data)

        bus.subscribe("TEST_EVENT", handler)
        bus.emit("TEST_EVENT", "Hello")

        assert received == ["Hello"]

    def test_unsubscribe(self):
        """Unsubscribe prevents future callbacks."""
        bus = WorkshopEventBus()
        counter = [0]

        def handler(data):
            counter[0] += 1

        bus.subscribe("PING", handler)
        bus.emit("PING")
        assert counter[0] == 1

        bus.unsubscribe("PING", handler)
        bus.emit("PING")
        assert counter[0] == 1  # Should not increment


class TestEventBusValidation:
    """Tests for callback validation."""

    def test_subscribe_non_callable_raises_validation_exception(self):
        """Subscribing with non-callable raises ValidationException."""
        from game.core.exceptions import ValidationException
        bus = WorkshopEventBus()
        with pytest.raises(ValidationException) as exc_info:
            bus.subscribe("TEST", "not a callback")
        assert "callable" in str(exc_info.value)
        assert "str" in str(exc_info.value)

    def test_subscribe_none_raises_validation_exception(self):
        """Subscribing with None raises ValidationException."""
        from game.core.exceptions import ValidationException
        bus = WorkshopEventBus()
        with pytest.raises(ValidationException):
            bus.subscribe("TEST", None)

    def test_subscribe_integer_raises_validation_exception(self):
        """Subscribing with integer raises ValidationException."""
        from game.core.exceptions import ValidationException
        bus = WorkshopEventBus()
        with pytest.raises(ValidationException):
            bus.subscribe("TEST", 42)

    def test_subscribe_callable_class_instance_works(self):
        """Subscribing with callable class instance works."""
        bus = WorkshopEventBus()

        class Handler:
            def __init__(self):
                self.called = False
            def __call__(self, data):
                self.called = True

        handler = Handler()
        bus.subscribe("TEST", handler)
        bus.emit("TEST", "data")
        assert handler.called

    def test_subscribe_lambda_works(self):
        """Subscribing with lambda works."""
        bus = WorkshopEventBus()
        results = []
        bus.subscribe("TEST", lambda d: results.append(d))
        bus.emit("TEST", "value")
        assert results == ["value"]

    def test_subscribe_method_works(self):
        """Subscribing with bound method works."""
        bus = WorkshopEventBus()

        class Receiver:
            def __init__(self):
                self.received = None
            def handle(self, data):
                self.received = data

        receiver = Receiver()
        bus.subscribe("TEST", receiver.handle)
        bus.emit("TEST", "method_data")
        assert receiver.received == "method_data"


class TestEventBusMultipleSubscribers:
    """Tests for multiple subscriber handling."""

    def test_multiple_subscribers_receive_events(self):
        """All subscribers receive the event."""
        bus = WorkshopEventBus()
        results = []

        def handler1(data):
            results.append(f"h1:{data}")

        def handler2(data):
            results.append(f"h2:{data}")

        bus.subscribe("MULTI", handler1)
        bus.subscribe("MULTI", handler2)
        bus.emit("MULTI", "test")

        assert len(results) == 2
        assert "h1:test" in results
        assert "h2:test" in results

    def test_emit_no_subscribers_no_error(self):
        """Emitting to nonexistent event type doesn't error."""
        bus = WorkshopEventBus()
        # Should not raise
        bus.emit("NONEXISTENT_EVENT", {"data": 123})


class TestEventBusErrorHandling:
    """Tests for error handling in event handlers."""

    @patch('game.ui.screens.builder.event_bus.logger')
    def test_error_in_handler_uses_logger(self, mock_logger):
        """Handler exceptions are logged, not printed."""
        bus = WorkshopEventBus()
        received = []

        def bad_handler(data):
            raise ValueError("Test error")

        def good_handler(data):
            received.append(data)

        bus.subscribe("ERROR_TEST", bad_handler)
        bus.subscribe("ERROR_TEST", good_handler)

        # Should not raise - errors are caught
        bus.emit("ERROR_TEST", "payload")

        # Bad handler logged error
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args[0][0]
        assert "ERROR_TEST" in call_args
        assert "Test error" in call_args

        # Good handler still received the event
        assert received == ["payload"]

    def test_handler_exception_does_not_stop_others(self):
        """One failing handler doesn't prevent others from running."""
        bus = WorkshopEventBus()
        results = []

        def failing_handler(data):
            raise RuntimeError("I fail!")

        def succeeding_handler(data):
            results.append(data)

        bus.subscribe("CONTINUE", failing_handler)
        bus.subscribe("CONTINUE", succeeding_handler)

        with patch('game.ui.screens.builder.event_bus.logger'):
            bus.emit("CONTINUE", "value")

        assert results == ["value"]


class TestEventBusDefensiveCopy:
    """Tests for defensive copy during emit."""

    def test_unsubscribe_during_emit_safe(self):
        """Unsubscribing during emit doesn't cause iteration errors."""
        bus = WorkshopEventBus()
        results = []

        def unsubscribing_handler(data):
            results.append("unsub")
            bus.unsubscribe("MODIFY", unsubscribing_handler)

        def normal_handler(data):
            results.append("normal")

        bus.subscribe("MODIFY", unsubscribing_handler)
        bus.subscribe("MODIFY", normal_handler)

        # Should not raise RuntimeError about dict changing size
        bus.emit("MODIFY", None)

        assert "normal" in results

    def test_subscribe_during_emit_safe(self):
        """Subscribing during emit doesn't cause iteration errors."""
        bus = WorkshopEventBus()
        results = []

        def new_handler(data):
            results.append("new")

        def subscribing_handler(data):
            results.append("orig")
            bus.subscribe("MODIFY2", new_handler)

        bus.subscribe("MODIFY2", subscribing_handler)

        # First emit
        bus.emit("MODIFY2", None)
        assert results == ["orig"]

        # Second emit should include new handler
        results.clear()
        bus.emit("MODIFY2", None)
        assert "orig" in results
        assert "new" in results


class TestEventBusNoneData:
    """Tests for None data handling."""

    def test_emit_with_none_data(self):
        """Emit with None data works correctly."""
        bus = WorkshopEventBus()
        called = [False]
        data_received = ["NOT_SET"]

        def handler(data):
            called[0] = True
            data_received[0] = data

        bus.subscribe("NONE_TEST", handler)
        bus.emit("NONE_TEST", None)

        assert called[0]
        assert data_received[0] is None

    def test_emit_without_data_argument(self):
        """Emit without data argument passes None."""
        bus = WorkshopEventBus()
        data_received = ["NOT_SET"]

        def handler(data):
            data_received[0] = data

        bus.subscribe("NO_DATA", handler)
        bus.emit("NO_DATA")

        assert data_received[0] is None
