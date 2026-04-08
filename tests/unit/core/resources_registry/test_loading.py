"""
Tests for Resource Catalog Loading (game/core/resources.py)

Tests the ResourceCatalog.from_json() and from_data() methods for happy path,
error handling, edge cases, and logging behavior.

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

from game.core.resources import ResourceCatalog


# =============================================================================
# Group 1: Happy Path (5 tests)
# =============================================================================

class TestHappyPath:
    """Tests for successful resource loading scenarios."""

    def test_load_resources_basic_happy_path(self, sample_resources_file):
        """Load resources from a valid JSON file successfully."""
        catalog = ResourceCatalog.from_json(sample_resources_file)

        assert len(catalog.all_ids()) == 3
        assert catalog.has("fuel")
        assert catalog.has("energy")
        assert catalog.has("ammo")

    def test_load_resources_uses_default_path(self, tmp_path, monkeypatch):
        """When no filepath is provided, use Paths.RESOURCES_FILE."""
        resources_data = {"resources": [{"id": "default_resource"}]}

        with patch('game.core.resources.os.path.exists') as mock_exists, \
             patch('game.core.resources.load_json_required') as mock_load:
            mock_exists.return_value = True
            mock_load.return_value = resources_data

            ResourceCatalog.from_json()  # No filepath argument

            mock_exists.assert_called()
            call_args = mock_exists.call_args_list[0][0][0]
            assert call_args.endswith(os.path.join("data", "resources.json"))

    def test_load_resources_with_custom_filepath(self, tmp_path):
        """Load resources from a custom filepath."""
        custom_path = tmp_path / "custom" / "my_resources.json"
        custom_path.parent.mkdir(parents=True, exist_ok=True)
        custom_data = {"resources": [{"id": "custom_fuel", "name": "Custom Fuel"}]}
        custom_path.write_text(json.dumps(custom_data))

        catalog = ResourceCatalog.from_json(str(custom_path))

        assert catalog.has("custom_fuel")
        assert catalog.get("custom_fuel").name == "Custom Fuel"

    def test_load_resources_preserves_standard_fields(self, tmp_path):
        """Standard fields from resource definitions are preserved."""
        resources_data = {
            "resources": [
                {
                    "id": "plasma",
                    "name": "Plasma Energy",
                    "description": "High-energy plasma for weapons",
                    "display_group": "operational",
                    "has_quality": True,
                }
            ]
        }
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps(resources_data))

        catalog = ResourceCatalog.from_json(str(filepath))
        plasma = catalog.get("plasma")

        assert plasma.id == "plasma"
        assert plasma.name == "Plasma Energy"
        assert plasma.description == "High-energy plasma for weapons"
        assert plasma.display_group == "operational"
        assert plasma.has_quality is True

    def test_load_resources_handles_absolute_path(self, tmp_path):
        """Load resources using an absolute path works correctly."""
        abs_path = tmp_path / "absolute_resources.json"
        abs_path.write_text(json.dumps({"resources": [{"id": "abs_resource"}]}))

        assert os.path.isabs(str(abs_path))

        catalog = ResourceCatalog.from_json(str(abs_path))

        assert catalog.has("abs_resource")


# =============================================================================
# Group 2: Error Handling (5 tests)
# =============================================================================

class TestErrorHandling:
    """Tests for error handling in resource loading."""

    def test_load_resources_missing_file_returns_empty(self):
        """When file doesn't exist, return empty catalog."""
        catalog = ResourceCatalog.from_json("nonexistent_file_12345.json")

        assert len(catalog.all_ids()) == 0

    def test_load_resources_missing_file_abs_path_fallback(self, tmp_path, monkeypatch):
        """When relative path fails, try absolute path based on module location."""
        with patch('game.core.resources.os.path.exists') as mock_exists:
            mock_exists.side_effect = [False, False]

            catalog = ResourceCatalog.from_json("data/resources.json")

            assert len(catalog.all_ids()) == 0

    def test_load_resources_malformed_json_returns_empty(self, tmp_path):
        """When JSON is malformed, return empty catalog."""
        malformed_file = tmp_path / "malformed.json"
        malformed_file.write_text("{ not valid json }")

        catalog = ResourceCatalog.from_json(str(malformed_file))

        assert len(catalog.all_ids()) == 0

    def test_load_resources_invalid_json_exception_handling(self, tmp_path):
        """Exception from invalid JSON is caught and handled gracefully."""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("totally not json {{{{")

        # Should not raise an exception
        catalog = ResourceCatalog.from_json(str(invalid_file))

        assert len(catalog.all_ids()) == 0

    def test_load_resources_empty_file_returns_empty(self, tmp_path):
        """When file is empty, return empty catalog."""
        empty_file = tmp_path / "empty.json"
        empty_file.write_text("")

        catalog = ResourceCatalog.from_json(str(empty_file))

        assert len(catalog.all_ids()) == 0


