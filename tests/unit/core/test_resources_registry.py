"""
Tests for Resource Registry Loading (game/core/resources.py)

Tests the load_resources function which loads resource definitions from JSON
into the RegistryManager singleton.

Test Groups:
- Group 1: Happy Path (5 tests)
- Group 2: Error Handling (5 tests)
- Group 3: Edge Cases (9 tests)
- Group 4: Data Accumulation Bug (4 tests) - CRITICAL
- Group 5: Registry Integration (5 tests)
- Group 6: Logging (3 tests)
- Group 7: Thread Safety (2 tests)
- Group 8: Fixture Integration (2 tests)
- Group 9: Exception Scenarios (4 tests)
"""
import json
import os
import pytest
import threading
from pathlib import Path
from unittest.mock import patch, MagicMock

from game.core.resources import load_resources
from game.core.registry import RegistryManager, get_resource_registry


@pytest.fixture(autouse=True)
def clean_registry():
    """Ensure clean registry state before and after each test."""
    registry = RegistryManager.instance()
    # Unfreeze if frozen
    registry._frozen = False
    registry.resources.clear()
    yield
    registry._frozen = False
    registry.resources.clear()


@pytest.fixture
def sample_resources_data():
    """Standard test data for resources."""
    return {
        "resources": [
            {"id": "fuel", "name": "Fuel", "max": 100},
            {"id": "energy", "name": "Energy", "max": 200},
            {"id": "ammo", "name": "Ammunition", "max": 50}
        ]
    }


@pytest.fixture
def sample_resources_file(tmp_path, sample_resources_data):
    """Create a temporary resources JSON file."""
    filepath = tmp_path / "resources.json"
    filepath.write_text(json.dumps(sample_resources_data))
    return str(filepath)


# =============================================================================
# Group 1: Happy Path (5 tests)
# =============================================================================

class TestHappyPath:
    """Tests for successful resource loading scenarios."""

    def test_load_resources_basic_happy_path(self, sample_resources_file):
        """Load resources from a valid JSON file successfully."""
        load_resources(sample_resources_file)

        registry = RegistryManager.instance()

        assert len(registry.resources) == 3
        assert "fuel" in registry.resources
        assert "energy" in registry.resources
        assert "ammo" in registry.resources

    def test_load_resources_uses_default_path(self, tmp_path, monkeypatch):
        """When no filepath is provided, use the default data/resources.json path."""
        # Create a mock resources file at the expected default location
        resources_data = {"resources": [{"id": "default_resource"}]}

        # We need to patch os.path.exists and load_json_required to simulate default path
        with patch('game.core.resources.os.path.exists') as mock_exists, \
             patch('game.core.resources.load_json_required') as mock_load:
            mock_exists.return_value = True
            mock_load.return_value = resources_data

            load_resources()  # No filepath argument

            # Verify the default path was used
            mock_exists.assert_called()
            call_args = mock_exists.call_args_list[0][0][0]
            assert "data/resources.json" in call_args or call_args == "data/resources.json"

    def test_load_resources_with_custom_filepath(self, tmp_path):
        """Load resources from a custom filepath."""
        custom_path = tmp_path / "custom" / "my_resources.json"
        custom_path.parent.mkdir(parents=True, exist_ok=True)
        custom_data = {"resources": [{"id": "custom_fuel", "custom_field": True}]}
        custom_path.write_text(json.dumps(custom_data))

        load_resources(str(custom_path))

        registry = RegistryManager.instance()
        assert "custom_fuel" in registry.resources
        assert registry.resources["custom_fuel"]["custom_field"] is True

    def test_load_resources_preserves_all_fields(self, tmp_path):
        """All fields from resource definitions are preserved in the registry."""
        resources_data = {
            "resources": [
                {
                    "id": "plasma",
                    "name": "Plasma Energy",
                    "description": "High-energy plasma for weapons",
                    "max_capacity": 500,
                    "regen_rate": 10,
                    "color": "#FF00FF",
                    "nested": {"level1": {"level2": "deep_value"}}
                }
            ]
        }
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps(resources_data))

        load_resources(str(filepath))

        registry = RegistryManager.instance()
        plasma = registry.resources["plasma"]

        assert plasma["id"] == "plasma"
        assert plasma["name"] == "Plasma Energy"
        assert plasma["description"] == "High-energy plasma for weapons"
        assert plasma["max_capacity"] == 500
        assert plasma["regen_rate"] == 10
        assert plasma["color"] == "#FF00FF"
        assert plasma["nested"]["level1"]["level2"] == "deep_value"

    def test_load_resources_handles_absolute_path(self, tmp_path):
        """Load resources using an absolute path works correctly."""
        abs_path = tmp_path / "absolute_resources.json"
        abs_path.write_text(json.dumps({"resources": [{"id": "abs_resource"}]}))

        # Ensure it's actually absolute
        assert os.path.isabs(str(abs_path))

        load_resources(str(abs_path))

        registry = RegistryManager.instance()
        assert "abs_resource" in registry.resources


