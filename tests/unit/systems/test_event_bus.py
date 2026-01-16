"""Tests for the EventBus class."""
import unittest
from unittest.mock import patch, MagicMock
from ui.builder.event_bus import EventBus


class TestEventBus(unittest.TestCase):
    """Core event bus functionality tests."""

    def test_subprocess_communication(self):
        """Basic subscribe and emit works."""
        bus = EventBus()
        self.received = None

        def handler(data):
            self.received = data

        bus.subscribe("TEST_EVENT", handler)
        bus.emit("TEST_EVENT", "Hello")

        self.assertEqual(self.received, "Hello")

    def test_unsubscribe(self):
        """Unsubscribe prevents future callbacks."""
        bus = EventBus()
        self.counter = 0

        def handler(data):
            self.counter += 1

        bus.subscribe("PING", handler)
        bus.emit("PING")
        self.assertEqual(self.counter, 1)

        bus.unsubscribe("PING", handler)
        bus.emit("PING")
        self.assertEqual(self.counter, 1)  # Should not increment


class TestEventBusMultipleSubscribers(unittest.TestCase):
    """Tests for multiple subscriber handling."""

    def test_multiple_subscribers_receive_events(self):
        """All subscribers receive the event."""
        bus = EventBus()
        results = []

        def handler1(data):
            results.append(f"h1:{data}")

        def handler2(data):
            results.append(f"h2:{data}")

        bus.subscribe("MULTI", handler1)
        bus.subscribe("MULTI", handler2)
        bus.emit("MULTI", "test")

        self.assertEqual(len(results), 2)
        self.assertIn("h1:test", results)
        self.assertIn("h2:test", results)

    def test_emit_no_subscribers_no_error(self):
        """Emitting to nonexistent event type doesn't error."""
        bus = EventBus()
        # Should not raise
        bus.emit("NONEXISTENT_EVENT", {"data": 123})


class TestEventBusErrorHandling(unittest.TestCase):
    """Tests for error handling in event handlers."""

    @patch('ui.builder.event_bus.log_error')
    def test_error_in_handler_uses_logger(self, mock_log_error):
        """Handler exceptions are logged, not printed."""
        bus = EventBus()

        def bad_handler(data):
            raise ValueError("Test error")

        def good_handler(data):
            self.received = data

        self.received = None
        bus.subscribe("ERROR_TEST", bad_handler)
        bus.subscribe("ERROR_TEST", good_handler)

        # Should not raise - errors are caught
        bus.emit("ERROR_TEST", "payload")

        # Bad handler logged error
        mock_log_error.assert_called_once()
        call_args = mock_log_error.call_args[0][0]
        self.assertIn("ERROR_TEST", call_args)
        self.assertIn("Test error", call_args)

        # Good handler still received the event
        self.assertEqual(self.received, "payload")

    def test_handler_exception_does_not_stop_others(self):
        """One failing handler doesn't prevent others from running."""
        bus = EventBus()
        results = []

        def failing_handler(data):
            raise RuntimeError("I fail!")

        def succeeding_handler(data):
            results.append(data)

        bus.subscribe("CONTINUE", failing_handler)
        bus.subscribe("CONTINUE", succeeding_handler)

        with patch('ui.builder.event_bus.log_error'):
            bus.emit("CONTINUE", "value")

        self.assertEqual(results, ["value"])


class TestEventBusDefensiveCopy(unittest.TestCase):
    """Tests for defensive copy during emit."""

    def test_unsubscribe_during_emit_safe(self):
        """Unsubscribing during emit doesn't cause iteration errors."""
        bus = EventBus()
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

        self.assertIn("normal", results)

    def test_subscribe_during_emit_safe(self):
        """Subscribing during emit doesn't cause iteration errors."""
        bus = EventBus()
        results = []

        def new_handler(data):
            results.append("new")

        def subscribing_handler(data):
            results.append("orig")
            bus.subscribe("MODIFY2", new_handler)

        bus.subscribe("MODIFY2", subscribing_handler)

        # First emit
        bus.emit("MODIFY2", None)
        self.assertEqual(results, ["orig"])

        # Second emit should include new handler
        results.clear()
        bus.emit("MODIFY2", None)
        self.assertIn("orig", results)
        self.assertIn("new", results)


class TestEventBusNoneData(unittest.TestCase):
    """Tests for None data handling."""

    def test_emit_with_none_data(self):
        """Emit with None data works correctly."""
        bus = EventBus()
        self.called = False
        self.data_received = "NOT_SET"

        def handler(data):
            self.called = True
            self.data_received = data

        bus.subscribe("NONE_TEST", handler)
        bus.emit("NONE_TEST", None)

        self.assertTrue(self.called)
        self.assertIsNone(self.data_received)

    def test_emit_without_data_argument(self):
        """Emit without data argument passes None."""
        bus = EventBus()
        self.data_received = "NOT_SET"

        def handler(data):
            self.data_received = data

        bus.subscribe("NO_DATA", handler)
        bus.emit("NO_DATA")

        self.assertIsNone(self.data_received)


if __name__ == '__main__':
    unittest.main()
