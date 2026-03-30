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

    def get_zones_at_global_hex(self, global_hex):
        """Return zone objects at location (empty for these tests)."""
        return []


@pytest.fixture
def mock_galaxy():
    """Provide a fresh MockGalaxy instance."""
    return MockGalaxy()


def create_mock_ship_instance(
    name="TestShip",
    owner_id=0,
    is_alive=True,
    is_derelict=False,
    consumable_levels=None,
    component_toggles=None,
    design_data=None,
    registries=None
):
    """Helper to create a mock ShipInstance for testing.

    PROJ-211: Added registries parameter for DI compliance. Required for tests
    that call get_calculated_stats() or add ships to fleets.
    """
    from game.strategy.data.ship_instance import ShipInstance

    ship = ShipInstance(
        instance_id=f"test-{name}",
        design_id=name,
        name=name,
        owner_id=owner_id,
        is_alive=is_alive,
        is_derelict=is_derelict,
    )
    if consumable_levels:
        ship.consumable_levels = consumable_levels.copy()
    if component_toggles:
        ship.component_toggles = component_toggles.copy()
    if design_data:
        ship.design_data = design_data
    else:
        ship.design_data = {'name': name, 'layers': {}}
    if registries is not None:
        ship._registries = registries
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


def create_colony_ship(name="Colony Ship", owner_id=0, pod_type="ICE_DWARF", registries=None):
    """Helper to create a colony ship with proper pod for colonization.

    PROJ-140: Colony ships need a proper colony pod in design_data to colonize.
    PROJ-211: Added registries parameter for DI compliance.

    Args:
        name: Ship name
        owner_id: Owner empire ID
        pod_type: Planet type this ship can colonize (e.g. "ICE_DWARF")
        registries: Optional GameRegistries for DI compliance

    Returns:
        ShipInstance with colony pod ability
    """
    from game.strategy.data.ship_instance import ShipInstance

    ship = ShipInstance(
        instance_id=f"colony-{name.lower().replace(' ', '-')}-{id(name)}",
        design_id=f"{pod_type}_colony_ship",
        name=name,
        owner_id=owner_id,
        design_data={
            'name': name,
            'vehicle_type': 'Ship',
            'stats': {'mass': 100},
            'expected_stats': {'speed': 10.0},  # PROJ-211: For Fleet speed calc
            'layers': {
                'HULL': [{'id': f'{pod_type.lower()}_colony_pod'}]
            }
        },
    )
    if registries is not None:
        ship.set_registries(registries)
    return ship


class MockPlanetType:
    """Mock planet type with name attribute."""
    def __init__(self, name):
        self.name = name
