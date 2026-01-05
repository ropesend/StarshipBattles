
import sys
import os
import unittest
import math

# Add project root to path
sys.path.append(os.getcwd())

from game.simulation.components.component import load_components, create_component, load_modifiers

class TestScalingLogic(unittest.TestCase):
    def setUp(self):
        load_components("data/components.json")
        load_modifiers("data/modifiers.json")

    def test_consumption_scaling_linear(self):
        """Test linear consumption scaling."""
        engine = create_component('standard_engine')
        
        # Get base consumption
        base_cons = 0
        from game.simulation.systems.resource_manager import ResourceConsumption
        for ab in engine.ability_instances:
             if isinstance(ab, ResourceConsumption) and ab.resource_name == 'fuel':
                 base_cons = ab.amount
                 break
                 
        engine.add_modifier('efficient_engines') # 0.8x mul
        engine.recalculate_stats()
        
        new_cons = 0
        for ab in engine.ability_instances:
             if isinstance(ab, ResourceConsumption) and ab.resource_name == 'fuel':
                 new_cons = ab.amount
                 break
                 
        self.assertAlmostEqual(new_cons, base_cons * 0.8, msg="Fuel cost should scale linearly with size")

        # 2. Railgun - Ammo Cost
        rg = create_component("railgun")
        base_ammo = 0
        from game.simulation.systems.resource_manager import ResourceConsumption
        for ab in rg.ability_instances:
             if isinstance(ab, ResourceConsumption) and ab.resource_name == 'ammo':
                 base_ammo = ab.amount
                 break
                 
        rg.add_modifier("simple_size_mount", 2.0)
        rg.recalculate_stats()
        
        new_ammo = 0
        for ab in rg.ability_instances:
             if isinstance(ab, ResourceConsumption) and ab.resource_name == 'ammo':
                 new_ammo = ab.amount
                 break
        
        self.assertAlmostEqual(new_ammo, base_ammo * 2, msg="Ammo cost should scale linearly with size")

        # 3. Laser Cannon - Energy Cost
        lc = create_component("laser_cannon")
        base_energy = 0
        for ab in lc.ability_instances:
             if isinstance(ab, ResourceConsumption) and ab.resource_name == 'energy':
                 base_energy = ab.amount
                 break
                 
        lc.add_modifier("simple_size_mount", 2.0)
        lc.recalculate_stats()
        
        new_energy = 0
        for ab in lc.ability_instances:
             if isinstance(ab, ResourceConsumption) and ab.resource_name == 'energy':
                 new_energy = ab.amount
                 break
        
        self.assertAlmostEqual(new_energy, base_energy * 2, msg="Energy cost should scale linearly with size")

    def _get_crew_req(self, comp):
        ab = comp.get_ability("CrewRequired")
        if ab: return ab.amount
        return comp.abilities.get("CrewRequired", 0)

    def test_crew_requirement_scaling_size_mount(self):
        """
        Verify Crew Required scales with sqrt(mass) for Size Mount.
        Size Mount x4 -> Mass x4 -> Sqrt(4) = 2x Crew Req.
        """
        # Railgun has CrewRequired: 5
        rg = create_component("railgun")
        base_crew = self._get_crew_req(rg)
        self.assertEqual(base_crew, 5, "Base Railgun Crew Req should be 5")
        
        # Add Size Mount x4
        rg.add_modifier("simple_size_mount", 4.0)
        rg.recalculate_stats()
        
        expected_crew = int(math.ceil(base_crew * math.sqrt(4.0))) # 5 * 2 = 10
        current_crew = self._get_crew_req(rg)
        
        self.assertEqual(current_crew, expected_crew, 
                         f"Crew Req should scale with sqrt(mass). Expected {expected_crew}, got {current_crew}")

    def test_crew_requirement_scaling_range_mount(self):
        """
        Verify Crew Required scales with sqrt(mass) for Range Mount.
        Range Mount Level 1 -> Mass x3.5 -> Sqrt(3.5).
        """
        # Railgun CrewReq: 5
        rg = create_component("railgun")
        base_crew = self._get_crew_req(rg)
        
        rg.add_modifier("range_mount", 1.0)
        rg.recalculate_stats()
        
        mass_mult = 3.5 ** 1.0
        expected_crew = int(math.ceil(base_crew * math.sqrt(mass_mult)))
        current_crew = self._get_crew_req(rg)
        
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
        base_crew = self._get_crew_req(rg)
        
        rg.add_modifier("simple_size_mount", 2.0)
        rg.add_modifier("range_mount", 1.0)
        rg.recalculate_stats()
        
        # Mass Mults accumulate multiplicatively in current logic? 
        # range_mount: stats['mass_mult'] *= 3.5^level
        # simple_size: stats['mass_mult'] *= scale
        
        total_mass_mult = 2.0 * 3.5
        expected_crew = int(math.ceil(base_crew * math.sqrt(total_mass_mult)))
        current_crew = self._get_crew_req(rg)
        
        self.assertEqual(current_crew, expected_crew, "Crew Req should scale with sqrt of total mass multiplier")

if __name__ == '__main__':
    unittest.main()
