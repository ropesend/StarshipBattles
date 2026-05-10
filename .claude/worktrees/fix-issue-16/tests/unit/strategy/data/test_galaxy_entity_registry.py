"""Unit tests for GalaxyEntityRegistry.

Tests entity lifecycle management: registration, lookup, and unregistration
of planets, fleets, and zone objects.
"""

import pytest
from game.core.hex_math import HexCoord
from game.strategy.data.galaxy_entity_registry import GalaxyEntityRegistry


# ---------------------------------------------------------------------------
# Lightweight test doubles (no real Galaxy/Planet/Fleet imports needed)
# ---------------------------------------------------------------------------

class _MockGalaxy:
    """Minimal Galaxy substitute exposing only the state dicts that
    GalaxyEntityRegistry reads/writes."""

    def __init__(self):
        self._next_planet_id = 1
        self.planets_by_id = {}
        self._planet_to_system = {}
        self._global_hex_planets = {}
        self._global_hex_zones = {}
        self._zone_to_system = {}
        self.fleets_by_id = {}


class _MockStarSystem:
    def __init__(self, global_location: HexCoord):
        self.global_location = global_location
        self.planets = []
        self.stars = []
        self.warp_points = []
        self.storms = []


class _MockPlanet:
    def __init__(self, location: HexCoord, radius_hexes: int = 0):
        self.id = None  # assigned by register_planet
        self.location = location
        self.radius_hexes = radius_hexes
        # occupied_hexes only relevant when radius_hexes > 0
        if radius_hexes > 0:
            self.occupied_hexes = [location]
        else:
            self.occupied_hexes = []


class _MockFleet:
    def __init__(self, fleet_id: int, location: HexCoord | None = None):
        self.id = fleet_id
        self.location = location


class _MockZone:
    """Zone occupant (e.g. star or Dyson Sphere) with occupied_hexes."""

    def __init__(self, hexes: list[HexCoord]):
        self.occupied_hexes = hexes


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def galaxy():
    return _MockGalaxy()


@pytest.fixture
def registry(galaxy):
    return GalaxyEntityRegistry(galaxy)


@pytest.fixture
def system():
    return _MockStarSystem(global_location=HexCoord(5, 5))


# ===========================================================================
# Planet registration
# ===========================================================================

class TestPlanetRegistration:
    """register_planet assigns an ID and indexes the planet."""

    def test_register_planet_assigns_sequential_ids(self, registry, galaxy, system):
        p1 = _MockPlanet(location=HexCoord(1, 0))
        p2 = _MockPlanet(location=HexCoord(2, 0))

        registry.register_planet(system, p1)
        registry.register_planet(system, p2)

        assert p1.id == 1
        assert p2.id == 2
        assert galaxy._next_planet_id == 3

    def test_register_planet_adds_to_id_lookup(self, registry, galaxy, system):
        planet = _MockPlanet(location=HexCoord(1, 0))
        registry.register_planet(system, planet)

        assert galaxy.planets_by_id[planet.id] is planet

    def test_register_planet_adds_to_reverse_system_lookup(self, registry, galaxy, system):
        planet = _MockPlanet(location=HexCoord(1, 0))
        registry.register_planet(system, planet)

        assert galaxy._planet_to_system[planet] is system

    def test_register_planet_adds_to_spatial_index(self, registry, galaxy, system):
        planet = _MockPlanet(location=HexCoord(1, 0))
        registry.register_planet(system, planet)

        global_hex = system.global_location + planet.location
        assert planet in galaxy._global_hex_planets[global_hex]

    def test_register_multiple_planets_at_same_hex(self, registry, galaxy, system):
        """Two planets at the same local offset both appear in the spatial list."""
        p1 = _MockPlanet(location=HexCoord(1, 0))
        p2 = _MockPlanet(location=HexCoord(1, 0))
        registry.register_planet(system, p1)
        registry.register_planet(system, p2)

        global_hex = system.global_location + HexCoord(1, 0)
        assert len(galaxy._global_hex_planets[global_hex]) == 2

    def test_register_planet_with_zone_footprint(self, registry, galaxy, system):
        """A planet with radius_hexes > 0 is also registered as a zone."""
        planet = _MockPlanet(location=HexCoord(0, 1), radius_hexes=1)
        registry.register_planet(system, planet)

        # Should appear in both planet and zone indexes
        assert planet.id is not None
        assert id(planet) in galaxy._zone_to_system


