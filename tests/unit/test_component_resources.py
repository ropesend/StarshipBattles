import unittest
from game.simulation.components.component import Component
from game.simulation.systems.resource_manager import ResourceConsumption, ABILITY_REGISTRY, ResourceState, ResourceRegistry

class MockShip:
    def __init__(self):
        self.resources = ResourceRegistry()

class TestComponentCapabilities(unittest.TestCase):
    def test_fuel_ability(self):
        # TEST REFACTOR: Using strict ability definition instead of legacy 'fuel_cost'
        data = {
            "id": "test_engine",
            "name": "Test Engine",
            "type": "Engine",
            "mass": 10,
            "hp": 100,
            "abilities": {
                "ResourceConsumption": [
                    {"resource": "fuel", "amount": 5.0, "trigger": "constant"}
                ]
            }
        }
        c = Component(data)
        
        # Check if ResourceConsumption ability was created
        self.assertTrue(len(c.ability_instances) > 0)
        
        found = False
        for ab in c.ability_instances:
            if isinstance(ab, ResourceConsumption):
                if ab.resource_name == 'fuel' and ab.amount == 5.0 and ab.trigger == 'constant':
                    found = True
        self.assertTrue(found, "Fuel Ability failed to instantiate")

    def test_storage_capacity_modifier(self):
        # TEST COMPONENT MODIFIER SCALING for ResourceStorage
        data = {
            "id": "test_tank",
            "name": "Test Tank",
            "type": "Tank",
            "mass": 10,
            "hp": 100,
            "abilities": {
                "ResourceStorage": [
                    {"resource": "fuel", "amount": 100.0}
                ]
            }
        }
        c = Component(data)
        
        # Initial Check
        from game.simulation.systems.resource_manager import ResourceStorage
        storage = next((ab for ab in c.ability_instances if isinstance(ab, ResourceStorage)), None)
        self.assertIsNotNone(storage)
        self.assertEqual(storage.max_amount, 100.0)
        
        # Apply Modifier (Simulate 'capacity_mult')
        # We need a defined modifier. Let's manually inject one or rely on mocking if needed.
        # But for unit test helper 'add_modifier' needs registry. 
        # Alternatively, we can mock the modifier logic or register a temp one.
        # Easiest: Manually trigger _apply_base_stats with a crafted stats dict for unit testing internal logic.
        
        stats = {
            'mass_mult': 1.0, 'hp_mult': 1.0, 'damage_mult': 1.0, 'range_mult': 1.0,
            'cost_mult': 1.0, 'thrust_mult': 1.0, 'turn_mult': 1.0, 'energy_gen_mult': 1.0,
            'capacity_mult': 2.0, # The key modifier
            'crew_capacity_mult': 1.0, 'life_support_capacity_mult': 1.0,
            'consumption_mult': 1.0, 'mass_add': 0.0, 'arc_add': 0.0, 'accuracy_add': 0.0,
            'arc_set': None, 'properties': {}, 'reload_mult': 1.0, 'endurance_mult': 1.0,
            'projectile_hp_mult': 1.0, 'projectile_damage_mult': 1.0, 'projectile_stealth_level': 0.0,
            'crew_req_mult': 1.0
        }
        
        # We can call _apply_base_stats directly to verifying the logic handles mapping stats -> ability
        c._apply_base_stats(stats, old_max_hp=100)
        
        self.assertEqual(storage.max_amount, 200.0, "Capacity modifier failed to scale ResourceStorage ability")

    def test_energy_activation_ability(self):
        # TEST REFACTOR: Using strict ability definition
        data = {
            "id": "test_laser",
            "name": "Laser",
            "type": "Weapon",
            "mass": 10,
            "hp": 100,
            "abilities": {
                "ResourceConsumption": [
                    {"resource": "energy", "amount": 10.0, "trigger": "activation"}
                ]
            }
        }
        c = Component(data)
        
        found = False
        for ab in c.ability_instances:
            if isinstance(ab, ResourceConsumption):
                if ab.resource_name == 'energy' and ab.amount == 10.0 and ab.trigger == 'activation':
                    found = True
        self.assertTrue(found, "Energy Activation ability failed to instantiate")

class TestComponentOperation(unittest.TestCase):
    def test_operational_status(self):
        # TEST REFACTOR: Using strict ability definition
        data = {
            "id": "test_engine",
            "name": "Test Engine",
            "type": "Engine",
            "mass": 10,
            "hp": 100,
            "abilities": {
                "ResourceConsumption": [
                    {"resource": "fuel", "amount": 10.0, "trigger": "constant"}
                ]
            }
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
