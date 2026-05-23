"""
Tests for ShipComponentManager DI compliance (PROJ-252 Phase 3).

Verifies that ShipComponentManager and ShipValidatorHelper do NOT use
get_default_registry_provider() and instead use Ship's existing registries.
"""
import importlib

import pytest


class TestShipComponentManagerDI:
    """ShipComponentManager should use Ship's registries, not the global provider."""

    @pytest.mark.parametrize(
        "module_name",
        [
            "game.simulation.entities.ship_component_manager",
            "game.simulation.entities.ship_validator_helper",
        ],
        ids=["component_manager", "validator_helper"],
    )
    def test_no_global_registry_import(self, module_name):
        """Module should not import get_default_registry_provider."""
        source = importlib.util.find_spec(module_name)
        with open(source.origin, 'r') as f:
            content = f.read()
        assert 'get_default_registry_provider' not in content
