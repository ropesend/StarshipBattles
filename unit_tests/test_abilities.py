
import unittest
from unittest.mock import MagicMock
from abilities import (
    create_ability, 
    Ability, 
    ResourceConsumption, 
    ResourceStorage, 
    CombatPropulsion, 
    ManeuveringThruster, 
    WeaponAbility, 
    ProjectileWeaponAbility,
    VehicleLaunchAbility
)

class TestAbilities(unittest.TestCase):
    def setUp(self):
        self.mock_component = MagicMock()
        self.mock_ship = MagicMock()
        self.mock_component.ship = self.mock_ship
        self.mock_resources = MagicMock()
        self.mock_ship.resources = self.mock_resources

    def test_create_ability_primitives(self):
        # Test creation from primitive shortcuts
        ab = create_ability("CombatPropulsion", self.mock_component, 1500)
        self.assertIsInstance(ab, CombatPropulsion)
        self.assertEqual(ab.thrust_force, 1500)

        ab = create_ability("FuelStorage", self.mock_component, 2000)
        self.assertIsInstance(ab, ResourceStorage)
        self.assertEqual(ab.resource_type, "fuel")
        self.assertEqual(ab.max_amount, 2000)

    def test_create_ability_dict(self):
        # Test creation from dict
        data = {"value": 50, "tags": ["test"]}
        ab = create_ability("ManeuveringThruster", self.mock_component, data)
        self.assertIsInstance(ab, ManeuveringThruster)
        self.assertEqual(ab.turn_rate, 50)
        self.assertIn("test", ab.tags)

    def test_resource_consumption_constant(self):
        # Test constant consumption update
        data = {"resource": "fuel", "amount": 10, "trigger": "constant"}
        ab = ResourceConsumption(self.mock_component, data)
        
        # Setup mock resource
        mock_fuel = MagicMock()
        mock_fuel.consume.return_value = True
        self.mock_resources.get_resource.return_value = mock_fuel
        
        # Update (tick)
        result = ab.update()
        self.assertTrue(result)
        # Should consume amount * 0.01
        mock_fuel.consume.assert_called_with(0.1) 

    def test_resource_consumption_activation(self):
        # Test activation trigger
        data = {"resource": "energy", "amount": 5, "trigger": "activation"}
        ab = ResourceConsumption(self.mock_component, data)
        
        # Update shouldn't consume
        ab.update()
        self.mock_resources.get_resource.assert_not_called()
        
        # Manual consumption
        mock_energy = MagicMock()
        mock_energy.consume.return_value = True
        self.mock_resources.get_resource.return_value = mock_energy
        
        success = ab.check_and_consume()
        self.assertTrue(success)
        mock_energy.consume.assert_called_with(5)

    def test_weapon_ability(self):
        data = {
            "damage": 50,
            "range": 1000,
            "cooldown": 2.0, # Not used, uses reload usually or similar
            "reload": 1.5,
            "projectile_speed": 800
        }
        ab = create_ability("ProjectileWeaponAbility", self.mock_component, data)
        self.assertIsInstance(ab, ProjectileWeaponAbility)
        self.assertEqual(ab.damage, 50)
        self.assertIsInstance(ab, WeaponAbility)
        self.assertEqual(ab.projectile_speed, 800)
        
        # Cooldown Logic
        self.assertTrue(ab.can_fire())
        ab.fire(target=None)
        self.assertFalse(ab.can_fire())
        self.assertEqual(ab.cooldown_timer, 1.5)
        
        # Update decrements
        ab.update() # -0.01
        self.assertAlmostEqual(ab.cooldown_timer, 1.49)

    def test_vehicle_launch(self):
        data = {"fighter_class": "Ace Fighter", "cycle_time": 2.0}
        ab = VehicleLaunchAbility(self.mock_component, data)
        
        self.assertTrue(ab.try_launch())
        self.assertFalse(ab.try_launch()) # Cooldown active
        
        # fast forward
        ab.cooldown = 0
        self.assertTrue(ab.try_launch())

    def test_ui_rows(self):
        ab = CombatPropulsion(self.mock_component, 100)
        rows = ab.get_ui_rows()
        self.assertEqual(rows[0]['label'], 'Thrust')
        self.assertEqual(rows[0]['value'], '100 N')

if __name__ == '__main__':
    unittest.main()
