import pytest
import math

from game.simulation.entities.ship import Ship
from game.simulation.entities.ship_loader import initialize_ship_data
from game.simulation.components import Component, LayerType, load_components
from game.core.registry import RegistryManager
from tests.fixtures.paths import get_project_root, get_data_dir


@pytest.fixture
def ship_data():
    """Initialize ship data and load components, clean up registry after test."""
    initialize_ship_data(str(get_project_root()))
    load_components(str(get_data_dir() / "components.json"))
    yield
    RegistryManager.instance().clear()


class TestDynamicLayers:

    def test_fighter_layers(self, ship_data):
        """Fighter (Small) should have CORE and ARMOR only."""
        ship = Ship("Test Fighter", 0, 0, (255, 0, 0), ship_class="Fighter (Small)")

        assert LayerType.CORE in ship.layers
        assert LayerType.ARMOR in ship.layers
        # Should NOT have OUTER or INNER
        assert LayerType.OUTER not in ship.layers
        assert LayerType.INNER not in ship.layers

        # Check radii
        assert ship.layers[LayerType.CORE]['radius_pct'] == pytest.approx(0.877, abs=0.001)
        assert ship.layers[LayerType.ARMOR]['radius_pct'] == 1.0

    def test_satellite_layers(self, ship_data):
        """Satellite (Small) should have CORE, OUTER, ARMOR."""
        ship = Ship("Test Satellite", 0, 0, (255, 0, 0), ship_class="Satellite (Small)")

        assert LayerType.CORE in ship.layers
        assert LayerType.OUTER in ship.layers
        assert LayerType.ARMOR in ship.layers
        assert LayerType.INNER not in ship.layers

    def test_cruiser_layers(self, ship_data):
        """Cruiser should have all 4 layers."""
        ship = Ship("Test Cruiser", 0, 0, (255, 0, 0), ship_class="Cruiser")

        assert LayerType.CORE in ship.layers
        assert LayerType.INNER in ship.layers
        assert LayerType.OUTER in ship.layers
        assert LayerType.ARMOR in ship.layers

    def test_restriction_logic(self, ship_data):
        """Test that layer restrictions block components correctly."""
        # To test restrictions, we need a ship class that HAS a restriction.
        # But our current vehicleclasses.json doesn't have any explicit restriction strings added yet.
        # So we will mock one for this test instance.

        ship = Ship("Restricted Ship", 0, 0, (255, 0, 0), ship_class="Escort")
        # Add a fake restriction to OUTER layer
        ship.layers[LayerType.OUTER]['restrictions'].append("block_classification:Weapons")
        # Clear restrictions on CORE to ensure test isolation (since Escort now has default blocks)
        ship.layers[LayerType.CORE]['restrictions'] = []

        # Create a mock Weapon component
        # We can simulate a component nicely
        weapon_data = {
            "id": "test_weapon",
            "name": "Test Weapon",
            "type": "Weapon",
            "mass": 10, "hp": 10,
            # allowed_layers removed
            "allowed_vehicle_types": ["Ship"],
            "major_classification": "Weapons"
        }
        weapon = Component(weapon_data)

        # Try to add to OUTER (should fail)
        success = ship.add_component(weapon, LayerType.OUTER)
        assert not success, "Should satisfy block_classification:Weapons restriction"

        # Try to add to CORE (should succeed if allowed)
        success = ship.add_component(weapon, LayerType.CORE)
        assert success, "Should allow in non-restricted layer"
