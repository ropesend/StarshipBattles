"""
Reproduction test for BUG-12: Component Addition to Hull Layer.

PROJ-50: Updated to use fresh_registries for DI.
"""
import pytest
import pygame
from game.simulation.entities.ship import Ship, LayerType
from game.simulation.entities.ship_loader import initialize_ship_data
from game.simulation.components.component import load_components, create_component
from game.core.registry import RegistryManager
from tests.fixtures.paths import get_project_root
from game.simulation.entities.layer_data import LayerData


class TestBug12HullAddition:
    """Reproduction test for BUG-12: Component Addition to Hull Layer.

    PROJ-50: Updated to use fresh_registries for DI.
    """

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        """Setup test with DI registries. PROJ-50."""
        pygame.init()
        self.registries = fresh_registries
        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort", registries=fresh_registries)
        yield ship
        pygame.quit()

    def test_prevent_non_hull_addition_to_hull_layer(self, setup):
        """Verify that non-hull components cannot be added to the HULL layer. PROJ-50: Uses DI."""
        ship = setup
        # 'armor_plate' is definitely not a hull component
        comp = create_component('armor_plate', registries=self.registries)
        assert comp is not None

        # This SHOULD return False and not add the component
        res = ship.add_component(comp, LayerType.HULL)

        assert res is False, "Should NOT be able to add armor_plate to HULL layer"
        assert comp not in ship.layers[LayerType.HULL].components, \
            "Component should not be present in HULL layer list"

    def test_prevent_any_addition_to_hull_layer_in_builder(self, setup):
        """Verify that even 'bridge' or 'engine' cannot be added to HULL layer. PROJ-50: Uses DI."""
        ship = setup
        for comp_id in ['bridge', 'standard_engine']:
            comp = create_component(comp_id, registries=self.registries)
            res = ship.add_component(comp, LayerType.HULL)
            assert res is False, f"Should NOT be able to add {comp_id} to HULL layer"
            assert comp not in ship.layers[LayerType.HULL].components
