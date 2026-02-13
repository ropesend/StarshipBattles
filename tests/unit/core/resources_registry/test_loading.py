"""
Tests for Resource Registry Loading (game/core/resources.py)

Tests the load_resources_data function for happy path, error handling,
edge cases, and logging behavior.

Test Groups:
- Group 1: Happy Path (5 tests)
- Group 2: Error Handling (5 tests)
- Group 3: Edge Cases (9 tests)
- Group 6: Logging (3 tests)
"""
import json
import os
import pytest
from unittest.mock import patch

from game.core.resources import load_resources_data
from game.core.registry import RegistryManager


# =============================================================================
# Group 1: Happy Path (5 tests)
# =============================================================================

class TestHappyPath:
    """Tests for successful resource loading scenarios."""

    def test_load_resources_basic_happy_path(self, sample_resources_file):
        """Load resources from a valid JSON file successfully."""
        result = load_resources_data(sample_resources_file)

        assert len(result) == 3
        assert "fuel" in result
        assert "energy" in result
        assert "ammo" in result

    def test_load_resources_uses_default_path(self, tmp_path, monkeypatch):
        """When no filepath is provided, use the default data/resources.json path."""
        # Create a mock resources file at the expected default location
        resources_data = {"resources": [{"id": "default_resource"}]}

        # We need to patch os.path.exists and load_json_required to simulate default path
        with patch('game.core.resources.os.path.exists') as mock_exists, \
             patch('game.core.resources.load_json_required') as mock_load:
            mock_exists.return_value = True
            mock_load.return_value = resources_data

            load_resources_data()  # No filepath argument

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

        result = load_resources_data(str(custom_path))

        assert "custom_fuel" in result
        assert result["custom_fuel"]["custom_field"] is True

    def test_load_resources_preserves_all_fields(self, tmp_path):
        """All fields from resource definitions are preserved in the result."""
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

        result = load_resources_data(str(filepath))
        plasma = result["plasma"]

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

        result = load_resources_data(str(abs_path))

        assert "abs_resource" in result


# =============================================================================
# Group 2: Error Handling (5 tests)
# =============================================================================

class TestErrorHandling:
    """Tests for error handling in resource loading."""

    def test_load_resources_missing_file_uses_defaults(self):
        """When file doesn't exist, fall back to default resources."""
        result = load_resources_data("nonexistent_file_12345.json")

        # Should have default resources
        assert "fuel" in result
        assert "energy" in result
        assert "ammo" in result
        assert len(result) == 3

    def test_load_resources_missing_file_abs_path_fallback(self, tmp_path, monkeypatch):
        """When relative path fails, try absolute path based on module location."""
        # This tests the fallback logic where it tries project_root/filepath
        with patch('game.core.resources.os.path.exists') as mock_exists:
            # First call (relative) returns False, second call (absolute) returns True
            mock_exists.side_effect = [False, False]

            result = load_resources_data("data/resources.json")

            # Should fall back to defaults since neither path exists
            assert "fuel" in result

    def test_load_resources_malformed_json_uses_defaults(self, tmp_path):
        """When JSON is malformed, fall back to default resources."""
        malformed_file = tmp_path / "malformed.json"
        malformed_file.write_text("{ not valid json }")

        result = load_resources_data(str(malformed_file))

        # Should have default resources
        assert "fuel" in result
        assert "energy" in result
        assert "ammo" in result

    def test_load_resources_invalid_json_exception_handling(self, tmp_path):
        """Exception from invalid JSON is caught and handled gracefully."""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("totally not json {{{{")

        # Should not raise an exception
        result = load_resources_data(str(invalid_file))

        # Should have defaults
        assert len(result) == 3

    def test_load_resources_empty_file_uses_defaults(self, tmp_path):
        """When file is empty, fall back to default resources."""
        empty_file = tmp_path / "empty.json"
        empty_file.write_text("")

        result = load_resources_data(str(empty_file))

        # Should have default resources
        assert "fuel" in result
        assert "energy" in result
        assert "ammo" in result


