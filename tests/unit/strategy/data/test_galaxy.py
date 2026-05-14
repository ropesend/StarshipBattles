"""
Unit tests for Galaxy class.

Tests core galaxy functionality including system lookups, name mapping,
and zone registry (PROJ-139).
"""

import pytest
from game.strategy.data.galaxy import Galaxy
from game.strategy.data.star_system import StarSystem
from game.strategy.data.spectrum import Spectrum
from game.strategy.data.stars import Star, StarType
from game.strategy.data.planet import Planet, PlanetType
from game.core.hex_math import HexCoord


def make_test_star(name="TestStar", radius_hexes=1, location=None):
    """Create a minimal Star for testing zone functionality."""
    if location is None:
        location = HexCoord(0, 0)
    return Star(
        name=name,
        mass=1.0,
        radius_hexes=radius_hexes,
        temperature=5778,
        luminosity=1.0,
        spectrum=Spectrum(
            gamma_ray=0.1, xray=0.2, ultraviolet=0.3, blue=0.4, green=0.5,
            red=0.6, infrared=0.7, microwave=0.8, radio=0.9
        ),
        star_type=StarType.MAIN_SEQUENCE,
        color=(255, 200, 150),
        age=4.6e9,
        location=location
    )


def make_test_planet(name="TestPlanet", planet_type=PlanetType.BARREN,
                     location=None, radius_hexes=0):
    """Create a minimal Planet for testing zone functionality."""
    if location is None:
        location = HexCoord(0, 0)
    return Planet(
        name=name,
        location=location,
        orbit_distance=1,
        mass=5.972e24,  # Earth mass
        radius=6.371e6,  # Earth radius
        surface_area=5.1e14,
        density=5515,
        surface_gravity=9.81,
        surface_pressure=101325,
        surface_temperature=288,
        surface_water=0.7,
        tectonic_activity=0.5,
        magnetic_field=1.0,
        planet_type=planet_type,
        radius_hexes=radius_hexes
    )


class TestGalaxyNameMap:
    """Tests for Galaxy name_map and get_system_by_name()."""

    def test_get_system_by_name_returns_correct_system(self):
        """get_system_by_name() should return the system with matching name."""
        galaxy = Galaxy(radius=1000)
        system = StarSystem(name="Alpha", global_location=HexCoord(0, 0))
        galaxy.add_system(system)

        result = galaxy.get_system_by_name("Alpha")

        assert result is system

    def test_get_system_by_name_returns_none_for_unknown_name(self):
        """get_system_by_name() should return None for unknown names."""
        galaxy = Galaxy(radius=1000)
        system = StarSystem(name="Alpha", global_location=HexCoord(0, 0))
        galaxy.add_system(system)

        result = galaxy.get_system_by_name("Unknown")

        assert result is None

    def test_get_system_by_name_empty_galaxy(self):
        """get_system_by_name() should return None for empty galaxy."""
        galaxy = Galaxy(radius=1000)

        result = galaxy.get_system_by_name("Alpha")

        assert result is None

    def test_name_map_populated_on_add_system(self):
        """add_system() should populate name_map."""
        galaxy = Galaxy(radius=1000)
        system = StarSystem(name="Beta", global_location=HexCoord(10, 20))

        galaxy.add_system(system)

        assert "Beta" in galaxy.name_map
        assert galaxy.name_map["Beta"] is system

    def test_name_map_with_multiple_systems(self):
        """name_map should contain all added systems."""
        galaxy = Galaxy(radius=1000)
        s1 = StarSystem(name="Alpha", global_location=HexCoord(0, 0))
        s2 = StarSystem(name="Beta", global_location=HexCoord(100, 0))
        s3 = StarSystem(name="Gamma", global_location=HexCoord(0, 100))

        galaxy.add_system(s1)
        galaxy.add_system(s2)
        galaxy.add_system(s3)

        assert galaxy.get_system_by_name("Alpha") is s1
        assert galaxy.get_system_by_name("Beta") is s2
        assert galaxy.get_system_by_name("Gamma") is s3

    def test_get_system_by_name_is_case_sensitive(self):
        """get_system_by_name() should be case-sensitive."""
        galaxy = Galaxy(radius=1000)
        system = StarSystem(name="Alpha", global_location=HexCoord(0, 0))
        galaxy.add_system(system)

        # Exact match works
        assert galaxy.get_system_by_name("Alpha") is system
        # Different case returns None
        assert galaxy.get_system_by_name("alpha") is None
        assert galaxy.get_system_by_name("ALPHA") is None

    def test_name_map_preserved_after_from_dict(self):
        """name_map should be rebuilt correctly after deserialization."""
        galaxy = Galaxy(radius=1000)
        s1 = StarSystem(name="Alpha", global_location=HexCoord(0, 0))
        s2 = StarSystem(name="Beta", global_location=HexCoord(100, 0))
        galaxy.add_system(s1)
        galaxy.add_system(s2)

        # Serialize and deserialize
        data = galaxy.to_dict()
        restored = Galaxy.from_dict(data)

        # Name map should work on restored galaxy
        assert restored.get_system_by_name("Alpha") is not None
        assert restored.get_system_by_name("Alpha").name == "Alpha"
        assert restored.get_system_by_name("Beta") is not None
        assert restored.get_system_by_name("Beta").name == "Beta"
        assert restored.get_system_by_name("Unknown") is None


