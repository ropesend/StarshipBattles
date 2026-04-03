"""Tests for FleetCapabilityCalculator DI functionality.

PROJ-211 Task 2.2: Tests verifying DI path for component registry access.
"""

import pytest
from unittest.mock import MagicMock


def make_ship_instance_with_registries(name: str, design_data: dict, registries):
    """Helper to create ShipInstance with registries set."""
    from game.strategy.data.ship_instance import ShipInstance
    ship = ShipInstance(
        instance_id=f"test-{name}",
        design_id=f"design-{name}",
        name=name,
        owner_id=0,
        design_data=design_data or {}
    )
    ship.set_registries(registries)
    return ship


def create_mock_registries(components: dict = None):
    """Create mock GameRegistries with specified components."""
    mock = MagicMock()
    mock.components = components or {}
    mock.modifiers = {}
    mock.vehicle_classes = {}
    mock.resources = {}
    return mock


class TestStaticMethodsUseShipRegistries:
    """Test that static methods prefer ship._registries over global fallback."""

    def test_ship_has_spaceyard_uses_ship_registries(self):
        """ship_has_spaceyard uses ship._registries.components when available."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator

        # Create registry with space_shipyard having SpaceShipyard ability
        component_registry = {
            'space_shipyard': {
                'abilities': {'SpaceShipyard': {}}
            }
        }
        registries = create_mock_registries(component_registry)

        ship = make_ship_instance_with_registries(
            name="Yard Ship",
            design_data={"layers": {"hull": [{"id": "space_shipyard"}]}},
            registries=registries
        )

        # Should use ship's registries, not global fallback
        result = FleetCapabilityCalculator.ship_has_spaceyard(ship)
        assert result is True

    def test_ship_has_spaceyard_empty_registry_returns_false(self):
        """ship_has_spaceyard returns False when ship's registry doesn't have component."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator

        # Empty registry - space_shipyard not defined
        registries = create_mock_registries({})

        ship = make_ship_instance_with_registries(
            name="Yard Ship",
            design_data={"layers": {"hull": [{"id": "space_shipyard"}]}},
            registries=registries
        )

        # Component not in registry, so ability check returns False
        result = FleetCapabilityCalculator.ship_has_spaceyard(ship)
        assert result is False

class TestFleetCapabilityCalculatorDI:
    """Test FleetCapabilityCalculator instance with injected registry."""

    def test_calculator_with_injected_registry(self, fresh_registries):
        """FleetCapabilityCalculator uses injected component_registry."""
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord
        from game.strategy.data.ship_instance import ShipInstance

        # Create component registry with SpaceShipyard ability
        component_registry = {
            'space_shipyard': {
                'abilities': {'SpaceShipyard': {}}
            }
        }

        # Create fleet with injected registry
        fleet = Fleet(1, 0, HexCoord(0, 0), component_registry=component_registry)

        # Create ship with yard component
        # PROJ-211: Pass registries for DI compliance (add_ship triggers speed calc)
        ship = ShipInstance(
            instance_id="test-ship",
            design_id="design-1",
            name="Yard Ship",
            owner_id=0,
            design_data={"layers": {"hull": [{"id": "space_shipyard"}]}}
        )
        ship._registries = fresh_registries
        fleet.add_ship(ship)

        # Calculator should use injected registry
        # PROJ-210: Space shipyard properties accessed via capabilities
        assert fleet.capabilities.has_space_shipyard is True
        assert fleet.capabilities.space_shipyard_count == 1

    def test_fleet_from_dict_passes_registries(self):
        """Fleet.from_dict passes registries to ships and calculator."""
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord
        from game.core.registry import GameRegistries

        # Create test registries
        registries = GameRegistries(
            components={'space_shipyard': {'abilities': {'SpaceShipyard': {}}}},
            modifiers={},
            vehicle_classes={},
            resources={}
        )

        # Fleet data with a ship
        fleet_data = {
            'id': 100,
            'owner_id': 0,
            'location': {'q': 5, 'r': 3},
            'speed': 5.0,
            'ships': [{
                'instance_id': 'ship-1',
                'design_id': 'design-1',
                'name': 'Yard Ship',
                'owner_id': 0,
                'design_data': {'layers': {'hull': [{'id': 'space_shipyard'}]}},
                'current_hp': 100,
                'max_hp': 100,
                'status': 'operational',
                'component_damage': {},
                'component_toggles': {},
                'fuel': 100,
                'energy': 100,
                'max_fuel': 100,
                'max_energy': 100,
                'cargo_contents': {},
            }],
            'orders': [],
            'path': [],
            'construction_queue': [],
        }

        # Restore fleet with registries
        fleet = Fleet.from_dict(fleet_data, registries=registries)

        # Fleet should have registry
        assert fleet._component_registry == registries.components

        # Ship should have registries
        assert len(fleet.ships) == 1
        assert fleet.ships[0]._registries is not None
        assert fleet.ships[0]._registries.components == registries.components

        # Capability checks should work
        assert fleet.capabilities.has_space_shipyard is True


class TestFleetCreationWithRegistry:
    """Test Fleet creation with component_registry parameter."""

    def test_fleet_init_accepts_component_registry(self):
        """Fleet.__init__ accepts and stores component_registry."""
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        registry = {'test_component': {'abilities': {}}}
        fleet = Fleet(1, 0, HexCoord(0, 0), component_registry=registry)

        assert fleet._component_registry == registry

    def test_fleet_init_without_registry_uses_none(self):
        """Fleet.__init__ without registry sets _component_registry to None."""
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(1, 0, HexCoord(0, 0))

        assert fleet._component_registry is None
