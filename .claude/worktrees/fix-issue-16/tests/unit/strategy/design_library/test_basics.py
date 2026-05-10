"""
Tests for DesignLibrary basic operations.
"""

import pytest
import tempfile
import shutil
import os
from unittest.mock import MagicMock
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

        assert success, f"Save failed: {message}"
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
        success, message = library.save_design(ship, "Built Ship", {"built_ship"})

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

        assert success, f"Update failed: {message}"

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

        assert success, f"Mark obsolete failed: {message}"

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
        assert DesignLibrary._sanitize_design_id("Simple Name") == "simple_name"
        assert DesignLibrary._sanitize_design_id("Name!@#$%With^&*()Special") == "namewithspecial"
        assert DesignLibrary._sanitize_design_id("   Spaces   ") == "spaces"
        assert DesignLibrary._sanitize_design_id("") == "unnamed_design"

    def test_has_design(self, setup_library):
        """Can check if design exists"""
        tmpdir, designs_folder, library = setup_library
        # Create a design
        design = {
            "name": "Existing",
            "ship_class": "Escort",
            "layers": {}
        }
        save_json(os.path.join(designs_folder, "existing.json"), design)

        assert library.has_design("existing")
        assert not library.has_design("nonexistent")

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

        assert success, "Increment built count failed"

        # Verify
        from game.core.json_utils import load_json_required
        updated = load_json_required(os.path.join(designs_folder, "buildable.json"))
        assert updated["_metadata"]["times_built"] == 1
