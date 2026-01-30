"""
Test to catch regressions in the layer restriction refactor.
Specifically tests that:
1. Components no longer have the deprecated `allowed_layers` attribute
2. Builder drop logic works without relying on that attribute
"""
import pytest

from game.simulation.components.component import Component
from game.simulation.entities.ship import Ship, LayerType


@pytest.fixture
def cruiser_ship(fresh_registries):
    """Create a Cruiser ship for testing."""
    return Ship("TestShip", 0, 0, (255, 255, 255), 0, ship_class="Cruiser", registries=fresh_registries)


class TestAllowedLayersRemoval:
    """
    Ensure the deprecated `allowed_layers` attribute has been fully removed
    from all component classes to prevent AttributeError crashes.
    """

    def test_component_base_class_no_allowed_layers(self, fresh_registries):
        """Base Component class should not define allowed_layers."""
        # Create a minimal component with required fields
        comp = Component({
            'id': 'test',
            'name': 'Test',
            'type': 'TestType',
            'mass': 10,
            'hp': 10
        }, registries=fresh_registries)
        assert not hasattr(comp, 'allowed_layers'), \
            "Component base class should not have 'allowed_layers' attribute"

    def test_bridge_no_allowed_layers(self, fresh_registries):
        """Bridge component should not have allowed_layers."""
        comps = fresh_registries.components
        if 'bridge' in comps:
            bridge = comps['bridge'].clone()
            assert not hasattr(bridge, 'allowed_layers'), \
                "Bridge should not have 'allowed_layers' attribute"

    def test_engine_no_allowed_layers(self, fresh_registries):
        """Engine component should not have allowed_layers."""
        comps = fresh_registries.components
        if 'standard_engine' in comps:
            engine = comps['standard_engine'].clone()
            assert not hasattr(engine, 'allowed_layers'), \
                "Engine should not have 'allowed_layers' attribute"

    def test_armor_no_allowed_layers(self, fresh_registries):
        """Armor component should not have allowed_layers."""
        comps = fresh_registries.components
        if 'basic_armor' in comps:
            armor = comps['basic_armor'].clone()
            assert not hasattr(armor, 'allowed_layers'), \
                "Armor should not have 'allowed_layers' attribute"

    def test_all_registry_components_no_allowed_layers(self, fresh_registries):
        """
        Comprehensive check: ALL components in the registry must not have allowed_layers.
        This prevents any component from causing an AttributeError when dropped in the builder.
        """
        for comp_id, comp in fresh_registries.components.items():
            cloned = comp.clone()
            assert not hasattr(cloned, 'allowed_layers'), \
                f"Component '{comp_id}' should not have 'allowed_layers' attribute"


class TestBuilderDropValidation:
    """
    Test that component placement validation works correctly through the
    centralized validator, not through a per-component allowed_layers check.
    """

    def test_validator_handles_component_placement(self, cruiser_ship, fresh_registries):
        """Validator should handle layer checks without allowed_layers."""
        from game.simulation.entities.ship_loader import get_or_create_validator

        comps = fresh_registries.components
        if 'bridge' not in comps:
            pytest.skip("No bridge in registry")
        bridge = comps['bridge'].clone()

        # Validate should work without AttributeError
        result = get_or_create_validator().validate_addition(cruiser_ship, bridge, LayerType.CORE)

        # Result should be a ValidationResult object
        assert hasattr(result, 'is_valid')
        assert hasattr(result, 'errors')

    def test_weapon_blocked_in_core_layer(self, cruiser_ship, fresh_registries):
        """Weapon should be blocked in CORE layer via vehiclelayers.json rules."""
        from game.simulation.entities.ship_loader import get_or_create_validator

        # Find any weapon component in registry
        weapon_id = None
        comps = fresh_registries.components
        for comp_id, comp in comps.items():
            if getattr(comp, 'major_classification', None) == 'Weapons':
                weapon_id = comp_id
                break

        if not weapon_id:
            pytest.skip("No weapon component in registry")

        weapon = comps[weapon_id].clone()

        # Try to place weapon in CORE (should be blocked by block_classification:Weapons rule)
        result = get_or_create_validator().validate_addition(cruiser_ship, weapon, LayerType.CORE)

        # Weapon should fail validation in CORE
        assert not result.is_valid, "Weapon should not be allowed in CORE layer"

    def test_armor_allowed_in_armor_layer(self, cruiser_ship, fresh_registries):
        """Armor should be allowed in ARMOR layer."""
        from game.simulation.entities.ship_loader import get_or_create_validator

        # Find any armor component in registry
        armor_id = None
        for comp_id, comp in fresh_registries.components.items():
            if getattr(comp, 'major_classification', None) == 'Armor':
                armor_id = comp_id
                break

        if not armor_id:
            pytest.skip("No armor component in registry")

        armor = fresh_registries.components[armor_id].clone()

        result = get_or_create_validator().validate_addition(cruiser_ship, armor, LayerType.ARMOR)

        assert result.is_valid, f"Armor should be allowed in ARMOR layer. Errors: {result.errors}"