class TestGalaxySystemLookup:
    """Tests for system coordinate lookups."""

    def test_systems_dict_keyed_by_coord(self):
        """systems dict should be keyed by HexCoord."""
        galaxy = Galaxy(radius=1000)
        coord = HexCoord(5, 10)
        system = StarSystem(name="Test", global_location=coord)
        galaxy.add_system(system)

        assert coord in galaxy.systems
        assert galaxy.systems[coord] is system

    def test_add_system_updates_both_maps(self):
        """add_system() should update both systems and name_map."""
        galaxy = Galaxy(radius=1000)
        coord = HexCoord(42, -10)
        system = StarSystem(name="Dual", global_location=coord)

        galaxy.add_system(system)

        # Both lookups should work
        assert galaxy.systems[coord] is system
        assert galaxy.name_map["Dual"] is system
        assert galaxy.get_system_by_name("Dual") is system


class TestGalaxyPlanetGlobalHex:
    """Tests for get_planet_global_hex() method."""

    def test_returns_correct_global_hex(self):
        """Registered planet returns system.global_location + planet.location."""
        galaxy = Galaxy(radius=1000)
        system = StarSystem(name="Test", global_location=HexCoord(10, 5))
        planet = make_test_planet(name="TestPlanet", location=HexCoord(1, 2))
        system.planets.append(planet)
        galaxy.add_system(system)
        galaxy.register_planet(system, planet)

        result = galaxy.get_planet_global_hex(planet)

        assert result == HexCoord(11, 7)

    def test_returns_none_for_unregistered_planet(self):
        """Unregistered planet returns None."""
        galaxy = Galaxy(radius=1000)
        planet = make_test_planet(name="Orphan")

        result = galaxy.get_planet_global_hex(planet)

        assert result is None


