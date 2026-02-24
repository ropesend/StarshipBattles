"""Protocol conformance tests for strategy-simulation boundary.

PROJ-90 Phase 4: Verifies that concrete types satisfy the IPostBattleShip
and IResourceReader protocols, ensuring the boundary contracts are enforced.

PROJ-174: Uses deprecated get_default_registries() in fixture.
"""

import pytest

# PROJ-174: Suppress deprecation warnings - fixture uses deprecated API
pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")

from game.core.protocols import (
    IPostBattleShip,
    IResourceReader,
    is_post_battle_ship,
    is_resource_reader,
)
from game.core.constants import LayerType
from game.simulation.entities.layer_data import LayerData


class TestIPostBattleShipConformance:
    """Test that Ship satisfies IPostBattleShip protocol."""

    @pytest.fixture
    def simple_ship(self):
        """Create a simple ship for testing."""
        from game.simulation.entities.ship import Ship
        from game.core.registry import get_default_registries

        registries = get_default_registries()
        ship = Ship(
            name="Test Ship",
            x=0.0,
            y=0.0,
            color=(255, 255, 255),
            registries=registries
        )
        return ship

    def test_ship_satisfies_protocol_via_isinstance(self, simple_ship):
        """Ship should satisfy IPostBattleShip via isinstance check."""
        assert isinstance(simple_ship, IPostBattleShip)

    def test_ship_satisfies_protocol_via_typeguard(self, simple_ship):
        """Ship should satisfy IPostBattleShip via TypeGuard function."""
        assert is_post_battle_ship(simple_ship)

    def test_ship_has_name_property(self, simple_ship):
        """Ship.name should be accessible."""
        assert hasattr(simple_ship, 'name')
        assert isinstance(simple_ship.name, str)
        assert simple_ship.name == "Test Ship"

    def test_ship_has_hp_property(self, simple_ship):
        """Ship.hp should be accessible."""
        assert hasattr(simple_ship, 'hp')
        assert isinstance(simple_ship.hp, int)
        assert simple_ship.hp >= 0

    def test_ship_has_max_hp_property(self, simple_ship):
        """Ship.max_hp should be accessible."""
        assert hasattr(simple_ship, 'max_hp')
        assert isinstance(simple_ship.max_hp, int)
        assert simple_ship.max_hp >= 0

    def test_ship_has_is_alive_attribute(self, simple_ship):
        """Ship.is_alive should be accessible."""
        assert hasattr(simple_ship, 'is_alive')
        assert isinstance(simple_ship.is_alive, bool)
        assert simple_ship.is_alive is True  # New ship should be alive

    def test_ship_has_is_derelict_attribute(self, simple_ship):
        """Ship.is_derelict should be accessible."""
        assert hasattr(simple_ship, 'is_derelict')
        assert isinstance(simple_ship.is_derelict, bool)
        assert simple_ship.is_derelict is False  # New ship not derelict

    def test_ship_has_layers_attribute(self, simple_ship):
        """Ship.layers should be accessible as dict."""
        assert hasattr(simple_ship, 'layers')
        assert isinstance(simple_ship.layers, dict)
        # Verify typed layer structure (PROJ-84 / PROJ-93)
        for key, value in simple_ship.layers.items():
            assert isinstance(key, LayerType), f"Layer key {key} should be LayerType"
            assert isinstance(value, LayerData), f"Layer value for {key} should be LayerData"

    def test_ship_has_resources_attribute(self, simple_ship):
        """Ship.resources should be accessible."""
        assert hasattr(simple_ship, 'resources')
        # May be None or a ResourceRegistry
        assert simple_ship.resources is not None


class TestIResourceReaderConformance:
    """Test that ResourceRegistry satisfies IResourceReader protocol."""

    @pytest.fixture
    def resource_registry(self):
        """Create a ResourceRegistry for testing."""
        from game.simulation.systems.resource_manager import ResourceRegistry

        registry = ResourceRegistry()
        # Register storage capacity
        registry.register_storage('fuel', 100.0)
        registry.register_storage('energy', 50.0)
        # Fill to capacity
        registry.set_value('fuel', 100.0)
        registry.set_value('energy', 50.0)
        return registry

    def test_registry_satisfies_protocol_via_isinstance(self, resource_registry):
        """ResourceRegistry should satisfy IResourceReader via isinstance."""
        assert isinstance(resource_registry, IResourceReader)

    def test_registry_satisfies_protocol_via_typeguard(self, resource_registry):
        """ResourceRegistry should satisfy IResourceReader via TypeGuard."""
        assert is_resource_reader(resource_registry)

    def test_registry_get_value(self, resource_registry):
        """ResourceRegistry.get_value should work."""
        assert resource_registry.get_value('fuel') == 100.0
        assert resource_registry.get_value('energy') == 50.0

    def test_registry_get_max_value(self, resource_registry):
        """ResourceRegistry.get_max_value should work."""
        assert resource_registry.get_max_value('fuel') == 100.0
        assert resource_registry.get_max_value('energy') == 50.0

    def test_registry_get_value_unknown_resource(self, resource_registry):
        """get_value for unknown resource should return 0."""
        assert resource_registry.get_value('unknown') == 0.0

    def test_registry_get_max_value_unknown_resource(self, resource_registry):
        """get_max_value for unknown resource should return 0."""
        assert resource_registry.get_max_value('unknown') == 0.0


class TestProtocolNegativeCases:
    """Test that non-conforming objects fail protocol checks."""

    def test_dict_does_not_satisfy_post_battle_ship(self):
        """Plain dict should not satisfy IPostBattleShip."""
        fake_ship = {'name': 'fake', 'hp': 100}
        assert not isinstance(fake_ship, IPostBattleShip)
        assert not is_post_battle_ship(fake_ship)

    def test_none_does_not_satisfy_protocols(self):
        """None should not satisfy protocols."""
        assert not is_post_battle_ship(None)
        assert not is_resource_reader(None)
