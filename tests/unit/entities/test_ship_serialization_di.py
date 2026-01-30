"""
Tests for ShipSerializer dependency injection (PROJ-50).

These tests verify that ShipSerializer.from_dict():
1. Accepts GameRegistries via parameter (required)
2. Raises TypeError when registries is None
3. Works with injected registries for all operations
"""
import pytest

from game.simulation.entities.ship_serialization import ShipSerializer
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


@pytest.fixture
def ship_dict_data():
    """Create a basic ship dictionary for deserialization testing."""
    return {
        "name": "Test Ship",
        "ship_class": "frigate",
        "vehicle_type": "Ship",
        "theme_id": "Federation",
        "team_id": 0,
        "color": [255, 0, 0],
        "ai_strategy": "standard_ranged",
        "layers": {
            "CORE": [
                {"id": "bridge", "modifiers": [{"id": "simple_size_mount", "value": 1.0}]}
            ]
        },
        "resources": {},
        "expected_stats": {}
    }


# =============================================================================
# Test: from_dict with Registries (PROJ-50 Strict DI)
# =============================================================================

class TestShipSerializerFromDict:
    """Tests for ShipSerializer.from_dict with strict registries parameter."""

    def test_from_dict_accepts_registries(self, mock_registries, ship_dict_data):
        """from_dict should accept registries parameter."""
        ship = ShipSerializer.from_dict(ship_dict_data, registries=mock_registries)

        assert ship is not None
        assert ship.name == "Test Ship"
        assert ship._registries is mock_registries

    def test_from_dict_with_none_raises_typeerror(self, ship_dict_data):
        """from_dict with None registries should raise TypeError (PROJ-50 strict DI)."""
        with pytest.raises(TypeError, match="registries is required"):
            ShipSerializer.from_dict(ship_dict_data, registries=None)

    def test_from_dict_creates_components_with_registries(self, mock_registries, ship_dict_data):
        """from_dict should create components using injected registries."""
        from game.simulation.components.component_constants import LayerType

        ship = ShipSerializer.from_dict(ship_dict_data, registries=mock_registries)

        # Check component was created
        core_components = ship.layers[LayerType.CORE]['components']
        assert len(core_components) > 0

        # Component should also have the registries
        bridge = core_components[0]
        assert bridge._registries is mock_registries

    def test_from_dict_applies_modifiers_with_registries(self, mock_registries, ship_dict_data):
        """from_dict should apply modifiers using injected registries."""
        from game.simulation.components.component_constants import LayerType

        ship = ShipSerializer.from_dict(ship_dict_data, registries=mock_registries)

        core_components = ship.layers[LayerType.CORE]['components']
        assert len(core_components) > 0

        bridge = core_components[0]
        size_mod = bridge.get_modifier('simple_size_mount')
        assert size_mod is not None
        assert size_mod.value == 1.0


# =============================================================================
# Test: Strict DI Enforcement (PROJ-50)
# =============================================================================

class TestStrictDIEnforcement:
    """Tests ensuring strict DI is enforced (no backward compatibility with None)."""

    def test_to_dict_still_works(self, mock_registries):
        """to_dict should still work (doesn't need registries)."""
        ship = Ship(
            name="Test Ship",
            x=0, y=0,
            color=(255, 0, 0),
            team_id=0,
            ship_class="frigate",
            registries=mock_registries
        )

        data = ShipSerializer.to_dict(ship)

        assert data is not None
        assert data['name'] == "Test Ship"
        assert data['ship_class'] == "frigate"

    def test_roundtrip_with_registries(self, mock_registries):
        """Ship should survive serialization roundtrip with registries."""
        from game.simulation.components.component import create_component
        from game.simulation.components.component_constants import LayerType

        # Create original ship
        ship = Ship(
            name="Roundtrip Test",
            x=0, y=0,
            color=(255, 0, 0),
            team_id=0,
            ship_class="frigate",
            registries=mock_registries
        )

        # Add a component
        component = create_component('bridge', registries=mock_registries)
        ship.add_component(component, LayerType.CORE)

        # Serialize
        data = ShipSerializer.to_dict(ship)

        # Deserialize with registries
        loaded_ship = ShipSerializer.from_dict(data, registries=mock_registries)

        assert loaded_ship.name == ship.name
        assert loaded_ship.ship_class == ship.ship_class
        assert loaded_ship._registries is mock_registries
