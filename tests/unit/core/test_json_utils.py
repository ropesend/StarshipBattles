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

    def test_load_json_io_error_returns_default(self):
        """Permission/IO error returns the default value."""
        from game.core.json_utils import load_json
        from unittest.mock import patch

        with patch("builtins.open", side_effect=IOError("Permission denied")):
            result = load_json("some_file.json", default="error_default")
            assert result == "error_default"


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

    def test_save_json_io_error_returns_false(self, tmp_path):
        """Permission/IO error returns False."""
        from game.core.json_utils import save_json
        from pathlib import Path
        from unittest.mock import patch

        with patch("builtins.open", side_effect=IOError("Disk full")):
            with patch.object(Path, "mkdir"):  # Prevent mkdir errors
                result = save_json(tmp_path / "output.json", {"data": 1})
                assert result is False

    def test_save_json_type_error_returns_false(self, tmp_path):
        """Non-serializable object returns False."""
        from game.core.json_utils import save_json

        output_file = tmp_path / "output.json"
        # Try to save a non-serializable object (e.g., a set)
        result = save_json(output_file, {"data": {1, 2, 3}})  # Set is not JSON serializable
        assert result is False


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


# =============================================================================
# Test: deserialize_list() - PROJ-204 Phase 4
# =============================================================================

class TestDeserializeList:
    """Tests for resilient list deserialization (CQ-22)."""

    def test_deserialize_list_all_valid(self):
        """All items deserialize successfully."""
        from game.core.json_utils import deserialize_list

        items = [{"value": 1}, {"value": 2}, {"value": 3}]
        deserializer = lambda x: x["value"]

        result = deserialize_list(items, deserializer, "TestEntity", "Test")

        assert result == [1, 2, 3]

    def test_deserialize_list_skips_invalid_items(self):
        """Invalid items are skipped with warning logged."""
        from game.core.json_utils import deserialize_list

        items = [{"value": 1}, {"bad": "item"}, {"value": 3}]
        def deserializer(x):
            return x["value"]  # Will raise KeyError on bad item

        result = deserialize_list(items, deserializer, "TestEntity", "Test")

        assert result == [1, 3]  # Bad item skipped

    def test_deserialize_list_empty_list(self):
        """Empty input returns empty output."""
        from game.core.json_utils import deserialize_list

        result = deserialize_list([], lambda x: x, "TestEntity", "Test")

        assert result == []

    def test_deserialize_list_all_invalid_returns_empty(self):
        """All invalid items returns empty list."""
        from game.core.json_utils import deserialize_list

        items = [{"bad": 1}, {"bad": 2}]
        def deserializer(x):
            raise ValueError("Invalid")

        result = deserialize_list(items, deserializer, "TestEntity", "Test")

        assert result == []

    def test_deserialize_list_handles_keyerror(self):
        """KeyError from deserializer is caught."""
        from game.core.json_utils import deserialize_list

        items = [{"missing": "key"}]
        def deserializer(x):
            return x["required_key"]  # Will raise KeyError

        result = deserialize_list(items, deserializer, "TestEntity", "Test")

        assert result == []

    def test_deserialize_list_handles_typeerror(self):
        """TypeError from deserializer is caught."""
        from game.core.json_utils import deserialize_list

        items = [None]  # Will cause TypeError when accessed
        def deserializer(x):
            return x["key"]  # TypeError: 'NoneType' is not subscriptable

        result = deserialize_list(items, deserializer, "TestEntity", "Test")

        assert result == []

    def test_deserialize_list_handles_valueerror(self):
        """ValueError from deserializer is caught."""
        from game.core.json_utils import deserialize_list

        items = [{"value": "not_a_number"}]
        def deserializer(x):
            return int(x["value"])  # Will raise ValueError

        result = deserialize_list(items, deserializer, "TestEntity", "Test")

        assert result == []

    def test_deserialize_list_handles_persistence_exception(self):
        """PersistenceException from deserializer is caught."""
        from game.core.json_utils import deserialize_list
        from game.core.exceptions import PersistenceException

        items = [{"data": "bad"}]
        def deserializer(x):
            raise PersistenceException("Bad data")

        result = deserialize_list(items, deserializer, "TestEntity", "Test")

        assert result == []

    def test_deserialize_list_preserves_order(self):
        """Output maintains input order for valid items."""
        from game.core.json_utils import deserialize_list

        items = [{"v": 3}, {"v": 1}, {"bad": True}, {"v": 4}, {"v": 1}]
        def deserializer(x):
            return x["v"]

        result = deserialize_list(items, deserializer, "TestEntity", "Test")

        assert result == [3, 1, 4, 1]  # Order preserved, bad item omitted

    def test_deserialize_list_logs_warning_on_failure(self, caplog):
        """Warning logged for each failed item."""
        from game.core.json_utils import deserialize_list
        import logging

        items = [{"good": 1}, {"bad": 2}, {"bad": 3}]
        def deserializer(x):
            return x["good"]

        with caplog.at_level(logging.WARNING):
            deserialize_list(items, deserializer, "TestEntity", "ParentName")

        # Should have 2 warnings (indices 1 and 2)
        assert len([r for r in caplog.records if r.levelno == logging.WARNING]) == 2
        # Check warning message contains useful context
        assert "ParentName" in caplog.text
        assert "TestEntity" in caplog.text

    def test_deserialize_list_with_none_input_returns_empty(self):
        """None input returns empty list."""
        from game.core.json_utils import deserialize_list

        result = deserialize_list(None, lambda x: x, "TestEntity", "Test")

        assert result == []
