import unittest
from resources import ResourceState, ResourceRegistry, ResourceConsumption
from collections import namedtuple

# Mock Component/Ship for Ability testing
MockShip = namedtuple('MockShip', ['resources'])
MockComponent = namedtuple('MockComponent', ['ship', 'ability_instances'])

class TestResourceState(unittest.TestCase):
    def test_consume(self):
        r = ResourceState("fuel", max_value=100, current_value=50)
        self.assertTrue(r.consume(10))
        self.assertEqual(r.current_value, 40)
        
        self.assertFalse(r.consume(50)) # Not enough
        self.assertEqual(r.current_value, 40) # Unchanged

    def test_regen(self):
        r = ResourceState("energy", max_value=100, current_value=0, regen_rate=10)
        # With new tick based system, we need to loop or change test expectation.
        # Original test expected 1.0s update. Now 1 tick is 0.01s.
        # r.regen_rate is 10/sec. 0.01s -> 0.1 resource per tick.
        # To get 10 resource, we need 100 ticks.
        for _ in range(100):
             r.update()
        self.assertAlmostEqual(r.current_value, 10.0)
        
        # Update enough to cap
        # 9 more seconds = 900 ticks
        for _ in range(900):
            r.update()
        self.assertAlmostEqual(r.current_value, 100.0)

class TestResourceRegistry(unittest.TestCase):
    def test_registration(self):
        reg = ResourceRegistry()
        reg.register_storage("fuel", 100)
        
        r = reg.get_resource("fuel")
        self.assertIsNotNone(r)
        self.assertEqual(r.max_value, 100)
        
        # Add more storage
        reg.register_storage("fuel", 50)
        self.assertEqual(r.max_value, 150)

    def test_generation_registration(self):
        reg = ResourceRegistry()
        reg.register_generation("energy", 5)
        
        r = reg.get_resource("energy")
        self.assertIsNotNone(r)
        self.assertEqual(r.regen_rate, 5)
        
        reg.register_generation("energy", 10)
        self.assertEqual(r.regen_rate, 15)

class TestAbilities(unittest.TestCase):
    def test_consumption_ability(self):
        reg = ResourceRegistry()
        reg.register_storage("ammo", 10)
        reg.get_resource("ammo").current_value = 10
        
        ship = MockShip(reg)
        comp = MockComponent(ship, [])
        
        # Activation Trigger
        ability = ResourceConsumption(comp, {"resource": "ammo", "amount": 1, "trigger": "activation"})
        
        self.assertTrue(ability.check_and_consume())
        self.assertEqual(reg.get_resource("ammo").current_value, 9)
        
        # Drain
        reg.get_resource("ammo").current_value = 0
        self.assertFalse(ability.check_and_consume())

if __name__ == '__main__':
    unittest.main()
