"""Unit tests for GalaxySpatialIndex.

Tests spatial query operations: locating systems, planets, zones,
and warp points by hex coordinate.
"""

import pytest
from game.core.hex_math import HexCoord
from game.strategy.data.galaxy_spatial_index import GalaxySpatialIndex


# ---------------------------------------------------------------------------
# Lightweight test doubles
# ---------------------------------------------------------------------------

class _MockGalaxy:
    """Minimal Galaxy substitute with only the state dicts that
    GalaxySpatialIndex reads."""

    def __init__(self):
        self.systems = {}                  # HexCoord -> StarSystem
        self._planet_to_system = {}        # Planet -> StarSystem
        self._global_hex_planets = {}      # HexCoord -> List[Planet]
        self._global_hex_zones = {}        # HexCoord -> List[object]
        self._zone_to_system = {}          # id(obj) -> StarSystem
        self._global_hex_warp_points = {}  # HexCoord -> StarSystem


class _MockStarSystem:
    def __init__(self, global_location: HexCoord, name: str = "TestSystem"):
        self.name = name
        self.global_location = global_location
        self.planets = []
        self.stars = []
        self.warp_points = []
        self.storms = []


class _MockPlanet:
    """Planet-like object. Uses a class-level flag so isinstance() checks in
    the production code work (GalaxySpatialIndex imports Planet for routing)."""

    def __init__(self, location: HexCoord, radius_hexes: int = 0):
        self.id = None
        self.location = location
        self.radius_hexes = radius_hexes
        self.occupied_hexes = [location] if radius_hexes > 0 else []


class _MockFleet:
    def __init__(self, location: HexCoord):
        self.location = location


class _MockWarpPoint:
    def __init__(self, location: HexCoord, destination_id: str = "dest"):
        self.location = location
        self.destination_id = destination_id


class _MockZone:
    """Zone occupant (star / Dyson Sphere) with occupied_hexes."""

    def __init__(self, hexes: list[HexCoord]):
        self.location = hexes[0] if hexes else HexCoord(0, 0)
        self.occupied_hexes = hexes


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def galaxy():
    return _MockGalaxy()


@pytest.fixture
def spatial(galaxy):
    return GalaxySpatialIndex(galaxy)


# ===========================================================================
# get_planets_at_global_hex
# ===========================================================================

class TestGetPlanetsAtGlobalHex:
    def test_returns_empty_list_for_empty_index(self, spatial):
        assert spatial.get_planets_at_global_hex(HexCoord(0, 0)) == []

    def test_returns_planets_registered_at_hex(self, spatial, galaxy):
        planet = _MockPlanet(location=HexCoord(1, 0))
        global_hex = HexCoord(6, 5)
        galaxy._global_hex_planets[global_hex] = [planet]

        result = spatial.get_planets_at_global_hex(global_hex)

        assert result == [planet]

    def test_returns_multiple_planets_at_same_hex(self, spatial, galaxy):
        p1 = _MockPlanet(location=HexCoord(1, 0))
        p2 = _MockPlanet(location=HexCoord(1, 0))
        hex_ = HexCoord(10, 10)
        galaxy._global_hex_planets[hex_] = [p1, p2]

        assert len(spatial.get_planets_at_global_hex(hex_)) == 2

    def test_does_not_return_planets_at_different_hex(self, spatial, galaxy):
        planet = _MockPlanet(location=HexCoord(1, 0))
        galaxy._global_hex_planets[HexCoord(1, 1)] = [planet]

        assert spatial.get_planets_at_global_hex(HexCoord(2, 2)) == []


# ===========================================================================
# get_zones_at_global_hex
# ===========================================================================

class TestGetZonesAtGlobalHex:
    def test_returns_empty_for_unregistered_hex(self, spatial):
        assert spatial.get_zones_at_global_hex(HexCoord(0, 0)) == []

    def test_returns_zone_at_registered_hex(self, spatial, galaxy):
        zone = _MockZone(hexes=[HexCoord(0, 0)])
        global_hex = HexCoord(5, 5)
        galaxy._global_hex_zones[global_hex] = [zone]

        assert spatial.get_zones_at_global_hex(global_hex) == [zone]


