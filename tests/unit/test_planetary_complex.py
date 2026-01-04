
import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from game.simulation.entities.ship import Ship, initialize_ship_data, VEHICLE_CLASSES, LayerType
from game.simulation.components.component import load_components, load_modifiers, get_all_components, COMPONENT_REGISTRY

class TestPlanetaryComplex(unittest.TestCase):
    """Test Planetary Complex implementation."""
    
    def setUp(self):
        initialize_ship_data()
        load_components()
        load_modifiers()

    def test_planetary_complex_tiers_exist(self):
        """Verify all 11 tiers of Planetary Complex exist."""
        for i in range(1, 12):
            class_name = f"Planetary Complex (Tier {i})"
            self.assertIn(class_name, VEHICLE_CLASSES, f"{class_name} missing")
            
            # Check mass doubling
            vehicle_def = VEHICLE_CLASSES[class_name]
            expected_mass = 1000 * (2**(i-1))
            self.assertEqual(vehicle_def['max_mass'], expected_mass, 
                            f"{class_name} mass incorrect")
            self.assertEqual(vehicle_def['type'], "Planetary Complex")

    def test_add_central_command(self):
        """Verify Central Complex Command can be added."""
        complex_ship = Ship("Test Complex", 0, 0, (255, 255, 255), 
                          ship_class="Planetary Complex (Tier 1)")
        
        command = COMPONENT_REGISTRY["central_complex_command"].clone()
        result = complex_ship.add_component(command, LayerType.CORE)
        self.assertTrue(result, "Should accept Central Complex Command")
        
        complex_ship.recalculate_stats()
        self.assertTrue(complex_ship.get_ability_total("CommandAndControl"), 
                       "Should have CommandAndControl ability")

    def test_accepts_ship_components(self):
        """Verify it accepts standard ship weapons and sensors."""
        complex_ship = Ship("Test Complex", 0, 0, (255, 255, 255), 
                          ship_class="Planetary Complex (Tier 1)")
        
        # Weapons
        railgun = COMPONENT_REGISTRY["railgun"].clone()
        result = complex_ship.add_component(railgun, LayerType.OUTER)
        self.assertTrue(result, "Should accept Railgun")
        
        # Sensors
        sensor = COMPONENT_REGISTRY["combat_sensor"].clone()
        result = complex_ship.add_component(sensor, LayerType.OUTER)
        self.assertTrue(result, "Should accept Combat Sensor")
        
        # Shields
        shield = COMPONENT_REGISTRY["shield_generator"].clone()
        result = complex_ship.add_component(shield, LayerType.INNER)
        self.assertTrue(result, "Should accept Shield Generator")

    def test_rejects_propulsion(self):
        """Verify it rejects engines and thrusters."""
        complex_ship = Ship("Test Complex", 0, 0, (255, 255, 255), 
                          ship_class="Planetary Complex (Tier 1)")
        
        engine = COMPONENT_REGISTRY["standard_engine"].clone()
        result = complex_ship.add_component(engine, LayerType.INNER)
        self.assertFalse(result, "Should REJECT Standard Engine")
        
        thruster = COMPONENT_REGISTRY["thruster"].clone()
        result = complex_ship.add_component(thruster, LayerType.OUTER)
        self.assertFalse(result, "Should REJECT Thruster")

    def test_rejects_ship_bridge(self):
        """Verify it rejects standard Ship Bridge."""
        complex_ship = Ship("Test Complex", 0, 0, (255, 255, 255), 
                          ship_class="Planetary Complex (Tier 1)")
        
        bridge = COMPONENT_REGISTRY["bridge"].clone()
        result = complex_ship.add_component(bridge, LayerType.CORE)
        self.assertFalse(result, "Should REJECT standard Ship Bridge")

    def test_movement_capabilities(self):
        """Verify it has zero movement capabilities."""
        complex_ship = Ship("Test Complex", 0, 0, (255, 255, 255), 
                          ship_class="Planetary Complex (Tier 1)")
        
        command = COMPONENT_REGISTRY["central_complex_command"].clone()
        complex_ship.add_component(command, LayerType.CORE)
        complex_ship.recalculate_stats()
        
        self.assertEqual(complex_ship.total_thrust, 0)
        self.assertEqual(complex_ship.turn_speed, 0)

if __name__ == '__main__':
    unittest.main()
