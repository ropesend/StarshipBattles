"""
Tests for game/core/resources.py module.

TCG-FND-007: Tests for resource loading functionality:
- load_resources_data() pure function
- Path resolution (_resolve_resource_path)
- Default resource fallbacks
- Error handling (JSON errors, missing files, permission errors)
"""
import pytest
import json
import os
from unittest.mock import patch, MagicMock

from game.core.resources import (
    load_resources_data,
    _get_default_resources,
    _resolve_resource_path,
)
from game.core.constants import ResourceType


class TestGetDefaultResources:
    """Tests for _get_default_resources()."""

    def test_returns_dict(self):
        """Returns a dictionary."""
        result = _get_default_resources()
        assert isinstance(result, dict)

    def test_contains_fuel(self):
        """Contains FUEL resource."""
        result = _get_default_resources()
        assert ResourceType.FUEL in result
        assert result[ResourceType.FUEL]['id'] == ResourceType.FUEL

    def test_contains_energy(self):
        """Contains ENERGY resource."""
        result = _get_default_resources()
        assert ResourceType.ENERGY in result
        assert result[ResourceType.ENERGY]['id'] == ResourceType.ENERGY

    def test_contains_ammo(self):
        """Contains AMMO resource."""
        result = _get_default_resources()
        assert ResourceType.AMMO in result
        assert result[ResourceType.AMMO]['id'] == ResourceType.AMMO

    def test_returns_new_dict_each_time(self):
        """Returns independent copies each call."""
        result1 = _get_default_resources()
        result2 = _get_default_resources()

        assert result1 is not result2
        # Modifying one doesn't affect other
        result1[ResourceType.FUEL]['test'] = 'modified'
        assert 'test' not in result2[ResourceType.FUEL]


class TestResolveResourcePath:
    """Tests for _resolve_resource_path()."""

    def test_absolute_path_exists(self, tmp_path):
        """Returns absolute path if it exists."""
        test_file = tmp_path / "resources.json"
        test_file.write_text("{}")

        result = _resolve_resource_path(str(test_file))

        assert result == str(test_file)

    def test_absolute_path_not_exists(self):
        """Returns None for non-existent absolute path."""
        result = _resolve_resource_path("/nonexistent/path/resources.json")

        assert result is None

    def test_relative_path_resolved_via_paths(self, tmp_path):
        """Relative paths resolved using Paths.ROOT_DIR."""
        # Use a unique filename that definitely doesn't exist anywhere else
        unique_name = "test_unique_resources_xyz123.json"
        test_file = tmp_path / unique_name
        test_file.write_text("{}")

        with patch('game.core.resources.Paths') as mock_paths:
            mock_paths.ROOT_DIR = str(tmp_path)

            result = _resolve_resource_path(unique_name)

            assert result == str(test_file)

    def test_relative_path_not_found(self):
        """Returns None if relative path doesn't resolve."""
        # Use a unique nonexistent filename
        nonexistent_file = "nonexistent_xyz123_456.json"

        with patch('game.core.resources.Paths') as mock_paths:
            mock_paths.ROOT_DIR = "/definitely/nonexistent/root_xyz"

            result = _resolve_resource_path(nonexistent_file)

            assert result is None


