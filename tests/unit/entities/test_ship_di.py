"""
Tests for Ship dependency injection (PROJ-38).

These tests verify that Ship:
1. Accepts GameRegistries via constructor
2. Works with injected registries (no global state needed)
3. Has transitional fallback to get_default_registries()
"""
import pytest

from game.simulation.entities.ship import Ship
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
# Test: Ship Constructor with Registries
# =============================================================================

class TestShipConstructor:
    """Tests for Ship constructor with registries injection."""

    def test_accepts_registries_in_constructor(self, mock_registries):
        """Ship should accept GameRegistries in constructor."""
        ship = Ship(
            name="Test Ship",
            x=0, y=0,
            color=(255, 0, 0),
            team_id=0,
            ship_class="frigate",
            registries=mock_registries
        )

        assert hasattr(ship, '_registries')
        assert ship._registries is mock_registries

    def test_constructor_with_none_uses_default(self, mock_registries):
        """Ship with None registries should fall back to default registries."""
        set_default_registries(mock_registries)

        ship = Ship(
            name="Test Ship",
            x=0, y=0,
            color=(255, 0, 0),
            team_id=0,
            ship_class="frigate",
            registries=None
        )

        assert ship._registries is not None

    def test_constructor_without_registries_uses_default(self, mock_registries):
        """Ship without registries arg should fall back to default registries."""
        set_default_registries(mock_registries)

        # Legacy pattern - no registries argument
        ship = Ship(
            name="Test Ship",
            x=0, y=0,
            color=(255, 0, 0),
            team_id=0,
            ship_class="frigate"
        )

        assert ship._registries is not None


# =============================================================================
# Test: Ship Methods Use Injected Registries
# =============================================================================

class TestShipMethodsWithRegistries:
    """Tests for Ship methods using injected registries."""

    def test_initialize_layers_uses_injected_registries(self, mock_registries):
        """_initialize_layers should use injected vehicle_classes registry."""
        ship = Ship(
            name="Test Ship",
            x=0, y=0,
            color=(255, 0, 0),
            team_id=0,
            ship_class="frigate",
            registries=mock_registries
        )

        # Should have layers defined from registry
        assert len(ship.layers) > 0

    def test_add_component_with_injected_registries(self, mock_registries):
        """add_component should work with ship using injected registries."""
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
# Test: Backward Compatibility
# =============================================================================

class TestShipBackwardCompatibility:
    """Tests ensuring backward compatibility with legacy interface."""

    def test_ship_works_without_registries_arg(self):
        """Ship should work without registries argument (legacy pattern)."""
        ship = Ship(
            name="Test Ship",
            x=0, y=0,
            color=(255, 0, 0),
            team_id=0,
            ship_class="frigate"
        )

        assert ship is not None
        assert ship.name == "Test Ship"
        assert ship.ship_class == "frigate"

    def test_add_component_works_without_explicit_registries(self):
        """add_component should work on ship created without explicit registries."""
        from game.simulation.components.component import create_component
        from game.simulation.components.component_constants import LayerType

        ship = Ship(
            name="Test Ship",
            x=0, y=0,
            color=(255, 0, 0),
            team_id=0,
            ship_class="frigate"
        )

        component = create_component('bridge')
        assert component is not None

        result = ship.add_component(component, LayerType.CORE)

        assert result is True
