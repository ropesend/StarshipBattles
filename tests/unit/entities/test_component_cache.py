"""Tests for Component cache thread safety."""
from game.simulation.components.component import (
    reset_component_caches,
    ComponentCacheManager,
)


class TestComponentCacheManager:
    """Test ComponentCacheManager construction and thread safety."""

    def test_direct_instantiation_creates_new_instance(self):
        """Direct instantiation creates independent instances."""
        manager1 = ComponentCacheManager()
        manager2 = ComponentCacheManager()
        assert manager1 is not manager2

    def test_cache_manager_is_plain_class(self):
        """PROJ-258: ComponentCacheManager is a plain class (no SingletonMeta)."""
        assert type(ComponentCacheManager) is type

    def test_cache_manager_initial_state(self):
        """ComponentCacheManager should start with None caches."""
        manager = ComponentCacheManager()

        assert manager.component_cache is None
        assert manager.modifier_cache is None
        assert manager.last_component_file is None
        assert manager.last_modifier_file is None


class TestResetComponentCachesFunction:
    """Test the reset_component_caches convenience function."""

    def test_reset_component_caches_creates_fresh_manager(self):
        """reset_component_caches() should create a fresh cache manager."""
        from game.simulation.components.component_loader import get_default_cache_manager

        manager = get_default_cache_manager()
        manager.component_cache = {"test": "value"}

        reset_component_caches()

        manager = get_default_cache_manager()
        assert manager.component_cache is None