class TestLoadResourcesData:
    """Tests for load_resources_data() pure function."""

    def test_returns_dict(self, tmp_path):
        """Returns a dictionary."""
        test_file = tmp_path / "resources.json"
        test_file.write_text('{"resources": []}')

        with patch('game.core.resources._resolve_resource_path', return_value=str(test_file)):
            result = load_resources_data(str(test_file))

        assert isinstance(result, dict)

    def test_parses_resources_list(self, tmp_path):
        """Parses resources list into dict keyed by ID."""
        test_data = {
            "resources": [
                {"id": "fuel", "name": "Fuel", "max": 100},
                {"id": "energy", "name": "Energy", "max": 50}
            ]
        }
        test_file = tmp_path / "resources.json"
        test_file.write_text(json.dumps(test_data))

        with patch('game.core.resources._resolve_resource_path', return_value=str(test_file)):
            result = load_resources_data(str(test_file))

        assert 'fuel' in result
        assert result['fuel']['name'] == 'Fuel'
        assert result['fuel']['max'] == 100

        assert 'energy' in result
        assert result['energy']['name'] == 'Energy'

    def test_file_not_found_returns_defaults(self):
        """Missing file returns default resources."""
        with patch('game.core.resources._resolve_resource_path', return_value=None):
            with patch('game.core.resources.logger') as mock_log:
                result = load_resources_data("nonexistent.json")

        assert ResourceType.FUEL in result
        assert ResourceType.ENERGY in result
        assert ResourceType.AMMO in result
        mock_log.warning.assert_called()

    def test_json_decode_error_returns_defaults(self, tmp_path):
        """Invalid JSON returns default resources."""
        test_file = tmp_path / "bad.json"
        test_file.write_text("not valid json {{{")

        with patch('game.core.resources._resolve_resource_path', return_value=str(test_file)):
            with patch('game.core.resources.logger') as mock_log:
                result = load_resources_data(str(test_file))

        assert ResourceType.FUEL in result
        mock_log.warning.assert_called()
        assert 'Invalid JSON' in str(mock_log.warning.call_args)

    def test_permission_error_returns_defaults(self, tmp_path):
        """Permission error returns default resources."""
        test_file = tmp_path / "resources.json"
        test_file.write_text("{}")

        with patch('game.core.resources._resolve_resource_path', return_value=str(test_file)):
            with patch('game.core.resources.load_json_required', side_effect=PermissionError("Access denied")):
                with patch('game.core.resources.logger') as mock_log:
                    result = load_resources_data(str(test_file))

        assert ResourceType.FUEL in result
        mock_log.warning.assert_called()

    def test_os_error_returns_defaults(self, tmp_path):
        """OS error returns default resources."""
        test_file = tmp_path / "resources.json"
        test_file.write_text("{}")

        with patch('game.core.resources._resolve_resource_path', return_value=str(test_file)):
            with patch('game.core.resources.load_json_required', side_effect=OSError("Disk error")):
                with patch('game.core.resources.logger') as mock_log:
                    result = load_resources_data(str(test_file))

        assert ResourceType.FUEL in result
        mock_log.warning.assert_called()

    def test_malformed_data_returns_defaults(self, tmp_path):
        """Malformed data structure returns defaults."""
        test_file = tmp_path / "resources.json"
        # resources is not a list
        test_file.write_text('{"resources": "not a list"}')

        with patch('game.core.resources._resolve_resource_path', return_value=str(test_file)):
            with patch('game.core.resources.logger') as mock_log:
                result = load_resources_data(str(test_file))

        # Should fall back to defaults due to TypeError when iterating
        assert ResourceType.FUEL in result

    def test_empty_resources_list(self, tmp_path):
        """Empty resources list returns empty dict."""
        test_file = tmp_path / "resources.json"
        test_file.write_text('{"resources": []}')

        with patch('game.core.resources._resolve_resource_path', return_value=str(test_file)):
            result = load_resources_data(str(test_file))

        assert result == {}

    def test_resource_without_id_skipped(self, tmp_path):
        """Resources without id field are skipped."""
        test_data = {
            "resources": [
                {"name": "No ID"},  # Missing id
                {"id": "valid", "name": "Valid"}
            ]
        }
        test_file = tmp_path / "resources.json"
        test_file.write_text(json.dumps(test_data))

        with patch('game.core.resources._resolve_resource_path', return_value=str(test_file)):
            result = load_resources_data(str(test_file))

        assert 'valid' in result
        assert len(result) == 1

    def test_returns_deep_copy(self, tmp_path):
        """Returns deep copies of resource data."""
        test_data = {
            "resources": [
                {"id": "fuel", "nested": {"value": 100}}
            ]
        }
        test_file = tmp_path / "resources.json"
        test_file.write_text(json.dumps(test_data))

        with patch('game.core.resources._resolve_resource_path', return_value=str(test_file)):
            result1 = load_resources_data(str(test_file))
            result2 = load_resources_data(str(test_file))

        # Modifying nested value in result1 shouldn't affect result2
        result1['fuel']['nested']['value'] = 999
        assert result2['fuel']['nested']['value'] == 100

    def test_default_file_path(self):
        """Default path is data/resources.json."""
        with patch('game.core.resources._resolve_resource_path', return_value=None) as mock_resolve:
            with patch('game.core.resources.logger'):
                load_resources_data()

        mock_resolve.assert_called_with("data/resources.json")


class TestEdgeCases:
    """Edge case tests."""

    def test_none_id_in_resource(self, tmp_path):
        """Resource with id=None is skipped."""
        test_data = {
            "resources": [
                {"id": None, "name": "Null ID"},
                {"id": "valid", "name": "Valid"}
            ]
        }
        test_file = tmp_path / "resources.json"
        test_file.write_text(json.dumps(test_data))

        with patch('game.core.resources._resolve_resource_path', return_value=str(test_file)):
            result = load_resources_data(str(test_file))

        assert 'valid' in result
        assert None not in result
        assert len(result) == 1

    def test_empty_string_id(self, tmp_path):
        """Resource with empty string id is skipped."""
        test_data = {
            "resources": [
                {"id": "", "name": "Empty ID"},
                {"id": "valid", "name": "Valid"}
            ]
        }
        test_file = tmp_path / "resources.json"
        test_file.write_text(json.dumps(test_data))

        with patch('game.core.resources._resolve_resource_path', return_value=str(test_file)):
            result = load_resources_data(str(test_file))

        assert 'valid' in result
        assert '' not in result
        assert len(result) == 1

    def test_duplicate_ids_last_wins(self, tmp_path):
        """Duplicate IDs use last value."""
        test_data = {
            "resources": [
                {"id": "dupe", "name": "First"},
                {"id": "dupe", "name": "Second"}
            ]
        }
        test_file = tmp_path / "resources.json"
        test_file.write_text(json.dumps(test_data))

        with patch('game.core.resources._resolve_resource_path', return_value=str(test_file)):
            result = load_resources_data(str(test_file))

        assert result['dupe']['name'] == "Second"
