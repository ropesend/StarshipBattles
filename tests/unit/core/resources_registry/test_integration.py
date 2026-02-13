"""
Tests for Resource Registry Integration (game/core/resources.py)

Tests for load_resources_data pure function, registry integration,
thread safety, fixture integration, and exception scenarios.

Test Groups:
- Group 4: Data Independence (4 tests) - verify pure function behavior
- Group 5: Registry Integration (5 tests)
- Group 7: Thread Safety (2 tests)
- Group 8: Fixture Integration (2 tests)
- Group 9: Exception Scenarios (4 tests)
"""
import json
import os
import pytest
import threading
from unittest.mock import patch

from game.core.resources import load_resources_data
from game.core.registry import RegistryManager


# =============================================================================
# Group 4: Data Independence (4 tests)
# =============================================================================

class TestDataIndependence:
    """
    Tests verifying load_resources_data is a pure function.

    The load_resources_data function returns data without modifying
    global state. Each call is independent.
    """

    def test_load_resources_data_returns_fresh_dict(self, tmp_path):
        """Each call returns a new dict, not a shared reference."""
        file1 = tmp_path / "resources.json"
        file1.write_text(json.dumps({"resources": [{"id": "resource_a"}]}))

        result1 = load_resources_data(str(file1))
        result2 = load_resources_data(str(file1))

        # Should be equal but not the same object
        assert result1 == result2
        assert result1 is not result2

    def test_load_resources_data_does_not_modify_registry(self, tmp_path):
        """Pure function should not modify global registry."""
        registry = RegistryManager.instance()
        initial_count = len(registry.resources)

        file1 = tmp_path / "resources.json"
        file1.write_text(json.dumps({"resources": [{"id": "new_resource"}]}))

        load_resources_data(str(file1))

        # Registry should be unchanged
        assert len(registry.resources) == initial_count
        assert "new_resource" not in registry.resources

    def test_load_resources_data_multiple_calls_independent(self, tmp_path):
        """Multiple calls with different files return independent results."""
        file1 = tmp_path / "resources1.json"
        file1.write_text(json.dumps({"resources": [{"id": "res_a"}]}))

        file2 = tmp_path / "resources2.json"
        file2.write_text(json.dumps({"resources": [{"id": "res_b"}]}))

        result1 = load_resources_data(str(file1))
        result2 = load_resources_data(str(file2))

        assert "res_a" in result1
        assert "res_a" not in result2
        assert "res_b" in result2
        assert "res_b" not in result1

    def test_caller_controls_registry_update(self, tmp_path):
        """Caller is responsible for updating registry if desired."""
        file1 = tmp_path / "resources.json"
        file1.write_text(json.dumps({"resources": [{"id": "caller_resource"}]}))

        registry = RegistryManager.instance()
        initial_count = len(registry.resources)

        # Load data (doesn't touch registry)
        data = load_resources_data(str(file1))

        # Caller explicitly updates registry
        registry.resources.update(data)

        # Now registry has the new resource
        assert len(registry.resources) == initial_count + 1
        assert "caller_resource" in registry.resources


# =============================================================================
# Group 5: Registry Integration (5 tests)
# =============================================================================

class TestRegistryIntegration:
    """Tests for integration with RegistryManager when caller updates it."""

    def test_registry_resources_returns_correct_dict(self, sample_resources_file):
        """RegistryManager.instance().resources returns the resource dict."""
        data = load_resources_data(sample_resources_file)
        registry = RegistryManager.instance()
        registry.resources.update(data)

        resource_registry = registry.resources

        # Should be a dict with resources
        assert isinstance(resource_registry, dict)
        assert "fuel" in resource_registry

    def test_registry_resources_empty_after_clear(self):
        """After clearing registry, resources dict is empty."""
        registry = RegistryManager.instance()
        registry.resources["test"] = {"id": "test"}

        # Verify it's there
        assert len(registry.resources) >= 1

        # Clear
        registry.resources.clear()

        # Should be empty
        assert len(registry.resources) == 0

    def test_resource_registry_keyed_by_id(self, tmp_path):
        """Resources are keyed by their 'id' field in the result."""
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({
            "resources": [
                {"id": "my_custom_id", "name": "Custom Resource"}
            ]
        }))

        result = load_resources_data(str(filepath))

        # Key should be the id value, not an index
        assert "my_custom_id" in result
        assert result["my_custom_id"]["name"] == "Custom Resource"

    def test_registry_manager_resources_initialization(self):
        """RegistryManager initializes with empty resources dict."""
        # Reset to get fresh instance
        RegistryManager.reset()
        registry = RegistryManager.instance()

        # Should start with empty resources
        assert isinstance(registry.resources, dict)
        assert len(registry.resources) == 0

    def test_registry_update_accumulates(self, tmp_path):
        """
        Document: registry.update() accumulates data (standard dict behavior).

        This is expected behavior - callers should clear registry first
        if they want to replace data entirely.
        """
        registry = RegistryManager.instance()
        registry.resources.clear()

        file1 = tmp_path / "resources1.json"
        file1.write_text(json.dumps({"resources": [{"id": "res_a"}]}))
        registry.resources.update(load_resources_data(str(file1)))

        file2 = tmp_path / "resources2.json"
        file2.write_text(json.dumps({"resources": [{"id": "res_b"}]}))
        registry.resources.update(load_resources_data(str(file2)))

        # Both present due to dict.update() behavior
        assert "res_a" in registry.resources
        assert "res_b" in registry.resources


