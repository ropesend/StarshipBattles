"""Shared fixtures and helpers for turn engine tests."""
import pytest
from unittest.mock import MagicMock
from game.core.hex_math import HexCoord


class MockGalaxy:
    """Mock galaxy for turn engine testing."""
    def __init__(self):
        self.systems = {}

    def get_planets_at_global_hex(self, global_hex):
        """Return planets at the given global hex (calculates from system data)."""
        result = []
        for sys in self.systems.values():
            for p in sys.planets:
                if hasattr(p, 'location') and (sys.global_location + p.location) == global_hex:
                    result.append(p)
        return result


@pytest.fixture
def mock_galaxy():
    """Provide a fresh MockGalaxy instance."""
    return MockGalaxy()


def create_mock_ship_instance(
    name="TestShip",
    owner_id=0,
    is_destroyed=False,
    is_derelict=False,
    resource_levels=None,
    component_toggles=None,
    design_data=None
):
    """Helper to create a mock ShipInstance for testing."""
    from game.strategy.data.ship_instance import ShipInstance

    ship = ShipInstance(
        instance_id=f"test-{name}",
        design_id=name,
        name=name,
        owner_id=owner_id,
        is_destroyed=is_destroyed,
        is_derelict=is_derelict,
    )
    if resource_levels:
        ship.resource_levels = resource_levels.copy()
    if component_toggles:
        ship.component_toggles = component_toggles.copy()
    if design_data:
        ship.design_data = design_data
    else:
        ship.design_data = {'name': name, 'layers': {}}
    return ship


def create_mock_component_def(
    abilities=None,
    comp_type='Generic',
    max_hp=100,
    mass=10,
    damage_threshold=0.3
):
    """Helper to create a mock component definition."""
    mock_def = MagicMock()
    mock_def.abilities = abilities or {}
    mock_def.type_str = comp_type
    mock_def.max_hp = max_hp
    mock_def.mass = mass
    mock_def.damage_threshold = damage_threshold
    return mock_def
