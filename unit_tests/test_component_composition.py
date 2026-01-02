
import unittest
from unittest.mock import MagicMock
from components import Component
from abilities import CombatPropulsion, ResourceConsumption, WeaponAbility

class TestComponentComposition(unittest.TestCase):
    def setUp(self):
        self.mock_ship = MagicMock()
        self.mock_resources = MagicMock()
        self.mock_ship.resources = self.mock_resources

    
    def test_generic_engine_construction(self):
        # A generic component that acts as an engine via composition
        data = {
            "id": "gen_eng_1",
            "name": "Generic Engine",
            "type": "Generic",
            "mass": 100,
            "hp": 50,
            "abilities": {
                "CombatPropulsion": 1000,
                # Use explicit dict to ensure constant trigger for testing idle consumption
                "ResourceConsumption": {"resource": "energy", "amount": 10, "trigger": "constant"}
            }
        }
        
        comp = Component(data)
        comp.ship = self.mock_ship
        
        # Verify Abilities exist
        self.assertTrue(comp.has_ability("CombatPropulsion"))
        self.assertTrue(comp.has_ability("ResourceConsumption"))
        
        # Verify Attributes via helper
        prop = comp.get_ability("CombatPropulsion")
        self.assertEqual(prop.thrust_force, 1000)
        
        # Test Operation (Resource Consumption)
        # Mock resource
        mock_energy = MagicMock()
        mock_energy.consume.return_value = True
        self.mock_resources.get_resource.return_value = mock_energy
        
        comp.update()
        self.assertTrue(comp.is_operational)
        
        # Test Starvation
        mock_energy.consume.return_value = False
        comp.update()
        self.assertFalse(comp.is_operational, "Component should be non-operational if constant resource consumption fails")

    def test_generic_weapon_composition(self):
        data = {
            "id": "gen_wep_1",
            "name": "Generic Gun",
            "type": "Generic",
            "mass": 50, # Added mass
            "hp": 20,
            "abilities": {
                "ProjectileWeaponAbility": {
                    "damage": 50,
                    "range": 1000,
                    "reload": 2.0
                }
            }
        }
        
        comp = Component(data)
        
        wep = comp.get_ability("WeaponAbility") # Polymorphic lookup
        self.assertIsNotNone(wep)
        self.assertEqual(wep.damage, 50)
        self.assertEqual(wep.reload_time, 2.0)
        
        # Verify we can also find it by specific type
        proj = comp.get_ability("ProjectileWeaponAbility")
        self.assertIsNotNone(proj)
        self.assertEqual(proj, wep)
