
import unittest
import sys
import os
import pygame
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from game.simulation.entities.ship import Ship, LayerType, initialize_ship_data, load_vehicle_classes
from game.simulation.components.component import create_component, Component, Modifier

class TestShipRequirements(unittest.TestCase):
    """
    Data-driven tests for ship operational requirements.
    Verifies that 'is_derelict' is correctly determined by vehicle class requirements.
    """

    @classmethod
    def setUpClass(cls):
        pygame.init()
        # Ensure we have clean data loading
        # We will be patching VEHICLE_CLASSES heavily in these tests
        pass

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.ship = Ship("TestShip", 0, 0, (255, 255, 255))
        # Clear layers
        self.ship.layers[LayerType.CORE]['components'] = []
        
        # Mock class data (default)
        self.class_data = {
            "hull_mass": 50, 
            "max_mass": 1000,
            "requirements": {} 
        }
        
    def _inject_class_data(self, requirements):
        """Helper to inject specific requirements into VEHICLE_CLASSES"""
        self.class_data['requirements'] = requirements
        
        from game.simulation.entities.ship import VEHICLE_CLASSES
        VEHICLE_CLASSES["RequirementsTest"] = self.class_data
        self.ship.ship_class = "RequirementsTest"
        self.ship.update_derelict_status()

    def _create_mock_component(self, id, name, abilities, mass=10, hp=10, c_type="Component"):
        data = {
            "id": id,
            "name": name,
            "mass": mass,
            "hp": hp,
            "type": c_type,
            "abilities": abilities
        }
        # Assuming Component class can handle this dict directly
        # and doesn't strict check registry for basic unit tests unless we use create_component
        return Component(data)

    def test_no_requirements_defaults_to_operational(self):
        """A ship with no requirements should naturally be operational (not derelict)."""
        self._inject_class_data({})
        self.assertFalse(self.ship.is_derelict)

    def test_boolean_requirement_missing(self):
        """Test simple boolean requirement (e.g., CommandAndControl)."""
        # Requirement: Needs "Command" ability
        self._inject_class_data({"Command": True})
        
        # Initially empty -> Derelict
        self.ship.update_derelict_status()
        self.assertTrue(self.ship.is_derelict, "Should be derelict without Command ability")
        
    def test_boolean_requirement_met(self):
        """Test satisfying a boolean requirement."""
        self._inject_class_data({"Command": True})
        
        bridge = self._create_mock_component("bridge_id", "Bridge", {"Command": True}, 50, 50, "Bridge")
        bridge.is_active = True
        
        self.ship.layers[LayerType.CORE]['components'] = [bridge]
        self.ship.update_derelict_status()
        
        self.assertFalse(self.ship.is_derelict, "Should function with Command ability")

    def test_numeric_threshold_requirement(self):
        """Test numeric requirement (e.g. PowerOutput > 100)."""
        self._inject_class_data({"Power": 100})
        
        # 1. Underpowered
        gen_small = self._create_mock_component("gen_s", "Small Gen", {"Power": 50}, 10, 10, "Generator")
        gen_small.is_active = True
        
        self.ship.layers[LayerType.CORE]['components'] = [gen_small]
        self.ship.update_derelict_status()
        self.assertTrue(self.ship.is_derelict, "50 Power < 100 Req -> Derelict")
        
        # 2. Sufficient
        gen_large = self._create_mock_component("gen_l", "Large Gen", {"Power": 60}, 10, 10, "Generator")
        gen_large.is_active = True
        
        self.ship.layers[LayerType.CORE]['components'].append(gen_large)
        self.ship.update_derelict_status()
        self.assertFalse(self.ship.is_derelict, "110 Power > 100 Req -> Operational")

    def test_multiple_requirements_all_or_nothing(self):
        """Verify all requirements must be met."""
        self._inject_class_data({"Command": True, "LifeSupport": True})
        
        bridge = self._create_mock_component("bridge", "Bridge", {"Command": True}, 10, 10, "Bridge")
        bridge.is_active = True
        
        # Only Bridge
        self.ship.layers[LayerType.CORE]['components'] = [bridge]
        self.ship.update_derelict_status()
        self.assertTrue(self.ship.is_derelict, "Missing LifeSupport")
        
        # Add Life Support
        ls = self._create_mock_component("ls", "LifeSupport", {"LifeSupport": True}, 10, 10, "LifeSupport")
        ls.is_active = True
        
        self.ship.layers[LayerType.CORE]['components'].append(ls)
        self.ship.update_derelict_status()
        self.assertFalse(self.ship.is_derelict, "All met")

    def test_modifier_granted_requirement(self):
        """Verify abilities granted by Modifiers satisfy requirements."""
        self._inject_class_data({"AdvancedSensors": True})
        
        # Basic sensor (no advanced ability)
        sensor = self._create_mock_component("sensor", "Sensor", {"StandardSensors": True}, 10, 10, "Sensor")
        sensor.is_active = True
        
        self.ship.layers[LayerType.CORE]['components'] = [sensor]
        self.ship.update_derelict_status()
        self.assertTrue(self.ship.is_derelict, "Initially missing AdvancedSensors")
        
        # Apply Modifier 'AdvancedSuite' manually to abilities
        # In real engine, modifier logic would add this via create_modifier or similar context
        # Here we verify that if the component HAS the ability (via modifier), it works.
        sensor.abilities["AdvancedSensors"] = True
        
        self.ship.update_derelict_status()
        self.assertFalse(self.ship.is_derelict, "Modifier-granted ability should satisfy req")

    def test_runtime_derelict_update(self):
        """Verify status updates when components are destroyed/repaired."""
        self._inject_class_data({"Engine": True})
        
        engine = self._create_mock_component("eng", "Engine", {"Engine": True}, 10, 10, "Engine")
        engine.is_active = True
        
        self.ship.layers[LayerType.CORE]['components'] = [engine]
        self.ship.update_derelict_status()
        self.assertFalse(self.ship.is_derelict)
        
        # Destroy Engine
        engine.current_hp = 0
        # self.ship.update_derelict_status() checks for current_hp > 0
        self.ship.update_derelict_status() 
        self.assertTrue(self.ship.is_derelict, "Destroyed engine -> Derelict")
        
        # Repair
        engine.current_hp = 5
        self.ship.update_derelict_status()
        self.assertFalse(self.ship.is_derelict, "Repaired engine -> Operational")

if __name__ == '__main__':
    unittest.main()
