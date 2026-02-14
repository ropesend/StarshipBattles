"""
Unit tests for Galaxy class.

Tests core galaxy functionality including system lookups, name mapping,
and zone registry (PROJ-139).
"""

import pytest
from game.strategy.data.galaxy import Galaxy, StarSystem
from game.strategy.data.stars import Star, StarType, Spectrum
from game.strategy.data.planet import Planet, PlanetType
from game.core.hex_math import HexCoord


def make_test_star(name="TestStar", diameter_hexes=1.0, location=None):
    """Create a minimal Star for testing zone functionality."""
    if location is None:
        location = HexCoord(0, 0)
    return Star(
        name=name,
        mass=1.0,
        diameter_hexes=diameter_hexes,
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
                     location=None, diameter_hexes=0.0):
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
        diameter_hexes=diameter_hexes
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


class TestGalaxyZoneRegistry:
    """Tests for PROJ-139 Zone Registry functionality."""

    def test_register_zone_adds_to_all_hexes(self):
        """register_zone() should add object to all its occupied hexes."""
        galaxy = Galaxy(radius=1000)
        # Create a star with diameter 3 (radius=2 -> 19 hexes)
        star = make_test_star(diameter_hexes=3.0)
        system = StarSystem(name="Test", global_location=HexCoord(10, 20), stars=[star])

        galaxy.register_zone(system, star)

        # Should be registered at all occupied hexes
        for local_hex in star.occupied_hexes:
            global_hex = system.global_location + local_hex
            assert star in galaxy.get_zones_at_global_hex(global_hex)

    def test_unregister_zone_removes_from_all_hexes(self):
        """unregister_zone() should remove object from all its occupied hexes."""
        galaxy = Galaxy(radius=1000)
        star = make_test_star(diameter_hexes=3.0)
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
        star = make_test_star(diameter_hexes=1.0)
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
        star = make_test_star(diameter_hexes=1.0)
        system = StarSystem(name="Test", global_location=HexCoord(0, 0), stars=[star])

        galaxy.register_zone(system, star)
        galaxy.register_zone(system, star)

        # Count occurrences at center hex
        result = galaxy.get_zones_at_global_hex(HexCoord(0, 0))
        assert result.count(star) == 1

    def test_add_system_registers_star_zones(self):
        """add_system() should automatically register star zones."""
        galaxy = Galaxy(radius=1000)
        star = make_test_star(diameter_hexes=3.0)
        system = StarSystem(name="Test", global_location=HexCoord(50, 50), stars=[star])

        galaxy.add_system(system)

        # Star zones should be registered
        for local_hex in star.occupied_hexes:
            global_hex = system.global_location + local_hex
            assert star in galaxy.get_zones_at_global_hex(global_hex)

    def test_from_dict_rebuilds_star_zones(self):
        """from_dict() should rebuild star zone registry."""
        galaxy = Galaxy(radius=1000)
        star = make_test_star(name="TestStar", diameter_hexes=3.0)
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

        # Create Dyson Sphere planet with diameter_hexes
        dyson = make_test_planet(
            name="Dyson Sphere",
            planet_type=PlanetType.DYSON_SPHERE,
            location=HexCoord(0, 0),
            diameter_hexes=11.0  # 11-hex diameter -> radius 6 -> 127 hexes
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
            diameter_hexes=11.0
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
        star = make_test_star(name="BigStar", diameter_hexes=5.0)
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
            diameter_hexes=11.0  # radius 6
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
        star = make_test_star(diameter_hexes=3.0)
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
        star = make_test_star(name="Sol", diameter_hexes=2.0)
        system = StarSystem(name="Test", global_location=HexCoord(50, 50), stars=[star])
        galaxy.add_system(system)

        # Create Dyson Sphere planet with diameter_hexes
        dyson = make_test_planet(
            name="Dyson Sphere",
            planet_type=PlanetType.DYSON_SPHERE,
            location=HexCoord(5, 0),
            diameter_hexes=11.0  # 11-hex diameter -> radius 6
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

    def test_planet_diameter_hexes_preserved_after_from_dict(self):
        """Planet.diameter_hexes should be preserved through serialization."""
        galaxy = Galaxy(radius=1000)
        system = StarSystem(name="Test", global_location=HexCoord(0, 0))
        galaxy.add_system(system)

        dyson = make_test_planet(
            name="Dyson Test",
            planet_type=PlanetType.DYSON_SPHERE,
            location=HexCoord(0, 0),
            diameter_hexes=11.0
        )
        system.planets.append(dyson)
        galaxy.register_planet(system, dyson)

        # Serialize and deserialize
        data = galaxy.to_dict()
        restored = Galaxy.from_dict(data)

        restored_system = restored.get_system_by_name("Test")
        restored_dyson = next(p for p in restored_system.planets if p.name == "Dyson Test")

        # diameter_hexes should be preserved
        assert restored_dyson.diameter_hexes == 11.0

    def test_star_zones_and_dyson_zones_coexist_after_from_dict(self):
        """from_dict() should rebuild both star and Dyson Sphere zones correctly."""
        galaxy = Galaxy(radius=1000)
        star = make_test_star(name="BigStar", diameter_hexes=5.0)  # radius 3 -> 37 hexes
        system = StarSystem(name="Test", global_location=HexCoord(0, 0), stars=[star])
        galaxy.add_system(system)

        # Add Dyson Sphere far from star
        dyson = make_test_planet(
            name="Dyson",
            planet_type=PlanetType.DYSON_SPHERE,
            location=HexCoord(20, 0),
            diameter_hexes=11.0
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
