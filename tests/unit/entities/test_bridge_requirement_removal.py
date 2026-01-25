import pytest
from unittest.mock import MagicMock, patch
import json

from game.simulation.ship_validator import ShipDesignValidator, ValidationResult
from game.simulation.entities.ship import Ship, LayerType
from game.core.registry import RegistryManager
from game.simulation.components import Component
from tests.fixtures.paths import get_unit_test_data_dir


@pytest.fixture
def validator_with_test_data():
    """Load test vehicle classes and set up validator."""
    test_data_path = str(get_unit_test_data_dir() / "test_vehicleclasses.json")
    with open(test_data_path, "r") as f:
        vehicle_data = json.load(f)["classes"]

    # Mock global vehicle_classes with our test data for the scope of this test
    classes = RegistryManager.instance().vehicle_classes
    original_vehicle_classes = classes.copy()
    classes.clear()
    classes.update(vehicle_data)

    validator = ShipDesignValidator()

    yield validator

    # Restore global vehicle_classes
    classes.clear()
    classes.update(original_vehicle_classes)


class TestBridgeRequirementRemoval:
    def test_valid_class_without_bridge(self, validator_with_test_data):
        """Test that a class defined without bridge requirement is valid without one."""
        # 'TestClass' in test_vehicleclasses.json has logic that implies NO requirements
        # (It actually has no "requirements" field in the json provided in the prompt)

        validator = validator_with_test_data

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
        result = validator.validate_design(ship)

        # Check that we DO NOT have "Ship needs a Bridge!" error
        error_messages = result.errors
        assert not any("Ship needs a Bridge!" in err for err in error_messages), \
            f"Validation failed with bridge error: {error_messages}"
