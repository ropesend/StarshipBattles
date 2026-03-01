"""
Unit tests for Planet.occupied_hexes and radius_hexes (PROJ-139 IZoneOccupant).

Tests cover:
- occupied_hexes property for normal planets (single hex)
- occupied_hexes property for multi-hex objects (Dyson Spheres)
- radius_hexes serialization round-trip
"""

import pytest
from game.core.hex_math import HexCoord, hex_distance
from game.strategy.data.planet import Planet, PlanetType


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def normal_planet():
    """Create a normal planet with no multi-hex zone."""
    return Planet(
        name="Terra Nova",
        location=HexCoord(5, -3),
        orbit_distance=3,
        mass=5.97e24,
        radius=6.371e6,
        surface_area=5.1e14,
        density=5515.0,
        surface_gravity=9.81,
        surface_pressure=101325.0,
        surface_temperature=288.0,
        surface_water=0.7,
        tectonic_activity=0.5,
        magnetic_field=1.0,
        atmosphere={"N2": 79000.0, "O2": 21000.0},
        planet_type=PlanetType.CONTINENTAL
    )


@pytest.fixture
def dyson_sphere():
    """Create a Dyson Sphere with multi-hex zone (radius 6 = 91 hexes)."""
    return Planet(
        name="Dyson Alpha",
        location=HexCoord(0, 0),
        orbit_distance=0,
        mass=1.0e30,
        radius=1.5e11,
        surface_area=2.83e23,
        density=100.0,
        surface_gravity=9.81,
        surface_pressure=101325.0,
        surface_temperature=288.0,
        surface_water=0.3,
        tectonic_activity=0.0,
        magnetic_field=1.0,
        atmosphere={},
        planet_type=PlanetType.DYSON_SPHERE,
        radius_hexes=6
    )


# =============================================================================
# Test: occupied_hexes Property
# =============================================================================

class TestPlanetOccupiedHexes:
    """Tests for Planet.occupied_hexes property."""

    def test_normal_planet_occupied_hexes_single(self, normal_planet):
        """Normal planet (radius_hexes=0) returns single hex."""
        hexes = normal_planet.occupied_hexes

        assert len(hexes) == 1
        assert normal_planet.location in hexes
        assert isinstance(hexes, frozenset)

    def test_dyson_sphere_occupied_hexes_zone(self, dyson_sphere):
        """Dyson Sphere with radius_hexes=6 returns 91-hex zone."""
        hexes = dyson_sphere.occupied_hexes

        # radius_hexes=6 -> fill(loc, 5) -> 1 + 6 + 12 + 18 + 24 + 30 = 91
        assert len(hexes) == 91
        assert dyson_sphere.location in hexes

        # All hexes should be within distance 5 of center
        for h in hexes:
            assert hex_distance(dyson_sphere.location, h) <= 5

    def test_occupied_hexes_with_offset_center(self):
        """Multi-hex zone with offset center returns correctly offset hexes."""
        planet = Planet(
            name="Offset Dyson",
            location=HexCoord(10, -5),
            orbit_distance=0,
            mass=1.0e30,
            radius=1.5e11,
            surface_area=2.83e23,
            density=100.0,
            surface_gravity=9.81,
            surface_pressure=101325.0,
            surface_temperature=288.0,
            surface_water=0.3,
            tectonic_activity=0.0,
            magnetic_field=1.0,
            planet_type=PlanetType.DYSON_SPHERE,
            radius_hexes=3  # center + 2 rings = 19 hexes
        )

        hexes = planet.occupied_hexes

        # radius_hexes=3 -> fill(loc, 2) -> 1 + 6 + 12 = 19 hexes
        assert len(hexes) == 19
        assert planet.location in hexes

        # Origin should NOT be in zone (offset center)
        assert HexCoord(0, 0) not in hexes

        # All hexes should be within distance 2 of center
        for h in hexes:
            assert hex_distance(planet.location, h) <= 2

    def test_occupied_hexes_returns_frozenset(self, normal_planet, dyson_sphere):
        """occupied_hexes returns frozenset (immutable)."""
        assert isinstance(normal_planet.occupied_hexes, frozenset)
        assert isinstance(dyson_sphere.occupied_hexes, frozenset)


# =============================================================================
# Test: radius_hexes Serialization
# =============================================================================

class TestPlanetRadiusHexesSerialization:
    """Tests for radius_hexes serialization round-trip."""

    def test_normal_planet_serialization_has_radius_hexes(self, normal_planet):
        """Normal planet to_dict includes radius_hexes=0."""
        data = normal_planet.to_dict()

        assert 'radius_hexes' in data
        assert data['radius_hexes'] == 0

    def test_dyson_sphere_serialization_has_radius_hexes(self, dyson_sphere):
        """Dyson Sphere to_dict includes radius_hexes=6."""
        data = dyson_sphere.to_dict()

        assert 'radius_hexes' in data
        assert data['radius_hexes'] == 6

    def test_planet_roundtrip_preserves_radius_hexes(self, dyson_sphere):
        """from_dict(to_dict()) preserves radius_hexes."""
        data = dyson_sphere.to_dict()
        restored = Planet.from_dict(data)

        assert restored.radius_hexes == dyson_sphere.radius_hexes
        assert restored.radius_hexes == 6

    def test_from_dict_defaults_radius_hexes_to_zero(self):
        """from_dict with missing radius_hexes defaults to 0."""
        # Minimal data without radius_hexes (old save format)
        data = {
            'id': 1,
            'name': 'Old Planet',
            'location': {'q': 1, 'r': 2},
            'orbit_distance': 3,
            'mass': 5.97e24,
            'radius': 6.371e6,
            'surface_area': 5.1e14,
            'density': 5515.0,
            'surface_gravity': 9.81,
            'surface_pressure': 101325.0,
            'surface_temperature': 288.0,
            'surface_water': 0.7,
            'tectonic_activity': 0.5,
            'magnetic_field': 1.0,
            'atmosphere': {},
            'planet_type': 'CONTINENTAL'
            # Note: no radius_hexes key
        }

        planet = Planet.from_dict(data)

        assert planet.radius_hexes == 0
        assert len(planet.occupied_hexes) == 1

    def test_roundtrip_with_various_radius_hexes(self):
        """Round-trip preserves various radius_hexes values."""
        test_values = [0, 1, 2, 3, 4, 6]

        for radius in test_values:
            planet = Planet(
                name="Test Planet",
                location=HexCoord(0, 0),
                orbit_distance=0,
                mass=1.0e24,
                radius=1.0e6,
                surface_area=1.0e12,
                density=5000.0,
                surface_gravity=9.81,
                surface_pressure=101325.0,
                surface_temperature=300.0,
                surface_water=0.0,
                tectonic_activity=0.0,
                magnetic_field=0.0,
                planet_type=PlanetType.BARREN,
                radius_hexes=radius
            )

            data = planet.to_dict()
            restored = Planet.from_dict(data)

            assert restored.radius_hexes == radius, f"Failed for radius {radius}"
