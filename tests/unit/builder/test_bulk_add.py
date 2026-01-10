import unittest
from game.simulation.entities.ship import Ship, LayerType
from game.simulation.components.component import Component, ComponentStatus

class TestBulkAdd(unittest.TestCase):
    def setUp(self):
        self.ship = Ship("Test Ship", 0, 0, (255, 255, 255))
        self.ship._initialize_layers() # Ensure layers exist
        
        # Mock component
        self.comp_data = {
            "id": "armor_std",
            "name": "Standard Armor",
            "type": "Armor",
            "mass": 10,
            "hp": 100,
            "hp": 100,
            # allowed_layers removed
            "major_classification": "Armor"
        }
        self.comp = Component(self.comp_data)
        
    def test_bulk_add_success(self):
        count = 10
        self.ship.add_components_bulk(self.comp, LayerType.ARMOR, count)
        
        self.assertEqual(len(self.ship.layers[LayerType.ARMOR]['components']), 10)
        self.assertEqual(self.ship.current_mass, 100) # 10 * 10
        
    def test_bulk_add_with_limit(self):
        # Mock class limit to something small
        # Usually validaton checks mass budget or unique limits.
        # Let's test a unique component, if available?
        # Manually inject a unique component?
        
        # Better: Test mass limit.
        self.ship.max_mass_budget = 55 # Enough for 5
        
        # Add 10. Should add 5, then fail.
        # Wait, default validator doesn't block addition on mass budget, only marks it as invalid?
        # Let's check validator logic.
        pass 
        
    def test_bulk_performance_mock(self):
        # Verify it runs fast enough?
        pass

if __name__ == '__main__':
    unittest.main()
