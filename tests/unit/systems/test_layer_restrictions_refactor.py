import unittest
from unittest.mock import MagicMock
from ship_validator import LayerRestrictionDefinitionRule, ValidationResult
from game.simulation.components.component import Component, LayerType

class TestLayerRestrictionsRefactor(unittest.TestCase):
    def setUp(self):
        self.rule = LayerRestrictionDefinitionRule()
        self.ship = MagicMock()
        self.ship.layers = {
            LayerType.CORE: {
                'restrictions': ["block_classification:Weapons"]
            },
            LayerType.ARMOR: {
                'restrictions': ["allow_classification:Armor"]
            },
            LayerType.INNER: {
                'restrictions': [] # No restrictions
            }
        }

    def create_mock_component(self, comp_id, classification, type_str):
        comp = MagicMock(spec=Component)
        comp.id = comp_id
        comp.data = {'major_classification': classification}
        comp.type_str = type_str
        return comp

    def test_block_classification(self):
        # CORE blocks Weapons
        weapon = self.create_mock_component("gun", "Weapons", "ProjectileWeapon")
        result = self.rule.validate(self.ship, weapon, LayerType.CORE)
        self.assertFalse(result.is_valid)
        self.assertIn("Classification 'Weapons' blocked", result.errors[0])
        
        # CORE should allow Engines (if not blocked) - checking partial block
        engine = self.create_mock_component("eng", "Engines", "Engine")
        result = self.rule.validate(self.ship, engine, LayerType.CORE)
        self.assertTrue(result.is_valid)

    def test_allow_classification_only(self):
        # ARMOR layer allows ONLY Armor
        armor = self.create_mock_component("plate", "Armor", "Armor")
        result = self.rule.validate(self.ship, armor, LayerType.ARMOR)
        self.assertTrue(result.is_valid)
        
        # Should reject weapon
        weapon = self.create_mock_component("gun", "Weapons", "ProjectileWeapon")
        result = self.rule.validate(self.ship, weapon, LayerType.ARMOR)
        self.assertFalse(result.is_valid)
        self.assertIn("Layer restricts components", result.errors[0])

    def test_no_restrictions(self):
        # INNER has no restrictions -> Allow All
        weapon = self.create_mock_component("gun", "Weapons", "ProjectileWeapon")
        result = self.rule.validate(self.ship, weapon, LayerType.INNER)
        self.assertTrue(result.is_valid)

if __name__ == '__main__':
    unittest.main()
