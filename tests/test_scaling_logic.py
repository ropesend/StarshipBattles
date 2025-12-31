
import sys
import os
import unittest
import math

# Add project root to path
sys.path.append(os.getcwd())

from components import load_components, create_component, load_modifiers, MODIFIER_REGISTRY

class TestScalingLogic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_components("data/components.json")
        load_modifiers("data/modifiers.json")

    def test_consumption_scaling_linear(self):
        """
        Verify that consumption (fuel, ammo, energy) scales linearly with Size Mount.
        """
        # 1. Engine - Fuel Cost
        eng = create_component("standard_engine")
        base_fuel = eng.fuel_cost_per_sec
        # Add Size Mount x2
        eng.add_modifier("simple_size_mount", 2.0)
        
        self.assertAlmostEqual(eng.fuel_cost_per_sec, base_fuel * 2, msg="Fuel cost should scale linearly with size")

        # 2. Railgun - Ammo Cost
        rg = create_component("railgun")
        base_ammo = rg.ammo_cost
        rg.add_modifier("simple_size_mount", 2.0)
        
        self.assertAlmostEqual(rg.ammo_cost, base_ammo * 2, msg="Ammo cost should scale linearly with size")

        # 3. Laser Cannon - Energy Cost
        lc = create_component("laser_cannon")
        base_energy = lc.energy_cost
        lc.add_modifier("simple_size_mount", 2.0)
        
        self.assertAlmostEqual(lc.energy_cost, base_energy * 2, msg="Energy cost should scale linearly with size")

    def test_crew_requirement_scaling_size_mount(self):
        """
        Verify Crew Required scales with sqrt(mass) for Size Mount.
        Size Mount x4 -> Mass x4 -> Sqrt(4) = 2x Crew Req.
        """
        # Railgun has CrewRequired: 5
        rg = create_component("railgun")
        base_crew = rg.abilities.get("CrewRequired", 0)
        self.assertEqual(base_crew, 5, "Base Railgun Crew Req should be 5")
        
        # Add Size Mount x4
        rg.add_modifier("simple_size_mount", 4.0)
        
        expected_crew = int(math.ceil(base_crew * math.sqrt(4.0))) # 5 * 2 = 10
        current_crew = rg.abilities.get("CrewRequired", 0)
        
        self.assertEqual(current_crew, expected_crew, 
                         f"Crew Req should scale with sqrt(mass). Expected {expected_crew}, got {current_crew}")

    def test_crew_requirement_scaling_range_mount(self):
        """
        Verify Crew Required scales with sqrt(mass) for Range Mount.
        Range Mount Level 1 -> Mass x3.5 -> Sqrt(3.5).
        """
        # Railgun CrewReq: 5
        rg = create_component("railgun")
        base_crew = rg.abilities.get("CrewRequired", 0)
        
        rg.add_modifier("range_mount", 1.0)
        
        mass_mult = 3.5 ** 1.0
        expected_crew = int(math.ceil(base_crew * math.sqrt(mass_mult)))
        current_crew = rg.abilities.get("CrewRequired", 0)
        
        # We expect this to fail effectively until implemented
        print(f"Range Mount Test: Base {base_crew}, MassMult {mass_mult}, Expected {expected_crew}, Got {current_crew}")
        
        self.assertEqual(current_crew, expected_crew, 
                         f"Crew Req should scale with sqrt(mass_mult) for Range Mount.")

    def test_crew_requirement_scaling_combined(self):
        """
        Verify scaling works if multiple modifiers affect mass.
        """
        # Use simple size x2 and Range Mount x1
        rg = create_component("railgun")
        base_crew = rg.abilities.get("CrewRequired", 0)
        
        rg.add_modifier("simple_size_mount", 2.0)
        rg.add_modifier("range_mount", 1.0)
        
        # Mass Mults accumulate multiplicatively in current logic? 
        # range_mount: stats['mass_mult'] *= 3.5^level
        # simple_size: stats['mass_mult'] *= scale
        
        total_mass_mult = 2.0 * 3.5
        expected_crew = int(math.ceil(base_crew * math.sqrt(total_mass_mult)))
        current_crew = rg.abilities.get("CrewRequired", 0)
        
        self.assertEqual(current_crew, expected_crew, "Crew Req should scale with sqrt of total mass multiplier")

if __name__ == '__main__':
    unittest.main()
