import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from components import Component, Modifier, MODIFIER_REGISTRY
from ui.builder.modifier_logic import ModifierLogic

class TestMandatoryUpdates(unittest.TestCase):

    def setUp(self):
        # Setup Mock Registry with necessary mods
        self.test_registry = {
            'simple_size_mount': Modifier({'id': 'simple_size_mount', 'name': 'Size', 'type': 'linear', 'min_val': 1, 'max_val': 100}),
            'range_mount': Modifier({'id': 'range_mount', 'name': 'Range', 'type': 'linear', 'min_val': 0, 'max_val': 10, 'restrictions': {'allow_types': ['ProjectileWeapon']}}),
            'facing': Modifier({'id': 'facing', 'name': 'Facing', 'type': 'linear', 'min_val': 0, 'max_val': 360}),
            'turret_mount': Modifier({'id': 'turret_mount', 'name': 'Turret', 'type': 'linear', 'min_val': 0, 'max_val': 360}),
            'rapid_fire': Modifier({'id': 'rapid_fire', 'name': 'Rapid Fire', 'type': 'linear', 'min_val': 1, 'max_val': 10, 'restrictions': {'allow_types': ['Weapon', 'ProjectileWeapon', 'BeamWeapon', 'SeekerWeapon']}}),
            'automation': Modifier({'id': 'automation', 'name': 'Automation', 'type': 'linear', 'min_val': 0, 'max_val': 0.99, 'restrictions': {'allow_abilities': ['CrewRequired']}}),
            'seeker_endurance': Modifier({'id': 'seeker_endurance', 'name': 'Endurance', 'type': 'linear', 'min_val': 1, 'max_val': 10, 'restrictions': {'allow_types': ['SeekerWeapon']}}),
            # Add others if needed
        }

    def test_automation_mandatory(self):
        # Mock Component with CrewRequired
        comp_data = {'id': 'test', 'name': 'Test', 'type': 'Weapon', 'hp':10, 'mass':10, 'abilities': {'CrewRequired': 5}}
        comp = Component(comp_data)
        
        with patch.dict(MODIFIER_REGISTRY, self.test_registry, clear=True):
            mandatory = ModifierLogic.get_mandatory_modifiers(comp)
            
            self.assertIn('automation', mandatory)
            self.assertIn('rapid_fire', mandatory) # Weapon
            self.assertIn('simple_size_mount', mandatory)

    def test_automation_not_mandatory_no_crew(self):
        # Mock Component without CrewRequired
        comp_data = {'id': 'test', 'name': 'Test', 'type': 'Weapon', 'hp':10, 'mass':10, 'abilities': {}}
        comp = Component(comp_data)
        
        with patch.dict(MODIFIER_REGISTRY, self.test_registry, clear=True):
            mandatory = ModifierLogic.get_mandatory_modifiers(comp)
            
            self.assertNotIn('automation', mandatory)
            self.assertIn('rapid_fire', mandatory)

    def test_seeker_mandatory(self):
        comp_data = {'id': 'seeker', 'name': 'Seeker', 'type': 'SeekerWeapon', 'hp':10, 'mass':10}
        comp = Component(comp_data)
        
        with patch.dict(MODIFIER_REGISTRY, self.test_registry, clear=True):
            mandatory = ModifierLogic.get_mandatory_modifiers(comp)
            
            self.assertIn('seeker_endurance', mandatory)
            self.assertIn('rapid_fire', mandatory)
            # Should NOT have range_mount if registry restricts it (mock registry restricts to ProjectileWeapon)
            self.assertNotIn('range_mount', mandatory) 

if __name__ == '__main__':
    unittest.main()
