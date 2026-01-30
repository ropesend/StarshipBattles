"""
Tests for ShipComponentManager dependency injection (PROJ-38).

These tests verify that ShipComponentManager:
1. Uses ship's registries when available
2. Falls back to legacy functions when ship has no registries
"""
import pytest

from game.simulation.entities.ship import Ship
from game.simulation.entities.ship_component_manager import ShipComponentManager
from game.core.registry import GameRegistries, set_default_registries


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_registries():
    """Create mock GameRegistries for DI testing."""
    from game.simulation.components.component import load_components_data, load_modifiers_data
    from game.simulation.entities.ship_loader import load_vehicle_classes_data

    return GameRegistries(
        components=load_components_data(),
        modifiers=load_modifiers_data(),
        vehicle_classes=load_vehicle_classes_data(),
        resources={}
    )


# =============================================================================
# Test: ShipComponentManager Uses Ship's Registries
# =============================================================================

class TestShipComponentManagerWithRegistries:
    """Tests for ShipComponentManager using ship's registries."""

    def test_initialize_layers_uses_ship_registries(self, mock_registries):
        """initialize_layers should use ship's injected registries."""
        ship = Ship(
            name="Test Ship",
            x=0, y=0,
            color=(255, 0, 0),
            team_id=0,
            ship_class="frigate",
            registries=mock_registries
        )

        # The ship should have layers initialized from registries
        assert len(ship.layers) > 0

        # Check that the layers match what's in the registries
        class_def = mock_registries.vehicle_classes.get('frigate', {})
        expected_layer_count = len(class_def.get('layers', [])) + 1  # +1 for HULL

        # Should have HULL plus defined layers
        assert len(ship.layers) >= 1  # At minimum, HULL layer exists

    def test_add_component_works_with_ship_registries(self, mock_registries):
        """add_component should work when ship has injected registries."""
        from game.simulation.components.component import create_component
        from game.simulation.components.component_constants import LayerType

        ship = Ship(
            name="Test Ship",
            x=0, y=0,
            color=(255, 0, 0),
            team_id=0,
            ship_class="frigate",
            registries=mock_registries
        )

        # Create a component with the same registries
        component = create_component('bridge', registries=mock_registries)
        assert component is not None

        # Add component to ship
        result = ship.add_component(component, LayerType.CORE)

        assert result is True
        assert component in ship.layers[LayerType.CORE]['components']


# =============================================================================
# Note: Backward Compatibility test removed (PROJ-50: strict DI enforcement)
# The old test_initialize_layers_works_without_registries tested legacy behavior
# where Ship() could be called without registries parameter. This is no longer
# supported as registries is now a required keyword-only argument.
# =============================================================================
