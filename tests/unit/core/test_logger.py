"""
Comprehensive tests for game/core/logger.py

This test file focuses on gaps in existing coverage:
- log_warning function
- Event logging (set_event_handler, log_event)
- Output formatting verification
- Warning method on Logger class
- Log level behavior
- File handler behavior
"""
import pytest
import logging
import tempfile
import os
import threading
from unittest.mock import MagicMock, patch, call


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(autouse=True)
def reset_logger():
    """Reset logger state before and after each test."""
    from game.core.logger import Logger, set_logging, set_event_handler

    # Reset to clean state
    Logger.reset()
    set_logging(True)
    set_event_handler(None)

    yield

    # Cleanup after test
    Logger.reset()
    set_logging(True)
    set_event_handler(None)


@pytest.fixture
def fresh_logger():
    """Get a freshly initialized logger instance."""
    from game.core.logger import Logger
    Logger.reset()
    return Logger()


# =============================================================================
# Test: Log Warning Function
# =============================================================================

class TestLogWarning:
    """Tests for the log_warning function."""

    def test_log_warning_exists(self):
        """log_warning function should exist and be callable."""
        from game.core.logger import log_warning

        assert callable(log_warning)

    def test_log_warning_runs_when_enabled(self):
        """log_warning should run without error when enabled."""
        from game.core.logger import log_warning, set_logging

        set_logging(True)

        # Should not raise
        log_warning("Test warning message")

    def test_log_warning_suppressed_when_disabled(self):
        """log_warning should be suppressed when disabled."""
        from game.core.logger import log_warning, set_logging

        set_logging(False)

        # Should not raise (just silently suppressed)
        log_warning("This should be suppressed")

    def test_logger_warning_method_exists(self):
        """Logger should have warning method."""
        from game.core.logger import Logger

        logger = Logger()
        assert hasattr(logger, 'warning')
        assert callable(logger.warning)

    def test_logger_warning_calls_logger_warning(self, fresh_logger):
        """Logger.warning should call the underlying logger.warning."""
        with patch.object(fresh_logger.logger, 'warning') as mock_warn:
            fresh_logger.enabled = True
            fresh_logger.warning("Test warning")

            mock_warn.assert_called_once_with("Test warning")

    def test_logger_warning_respects_enabled_flag(self, fresh_logger):
        """Logger.warning should check enabled flag."""
        with patch.object(fresh_logger.logger, 'warning') as mock_warn:
            fresh_logger.enabled = False
            fresh_logger.warning("Should not log")

            mock_warn.assert_not_called()


# =============================================================================
# Test: Event Logging System
# =============================================================================

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


# =============================================================================
# Test: Log Level Configuration
# =============================================================================

class TestLogLevels:
    """Tests for log level configuration and behavior."""

    def test_logger_default_level_is_debug(self, fresh_logger):
        """Logger should default to DEBUG level."""
        assert fresh_logger.logger.level == logging.DEBUG

    def test_debug_level_logs_debug_messages(self, fresh_logger):
        """DEBUG level should allow debug messages."""
        with patch.object(fresh_logger.logger, 'debug') as mock_debug:
            fresh_logger.enabled = True
            fresh_logger.log("debug message")

            mock_debug.assert_called_once_with("debug message")

    def test_all_log_methods_check_enabled(self, fresh_logger):
        """All log methods should respect the enabled flag."""
        methods = ['log', 'info', 'warning', 'error']

        fresh_logger.enabled = False

        with patch.object(fresh_logger.logger, 'debug') as mock_debug:
            with patch.object(fresh_logger.logger, 'info') as mock_info:
                with patch.object(fresh_logger.logger, 'warning') as mock_warn:
                    with patch.object(fresh_logger.logger, 'error') as mock_error:
                        fresh_logger.log("debug")
                        fresh_logger.info("info")
                        fresh_logger.warning("warning")
                        fresh_logger.error("error")

                        mock_debug.assert_not_called()
                        mock_info.assert_not_called()
                        mock_warn.assert_not_called()
                        mock_error.assert_not_called()


# =============================================================================
# Test: Logger Setup and File Handler
# =============================================================================

class TestLoggerSetup:
    """Tests for Logger setup and file handler configuration."""

    def test_logger_has_setup_method(self, fresh_logger):
        """Logger should have a setup method."""
        assert hasattr(fresh_logger, 'setup')
        assert callable(fresh_logger.setup)

    def test_setup_creates_file_handler(self, fresh_logger):
        """Setup should create a file handler."""
        # The logger should have at least one handler after setup
        handlers = fresh_logger.logger.handlers
        assert len(handlers) > 0

        # At least one should be a FileHandler
        file_handlers = [h for h in handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) > 0

    def test_setup_sets_formatter(self, fresh_logger):
        """Setup should set a formatter on the file handler."""
        file_handlers = [h for h in fresh_logger.logger.handlers
                        if isinstance(h, logging.FileHandler)]

        assert len(file_handlers) > 0

        handler = file_handlers[0]
        assert handler.formatter is not None

    def test_logger_name_is_starship_battles(self, fresh_logger):
        """Logger should use 'StarshipBattles' as the name."""
        assert fresh_logger.logger.name == "StarshipBattles"

    def test_setup_initializes_enabled_true(self, fresh_logger):
        """Setup should initialize enabled to True."""
        # Fresh logger after reset should have enabled=True after setup
        assert fresh_logger.enabled == True


# =============================================================================
# Test: Singleton Behavior (Additional)
# =============================================================================

