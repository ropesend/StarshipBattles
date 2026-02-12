"""
Unit tests for Logger class and module-level functions.

Tests singleton behavior, enabled flag, module-level functions,
and event handler functionality.
"""
import pytest
from unittest.mock import patch, MagicMock

from game.core.logger import (
    Logger,
    log_debug,
    log_info,
    log_warning,
    log_error,
    set_logging,
    set_event_handler,
    log_event,
)


@pytest.fixture(autouse=True)
def reset_logger():
    """Reset Logger singleton and event handler before/after each test."""
    Logger.reset()
    set_event_handler(None)
    yield
    Logger.reset()
    set_event_handler(None)


@pytest.fixture
def mock_paths(tmp_path):
    """Mock Paths.BATTLE_LOG to use a temp file."""
    log_file = tmp_path / "logs" / "battle.log"
    with patch("game.core.logger.Paths") as mock:
        mock.BATTLE_LOG = str(log_file)
        yield mock


class TestLoggerSingleton:
    """Tests for Logger singleton behavior."""

    def test_logger_singleton_same_instance(self, mock_paths):
        """Logger() returns the same instance each time."""
        logger1 = Logger.instance()
        logger2 = Logger.instance()
        assert logger1 is logger2

    def test_logger_reset_creates_new_instance(self, mock_paths):
        """After reset(), a new instance is created."""
        logger1 = Logger.instance()
        Logger.reset()
        logger2 = Logger.instance()
        # After reset, it's a different instance
        assert logger1 is not logger2


class TestLoggerEnabledFlag:
    """Tests for set_enabled behavior."""

    def test_set_enabled_false_suppresses_logs(self, mock_paths):
        """Messages are not logged when disabled."""
        logger = Logger.instance()
        logger.set_enabled(False)

        # Mock the underlying logger
        logger.logger = MagicMock()

        logger.log("test message")
        logger.info("info message")
        logger.warning("warning message")
        logger.error("error message")

        # No calls should be made when disabled
        logger.logger.debug.assert_not_called()
        logger.logger.info.assert_not_called()
        logger.logger.warning.assert_not_called()
        logger.logger.error.assert_not_called()

    def test_set_enabled_true_allows_logs(self, mock_paths):
        """Messages are logged when enabled."""
        logger = Logger.instance()
        logger.set_enabled(True)

        # Mock the underlying logger
        logger.logger = MagicMock()

        logger.log("test message")
        logger.info("info message")
        logger.warning("warning message")
        logger.error("error message")

        # All calls should be made when enabled
        logger.logger.debug.assert_called_once_with("test message")
        logger.logger.info.assert_called_once_with("info message")
        logger.logger.warning.assert_called_once_with("warning message")
        logger.logger.error.assert_called_once_with("error message")


class TestModuleLevelFunctions:
    """Tests for module-level convenience functions."""

    def test_log_debug_delegates(self, mock_paths):
        """log_debug() calls Logger instance log method."""
        logger = Logger.instance()
        logger.logger = MagicMock()

        log_debug("debug message")

        logger.logger.debug.assert_called_once_with("debug message")

    def test_log_info_delegates(self, mock_paths):
        """log_info() calls Logger instance info method."""
        logger = Logger.instance()
        logger.logger = MagicMock()

        log_info("info message")

        logger.logger.info.assert_called_once_with("info message")

    def test_log_warning_delegates(self, mock_paths):
        """log_warning() calls Logger instance warning method."""
        logger = Logger.instance()
        logger.logger = MagicMock()

        log_warning("warning message")

        logger.logger.warning.assert_called_once_with("warning message")

    def test_log_error_delegates(self, mock_paths):
        """log_error() calls Logger instance error method."""
        logger = Logger.instance()
        logger.logger = MagicMock()

        log_error("error message")

        logger.logger.error.assert_called_once_with("error message")

    def test_set_logging_sets_enabled(self, mock_paths):
        """set_logging() sets the enabled flag."""
        logger = Logger.instance()

        set_logging(False)
        assert logger.enabled is False

        set_logging(True)
        assert logger.enabled is True


class TestEventHandler:
    """Tests for event handler functionality."""

    def test_set_event_handler_registers_callback(self, mock_paths):
        """set_event_handler stores the callback."""
        handler = MagicMock()
        set_event_handler(handler)

        # Verify by calling log_event
        log_event("test_event", key="value")
        handler.assert_called_once_with("test_event", key="value")

    def test_log_event_calls_handler(self, mock_paths):
        """log_event invokes handler with event_type and kwargs."""
        handler = MagicMock()
        set_event_handler(handler)

        log_event("damage", amount=50, target="ship1")

        handler.assert_called_once_with("damage", amount=50, target="ship1")

    def test_log_event_no_handler_no_crash(self, mock_paths):
        """log_event with no handler registered does not crash."""
        set_event_handler(None)

        # Should not raise
        log_event("some_event", data="value")

    def test_log_event_handler_exception_caught(self, mock_paths):
        """Exception in handler is caught and logged, not raised."""
        def bad_handler(*args, **kwargs):
            raise ValueError("Handler error")

        set_event_handler(bad_handler)
        logger = Logger.instance()
        logger.logger = MagicMock()

        # Should not raise
        log_event("test_event")

        # Error should be logged
        logger.logger.error.assert_called_once()
        call_args = logger.logger.error.call_args[0][0]
        assert "Event handler error" in call_args
        assert "test_event" in call_args