class TestGalaxyZoneRegistry:
    """Tests for PROJ-139 Zone Registry functionality."""

    def test_register_zone_adds_to_all_hexes(self):
        """register_zone() should add object to all its occupied hexes."""
        galaxy = Galaxy(radius=1000)
        # Create a star with diameter 3 (radius=2 -> 19 hexes)
        star = make_test_star(radius_hexes=2)
        system = StarSystem(name="Test", global_location=HexCoord(10, 20), stars=[star])

        galaxy.register_zone(system, star)

        # Should be registered at all occupied hexes
        for local_hex in star.occupied_hexes:
            global_hex = system.global_location + local_hex
            assert star in galaxy.get_zones_at_global_hex(global_hex)

    def test_unregister_zone_removes_from_all_hexes(self):
        """unregister_zone() should remove object from all its occupied hexes."""
        galaxy = Galaxy(radius=1000)
        star = make_test_star(radius_hexes=2)
        system = StarSystem(name="Test", global_location=HexCoord(10, 20), stars=[star])

        galaxy.register_zone(system, star)
        galaxy.unregister_zone(system, star)

        # Should no longer be at any hex
        for local_hex in star.occupied_hexes:
            global_hex = system.global_location + local_hex
            assert star not in galaxy.get_zones_at_global_hex(global_hex)

    def test_get_zones_at_global_hex_returns_object(self):
        """get_zones_at_global_hex() should return objects at that hex."""
        galaxy = Galaxy(radius=1000)
        star = make_test_star(radius_hexes=1)
        system = StarSystem(name="Test", global_location=HexCoord(5, 5), stars=[star])

        galaxy.register_zone(system, star)

        # Query at center hex
        result = galaxy.get_zones_at_global_hex(HexCoord(5, 5))
        assert star in result

    def test_get_zones_at_global_hex_empty_returns_empty_list(self):
        """get_zones_at_global_hex() should return empty list for empty hex."""
        galaxy = Galaxy(radius=1000)

        result = galaxy.get_zones_at_global_hex(HexCoord(100, 100))

        assert result == []

    def test_register_zone_no_duplicates(self):
        """Registering the same zone twice should not create duplicates."""
        galaxy = Galaxy(radius=1000)
        star = make_test_star(radius_hexes=1)
        system = StarSystem(name="Test", global_location=HexCoord(0, 0), stars=[star])

        galaxy.register_zone(system, star)
        galaxy.register_zone(system, star)

        # Count occurrences at center hex
        result = galaxy.get_zones_at_global_hex(HexCoord(0, 0))
        assert result.count(star) == 1

    def test_add_system_registers_star_zones(self):
        """add_system() should automatically register star zones."""
        galaxy = Galaxy(radius=1000)
        star = make_test_star(radius_hexes=2)
        system = StarSystem(name="Test", global_location=HexCoord(50, 50), stars=[star])

        galaxy.add_system(system)

        # Star zones should be registered
        for local_hex in star.occupied_hexes:
            global_hex = system.global_location + local_hex
            assert star in galaxy.get_zones_at_global_hex(global_hex)

    def test_from_dict_rebuilds_star_zones(self):
        """from_dict() should rebuild star zone registry."""
        galaxy = Galaxy(radius=1000)
        star = make_test_star(name="TestStar", radius_hexes=2)
        system = StarSystem(name="Test", global_location=HexCoord(30, 40), stars=[star])
        galaxy.add_system(system)

        # Serialize and deserialize
        data = galaxy.to_dict()
        restored = Galaxy.from_dict(data)

        # Zone registry should be rebuilt
        restored_system = restored.get_system_by_name("Test")
        restored_star = restored_system.stars[0]
        for local_hex in restored_star.occupied_hexes:
            global_hex = restored_system.global_location + local_hex
            zones = restored.get_zones_at_global_hex(global_hex)
            assert any(s.name == "TestStar" for s in zones)

    def test_register_dyson_sphere_planet_creates_zones(self):
        """register_planet() should create zones for multi-hex planets."""
        galaxy = Galaxy(radius=1000)
        system = StarSystem(name="Test", global_location=HexCoord(0, 0))
        galaxy.add_system(system)

        # Create Dyson Sphere planet with radius_hexes
        dyson = make_test_planet(
            name="Dyson Sphere",
            planet_type=PlanetType.DYSON_SPHERE,
            location=HexCoord(0, 0),
            radius_hexes=6  # center + 5 rings = 91 hexes
        )
        system.planets.append(dyson)
        galaxy.register_planet(system, dyson)

        # Dyson zone should be registered at all occupied hexes
        for local_hex in dyson.occupied_hexes:
            global_hex = system.global_location + local_hex
            assert dyson in galaxy.get_zones_at_global_hex(global_hex)

    def test_unregister_dyson_sphere_planet_removes_zones(self):
        """unregister_planet() should remove zones for multi-hex planets."""
        galaxy = Galaxy(radius=1000)
        system = StarSystem(name="Test", global_location=HexCoord(0, 0))
        galaxy.add_system(system)

        dyson = make_test_planet(
            name="Dyson Sphere",
            planet_type=PlanetType.DYSON_SPHERE,
            location=HexCoord(0, 0),
            radius_hexes=6
        )
        system.planets.append(dyson)
        galaxy.register_planet(system, dyson)
        galaxy.unregister_planet(dyson)

        # Dyson zone should be removed
        for local_hex in dyson.occupied_hexes:
            global_hex = system.global_location + local_hex
            assert dyson not in galaxy.get_zones_at_global_hex(global_hex)

    def test_get_system_at_location_finds_system_via_star_zone(self):
        """get_system_at_location() should find system via star zone hex."""
        galaxy = Galaxy(radius=1000)
        # Star with diameter 5 -> radius 3 -> zone extends 3 hexes from center
        star = make_test_star(name="BigStar", radius_hexes=3)
        system = StarSystem(name="Test", global_location=HexCoord(100, 100), stars=[star])
        galaxy.add_system(system)

        # Query at an outer zone hex (offset from center)
        zone_hex = HexCoord(100 + 2, 100)  # 2 hexes right of center (within radius 3)

        result = galaxy.get_system_at_location(zone_hex)

        assert result is system

    def test_get_system_at_location_finds_system_via_dyson_zone(self):
        """get_system_at_location() should find system via Dyson Sphere zone."""
        galaxy = Galaxy(radius=1000)
        system = StarSystem(name="Test", global_location=HexCoord(200, 200))
        galaxy.add_system(system)

        dyson = make_test_planet(
            name="Dyson Sphere",
            planet_type=PlanetType.DYSON_SPHERE,
            location=HexCoord(0, 0),
            radius_hexes=6
        )
        system.planets.append(dyson)
        galaxy.register_planet(system, dyson)

        # Query at zone hex (5 hexes from center, within radius 6)
        zone_hex = HexCoord(200 + 5, 200)

        result = galaxy.get_system_at_location(zone_hex)

        assert result is system

    def test_get_all_fleets_in_system_includes_zone_hexes(self):
        """get_all_fleets_in_system() should include star and Dyson zone hexes."""
        galaxy = Galaxy(radius=1000)
        star = make_test_star(radius_hexes=2)
        system = StarSystem(name="Test", global_location=HexCoord(0, 0), stars=[star])
        galaxy.add_system(system)

        # Create a mock empire with a fleet at a zone hex
        class MockFleet:
            def __init__(self, loc):
                self.location = loc

        class MockEmpire:
            def __init__(self, fleets):
                self.fleets = fleets

        # Fleet at zone hex (1, 0) which is in star's zone (radius 2)
        fleet = MockFleet(HexCoord(1, 0))
        empire = MockEmpire([fleet])

        result = galaxy.get_all_fleets_in_system(system, [empire])

        assert len(result) == 1
        assert result[0] == (empire, fleet)


