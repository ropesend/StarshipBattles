"""
Shared fixtures for AI strategy integration tests.
"""

import pytest
import pygame
from game.simulation.entities.ship import Ship, LayerType
from game.simulation.components.component import load_components, create_component
from game.ai.policy_manager import get_default_policy_manager
from game.engine.spatial import SpatialGrid
from game.core.registry import get_default_registry_provider
from tests.fixtures.paths import get_data_dir, get_unit_test_data_dir


@pytest.fixture(autouse=True)
def setup_game_data():
    """Load required game data for AI tests."""
    data_dir = get_data_dir()
    unit_test_data_dir = get_unit_test_data_dir()

    # PROJ-211: Pass registry_provider explicitly (no fallback)
    provider = get_default_registry_provider()
    load_components(str(data_dir / "components.json"), registry_provider=provider)
    from game.simulation.entities.ship_loader import load_vehicle_classes
    load_vehicle_classes(str(unit_test_data_dir / "test_vehicleclasses.json"), registry_provider=provider)

    # Load test data for AI strategies
    manager = get_default_policy_manager()
    manager.load_data(
        str(unit_test_data_dir),
        targeting_file="test_targeting_policies.json",
        movement_file="test_movement_policies.json",
    )
    manager._loaded = True

    yield

    get_default_policy_manager().clear()


@pytest.fixture
def spatial_grid():
    """Create a spatial grid for battle."""
    return SpatialGrid(cell_size=2000)


@pytest.fixture
def create_test_ship(fresh_registries):
    """Factory to create test ships with components."""
    def _create(name, x, y, team_id, ship_class="TestM_4L"):
        ship = Ship(name, x, y, (0, 255, 0), team_id=team_id, ship_class=ship_class, registries=fresh_registries)
        ship.add_component(create_component('bridge', registries=fresh_registries), LayerType.CORE)
        ship.add_component(create_component('crew_quarters', registries=fresh_registries), LayerType.CORE)
        ship.add_component(create_component('life_support', registries=fresh_registries), LayerType.CORE)
        ship.add_component(create_component('standard_engine', registries=fresh_registries), LayerType.OUTER)
        ship.add_component(create_component('thruster', registries=fresh_registries), LayerType.INNER)
        ship.recalculate_stats()
        return ship
    return _create