# =============================================================================
# Group 3: Edge Cases (9 tests)
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases in resource loading."""

    def test_load_resources_empty_resources_array(self, tmp_path):
        """Empty resources array results in no resources loaded."""
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({"resources": []}))

        catalog = ResourceCatalog.from_json(str(filepath))

        assert len(catalog.all_ids()) == 0

    def test_load_resources_missing_resources_key(self, tmp_path):
        """Missing 'resources' key results in empty catalog."""
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({"other_key": "value"}))

        catalog = ResourceCatalog.from_json(str(filepath))

        assert len(catalog.all_ids()) == 0

    def test_load_resources_null_resources_value(self, tmp_path):
        """When resources value is null, handle gracefully."""
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({"resources": None}))

        catalog = ResourceCatalog.from_json(str(filepath))

        # Should handle gracefully (empty or defaults)
        assert isinstance(catalog, ResourceCatalog)

    def test_load_resources_resources_not_array(self, tmp_path):
        """When resources is not an array, handle gracefully."""
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({"resources": {"id": "not_array"}}))

        catalog = ResourceCatalog.from_json(str(filepath))

        assert isinstance(catalog, ResourceCatalog)

    def test_load_resources_resource_missing_id_field(self, tmp_path):
        """Resources without an id field are silently skipped."""
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({
            "resources": [
                {"name": "No ID Resource"},
                {"id": "valid_resource"}
            ]
        }))

        catalog = ResourceCatalog.from_json(str(filepath))

        assert len(catalog.all_ids()) == 1
        assert catalog.has("valid_resource")

    def test_load_resources_resource_null_id(self, tmp_path):
        """Resources with null id are skipped (falsy check)."""
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({
            "resources": [
                {"id": None, "name": "Null ID"},
                {"id": "valid_resource"}
            ]
        }))

        catalog = ResourceCatalog.from_json(str(filepath))

        assert len(catalog.all_ids()) == 1
        assert catalog.has("valid_resource")

    def test_load_resources_resource_empty_string_id(self, tmp_path):
        """Resources with empty string id are skipped (falsy check)."""
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({
            "resources": [
                {"id": "", "name": "Empty ID"},
                {"id": "valid_resource"}
            ]
        }))

        catalog = ResourceCatalog.from_json(str(filepath))

        assert len(catalog.all_ids()) == 1
        assert catalog.has("valid_resource")

    def test_load_resources_duplicate_ids_last_wins(self, tmp_path):
        """When duplicate IDs exist, the last one wins."""
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({
            "resources": [
                {"id": "fuel", "name": "Version 1"},
                {"id": "fuel", "name": "Version 2"},
                {"id": "fuel", "name": "Version 3"}
            ]
        }))

        catalog = ResourceCatalog.from_json(str(filepath))

        assert len(catalog.all_ids()) == 1
        assert catalog.get("fuel").name == "Version 3"

    def test_load_resources_duplicate_ids_no_warning(self, tmp_path):
        """No warning is logged when duplicate IDs are encountered."""
        filepath = tmp_path / "resources.json"
        filepath.write_text(json.dumps({
            "resources": [
                {"id": "fuel", "name": "Version 1"},
                {"id": "fuel", "name": "Version 2"}
            ]
        }))

        with patch('game.core.resources.logger') as mock_logger:
            ResourceCatalog.from_json(str(filepath))

            duplicate_warnings = [
                call for call in mock_logger.warning.call_args_list
                if 'duplicate' in str(call).lower()
            ]
            assert len(duplicate_warnings) == 0


# =============================================================================
# Group 6: Logging (3 tests)
# =============================================================================

class TestLogging:
    """Tests for logging behavior during resource loading."""

    def test_load_resources_no_info_log_on_success(self, sample_resources_file):
        """Successful load does not log info."""
        with patch('game.core.resources.logger') as mock_logger:
            catalog = ResourceCatalog.from_json(sample_resources_file)

            mock_logger.info.assert_not_called()
            assert len(catalog.all_ids()) == 3

    def test_load_resources_logs_missing_file_warning(self):
        """Missing file logs a warning message."""
        with patch('game.core.resources.logger') as mock_logger:
            ResourceCatalog.from_json("nonexistent_file_xyz.json")

            mock_logger.warning.assert_called_once()
            call_args = str(mock_logger.warning.call_args)
            assert "not found" in call_args.lower()

    def test_load_resources_logs_parse_failure_warning(self, tmp_path):
        """Parse failure logs a warning message."""
        malformed_file = tmp_path / "malformed.json"
        malformed_file.write_text("{ invalid }")

        with patch('game.core.resources.logger') as mock_logger:
            ResourceCatalog.from_json(str(malformed_file))

            mock_logger.warning.assert_called_once()
            call_args = str(mock_logger.warning.call_args)
            assert "failed" in call_args.lower() or "load" in call_args.lower()
