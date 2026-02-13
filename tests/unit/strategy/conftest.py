"""
Fixtures for strategy layer unit tests.

PROJ-08: Data-Driven Resource System Test Fixtures
"""
import pytest
import json
from typing import Dict, Any, List
from unittest.mock import MagicMock, patch

from game.core.registry import RegistryManager


@pytest.fixture
def reset_resource_registry():
    """Clear and reset resource registry between tests."""
    registry = RegistryManager.instance()
    registry.resources.clear()
    yield
    registry.resources.clear()


@pytest.fixture
def temp_resources_json(tmp_path):
    """Create temporary resources.json for testing."""
    def _create(resources_list: List[Dict[str, Any]]):
        filepath = tmp_path / "resources.json"
        data = {"resources": resources_list}
        filepath.write_text(json.dumps(data))
        return str(filepath)
    return _create


@pytest.fixture
def custom_resource_registry(reset_resource_registry, temp_resources_json):
    """Registry with custom 'glag' resource loaded."""
    from game.core.resources import load_resources_data

    filepath = temp_resources_json([
        {"id": "fuel"},
        {"id": "energy"},
        {"id": "ammo"},
        {"id": "glag", "display_name": "Glag Units"},
    ])
    registry = RegistryManager.instance()
    registry.resources.update(load_resources_data(filepath))
    return registry


class MockComponent:
    """Mock component for testing without full registry."""

    def __init__(
        self,
        comp_id: str,
        mass: float = 100,
        max_hp: float = 100,
        abilities: dict = None,
        type_str: str = 'Generic',
        damage_threshold: float = 0.3
    ):
        self.id = comp_id
        self.mass = mass
        self.max_hp = max_hp
        self.abilities = abilities or {}
        self.type_str = type_str
        self.damage_threshold = damage_threshold


@pytest.fixture
def mock_component():
    """Factory fixture for creating mock components."""
    return MockComponent


@pytest.fixture
def make_design_data():
    """Factory for creating design_data with components."""
    def _make(components_by_layer: Dict[str, List[str]]) -> Dict[str, Any]:
        layers = {}
        for layer_name, comp_ids in components_by_layer.items():
            layers[layer_name] = [{'id': cid} for cid in comp_ids]
        return {'layers': layers}
    return _make


@pytest.fixture
def make_design_data_with_stats():
    """Factory for creating design_data with expected_stats fallback."""
    def _make(
        components_by_layer: Dict[str, List[str]] = None,
        expected_stats: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        layers = {}
        if components_by_layer:
            for layer_name, comp_ids in components_by_layer.items():
                layers[layer_name] = [{'id': cid} for cid in comp_ids]

        result = {'layers': layers, 'name': 'TestShip'}
        if expected_stats:
            result['expected_stats'] = expected_stats
        return result
    return _make


@pytest.fixture
def ship_stats_with_custom_resources():
    """Mock stats with custom resource types for testing."""
    return {
        'max_hp': 100,
        'mass': 500,
        'resource_storage': {'fuel': 500, 'energy': 300, 'glag': 100},
        'resource_consumption_per_hex': {'fuel': 10, 'glag': 5},
        'resource_consumption_per_turn': {'energy': 50, 'glag': 2},
        'warp_resource_costs': {'energy': 1000, 'fuel': 50},
        'strategic_movement': 100,
        'warp_max_tonnage': 5000,
    }


@pytest.fixture
def mock_component_registry():
    """Fixture that provides a mock component registry context manager."""
    def _create_mock_registry(components_dict: Dict[str, MockComponent]):
        return patch(
            'game.strategy.services.ship_stats_calculator.get_default_registry_provider',
            return_value=MagicMock(get_components=MagicMock(return_value=components_dict))
        )
    return _create_mock_registry


@pytest.fixture
def ship_with_per_turn_component(make_design_data_with_stats):
    """ShipInstance with a per-turn energy consumption component."""
    from game.strategy.data.ship_instance import ShipInstance

    design_data = make_design_data_with_stats(
        expected_stats={
            'max_hp': 100,
            'mass': 200,
            'resource_storage': {'energy': 500, 'fuel': 1000},
            'resource_consumption_per_hex': {'fuel': 10},
            'resource_consumption_per_turn': {'energy': 100},
            'warp_resource_costs': {},
            'strategic_movement': 50,
            'warp_max_tonnage': 0,
        }
    )

    return ShipInstance(
        instance_id='test-ship-1',
        design_id='TestDesign',
        name='Test Ship',
        owner_id=0,
        design_data=design_data,
    )


@pytest.fixture
def ship_with_warp_drive(make_design_data_with_stats):
    """ShipInstance with warp capability."""
    from game.strategy.data.ship_instance import ShipInstance

    design_data = make_design_data_with_stats(
        expected_stats={
            'max_hp': 100,
            'mass': 200,
            'resource_storage': {'energy': 2000, 'fuel': 5000},
            'resource_consumption_per_hex': {'fuel': 20},
            'resource_consumption_per_turn': {},
            'warp_resource_costs': {'energy': 500, 'fuel': 100},
            'strategic_movement': 80,
            'warp_max_tonnage': 3000,
        }
    )

    return ShipInstance(
        instance_id='test-warp-ship',
        design_id='WarpDesign',
        name='Warp Ship',
        owner_id=0,
        design_data=design_data,
    )


@pytest.fixture
def ship_with_custom_resources(make_design_data_with_stats, ship_stats_with_custom_resources):
    """ShipInstance with custom resource types (glag)."""
    from game.strategy.data.ship_instance import ShipInstance

    design_data = make_design_data_with_stats(
        expected_stats=ship_stats_with_custom_resources
    )

    return ShipInstance(
        instance_id='test-custom-ship',
        design_id='CustomDesign',
        name='Custom Ship',
        owner_id=0,
        design_data=design_data,
    )


@pytest.fixture
def fleet_with_resource_ships(
    ship_with_per_turn_component,
    ship_with_warp_drive,
):
    """Fleet containing ships with various resource consumption patterns."""
    from game.strategy.data.fleet import Fleet
    from game.core.hex_math import HexCoord

    fleet = Fleet(
        fleet_id='test-fleet',
        owner_id=0,
        location=HexCoord(0, 0),
        speed=5.0
    )
    fleet.ships.append(ship_with_per_turn_component)
    fleet.ships.append(ship_with_warp_drive)
    return fleet


@pytest.fixture
def empty_fleet():
    """Empty fleet for edge case testing."""
    from game.strategy.data.fleet import Fleet
    from game.core.hex_math import HexCoord

    return Fleet(
        fleet_id='empty-fleet',
        owner_id=0,
        location=HexCoord(0, 0),
        speed=5.0
    )


