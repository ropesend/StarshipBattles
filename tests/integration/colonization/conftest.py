"""
Fixtures for colonization integration tests.

PROJ-40/NEW-INT-001: Uses deterministic galaxy generation with fixed seed.
"""

import pytest
import random

from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet
from game.strategy.data.galaxy import Galaxy
from tests.conftest import make_mock_ship_instance


# Fixed seed for deterministic galaxy generation
GALAXY_SEED = 42


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
def empire_with_fleet(simple_galaxy):
    """Create empire with a colonization-capable fleet.

    PROJ-40/NEW-INT-001: Deterministic fixture that always finds a planet.
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
    fleet.ships = [make_mock_ship_instance("Colony Ship", empire.id)]
    empire.add_fleet(fleet)
    return empire, fleet, target_planet, simple_galaxy