class TestZoneSerializationRoundTrip:
    """Tests for zone registry preservation across serialization."""

    def test_dyson_sphere_zones_rebuilt_after_from_dict(self):
        """from_dict() should rebuild Dyson Sphere zone registry."""
        galaxy = Galaxy(radius=1000)
        star = make_test_star(name="Sol", radius_hexes=2)
        system = StarSystem(name="Test", global_location=HexCoord(50, 50), stars=[star])
        galaxy.add_system(system)

        # Create Dyson Sphere planet with radius_hexes
        dyson = make_test_planet(
            name="Dyson Sphere",
            planet_type=PlanetType.DYSON_SPHERE,
            location=HexCoord(5, 0),
            radius_hexes=6  # center + 5 rings = 91 hexes
        )
        system.planets.append(dyson)
        galaxy.register_planet(system, dyson)

        # Serialize and deserialize
        data = galaxy.to_dict()
        restored = Galaxy.from_dict(data)

        # Dyson zone should be rebuilt
        restored_system = restored.get_system_by_name("Test")
        restored_dyson = next(p for p in restored_system.planets if p.name == "Dyson Sphere")

        # Check zone exists at multiple zone hexes
        for local_hex in restored_dyson.occupied_hexes:
            global_hex = restored_system.global_location + local_hex
            zones = restored.get_zones_at_global_hex(global_hex)
            assert any(p.name == "Dyson Sphere" for p in zones), \
                f"Dyson zone not rebuilt at {global_hex}"

    def test_planet_radius_hexes_preserved_after_from_dict(self):
        """Planet.radius_hexes should be preserved through serialization."""
        galaxy = Galaxy(radius=1000)
        system = StarSystem(name="Test", global_location=HexCoord(0, 0))
        galaxy.add_system(system)

        dyson = make_test_planet(
            name="Dyson Test",
            planet_type=PlanetType.DYSON_SPHERE,
            location=HexCoord(0, 0),
            radius_hexes=6
        )
        system.planets.append(dyson)
        galaxy.register_planet(system, dyson)

        # Serialize and deserialize
        data = galaxy.to_dict()
        restored = Galaxy.from_dict(data)

        restored_system = restored.get_system_by_name("Test")
        restored_dyson = next(p for p in restored_system.planets if p.name == "Dyson Test")

        # radius_hexes should be preserved
        assert restored_dyson.radius_hexes == 6

    def test_star_zones_and_dyson_zones_coexist_after_from_dict(self):
        """from_dict() should rebuild both star and Dyson Sphere zones correctly."""
        galaxy = Galaxy(radius=1000)
        star = make_test_star(name="BigStar", radius_hexes=3)  # center + 2 rings = 19 hexes
        system = StarSystem(name="Test", global_location=HexCoord(0, 0), stars=[star])
        galaxy.add_system(system)

        # Add Dyson Sphere far from star
        dyson = make_test_planet(
            name="Dyson",
            planet_type=PlanetType.DYSON_SPHERE,
            location=HexCoord(20, 0),
            radius_hexes=6
        )
        system.planets.append(dyson)
        galaxy.register_planet(system, dyson)

        # Serialize and deserialize
        data = galaxy.to_dict()
        restored = Galaxy.from_dict(data)

        restored_system = restored.get_system_by_name("Test")
        restored_star = restored_system.stars[0]
        restored_dyson = next(p for p in restored_system.planets if p.name == "Dyson")

        # Star zones rebuilt
        star_zone_hex = restored_system.global_location + HexCoord(2, 0)
        star_zones = restored.get_zones_at_global_hex(star_zone_hex)
        assert any(hasattr(z, 'star_type') for z in star_zones), "Star zone not rebuilt"

        # Dyson zones rebuilt
        dyson_zone_hex = restored_system.global_location + HexCoord(20 + 3, 0)
        dyson_zones = restored.get_zones_at_global_hex(dyson_zone_hex)
        assert any(p.name == "Dyson" for p in dyson_zones), "Dyson zone not rebuilt"


