"""
Tests for error logging in DesignLibrary (ERR-005, ERR-010).
"""

import pytest
import tempfile
import shutil
import os
import json
import logging
from unittest.mock import patch
from game.strategy.systems.design_library import DesignLibrary


class TestDesignLibraryErrorLogging:
    """Tests for error logging in DesignLibrary (ERR-005, ERR-010)."""

    @pytest.fixture(autouse=True)
    def setup_library(self):
        """Create temporary directory for test designs"""
        tmpdir = tempfile.mkdtemp()
        designs_folder = os.path.join(tmpdir, "designs", "empire_1")
        os.makedirs(designs_folder)

        library = DesignLibrary(tmpdir, empire_id=1)

        yield tmpdir, designs_folder, library

        shutil.rmtree(tmpdir)

    def test_init_folder_creation_failure_logs_with_path(self, caplog):
        """Init folder creation failure should log with path context (ERR-010)."""
        tmpdir = tempfile.mkdtemp()
        try:
            # Track calls to makedirs
            call_count = 0
            original_makedirs = os.makedirs

            def mock_makedirs(path, *args, **kwargs):
                nonlocal call_count
                call_count += 1
                # Fail on first call (primary folder), succeed on second (fallback)
                if call_count == 1:
                    raise PermissionError("Access denied")
                return original_makedirs(path, *args, **kwargs)

            with patch('os.makedirs', side_effect=mock_makedirs):
                with caplog.at_level(logging.ERROR):
                    # This should fail to create the folder and log with path context
                    library = DesignLibrary(tmpdir, empire_id=99)

            # Should have logged an error with the path - find the permission/creation error
            error_logs = [r for r in caplog.records
                         if r.levelno >= logging.ERROR and ('Permission denied' in r.message or 'designs folder' in r.message)]
            assert len(error_logs) > 0, "Should log folder creation error"
            error_text = error_logs[0].message
            # The error should include the actual path being created
            assert 'empire_99' in error_text or tmpdir in error_text, \
                f"Error should include path context. Got: {error_text}"
        finally:
            shutil.rmtree(tmpdir)

    def test_increment_built_count_logs_on_failure(self, setup_library, caplog):
        """increment_built_count failure should log warning (ERR-010)."""
        tmpdir, designs_folder, library = setup_library

        # Create a design with corrupted JSON
        corrupted_file = os.path.join(designs_folder, "Corrupt_Design.json")
        with open(corrupted_file, "w") as f:
            f.write("{ not valid json }")

        with caplog.at_level(logging.WARNING):
            result = library.increment_built_count("Corrupt_Design")

        assert result is False
        # Should have logged a warning
        warning_logs = [r for r in caplog.records if r.levelno >= logging.WARNING]
        assert len(warning_logs) > 0, "Should log warning when increment_built_count fails"
        warning_text = ' '.join(r.message for r in warning_logs)
        assert 'Corrupt_Design' in warning_text, "Warning should include design_id"

    def test_increment_built_count_nonexistent_silent(self, setup_library, caplog):
        """increment_built_count for missing design should not log (normal behavior)."""
        tmpdir, designs_folder, library = setup_library

        with caplog.at_level(logging.WARNING):
            result = library.increment_built_count("Nonexistent_Design")

        assert result is False
        # Should NOT log warning for simply missing files (expected behavior)
        design_warnings = [r for r in caplog.records
                          if 'Nonexistent_Design' in r.message]
        assert len(design_warnings) == 0, "Missing file should not log warning"

    def test_load_design_data_logs_on_corrupted_file(self, setup_library, caplog):
        """Loading corrupted design file should log warning with context."""
        tmpdir, designs_folder, library = setup_library

        # Create corrupted design file
        corrupted_file = os.path.join(designs_folder, "Bad_Design.json")
        with open(corrupted_file, "w") as f:
            f.write("{ invalid json }")

        with caplog.at_level(logging.WARNING):
            result = library.load_design_data("Bad_Design")

        assert result is None
        # Should have logged a warning
        warning_logs = [r for r in caplog.records if r.levelno >= logging.WARNING]
        assert len(warning_logs) > 0, "Should log warning for corrupted design"
        # Warning should include design_id
        warning_text = ' '.join(r.message for r in warning_logs)
        assert 'Bad_Design' in warning_text, "Warning should include design_id"

    def test_load_design_data_no_warning_for_missing(self, setup_library, caplog):
        """Missing design file should not log warning (normal behavior)."""
        tmpdir, designs_folder, library = setup_library

        with caplog.at_level(logging.WARNING):
            result = library.load_design_data("Nonexistent_Design")

        assert result is None
        # Should NOT log warning for simply missing files
        design_warnings = [r for r in caplog.records
                          if 'Nonexistent_Design' in r.message]
        assert len(design_warnings) == 0, "Missing file should not log warning"

    def test_load_design_data_success_no_warning(self, setup_library, caplog):
        """Successful load should not produce warnings."""
        tmpdir, designs_folder, library = setup_library

        # Create valid design file
        valid_design = {
            "name": "Good Design",
            "class_id": "fighter",
            "components": []
        }
        design_file = os.path.join(designs_folder, "Good_Design.json")
        with open(design_file, "w") as f:
            json.dump(valid_design, f)

        with caplog.at_level(logging.WARNING):
            result = library.load_design_data("Good_Design")

        assert result is not None
        assert result["name"] == "Good Design"
        # No warnings for successful load
        design_warnings = [r for r in caplog.records
                          if 'Good_Design' in r.message]
        assert len(design_warnings) == 0, "Successful load should not log warning"
