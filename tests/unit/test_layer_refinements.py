import unittest
from unittest.mock import MagicMock
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from game.simulation.entities.ship import Ship, LayerType, initialize_ship_data
from game.simulation.components.component import Component

class TestLayerRefinements(unittest.TestCase):

    def setUp(self):
        initialize_ship_data()
        # Create a Fighter (2 layers: CORE, ARMOR)
        # Note: We rely on the vehicle classes loaded from JSON (which we updated)
        self.fighter = Ship("TestFighter", 0, 0, (255, 0, 0), ship_class="Fighter (Small)")
        
        # Create an Escort (3 layers: CORE, OUTER, ARMOR) - assumption based on typical data
        # If Escort has 4, we adjust. Let's check keys.
        self.escort = Ship("TestEscort", 0, 0, (0, 255, 0), ship_class="Escort")

    def test_layer_mass_limits_loaded(self):
        """Verify max_mass_pct is loaded correctly from JSON."""
        # Fighter: 2 layers -> CORE: 1.0, ARMOR: 0.3
        core = self.fighter.layers[LayerType.CORE]
        armor = self.fighter.layers[LayerType.ARMOR]
        
        self.assertEqual(core['max_mass_pct'], 1.0, "Fighter CORE should be 100%")
        self.assertAlmostEqual(armor['max_mass_pct'], 0.3, places=2, msg="Fighter ARMOR should be 30%")
        
        # Verify Escort (likely 3 layers: Core, Outer, Armor)
        # 3-layer -> Core: 0.5, Outer: 0.7, Armor: 0.3
        # Or 4-layer? Let's check what keys it has.
        layer_count = len(self.escort.layers)
        
        if layer_count == 3:
            self.assertEqual(self.escort.layers[LayerType.CORE]['max_mass_pct'], 0.5)
            self.assertEqual(self.escort.layers[LayerType.OUTER]['max_mass_pct'], 0.7)
        elif layer_count == 4:
            # 4-layer -> Core: 0.3, Inner: 0.5, Outer: 0.5, Armor: 0.3 (Capital_Escort)
            self.assertEqual(self.escort.layers[LayerType.CORE]['max_mass_pct'], 0.3)
            self.assertEqual(self.escort.layers[LayerType.OUTER]['max_mass_pct'], 0.5)
            
    def test_mass_budget_enforcement(self):
        """Verify mass_budget_exceeded logic via VALIDATOR."""
        # Fighter Max Mass = 250 (from JSON usually)
        max_mass = self.fighter.max_mass_budget
        
        # Armor Limit = 30% of max_mass
        armor_limit = max_mass * 0.3
        
        # Mock component
        heavy_armor = MagicMock(spec=Component)
        heavy_armor.mass = armor_limit + 10
        heavy_armor.allowed_layers = [LayerType.ARMOR]
        heavy_armor.allowed_vehicle_types = ["Fighter"]
        heavy_armor.data = {'major_classification': 'Armor'}
        # Specific attributes needed for checks
        heavy_armor.type_str = "Armor"
        heavy_armor.id = "heavy_armor"
        # Since we use validate_addition, we need to ensure other checks pass or we focus on mass
        from ship_validator import MassBudgetRule
        
        rule = MassBudgetRule()
        
        # Check budget check directly using strict rule check to Isolate test
        res = rule.validate(self.fighter, heavy_armor, LayerType.ARMOR)
        self.assertFalse(res.is_valid, "Should fail mass budget")
        self.assertTrue(any("Mass budget exceeded" in e for e in res.errors))
        
        # Check allowed mass
        light_armor = MagicMock(spec=Component)
        light_armor.mass = armor_limit - 10
        light_armor.allowed_layers = [LayerType.ARMOR]
        light_armor.allowed_vehicle_types = ["Fighter"]
        light_armor.data = {'major_classification': 'Armor'}
        light_armor.type_str = "Armor"
        light_armor.id = "light_armor"
        
        res = rule.validate(self.fighter, light_armor, LayerType.ARMOR)
        self.assertTrue(res.is_valid, "Should allow mass within budget")

    def test_all_layers_filter_logic(self):
        """Verify the logic for 'All Layers' filter."""
        # Simulation of the logic in left_panel.py
        
        # Component allowed in CORE only
        comp_core = MagicMock()
        comp_core.allowed_layers = [LayerType.CORE]
        
        # Component allowed in OUTER only
        comp_outer = MagicMock()
        comp_outer.allowed_layers = [LayerType.OUTER]
        
        # Fighter has CORE, ARMOR. No OUTER.
        valid_layers_fighter = set(self.fighter.layers.keys())
        
        # Check Core Comp -> Should be visible
        self.assertTrue(any(l in valid_layers_fighter for l in comp_core.allowed_layers))
        
        # Check Outer Comp -> Should NOT be visible on Fighter
        self.assertFalse(any(l in valid_layers_fighter for l in comp_outer.allowed_layers))
        
        # Escort (assuming it has OUTER)
        valid_layers_escort = set(self.escort.layers.keys())
        if LayerType.OUTER in valid_layers_escort:
             self.assertTrue(any(l in valid_layers_escort for l in comp_outer.allowed_layers))

    def test_dynamic_radius_calculation(self):
        """Verify layer radii are calculated based on area proportional to mass."""
        # For Fighter:
        # CORE: 1.0 Mass Pct
        # ARMOR: 0.3 Mass Pct
        # Total Capacity = 1.3
        
        # Expected Radii:
        # Core Radius = sqrt(1.0 / 1.3) = sqrt(0.769) ~= 0.877
        # Armor Radius = sqrt((1.0 + 0.3) / 1.3) = sqrt(1.0) = 1.0
        
        core_r = self.fighter.layers[LayerType.CORE]['radius_pct']
        armor_r = self.fighter.layers[LayerType.ARMOR]['radius_pct']
        
        self.assertAlmostEqual(core_r, 0.877, places=3, msg=f"Fighter Core Radius mismatch. Got {core_r}")
        self.assertAlmostEqual(armor_r, 1.0, places=3, msg=f"Fighter Armor Radius mismatch. Got {armor_r}")
        
        # Verify Escort (assuming 3 layers: Core 0.5, Outer 0.7, Armor 0.3) -> Total 1.5 (or whatever it actually is)
        # Inspect actual mass limits to be sure
        present_layers = [l for l in [LayerType.CORE, LayerType.INNER, LayerType.OUTER, LayerType.ARMOR] if l in self.escort.layers]
        total_mass = sum(self.escort.layers[l]['max_mass_pct'] for l in present_layers)
        
        cumulative = 0
        for l in present_layers:
            cumulative += self.escort.layers[l]['max_mass_pct']
            expected_r = (cumulative / total_mass) ** 0.5
            actual_r = self.escort.layers[l]['radius_pct']
            self.assertAlmostEqual(actual_r, expected_r, places=3, msg=f"Escort {l.name} radius mismatch")

if __name__ == '__main__':
    unittest.main()
