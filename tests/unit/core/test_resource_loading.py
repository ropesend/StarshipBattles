"""
Unit tests for game/core/resources.py

Tests resource loading, error paths, and default fallbacks.
"""
import json
import pytest
from unittest.mock import patch, MagicMock

from game.core.resources import (
    _get_default_resources,
    _resolve_resource_path,
    load_resources_data,
)
from game.core.constants import ResourceType


# =============================================================================
# _get_default_resources Tests
# =============================================================================

class TestGetDefaultResources:
    """Tests for _get_default_resources function."""

    def test_default_resources_has_fuel_energy_ammo(self):
        """Returns dict with all 3 resource types."""
        defaults = _get_default_resources()

        assert ResourceType.FUEL in defaults
        assert ResourceType.ENERGY in defaults
        assert ResourceType.AMMO in defaults
        assert len(defaults) == 3


# =============================================================================
# _resolve_resource_path Tests
# =============================================================================

class TestResolveResourcePath:
    """Tests for _resolve_resource_path function."""

    def test_resolve_existing_file(self, tmp_path):
        """Returns path when file exists at given location."""
        test_file = tmp_path / "test.json"
        test_file.write_text("{}")

        result = _resolve_resource_path(str(test_file))
        assert result == str(test_file)

    def test_resolve_nonexistent_returns_none(self):
        """Returns None when file doesn't exist."""
        result = _resolve_resource_path("/nonexistent/path/to/file.json")
        assert result is None


# =============================================================================
# load_resources_data Tests
# =============================================================================

class TestLoadResourcesData:
    """Tests for load_resources_data function."""

    def test_load_resources_data_success(self, tmp_path):
        """Parses valid JSON into dict keyed by ID."""
        test_file = tmp_path / "resources.json"
        test_data = {
            "resources": [
                {"id": "fuel", "name": "Fuel"},
                {"id": "energy", "name": "Energy"},
            ]
        }
        test_file.write_text(json.dumps(test_data))

        with patch('game.core.resources._resolve_resource_path', return_value=str(test_file)):
            result = load_resources_data(str(test_file))

        assert "fuel" in result
        assert "energy" in result
        assert result["fuel"]["name"] == "Fuel"

    def test_load_resources_data_file_not_found(self):
        """Returns defaults on FileNotFoundError."""
        with patch('game.core.resources._resolve_resource_path', return_value="/some/path.json"):
            with patch('game.core.resources.load_json_required', side_effect=FileNotFoundError("test")):
                result = load_resources_data()

        assert ResourceType.FUEL in result
        assert ResourceType.ENERGY in result
        assert ResourceType.AMMO in result

    def test_load_resources_data_invalid_json(self):
        """Returns defaults on JSONDecodeError."""
        with patch('game.core.resources._resolve_resource_path', return_value="/some/path.json"):
            with patch('game.core.resources.load_json_required',
                      side_effect=json.JSONDecodeError("test", "doc", 0)):
                result = load_resources_data()

        assert ResourceType.FUEL in result

    def test_load_resources_data_permission_error(self):
        """Returns defaults on PermissionError."""
        with patch('game.core.resources._resolve_resource_path', return_value="/some/path.json"):
            with patch('game.core.resources.load_json_required',
                      side_effect=PermissionError("test")):
                result = load_resources_data()

        assert ResourceType.FUEL in result

    def test_load_resources_data_malformed_data(self):
        """Returns defaults on TypeError (malformed structure)."""
        with patch('game.core.resources._resolve_resource_path', return_value="/some/path.json"):
            # Simulate malformed data that causes TypeError during iteration
            with patch('game.core.resources.load_json_required', return_value=None):
                result = load_resources_data()

        # Should get defaults due to AttributeError (None.get())
        assert ResourceType.FUEL in result

    def test_load_resources_data_no_file_returns_defaults(self):
        """Returns defaults when path resolves to None."""
        with patch('game.core.resources._resolve_resource_path', return_value=None):
            result = load_resources_data()

        assert ResourceType.FUEL in result
        assert ResourceType.ENERGY in result
        assert ResourceType.AMMO in result

    def test_load_resources_data_empty_resources_list(self, tmp_path):
        """Returns empty dict for empty resources array."""
        test_file = tmp_path / "resources.json"
        test_data = {"resources": []}
        test_file.write_text(json.dumps(test_data))

        with patch('game.core.resources._resolve_resource_path', return_value=str(test_file)):
            result = load_resources_data(str(test_file))

        assert result == {}


# =============================================================================
# load_resources_data Integration Tests
# =============================================================================

class TestLoadResourcesData:
    """Tests for load_resources_data function (pure DI pattern)."""

    def test_load_resources_data_returns_data(self, tmp_path):
        """Returns parsed resource data."""
        test_file = tmp_path / "resources.json"
        test_data = {
            "resources": [
                {"id": "test_resource", "name": "Test"},
            ]
        }
        test_file.write_text(json.dumps(test_data))

        result = load_resources_data(str(test_file))

        assert "test_resource" in result
        assert result["test_resource"]["name"] == "Test"

    def test_load_resources_data_file_not_found_returns_defaults(self):
        """Returns defaults when file not found."""
        with patch('game.core.resources._resolve_resource_path', return_value="/some/path.json"):
            with patch('game.core.resources.load_json_required', side_effect=FileNotFoundError("test")):
                result = load_resources_data()

        assert ResourceType.FUEL in result

    def test_load_resources_data_invalid_json_returns_defaults(self):
        """Returns defaults on invalid JSON."""
        with patch('game.core.resources._resolve_resource_path', return_value="/some/path.json"):
            with patch('game.core.resources.load_json_required',
                      side_effect=json.JSONDecodeError("test", "doc", 0)):
                result = load_resources_data()

        assert ResourceType.FUEL in result

    def test_load_resources_data_missing_file_returns_defaults(self):
        """Unresolvable path returns defaults."""
        with patch('game.core.resources._resolve_resource_path', return_value=None):
            result = load_resources_data()

        assert ResourceType.FUEL in result
