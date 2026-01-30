"""Tests for log level configuration, setup, and formatting."""
import pytest
import logging
from unittest.mock import patch


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
        assert fresh_logger.enabled is True


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
