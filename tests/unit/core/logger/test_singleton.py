"""Tests for singleton behavior, global functions, and edge cases."""
import pytest
import threading
from unittest.mock import patch


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
        assert _logger.enabled is False

        set_logging(True)
        assert _logger.enabled is True


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
        """Exception in event handler should not crash log_event.

        PROJ-45: Handler exceptions are caught and logged - they should NOT
        propagate to callers. This prevents buggy handlers from crashing
        simulation code.
        """
        from game.core.logger import set_event_handler, log_event

        def bad_handler(event_type, **kwargs):
            raise ValueError("Handler error")

        set_event_handler(bad_handler)

        # Should NOT raise - handler exceptions are caught and logged
        log_event("test_event")  # No exception expected

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