# ===========================================================================
# get_planet_global_hex
# ===========================================================================

class TestGetPlanetGlobalHex:
    def test_returns_global_hex_for_registered_planet(self, spatial, galaxy):
        system = _MockStarSystem(global_location=HexCoord(10, 20))
        planet = _MockPlanet(location=HexCoord(1, -1))
        galaxy._planet_to_system[planet] = system

        result = spatial.get_planet_global_hex(planet)

        assert result == HexCoord(11, 19)

    def test_returns_none_for_unregistered_planet(self, spatial):
        planet = _MockPlanet(location=HexCoord(1, 0))

        assert spatial.get_planet_global_hex(planet) is None


# ===========================================================================
# get_system_of_planet
# ===========================================================================

class TestGetSystemOfPlanet:
    def test_returns_system_for_registered_planet(self, spatial, galaxy):
        system = _MockStarSystem(global_location=HexCoord(5, 5))
        planet = _MockPlanet(location=HexCoord(1, 0))
        galaxy._planet_to_system[planet] = system

        assert spatial.get_system_of_planet(planet) is system

    def test_returns_none_for_unregistered_planet(self, spatial):
        planet = _MockPlanet(location=HexCoord(1, 0))

        assert spatial.get_system_of_planet(planet) is None


# ===========================================================================
# get_system_of_object
# ===========================================================================

class TestGetSystemOfObject:
    def test_returns_system_when_fleet_at_system_location(self, spatial, galaxy):
        system = _MockStarSystem(global_location=HexCoord(5, 5))
        galaxy.systems[HexCoord(5, 5)] = system
        fleet = _MockFleet(location=HexCoord(5, 5))

        assert spatial.get_system_of_object(fleet) is system

    def test_returns_none_for_fleet_in_deep_space(self, spatial, galaxy):
        system = _MockStarSystem(global_location=HexCoord(5, 5))
        galaxy.systems[HexCoord(5, 5)] = system
        fleet = _MockFleet(location=HexCoord(99, 99))

        assert spatial.get_system_of_object(fleet) is None

    def test_returns_none_for_object_without_location(self, spatial):
        obj = object()  # no location attribute

        assert spatial.get_system_of_object(obj) is None

    def test_auto_routes_real_planet_to_planet_lookup(self, spatial, galaxy):
        """When passed an actual Planet instance, delegates to
        get_system_of_planet (which uses the planet-to-system reverse map
        rather than global location matching)."""
        from game.strategy.data.planet import Planet

        system = _MockStarSystem(global_location=HexCoord(5, 5))
        # Create a real Planet to trigger the isinstance check.
        # Must set enough attrs for Planet.__hash__ (name, location, orbit_distance).
        planet = Planet.__new__(Planet)
        planet.name = "TestPlanet"
        planet.location = HexCoord(1, 0)
        planet.orbit_distance = 1
        planet.id = 1
        galaxy._planet_to_system[planet] = system

        assert spatial.get_system_of_object(planet) is system


# ===========================================================================
# get_system_at_location  (unified lookup)
# ===========================================================================

class TestGetSystemAtLocation:
    def test_returns_system_at_direct_location(self, spatial, galaxy):
        system = _MockStarSystem(global_location=HexCoord(3, 3))
        galaxy.systems[HexCoord(3, 3)] = system

        assert spatial.get_system_at_location(HexCoord(3, 3)) is system

    def test_returns_system_via_planet_index(self, spatial, galaxy):
        system = _MockStarSystem(global_location=HexCoord(5, 5))
        planet = _MockPlanet(location=HexCoord(1, 0))
        planet_hex = HexCoord(6, 5)
        galaxy._global_hex_planets[planet_hex] = [planet]
        galaxy._planet_to_system[planet] = system

        assert spatial.get_system_at_location(planet_hex) is system

    def test_returns_system_via_zone_index(self, spatial, galaxy):
        system = _MockStarSystem(global_location=HexCoord(5, 5))
        zone = _MockZone(hexes=[HexCoord(0, 0)])
        zone_hex = HexCoord(5, 5)
        galaxy._global_hex_zones[zone_hex] = [zone]
        galaxy._zone_to_system[id(zone)] = system

        assert spatial.get_system_at_location(zone_hex) is system

    def test_returns_system_via_warp_point_index(self, spatial, galaxy):
        system = _MockStarSystem(global_location=HexCoord(5, 5))
        wp_hex = HexCoord(7, 5)
        galaxy._global_hex_warp_points[wp_hex] = system

        assert spatial.get_system_at_location(wp_hex) is system

    def test_returns_none_for_deep_space(self, spatial):
        assert spatial.get_system_at_location(HexCoord(99, 99)) is None

    def test_priority_direct_system_over_planet(self, spatial, galaxy):
        """If a hex is both a system location AND has a planet, the direct
        system match wins (short-circuit)."""
        system = _MockStarSystem(global_location=HexCoord(5, 5))
        galaxy.systems[HexCoord(5, 5)] = system
        # Also has planet data at same hex
        planet = _MockPlanet(location=HexCoord(0, 0))
        galaxy._global_hex_planets[HexCoord(5, 5)] = [planet]

        assert spatial.get_system_at_location(HexCoord(5, 5)) is system


