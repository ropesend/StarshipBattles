
import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from game.simulation.components.component import Component, LayerType
from game.simulation.entities.ship import Ship
from ship_stats import ShipStatsCalculator

class TestStackingRules(unittest.TestCase):
    def setUp(self):
        self.ship = Ship("Test Ship", 0, 0, (255, 0, 0), ship_class="Cruiser")
        # Mock layers
        self.ship.layers[LayerType.OUTER] = {'components': [], 'radius_pct': 1.0, 'restrictions': [], 'max_mass_pct': 1.0, 'max_hp_pool': 100, 'hp_pool': 100}
        self.ship.layers[LayerType.ARMOR] = {'components': [], 'radius_pct': 1.0, 'restrictions': [], 'max_mass_pct': 1.0, 'max_hp_pool': 100, 'hp_pool': 100}
        self.ship.layers[LayerType.INNER] = {'components': [], 'radius_pct': 1.0, 'restrictions': [], 'max_mass_pct': 1.0, 'max_hp_pool': 100, 'hp_pool': 100}

        # Mocks for testing behavior
        self.sensor_data = {
            "id": "sensor_1", "name": "Sensor", "type": "Sensor", "mass": 10, "hp": 10, "allowed_layers": ["OUTER"],
            "abilities": { "ToHitAttackModifier": { "value": 2.0, "stack_group": "Sensor" } } 
        }
        self.mini_sensor_data = {
            "id": "sensor_2", "name": "Mini Sensor", "type": "Sensor", "mass": 5, "hp": 5, "allowed_layers": ["OUTER"],
            "abilities": { "ToHitAttackModifier": { "value": 1.5, "stack_group": "Sensor" } }
        }
        self.ecm_data = {
            "id": "ecm_1", "name": "ECM", "type": "Electronics", "mass": 10, "hp": 10, "allowed_layers": ["OUTER"],
            "abilities": { "ToHitDefenseModifier": { "value": 2.0, "stack_group": "ECM" } }
        }
        self.mini_ecm_data = {
            "id": "ecm_2", "name": "Mini ECM", "type": "Electronics", "mass": 5, "hp": 5, "allowed_layers": ["OUTER"],
            "abilities": { "ToHitDefenseModifier": { "value": 1.2, "stack_group": "ECM" } }
        }
        self.scattering_data = {
            "id": "scat_1", "name": "Scattering", "type": "Armor", "mass": 10, "hp": 10, "allowed_layers": ["ARMOR"],
            "abilities": { "ToHitDefenseModifier": { "value": 1.5, "stack_group": "Scattering" } }
        }
        self.crew_quarters_data = {
            "id": "crew_1", "name": "Crew Q", "type": "CrewQuarters", "mass": 10, "hp": 10, "allowed_layers": ["INNER"],
            "abilities": { "CrewCapacity": 10 }
        }

    def _make_comp(self, data):
        return Component(data)

    def test_sensor_stacking(self):
        """Sensors should PROVIDE REDUNDANCY (Max), not stack (Multiply/Sum)"""
        # Sensor 1 (2.0) + Sensor 2 (1.5) -> Max is 2.0.
        c1 = self._make_comp(self.sensor_data)
        c2 = self._make_comp(self.mini_sensor_data)
        self.ship.add_component(c1, LayerType.OUTER)
        self.ship.add_component(c2, LayerType.OUTER)
        
        # Expected: 2.0
        self.assertAlmostEqual(self.ship.baseline_to_hit_offense, 2.0)

    def test_ecm_redundancy(self):
        """ECM should PROVIDE REDUNDANCY (Max)"""
        # ECM (2.0) + Mini ECM (1.2) -> Max is 2.0.
        c1 = self._make_comp(self.ecm_data)
        c2 = self._make_comp(self.mini_ecm_data)
        self.ship.add_component(c1, LayerType.OUTER)
        self.ship.add_component(c2, LayerType.OUTER)
        
        # Check defense profile (raw calculation might differ, check stats via calculator if possible or reverse engineer)
        # ship.to_hit_profile uses defense_mods
        # ToHitDefenseModifier total should be 2.0
        
        totals = self.ship.stats_calculator.calculate_ability_totals([c1, c2])
        self.assertAlmostEqual(totals.get('ToHitDefenseModifier', 0), 2.0)

    def test_ecm_and_scattering_stacking(self):
        """ECM and Scattering should STACK (Multiply)"""
        # ECM (2.0) [Group ECM] + Scattering (1.5) [Group Scattering] -> 2.0 * 1.5 = 3.0
        c1 = self._make_comp(self.ecm_data)
        c2 = self._make_comp(self.scattering_data)
        self.ship.add_component(c1, LayerType.OUTER)
        self.ship.add_component(c2, LayerType.ARMOR)
        
        totals = self.ship.stats_calculator.calculate_ability_totals([c1, c2])
        self.assertAlmostEqual(totals.get('ToHitDefenseModifier', 0), 3.0)

    def test_normal_stacking(self):
        """Crew Quarters should stack normally (Sum)"""
        c1 = self._make_comp(self.crew_quarters_data)
        c2 = self._make_comp(self.crew_quarters_data)
        self.ship.add_component(c1, LayerType.INNER)
        self.ship.add_component(c2, LayerType.INNER)
        
        # ship.crew_onboard should be 20
        self.assertEqual(self.ship.crew_onboard, 20)

if __name__ == '__main__':
    unittest.main()
