"""
Test to catch regressions in the layer restriction refactor.
Specifically tests that:
1. Components no longer have the deprecated `allowed_layers` attribute
2. Builder drop logic works without relying on that attribute
"""
import unittest

from game.simulation.components.component import Component, load_components
from game.core.registry import RegistryManager
from game.simulation.entities.ship import Ship, LayerType, initialize_ship_data


class TestAllowedLayersRemoval(unittest.TestCase):
    """
    Ensure the deprecated `allowed_layers` attribute has been fully removed
    from all component classes to prevent AttributeError crashes.
    """
    
    def setUp(self):
        initialize_ship_data()
        load_components()

    def tearDown(self) -> None:
        """Clear the global registry state."""
        RegistryManager.instance().clear()
    
    def test_component_base_class_no_allowed_layers(self):
        """Base Component class should not define allowed_layers."""
        # Create a minimal component with required fields
        comp = Component({
            'id': 'test', 
            'name': 'Test', 
            'type': 'TestType',
            'mass': 10, 
            'hp': 10
        })
        self.assertFalse(
            hasattr(comp, 'allowed_layers'),
            "Component base class should not have 'allowed_layers' attribute"
        )
    
    def test_bridge_no_allowed_layers(self):
        """Bridge component should not have allowed_layers."""
        comps = RegistryManager.instance().components
        if 'bridge' in comps:
            bridge = comps['bridge'].clone()
            self.assertFalse(
                hasattr(bridge, 'allowed_layers'),
                "Bridge should not have 'allowed_layers' attribute"
            )
    
    def test_engine_no_allowed_layers(self):
        """Engine component should not have allowed_layers."""
        comps = RegistryManager.instance().components
        if 'standard_engine' in comps:
            engine = comps['standard_engine'].clone()
            self.assertFalse(
                hasattr(engine, 'allowed_layers'),
                "Engine should not have 'allowed_layers' attribute"
            )
    
    def test_armor_no_allowed_layers(self):
        """Armor component should not have allowed_layers."""
        comps = RegistryManager.instance().components
        if 'basic_armor' in comps:
            armor = comps['basic_armor'].clone()
            self.assertFalse(
                hasattr(armor, 'allowed_layers'),
                "Armor should not have 'allowed_layers' attribute"
            )
    
    def test_all_registry_components_no_allowed_layers(self):
        """
        Comprehensive check: ALL components in the registry must not have allowed_layers.
        This prevents any component from causing an AttributeError when dropped in the builder.
        """
        for comp_id, comp in RegistryManager.instance().components.items():
            cloned = comp.clone()
            self.assertFalse(
                hasattr(cloned, 'allowed_layers'),
                f"Component '{comp_id}' should not have 'allowed_layers' attribute"
            )


class TestBuilderDropValidation(unittest.TestCase):
    """
    Test that component placement validation works correctly through the
    centralized validator, not through a per-component allowed_layers check.
    """
    
    
    def setUp(self):
        initialize_ship_data()
        load_components()
        self.ship = Ship("TestShip", 0, 0, (255, 255, 255), 0, ship_class="Cruiser")

    def tearDown(self) -> None:
        """Clear the global registry state."""
        RegistryManager.instance().clear()
    
    def test_validator_handles_component_placement(self):
        """Validator should handle layer checks without allowed_layers."""
        from game.simulation.entities.ship import get_or_create_validator
        
        comps = RegistryManager.instance().components
        if 'bridge' not in comps:
            self.skipTest("No bridge in registry")
        bridge = comps['bridge'].clone()
        
        # Validate should work without AttributeError
        result = get_or_create_validator().validate_addition(self.ship, bridge, LayerType.CORE)
        
        # Result should be a ValidationResult object
        self.assertTrue(hasattr(result, 'is_valid'))
        self.assertTrue(hasattr(result, 'errors'))
    
    def test_weapon_blocked_in_core_layer(self):
        """Weapon should be blocked in CORE layer via vehiclelayers.json rules."""
        from game.simulation.entities.ship import get_or_create_validator
        
        # Find any weapon component in registry
        weapon_id = None
        comps = RegistryManager.instance().components
        for comp_id, comp in comps.items():
            if getattr(comp, 'major_classification', None) == 'Weapons':
                weapon_id = comp_id
                break
        
        if not weapon_id:
            self.skipTest("No weapon component in registry")
        
        weapon = comps[weapon_id].clone()
        
        # Try to place weapon in CORE (should be blocked by block_classification:Weapons rule)
        result = get_or_create_validator().validate_addition(self.ship, weapon, LayerType.CORE)
        
        # Weapon should fail validation in CORE
        self.assertFalse(
            result.is_valid,
            "Weapon should not be allowed in CORE layer"
        )
    
    def test_armor_allowed_in_armor_layer(self):
        """Armor should be allowed in ARMOR layer."""
        from game.simulation.entities.ship import get_or_create_validator
        
        # Find any armor component in registry
        armor_id = None
        for comp_id, comp in RegistryManager.instance().components.items():
            if getattr(comp, 'major_classification', None) == 'Armor':
                armor_id = comp_id
                break
        
        if not armor_id:
            self.skipTest("No armor component in registry")
        
        armor = RegistryManager.instance().components[armor_id].clone()
        
        result = get_or_create_validator().validate_addition(self.ship, armor, LayerType.ARMOR)
        
        self.assertTrue(
            result.is_valid,
            f"Armor should be allowed in ARMOR layer. Errors: {result.errors}"
        )


if __name__ == '__main__':
    unittest.main()