class TestRestorePlanet:
    """Tests for restore_planet() method (PROJ-179 Phase 2)."""

    def test_restore_planet_preserves_existing_id(self):
        """restore_planet() should preserve planet's existing ID, not reassign."""
        galaxy = Galaxy(radius=1000)
        system = StarSystem(name="Test", global_location=HexCoord(0, 0))
        galaxy.add_system(system)

        planet = make_test_planet(name="Preserved", location=HexCoord(3, 0))
        planet.id = 42  # Pre-set ID (simulating deserialization)
        system.planets.append(planet)

        galaxy._registry.restore_planet(system, planet)

        # ID should be preserved, not changed
        assert planet.id == 42
        assert galaxy.planets_by_id[42] is planet

    def test_restore_planet_registers_in_spatial_index(self):
        """restore_planet() should register planet in spatial index."""
        galaxy = Galaxy(radius=1000)
        system = StarSystem(name="Test", global_location=HexCoord(10, 20))
        galaxy.add_system(system)

        planet = make_test_planet(name="Indexed", location=HexCoord(5, 5))
        planet.id = 100
        system.planets.append(planet)

        galaxy._registry.restore_planet(system, planet)

        # Should be in spatial index
        global_hex = HexCoord(15, 25)  # system(10,20) + planet(5,5)
        assert planet in galaxy.get_planets_at_global_hex(global_hex)

    def test_restore_planet_enables_get_system_of_planet(self):
        """restore_planet() should enable get_system_of_planet() lookup."""
        galaxy = Galaxy(radius=1000)
        system = StarSystem(name="Test", global_location=HexCoord(0, 0))
        galaxy.add_system(system)

        planet = make_test_planet(name="Findable", location=HexCoord(2, 3))
        planet.id = 200
        system.planets.append(planet)

        galaxy._registry.restore_planet(system, planet)

        assert galaxy.get_system_of_planet(planet) is system

    def test_restore_planet_registers_multi_hex_zones(self):
        """restore_planet() should register zones for multi-hex planets."""
        galaxy = Galaxy(radius=1000)
        system = StarSystem(name="Test", global_location=HexCoord(0, 0))
        galaxy.add_system(system)

        dyson = make_test_planet(
            name="Restored Dyson",
            planet_type=PlanetType.DYSON_SPHERE,
            location=HexCoord(0, 0),
            radius_hexes=6
        )
        dyson.id = 300
        system.planets.append(dyson)

        galaxy._registry.restore_planet(system, dyson)

        # Zone should be registered
        for local_hex in dyson.occupied_hexes:
            global_hex = system.global_location + local_hex
            assert dyson in galaxy.get_zones_at_global_hex(global_hex)

    def test_from_dict_preserves_planet_ids(self):
        """Galaxy.from_dict() should preserve planet IDs (not reassign)."""
        galaxy = Galaxy(radius=1000)
        system = StarSystem(name="Test", global_location=HexCoord(0, 0))
        galaxy.add_system(system)

        # Register planets with known IDs
        planet1 = make_test_planet(name="Planet1", location=HexCoord(1, 0))
        planet2 = make_test_planet(name="Planet2", location=HexCoord(2, 0))
        planet3 = make_test_planet(name="Planet3", location=HexCoord(3, 0))
        system.planets.extend([planet1, planet2, planet3])
        galaxy.register_planet(system, planet1)
        galaxy.register_planet(system, planet2)
        galaxy.register_planet(system, planet3)

        # Record original IDs
        original_ids = {p.name: p.id for p in system.planets}

        # Serialize and deserialize
        data = galaxy.to_dict()
        restored = Galaxy.from_dict(data)

        # Verify IDs preserved
        restored_system = restored.get_system_by_name("Test")
        for planet in restored_system.planets:
            assert planet.id == original_ids[planet.name], \
                f"Planet {planet.name} ID changed from {original_ids[planet.name]} to {planet.id}"

    def test_from_dict_enables_get_system_of_planet_for_all(self):
        """After from_dict(), get_system_of_planet() should work for all planets."""
        galaxy = Galaxy(radius=1000)
        system = StarSystem(name="Test", global_location=HexCoord(50, 50))
        galaxy.add_system(system)

        # Add multiple planets
        for i in range(5):
            planet = make_test_planet(name=f"Planet{i}", location=HexCoord(i * 2, 0))
            system.planets.append(planet)
            galaxy.register_planet(system, planet)

        # Serialize and deserialize
        data = galaxy.to_dict()
        restored = Galaxy.from_dict(data)

        # All planets should be findable
        restored_system = restored.get_system_by_name("Test")
        for planet in restored_system.planets:
            found_system = restored.get_system_of_planet(planet)
            assert found_system is restored_system, \
                f"get_system_of_planet() failed for {planet.name}"

    def test_from_dict_enables_get_planets_at_global_hex(self):
        """After from_dict(), get_planets_at_global_hex() should return correct planets."""
        galaxy = Galaxy(radius=1000)
        system = StarSystem(name="Test", global_location=HexCoord(100, 100))
        galaxy.add_system(system)

        planet = make_test_planet(name="TestPlanet", location=HexCoord(5, 5))
        system.planets.append(planet)
        galaxy.register_planet(system, planet)

        # Serialize and deserialize
        data = galaxy.to_dict()
        restored = Galaxy.from_dict(data)

        # Query at global hex
        global_hex = HexCoord(105, 105)  # system(100,100) + planet(5,5)
        planets = restored.get_planets_at_global_hex(global_hex)
        assert len(planets) == 1
        assert planets[0].name == "TestPlanet"


