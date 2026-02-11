"""Tests for Logger singleton and utility functions."""
import threading

from game.core.logger import Logger, log_debug, log_info, log_error, set_logging


class TestLoggerSingleton:
    """Test Logger singleton pattern."""

    def test_logger_is_singleton(self):
        """Multiple Logger() calls should return same instance."""
        logger1 = Logger()
        logger2 = Logger()

        assert logger1 is logger2

    def test_instance_returns_singleton(self):
        """Logger.instance() should return the singleton."""
        logger = Logger.instance()
        assert logger is not None
        assert isinstance(logger, Logger)


class TestLoggerFunctions:
    """Test logging utility functions."""

    def test_set_logging_disables(self):
        """set_logging(False) should disable logging."""
        logger = Logger.instance()
        original = logger.enabled

        set_logging(False)
        assert logger.enabled is False

        # Restore
        set_logging(original)

    def test_set_logging_enables(self):
        """set_logging(True) should enable logging."""
        logger = Logger.instance()
        original = logger.enabled

        set_logging(True)
        assert logger.enabled is True

        # Restore
        set_logging(original)

    def test_log_debug_runs_when_enabled(self):
        """log_debug should run without error when enabled."""
        set_logging(True)

        # Should not raise
        log_debug("Test debug message")

    def test_log_info_runs_when_enabled(self):
        """log_info should run without error when enabled."""
        set_logging(True)

        # Should not raise
        log_info("Test info message")

    def test_log_error_always_runs(self):
        """log_error should run even when disabled."""
        set_logging(False)

        # Should not raise
        log_error("Test error message")

        set_logging(True)

    def test_log_debug_suppressed_when_disabled(self):
        """log_debug should be suppressed when disabled."""
        set_logging(False)

        # Should not raise (just silently suppressed)
        log_debug("This should be suppressed")

        set_logging(True)


class TestLoggerInstance:
    """Test Logger instance methods."""

    def test_logger_has_enabled_attribute(self):
        """Logger should have an enabled attribute."""
        logger = Logger()
        assert hasattr(logger, 'enabled')

    def test_logger_has_log_method(self):
        """Logger should have log method."""
        logger = Logger()
        assert hasattr(logger, 'log')
        assert callable(logger.log)

    def test_logger_has_info_method(self):
        """Logger should have info method."""
        logger = Logger()
        assert hasattr(logger, 'info')
        assert callable(logger.info)

    def test_logger_has_error_method(self):
        """Logger should have error method."""
        logger = Logger()
        assert hasattr(logger, 'error')
        assert callable(logger.error)


class TestLoggerThreadSafety:
    """Test Logger thread safety and reset functionality."""

    def teardown_method(self):
        """Reset logger after each test."""
        # Reset to ensure clean state for other tests
        if hasattr(Logger, 'reset'):
            Logger.reset()

    def test_logger_has_reset_classmethod(self):
        """Logger should have a reset classmethod for test isolation."""
        assert hasattr(Logger, 'reset')
        assert callable(Logger.reset)

    def test_reset_allows_reinitialization(self):
        """After reset, Logger should reinitialize on next access."""
        logger1 = Logger()
        Logger.reset()
        logger2 = Logger()

        # After reset, we should get a fresh instance
        # (the actual object may be the same, but it should be reinitialized)
        assert hasattr(logger2, 'enabled')

    def test_logger_is_thread_safe(self):
        """Logger class should be thread-safe via SingletonMeta."""
        # SingletonMeta provides thread-safety with per-class locks
        from game.core.singleton import SingletonMeta
        assert isinstance(Logger, SingletonMeta)

    def test_concurrent_logger_access(self):
        """Multiple threads accessing Logger should not cause race conditions."""
        Logger.reset()

        results = []
        errors = []

        def get_logger():
            try:
                logger = Logger()
                results.append(logger)
            except Exception as e:
                errors.append(e)

        # Create multiple threads that try to instantiate Logger simultaneously
        threads = [threading.Thread(target=get_logger) for _ in range(10)]

        # Start all threads nearly simultaneously
        for t in threads:
            t.start()

        # Wait for all to complete
        for t in threads:
            t.join()

        # All should have succeeded
        assert len(errors) == 0
        assert len(results) == 10

        # All should be the same instance (singleton)
        first = results[0]
        for logger in results[1:]:
            assert logger is first