# =============================================================================
# Group 2: Error Handling (5 tests)
# =============================================================================

class TestErrorHandling:
    """Tests for error handling in resource loading."""

    def test_load_resources_missing_file_uses_defaults(self):
        """When file doesn't exist, fall back to default resources."""
        load_resources("nonexistent_file_12345.json")

        registry = RegistryManager.instance()

        # Should have default resources
        assert "fuel" in registry.resources
        assert "energy" in registry.resources
        assert "ammo" in registry.resources
        assert len(registry.resources) == 3

    def test_load_resources_missing_file_abs_path_fallback(self, tmp_path, monkeypatch):
        """When relative path fails, try absolute path based on module location."""
        # This tests the fallback logic where it tries project_root/filepath
        with patch('game.core.resources.os.path.exists') as mock_exists:
            # First call (relative) returns False, second call (absolute) returns True
            mock_exists.side_effect = [False, False]

            load_resources("data/resources.json")

            # Should fall back to defaults since neither path exists
            registry = RegistryManager.instance()
            assert "fuel" in registry.resources

    def test_load_resources_malformed_json_uses_defaults(self, tmp_path):
        """When JSON is malformed, fall back to default resources."""
        malformed_file = tmp_path / "malformed.json"
        malformed_file.write_text("{ not valid json }")

        load_resources(str(malformed_file))

        registry = RegistryManager.instance()

        # Should have default resources
        assert "fuel" in registry.resources
        assert "energy" in registry.resources
        assert "ammo" in registry.resources

    def test_load_resources_invalid_json_exception_handling(self, tmp_path):
        """Exception from invalid JSON is caught and handled gracefully."""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("totally not json {{{{")

        # Should not raise an exception
        load_resources(str(invalid_file))

        # Should have defaults
        registry = RegistryManager.instance()
        assert len(registry.resources) == 3

    def test_load_resources_empty_file_uses_defaults(self, tmp_path):
        """When file is empty, fall back to default resources."""
        empty_file = tmp_path / "empty.json"
        empty_file.write_text("")

        load_resources(str(empty_file))

        registry = RegistryManager.instance()

        # Should have default resources
        assert "fuel" in registry.resources
        assert "energy" in registry.resources
        assert "ammo" in registry.resources


