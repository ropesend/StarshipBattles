
import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from ship import Ship, initialize_ship_data, VEHICLE_CLASSES, LayerType
from components import load_components, get_all_components, COMPONENT_REGISTRY, Bridge

class TestVehicleTypes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize data
        initialize_ship_data()
        load_components()

    def test_vehicle_type_loading(self):
        # Verify classes loaded
        self.assertIn("Fighter (Small)", VEHICLE_CLASSES)
        self.assertIn("Satellite (Small)", VEHICLE_CLASSES)
        
        # Verify types
        self.assertEqual(VEHICLE_CLASSES["Escort"]["type"], "Ship")
        self.assertEqual(VEHICLE_CLASSES["Fighter (Small)"]["type"], "Fighter")
        self.assertEqual(VEHICLE_CLASSES["Satellite (Small)"]["type"], "Satellite")

    def test_ship_initialization(self):
        # Create a Fighter
        fighter = Ship("Test Fighter", 0, 0, (255,0,0), ship_class="Fighter (Small)")
        self.assertEqual(fighter.vehicle_type, "Fighter")
        # Base mass should match class hull mass
        self.assertEqual(fighter.base_mass, 5) 
        
        # Create a Satellite
        sat = Ship("Test Satellite", 0, 0, (255,0,0), ship_class="Satellite (Small)")
        self.assertEqual(sat.vehicle_type, "Satellite")
        self.assertEqual(sat.base_mass, 50)

    def test_component_restrictions(self):
        fighter = Ship("Test Fighter", 0, 0, (255,0,0), ship_class="Fighter (Small)")
        
        # Fighter Cockpit (Should be allowed)
        cockpit = COMPONENT_REGISTRY["fighter_cockpit"].clone()
        success = fighter.add_component(cockpit, LayerType.CORE)
        self.assertTrue(success, "Fighter Cockpit should be allowed on Fighter")
        
        # Standard Bridge (Should NOT be allowed)
        bridge = COMPONENT_REGISTRY["bridge"].clone()
        success = fighter.add_component(bridge, LayerType.CORE)
        self.assertFalse(success, "Standard Bridge should NOT be allowed on Fighter")
        
        # Allowed check
        self.assertIn("Fighter", cockpit.allowed_vehicle_types)
        self.assertNotIn("Fighter", bridge.allowed_vehicle_types)

    def test_satellite_logic(self):
        sat = Ship("Test Satellite", 0, 0, (255,0,0), ship_class="Satellite (Small)")
        
        # Add Satellite Core (Command)
        core = COMPONENT_REGISTRY["satellite_core"].clone()
        sat.add_component(core, LayerType.CORE)
        
        # Recalculate stats
        sat.recalculate_stats()
        
        # Should NOT be derelict despite 0 thrust
        self.assertEqual(sat.total_thrust, 0)
        self.assertFalse(sat.is_derelict, "Satellite with Core should NOT be derelict even with 0 thrust")
        
        # Verify standard ship behavior for contrast
        ship = Ship("Test Ship", 0, 0, (255,0,0), ship_class="Escort")
        bridge = COMPONENT_REGISTRY["bridge"].clone()
        ship.add_component(bridge, LayerType.CORE)
        ship.recalculate_stats()
        
        self.assertEqual(ship.total_thrust, 0)
        self.assertTrue(ship.is_derelict, "Standard Ship with 0 thrust SHOULD be derelict")

    def test_satellite_crew_logic(self):
         # Satellites should ignore crew requirements
         sat = Ship("Test Satellite", 0, 0, (255,0,0), ship_class="Satellite (Small)")
         
         # Add a weapon that usually requires crew (if allowed on sat)
         # Railgun is allowed on Satellite and requires 5 Crew
         railgun = COMPONENT_REGISTRY["railgun"].clone()
         
         # Check restriction first (ensure I added it to allowed)
         self.assertIn("Satellite", railgun.allowed_vehicle_types)
         
         sat.add_component(railgun, LayerType.OUTER)
         
         # Recalculate
         sat.recalculate_stats()
         
         # Weapon should be active (crew requirement ignored)
         self.assertTrue(railgun.is_active, "Railgun on Satellite should be active despite no crew")
         self.assertEqual(sat.crew_required, 0, "Satellite should have 0 crew required")

if __name__ == '__main__':
    unittest.main()
