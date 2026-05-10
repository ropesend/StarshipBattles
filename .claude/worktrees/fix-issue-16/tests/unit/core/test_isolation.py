"""
Tests for verifying test isolation between tests.

PROJ-48: Added to verify that the reset_game_state fixture properly
isolates tests from each other.

These tests are designed to be run in sequence to verify that state
from one test doesn't leak into the next.
"""
import pytest
from game.core.registry import get_default_registry_manager


class TestRegistryIsolation:
    """
    Verify that registry state doesn't leak between tests.

    These tests must run in order (test_isolation_part1 before test_isolation_part2)
    to verify proper isolation.
    """

    def test_isolation_part1_modify_registry(self):
        """
        First part of isolation test - add data to registry.

        This test adds a custom component to the registry. The next test
        should NOT see this data if isolation is working correctly.
        """
        mgr = get_default_registry_manager()

        # Add a unique test component directly to the components dict
        test_component = {
            'id': '__isolation_test_component__',
            'name': 'Isolation Test Component',
            'type': 'test'
        }
        mgr.components['__isolation_test_component__'] = test_component

        # Verify it was added
        assert '__isolation_test_component__' in mgr.components

    def test_isolation_part2_verify_clean_state(self):
        """
        Second part of isolation test - verify registry is clean.

        This test verifies that the component added in the previous test
        is NOT present, confirming isolation is working.
        """
        mgr = get_default_registry_manager()

        # The test component from part 1 should NOT be present
        # (reset_game_state should have cleared it)
        component = mgr.components.get('__isolation_test_component__')

        # Either returns None or the production data (not our test component)
        if component is not None:
            assert component.get('type') != 'test', (
                "Test isolation failed: component from previous test leaked!"
            )


class TestPolicyManagerIsolation:
    """Verify PolicyManager state doesn't leak between tests."""

    def test_policy_isolation_part1_modify_policies(self):
        """Add a custom policy that should be cleared after test."""
        from game.ai.policy_manager import get_default_policy_manager

        mgr = get_default_policy_manager()
        # Add a test policy
        mgr.movement_policies['__isolation_test_policy__'] = {'name': 'Test Policy'}

        # Verify it was added
        assert '__isolation_test_policy__' in mgr.movement_policies

    def test_policy_isolation_part2_verify_clean(self):
        """Verify custom policy was cleared by reset_game_state."""
        from game.ai.policy_manager import get_default_policy_manager

        mgr = get_default_policy_manager()

        # The test policy should NOT be present if isolation worked
        # (reset_game_state clears policies)
        assert '__isolation_test_policy__' not in mgr.movement_policies, (
            "PolicyManager isolation failed: policy from previous test leaked!"
        )


class TestComponentCacheIsolation:
    """Verify component cache state doesn't leak between tests."""

    def test_cache_isolation_part1_modify_cache(self):
        """Add a component to cache that should be cleared after test."""
        from game.simulation.components.component_loader import get_default_cache_manager

        cache = get_default_cache_manager()
        original_count = len(cache.component_cache) if cache.component_cache else 0

        # Add a test component to the cache
        if cache.component_cache is None:
            cache.component_cache = {}
        cache.component_cache['__isolation_test_cached__'] = {'test': True}

        # Verify it was added
        assert '__isolation_test_cached__' in cache.component_cache

    def test_cache_isolation_part2_verify_clean(self):
        """Verify custom cached component was cleared."""
        from game.simulation.components.component_loader import get_default_cache_manager

        cache = get_default_cache_manager()

        # Our test component should NOT be present if isolation worked
        if cache.component_cache:
            # Either it's None/empty or our test key is gone
            assert '__isolation_test_cached__' not in cache.component_cache, (
                "ComponentCacheManager isolation failed: cache from previous test leaked!"
            )
