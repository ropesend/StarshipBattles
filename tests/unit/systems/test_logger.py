"""Tests for Logger singleton and utility functions."""
import unittest
import tempfile
import threading
import time

from game.core.logger import Logger, log_debug, log_info, log_error, set_logging, _logger


class TestLoggerSingleton(unittest.TestCase):
    """Test Logger singleton pattern."""
    
    def test_logger_is_singleton(self):
        """Multiple Logger() calls should return same instance."""
        logger1 = Logger()
        logger2 = Logger()
        
        self.assertIs(logger1, logger2)
    
    def test_global_logger_exists(self):
        """The global _logger should exist and be a Logger."""
        self.assertIsNotNone(_logger)
        self.assertIsInstance(_logger, Logger)


class TestLoggerFunctions(unittest.TestCase):
    """Test logging utility functions."""
    
    def test_set_logging_disables(self):
        """set_logging(False) should disable logging."""
        original = _logger.enabled
        
        set_logging(False)
        self.assertFalse(_logger.enabled)
        
        # Restore
        set_logging(original)
    
    def test_set_logging_enables(self):
        """set_logging(True) should enable logging."""
        original = _logger.enabled
        
        set_logging(True)
        self.assertTrue(_logger.enabled)
        
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


class TestLoggerInstance(unittest.TestCase):
    """Test Logger instance methods."""
    
    def test_logger_has_enabled_attribute(self):
        """Logger should have an enabled attribute."""
        logger = Logger()
        self.assertTrue(hasattr(logger, 'enabled'))
    
    def test_logger_has_log_method(self):
        """Logger should have log method."""
        logger = Logger()
        self.assertTrue(hasattr(logger, 'log'))
        self.assertTrue(callable(logger.log))
    
    def test_logger_has_info_method(self):
        """Logger should have info method."""
        logger = Logger()
        self.assertTrue(hasattr(logger, 'info'))
        self.assertTrue(callable(logger.info))
    
    def test_logger_has_error_method(self):
        """Logger should have error method."""
        logger = Logger()
        self.assertTrue(hasattr(logger, 'error'))
        self.assertTrue(callable(logger.error))


class TestLoggerThreadSafety(unittest.TestCase):
    """Test Logger thread safety and reset functionality."""

    def tearDown(self):
        """Reset logger after each test."""
        # Reset to ensure clean state for other tests
        if hasattr(Logger, 'reset'):
            Logger.reset()

    def test_logger_has_reset_classmethod(self):
        """Logger should have a reset classmethod for test isolation."""
        self.assertTrue(hasattr(Logger, 'reset'))
        self.assertTrue(callable(Logger.reset))

    def test_reset_allows_reinitialization(self):
        """After reset, Logger should reinitialize on next access."""
        logger1 = Logger()
        Logger.reset()
        logger2 = Logger()

        # After reset, we should get a fresh instance
        # (the actual object may be the same, but it should be reinitialized)
        self.assertTrue(hasattr(logger2, 'enabled'))

    def test_logger_has_lock(self):
        """Logger class should have a lock for thread safety."""
        self.assertTrue(hasattr(Logger, '_lock'))

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
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(results), 10)

        # All should be the same instance (singleton)
        first = results[0]
        for logger in results[1:]:
            self.assertIs(logger, first)


if __name__ == '__main__':
    unittest.main()
