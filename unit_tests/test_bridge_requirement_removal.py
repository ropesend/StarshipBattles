
import unittest
from unittest.mock import MagicMock, patch
import json
import os
import sys

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import necessary classes
from ship_validator import ShipDesignValidator, ValidationResult
from ship import Ship, VEHICLE_CLASSES, LayerType
from components import Component

class TestBridgeRequirementRemoval(unittest.TestCase):
    def setUp(self):
        # Load the test vehicle classes data
        self.test_data_path = os.path.join("unit_tests", "data", "test_vehicleclasses.json")
        with open(self.test_data_path, "r") as f:
            self.vehicle_data = json.load(f)["classes"]
            
        # Mock global VEHICLE_CLASSES with our test data for the scope of this test
        self.original_vehicle_classes = VEHICLE_CLASSES.copy()
        VEHICLE_CLASSES.clear()
        VEHICLE_CLASSES.update(self.vehicle_data)
        
        self.validator = ShipDesignValidator()

    def tearDown(self):
        # Restore global VEHICLE_CLASSES
        VEHICLE_CLASSES.clear()
        VEHICLE_CLASSES.update(self.original_vehicle_classes)

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
        
    def test_class_with_command_requirement(self):
        """Test that a class WITH command requirement still fails if no bridge/command provider."""
        # We need to simulate a class that DOES require command
        # Let's inject one into the mock data
        VEHICLE_CLASSES["CommandShip"] = {
            "requirements": {
                "command": {
                    "ability": "CommandAndControl",
                    "min_value": True
                }
            }
        }
        
        ship = MagicMock(spec=Ship)
        ship.ship_class = "CommandShip"
        ship.layers = {LayerType.CORE: {'components': []}}
        ship.current_mass = 100
        ship.max_mass_budget = 1000
        
        result = self.validator.validate_design(ship)
        
        # This SHOULD fail because of ClassRequirementsRule, but NOT BridgeExistenceRule
        # The error message from ClassRequirementsRule is "Needs Command And Control"
        self.assertTrue(any("Needs Command And Control" in err for err in result.errors),
                        f"Expected 'Needs Command And Control' error, got: {result.errors}")
                        
if __name__ == '__main__':
    unittest.main()