class TestGetSystemOfObject:
    """Tests for get_system_of_object() (PROJ-184 Phase 1)."""

    def test_get_system_of_object_autoroutes_planet(self):
        """get_system_of_object() should auto-route Planet to get_system_of_planet()."""
        galaxy = Galaxy(radius=1000)
        system = StarSystem(name="Test", global_location=HexCoord(100, 100))
        galaxy.add_system(system)

        planet = make_test_planet(name="TestPlanet", location=HexCoord(5, 5))
        system.planets.append(planet)
        galaxy.register_planet(system, planet)

        # Call get_system_of_object with a Planet - should auto-route
        result = galaxy.get_system_of_object(planet)

        assert result is system

    def test_get_system_of_object_returns_none_for_no_location(self):
        """get_system_of_object() should return None for object without location."""
        galaxy = Galaxy(radius=1000)

        class NoLocationObject:
            pass

        obj = NoLocationObject()
        result = galaxy.get_system_of_object(obj)

        assert result is None

    def test_get_system_of_object_returns_system_for_fleet_at_system(self):
        """get_system_of_object() should return system for Fleet-like object at system coord."""
        galaxy = Galaxy(radius=1000)
        system = StarSystem(name="Test", global_location=HexCoord(50, 50))
        galaxy.add_system(system)

        class MockFleet:
            def __init__(self, loc):
                self.location = loc

        fleet = MockFleet(HexCoord(50, 50))  # At system's global_location
        result = galaxy.get_system_of_object(fleet)

        assert result is system

    def test_get_system_of_object_returns_none_for_fleet_in_deep_space(self):
        """get_system_of_object() should return None for Fleet-like object in deep space."""
        galaxy = Galaxy(radius=1000)
        system = StarSystem(name="Test", global_location=HexCoord(50, 50))
        galaxy.add_system(system)

        class MockFleet:
            def __init__(self, loc):
                self.location = loc

        fleet = MockFleet(HexCoord(999, 999))  # Deep space, not at any system
        result = galaxy.get_system_of_object(fleet)

        assert result is None


