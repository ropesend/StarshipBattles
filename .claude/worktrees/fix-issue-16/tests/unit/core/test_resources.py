"""
Tests for game/core/resources.py module.

Tests for resource loading functionality:
- ResourceCatalog.from_json() and from_data()
- Path resolution (_resolve_resource_path)
- Error handling (JSON errors, missing files, permission errors)
"""
import pytest
import json
import os
from unittest.mock import patch, MagicMock

from game.core.resources import (
    ResourceCatalog,
    _resolve_resource_path,
)


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


class TestResourceCatalogFromJson:
    """Tests for ResourceCatalog.from_json()."""

    def test_returns_catalog(self, tmp_path):
        """Returns a ResourceCatalog."""
        test_file = tmp_path / "resources.json"
        test_file.write_text('{"resources": []}')

        catalog = ResourceCatalog.from_json(str(test_file))

        assert isinstance(catalog, ResourceCatalog)

    def test_parses_resources_list(self, tmp_path):
        """Parses resources list into catalog."""
        test_data = {
            "resources": [
                {"id": "fuel", "name": "Fuel", "description": "Ship fuel"},
                {"id": "energy", "name": "Energy"}
            ]
        }
        test_file = tmp_path / "resources.json"
        test_file.write_text(json.dumps(test_data))

        catalog = ResourceCatalog.from_json(str(test_file))

        assert catalog.has('fuel')
        assert catalog.get('fuel').name == 'Fuel'
        assert catalog.has('energy')
        assert catalog.get('energy').name == 'Energy'

    def test_file_not_found_returns_empty_catalog(self):
        """Missing file returns empty catalog."""
        with patch('game.core.resources.logger') as mock_log:
            catalog = ResourceCatalog.from_json("nonexistent_xyz.json")

        assert len(catalog.all_ids()) == 0
        mock_log.warning.assert_called()

    def test_json_decode_error_returns_empty_catalog(self, tmp_path):
        """Invalid JSON returns empty catalog."""
        test_file = tmp_path / "bad.json"
        test_file.write_text("not valid json {{{")

        with patch('game.core.resources.logger') as mock_log:
            catalog = ResourceCatalog.from_json(str(test_file))

        assert len(catalog.all_ids()) == 0

    def test_empty_resources_list(self, tmp_path):
        """Empty resources list returns empty catalog."""
        test_file = tmp_path / "resources.json"
        test_file.write_text('{"resources": []}')

        catalog = ResourceCatalog.from_json(str(test_file))

        assert catalog.all_ids() == []

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

        catalog = ResourceCatalog.from_json(str(test_file))

        assert catalog.has('valid')
        assert len(catalog.all_ids()) == 1


class TestResourceCatalogEdgeCases:
    """Edge case tests for ResourceCatalog."""

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

        catalog = ResourceCatalog.from_json(str(test_file))

        assert catalog.has('valid')
        assert len(catalog.all_ids()) == 1

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

        catalog = ResourceCatalog.from_json(str(test_file))

        assert catalog.has('valid')
        assert not catalog.has('')
        assert len(catalog.all_ids()) == 1

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

        catalog = ResourceCatalog.from_json(str(test_file))

        assert catalog.get('dupe').name == "Second"
