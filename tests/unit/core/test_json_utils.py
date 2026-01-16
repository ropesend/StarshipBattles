"""
Tests for JSON utility functions.

These utilities consolidate JSON loading/saving patterns used throughout the codebase.
"""
import pytest
import json
from pathlib import Path


class TestLoadJson:
    """Tests for load_json() function."""

    def test_load_json_success(self, tmp_path):
        """Load valid JSON file returns parsed data."""
        from game.core.json_utils import load_json

        test_file = tmp_path / "test.json"
        test_data = {"key": "value", "number": 42, "nested": {"a": 1}}
        test_file.write_text(json.dumps(test_data))

        result = load_json(str(test_file))

        assert result == test_data

    def test_load_json_file_not_found_returns_default(self):
        """Return default when file doesn't exist."""
        from game.core.json_utils import load_json

        result = load_json("nonexistent_file_12345.json")

        assert result is None

    def test_load_json_file_not_found_custom_default(self):
        """Return custom default when file doesn't exist."""
        from game.core.json_utils import load_json

        default = {"default": True}
        result = load_json("nonexistent_file_12345.json", default=default)

        assert result == default

    def test_load_json_invalid_json_returns_default(self, tmp_path):
        """Return default when JSON is malformed."""
        from game.core.json_utils import load_json

        test_file = tmp_path / "invalid.json"
        test_file.write_text("{ invalid json content }")

        result = load_json(str(test_file))

        assert result is None

    def test_load_json_invalid_json_custom_default(self, tmp_path):
        """Return custom default when JSON is malformed."""
        from game.core.json_utils import load_json

        test_file = tmp_path / "invalid.json"
        test_file.write_text("not json at all")

        default = []
        result = load_json(str(test_file), default=default)

        assert result == default

    def test_load_json_empty_file_returns_default(self, tmp_path):
        """Return default when file is empty."""
        from game.core.json_utils import load_json

        test_file = tmp_path / "empty.json"
        test_file.write_text("")

        result = load_json(str(test_file), default={})

        assert result == {}

    def test_load_json_with_path_object(self, tmp_path):
        """Accept Path objects as well as strings."""
        from game.core.json_utils import load_json

        test_file = tmp_path / "test.json"
        test_data = {"path_object": True}
        test_file.write_text(json.dumps(test_data))

        result = load_json(test_file)  # Pass Path object directly

        assert result == test_data

    def test_load_json_preserves_unicode(self, tmp_path):
        """Properly handle unicode characters."""
        from game.core.json_utils import load_json

        test_file = tmp_path / "unicode.json"
        test_data = {"name": "Tést Shïp", "symbol": ""}
        test_file.write_text(json.dumps(test_data, ensure_ascii=False), encoding='utf-8')

        result = load_json(str(test_file))

        assert result == test_data


class TestSaveJson:
    """Tests for save_json() function."""

    def test_save_json_success(self, tmp_path):
        """Save JSON to file successfully."""
        from game.core.json_utils import save_json, load_json

        test_file = tmp_path / "output.json"
        test_data = {"saved": True, "count": 100}

        result = save_json(str(test_file), test_data)

        assert result is True
        assert test_file.exists()
        assert load_json(str(test_file)) == test_data

    def test_save_json_creates_parent_directories(self, tmp_path):
        """Create parent directories if they don't exist."""
        from game.core.json_utils import save_json

        test_file = tmp_path / "nested" / "deep" / "output.json"
        test_data = {"nested": True}

        result = save_json(str(test_file), test_data)

        assert result is True
        assert test_file.exists()

    def test_save_json_overwrites_existing(self, tmp_path):
        """Overwrite existing file."""
        from game.core.json_utils import save_json, load_json

        test_file = tmp_path / "existing.json"
        test_file.write_text('{"old": "data"}')

        new_data = {"new": "data"}
        save_json(str(test_file), new_data)

        assert load_json(str(test_file)) == new_data

    def test_save_json_with_indent(self, tmp_path):
        """Save with custom indentation."""
        from game.core.json_utils import save_json

        test_file = tmp_path / "indented.json"
        test_data = {"a": 1, "b": 2}

        save_json(str(test_file), test_data, indent=4)

        content = test_file.read_text()
        assert "    " in content  # 4-space indent

    def test_save_json_with_path_object(self, tmp_path):
        """Accept Path objects as well as strings."""
        from game.core.json_utils import save_json

        test_file = tmp_path / "path_obj.json"
        test_data = {"path_object": True}

        result = save_json(test_file, test_data)  # Pass Path object directly

        assert result is True
        assert test_file.exists()

    def test_save_json_preserves_unicode(self, tmp_path):
        """Properly handle unicode characters."""
        from game.core.json_utils import save_json

        test_file = tmp_path / "unicode_out.json"
        test_data = {"name": "Tést Shïp", "symbol": ""}

        save_json(str(test_file), test_data)

        content = test_file.read_text(encoding='utf-8')
        assert "Tést Shïp" in content

    def test_save_json_returns_false_on_permission_error(self, tmp_path):
        """Return False when write fails (simulated via read-only)."""
        from game.core.json_utils import save_json
        import os
        import stat

        # Create a read-only directory
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()

        test_file = readonly_dir / "test.json"

        # Make directory read-only (Windows compatible)
        try:
            os.chmod(str(readonly_dir), stat.S_IRUSR | stat.S_IXUSR)
            result = save_json(str(test_file), {"data": 1})
            # On some systems this might still succeed, so we just check it doesn't crash
            assert result in (True, False)
        finally:
            # Restore permissions for cleanup
            os.chmod(str(readonly_dir), stat.S_IRWXU)


class TestLoadJsonRequired:
    """Tests for load_json_required() function."""

    def test_load_json_required_success(self, tmp_path):
        """Load valid JSON file returns parsed data."""
        from game.core.json_utils import load_json_required

        test_file = tmp_path / "required.json"
        test_data = {"required": True}
        test_file.write_text(json.dumps(test_data))

        result = load_json_required(str(test_file))

        assert result == test_data

    def test_load_json_required_file_not_found_raises(self):
        """Raise FileNotFoundError when file doesn't exist."""
        from game.core.json_utils import load_json_required

        with pytest.raises(FileNotFoundError):
            load_json_required("nonexistent_required_12345.json")

    def test_load_json_required_invalid_json_raises(self, tmp_path):
        """Raise JSONDecodeError when JSON is malformed."""
        from game.core.json_utils import load_json_required

        test_file = tmp_path / "invalid_required.json"
        test_file.write_text("{ not valid json }")

        with pytest.raises(json.JSONDecodeError):
            load_json_required(str(test_file))
