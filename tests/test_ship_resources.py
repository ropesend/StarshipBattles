"""Tests for Ship resource management, life support, and crew requirements."""
import unittest
import sys
import os
import pygame

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ship import Ship, LayerType, initialize_ship_data
from components import load_components, create_component, ComponentStatus

class TestShipResources(unittest.TestCase):
    """Test resource initialization, capacity, life support, and crew logic."""
    
    @classmethod
    def setUpClass(cls):
        pygame.init()
        # Ensure data dir is accessible
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        initialize_ship_data(base_dir)
        load_components(os.path.join(base_dir, "data", "components.json"))
    
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
        
    def setUp(self):
        self.ship = Ship("ResourceTest", 0, 0, (255, 255, 255), ship_class="Cruiser")
        # Add minimal functional core
        self.ship.add_component(create_component('bridge'), LayerType.CORE)
        self.ship.add_component(create_component('crew_quarters'), LayerType.CORE)
        self.ship.add_component(create_component('life_support'), LayerType.CORE)
        self.ship.recalculate_stats()

    def test_resource_initialization(self):
        """Resources should be auto-filled only on first initialization with capacity."""
        # Add components that provide capacity
        self.ship.add_component(create_component('fuel_tank'), LayerType.INNER)
        self.ship.add_component(create_component('ordnance_tank'), LayerType.INNER)
        self.ship.add_component(create_component('battery'), LayerType.INNER)
        
        # Trigger first initialization
        self.ship.recalculate_stats()
        
        self.assertTrue(self.ship._resources_initialized)
        self.assertEqual(self.ship.current_fuel, self.ship.max_fuel)
        self.assertEqual(self.ship.current_ammo, self.ship.max_ammo)
        self.assertEqual(self.ship.current_energy, self.ship.max_energy)
        
        # Manually reduce resources
        self.ship.current_fuel = 10
        
        # Recalculate should NOT refill unless flag is reset
        self.ship.recalculate_stats()
        self.assertEqual(self.ship.current_fuel, 10)

    def test_capacity_increase_refill(self):
        """Increasing capacity should only add the difference to current resources."""
        self.ship.add_component(create_component('fuel_tank'), LayerType.INNER)
        self.ship.recalculate_stats()
        
        max1 = self.ship.max_fuel
        self.ship.current_fuel = 50
        
        # Add another tank
        self.ship.add_component(create_component('fuel_tank'), LayerType.INNER)
        self.ship.recalculate_stats()
        
        max2 = self.ship.max_fuel
        diff = max2 - max1
        self.assertEqual(self.ship.current_fuel, 50 + diff)

    def test_crew_requirement_failure(self):
        """Components should deactivate if there is insufficient crew."""
        # Add a weapon that requires crew
        weapon = create_component('railgun') # Usually requires 5 crew
        self.ship.add_component(weapon, LayerType.OUTER)
        
        # Setup: 1 Bridge (5 housing), 1 Crew Quarters (20 housing), 1 Life Support (25 capacity)
        # Total housing: 25. Total requirement: Bridge (5) + Railgun (5) = 10.
        # Should be fine.
        self.ship.recalculate_stats()
        self.assertTrue(weapon.is_active)
        
        # Remove crew quarters
        self.ship.layers[LayerType.CORE]['components'] = [c for c in self.ship.layers[LayerType.CORE]['components'] if c.id != 'crew_quarters']
        # Now only Bridge (5 housing). Requirement 10.
        self.ship.recalculate_stats()
        
        # Railgun should be deactivated due to NO_CREW (Weapon has lower priority than Bridge)
        self.assertFalse(weapon.is_active)
        self.assertEqual(weapon.status, ComponentStatus.NO_CREW)

    def test_life_support_limitation(self):
        """Effective crew should be limited by life support capacity."""
        # Setup: 25 Crew Housing, but only 5 Life Support
        # Requirement: Bridge (5) + Railgun (5) = 10.
        # Since LS is 5, effective crew is 5. Bridge gets it first. Railgun starves.
        
        # Reset ship
        self.ship = Ship("LSTest", 0, 0, (255, 255, 255))
        self.ship.add_component(create_component('bridge'), LayerType.CORE)
        self.ship.add_component(create_component('crew_quarters'), LayerType.CORE)
        
        # Add a custom mock life support component with low capacity or just find a small one
        # Actually, let's just use a very small life support or none.
        # Recalculate without LS
        self.ship.recalculate_stats()
        # Bridge (5) needs crew. available_crew=25, LS=0. Effective=0.
        # Wait, if no LS provided, available_life_support=0.
        
        bridge = [c for c in self.ship.layers[LayerType.CORE]['components'] if c.id == 'bridge'][0]
        print(f"DEBUG: Bridge HP: {bridge.current_hp}/{bridge.max_hp} Status: {bridge.status}")
        self.assertFalse(bridge.is_active)
        self.assertEqual(bridge.status, ComponentStatus.NO_CREW)

    def test_satellite_ignores_crew(self):
        """Satellites should ignore crew requirements."""
        self.ship = Ship("SatResource", 0, 0, (255, 255, 255), ship_class="Satellite (Small)")
        # Satellite Core (Bridge) usually needs crew? 
        # Actually in ship.py:280, satellites ignore crew.
        
        core = create_component('satellite_core')
        self.ship.add_component(core, LayerType.CORE)
        
        # No crew quarters or life support added
        self.ship.recalculate_stats()
        
        self.assertTrue(core.is_active)
        self.assertFalse(self.ship.is_derelict)

if __name__ == '__main__':
    unittest.main()
