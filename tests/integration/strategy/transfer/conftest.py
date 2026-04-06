"""
Fixtures and factory functions for transfer validation integration tests.

PROJ-159: Uses real Planet/Fleet objects instead of MagicMock to satisfy
protocol-based type checking (is_planet() uses isinstance(obj, IPlanet)).

PROJ-211: Updated to use ship_factory fixture for DI compliance.
"""

import pytest
from game.strategy.data.planet import Planet, PlanetType, SpeciesPopulation
from game.strategy.data.fleet import Fleet
from game.strategy.data.ship_instance import ShipInstance
from game.core.hex_math import HexCoord
from game.core.registry import GameRegistries


# --- Factory Functions ---

def create_test_planet(
    name: str = "Test Colony",
    owner_id: int = 0,
    population_count: int = 1000,
    location: HexCoord = None,
    species_id: str = "human"
) -> Planet:
    """
    Create a minimal Planet for integration tests.

    Uses Earth-like defaults for mandatory physical properties.
    Only test-relevant fields (name, owner_id, populations) are exposed.
    """
    if location is None:
        location = HexCoord(0, 0)

    populations = []
    if population_count > 0:
        populations.append(SpeciesPopulation(race_id=species_id, count=population_count))

    return Planet(
        name=name,
        location=location,
        orbit_distance=1,
        mass=5.972e24,
        radius=6.371e6,
        surface_area=5.1e14,
        density=5514.0,
        surface_gravity=9.81,
        surface_pressure=101325.0,
        surface_temperature=288.0,
        surface_water=0.71,
        tectonic_activity=0.3,
        magnetic_field=1.0,
        planet_type=PlanetType.CONTINENTAL,
        owner_id=owner_id,
        populations=populations
    )


def create_transport_ship(
    name: str = "Transport-1",
    owner_id: int = 0,
    cargo_capacity: int = 100,
    current_cargo: int = 0,
    registries: GameRegistries = None
) -> ShipInstance:
    """
    Create a ship with passenger cargo capacity.

    Uses expected_stats to bypass registry lookup and set exact cargo capacity.
    This allows tests to control capacity precisely without depending on
    component registry definitions.

    PROJ-211: Added registries parameter for DI compliance.
    """
    design = {
        "name": name,
        "hull_id": "test_hull",
        "layers": {},  # Empty layers - calculator will use expected_stats
        "expected_stats": {
            "max_hp": 100,
            "mass": 100,
            "cargo_storage": {"passengers": cargo_capacity}
        }
    }
    ship = ShipInstance.create(design, owner_id=owner_id, name=name, registries=registries)
    # Pre-cache stats for designs with no real component layers
    ship._cached_stats = design["expected_stats"]
    if current_cargo > 0:
        ship.cargo_contents["passengers"] = current_cargo
    return ship


def create_transport_fleet(
    fleet_id: int = 1,
    owner_id: int = 0,
    location: HexCoord = None,
    cargo_capacity: int = 100,
    current_cargo: int = 0,
    registries: GameRegistries = None
) -> Fleet:
    """
    Create a fleet with a transport ship.

    Args:
        fleet_id: Fleet identifier
        owner_id: Owner (0=player)
        location: Fleet location (default: origin)
        cargo_capacity: Passenger capacity of transport ship
        current_cargo: Current passengers loaded
        registries: GameRegistries for DI (PROJ-211)
    """
    if location is None:
        location = HexCoord(0, 0)

    fleet = Fleet(fleet_id, owner_id, location)
    ship = create_transport_ship(
        name=f"Transport-{fleet_id}",
        owner_id=owner_id,
        cargo_capacity=cargo_capacity,
        current_cargo=current_cargo,
        registries=registries
    )
    fleet.add_ship(ship)
    return fleet


# --- Mock Galaxy Infrastructure ---

class MockSystem:
    """Minimal system for transfer validation tests."""

    def __init__(self, global_location: HexCoord, planets: list = None):
        self.global_location = global_location
        self.planets = planets if planets is not None else []
        self.name = f"System-{global_location}"


class MockGalaxy:
    """
    Minimal galaxy for transfer validation tests.

    Provides the methods needed by TransferValidator:
    - get_system_at_location(location)
    - systems dict for iteration
    """

    def __init__(self):
        self.systems = {}

    def add_system(self, system: MockSystem):
        """Add a system to the galaxy."""
        self.systems[system.global_location] = system

    def get_system_at_location(self, location: HexCoord) -> MockSystem:
        """Get system at the given location."""
        return self.systems.get(location)


# --- Pytest Fixtures ---

@pytest.fixture
def colonized_planet() -> Planet:
    """A colonized planet with population at origin."""
    return create_test_planet(
        name="Alpha Colony",
        owner_id=0,
        population_count=1000,
        location=HexCoord(0, 0)
    )


@pytest.fixture
def uncolonized_planet() -> Planet:
    """An uncolonized planet (no owner)."""
    return create_test_planet(
        name="Beta",
        owner_id=None,
        population_count=0,
        location=HexCoord(0, 0)
    )


@pytest.fixture
def transport_fleet(fresh_registries) -> Fleet:
    """Fleet with empty transport capacity at origin."""
    return create_transport_fleet(
        fleet_id=1,
        cargo_capacity=100,
        current_cargo=0,
        location=HexCoord(0, 0),
        registries=fresh_registries
    )


@pytest.fixture
def loaded_fleet(fresh_registries) -> Fleet:
    """Fleet with passengers already loaded at origin."""
    return create_transport_fleet(
        fleet_id=2,
        cargo_capacity=100,
        current_cargo=50,
        location=HexCoord(0, 0),
        registries=fresh_registries
    )


@pytest.fixture
def mock_galaxy(colonized_planet) -> MockGalaxy:
    """Galaxy with colonized planet at origin system."""
    galaxy = MockGalaxy()
    system = MockSystem(HexCoord(0, 0), [colonized_planet])
    galaxy.add_system(system)
    return galaxy
