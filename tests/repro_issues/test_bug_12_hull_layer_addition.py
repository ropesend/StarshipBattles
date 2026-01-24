import pytest
import pygame
from game.simulation.entities.ship import Ship, initialize_ship_data, LayerType
from game.simulation.components.component import load_components, create_component
from game.core.registry import RegistryManager
from game.core.constants import COMPONENTS_FILE
from tests.fixtures.paths import get_project_root


class TestBug12HullAddition:
    """Reproduction test for BUG-12: Component Addition to Hull Layer."""

    @pytest.fixture(autouse=True)
    def setup(self):
        pygame.init()
        # Set up registry and data
        initialize_ship_data(str(get_project_root()))
        load_components(COMPONENTS_FILE)
        ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort")
        yield ship
        pygame.quit()
        RegistryManager.instance().clear()

    def test_prevent_non_hull_addition_to_hull_layer(self, setup):
        """Verify that non-hull components cannot be added to the HULL layer."""
        ship = setup
        # 'armor_plate' is definitely not a hull component
        comp = create_component('armor_plate')
        assert comp is not None

        # This SHOULD return False and not add the component
        res = ship.add_component(comp, LayerType.HULL)

        assert res is False, "Should NOT be able to add armor_plate to HULL layer"
        assert comp not in ship.layers[LayerType.HULL]['components'], \
            "Component should not be present in HULL layer list"

    def test_prevent_any_addition_to_hull_layer_in_builder(self, setup):
        """Verify that even 'bridge' or 'engine' cannot be added to HULL layer."""
        ship = setup
        for comp_id in ['bridge', 'standard_engine']:
            comp = create_component(comp_id)
            res = ship.add_component(comp, LayerType.HULL)
            assert res is False, f"Should NOT be able to add {comp_id} to HULL layer"
            assert comp not in ship.layers[LayerType.HULL]['components']
