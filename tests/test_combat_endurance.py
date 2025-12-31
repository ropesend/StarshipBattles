import unittest
import sys
import os
import pygame

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ship import Ship, initialize_ship_data
from components import load_components, create_component, Component, LayerType
from ship_stats import ShipStatsCalculator

class TestCombatEndurance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        initialize_ship_data(base_dir)
        load_components(os.path.join(base_dir, "data", "components.json"))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.ship = Ship("EnduranceTest", 0, 0, (255, 255, 255), ship_class="Cruiser")
        # Add basic crew support
        self.ship.add_component(create_component('bridge'), LayerType.CORE)
        self.ship.add_component(create_component('crew_quarters'), LayerType.CORE)
        self.ship.add_component(create_component('life_support'), LayerType.CORE)
        self.calculator = ShipStatsCalculator(self.ship.vehicle_classes if hasattr(self.ship, 'vehicle_classes') else {})

    def test_fuel_endurance(self):
        # Add Fuel Tank: 1000 capacity
        tank = create_component('fuel_tank')
        tank.data['capacity'] = 1000
        tank.capacity = 1000
        self.ship.add_component(tank, LayerType.INNER)
        
        # Add Engine: standard_engine cost 0.5 default
        engine = create_component('standard_engine')
        # We need to update data to ensure recalculate_stats doesn't reset it
        engine.data['fuel_cost'] = 10
        engine.fuel_cost_per_sec = 10
        self.ship.add_component(engine, LayerType.OUTER)
        
        self.ship.recalculate_stats()
        
        self.assertEqual(self.ship.fuel_consumption, 10.0)
        self.assertEqual(self.ship.fuel_endurance, 100.0) # 1000 / 10

    def test_ordnance_endurance(self):
        # Add Ammo Tank: 500 capacity
        tank = create_component('ordnance_tank')
        tank.data['capacity'] = 500
        tank.capacity = 500
        tank.resource_type = 'ammo'
        self.ship.add_component(tank, LayerType.INNER)
        
        # Add Weapon: railgun 
        weapon = create_component('railgun')
        weapon.data['reload'] = 2.0
        weapon.reload_time = 2.0
        weapon.data['ammo_cost'] = 10
        weapon.ammo_cost = 10
        self.ship.add_component(weapon, LayerType.OUTER)
        
        self.ship.recalculate_stats()
        
        # Rate = 10 / 2.0 = 5.0
        self.assertEqual(self.ship.ammo_consumption, 5.0)
        self.assertEqual(self.ship.ammo_endurance, 100.0) # 500 / 5

    def test_energy_endurance_drain(self):
        # Add Generator: generator (25/s)
        gen = create_component('generator')
        gen.data['energy_generation'] = 50
        gen.energy_generation_rate = 50
        self.ship.add_component(gen, LayerType.INNER)
        
        # Add Battery: 1000 capacity
        bat = create_component('battery')
        bat.data['capacity'] = 1000
        bat.capacity = 1000
        bat.resource_type = 'energy'
        self.ship.add_component(bat, LayerType.INNER)
        
        # Add Beam Weapon: laser_cannon
        # Override
        beam = create_component('laser_cannon')
        beam.data['reload'] = 1.0
        beam.reload_time = 1.0
        beam.data['energy_cost'] = 100
        beam.energy_cost = 100
        self.ship.add_component(beam, LayerType.OUTER)
        
        self.ship.recalculate_stats()
        
        # Net = 50 - 100 = -50
        self.assertEqual(self.ship.energy_consumption, 100.0)
        self.assertEqual(self.ship.energy_net, -50.0)
        self.assertEqual(self.ship.energy_endurance, 20.0) # 1000 / 50

    def test_energy_recharge(self):
        # Add Generator: generator
        gen = create_component('generator')
        gen.data['energy_generation'] = 100
        gen.energy_generation_rate = 100
        self.ship.add_component(gen, LayerType.INNER)
        
        # Add Battery: 2000 capacity
        bat = create_component('battery')
        bat.data['capacity'] = 2000
        bat.capacity = 2000
        self.ship.add_component(bat, LayerType.INNER)
        
        self.ship.recalculate_stats()
        
        self.assertEqual(self.ship.energy_recharge, 20.0) # 2000 / 100
        self.assertEqual(self.ship.energy_endurance, float('inf')) # Positive net

    def test_standard_components_defaults(self):
        """Verify standard components (Laser, Generator) work without manual data tweaking."""
        # Add Generator (25 gen)
        self.ship.add_component(create_component('generator'), LayerType.INNER)
        # Add Battery
        self.ship.add_component(create_component('battery'), LayerType.INNER)
        # Add Laser (5 cost, 0.2 reload -> 25 cost/sec)
        self.ship.add_component(create_component('laser_cannon'), LayerType.OUTER)
        
        self.ship.recalculate_stats()
        
        self.assertEqual(self.ship.energy_gen_rate, 25.0)
        self.assertEqual(self.ship.energy_consumption, 25.0)
        # Net 0
        self.assertEqual(self.ship.energy_net, 0.0)
        self.assertEqual(self.ship.energy_endurance, float('inf'))

if __name__ == '__main__':
    unittest.main()
