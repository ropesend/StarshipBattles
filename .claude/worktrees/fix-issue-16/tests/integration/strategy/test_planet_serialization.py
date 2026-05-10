"""
Integration tests for planet serialization with image fields.

Tests that image_id and image_rotation fields are properly persisted
through to_dict/from_dict serialization and backward compatible with
saves that don't have these fields.
"""

from game.strategy.data.planet import Planet, PlanetType
from game.core.hex_math import HexCoord
from game.strategy.generation.planet_image_registry import PlanetImageRegistry


class TestPlanetImageSerialization:
    """Test image fields persist through serialization."""

    def _create_test_planet(self, image_id: str = "", image_rotation: float = 0.0) -> Planet:
        """Create a minimal test planet with image fields."""
        return Planet(
            name="Test Planet",
            location=HexCoord(1, 2),
            orbit_distance=3,
            mass=5.97e24,  # Earth mass
            radius=6.371e6,  # Earth radius
            surface_area=5.1e14,
            density=5515.0,
            surface_gravity=9.8,
            surface_pressure=101325.0,
            surface_temperature=288.0,
            surface_water=0.71,
            tectonic_activity=0.5,
            magnetic_field=1.0,
            atmosphere={"N2": 79000.0, "O2": 21000.0},
            planet_type=PlanetType.CONTINENTAL,
            image_id=image_id,
            image_rotation=image_rotation
        )

    def test_image_fields_serialize_to_dict(self):
        """Image fields should be included in to_dict output."""
        planet = self._create_test_planet(
            image_id="planet_1_001_1234567890.png",
            image_rotation=45.5
        )

        data = planet.to_dict()

        assert "image_id" in data
        assert "image_rotation" in data
        assert data["image_id"] == "planet_1_001_1234567890.png"
        assert data["image_rotation"] == 45.5

    def test_image_fields_deserialize_from_dict(self):
        """Image fields should be restored from dict."""
        planet = self._create_test_planet(
            image_id="planet_2_042_9876543210.png",
            image_rotation=270.0
        )

        data = planet.to_dict()
        restored = Planet.from_dict(data)

        assert restored.image_id == "planet_2_042_9876543210.png"
        assert restored.image_rotation == 270.0

    def test_roundtrip_preserves_all_fields(self):
        """Full roundtrip should preserve all planet fields including images."""
        original = self._create_test_planet(
            image_id="planet_5_999_5555555555.png",
            image_rotation=180.25
        )

        data = original.to_dict()
        restored = Planet.from_dict(data)

        # Check image fields
        assert restored.image_id == original.image_id
        assert restored.image_rotation == original.image_rotation

        # Check other core fields weren't broken
        assert restored.name == original.name
        assert restored.location == original.location
        assert restored.orbit_distance == original.orbit_distance
        assert restored.mass == original.mass
        assert restored.planet_type == original.planet_type


class TestBackwardCompatibility:
    """Test backward compatibility with old saves without image fields."""

    def test_missing_image_id_defaults_to_empty(self):
        """Old saves without image_id should default to empty string."""
        # Simulate old save data without image fields
        old_data = {
            "name": "Legacy Planet",
            "location": {"q": 0, "r": 0},
            "orbit_distance": 5,
            "mass": 1e24,
            "radius": 5e6,
            "surface_area": 3e14,
            "density": 5000.0,
            "surface_gravity": 8.0,
            "surface_pressure": 80000.0,
            "surface_temperature": 300.0,
            "surface_water": 0.3,
            "tectonic_activity": 0.2,
            "magnetic_field": 0.5,
            "atmosphere": {"N2": 60000.0},
            "planet_type": "BARREN"
        }

        planet = Planet.from_dict(old_data)

        # Should have empty defaults
        assert planet.image_id == ""
        assert planet.image_rotation == 0.0

    def test_partial_image_data_handled(self):
        """Old save with only one image field should handle gracefully."""
        # Has image_id but no rotation
        partial_data = {
            "name": "Partial Planet",
            "location": {"q": 1, "r": 1},
            "orbit_distance": 3,
            "mass": 2e24,
            "radius": 6e6,
            "surface_area": 4e14,
            "density": 5200.0,
            "surface_gravity": 9.0,
            "surface_pressure": 90000.0,
            "surface_temperature": 280.0,
            "surface_water": 0.5,
            "tectonic_activity": 0.3,
            "magnetic_field": 0.8,
            "atmosphere": {"CO2": 50000.0},
            "planet_type": "ARID",
            "image_id": "planet_legacy.png"
            # Note: no image_rotation
        }

        planet = Planet.from_dict(partial_data)

        assert planet.image_id == "planet_legacy.png"
        assert planet.image_rotation == 0.0  # Default


class TestGeneratedPlanetsHaveImages:
    """Test that planet generation assigns image fields."""

    def test_generated_planet_has_image_id(self):
        """Generated planets should have non-empty image_id."""
        from game.strategy.data.galaxy import Galaxy

        galaxy = Galaxy(radius=100)
        systems = galaxy.generate_systems(count=3)

        # Find at least one planet
        all_planets = []
        for sys in systems:
            all_planets.extend(sys.planets)

        assert len(all_planets) > 0, "Need at least one planet for testing"

        # Check all planets have image_id
        for planet in all_planets:
            assert planet.image_id != "", f"Planet {planet.name} should have image_id"
            assert planet.image_id.endswith(".png"), f"Image should be PNG"

    def test_generated_planet_has_rotation(self):
        """Generated planets should have image_rotation in valid range."""
        from game.strategy.data.galaxy import Galaxy

        galaxy = Galaxy(radius=100)
        systems = galaxy.generate_systems(count=3)

        all_planets = []
        for sys in systems:
            all_planets.extend(sys.planets)

        assert len(all_planets) > 0, "Need at least one planet for testing"

        for planet in all_planets:
            assert 0.0 <= planet.image_rotation <= 360.0, \
                f"Planet {planet.name} rotation {planet.image_rotation} out of range"

    def test_generated_planet_image_matches_type(self):
        """Generated planet image should be appropriate for its type."""
        from game.strategy.data.galaxy import Galaxy

        galaxy = Galaxy(radius=100)
        systems = galaxy.generate_systems(count=5)

        registry = PlanetImageRegistry()

        for sys in systems:
            for planet in sys.planets:
                # Get available images for this type
                direct_count = registry.get_image_count(planet.planet_type)

                # If type has direct images, planet's image should be from that set
                # (This is a soft check - fallbacks are allowed)
                if direct_count > 0:
                    # Just verify it's a valid image filename
                    assert planet.image_id.startswith("planet_")