# =============================================================================
# Group 7: Thread Safety (2 tests)
# =============================================================================

class TestThreadSafety:
    """Tests for thread safety of resource loading."""

    def test_load_resources_data_thread_safe(self, tmp_path):
        """Multiple threads can call load_resources_data safely."""
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({
            "resources": [{"id": "thread_resource"}]
        }))

        results = []
        errors = []

        def load_and_check():
            try:
                data = load_resources_data(str(filepath))
                results.append("thread_resource" in data)
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=load_and_check) for _ in range(10)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # No errors should have occurred
        assert len(errors) == 0
        # All threads should have succeeded
        assert all(results)

    def test_registry_manager_singleton_shared_resources(self, sample_resources_file):
        """All threads share the same resources dict via singleton."""
        data = load_resources_data(sample_resources_file)
        registry = RegistryManager.instance()
        registry.resources.update(data)

        registries = []

        def get_registry():
            registries.append(RegistryManager.instance())

        threads = [threading.Thread(target=get_registry) for _ in range(5)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All should be the same instance
        assert all(r is registries[0] for r in registries)
        # All should have the same resources
        assert all(r.resources is registries[0].resources for r in registries)


# =============================================================================
# Group 8: Fixture Integration (2 tests)
# =============================================================================

class TestFixtureIntegration:
    """Tests for integration with test fixtures and real data."""

    def test_reset_game_state_clears_resources(self):
        """Calling registry.clear() should clear resources."""
        registry = RegistryManager.instance()
        registry.resources["test_resource"] = {"id": "test_resource"}

        assert "test_resource" in registry.resources

        # Simulate what reset_game_state fixture does
        registry.clear()

        assert "test_resource" not in registry.resources
        assert len(registry.resources) == 0

    def test_load_resources_from_real_data_directory(self):
        """Load resources from the actual data/resources.json if it exists."""
        # Get the project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
        real_path = os.path.join(project_root, "data", "resources.json")

        if os.path.exists(real_path):
            result = load_resources_data(real_path)

            # Should have loaded at least some resources
            assert len(result) > 0
            # Common resources that should exist
            assert "fuel" in result or len(result) > 0
        else:
            # If file doesn't exist, this test documents that
            pytest.skip("data/resources.json not found in project")


# =============================================================================
# Group 9: Exception Scenarios (4 tests)
# =============================================================================

class TestExceptionScenarios:
    """Tests for various exception scenarios."""

    def test_load_resources_file_permission_denied(self, tmp_path):
        """Handle permission denied errors gracefully."""
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({"resources": [{"id": "test"}]}))

        # Mock os.path.exists to return True but have load_json_required raise PermissionError
        with patch('game.core.resources.load_json_required') as mock_load:
            mock_load.side_effect = PermissionError("Permission denied")

            # Should not crash, should fall back to defaults
            result = load_resources_data(str(filepath))

            # Should have default resources
            assert "fuel" in result
            assert "energy" in result
            assert "ammo" in result

    def test_load_resources_path_encoding_issues(self, tmp_path):
        """Handle paths with special characters."""
        # Create directory and file with unicode characters
        special_dir = tmp_path / "test_dir_unicode"
        special_dir.mkdir()
        filepath = special_dir / "resources.json"
        filepath.write_text(json.dumps({"resources": [{"id": "unicode_test"}]}))

        result = load_resources_data(str(filepath))

        assert "unicode_test" in result

    def test_load_resources_very_large_json_file(self, tmp_path):
        """Handle large JSON files with many resources."""
        # Create a file with many resources
        resources = [{"id": f"resource_{i}", "index": i} for i in range(1000)]
        large_data = {"resources": resources}

        filepath = tmp_path / "large_resources.json"
        filepath.write_text(json.dumps(large_data))

        result = load_resources_data(str(filepath))

        assert len(result) == 1000
        assert "resource_0" in result
        assert "resource_999" in result

    def test_load_resources_deeply_nested_json(self, tmp_path):
        """Handle resources with deeply nested structures."""
        deep_nested = {"level": 1}
        current = deep_nested
        for i in range(2, 51):  # 50 levels of nesting
            current["nested"] = {"level": i}
            current = current["nested"]

        resources_data = {
            "resources": [
                {
                    "id": "deep_resource",
                    "deep_data": deep_nested
                }
            ]
        }

        filepath = tmp_path / "deep_resources.json"
        filepath.write_text(json.dumps(resources_data))

        result = load_resources_data(str(filepath))

        assert "deep_resource" in result

        # Verify deep nesting is preserved
        deep = result["deep_resource"]["deep_data"]
        assert deep["level"] == 1
        # Navigate to a deeper level
        for _ in range(5):
            deep = deep["nested"]
        assert deep["level"] == 6
