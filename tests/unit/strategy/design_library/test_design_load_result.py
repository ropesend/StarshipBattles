"""
Tests for DesignLoadResult dataclass and load_design_data error discrimination.

PROJ-251 Phase 3: DesignLibrary Error Discrimination
"""
import json
import os
import pytest
import tempfile
import shutil
from unittest.mock import patch

from game.strategy.systems.design_library import DesignLibrary, DesignLoadResult


class TestDesignLoadResult:
    """Tests for the DesignLoadResult dataclass."""

    def test_ok_has_success_true(self):
        """DesignLoadResult.ok() has success=True and carries data."""
        data = {"name": "Fighter", "class_id": "fighter"}
        result = DesignLoadResult.ok(data)
        assert result.success is True
        assert result.data == data
        assert result.error is None
        assert result.error_type is None

    def test_not_found_has_success_false(self):
        """DesignLoadResult.not_found() has success=False with error_type."""
        result = DesignLoadResult.not_found("my_design")
        assert result.success is False
        assert result.data is None
        assert result.error_type == "not_found"
        assert "my_design" in result.error

    def test_corrupt_json_has_success_false(self):
        """DesignLoadResult.corrupt() has success=False with error_type."""
        result = DesignLoadResult.corrupt("my_design", "unexpected EOF")
        assert result.success is False
        assert result.data is None
        assert result.error_type == "corrupt_json"
        assert "my_design" in result.error

    def test_invalid_schema_has_success_false(self):
        """DesignLoadResult.invalid_schema() has success=False."""
        result = DesignLoadResult.invalid_schema("my_design", "missing 'name' key")
        assert result.success is False
        assert result.data is None
        assert result.error_type == "invalid_schema"

    def test_permission_denied_has_success_false(self):
        """DesignLoadResult.permission_denied() has success=False."""
        result = DesignLoadResult.permission_denied("my_design", "Access denied")
        assert result.success is False
        assert result.data is None
        assert result.error_type == "permission_denied"
        assert "my_design" in result.error

    def test_io_error_has_success_false(self):
        """DesignLoadResult.io_error() has success=False."""
        result = DesignLoadResult.io_error("my_design", "disk full")
        assert result.success is False
        assert result.data is None
        assert result.error_type == "io_error"

    def test_result_is_frozen(self):
        """DesignLoadResult is immutable."""
        result = DesignLoadResult.ok({"name": "Fighter"})
        with pytest.raises(AttributeError):
            result.data = {"different": "data"}


class TestLoadDesignDataErrorDiscrimination:
    """Tests for load_design_data returning DesignLoadResult."""

    @pytest.fixture(autouse=True)
    def setup_library(self):
        """Create temporary directory for test designs."""
        tmpdir = tempfile.mkdtemp()
        designs_folder = os.path.join(tmpdir, "designs", "empire_1")
        os.makedirs(designs_folder)
        library = DesignLibrary(tmpdir, empire_id=1)
        yield tmpdir, designs_folder, library
        shutil.rmtree(tmpdir)

    def test_load_nonexistent_returns_not_found(self, setup_library):
        """Loading a nonexistent design returns not_found result."""
        _, _, library = setup_library
        result = library.load_design_data("nonexistent")
        assert result.success is False
        assert result.error_type == "not_found"

    def test_load_corrupt_json_returns_corrupt(self, setup_library):
        """Loading corrupt JSON returns corrupt_json result."""
        _, designs_folder, library = setup_library
        filepath = os.path.join(designs_folder, "bad.json")
        with open(filepath, "w") as f:
            f.write("{ not valid json }")
        result = library.load_design_data("bad")
        assert result.success is False
        assert result.error_type == "corrupt_json"
        assert "bad" in result.error

    def test_load_valid_design_returns_ok(self, setup_library):
        """Loading a valid design returns ok result with data."""
        _, designs_folder, library = setup_library
        design = {"name": "Fighter", "class_id": "fighter", "components": []}
        filepath = os.path.join(designs_folder, "fighter.json")
        with open(filepath, "w") as f:
            json.dump(design, f)
        result = library.load_design_data("fighter")
        assert result.success is True
        assert result.data["name"] == "Fighter"

    def test_load_permission_denied_returns_permission_denied(self, setup_library):
        """Loading with permission error returns permission_denied result."""
        _, designs_folder, library = setup_library
        # Create a valid file first
        filepath = os.path.join(designs_folder, "locked.json")
        with open(filepath, "w") as f:
            json.dump({"name": "Locked"}, f)

        with patch('game.strategy.systems.design_library.load_json_required',
                   side_effect=PermissionError("Access denied")):
            result = library.load_design_data("locked")
        assert result.success is False
        assert result.error_type == "permission_denied"

    def test_load_os_error_returns_io_error(self, setup_library):
        """Loading with OS error returns io_error result."""
        _, designs_folder, library = setup_library
        filepath = os.path.join(designs_folder, "broken.json")
        with open(filepath, "w") as f:
            json.dump({"name": "Broken"}, f)

        with patch('game.strategy.systems.design_library.load_json_required',
                   side_effect=OSError("Disk error")):
            result = library.load_design_data("broken")
        assert result.success is False
        assert result.error_type == "io_error"

    def test_no_designs_folder_returns_not_found(self, setup_library):
        """No designs_folder returns not_found."""
        _, _, library = setup_library
        library.designs_folder = None
        result = library.load_design_data("anything")
        assert result.success is False
        assert result.error_type == "not_found"

    def test_result_data_is_none_on_failure(self, setup_library):
        """All failure results have data=None."""
        _, _, library = setup_library
        result = library.load_design_data("nonexistent")
        assert result.data is None
