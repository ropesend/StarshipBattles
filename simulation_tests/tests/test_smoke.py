"""Smoke test to verify simulation test infrastructure."""
import pytest
import os

from game.simulation.entities.ship import Ship
from game.simulation.components.component import create_component
from game.core.registry import get_default_registry_provider, get_default_registries


@pytest.mark.simulation
class TestSimulationInfrastructure:
    """Verify test infrastructure is working."""
    
    @pytest.fixture(autouse=True)
    def setup(self, isolated_registry):
        """Use isolated registry for all tests in this class."""
        pass
    
    def test_vehicle_classes_loaded(self):
        """Verify test vehicle classes are loaded."""
        classes = get_default_registry_provider().get_vehicle_classes()
        vc = classes.get('TestS_2L')
        assert vc is not None
        assert vc['max_mass'] == 2000
    
    def test_components_loaded(self):
        """Verify test components are loaded."""
        registries = get_default_registries()
        comp = create_component('test_engine_std', registries=registries)
        assert comp is not None
        assert comp.mass == 0

    def test_ship_creation(self, ships_dir):
        """Verify ship can be created from test data."""
        import json
        ship_path = os.path.join(ships_dir, 'Test_Engine_1x_LowMass.json')

        with open(ship_path, 'r') as f:
            ship_data = json.load(f)

        registries = get_default_registries()
        ship = Ship.from_dict(ship_data, registries=registries)
        ship.recalculate_stats()
        
        assert ship is not None
        assert ship.ship_class == 'TestS_2L'
