"""
Tests for ShipComponentManager DI compliance (PROJ-252 Phase 3).

Verifies that ShipComponentManager and ShipValidatorHelper do NOT use
get_default_registry_provider() and instead use Ship's existing registries.
"""
import importlib


class TestShipComponentManagerDI:
    """ShipComponentManager should use Ship's registries, not the global provider."""

    def test_no_global_registry_import_in_component_manager(self):
        """ship_component_manager module should not import get_default_registry_provider."""
        source = importlib.util.find_spec(
            'game.simulation.entities.ship_component_manager'
        )
        with open(source.origin, 'r') as f:
            content = f.read()
        assert 'get_default_registry_provider' not in content

    def test_no_global_registry_import_in_validator_helper(self):
        """ship_validator_helper module should not import get_default_registry_provider."""
        source = importlib.util.find_spec(
            'game.simulation.entities.ship_validator_helper'
        )
        with open(source.origin, 'r') as f:
            content = f.read()
        assert 'get_default_registry_provider' not in content
