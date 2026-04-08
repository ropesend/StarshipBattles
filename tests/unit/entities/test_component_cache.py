"""Tests for Component cache thread safety."""
import pytest
import threading

from game.simulation.components.component import (
    reset_component_caches,
    ComponentCacheManager,
)


@pytest.fixture(autouse=True)
def reset_cache_after_test():
    """Reset cache after each test."""
    yield
    if hasattr(ComponentCacheManager, 'reset'):
        ComponentCacheManager.reset()


class TestComponentCacheManager:
    """Test ComponentCacheManager singleton and thread safety."""

    def test_cache_manager_singleton(self):
        """ComponentCacheManager.instance() should return same instance."""
        manager1 = ComponentCacheManager.instance()
        manager2 = ComponentCacheManager.instance()

        assert manager1 is manager2

    def test_cache_manager_is_plain_class(self):
        """PROJ-258: ComponentCacheManager is a plain class (no SingletonMeta)."""
        assert type(ComponentCacheManager) is type

    def test_cache_manager_initial_state(self):
        """ComponentCacheManager should start with None caches."""
        ComponentCacheManager.reset()
        manager = ComponentCacheManager.instance()

        assert manager.component_cache is None
        assert manager.modifier_cache is None
        assert manager.last_component_file is None
        assert manager.last_modifier_file is None

    def test_reset_clears_caches(self):
        """reset() should clear all cache values."""
        manager = ComponentCacheManager.instance()
        manager.component_cache = {"test": "value"}
        manager.modifier_cache = {"test": "value"}

        ComponentCacheManager.reset()
        manager = ComponentCacheManager.instance()

        assert manager.component_cache is None
        assert manager.modifier_cache is None

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
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 10

        # All should be the same instance (singleton)
        first = results[0]
        for manager in results[1:]:
            assert manager is first


class TestResetComponentCachesFunction:
    """Test the reset_component_caches convenience function."""

    def test_reset_component_caches_calls_manager_reset(self):
        """reset_component_caches() should reset the cache manager."""
        manager = ComponentCacheManager.instance()
        manager.component_cache = {"test": "value"}

        reset_component_caches()

        manager = ComponentCacheManager.instance()
        assert manager.component_cache is None
