"""Tests for TestRegistry singleton and thread safety."""
import threading

from combat_lab.registry import TestRegistry


class TestTestRegistrySingleton:
    """Test TestRegistry singleton pattern."""

    def test_registry_is_singleton(self):
        """Multiple TestRegistry() calls should return same instance."""
        registry1 = TestRegistry()
        registry2 = TestRegistry()

        assert registry1 is registry2


class TestTestRegistryThreadSafety:
    """Test TestRegistry thread safety and reset functionality."""

    def teardown_method(self):
        """Reset registry after each test."""
        if hasattr(TestRegistry, 'reset'):
            TestRegistry.reset()

    def test_registry_has_reset_classmethod(self):
        """TestRegistry should have a reset classmethod for test isolation."""
        assert hasattr(TestRegistry, 'reset')
        assert callable(TestRegistry.reset)

    def test_reset_allows_reinitialization(self):
        """After reset, TestRegistry should reinitialize on next access."""
        registry1 = TestRegistry()
        TestRegistry.reset()
        registry2 = TestRegistry()

        # After reset, we should get a fresh instance
        assert hasattr(registry2, 'scenarios')

    def test_registry_has_lock(self):
        """TestRegistry class should have a lock for thread safety."""
        assert hasattr(TestRegistry, '_lock')

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
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 10

        # All should be the same instance (singleton)
        first = results[0]
        for registry in results[1:]:
            assert registry is first
