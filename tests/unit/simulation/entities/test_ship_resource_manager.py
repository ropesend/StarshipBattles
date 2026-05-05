"""Unit tests for ShipResourceManager resource-state delegation."""

import pytest

from game.simulation.entities.ship import Ship
from game.simulation.entities.ship_stats import ShipStatsCalculator


@pytest.fixture
def ship(fresh_registries):
    return Ship(
        name="ResourceShip",
        x=0,
        y=0,
        color=(255, 255, 255),
        registries=fresh_registries,
    )


def test_resource_manager_state_is_exposed_through_ship_properties(ship) -> None:
    manager = ship._resource_manager

    assert manager.resources_initialized is False
    assert manager.prev_max_resources == {}
    assert manager.prev_max_shields == 0

    ship._resources_initialized = True
    ship._prev_max_resources = {"fuel": 20.0}
    ship._prev_max_shields = 15

    assert manager.resources_initialized is True
    assert manager.prev_max_resources == {"fuel": 20.0}
    assert manager.prev_max_shields == 15


def test_initialize_resources_first_pass_fills_capacity_and_records_previous_max(
    ship,
) -> None:
    calculator = ShipStatsCalculator({}, planetary_resource_ids=[])
    ship.resources.register_storage("fuel", 100.0)
    ship.max_shields = 25

    calculator._initialize_resources(ship)

    assert ship._resources_initialized is True
    assert ship.resources.get_value("fuel") == 100.0
    assert ship.current_shields == 25
    assert ship._prev_max_resources == {"fuel": 100.0}
    assert ship._prev_max_shields == 25


def test_initialize_resources_adds_only_capacity_and_shield_deltas(ship) -> None:
    calculator = ShipStatsCalculator({}, planetary_resource_ids=[])
    ship.resources.register_storage("fuel", 100.0)
    ship.max_shields = 25
    calculator._initialize_resources(ship)

    ship.resources.set_value("fuel", 70.0)
    ship.current_shields = 10
    ship.resources.reset_stats()
    ship.resources.register_storage("fuel", 150.0)
    ship.max_shields = 40

    calculator._initialize_resources(ship)

    assert ship.resources.get_value("fuel") == 120.0
    assert ship.current_shields == 25
    assert ship._prev_max_resources == {"fuel": 150.0}
    assert ship._prev_max_shields == 40
