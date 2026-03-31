"""
Tests for Resource Registry Integration (game/core/resources.py)

Tests for ResourceCatalog, registry integration,
thread safety, fixture integration, and exception scenarios.

Test Groups:
- Group 4: Data Independence (4 tests) - verify catalog returns independent data
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

from game.core.resources import ResourceCatalog
from game.core.registry import RegistryManager


# =============================================================================
# Group 4: Data Independence (4 tests)
# =============================================================================

class TestDataIndependence:
    """
    Tests verifying ResourceCatalog returns independent data.

    Each call to from_json() returns a new catalog instance.
    """

    def test_resource_catalog_returns_fresh_instance(self, tmp_path):
        """Each call returns a new catalog, not a shared reference."""
        file1 = tmp_path / "resources.json"
        file1.write_text(json.dumps({"resources": [{"id": "resource_a"}]}))

        result1 = ResourceCatalog.from_json(str(file1))
        result2 = ResourceCatalog.from_json(str(file1))

        # Should have same data but not be the same object
        assert result1.all_ids() == result2.all_ids()
        assert result1 is not result2

    def test_resource_catalog_does_not_modify_registry(self, tmp_path):
        """Loading a catalog should not modify global registry."""
        registry = RegistryManager.instance()
        initial_count = len(registry.resources)

        file1 = tmp_path / "resources.json"
        file1.write_text(json.dumps({"resources": [{"id": "new_resource"}]}))

        ResourceCatalog.from_json(str(file1))

        # Registry should be unchanged
        assert len(registry.resources) == initial_count
        assert "new_resource" not in registry.resources

    def test_resource_catalog_multiple_files_independent(self, tmp_path):
        """Multiple calls with different files return independent results."""
        file1 = tmp_path / "resources1.json"
        file1.write_text(json.dumps({"resources": [{"id": "res_a"}]}))

        file2 = tmp_path / "resources2.json"
        file2.write_text(json.dumps({"resources": [{"id": "res_b"}]}))

        result1 = ResourceCatalog.from_json(str(file1))
        result2 = ResourceCatalog.from_json(str(file2))

        assert result1.has("res_a")
        assert not result1.has("res_b")
        assert result2.has("res_b")
        assert not result2.has("res_a")

    def test_caller_controls_registry_update(self, tmp_path):
        """Caller is responsible for updating registry from catalog if desired."""
        file1 = tmp_path / "resources.json"
        file1.write_text(json.dumps({"resources": [{"id": "caller_resource", "name": "Caller"}]}))

        registry = RegistryManager.instance()
        initial_count = len(registry.resources)

        # Load catalog (doesn't touch registry)
        catalog = ResourceCatalog.from_json(str(file1))

        # Caller explicitly updates registry
        for defn in catalog.all_definitions():
            registry.resources[defn.id] = {'id': defn.id, 'name': defn.name}

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
        catalog = ResourceCatalog.from_json(sample_resources_file)
        registry = RegistryManager.instance()
        for defn in catalog.all_definitions():
            registry.resources[defn.id] = {'id': defn.id, 'name': defn.name}

        resource_registry = registry.resources

        assert isinstance(resource_registry, dict)
        assert "fuel" in resource_registry

    def test_registry_resources_empty_after_clear(self):
        """After clearing registry, resources dict is empty."""
        registry = RegistryManager.instance()
        registry.resources["test"] = {"id": "test"}

        assert len(registry.resources) >= 1

        registry.resources.clear()

        assert len(registry.resources) == 0

    def test_resource_catalog_keyed_by_id(self, tmp_path):
        """Resources in catalog are accessible by their 'id' field."""
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({
            "resources": [
                {"id": "my_custom_id", "name": "Custom Resource"}
            ]
        }))

        catalog = ResourceCatalog.from_json(str(filepath))

        assert catalog.has("my_custom_id")
        assert catalog.get("my_custom_id").name == "Custom Resource"

    def test_registry_manager_resources_initialization(self):
        """RegistryManager initializes with empty resources dict."""
        RegistryManager.reset()
        registry = RegistryManager.instance()

        assert isinstance(registry.resources, dict)
        assert len(registry.resources) == 0

    def test_registry_update_accumulates(self, tmp_path):
        """Registry update accumulates data (standard dict behavior)."""
        registry = RegistryManager.instance()
        registry.resources.clear()

        file1 = tmp_path / "resources1.json"
        file1.write_text(json.dumps({"resources": [{"id": "res_a", "name": "A"}]}))
        catalog1 = ResourceCatalog.from_json(str(file1))
        for defn in catalog1.all_definitions():
            registry.resources[defn.id] = {'id': defn.id, 'name': defn.name}

        file2 = tmp_path / "resources2.json"
        file2.write_text(json.dumps({"resources": [{"id": "res_b", "name": "B"}]}))
        catalog2 = ResourceCatalog.from_json(str(file2))
        for defn in catalog2.all_definitions():
            registry.resources[defn.id] = {'id': defn.id, 'name': defn.name}

        assert "res_a" in registry.resources
        assert "res_b" in registry.resources


# =============================================================================
# Group 7: Thread Safety (2 tests)
# =============================================================================

class TestThreadSafety:
    """Tests for thread safety of resource loading."""

    def test_resource_catalog_thread_safe(self, tmp_path):
        """Multiple threads can call ResourceCatalog.from_json safely."""
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({
            "resources": [{"id": "thread_resource"}]
        }))

        results = []
        errors = []

        def load_and_check():
            try:
                catalog = ResourceCatalog.from_json(str(filepath))
                results.append(catalog.has("thread_resource"))
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=load_and_check) for _ in range(10)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert all(results)

    def test_registry_manager_singleton_shared_resources(self, sample_resources_file):
        """All threads share the same resources dict via singleton."""
        catalog = ResourceCatalog.from_json(sample_resources_file)
        registry = RegistryManager.instance()
        for defn in catalog.all_definitions():
            registry.resources[defn.id] = {'id': defn.id, 'name': defn.name}

        registries = []

        def get_registry():
            registries.append(RegistryManager.instance())

        threads = [threading.Thread(target=get_registry) for _ in range(5)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert all(r is registries[0] for r in registries)
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

        registry.clear()

        assert "test_resource" not in registry.resources
        assert len(registry.resources) == 0

    def test_load_resources_from_real_data_directory(self):
        """Load resources from the actual data/resources.json if it exists."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
        real_path = os.path.join(project_root, "data", "resources.json")

        if os.path.exists(real_path):
            catalog = ResourceCatalog.from_json(real_path)

            assert len(catalog.all_ids()) > 0
            assert catalog.has("fuel") or len(catalog.all_ids()) > 0
        else:
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

        with patch('game.core.resources.load_json_required') as mock_load:
            mock_load.side_effect = PermissionError("Permission denied")

            catalog = ResourceCatalog.from_json(str(filepath))

            assert len(catalog.all_ids()) == 0

    def test_load_resources_path_encoding_issues(self, tmp_path):
        """Handle paths with special characters."""
        special_dir = tmp_path / "test_dir_unicode"
        special_dir.mkdir()
        filepath = special_dir / "resources.json"
        filepath.write_text(json.dumps({"resources": [{"id": "unicode_test"}]}))

        catalog = ResourceCatalog.from_json(str(filepath))

        assert catalog.has("unicode_test")

    def test_load_resources_very_large_json_file(self, tmp_path):
        """Handle large JSON files with many resources."""
        resources = [{"id": f"resource_{i}", "name": f"Resource {i}"} for i in range(1000)]
        large_data = {"resources": resources}

        filepath = tmp_path / "large_resources.json"
        filepath.write_text(json.dumps(large_data))

        catalog = ResourceCatalog.from_json(str(filepath))

        assert len(catalog.all_ids()) == 1000
        assert catalog.has("resource_0")
        assert catalog.has("resource_999")

    def test_load_resources_deeply_nested_description(self, tmp_path):
        """Handle resources with long descriptions."""
        resources_data = {
            "resources": [
                {
                    "id": "deep_resource",
                    "name": "Deep Resource",
                    "description": "A " * 1000 + "resource",
                }
            ]
        }

        filepath = tmp_path / "deep_resources.json"
        filepath.write_text(json.dumps(resources_data))

        catalog = ResourceCatalog.from_json(str(filepath))

        assert catalog.has("deep_resource")
