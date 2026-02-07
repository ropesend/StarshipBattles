"""
Reproduction test for BUG-08: Fuel validation issues.

PROJ-50: Updated to use fresh_registries for DI.
"""
import pygame
import pytest

from game.simulation.entities.ship import Ship, LayerType
from game.simulation.entities.ship_loader import load_vehicle_classes
from game.core.registry import RegistryManager
from game.simulation.components.component import load_components, create_component


class TestBug08FuelValidation:
    """PROJ-50: Updated to use fresh_registries for DI."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup pygame for test."""
        if not pygame.get_init():
            pygame.init()

    def test_class_requirements_fuel_storage_failure(self, fresh_registries):
        """
        Validation test: Verify ResourceStorage ability is correctly aggregated.

        Note: Post-Phase 5, 'requirements' has been removed from vehicleclasses.json.
        This test verifies the ability aggregation mechanism works correctly.
        Fuel tanks use 'ResourceStorage' ability, not 'FuelStorage'.

        PROJ-50: Updated to use DI via fresh_registries fixture.
        """
        # Create a Cruiser (has enough mass budget for fuel tank)
        ship = Ship("Test Cruiser", 0, 0, (255, 255, 255), ship_class="Cruiser", registries=fresh_registries)

        # Add Fuel Tank (provides 'ResourceStorage' ability for 'fuel')
        tank = create_component("fuel_tank", registries=fresh_registries)
        assert tank is not None, "Failed to create 'fuel_tank'"

        # Use INNER layer which is appropriate for fuel tanks
        success = ship.add_component(tank, LayerType.INNER)
        assert success, "Failed to add fuel tank to ship"

        # Force Recalculate
        ship.recalculate_stats()

        # Verify ResourceStorage ability is correctly aggregated
        # Check the resource registry for max fuel
        fuel_max = ship.resources.get_max_value('fuel')
        print(f"Max Fuel: {fuel_max}")

        # Fuel tank should provide fuel storage
        assert fuel_max > 0, "Fuel tank should provide fuel storage"

        # Validation should work without errors
        missing = ship.get_missing_requirements()
        print(f"Missing Requirements: {missing}")
        assert isinstance(missing, list)
