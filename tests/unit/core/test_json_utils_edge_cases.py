"""
Unit tests for JSON utils edge cases.

Tests load_json error paths, save_json error paths,
and load_json_required exception behavior.
"""
import json
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from game.core.json_utils import load_json, save_json, load_json_required


class TestLoadJsonErrorPaths:
    """Tests for load_json error handling."""

    def test_load_json_file_not_found_returns_default(self, tmp_path):
        """Missing file returns the default value."""
        missing_file = tmp_path / "nonexistent.json"
        result = load_json(missing_file, default={"fallback": True})
        assert result == {"fallback": True}

    def test_load_json_invalid_json_returns_default(self, tmp_path):
        """Malformed JSON returns the default value."""
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{ this is not valid json }")

        result = load_json(bad_file, default=[])
        assert result == []

    def test_load_json_io_error_returns_default(self, tmp_path):
        """Permission/IO error returns the default value."""
        # Simulate IOError via mock
        with patch("builtins.open", side_effect=IOError("Permission denied")):
            result = load_json("some_file.json", default="error_default")
            assert result == "error_default"

    def test_load_json_custom_default(self, tmp_path):
        """Custom default value is returned on any error."""
        missing_file = tmp_path / "missing.json"

        # Test with various default types
        assert load_json(missing_file, default=42) == 42
        assert load_json(missing_file, default="custom") == "custom"
        assert load_json(missing_file, default=None) is None

    def test_load_json_success(self, tmp_path):
        """Successful load returns parsed JSON."""
        json_file = tmp_path / "valid.json"
        json_file.write_text('{"key": "value", "number": 123}')

        result = load_json(json_file)
        assert result == {"key": "value", "number": 123}


class TestSaveJsonErrorPaths:
    """Tests for save_json error handling."""

    def test_save_json_io_error_returns_false(self, tmp_path):
        """Permission/IO error returns False."""
        # Use mock to simulate IOError on write
        with patch("builtins.open", side_effect=IOError("Disk full")):
            with patch.object(Path, "mkdir"):  # Prevent mkdir errors
                result = save_json(tmp_path / "output.json", {"data": 1})
                assert result is False

    def test_save_json_type_error_returns_false(self, tmp_path):
        """Non-serializable object returns False."""
        output_file = tmp_path / "output.json"

        # Try to save a non-serializable object (e.g., a set)
        result = save_json(output_file, {"data": {1, 2, 3}})  # Set is not JSON serializable
        assert result is False

    def test_save_json_creates_parent_dirs(self, tmp_path):
        """Parent directories are created if they don't exist."""
        nested_file = tmp_path / "a" / "b" / "c" / "output.json"

        result = save_json(nested_file, {"key": "value"})

        assert result is True
        assert nested_file.exists()

        # Verify content
        loaded = json.loads(nested_file.read_text())
        assert loaded == {"key": "value"}

    def test_save_json_success(self, tmp_path):
        """Successful save returns True and writes correct content."""
        output_file = tmp_path / "output.json"
        data = {"name": "test", "items": [1, 2, 3]}

        result = save_json(output_file, data)

        assert result is True
        assert output_file.exists()
        loaded = json.loads(output_file.read_text())
        assert loaded == data


class TestLoadJsonRequired:
    """Tests for load_json_required exception behavior."""

    def test_load_json_required_missing_raises_file_not_found(self, tmp_path):
        """Missing file raises FileNotFoundError."""
        missing_file = tmp_path / "required.json"

        with pytest.raises(FileNotFoundError):
            load_json_required(missing_file)

    def test_load_json_required_invalid_raises_decode_error(self, tmp_path):
        """Invalid JSON raises json.JSONDecodeError."""
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{ invalid json content }")

        with pytest.raises(json.JSONDecodeError):
            load_json_required(bad_file)

    def test_load_json_required_success(self, tmp_path):
        """Valid file returns parsed JSON."""
        json_file = tmp_path / "valid.json"
        json_file.write_text('{"required": true}')

        result = load_json_required(json_file)
        assert result == {"required": True}