# ===========================================================================
# Planet restoration (deserialization)
# ===========================================================================

class TestPlanetRestore:
    """restore_planet indexes a planet whose ID is already set."""

    def test_restore_planet_preserves_existing_id(self, registry, galaxy, system):
        planet = _MockPlanet(location=HexCoord(1, 0))
        planet.id = 42  # pre-set from deserialization

        registry.restore_planet(system, planet)

        assert planet.id == 42
        assert galaxy.planets_by_id[42] is planet

    def test_restore_planet_does_not_advance_next_id(self, registry, galaxy, system):
        planet = _MockPlanet(location=HexCoord(1, 0))
        planet.id = 99

        registry.restore_planet(system, planet)

        assert galaxy._next_planet_id == 1  # unchanged


# ===========================================================================
# Planet lookup
# ===========================================================================

class TestGetPlanetById:
    def test_returns_registered_planet(self, registry, system):
        planet = _MockPlanet(location=HexCoord(0, 0))
        registry.register_planet(system, planet)

        assert registry.get_planet_by_id(planet.id) is planet

    def test_returns_none_for_missing_id(self, registry):
        assert registry.get_planet_by_id(999) is None


# ===========================================================================
# Planet unregistration
# ===========================================================================

class TestUnregisterPlanet:
    def test_removes_from_id_registry(self, registry, galaxy, system):
        planet = _MockPlanet(location=HexCoord(1, 0))
        registry.register_planet(system, planet)

        registry.unregister_planet(planet)

        assert planet.id not in galaxy.planets_by_id

    def test_removes_from_reverse_lookup(self, registry, galaxy, system):
        planet = _MockPlanet(location=HexCoord(1, 0))
        registry.register_planet(system, planet)

        registry.unregister_planet(planet)

        assert planet not in galaxy._planet_to_system

    def test_removes_from_spatial_index(self, registry, galaxy, system):
        planet = _MockPlanet(location=HexCoord(1, 0))
        registry.register_planet(system, planet)

        registry.unregister_planet(planet)

        global_hex = system.global_location + planet.location
        assert global_hex not in galaxy._global_hex_planets

    def test_removes_from_system_planets_list(self, registry, system):
        planet = _MockPlanet(location=HexCoord(1, 0))
        system.planets.append(planet)
        registry.register_planet(system, planet)

        registry.unregister_planet(planet)

        assert planet not in system.planets

    def test_unregister_nonexistent_planet_does_not_raise(self, registry):
        """Unregistering a planet that was never registered is a no-op."""
        planet = _MockPlanet(location=HexCoord(0, 0))
        planet.id = 999

        # Should not raise
        registry.unregister_planet(planet)

    def test_unregister_cleans_up_zone_for_multihex_planet(self, registry, galaxy, system):
        planet = _MockPlanet(location=HexCoord(0, 1), radius_hexes=1)
        registry.register_planet(system, planet)
        assert id(planet) in galaxy._zone_to_system

        registry.unregister_planet(planet)

        assert id(planet) not in galaxy._zone_to_system

    def test_other_planets_at_same_hex_survive_unregister(self, registry, galaxy, system):
        """Unregistering one planet does not remove a co-located planet."""
        p1 = _MockPlanet(location=HexCoord(1, 0))
        p2 = _MockPlanet(location=HexCoord(1, 0))
        registry.register_planet(system, p1)
        registry.register_planet(system, p2)

        registry.unregister_planet(p1)

        global_hex = system.global_location + HexCoord(1, 0)
        assert p2 in galaxy._global_hex_planets[global_hex]
        assert p1 not in galaxy._global_hex_planets[global_hex]