# ===========================================================================
# get_all_fleets_in_system
# ===========================================================================

class _MockEmpire:
    def __init__(self, fleets: list):
        self.fleets = fleets


class TestGetAllFleetsInSystem:
    def test_finds_fleet_at_system_global_location(self, spatial):
        system = _MockStarSystem(global_location=HexCoord(5, 5))
        fleet = _MockFleet(location=HexCoord(5, 5))
        empire = _MockEmpire(fleets=[fleet])

        result = spatial.get_all_fleets_in_system(system, [empire])

        assert result == [(empire, fleet)]

    def test_finds_fleet_at_planet_location(self, spatial):
        system = _MockStarSystem(global_location=HexCoord(5, 5))
        planet = _MockPlanet(location=HexCoord(1, 0))
        system.planets = [planet]
        fleet = _MockFleet(location=HexCoord(6, 5))
        empire = _MockEmpire(fleets=[fleet])

        result = spatial.get_all_fleets_in_system(system, [empire])

        assert (empire, fleet) in result

    def test_finds_fleet_at_warp_point_location(self, spatial):
        system = _MockStarSystem(global_location=HexCoord(5, 5))
        wp = _MockWarpPoint(location=HexCoord(2, 0))
        system.warp_points = [wp]
        fleet = _MockFleet(location=HexCoord(7, 5))
        empire = _MockEmpire(fleets=[fleet])

        result = spatial.get_all_fleets_in_system(system, [empire])

        assert (empire, fleet) in result

    def test_does_not_find_fleet_outside_system(self, spatial):
        system = _MockStarSystem(global_location=HexCoord(5, 5))
        fleet = _MockFleet(location=HexCoord(99, 99))
        empire = _MockEmpire(fleets=[fleet])

        result = spatial.get_all_fleets_in_system(system, [empire])

        assert result == []

    def test_finds_fleets_from_multiple_empires(self, spatial):
        system = _MockStarSystem(global_location=HexCoord(5, 5))
        fleet_a = _MockFleet(location=HexCoord(5, 5))
        fleet_b = _MockFleet(location=HexCoord(5, 5))
        empire_a = _MockEmpire(fleets=[fleet_a])
        empire_b = _MockEmpire(fleets=[fleet_b])

        result = spatial.get_all_fleets_in_system(system, [empire_a, empire_b])

        assert len(result) == 2

    def test_returns_empty_for_no_empires(self, spatial):
        system = _MockStarSystem(global_location=HexCoord(5, 5))

        assert spatial.get_all_fleets_in_system(system, []) == []

    def test_finds_fleet_at_star_zone_hex(self, spatial):
        """Fleet at a star's zone hex (multi-hex star) is found."""
        system = _MockStarSystem(global_location=HexCoord(5, 5))
        star = _MockZone(hexes=[HexCoord(0, 0), HexCoord(1, 0)])
        star.location = HexCoord(0, 0)
        system.stars = [star]

        # Fleet at star's second occupied hex
        fleet = _MockFleet(location=HexCoord(6, 5))
        empire = _MockEmpire(fleets=[fleet])

        result = spatial.get_all_fleets_in_system(system, [empire])

        assert (empire, fleet) in result