# =============================================================================
# Group 3: Edge Cases (9 tests)
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases in resource loading."""

    def test_load_resources_empty_resources_array(self, tmp_path):
        """Empty resources array results in no resources loaded."""
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({"resources": []}))

        result = load_resources_data(str(filepath))

        assert len(result) == 0

    def test_load_resources_missing_resources_key_silent_failure(self, tmp_path):
        """
        BUG DOC: Missing 'resources' key silently results in empty result.

        When the JSON file doesn't have a 'resources' key, the code uses
        data.get('resources', []) which returns an empty list, resulting
        in no resources being loaded. This is silent - no warning is logged.

        Expected behavior: Should either warn about missing key or fail explicitly.
        Actual behavior: Silently returns empty result.
        """
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({"other_key": "value"}))

        result = load_resources_data(str(filepath))

        # BUG: No resources loaded and no warning given
        assert len(result) == 0

    def test_load_resources_null_resources_value(self, tmp_path):
        """When resources value is null, handle gracefully."""
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({"resources": None}))

        # Should not crash - will iterate over None which may raise TypeError
        # The exception handler should catch this and use defaults
        result = load_resources_data(str(filepath))

        # Falls back to defaults due to exception
        assert "fuel" in result

    def test_load_resources_resources_not_array(self, tmp_path):
        """When resources is not an array, handle gracefully."""
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({"resources": {"id": "not_array"}}))

        # Iterating over a dict iterates over keys, not causing obvious error
        # but not loading resources correctly either
        result = load_resources_data(str(filepath))

        # Iterating over dict yields strings (keys), which don't have .get()
        # This should trigger exception handler and fall back to defaults
        assert "fuel" in result

    def test_load_resources_resource_missing_id_field(self, tmp_path):
        """Resources without an id field are silently skipped."""
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({
            "resources": [
                {"name": "No ID Resource"},
                {"id": "valid_resource"}
            ]
        }))

        result = load_resources_data(str(filepath))

        # Only the valid resource should be loaded
        assert len(result) == 1
        assert "valid_resource" in result

    def test_load_resources_resource_null_id(self, tmp_path):
        """Resources with null id are skipped (falsy check)."""
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({
            "resources": [
                {"id": None, "name": "Null ID"},
                {"id": "valid_resource"}
            ]
        }))

        result = load_resources_data(str(filepath))

        # Only the valid resource should be loaded
        assert len(result) == 1
        assert "valid_resource" in result

    def test_load_resources_resource_empty_string_id(self, tmp_path):
        """Resources with empty string id are skipped (falsy check)."""
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({
            "resources": [
                {"id": "", "name": "Empty ID"},
                {"id": "valid_resource"}
            ]
        }))

        result = load_resources_data(str(filepath))

        # Only the valid resource should be loaded (empty string is falsy)
        assert len(result) == 1
        assert "valid_resource" in result

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

        result = load_resources_data(str(filepath))

        assert len(result) == 1
        # Last definition should win
        assert result["fuel"]["version"] == 3

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
            load_resources_data(str(filepath))

            # Currently no warning is issued for duplicates
            # This documents the current behavior (potential bug)
            duplicate_warnings = [
                call for call in mock_warning.call_args_list
                if 'duplicate' in str(call).lower()
            ]
            # BUG: No duplicate warning is issued
            assert len(duplicate_warnings) == 0


# =============================================================================
# Group 6: Logging (3 tests)
# =============================================================================

class TestLogging:
    """Tests for logging behavior during resource loading."""

    def test_load_resources_no_info_log_on_success(self, sample_resources_file):
        """Successful load does not log info (pure function)."""
        with patch('game.core.resources.log_info') as mock_info:
            result = load_resources_data(sample_resources_file)

            # Pure function should not log success (caller handles that)
            mock_info.assert_not_called()
            # But should still return data
            assert len(result) == 3

    def test_load_resources_logs_missing_file_warning(self):
        """Missing file logs a warning message."""
        with patch('game.core.resources.log_warning') as mock_warning:
            load_resources_data("nonexistent_file_xyz.json")

            mock_warning.assert_called_once()
            call_args = str(mock_warning.call_args)
            assert "not found" in call_args.lower() or "defaults" in call_args.lower()

    def test_load_resources_logs_parse_failure_warning(self, tmp_path):
        """Parse failure logs a warning message."""
        malformed_file = tmp_path / "malformed.json"
        malformed_file.write_text("{ invalid }")

        with patch('game.core.resources.log_warning') as mock_warning:
            load_resources_data(str(malformed_file))

            mock_warning.assert_called_once()
            call_args = str(mock_warning.call_args)
            assert "failed" in call_args.lower() or "error" in call_args.lower() or "load" in call_args.lower()