class TestGetSystemAtLocationO1:
    """Tests for O(1) get_system_at_location() (PROJ-179 Phase 2)."""

    def test_finds_system_via_planet_global_hex(self):
        """get_system_at_location() should find system via planet hex."""
        galaxy = Galaxy(radius=1000)
        system = StarSystem(name="Test", global_location=HexCoord(100, 100))
        galaxy.add_system(system)

        planet = make_test_planet(name="TestPlanet", location=HexCoord(5, 5))
        system.planets.append(planet)
        galaxy.register_planet(system, planet)

        # Query at planet's global hex
        global_hex = HexCoord(105, 105)  # system(100,100) + planet(5,5)
        result = galaxy.get_system_at_location(global_hex)

        assert result is system

    def test_finds_system_via_star_zone_global_hex(self):
        """get_system_at_location() should find system via star zone hex."""
        galaxy = Galaxy(radius=1000)
        star = make_test_star(name="BigStar", radius_hexes=3)  # radius 3
        system = StarSystem(name="Test", global_location=HexCoord(50, 50), stars=[star])
        galaxy.add_system(system)

        # Query at star zone hex (2 hexes from center)
        zone_hex = HexCoord(52, 50)
        result = galaxy.get_system_at_location(zone_hex)

        assert result is system

    def test_finds_system_via_warp_point_global_hex(self):
        """get_system_at_location() should find system via warp point hex."""
        galaxy = Galaxy(radius=1000)
        system_a = StarSystem(name="Alpha", global_location=HexCoord(0, 0))
        system_b = StarSystem(name="Beta", global_location=HexCoord(100, 0))
        galaxy.add_system(system_a)
        galaxy.add_system(system_b)

        # Create warp link
        galaxy.create_vars_link(system_a, system_b)

        # Get the warp point location
        wp = system_a.warp_points[0]
        wp_global_hex = system_a.global_location + wp.location

        result = galaxy.get_system_at_location(wp_global_hex)

        assert result is system_a

    def test_returns_none_for_deep_space_hex(self):
        """get_system_at_location() should return None for deep space."""
        galaxy = Galaxy(radius=1000)
        system = StarSystem(name="Test", global_location=HexCoord(0, 0))
        galaxy.add_system(system)

        # Query at distant hex
        deep_space = HexCoord(500, 500)
        result = galaxy.get_system_at_location(deep_space)

        assert result is None

    def test_finds_system_at_system_global_location(self):
        """get_system_at_location() should find system at its global_location."""
        galaxy = Galaxy(radius=1000)
        system = StarSystem(name="Test", global_location=HexCoord(25, 75))
        galaxy.add_system(system)

        result = galaxy.get_system_at_location(HexCoord(25, 75))

        assert result is system

    def test_finds_system_via_dyson_sphere_zone(self):
        """get_system_at_location() should find system via Dyson Sphere zone."""
        galaxy = Galaxy(radius=1000)
        system = StarSystem(name="Test", global_location=HexCoord(200, 200))
        galaxy.add_system(system)

        dyson = make_test_planet(
            name="Dyson Sphere",
            planet_type=PlanetType.DYSON_SPHERE,
            location=HexCoord(10, 0),
            radius_hexes=6
        )
        system.planets.append(dyson)
        galaxy.register_planet(system, dyson)

        # Query at zone hex (5 hexes from dyson center, within radius)
        # Dyson center is at 200+10=210, 200
        zone_hex = HexCoord(215, 200)
        result = galaxy.get_system_at_location(zone_hex)

        assert result is system

    def test_warp_point_index_updated_on_remove_warp_link(self):
        """remove_warp_link() should remove warp points from index."""
        galaxy = Galaxy(radius=1000)
        system_a = StarSystem(name="Alpha", global_location=HexCoord(0, 0))
        system_b = StarSystem(name="Beta", global_location=HexCoord(100, 0))
        galaxy.add_system(system_a)
        galaxy.add_system(system_b)

        # Create warp link
        galaxy.create_vars_link(system_a, system_b)
        wp = system_a.warp_points[0]
        wp_global_hex = system_a.global_location + wp.location

        # Verify it's findable
        assert galaxy.get_system_at_location(wp_global_hex) is system_a

        # Remove warp link
        galaxy.remove_warp_link("Alpha", "Beta")

        # Should no longer find system via old warp point location
        assert galaxy.get_system_at_location(wp_global_hex) is None

    def test_from_dict_rebuilds_warp_point_index(self):
        """Galaxy.from_dict() should rebuild warp point index."""
        galaxy = Galaxy(radius=1000)
        system_a = StarSystem(name="Alpha", global_location=HexCoord(0, 0))
        system_b = StarSystem(name="Beta", global_location=HexCoord(100, 0))
        galaxy.add_system(system_a)
        galaxy.add_system(system_b)
        galaxy.create_vars_link(system_a, system_b)

        wp = system_a.warp_points[0]
        wp_global_hex = system_a.global_location + wp.location

        # Serialize and deserialize
        data = galaxy.to_dict()
        restored = Galaxy.from_dict(data)

        # Should find system via warp point
        result = restored.get_system_at_location(wp_global_hex)
        assert result is not None
        assert result.name == "Alpha"
