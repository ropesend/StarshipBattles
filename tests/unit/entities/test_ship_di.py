"""
Tests for Ship dependency injection (PROJ-50).

These tests verify that Ship:
1. Accepts GameRegistries via constructor (required)
2. Raises TypeError when registries is None
3. Works with injected registries for all operations

PROJ-181: Removed _default_registries cleanup - no longer exists.
"""
import pytest

from game.core.exceptions import ValidationException
from game.simulation.entities.ship import Ship
from game.core.registry import GameRegistries


@pytest.fixture
def mock_registries():
    """Create mock GameRegistries for DI testing."""
    from game.simulation.components.component import load_components_data, load_modifiers_data
    from game.simulation.entities.ship_loader import load_vehicle_classes_data

    # PROJ-211: Only load_components_data needs registries
    minimal_registries = GameRegistries(components={}, modifiers={}, vehicle_classes={}, resources={})
    return GameRegistries(
        components=load_components_data(registries=minimal_registries),
        modifiers=load_modifiers_data(),
        vehicle_classes=load_vehicle_classes_data(),
        resources={}
    )


# =============================================================================
# Test: Ship Constructor with Registries (PROJ-50 Strict DI)
# =============================================================================

class TestShipConstructor:
    """Tests for Ship constructor with strict registries injection."""

    def test_constructor_with_none_raises_typeerror(self, mock_registries):
        """Ship with None registries should raise TypeError (PROJ-50 strict DI)."""
        with pytest.raises(ValidationException):
            Ship(
                name="Test Ship",
                x=0, y=0,
                color=(255, 0, 0),
                team_id=0,
                ship_class="frigate",
                registries=None
            )

    def test_constructor_stores_registries(self, mock_registries):
        """Ship constructor should store registries for later use."""
        ship = Ship(
            name="Test Ship",
            x=0, y=0,
            color=(255, 0, 0),
            team_id=0,
            ship_class="frigate",
            registries=mock_registries
        )

        assert ship._registries is mock_registries
        assert ship._registries.vehicle_classes is not None


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
        from game.core.constants import LayerType

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
        assert component in ship.layers[LayerType.CORE].components


# =============================================================================
# Test: Strict DI Enforcement (PROJ-50)
# =============================================================================

class TestStrictDIEnforcement:
    """Tests ensuring strict DI is enforced (no backward compatibility with None)."""

    def test_ship_requires_registries_parameter(self, mock_registries):
        """Ship must receive valid registries (PROJ-50)."""
        # Valid: with registries
        ship = Ship(
            name="Test Ship",
            x=0, y=0,
            color=(255, 0, 0),
            team_id=0,
            ship_class="frigate",
            registries=mock_registries
        )
        assert ship._registries is mock_registries

        # Invalid: with None
        with pytest.raises(ValidationException):
            Ship(
                name="Test Ship",
                x=0, y=0,
                color=(255, 0, 0),
                registries=None
            )

    def test_components_share_registries(self, mock_registries):
        """Components added to ship should use the same registries."""
        from game.simulation.components.component import create_component
        from game.core.constants import LayerType

        ship = Ship(
            name="Test Ship",
            x=0, y=0,
            color=(255, 0, 0),
            team_id=0,
            ship_class="frigate",
            registries=mock_registries
        )

        component = create_component('bridge', registries=mock_registries)
        ship.add_component(component, LayerType.CORE)

        # Component should have the same registries
        assert component._registries is mock_registries
