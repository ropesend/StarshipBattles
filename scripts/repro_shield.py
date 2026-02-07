import pytest
import pygame

from game.simulation.entities.ship import Ship
from game.simulation.entities.ship_loader import initialize_ship_data
from game.simulation.components.component import load_components, create_component
from game.core.constants import LayerType
from game.simulation.entities.ship_stats import ShipStatsCalculator
from game.core.registry import RegistryManager
from game.core.paths import Paths
from tests.fixtures.paths import get_project_root


@pytest.fixture
def ship_with_bridge():
    """Set up pygame and create a ship with bridge for testing."""
    pygame.init()
    # Ensure clean state
    RegistryManager.instance().clear()

    initialize_ship_data(str(get_project_root()))
    load_components(Paths.COMPONENTS_FILE)
    ship = Ship("ShieldRepro", 0, 0, (255, 255, 255), ship_class="Cruiser")
    ship.add_component(create_component('bridge'), LayerType.CORE)
    calculator = ShipStatsCalculator(RegistryManager.instance().vehicle_classes)

    yield ship, calculator

    pygame.quit()
    RegistryManager.instance().clear()


class TestShieldRepro:

    def test_shield_regen_cost(self, ship_with_bridge):
        ship, calculator = ship_with_bridge

        # 1. create ShieldRegen
        regen = create_component('shield_regen')
        # Expect 2.0 from json
        # ability_instances should have ResourceConsumption
        cons = regen.get_ability('ResourceConsumption')
        val = cons.amount if cons else 'MISSING'
        print(f"DEBUG: Initial Energy Cost: {val}")

        ship.add_component(regen, LayerType.INNER)
        ship.recalculate_stats()

        cons = regen.get_ability('ResourceConsumption')
        val = cons.amount if cons else 'MISSING'
        print(f"DEBUG: Post-Recalc Energy Cost: {val}")

        assert val == 2.0, "Energy cost should persist as 2.0"
