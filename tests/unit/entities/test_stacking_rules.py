import pytest

from game.simulation.components.component import Component
from game.core.constants import LayerType
from game.simulation.entities.ship import Ship
from game.simulation.entities.ship_stats import ShipStatsCalculator


@pytest.fixture
def ship_with_layers(fresh_registries):
    """Create a ship with mock layers for testing."""
    ship = Ship("Test Ship", 0, 0, (255, 0, 0), ship_class="Cruiser", registries=fresh_registries)
    # Mock layers
    ship.layers[LayerType.OUTER] = {'components': [], 'radius_pct': 1.0, 'restrictions': [], 'max_mass_pct': 1.0, 'max_hp_pool': 100, 'hp_pool': 100}
    ship.layers[LayerType.ARMOR] = {'components': [], 'radius_pct': 1.0, 'restrictions': [], 'max_mass_pct': 1.0, 'max_hp_pool': 100, 'hp_pool': 100}
    ship.layers[LayerType.INNER] = {'components': [], 'radius_pct': 1.0, 'restrictions': [], 'max_mass_pct': 1.0, 'max_hp_pool': 100, 'hp_pool': 100}
    ship._fresh_registries = fresh_registries  # Store for component creation
    return ship


@pytest.fixture
def component_data():
    """Return component data dicts for testing."""
    return {
        'sensor': {
            "id": "sensor_1", "name": "Sensor", "type": "Sensor", "mass": 10, "hp": 10, "allowed_layers": ["OUTER"],
            "abilities": {"ToHitAttackModifier": {"value": 2.0, "stack_group": "Sensor"}}
        },
        'mini_sensor': {
            "id": "sensor_2", "name": "Mini Sensor", "type": "Sensor", "mass": 5, "hp": 5, "allowed_layers": ["OUTER"],
            "abilities": {"ToHitAttackModifier": {"value": 1.5, "stack_group": "Sensor"}}
        },
        'ecm': {
            "id": "ecm_1", "name": "ECM", "type": "Electronics", "mass": 10, "hp": 10, "allowed_layers": ["OUTER"],
            "abilities": {"ToHitDefenseModifier": {"value": 2.0, "stack_group": "ECM"}}
        },
        'mini_ecm': {
            "id": "ecm_2", "name": "Mini ECM", "type": "Electronics", "mass": 5, "hp": 5, "allowed_layers": ["OUTER"],
            "abilities": {"ToHitDefenseModifier": {"value": 1.2, "stack_group": "ECM"}}
        },
        'scattering': {
            "id": "scat_1", "name": "Scattering", "type": "Armor", "mass": 10, "hp": 10, "allowed_layers": ["ARMOR"],
            "abilities": {"ToHitDefenseModifier": {"value": 1.5, "stack_group": "Scattering"}}
        },
        'crew_quarters': {
            "id": "crew_1", "name": "Crew Q", "type": "CrewQuarters", "mass": 10, "hp": 10, "allowed_layers": ["INNER"],
            "abilities": {"CrewCapacity": 10}
        }
    }


class TestStackingRules:
    def test_sensor_stacking(self, ship_with_layers, component_data):
        """Sensors should PROVIDE REDUNDANCY (Max), not stack (Multiply/Sum)"""
        # Sensor 1 (2.0) + Sensor 2 (1.5) -> Max is 2.0.
        regs = ship_with_layers._fresh_registries
        c1 = Component(component_data['sensor'], registries=regs)
        c2 = Component(component_data['mini_sensor'], registries=regs)
        ship_with_layers.add_component(c1, LayerType.OUTER)
        ship_with_layers.add_component(c2, LayerType.OUTER)

        # Expected: 2.0
        assert ship_with_layers.baseline_to_hit_offense == pytest.approx(2.0)

    def test_ecm_redundancy(self, ship_with_layers, component_data):
        """ECM should PROVIDE REDUNDANCY (Max)"""
        # ECM (2.0) + Mini ECM (1.2) -> Max is 2.0.
        regs = ship_with_layers._fresh_registries
        c1 = Component(component_data['ecm'], registries=regs)
        c2 = Component(component_data['mini_ecm'], registries=regs)
        ship_with_layers.add_component(c1, LayerType.OUTER)
        ship_with_layers.add_component(c2, LayerType.OUTER)

        # Check defense profile (raw calculation might differ, check stats via calculator if possible or reverse engineer)
        # ship.to_hit_profile uses defense_mods
        # ToHitDefenseModifier total should be 2.0

        totals = ship_with_layers.stats_calculator.calculate_ability_totals([c1, c2])
        assert totals.get('ToHitDefenseModifier', 0) == pytest.approx(2.0)

    def test_ecm_and_scattering_stacking(self, ship_with_layers, component_data):
        """ECM and Scattering should STACK (Multiply)"""
        # ECM (2.0) [Group ECM] + Scattering (1.5) [Group Scattering] -> 2.0 * 1.5 = 3.0
        regs = ship_with_layers._fresh_registries
        c1 = Component(component_data['ecm'], registries=regs)
        c2 = Component(component_data['scattering'], registries=regs)
        ship_with_layers.add_component(c1, LayerType.OUTER)
        ship_with_layers.add_component(c2, LayerType.ARMOR)

        totals = ship_with_layers.stats_calculator.calculate_ability_totals([c1, c2])
        assert totals.get('ToHitDefenseModifier', 0) == pytest.approx(3.0)

    def test_normal_stacking(self, ship_with_layers, component_data):
        """Crew Quarters should stack normally (Sum)"""
        regs = ship_with_layers._fresh_registries
        c1 = Component(component_data['crew_quarters'], registries=regs)
        c2 = Component(component_data['crew_quarters'], registries=regs)
        ship_with_layers.add_component(c1, LayerType.INNER)
        ship_with_layers.add_component(c2, LayerType.INNER)

        # ship.crew_onboard should be 20
        assert ship_with_layers.crew_onboard == 20
