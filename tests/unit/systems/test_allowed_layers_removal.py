"""
Test that builder drop logic works without the deprecated `allowed_layers` attribute.

PROJ-157: Removed TestAllowedLayersRemoval (one-time migration verification).
Kept TestBuilderDropValidation for ongoing centralized validator behavior.
"""
import pytest

from game.simulation.components.component import Component
from game.simulation.entities.ship import Ship, LayerType
from game.core.registry import get_default_registry_provider


@pytest.fixture
def cruiser_ship(fresh_registries):
    """Create a Cruiser ship for testing."""
    return Ship("TestShip", 0, 0, (255, 255, 255), 0, ship_class="Cruiser", registries=fresh_registries)


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

        # PROJ-211: Pass registry_provider explicitly (no fallback)
        provider = get_default_registry_provider()
        result = get_or_create_validator(registry_provider=provider).validate_addition(cruiser_ship, bridge, LayerType.CORE)

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

        # PROJ-211: Pass registry_provider explicitly (no fallback)
        provider = get_default_registry_provider()
        # Try to place weapon in CORE (should be blocked by block_classification:Weapons rule)
        result = get_or_create_validator(registry_provider=provider).validate_addition(cruiser_ship, weapon, LayerType.CORE)

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

        # PROJ-211: Pass registry_provider explicitly (no fallback)
        provider = get_default_registry_provider()
        result = get_or_create_validator(registry_provider=provider).validate_addition(cruiser_ship, armor, LayerType.ARMOR)

        assert result.is_valid, f"Armor should be allowed in ARMOR layer. Errors: {result.errors}"
