"""
Tests for SimulationDesignLoader - loads ship designs from design library files.

This module handles Ship instantiation from design files, which belongs in the
simulation layer (not strategy layer) because it creates simulation entities.

Part of PROJ-30: Strategy Mode Layer Boundary Cleanup (STRAT-01 fix).
"""
import pytest
import tempfile
import shutil
import os
from unittest.mock import MagicMock, patch

from game.core.json_utils import save_json
from game.core.registry import RegistryManager
from game.simulation.components.component import load_components, load_modifiers
from game.simulation.entities.ship_loader import load_vehicle_classes
from tests.fixtures.paths import get_data_dir


class TestSimulationDesignLoader:
    """Tests for SimulationDesignLoader class."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Set up test environment with components and vehicle classes loaded."""
        data_dir = get_data_dir()
        load_components(str(data_dir / "components.json"))
        load_modifiers(str(data_dir / "modifiers.json"))
        load_vehicle_classes(str(data_dir / "vehicleclasses.json"))

        # Create temp directory for design files
        self.tmpdir = tempfile.mkdtemp()

        yield

        shutil.rmtree(self.tmpdir)
        RegistryManager.instance().clear()

    def test_load_ship_from_design_data_returns_ship(self, fresh_registries):
        """load_ship_from_design_data creates Ship from dict data."""
        from game.simulation.services.design_loader import SimulationDesignLoader

        design_data = {
            "name": "Test Fighter",
            "ship_class": "Fighter",
            "vehicle_type": "Fighter",
            "mass": 50.0,
            "layers": {}
        }

        loader = SimulationDesignLoader(registries=fresh_registries)
        ship = loader.load_ship_from_design_data(design_data)

        assert ship is not None
        assert ship.name == "Test Fighter"

    def test_load_ship_from_design_data_positions_at_center(self, fresh_registries):
        """load_ship_from_design_data positions ship at specified center."""
        from game.simulation.services.design_loader import SimulationDesignLoader

        design_data = {
            "name": "Centered Ship",
            "ship_class": "Fighter",
            "vehicle_type": "Fighter",
            "mass": 50.0,
            "layers": {}
        }

        loader = SimulationDesignLoader(registries=fresh_registries)
        ship = loader.load_ship_from_design_data(
            design_data,
            center_x=1920 // 2,
            center_y=1080 // 2
        )

        assert ship.position.x == 960
        assert ship.position.y == 540

    def test_load_ship_from_design_data_recalculates_stats(self, fresh_registries):
        """load_ship_from_design_data calls recalculate_stats on ship."""
        from game.simulation.services.design_loader import SimulationDesignLoader

        design_data = {
            "name": "Stats Ship",
            "ship_class": "Fighter",
            "vehicle_type": "Fighter",
            "mass": 50.0,
            "layers": {}
        }

        loader = SimulationDesignLoader(registries=fresh_registries)

        # Patch Ship.from_dict to return a mock we can verify
        with patch('game.simulation.services.design_loader.Ship') as MockShip:
            mock_ship = MagicMock()
            MockShip.from_dict.return_value = mock_ship

            loader.load_ship_from_design_data(design_data)

            mock_ship.recalculate_stats.assert_called_once()

    def test_load_ship_from_file_success(self, fresh_registries):
        """load_ship_from_file loads from file path."""
        from game.simulation.services.design_loader import SimulationDesignLoader

        # Create design file
        design_data = {
            "name": "File Ship",
            "ship_class": "Fighter",
            "vehicle_type": "Fighter",
            "mass": 50.0,
            "layers": {}
        }
        filepath = os.path.join(self.tmpdir, "file_ship.json")
        save_json(filepath, design_data)

        loader = SimulationDesignLoader(registries=fresh_registries)
        ship, message = loader.load_ship_from_file(filepath)

        assert ship is not None
        assert ship.name == "File Ship"
        assert "Loaded" in message

    def test_load_ship_from_file_not_found(self, fresh_registries):
        """load_ship_from_file returns None for missing file."""
        from game.simulation.services.design_loader import SimulationDesignLoader

        loader = SimulationDesignLoader(registries=fresh_registries)
        filepath = os.path.join(self.tmpdir, "nonexistent.json")
        ship, message = loader.load_ship_from_file(filepath)

        assert ship is None
        assert "not found" in message.lower()

    def test_load_ship_from_file_invalid_json(self, fresh_registries):
        """load_ship_from_file returns None for invalid JSON."""
        from game.simulation.services.design_loader import SimulationDesignLoader

        # Create invalid JSON file
        filepath = os.path.join(self.tmpdir, "invalid.json")
        with open(filepath, "w") as f:
            f.write("{ not valid json }")

        loader = SimulationDesignLoader(registries=fresh_registries)
        ship, message = loader.load_ship_from_file(filepath)

        assert ship is None
        assert "Failed" in message or "failed" in message.lower()

    def test_load_ship_from_file_with_screen_dimensions(self, fresh_registries):
        """load_ship_from_file accepts width/height for positioning."""
        from game.simulation.services.design_loader import SimulationDesignLoader

        design_data = {
            "name": "Positioned Ship",
            "ship_class": "Fighter",
            "vehicle_type": "Fighter",
            "mass": 50.0,
            "layers": {}
        }
        filepath = os.path.join(self.tmpdir, "positioned.json")
        save_json(filepath, design_data)

        loader = SimulationDesignLoader(registries=fresh_registries)
        ship, message = loader.load_ship_from_file(filepath, width=800, height=600)

        assert ship is not None
        assert ship.position.x == 400  # 800 // 2
        assert ship.position.y == 300  # 600 // 2


class TestSimulationDesignLoaderIntegration:
    """Integration tests for SimulationDesignLoader with real components."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Set up test environment with components loaded."""
        data_dir = get_data_dir()
        load_components(str(data_dir / "components.json"))
        load_modifiers(str(data_dir / "modifiers.json"))
        load_vehicle_classes(str(data_dir / "vehicleclasses.json"))

        self.tmpdir = tempfile.mkdtemp()

        yield

        shutil.rmtree(self.tmpdir)
        RegistryManager.instance().clear()

    def test_loaded_ship_has_correct_stats(self, fresh_registries):
        """Loaded ship has stats calculated correctly."""
        from game.simulation.services.design_loader import SimulationDesignLoader
        from game.simulation.components.component import create_component
        from game.simulation.components.component_constants import LayerType
        from game.simulation.entities.ship import Ship

        # Build a ship with known components
        test_ship = Ship("Test Cruiser", 0, 0, (100, 100, 100), ship_class="Cruiser", registries=fresh_registries)
        test_ship.add_component(create_component("bridge", registries=fresh_registries), LayerType.CORE)
        test_ship.add_component(create_component("standard_engine", registries=fresh_registries), LayerType.INNER)
        test_ship.recalculate_stats()

        # Save it
        ship_data = test_ship.to_dict()
        filepath = os.path.join(self.tmpdir, "test_cruiser.json")
        save_json(filepath, ship_data)

        # Load it back
        loader = SimulationDesignLoader(registries=fresh_registries)
        loaded_ship, message = loader.load_ship_from_file(filepath)

        assert loaded_ship is not None
        # Stats should match original after recalculation
        assert loaded_ship.max_hp == test_ship.max_hp