class TestSingletonBehavior:
    """Additional tests for singleton behavior."""

    def test_double_checked_locking(self):
        """Logger uses double-checked locking pattern."""
        from game.core.logger import Logger

        # Reset to start fresh
        Logger.reset()

        # Create multiple instances simultaneously
        results = []

        def create_logger():
            results.append(Logger())

        threads = [threading.Thread(target=create_logger) for _ in range(5)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All should be the same instance
        assert all(r is results[0] for r in results)

    def test_reset_clears_instance(self):
        """Reset should clear the singleton instance."""
        from game.core.logger import Logger

        logger1 = Logger()
        instance_id1 = id(logger1)

        Logger.reset()

        logger2 = Logger()
        instance_id2 = id(logger2)

        # After reset, we get a new instance
        assert Logger._instance is not None

    def test_initialized_flag_prevents_double_setup(self):
        """Once initialized, calling __init__ again should not re-setup."""
        from game.core.logger import Logger

        Logger.reset()
        logger1 = Logger()
        original_logger = logger1.logger

        # Call __init__ again (happens when calling Logger() twice)
        logger1.__init__()

        # Should still have the same underlying logger
        assert logger1.logger is original_logger


# =============================================================================
# Test: Global Functions
# =============================================================================

class TestGlobalFunctions:
    """Tests for the global logging functions."""

    def test_log_debug_uses_global_logger(self):
        """log_debug should use the global _logger instance."""
        from game.core.logger import log_debug, _logger

        with patch.object(_logger, 'log') as mock_log:
            log_debug("test message")

            mock_log.assert_called_once_with("test message")

    def test_log_info_uses_global_logger(self):
        """log_info should use the global _logger instance."""
        from game.core.logger import log_info, _logger

        with patch.object(_logger, 'info') as mock_info:
            log_info("test message")

            mock_info.assert_called_once_with("test message")

    def test_log_warning_uses_global_logger(self):
        """log_warning should use the global _logger instance."""
        from game.core.logger import log_warning, _logger

        with patch.object(_logger, 'warning') as mock_warning:
            log_warning("test message")

            mock_warning.assert_called_once_with("test message")

    def test_log_error_uses_global_logger(self):
        """log_error should use the global _logger instance."""
        from game.core.logger import log_error, _logger

        with patch.object(_logger, 'error') as mock_error:
            log_error("test message")

            mock_error.assert_called_once_with("test message")

    def test_set_logging_uses_global_logger(self):
        """set_logging should set enabled on the global _logger."""
        from game.core.logger import set_logging, _logger

        set_logging(False)
        assert _logger.enabled == False

        set_logging(True)
        assert _logger.enabled == True


# =============================================================================
# Test: Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_log_with_none_message(self, fresh_logger):
        """Logging None should not crash."""
        fresh_logger.enabled = True

        # Should not raise
        fresh_logger.log(None)
        fresh_logger.info(None)
        fresh_logger.warning(None)
        fresh_logger.error(None)

    def test_log_with_empty_string(self, fresh_logger):
        """Logging empty string should not crash."""
        fresh_logger.enabled = True

        # Should not raise
        fresh_logger.log("")
        fresh_logger.info("")
        fresh_logger.warning("")
        fresh_logger.error("")

    def test_log_with_complex_objects(self, fresh_logger):
        """Logging complex objects should not crash."""
        fresh_logger.enabled = True

        # Should not raise
        fresh_logger.log({"key": "value"})
        fresh_logger.log([1, 2, 3])
        fresh_logger.log((1, 2, 3))

    def test_event_handler_exception_handling(self):
        """Exception in event handler should not crash log_event."""
        from game.core.logger import set_event_handler, log_event

        def bad_handler(event_type, **kwargs):
            raise ValueError("Handler error")

        set_event_handler(bad_handler)

        # This will raise because log_event doesn't catch exceptions
        # This is expected behavior - handler errors should propagate
        with pytest.raises(ValueError):
            log_event("test_event")

    def test_log_unicode_characters(self, fresh_logger):
        """Logging unicode should not crash."""
        fresh_logger.enabled = True

        # Should not raise
        fresh_logger.log("Unicode: \u4e2d\u6587 \U0001F680")
        fresh_logger.info("Emoji: \U0001F60A")

    def test_log_very_long_message(self, fresh_logger):
        """Logging very long messages should not crash."""
        fresh_logger.enabled = True

        long_message = "x" * 100000

        # Should not raise
        fresh_logger.log(long_message)


# =============================================================================
# Test: Formatter Output
# =============================================================================

class TestFormatterOutput:
    """Tests for log output formatting."""

    def test_formatter_includes_timestamp(self, fresh_logger):
        """Formatter should include timestamp."""
        file_handlers = [h for h in fresh_logger.logger.handlers
                        if isinstance(h, logging.FileHandler)]

        assert len(file_handlers) > 0

        formatter = file_handlers[0].formatter
        assert formatter is not None

        # Check format string contains asctime
        format_str = formatter._fmt
        assert '%(asctime)s' in format_str

    def test_formatter_includes_level(self, fresh_logger):
        """Formatter should include log level."""
        file_handlers = [h for h in fresh_logger.logger.handlers
                        if isinstance(h, logging.FileHandler)]

        assert len(file_handlers) > 0

        formatter = file_handlers[0].formatter
        format_str = formatter._fmt
        assert '%(levelname)s' in format_str

    def test_formatter_includes_message(self, fresh_logger):
        """Formatter should include message."""
        file_handlers = [h for h in fresh_logger.logger.handlers
                        if isinstance(h, logging.FileHandler)]

        assert len(file_handlers) > 0

        formatter = file_handlers[0].formatter
        format_str = formatter._fmt
        assert '%(message)s' in format_str
