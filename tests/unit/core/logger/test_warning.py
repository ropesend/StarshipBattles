"""Tests for log_warning function and Logger.warning method."""
import pytest
from unittest.mock import patch


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
