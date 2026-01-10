import unittest
from unittest.mock import MagicMock, patch
import json
import os

from game.simulation.ship_validator import ShipDesignValidator, ValidationResult
from game.simulation.entities.ship import Ship, LayerType
from game.core.registry import RegistryManager
from game.simulation.components.component import Component

class TestBridgeRequirementRemoval(unittest.TestCase):
    def setUp(self):
        # Load the test vehicle classes data
        self.test_data_path = os.path.join("tests", "unit", "data", "test_vehicleclasses.json")
        with open(self.test_data_path, "r") as f:
            self.vehicle_data = json.load(f)["classes"]
            
        # Mock global vehicle_classes with our test data for the scope of this test
        classes = RegistryManager.instance().vehicle_classes
        self.original_vehicle_classes = classes.copy()
        classes.clear()
        classes.update(self.vehicle_data)
        
        self.validator = ShipDesignValidator()

    def tearDown(self):
        # Restore global vehicle_classes
        classes = RegistryManager.instance().vehicle_classes
        classes.clear()
        classes.update(self.original_vehicle_classes)

    def test_valid_class_without_bridge(self):
        """Test that a class defined without bridge requirement is valid without one."""
        # 'TestClass' in test_vehicleclasses.json has logic that implies NO requirements
        # (It actually has no "requirements" field in the json provided in the prompt)
        
        ship = MagicMock(spec=Ship)
        ship.ship_class = "TestClass"
        ship.vehicle_type = "Ship"
        ship.layers = {
            LayerType.CORE: {'components': []},
            LayerType.INNER: {'components': []},
            LayerType.OUTER: {'components': []}
        }
        # Mocking values for MassBudgetRule to pass
        ship.current_mass = 100 
        ship.max_mass_budget = 5000
        
        # Validate design
        result = self.validator.validate_design(ship)
        
        # Check that we DO NOT have "Ship needs a Bridge!" error
        error_messages = result.errors
        self.assertFalse(any("Ship needs a Bridge!" in err for err in error_messages), 
                         f"Validation failed with bridge error: {error_messages}")
                        
if __name__ == '__main__':
    unittest.main()
