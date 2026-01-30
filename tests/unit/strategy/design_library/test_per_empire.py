"""
Tests for per-empire design folder structure.
"""

import pytest
import tempfile
import shutil
import os
from unittest.mock import MagicMock
from game.strategy.systems.design_library import DesignLibrary
from game.core.json_utils import save_json


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