# ===========================================================================
# Fleet registration
# ===========================================================================

class TestFleetRegistration:
    def test_register_fleet_enables_id_lookup(self, registry, galaxy):
        fleet = _MockFleet(fleet_id=10)
        registry.register_fleet(fleet)

        assert galaxy.fleets_by_id[10] is fleet

    def test_register_same_id_overwrites(self, registry, galaxy):
        fleet_a = _MockFleet(fleet_id=1)
        fleet_b = _MockFleet(fleet_id=1)
        registry.register_fleet(fleet_a)
        registry.register_fleet(fleet_b)

        assert galaxy.fleets_by_id[1] is fleet_b


class TestGetFleetById:
    def test_returns_registered_fleet(self, registry):
        fleet = _MockFleet(fleet_id=7)
        registry.register_fleet(fleet)

        assert registry.get_fleet_by_id(7) is fleet

    def test_returns_none_for_missing_id(self, registry):
        assert registry.get_fleet_by_id(42) is None


class TestUnregisterFleet:
    def test_removes_fleet_from_registry(self, registry, galaxy):
        fleet = _MockFleet(fleet_id=3)
        registry.register_fleet(fleet)

        registry.unregister_fleet(fleet)

        assert 3 not in galaxy.fleets_by_id

    def test_unregister_nonexistent_fleet_is_noop(self, registry):
        fleet = _MockFleet(fleet_id=999)
        # Should not raise
        registry.unregister_fleet(fleet)


# ===========================================================================
# Zone registration
# ===========================================================================

class TestZoneRegistration:
    def test_register_zone_indexes_all_occupied_hexes(self, registry, galaxy, system):
        zone = _MockZone(hexes=[HexCoord(0, 0), HexCoord(1, 0)])
        registry.register_zone(system, zone)

        for local_hex in zone.occupied_hexes:
            global_hex = system.global_location + local_hex
            assert zone in galaxy._global_hex_zones[global_hex]

    def test_register_zone_adds_reverse_lookup(self, registry, galaxy, system):
        zone = _MockZone(hexes=[HexCoord(0, 0)])
        registry.register_zone(system, zone)

        assert galaxy._zone_to_system[id(zone)] is system

    def test_register_zone_ignores_non_zone_occupant(self, registry, galaxy, system):
        """An object without occupied_hexes is silently skipped."""
        not_a_zone = object()
        registry.register_zone(system, not_a_zone)

        assert len(galaxy._global_hex_zones) == 0
        assert len(galaxy._zone_to_system) == 0

    def test_register_zone_is_idempotent(self, registry, galaxy, system):
        """Registering the same zone twice does not duplicate entries."""
        zone = _MockZone(hexes=[HexCoord(0, 0)])
        registry.register_zone(system, zone)
        registry.register_zone(system, zone)

        global_hex = system.global_location + HexCoord(0, 0)
        assert galaxy._global_hex_zones[global_hex].count(zone) == 1


class TestUnregisterZone:
    def test_unregister_removes_from_all_indexes(self, registry, galaxy, system):
        zone = _MockZone(hexes=[HexCoord(0, 0), HexCoord(1, 0)])
        registry.register_zone(system, zone)

        registry.unregister_zone(system, zone)

        assert id(zone) not in galaxy._zone_to_system
        for local_hex in zone.occupied_hexes:
            global_hex = system.global_location + local_hex
            assert global_hex not in galaxy._global_hex_zones

    def test_unregister_nonexistent_zone_is_noop(self, registry, system):
        zone = _MockZone(hexes=[HexCoord(0, 0)])
        # Should not raise
        registry.unregister_zone(system, zone)

    def test_unregister_zone_ignores_non_zone_occupant(self, registry, system):
        not_a_zone = object()
        # Should not raise
        registry.unregister_zone(system, not_a_zone)