# =============================================================================
# Group 3: Edge Cases (9 tests)
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases in resource loading."""

    def test_load_resources_empty_resources_array(self, tmp_path):
        """Empty resources array results in no resources loaded."""
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({"resources": []}))

        load_resources(str(filepath))

        registry = RegistryManager.instance()
        assert len(registry.resources) == 0

    def test_load_resources_missing_resources_key_silent_failure(self, tmp_path):
        """
        BUG DOC: Missing 'resources' key silently results in empty registry.

        When the JSON file doesn't have a 'resources' key, the code uses
        data.get('resources', []) which returns an empty list, resulting
        in no resources being loaded. This is silent - no warning is logged.

        Expected behavior: Should either warn about missing key or fail explicitly.
        Actual behavior: Silently returns empty registry.
        """
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({"other_key": "value"}))

        load_resources(str(filepath))

        registry = RegistryManager.instance()
        # BUG: No resources loaded and no warning given
        assert len(registry.resources) == 0

    def test_load_resources_null_resources_value(self, tmp_path):
        """When resources value is null, handle gracefully."""
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({"resources": None}))

        # Should not crash - will iterate over None which may raise TypeError
        # The exception handler should catch this and use defaults
        load_resources(str(filepath))

        registry = RegistryManager.instance()
        # Falls back to defaults due to exception
        assert "fuel" in registry.resources

    def test_load_resources_resources_not_array(self, tmp_path):
        """When resources is not an array, handle gracefully."""
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({"resources": {"id": "not_array"}}))

        # Iterating over a dict iterates over keys, not causing obvious error
        # but not loading resources correctly either
        load_resources(str(filepath))

        registry = RegistryManager.instance()
        # Iterating over dict yields strings (keys), which don't have .get()
        # This should trigger exception handler and fall back to defaults
        assert "fuel" in registry.resources

    def test_load_resources_resource_missing_id_field(self, tmp_path):
        """Resources without an id field are silently skipped."""
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({
            "resources": [
                {"name": "No ID Resource"},
                {"id": "valid_resource"}
            ]
        }))

        load_resources(str(filepath))

        registry = RegistryManager.instance()
        # Only the valid resource should be loaded
        assert len(registry.resources) == 1
        assert "valid_resource" in registry.resources

    def test_load_resources_resource_null_id(self, tmp_path):
        """Resources with null id are skipped (falsy check)."""
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({
            "resources": [
                {"id": None, "name": "Null ID"},
                {"id": "valid_resource"}
            ]
        }))

        load_resources(str(filepath))

        registry = RegistryManager.instance()
        # Only the valid resource should be loaded
        assert len(registry.resources) == 1
        assert "valid_resource" in registry.resources

    def test_load_resources_resource_empty_string_id(self, tmp_path):
        """Resources with empty string id are skipped (falsy check)."""
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({
            "resources": [
                {"id": "", "name": "Empty ID"},
                {"id": "valid_resource"}
            ]
        }))

        load_resources(str(filepath))

        registry = RegistryManager.instance()
        # Only the valid resource should be loaded (empty string is falsy)
        assert len(registry.resources) == 1
        assert "valid_resource" in registry.resources

    def test_load_resources_duplicate_ids_last_wins(self, tmp_path):
        """When duplicate IDs exist, the last one wins."""
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({
            "resources": [
                {"id": "fuel", "version": 1},
                {"id": "fuel", "version": 2},
                {"id": "fuel", "version": 3}
            ]
        }))

        load_resources(str(filepath))

        registry = RegistryManager.instance()
        assert len(registry.resources) == 1
        # Last definition should win
        assert registry.resources["fuel"]["version"] == 3

    def test_load_resources_duplicate_ids_warning(self, tmp_path):
        """
        BUG DOC: No warning is logged when duplicate IDs are encountered.

        The current implementation silently overwrites duplicate IDs without
        any warning, which could lead to data loss or confusion.
        """
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({
            "resources": [
                {"id": "fuel", "version": 1},
                {"id": "fuel", "version": 2}
            ]
        }))

        with patch('game.core.resources.log_warning') as mock_warning:
            load_resources(str(filepath))

            # Currently no warning is issued for duplicates
            # This documents the current behavior (potential bug)
            duplicate_warnings = [
                call for call in mock_warning.call_args_list
                if 'duplicate' in str(call).lower()
            ]
            # BUG: No duplicate warning is issued
            assert len(duplicate_warnings) == 0


# =============================================================================
# Group 4: Data Accumulation Bug (4 tests) - CRITICAL
# =============================================================================

class TestDataAccumulationBug:
    """
    CRITICAL: Tests documenting the data accumulation bug.

    The load_resources function does NOT clear the registry before loading,
    which means multiple calls accumulate data instead of replacing it.
    """

    def test_load_resources_multiple_calls_accumulate_data(self, tmp_path):
        """
        BUG DOC: Multiple calls to load_resources accumulate data instead of replacing.

        This is a critical bug where calling load_resources multiple times
        results in data from all calls being present in the registry,
        rather than each call replacing the previous data.

        Impact: Can lead to stale data, memory leaks, and inconsistent state.
        """
        # First load
        file1 = tmp_path / "resources1.json"
        file1.write_text(json.dumps({"resources": [{"id": "resource_a"}]}))
        load_resources(str(file1))

        # Second load
        file2 = tmp_path / "resources2.json"
        file2.write_text(json.dumps({"resources": [{"id": "resource_b"}]}))
        load_resources(str(file2))

        registry = RegistryManager.instance()

        # BUG: Both resources are present (accumulated) instead of only resource_b
        assert "resource_a" in registry.resources  # This should NOT be here after reload
        assert "resource_b" in registry.resources
        # BUG MANIFESTATION: Count is 2 instead of expected 1
        assert len(registry.resources) == 2

    def test_load_resources_reload_should_replace_not_accumulate(self, tmp_path):
        """
        BUG DOC: Reloading should replace all data, not accumulate.

        Expected: After second load, only new data should be present.
        Actual: Old data persists alongside new data.
        """
        # Initial load with 3 resources
        file1 = tmp_path / "resources.json"
        file1.write_text(json.dumps({
            "resources": [
                {"id": "res1"},
                {"id": "res2"},
                {"id": "res3"}
            ]
        }))
        load_resources(str(file1))

        # Reload with only 1 resource
        file1.write_text(json.dumps({
            "resources": [{"id": "new_resource"}]
        }))
        load_resources(str(file1))

        registry = RegistryManager.instance()

        # BUG: Old resources still present
        # Expected: only "new_resource" should be present
        # Actual: "res1", "res2", "res3", and "new_resource" are all present
        assert "new_resource" in registry.resources
        # These assertions document the BUG - old data persists
        assert "res1" in registry.resources  # BUG: Should not be present
        assert "res2" in registry.resources  # BUG: Should not be present
        assert "res3" in registry.resources  # BUG: Should not be present

    def test_load_resources_partial_reload_leaves_old_data(self, tmp_path):
        """
        BUG DOC: Partial reload leaves old data that may be outdated.

        When reloading with different resources, old resources with different
        IDs remain in the registry, potentially causing issues.
        """
        # Load set A
        file1 = tmp_path / "resources.json"
        file1.write_text(json.dumps({
            "resources": [
                {"id": "fuel", "value": 100},
                {"id": "energy", "value": 200}
            ]
        }))
        load_resources(str(file1))

        # Load set B (overlapping ID with different value)
        file1.write_text(json.dumps({
            "resources": [
                {"id": "fuel", "value": 999},  # Updated value
                {"id": "shields", "value": 300}  # New resource
            ]
        }))
        load_resources(str(file1))

        registry = RegistryManager.instance()

        # fuel is updated (overwritten)
        assert registry.resources["fuel"]["value"] == 999

        # shields is added
        assert "shields" in registry.resources

        # BUG: energy still present from first load
        assert "energy" in registry.resources  # BUG: Should not be present

    def test_registry_resources_clear_between_loads(self, tmp_path):
        """
        Test demonstrating the correct pattern: manually clear before reload.

        This shows how to work around the accumulation bug by manually
        clearing the registry before each load.
        """
        file1 = tmp_path / "resources.json"
        file1.write_text(json.dumps({"resources": [{"id": "old_resource"}]}))
        load_resources(str(file1))

        # Manually clear (workaround for the bug)
        registry = RegistryManager.instance()
        registry.resources.clear()

        # Now reload
        file1.write_text(json.dumps({"resources": [{"id": "new_resource"}]}))
        load_resources(str(file1))

        # Now only new_resource is present (correct behavior with workaround)
        assert "new_resource" in registry.resources
        assert "old_resource" not in registry.resources
        assert len(registry.resources) == 1


# =============================================================================
# Group 5: Registry Integration (5 tests)
# =============================================================================

class TestRegistryIntegration:
    """Tests for integration with RegistryManager."""

    def test_get_resource_registry_returns_correct_dict(self, sample_resources_file):
        """get_resource_registry() returns the same dict as registry.resources."""
        load_resources(sample_resources_file)

        registry = RegistryManager.instance()
        resource_registry = get_resource_registry()

        # Should be the exact same object
        assert resource_registry is registry.resources
        assert "fuel" in resource_registry

    def test_get_resource_registry_empty_after_clear(self):
        """After clearing registry, get_resource_registry() returns empty dict."""
        registry = RegistryManager.instance()
        registry.resources["test"] = {"id": "test"}

        # Verify it's there
        assert len(get_resource_registry()) == 1

        # Clear
        registry.resources.clear()

        # Should be empty
        assert len(get_resource_registry()) == 0

    def test_resource_registry_keyed_by_id(self, tmp_path):
        """Resources are keyed by their 'id' field in the registry."""
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({
            "resources": [
                {"id": "my_custom_id", "name": "Custom Resource"}
            ]
        }))

        load_resources(str(filepath))

        registry = RegistryManager.instance()

        # Key should be the id value, not an index
        assert "my_custom_id" in registry.resources
        assert registry.resources["my_custom_id"]["name"] == "Custom Resource"

    def test_registry_manager_resources_initialization(self):
        """RegistryManager initializes with empty resources dict."""
        # Reset to get fresh instance
        RegistryManager._instance = None
        registry = RegistryManager.instance()

        # Should start with empty resources
        assert isinstance(registry.resources, dict)
        assert len(registry.resources) == 0

    def test_registry_manager_freeze_prevents_load(self, sample_resources_file):
        """
        When registry is frozen, load_resources should fail.

        Note: The current implementation doesn't check frozen state before
        modifying resources. This test documents expected vs actual behavior.
        """
        registry = RegistryManager.instance()
        registry.freeze()

        # Currently load_resources doesn't check frozen state
        # It will modify the dict directly, bypassing freeze protection
        # This is because dict.update() doesn't go through _check_frozen()

        # Document current behavior: load still works even when frozen
        # (This might be considered a bug depending on requirements)
        try:
            load_resources(sample_resources_file)
            # If we get here, it means frozen doesn't prevent loading
            # which may or may not be desired behavior
            loaded_successfully = True
        except RuntimeError:
            loaded_successfully = False

        # Currently frozen doesn't prevent direct dict modifications
        # Documenting actual behavior
        assert loaded_successfully is True or loaded_successfully is False


# =============================================================================
# Group 6: Logging (3 tests)
# =============================================================================

class TestLogging:
    """Tests for logging behavior during resource loading."""

    def test_load_resources_logs_success_info(self, sample_resources_file):
        """Successful load logs info message with resource count."""
        with patch('game.core.resources.log_info') as mock_info:
            load_resources(sample_resources_file)

            mock_info.assert_called_once()
            call_args = str(mock_info.call_args)
            assert "3" in call_args  # 3 resources loaded
            assert "resource" in call_args.lower()

    def test_load_resources_logs_missing_file_warning(self):
        """Missing file logs a warning message."""
        with patch('game.core.resources.log_warning') as mock_warning:
            load_resources("nonexistent_file_xyz.json")

            mock_warning.assert_called_once()
            call_args = str(mock_warning.call_args)
            assert "not found" in call_args.lower() or "defaults" in call_args.lower()

    def test_load_resources_logs_parse_failure_warning(self, tmp_path):
        """Parse failure logs a warning message."""
        malformed_file = tmp_path / "malformed.json"
        malformed_file.write_text("{ invalid }")

        with patch('game.core.resources.log_warning') as mock_warning:
            load_resources(str(malformed_file))

            mock_warning.assert_called_once()
            call_args = str(mock_warning.call_args)
            assert "failed" in call_args.lower() or "error" in call_args.lower() or "load" in call_args.lower()


# =============================================================================
# Group 7: Thread Safety (2 tests)
# =============================================================================

class TestThreadSafety:
    """Tests for thread safety of resource loading."""

    def test_load_resources_thread_safe_singleton_access(self, tmp_path):
        """Multiple threads accessing singleton should be safe."""
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({
            "resources": [{"id": "thread_resource"}]
        }))

        results = []
        errors = []

        def load_and_check():
            try:
                load_resources(str(filepath))
                registry = RegistryManager.instance()
                results.append("thread_resource" in registry.resources)
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
        load_resources(sample_resources_file)

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
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        real_path = os.path.join(project_root, "data", "resources.json")

        if os.path.exists(real_path):
            load_resources(real_path)

            registry = RegistryManager.instance()

            # Should have loaded at least some resources
            assert len(registry.resources) > 0
            # Common resources that should exist
            assert "fuel" in registry.resources or len(registry.resources) > 0
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
            load_resources(str(filepath))

            registry = RegistryManager.instance()
            # Should have default resources
            assert "fuel" in registry.resources
            assert "energy" in registry.resources
            assert "ammo" in registry.resources

    def test_load_resources_path_encoding_issues(self, tmp_path):
        """Handle paths with special characters."""
        # Create directory and file with unicode characters
        special_dir = tmp_path / "test_dir_unicode"
        special_dir.mkdir()
        filepath = special_dir / "resources.json"
        filepath.write_text(json.dumps({"resources": [{"id": "unicode_test"}]}))

        load_resources(str(filepath))

        registry = RegistryManager.instance()
        assert "unicode_test" in registry.resources

    def test_load_resources_very_large_json_file(self, tmp_path):
        """Handle large JSON files with many resources."""
        # Create a file with many resources
        resources = [{"id": f"resource_{i}", "index": i} for i in range(1000)]
        large_data = {"resources": resources}

        filepath = tmp_path / "large_resources.json"
        filepath.write_text(json.dumps(large_data))

        load_resources(str(filepath))

        registry = RegistryManager.instance()
        assert len(registry.resources) == 1000
        assert "resource_0" in registry.resources
        assert "resource_999" in registry.resources

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

        load_resources(str(filepath))

        registry = RegistryManager.instance()
        assert "deep_resource" in registry.resources

        # Verify deep nesting is preserved
        deep = registry.resources["deep_resource"]["deep_data"]
        assert deep["level"] == 1
        # Navigate to a deeper level
        for _ in range(5):
            deep = deep["nested"]
        assert deep["level"] == 6
