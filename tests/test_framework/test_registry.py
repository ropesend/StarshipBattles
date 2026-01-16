"""Tests for TestRegistry singleton and thread safety."""
import unittest
import threading

from test_framework.registry import TestRegistry


class TestTestRegistrySingleton(unittest.TestCase):
    """Test TestRegistry singleton pattern."""

    def test_registry_is_singleton(self):
        """Multiple TestRegistry() calls should return same instance."""
        registry1 = TestRegistry()
        registry2 = TestRegistry()

        self.assertIs(registry1, registry2)


class TestTestRegistryThreadSafety(unittest.TestCase):
    """Test TestRegistry thread safety and reset functionality."""

    def tearDown(self):
        """Reset registry after each test."""
        if hasattr(TestRegistry, 'reset'):
            TestRegistry.reset()

    def test_registry_has_reset_classmethod(self):
        """TestRegistry should have a reset classmethod for test isolation."""
        self.assertTrue(hasattr(TestRegistry, 'reset'))
        self.assertTrue(callable(TestRegistry.reset))

    def test_reset_allows_reinitialization(self):
        """After reset, TestRegistry should reinitialize on next access."""
        registry1 = TestRegistry()
        TestRegistry.reset()
        registry2 = TestRegistry()

        # After reset, we should get a fresh instance
        self.assertTrue(hasattr(registry2, 'scenarios'))

    def test_registry_has_lock(self):
        """TestRegistry class should have a lock for thread safety."""
        self.assertTrue(hasattr(TestRegistry, '_lock'))

    def test_concurrent_registry_access(self):
        """Multiple threads accessing TestRegistry should not cause race conditions."""
        TestRegistry.reset()

        results = []
        errors = []

        def get_registry():
            try:
                registry = TestRegistry()
                results.append(registry)
            except Exception as e:
                errors.append(e)

        # Create multiple threads that try to instantiate TestRegistry simultaneously
        threads = [threading.Thread(target=get_registry) for _ in range(10)]

        # Start all threads nearly simultaneously
        for t in threads:
            t.start()

        # Wait for all to complete
        for t in threads:
            t.join()

        # All should have succeeded
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(results), 10)

        # All should be the same instance (singleton)
        first = results[0]
        for registry in results[1:]:
            self.assertIs(registry, first)


if __name__ == '__main__':
    unittest.main()
