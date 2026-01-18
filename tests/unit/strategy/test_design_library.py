"""
Tests for DesignLibrary
"""
import unittest
import tempfile
import os
from unittest.mock import MagicMock, patch
from game.strategy.systems.design_library import DesignLibrary
from game.core.json_utils import save_json


class TestDesignLibrary(unittest.TestCase):
    """Tests for DesignLibrary class"""

    def setUp(self):
        """Create temporary directory for test designs"""
        self.tmpdir = tempfile.mkdtemp()
        self.designs_folder = os.path.join(self.tmpdir, "designs")
        os.makedirs(self.designs_folder)

        self.library = DesignLibrary(self.tmpdir, empire_id=1)

    def tearDown(self):
        """Clean up temporary directory"""
        import shutil
        shutil.rmtree(self.tmpdir)

    def test_initialization_creates_folder(self):
        """Initialization creates designs folder if missing"""
        new_tmpdir = tempfile.mkdtemp()
        try:
            library = DesignLibrary(new_tmpdir, empire_id=1)
            self.assertTrue(os.path.exists(library.designs_folder))
        finally:
            import shutil
            shutil.rmtree(new_tmpdir)

    def test_scan_designs_empty(self):
        """Scanning empty library returns empty list"""
        designs = self.library.scan_designs()
        self.assertEqual(len(designs), 0)

    def test_scan_designs_with_files(self):
        """Scanning library with files returns metadata list"""
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

        save_json(os.path.join(self.designs_folder, "fighter_a.json"), design1)
        save_json(os.path.join(self.designs_folder, "cruiser_b.json"), design2)

        designs = self.library.scan_designs()

        self.assertEqual(len(designs), 2)
        names = [d.name for d in designs]
        self.assertIn("Fighter A", names)
        self.assertIn("Cruiser B", names)

    def test_save_design_new(self):
        """Can save a new design"""
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

        success, message = self.library.save_design(ship, "Test Ship", set())

        self.assertTrue(success)
        self.assertIn("Saved", message)
        # Check file was created
        self.assertTrue(os.path.exists(os.path.join(self.designs_folder, "Test_Ship.json")))

    def test_save_design_prevents_overwrite_built(self):
        """Cannot overwrite a design that has been built"""
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
        self.library.save_design(ship, "Built Ship", set())

        # Try to save again with design marked as built
        success, message = self.library.save_design(ship, "Built Ship", {"Built_Ship"})

        self.assertFalse(success)
        self.assertIn("built", message.lower())

    def test_save_design_can_update_unbuilt(self):
        """Can update a design that hasn't been built"""
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
        self.library.save_design(ship, "Unbuilt Ship", set())

        # Update (not in built set)
        success, message = self.library.save_design(ship, "Unbuilt Ship", set())

        self.assertTrue(success)

    def test_load_design(self):
        """Can load a design by ID"""
        # Create design file
        design_data = {
            "name": "Loadable Ship",
            "ship_class": "Frigate",
            "vehicle_type": "Ship",
            "mass": 2000.0,
            "layers": {}
        }
        save_json(os.path.join(self.designs_folder, "loadable.json"), design_data)

        # Mock Ship.from_dict
        with patch('game.strategy.systems.design_library.Ship') as MockShip:
            mock_ship = MagicMock()
            mock_ship.name = "Loadable Ship"
            MockShip.from_dict.return_value = mock_ship

            ship, message = self.library.load_design("loadable", 1920, 1080)

            self.assertIsNotNone(ship)
            self.assertIn("Loaded", message)
            MockShip.from_dict.assert_called_once()

    def test_load_design_not_found(self):
        """Loading nonexistent design returns None"""
        ship, message = self.library.load_design("nonexistent", 1920, 1080)

        self.assertIsNone(ship)
        self.assertIn("not found", message.lower())

    def test_mark_obsolete(self):
        """Can mark design as obsolete"""
        # Create design file
        design_data = {
            "name": "Old Design",
            "ship_class": "Escort",
            "layers": {},
            "_metadata": {"is_obsolete": False}
        }
        save_json(os.path.join(self.designs_folder, "old.json"), design_data)

        # Mark obsolete
        success, message = self.library.mark_obsolete("old", True)

        self.assertTrue(success)

        # Verify file updated
        from game.core.json_utils import load_json_required
        updated = load_json_required(os.path.join(self.designs_folder, "old.json"))
        self.assertTrue(updated["_metadata"]["is_obsolete"])

    def test_filter_designs_by_class(self):
        """Can filter designs by ship class"""
        # Create test designs
        for i, ship_class in enumerate(["Fighter", "Cruiser", "Fighter"]):
            design = {
                "name": f"Ship {i}",
                "ship_class": ship_class,
                "vehicle_type": "Ship",
                "mass": 1000.0,
                "layers": {}
            }
            save_json(os.path.join(self.designs_folder, f"ship_{i}.json"), design)

        # Filter for Fighters
        designs = self.library.filter_designs(ship_class="Fighter")

        self.assertEqual(len(designs), 2)
        for design in designs:
            self.assertEqual(design.ship_class, "Fighter")

    def test_filter_designs_by_vehicle_type(self):
        """Can filter designs by vehicle type"""
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
            save_json(os.path.join(self.designs_folder, f"vehicle_{i}.json"), design)

        # Filter for Fighters
        designs = self.library.filter_designs(vehicle_type="Fighter")

        self.assertEqual(len(designs), 1)
        self.assertEqual(designs[0].vehicle_type, "Fighter")

    def test_filter_designs_obsolete(self):
        """Can filter out obsolete designs"""
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
            save_json(os.path.join(self.designs_folder, f"design_{i}.json"), design)

        # Filter without obsolete
        designs = self.library.filter_designs(show_obsolete=False)

        self.assertEqual(len(designs), 2)
        for design in designs:
            self.assertFalse(design.is_obsolete)

        # Include obsolete
        designs = self.library.filter_designs(show_obsolete=True)

        self.assertEqual(len(designs), 3)

    def test_search_designs_by_name(self):
        """Can search designs by name"""
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
            save_json(os.path.join(self.designs_folder, f"ship_{i}.json"), design)

        # Search for "Alpha"
        designs = self.library.search_designs("Alpha")

        self.assertEqual(len(designs), 2)
        for design in designs:
            self.assertIn("Alpha", design.name)

    def test_sanitize_design_id(self):
        """Design ID sanitization works correctly"""
        self.assertEqual(
            DesignLibrary._sanitize_design_id("Simple Name"),
            "Simple_Name"
        )
        self.assertEqual(
            DesignLibrary._sanitize_design_id("Name!@#$%With^&*()Special"),
            "NameWithSpecial"
        )
        self.assertEqual(
            DesignLibrary._sanitize_design_id("   Spaces   "),
            "Spaces"
        )
        self.assertEqual(
            DesignLibrary._sanitize_design_id(""),
            "unnamed_design"
        )

    def test_design_exists(self):
        """Can check if design exists"""
        # Create a design
        design = {
            "name": "Existing",
            "ship_class": "Escort",
            "layers": {}
        }
        save_json(os.path.join(self.designs_folder, "existing.json"), design)

        self.assertTrue(self.library.design_exists("existing"))
        self.assertFalse(self.library.design_exists("nonexistent"))

    def test_increment_built_count(self):
        """Can increment built count"""
        # Create design
        design = {
            "name": "Buildable",
            "ship_class": "Escort",
            "layers": {},
            "_metadata": {"times_built": 0}
        }
        save_json(os.path.join(self.designs_folder, "buildable.json"), design)

        # Increment
        success = self.library.increment_built_count("buildable")

        self.assertTrue(success)

        # Verify
        from game.core.json_utils import load_json_required
        updated = load_json_required(os.path.join(self.designs_folder, "buildable.json"))
        self.assertEqual(updated["_metadata"]["times_built"], 1)


if __name__ == '__main__':
    unittest.main()
