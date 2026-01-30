"""
Tests for DesignLibrary
"""
import pytest
import tempfile
import shutil
import os
from unittest.mock import MagicMock, patch
from game.strategy.systems.design_library import DesignLibrary
from game.core.json_utils import save_json


class TestDesignLibrary:
    """Tests for DesignLibrary class"""

    @pytest.fixture(autouse=True)
    def setup_library(self):
        """Create temporary directory for test designs"""
        tmpdir = tempfile.mkdtemp()
        # Create per-empire folder structure (empire_id=1)
        designs_folder = os.path.join(tmpdir, "designs", "empire_1")
        os.makedirs(designs_folder)

        library = DesignLibrary(tmpdir, empire_id=1)

        yield tmpdir, designs_folder, library

        shutil.rmtree(tmpdir)

    def test_initialization_creates_folder(self):
        """Initialization creates designs folder if missing"""
        new_tmpdir = tempfile.mkdtemp()
        try:
            library = DesignLibrary(new_tmpdir, empire_id=1)
            assert os.path.exists(library.designs_folder)
        finally:
            shutil.rmtree(new_tmpdir)

    def test_scan_designs_empty(self, setup_library):
        """Scanning empty library returns empty list"""
        tmpdir, designs_folder, library = setup_library
        designs = library.scan_designs()
        assert len(designs) == 0

    def test_scan_designs_with_files(self, setup_library):
        """Scanning library with files returns metadata list"""
        tmpdir, designs_folder, library = setup_library
        # Create test design files
        design1 = {
            "name": "Fighter A",
            "ship_class": "Fighter",
            "vehicle_type": "Fighter",
            "mass": 50.0,
            "layers": {}
        }
        design2 = {
            "name": "Cruiser B",
            "ship_class": "Cruiser",
            "vehicle_type": "Ship",
            "mass": 5000.0,
            "layers": {}
        }

        save_json(os.path.join(designs_folder, "fighter_a.json"), design1)
        save_json(os.path.join(designs_folder, "cruiser_b.json"), design2)

        designs = library.scan_designs()

        assert len(designs) == 2
        names = [d.name for d in designs]
        assert "Fighter A" in names
        assert "Cruiser B" in names

    def test_save_design_new(self, setup_library):
        """Can save a new design"""
        tmpdir, designs_folder, library = setup_library
        ship = MagicMock()
        ship.name = "Test Ship"
        ship.ship_class = "Escort"
        ship.vehicle_type = "Ship"
        ship.mass = 1000.0
        ship.theme_id = "Federation"
        ship.layers = {}
        ship.to_dict.return_value = {
            "name": "Test Ship",
            "ship_class": "Escort",
            "vehicle_type": "Ship",
            "mass": 1000.0,
            "layers": {}
        }

        success, message = library.save_design(ship, "Test Ship", set())

        assert success
        assert "Saved" in message
        # Check file was created
        assert os.path.exists(os.path.join(designs_folder, "Test_Ship.json"))

    def test_save_design_prevents_overwrite_built(self, setup_library):
        """Cannot overwrite a design that has been built"""
        tmpdir, designs_folder, library = setup_library
        ship = MagicMock()
        ship.name = "Built Ship"
        ship.ship_class = "Escort"
        ship.vehicle_type = "Ship"
        ship.mass = 1000.0
        ship.theme_id = "Federation"
        ship.layers = {}
        ship.to_dict.return_value = {
            "name": "Built Ship",
            "ship_class": "Escort",
            "layers": {}
        }

        # First save
        library.save_design(ship, "Built Ship", set())

        # Try to save again with design marked as built
        success, message = library.save_design(ship, "Built Ship", {"Built_Ship"})

        assert not success
        assert "built" in message.lower()

    def test_save_design_can_update_unbuilt(self, setup_library):
        """Can update a design that hasn't been built"""
        tmpdir, designs_folder, library = setup_library
        ship = MagicMock()
        ship.name = "Unbuilt Ship"
        ship.ship_class = "Escort"
        ship.vehicle_type = "Ship"
        ship.mass = 1000.0
        ship.theme_id = "Federation"
        ship.layers = {}
        ship.to_dict.return_value = {
            "name": "Unbuilt Ship",
            "ship_class": "Escort",
            "layers": {}
        }

        # First save
        library.save_design(ship, "Unbuilt Ship", set())

        # Update (not in built set)
        success, message = library.save_design(ship, "Unbuilt Ship", set())

        assert success

    def test_mark_obsolete(self, setup_library):
        """Can mark design as obsolete"""
        tmpdir, designs_folder, library = setup_library
        # Create design file
        design_data = {
            "name": "Old Design",
            "ship_class": "Escort",
            "layers": {},
            "_metadata": {"is_obsolete": False}
        }
        save_json(os.path.join(designs_folder, "old.json"), design_data)

        # Mark obsolete
        success, message = library.mark_obsolete("old", True)

        assert success

        # Verify file updated
        from game.core.json_utils import load_json_required
        updated = load_json_required(os.path.join(designs_folder, "old.json"))
        assert updated["_metadata"]["is_obsolete"]

    def test_filter_designs_by_class(self, setup_library):
        """Can filter designs by ship class"""
        tmpdir, designs_folder, library = setup_library
        # Create test designs
        for i, ship_class in enumerate(["Fighter", "Cruiser", "Fighter"]):
            design = {
                "name": f"Ship {i}",
                "ship_class": ship_class,
                "vehicle_type": "Ship",
                "mass": 1000.0,
                "layers": {}
            }
            save_json(os.path.join(designs_folder, f"ship_{i}.json"), design)

        # Filter for Fighters
        designs = library.filter_designs(ship_class="Fighter")

        assert len(designs) == 2
        for design in designs:
            assert design.ship_class == "Fighter"

    def test_filter_designs_by_vehicle_type(self, setup_library):
        """Can filter designs by vehicle type"""
        tmpdir, designs_folder, library = setup_library
        # Create mixed types
        types = ["Ship", "Fighter", "Satellite"]
        for i, vtype in enumerate(types):
            design = {
                "name": f"Vehicle {i}",
                "ship_class": "Escort",
                "vehicle_type": vtype,
                "mass": 1000.0,
                "layers": {}
            }
            save_json(os.path.join(designs_folder, f"vehicle_{i}.json"), design)

        # Filter for Fighters
        designs = library.filter_designs(vehicle_type="Fighter")

        assert len(designs) == 1
        assert designs[0].vehicle_type == "Fighter"

    def test_filter_designs_obsolete(self, setup_library):
        """Can filter out obsolete designs"""
        tmpdir, designs_folder, library = setup_library
        # Create designs with mixed obsolete status
        for i in range(3):
            design = {
                "name": f"Design {i}",
                "ship_class": "Escort",
                "vehicle_type": "Ship",
                "mass": 1000.0,
                "layers": {},
                "_metadata": {"is_obsolete": i == 1}  # Middle one obsolete
            }
            save_json(os.path.join(designs_folder, f"design_{i}.json"), design)

        # Filter without obsolete
        designs = library.filter_designs(show_obsolete=False)

        assert len(designs) == 2
        for design in designs:
            assert not design.is_obsolete

        # Include obsolete
        designs = library.filter_designs(show_obsolete=True)

        assert len(designs) == 3

    def test_search_designs_by_name(self, setup_library):
        """Can search designs by name"""
        tmpdir, designs_folder, library = setup_library
        # Create designs
        names = ["Alpha Fighter", "Beta Cruiser", "Alpha Destroyer"]
        for i, name in enumerate(names):
            design = {
                "name": name,
                "ship_class": "Escort",
                "vehicle_type": "Ship",
                "mass": 1000.0,
                "layers": {}
            }
            save_json(os.path.join(designs_folder, f"ship_{i}.json"), design)

        # Search for "Alpha"
        designs = library.search_designs("Alpha")

        assert len(designs) == 2
        for design in designs:
            assert "Alpha" in design.name

    def test_sanitize_design_id(self):
        """Design ID sanitization works correctly"""
        assert DesignLibrary._sanitize_design_id("Simple Name") == "Simple_Name"
        assert DesignLibrary._sanitize_design_id("Name!@#$%With^&*()Special") == "NameWithSpecial"
        assert DesignLibrary._sanitize_design_id("   Spaces   ") == "Spaces"
        assert DesignLibrary._sanitize_design_id("") == "unnamed_design"

    def test_design_exists(self, setup_library):
        """Can check if design exists"""
        tmpdir, designs_folder, library = setup_library
        # Create a design
        design = {
            "name": "Existing",
            "ship_class": "Escort",
            "layers": {}
        }
        save_json(os.path.join(designs_folder, "existing.json"), design)

        assert library.design_exists("existing")
        assert not library.design_exists("nonexistent")

    def test_increment_built_count(self, setup_library):
        """Can increment built count"""
        tmpdir, designs_folder, library = setup_library
        # Create design
        design = {
            "name": "Buildable",
            "ship_class": "Escort",
            "layers": {},
            "_metadata": {"times_built": 0}
        }
        save_json(os.path.join(designs_folder, "buildable.json"), design)

        # Increment
        success = library.increment_built_count("buildable")

        assert success

        # Verify
        from game.core.json_utils import load_json_required
        updated = load_json_required(os.path.join(designs_folder, "buildable.json"))
        assert updated["_metadata"]["times_built"] == 1


