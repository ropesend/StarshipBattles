import unittest
from components import Component
from resources import ResourceConsumption, ABILITY_REGISTRY, ResourceState, ResourceRegistry

class MockShip:
    def __init__(self):
        self.resources = ResourceRegistry()

class TestComponentShim(unittest.TestCase):
    def test_fuel_shim(self):
        data = {
            "id": "test_engine",
            "name": "Test Engine",
            "type": "Engine",
            "mass": 10,
            "hp": 100,
            "fuel_cost": 5.0
        }
        c = Component(data)
        
        # Check if ResourceConsumption ability was created
        self.assertTrue(len(c.ability_instances) > 0)
        
        found = False
        for ab in c.ability_instances:
            if isinstance(ab, ResourceConsumption):
                if ab.resource_name == 'fuel' and ab.amount == 5.0 and ab.trigger == 'constant':
                    found = True
        self.assertTrue(found, "Fuel Cost shim failed")

    def test_energy_activation_shim(self):
        data = {
            "id": "test_laser",
            "name": "Laser",
            "type": "Weapon",
            "mass": 10,
            "hp": 100,
            "energy_cost": 10.0
        }
        c = Component(data)
        
        found = False
        for ab in c.ability_instances:
            if isinstance(ab, ResourceConsumption):
                if ab.resource_name == 'energy' and ab.amount == 10.0 and ab.trigger == 'activation':
                    found = True
        self.assertTrue(found, "Energy Activation shim failed")

class TestComponentOperation(unittest.TestCase):
    def test_operational_status(self):
        data = {
            "id": "test_engine",
            "name": "Test Engine",
            "type": "Engine",
            "mass": 10,
            "hp": 100,
            "fuel_cost": 10.0 # Constant drain
        }
        c = Component(data)
        ship = MockShip()
        ship.resources.register_storage("fuel", 100)
        ship.resources.get_resource("fuel").current_value = 20.000001
        c.ship = ship
        
        # Update 1 second -> consumes 10
        # 1 sec = 100 ticks
        for _ in range(100):
            c.update()
        self.assertTrue(c.is_operational, f"Component disabled! Fuel: {ship.resources.get_resource('fuel').current_value}")
        self.assertAlmostEqual(ship.resources.get_resource("fuel").current_value, 10, places=5)
        
        # Update 1 second -> consumes 10 -> empty
        for _ in range(100):
            c.update()
        self.assertTrue(c.is_operational)
        self.assertAlmostEqual(ship.resources.get_resource("fuel").current_value, 0, places=5)
        
        # Update 1 second -> consumes 0 (empty) -> Fails
        for _ in range(100):
            c.update()
        self.assertFalse(c.is_operational)

if __name__ == '__main__':
    unittest.main()
