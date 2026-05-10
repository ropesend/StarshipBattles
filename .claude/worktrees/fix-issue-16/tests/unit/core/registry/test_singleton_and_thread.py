"""
Tests for RegistryManager instance management, thread safety, and test isolation.

PROJ-258: RegistryManager migrated from SingletonMeta to DI via ApplicationContext.
Module-level get_default_registry_manager() / set_default_registry_manager() are
the permanent API for accessing the shared instance.
"""

import pytest
import threading
from unittest.mock import MagicMock

from game.core.registry import (
    RegistryManager,
    get_default_registry_manager,
    set_default_registry_manager,
)


# =============================================================================
# Test: Instance Management (module-level reference pattern)
# =============================================================================

class TestInstanceManagement:
    """Tests for RegistryManager instance access via module-level reference."""

    def test_get_default_returns_same_object(self):
        """get_default_registry_manager() should return the same instance."""
        r1 = get_default_registry_manager()
        r2 = get_default_registry_manager()
        assert r1 is r2

    def test_direct_instantiation_creates_new_object(self):
        """Direct RegistryManager() creates a NEW instance (not singleton)."""
        r1 = RegistryManager()
        r2 = RegistryManager()
        assert r1 is not r2

    def test_set_default_replaces_instance(self):
        """set_default_registry_manager() should replace the module-level instance."""
        r1 = get_default_registry_manager()
        id1 = id(r1)

        set_default_registry_manager(RegistryManager())

        r2 = get_default_registry_manager()
        id2 = id(r2)

        assert id1 != id2

    def test_set_default_provides_clean_state(self):
        """set_default_registry_manager(RegistryManager()) creates a fresh instance with empty registries."""
        r1 = get_default_registry_manager()
        r1.components["test"] = {"id": "test"}

        set_default_registry_manager(RegistryManager())

        r2 = get_default_registry_manager()
        assert len(r2.components) == 0


# =============================================================================
# Test: Thread Safety
# =============================================================================

class TestThreadSafety:
    """Tests for thread-safe operations."""

    def test_concurrent_instance_access(self):
        """Multiple threads calling get_default_registry_manager() should get same instance."""
        set_default_registry_manager(RegistryManager())
        results = []
        errors = []

        def get_instance():
            try:
                results.append(get_default_registry_manager())
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=get_instance) for _ in range(10)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(results) == 10

        # All should be same instance
        first = results[0]
        assert all(r is first for r in results)

    def test_concurrent_registration(self, registry):
        """Multiple threads registering components should not corrupt data."""

        def register_components(prefix):
            for i in range(10):
                registry.components[f"{prefix}_{i}"] = {"id": f"{prefix}_{i}"}

        threads = [
            threading.Thread(target=register_components, args=(f"thread_{i}",))
            for i in range(5)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have 50 components (5 threads x 10 components each)
        assert len(registry.components) == 50

    def test_concurrent_clear_is_safe(self, registry):
        """Concurrent clear operations should not crash."""
        registry.components["test"] = {"id": "test"}

        errors = []

        def clear_registry():
            try:
                registry.clear()
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=clear_registry) for _ in range(5)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # No errors
        assert len(errors) == 0
        # Registry should be empty
        assert len(registry.components) == 0


# =============================================================================
# Test: Test Isolation (CRITICAL)
# =============================================================================

class TestIsolation:
    """
    CRITICAL: Tests for test isolation behavior.

    These tests verify that the registry can be properly isolated between tests
    to prevent data accumulation bugs.
    """

    def test_set_default_provides_clean_slate(self):
        """set_default_registry_manager(RegistryManager()) should provide completely clean state."""
        # Populate with data
        r1 = get_default_registry_manager()
        r1.components["a"] = {"id": "a"}
        r1.modifiers["b"] = {"id": "b"}
        r1.vehicle_classes["c"] = {"name": "c"}
        r1.resources["d"] = {"id": "d"}
        r1.set_validator(MagicMock())
        r1.freeze()

        # Reset
        set_default_registry_manager(RegistryManager())

        # Get new instance
        r2 = get_default_registry_manager()

        # All should be empty/default
        assert len(r2.components) == 0
        assert len(r2.modifiers) == 0
        assert len(r2.vehicle_classes) == 0
        assert len(r2.resources) == 0
        assert r2._validator is None
        assert r2._frozen is False

    def test_clear_provides_clean_state_without_reset(self, registry):
        """clear() should empty all data without destroying instance."""
        registry.components["a"] = {"id": "a"}
        registry.modifiers["b"] = {"id": "b"}

        registry.clear()

        assert len(registry.components) == 0
        assert len(registry.modifiers) == 0

    def test_stale_references_after_set_default(self):
        """
        WARNING: Stale references after set_default can cause issues.

        When set_default_registry_manager() is called with a new instance,
        code holding old dict references will see stale data.
        The clear() method is safer as it preserves dict identity.
        """
        r1 = get_default_registry_manager()
        old_components = r1.components
        old_components["test"] = {"id": "test"}

        set_default_registry_manager(RegistryManager())

        r2 = get_default_registry_manager()

        # New instance has different dict
        assert r2.components is not old_components

        # Old reference still has data (stale)
        assert "test" in old_components
        # New instance is clean
        assert "test" not in r2.components

    def test_dict_identity_preserved_with_clear(self, registry):
        """clear() preserves dict identity, avoiding stale references."""
        old_components = registry.components
        registry.components["test"] = {"id": "test"}

        registry.clear()

        # Same dict object
        assert registry.components is old_components
        # But data is cleared
        assert "test" not in old_components

    def test_data_accumulation_bug_scenario(self):
        """
        BUG DOC: Demonstrate data accumulation if clear() not called.

        Without proper cleanup between tests, data accumulates in the
        shared registry.
        """
        set_default_registry_manager(RegistryManager())

        # Simulate first test
        r1 = get_default_registry_manager()
        r1.components["from_test_1"] = {"id": "from_test_1"}

        # Simulate second test (without cleanup)
        r2 = get_default_registry_manager()
        r2.components["from_test_2"] = {"id": "from_test_2"}

        # BUG: Both are present (data accumulated)
        assert "from_test_1" in r2.components
        assert "from_test_2" in r2.components
        assert len(r2.components) == 2  # Should be 1 if properly isolated