class TestDesignLibraryPerEmpire:
    """Tests for per-empire design folder structure"""

    @pytest.fixture(autouse=True)
    def setup_tmpdir(self):
        """Create temporary directory for test designs"""
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        shutil.rmtree(tmpdir)

    def test_design_library_uses_empire_subfolder(self, setup_tmpdir):
        """DesignLibrary stores designs in empire_N subfolder"""
        tmpdir = setup_tmpdir
        # Create library for empire 0
        library = DesignLibrary(tmpdir, empire_id=0)

        # Designs folder should include empire_0
        assert "empire_0" in library.designs_folder
        assert library.designs_folder.endswith(os.path.join("designs", "empire_0"))

    def test_design_library_isolates_empires(self, setup_tmpdir):
        """Empire 0 designs not visible to Empire 1 library"""
        tmpdir = setup_tmpdir
        # Create per-empire design folders
        designs_base = os.path.join(tmpdir, "designs")
        empire0_folder = os.path.join(designs_base, "empire_0")
        empire1_folder = os.path.join(designs_base, "empire_1")
        os.makedirs(empire0_folder)
        os.makedirs(empire1_folder)

        # Create design in empire 0's folder
        design = {
            "name": "Empire0 Ship",
            "ship_class": "Escort",
            "vehicle_type": "Ship",
            "mass": 1000.0,
            "layers": {}
        }
        save_json(os.path.join(empire0_folder, "e0_ship.json"), design)

        # Create libraries for each empire
        lib0 = DesignLibrary(tmpdir, empire_id=0)
        lib1 = DesignLibrary(tmpdir, empire_id=1)

        # Empire 0 should see the design
        designs0 = lib0.scan_designs()
        assert len(designs0) == 1
        assert designs0[0].name == "Empire0 Ship"

        # Empire 1 should NOT see it
        designs1 = lib1.scan_designs()
        assert len(designs1) == 0

    def test_design_library_creates_empire_folder(self, setup_tmpdir):
        """DesignLibrary creates empire folder if missing"""
        tmpdir = setup_tmpdir
        # Don't pre-create any folders
        library = DesignLibrary(tmpdir, empire_id=2)

        # Empire folder should exist now
        expected_path = os.path.join(tmpdir, "designs", "empire_2")
        assert os.path.exists(expected_path)
        assert library.designs_folder == expected_path

    def test_design_library_saves_to_empire_folder(self, setup_tmpdir):
        """Saving design goes to correct empire folder"""
        tmpdir = setup_tmpdir
        library = DesignLibrary(tmpdir, empire_id=1)

        # Create mock ship
        ship = MagicMock()
        ship.name = "Test Ship"
        ship.ship_class = "Escort"
        ship.vehicle_type = "Ship"
        ship.mass = 1000.0
        ship.theme_id = "Federation"
        ship.layers = {}
        ship.to_dict.return_value = {
            "name": "Test Ship",
            "ship_class": "Escort",
            "vehicle_type": "Ship",
            "mass": 1000.0,
            "layers": {}
        }

        # Save design
        success, message = library.save_design(ship, "Test Ship", set())

        assert success

        # Verify file is in empire_1 folder
        expected_file = os.path.join(tmpdir, "designs", "empire_1", "Test_Ship.json")
        assert os.path.exists(expected_file)


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
        import logging
        import tempfile

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
        import logging
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
        import logging
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
        import logging
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
        import logging
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
        import logging
        import json
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
