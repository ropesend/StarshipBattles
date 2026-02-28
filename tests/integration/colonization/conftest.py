"""
Fixtures for colonization integration tests.

PROJ-40/NEW-INT-001: Uses deterministic galaxy generation with fixed seed.
PROJ-55: Updated to create ships with colony pods matching planet types.
PROJ-211: Updated to inject registries for DI compliance.
"""

import pytest
import random

from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet
from game.strategy.data.galaxy import Galaxy
from game.strategy.data.ship_instance import ShipInstance


# Fixed seed for deterministic galaxy generation
GALAXY_SEED = 42


def make_colony_ship_for_planet(planet, owner_id: int, registries=None) -> ShipInstance:
    """Create a ship with a colony pod matching the planet's type.

    PROJ-55: Ships now need colony pods to colonize specific planet types.
    PROJ-211: Accepts optional registries for DI compliance.

    Args:
        planet: Planet object with planet_type attribute
        owner_id: Owner empire ID
        registries: Optional GameRegistries for DI compliance

    Returns:
        ShipInstance with appropriate colony pod in design_data
    """
    planet_type_str = planet.planet_type.name
    pod_id = f"{planet_type_str.lower()}_colony_pod"

    ship = ShipInstance(
        instance_id=f"colony-ship-{planet_type_str.lower()}-{id(planet)}",
        design_id=f"{planet_type_str}_colony_ship",
        name=f"Colony Ship ({planet_type_str})",
        owner_id=owner_id,
        design_data={
            'name': f"Colony Ship ({planet_type_str})",
            'vehicle_type': 'Ship',
            'stats': {'mass': 100},
            'expected_stats': {'speed': 10.0},  # PROJ-211: Add expected_stats for Fleet speed calc
            'layers': {
                'HULL': [{'id': pod_id}]
            }
        },
    )
    if registries is not None:
        ship.set_registries(registries)
    return ship


@pytest.fixture
def turn_engine(fresh_registries):
    """Create a standalone turn engine with DI registries.

    PROJ-50 Phase 8: Uses fresh_registries for strict DI compliance.
    """
    return TurnEngine(registries=fresh_registries)


@pytest.fixture
def simple_galaxy():
    """Create a deterministic galaxy with systems for testing.

    PROJ-40/NEW-INT-001: Uses fixed seed for reproducible results.
    The seed guarantees at least one system with an unowned planet.
    """
    random.seed(GALAXY_SEED)
    galaxy = Galaxy(radius=500)
    galaxy.generate_systems(count=5, min_dist=100)
    galaxy.generate_warp_lanes()
    return galaxy


@pytest.fixture
def empire_with_fleet(simple_galaxy, fresh_registries):
    """Create empire with a colonization-capable fleet.

    PROJ-40/NEW-INT-001: Deterministic fixture that always finds a planet.
    PROJ-55: Fleet now includes a colony ship with the correct pod type.
    PROJ-211: Uses fresh_registries for DI compliance.
    The deterministic simple_galaxy fixture guarantees an unowned planet exists.
    """
    empire = Empire(0, "Colonizer Empire", (0, 100, 200))

    # Find an unowned planet and create fleet at its location
    target_planet = None
    global_loc = None
    for system in simple_galaxy.systems.values():
        for planet in system.planets:
            if planet.owner_id is None:
                target_planet = planet
                global_loc = system.global_location + planet.location
                break
        if target_planet:
            break

    # With deterministic seed, we should always find a planet
    assert target_planet is not None, "Deterministic galaxy should have an unowned planet"

    fleet = Fleet(1, empire.id, global_loc, speed=10.0)
    # PROJ-55: Create colony ship with pod matching planet type
    # PROJ-211: Use registries for DI compliance
    fleet.ships = [make_colony_ship_for_planet(target_planet, empire.id, fresh_registries)]
    empire.add_fleet(fleet)
    return empire, fleet, target_planet, simple_galaxy
