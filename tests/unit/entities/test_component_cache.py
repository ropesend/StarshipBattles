"""Tests for Component cache thread safety."""
import unittest
import threading

from game.simulation.components.component import (
    reset_component_caches,
    ComponentCacheManager,
)


class TestComponentCacheManager(unittest.TestCase):
    """Test ComponentCacheManager singleton and thread safety."""

    def tearDown(self):
        """Reset cache after each test."""
        if hasattr(ComponentCacheManager, 'reset'):
            ComponentCacheManager.reset()

    def test_cache_manager_singleton(self):
        """ComponentCacheManager.instance() should return same instance."""
        manager1 = ComponentCacheManager.instance()
        manager2 = ComponentCacheManager.instance()

        self.assertIs(manager1, manager2)

    def test_cache_manager_has_lock(self):
        """ComponentCacheManager class should have a lock for thread safety."""
        self.assertTrue(hasattr(ComponentCacheManager, '_lock'))

    def test_cache_manager_has_reset(self):
        """ComponentCacheManager should have a reset classmethod."""
        self.assertTrue(hasattr(ComponentCacheManager, 'reset'))
        self.assertTrue(callable(ComponentCacheManager.reset))

    def test_cache_manager_initial_state(self):
        """ComponentCacheManager should start with None caches."""
        ComponentCacheManager.reset()
        manager = ComponentCacheManager.instance()

        self.assertIsNone(manager.component_cache)
        self.assertIsNone(manager.modifier_cache)
        self.assertIsNone(manager.last_component_file)
        self.assertIsNone(manager.last_modifier_file)

    def test_reset_clears_caches(self):
        """reset() should clear all cache values."""
        manager = ComponentCacheManager.instance()
        manager.component_cache = {"test": "value"}
        manager.modifier_cache = {"test": "value"}

        ComponentCacheManager.reset()
        manager = ComponentCacheManager.instance()

        self.assertIsNone(manager.component_cache)
        self.assertIsNone(manager.modifier_cache)

    def test_concurrent_cache_access(self):
        """Multiple threads accessing cache should not cause race conditions."""
        ComponentCacheManager.reset()

        results = []
        errors = []

        def get_cache_manager():
            try:
                manager = ComponentCacheManager.instance()
                results.append(manager)
            except Exception as e:
                errors.append(e)

        # Create multiple threads that try to get cache manager simultaneously
        threads = [threading.Thread(target=get_cache_manager) for _ in range(10)]

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
        for manager in results[1:]:
            self.assertIs(manager, first)


class TestResetComponentCachesFunction(unittest.TestCase):
    """Test the reset_component_caches convenience function."""

    def test_reset_component_caches_calls_manager_reset(self):
        """reset_component_caches() should reset the cache manager."""
        manager = ComponentCacheManager.instance()
        manager.component_cache = {"test": "value"}

        reset_component_caches()

        manager = ComponentCacheManager.instance()
        self.assertIsNone(manager.component_cache)


if __name__ == '__main__':
    unittest.main()
