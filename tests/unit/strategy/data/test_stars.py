"""
Unit tests for the stars module.

Tests cover:
- Spectrum dataclass: initialization, total output, serialization
- Star dataclass: initialization, serialization, location default
- StarGenerator: mass generation, type determination, color mapping,
                 radius mapping, spectrum generation, system generation
"""
import pytest
import random
from game.strategy.data.stars import (
    Spectrum,
    Star,
    StarType,
    StarGenerator,
    SOLAR_TEMP_K,
)
from game.core.hex_math import HexCoord, hex_distance


class TestSpectrum:
    """Tests for the Spectrum dataclass."""

    def test_spectrum_init_all_bands(self):
        """Spectrum stores all 9 electromagnetic bands."""
        spectrum = Spectrum(
            gamma_ray=0.1,
            xray=0.2,
            ultraviolet=0.3,
            blue=0.4,
            green=0.5,
            red=0.6,
            infrared=0.7,
            microwave=0.8,
            radio=0.9
        )
        assert spectrum.gamma_ray == 0.1
        assert spectrum.xray == 0.2
        assert spectrum.ultraviolet == 0.3
        assert spectrum.blue == 0.4
        assert spectrum.green == 0.5
        assert spectrum.red == 0.6
        assert spectrum.infrared == 0.7
        assert spectrum.microwave == 0.8
        assert spectrum.radio == 0.9

    def test_spectrum_get_total_output(self):
        """get_total_output returns sum of all bands."""
        spectrum = Spectrum(
            gamma_ray=1.0,
            xray=2.0,
            ultraviolet=3.0,
            blue=4.0,
            green=5.0,
            red=6.0,
            infrared=7.0,
            microwave=8.0,
            radio=9.0
        )
        expected_total = 1.0 + 2.0 + 3.0 + 4.0 + 5.0 + 6.0 + 7.0 + 8.0 + 9.0
        assert spectrum.get_total_output() == expected_total

    def test_spectrum_to_dict(self):
        """to_dict returns dict with all 9 band keys."""
        spectrum = Spectrum(
            gamma_ray=0.1,
            xray=0.2,
            ultraviolet=0.3,
            blue=0.4,
            green=0.5,
            red=0.6,
            infrared=0.7,
            microwave=0.8,
            radio=0.9
        )
        data = spectrum.to_dict()

        expected_keys = {
            'gamma_ray', 'xray', 'ultraviolet', 'blue', 'green',
            'red', 'infrared', 'microwave', 'radio'
        }
        assert set(data.keys()) == expected_keys
        assert data['gamma_ray'] == 0.1
        assert data['red'] == 0.6

    def test_spectrum_from_dict(self):
        """from_dict reconstructs Spectrum from dict."""
        data = {
            'gamma_ray': 1.0,
            'xray': 2.0,
            'ultraviolet': 3.0,
            'blue': 4.0,
            'green': 5.0,
            'red': 6.0,
            'infrared': 7.0,
            'microwave': 8.0,
            'radio': 9.0
        }
        spectrum = Spectrum.from_dict(data)

        assert spectrum.gamma_ray == 1.0
        assert spectrum.xray == 2.0
        assert spectrum.ultraviolet == 3.0
        assert spectrum.blue == 4.0
        assert spectrum.green == 5.0
        assert spectrum.red == 6.0
        assert spectrum.infrared == 7.0
        assert spectrum.microwave == 8.0
        assert spectrum.radio == 9.0

    def test_spectrum_serialization_roundtrip(self):
        """from_dict(to_dict()) preserves all values."""
        original = Spectrum(
            gamma_ray=0.123,
            xray=0.456,
            ultraviolet=0.789,
            blue=1.012,
            green=1.345,
            red=1.678,
            infrared=1.901,
            microwave=2.234,
            radio=2.567
        )
        roundtrip = Spectrum.from_dict(original.to_dict())

        assert roundtrip.gamma_ray == original.gamma_ray
        assert roundtrip.xray == original.xray
        assert roundtrip.ultraviolet == original.ultraviolet
        assert roundtrip.blue == original.blue
        assert roundtrip.green == original.green
        assert roundtrip.red == original.red
        assert roundtrip.infrared == original.infrared
        assert roundtrip.microwave == original.microwave
        assert roundtrip.radio == original.radio


class TestStar:
    """Tests for the Star dataclass."""

    @pytest.fixture
    def sample_spectrum(self):
        """Provide a sample spectrum for star tests."""
        return Spectrum(
            gamma_ray=0.1, xray=0.2, ultraviolet=0.3, blue=0.4, green=0.5,
            red=0.6, infrared=0.7, microwave=0.8, radio=0.9
        )

    def test_star_init(self, sample_spectrum):
        """Star stores all attributes correctly."""
        star = Star(
            name="Sol A",
            mass=1.0,
            radius_hexes=2,
            temperature=5778,
            luminosity=1.0,
            spectrum=sample_spectrum,
            star_type=StarType.MAIN_SEQUENCE,
            color=(255, 200, 150),
            age=4.6e9,
            location=HexCoord(5, -3)
        )

        assert star.name == "Sol A"
        assert star.mass == 1.0
        assert star.radius_hexes == 2
        assert star.temperature == 5778
        assert star.luminosity == 1.0
        assert star.spectrum == sample_spectrum
        assert star.star_type == StarType.MAIN_SEQUENCE
        assert star.color == (255, 200, 150)
        assert star.age == 4.6e9
        assert star.location == HexCoord(5, -3)

    def test_star_to_dict(self, sample_spectrum):
        """to_dict includes all fields with correct types."""
        star = Star(
            name="Test Star",
            mass=2.5,
            radius_hexes=3,
            temperature=8000,
            luminosity=5.0,
            spectrum=sample_spectrum,
            star_type=StarType.BLUE_GIANT,
            color=(100, 150, 255),
            age=1.0e9,
            location=HexCoord(10, -5)
        )
        data = star.to_dict()

        assert data['name'] == "Test Star"
        assert data['mass'] == 2.5
        assert data['radius_hexes'] == 3
        assert data['temperature'] == 8000
        assert data['luminosity'] == 5.0
        assert data['star_type'] == 'BLUE_GIANT'  # Enum converted to string
        assert data['color'] == [100, 150, 255]   # Tuple converted to list
        assert data['age'] == 1.0e9
        assert 'spectrum' in data
        assert isinstance(data['spectrum'], dict)
        assert 'location' in data
        assert isinstance(data['location'], dict)

    def test_star_from_dict(self, sample_spectrum):
        """from_dict reconstructs Star with correct types."""
        data = {
            'name': "Restored Star",
            'mass': 0.5,
            'radius_hexes': 1,
            'temperature': 3500,
            'luminosity': 0.1,
            'spectrum': sample_spectrum.to_dict(),
            'star_type': 'RED_DWARF',
            'color': [255, 100, 100],
            'age': 8.0e9,
            'location': {'q': 3, 'r': -2}
        }
        star = Star.from_dict(data)

        assert star.name == "Restored Star"
        assert star.mass == 0.5
        assert star.radius_hexes == 1
        assert star.temperature == 3500
        assert star.luminosity == 0.1
        assert isinstance(star.spectrum, Spectrum)
        assert star.star_type == StarType.RED_DWARF  # String to enum
        assert star.color == (255, 100, 100)  # List to tuple
        assert star.age == 8.0e9
        assert isinstance(star.location, HexCoord)
        assert star.location == HexCoord(3, -2)

    def test_star_serialization_roundtrip(self, sample_spectrum):
        """from_dict(to_dict()) preserves all fields."""
        original = Star(
            name="Roundtrip Star",
            mass=1.5,
            radius_hexes=2,
            temperature=6500,
            luminosity=2.0,
            spectrum=sample_spectrum,
            star_type=StarType.MAIN_SEQUENCE,
            color=(220, 220, 180),
            age=3.5e9,
            location=HexCoord(7, -4)
        )
        roundtrip = Star.from_dict(original.to_dict())

        assert roundtrip.name == original.name
        assert roundtrip.mass == original.mass
        assert roundtrip.radius_hexes == original.radius_hexes
        assert roundtrip.temperature == original.temperature
        assert roundtrip.luminosity == original.luminosity
        assert roundtrip.star_type == original.star_type
        assert roundtrip.color == original.color
        assert roundtrip.age == original.age
        assert roundtrip.location == original.location
        # Check spectrum roundtrip
        assert roundtrip.spectrum.get_total_output() == original.spectrum.get_total_output()

    def test_star_location_default_origin(self, sample_spectrum):
        """Default location is HexCoord(0, 0)."""
        star = Star(
            name="Default Location Star",
            mass=1.0,
            radius_hexes=1,
            temperature=5000,
            luminosity=1.0,
            spectrum=sample_spectrum,
            star_type=StarType.MAIN_SEQUENCE,
            color=(255, 255, 255),
            age=5.0e9
            # location not specified
        )
        assert star.location == HexCoord(0, 0)

    def test_star_image_id_default_empty(self, sample_spectrum):
        """Default image_id is empty string."""
        star = Star(
            name="No Image Star",
            mass=1.0, radius_hexes=1, temperature=5000, luminosity=1.0,
            spectrum=sample_spectrum, star_type=StarType.MAIN_SEQUENCE,
            color=(255, 255, 255), age=5.0e9,
        )
        assert star.image_id == ""

    def test_star_image_id_assigned(self, sample_spectrum):
        """image_id can be set to a filename."""
        star = Star(
            name="Imaged Star",
            mass=1.0, radius_hexes=1, temperature=5000, luminosity=1.0,
            spectrum=sample_spectrum, star_type=StarType.MAIN_SEQUENCE,
            color=(255, 255, 255), age=5.0e9,
            image_id="StarYellowVariant_3.png",
        )
        assert star.image_id == "StarYellowVariant_3.png"

    def test_star_to_dict_includes_image_id(self, sample_spectrum):
        """to_dict includes image_id."""
        star = Star(
            name="Dict Star",
            mass=1.0, radius_hexes=1, temperature=5000, luminosity=1.0,
            spectrum=sample_spectrum, star_type=StarType.MAIN_SEQUENCE,
            color=(255, 255, 255), age=5.0e9,
            image_id="StarBlueAsset.png",
        )
        data = star.to_dict()
        assert data['image_id'] == "StarBlueAsset.png"

    def test_star_from_dict_reads_image_id(self, sample_spectrum):
        """from_dict reads image_id field."""
        data = {
            'name': "From Dict Star", 'mass': 1.0, 'radius_hexes': 1,
            'temperature': 5000, 'luminosity': 1.0,
            'spectrum': sample_spectrum.to_dict(),
            'star_type': 'MAIN_SEQUENCE', 'color': [255, 255, 255],
            'age': 5.0e9, 'location': {'q': 0, 'r': 0},
            'image_id': 'StarRedVariant_2.png',
        }
        star = Star.from_dict(data)
        assert star.image_id == "StarRedVariant_2.png"

    def test_star_from_dict_missing_image_id_defaults_empty(self, sample_spectrum):
        """from_dict without image_id defaults to empty string."""
        data = {
            'name': "Legacy Star", 'mass': 1.0, 'radius_hexes': 1,
            'temperature': 5000, 'luminosity': 1.0,
            'spectrum': sample_spectrum.to_dict(),
            'star_type': 'MAIN_SEQUENCE', 'color': [255, 255, 255],
            'age': 5.0e9, 'location': {'q': 0, 'r': 0},
        }
        star = Star.from_dict(data)
        assert star.image_id == ""

    def test_star_image_id_roundtrip(self, sample_spectrum):
        """image_id survives to_dict/from_dict roundtrip."""
        original = Star(
            name="Roundtrip", mass=1.0, radius_hexes=1, temperature=5000,
            luminosity=1.0, spectrum=sample_spectrum,
            star_type=StarType.MAIN_SEQUENCE, color=(255, 255, 255),
            age=5.0e9, image_id="StarOrangeVariant_1.png",
        )
        roundtrip = Star.from_dict(original.to_dict())
        assert roundtrip.image_id == "StarOrangeVariant_1.png"


class TestStarOccupiedHexes:
    """Tests for Star.occupied_hexes property (PROJ-139 IZoneOccupant)."""

    @pytest.fixture
    def sample_spectrum(self):
        """Provide a sample spectrum for star tests."""
        return Spectrum(
            gamma_ray=0.1, xray=0.2, ultraviolet=0.3, blue=0.4, green=0.5,
            red=0.6, infrared=0.7, microwave=0.8, radio=0.9
        )

    def test_star_occupied_hexes_small(self, sample_spectrum):
        """radius_hexes=1 -> center only -> 1 hex."""
        star = Star(
            name="Small Star",
            mass=1.0,
            radius_hexes=1,
            temperature=5000,
            luminosity=1.0,
            spectrum=sample_spectrum,
            star_type=StarType.MAIN_SEQUENCE,
            color=(255, 200, 150),
            age=5.0e9,
            location=HexCoord(0, 0)
        )
        hexes = star.occupied_hexes
        # radius_hexes=1 -> fill(loc, 0) -> 1 hex (center only)
        assert len(hexes) == 1
        assert star.location in hexes

    def test_star_occupied_hexes_large(self, sample_spectrum):
        """radius_hexes=6 -> center + 5 rings -> 91 hexes."""
        star = Star(
            name="Large Star",
            mass=10.0,
            radius_hexes=6,
            temperature=8000,
            luminosity=100.0,
            spectrum=sample_spectrum,
            star_type=StarType.BLUE_GIANT,
            color=(100, 150, 255),
            age=1.0e9,
            location=HexCoord(0, 0)
        )
        hexes = star.occupied_hexes
        # radius_hexes=6 -> fill(loc, 5) -> 1 + 6 + 12 + 18 + 24 + 30 = 91 hexes
        assert len(hexes) == 91
        assert star.location in hexes
        # All hexes should be within distance 5 of location
        for h in hexes:
            assert hex_distance(star.location, h) <= 5

    def test_star_occupied_hexes_sub_hex(self, sample_spectrum):
        """radius_hexes=1 (compact remnant) -> center only -> 1 hex."""
        star = Star(
            name="Tiny Star",
            mass=0.5,
            radius_hexes=1,
            temperature=3000,
            luminosity=0.1,
            spectrum=sample_spectrum,
            star_type=StarType.WHITE_DWARF,
            color=(220, 220, 255),
            age=8.0e9,
            location=HexCoord(0, 0)
        )
        hexes = star.occupied_hexes
        # radius_hexes=1 -> fill(loc, 0) -> 1 hex (center only)
        assert len(hexes) == 1
        assert star.location in hexes

    def test_star_occupied_hexes_with_offset_location(self, sample_spectrum):
        """Star at non-origin location returns correctly offset hexes."""
        star = Star(
            name="Offset Star",
            mass=1.0,
            radius_hexes=2,
            temperature=5000,
            luminosity=1.0,
            spectrum=sample_spectrum,
            star_type=StarType.MAIN_SEQUENCE,
            color=(255, 200, 150),
            age=5.0e9,
            location=HexCoord(10, -5)
        )
        hexes = star.occupied_hexes
        # radius_hexes=2 -> fill(loc, 1) -> 7 hexes (center + ring 1)
        assert len(hexes) == 7
        assert star.location in hexes
        # All hexes should be within distance 1 of location
        for h in hexes:
            assert hex_distance(star.location, h) <= 1
        # Verify center is correct (not at origin)
        assert HexCoord(0, 0) not in hexes

    def test_star_occupied_hexes_returns_frozenset(self, sample_spectrum):
        """occupied_hexes returns a frozenset (immutable)."""
        star = Star(
            name="Test Star",
            mass=1.0,
            radius_hexes=1,
            temperature=5000,
            luminosity=1.0,
            spectrum=sample_spectrum,
            star_type=StarType.MAIN_SEQUENCE,
            color=(255, 200, 150),
            age=5.0e9
        )
        assert isinstance(star.occupied_hexes, frozenset)


class TestStarGenerator:
    """Tests for the StarGenerator class."""

    @pytest.fixture
    def generator(self):
        """Provide a StarGenerator instance."""
        return StarGenerator()

    def test_generate_mass_in_range(self, generator):
        """Generated mass is between 0.1 and 100.0 solar masses."""
        random.seed(42)
        for _ in range(100):
            mass = generator._generate_mass(is_primary=True)
            assert 0.1 <= mass <= 100.0, f"Mass {mass} out of range"

    def test_generate_mass_companion_less_than_primary(self, generator):
        """Companion mass is always less than primary mass."""
        random.seed(123)
        primary_mass = 5.0
        for _ in range(50):
            companion_mass = generator._generate_mass(
                is_primary=False,
                primary_mass=primary_mass
            )
            assert companion_mass < primary_mass, (
                f"Companion mass {companion_mass} >= primary {primary_mass}"
            )

    def test_determine_type_returns_valid_type(self, generator):
        """_determine_type_and_radius returns a valid StarType enum."""
        random.seed(456)
        for mass in [0.3, 0.7, 1.0, 2.0, 10.0, 50.0]:
            star_type, _, _, _, _, _ = generator._determine_type_and_radius(mass)
            assert isinstance(star_type, StarType)
            assert star_type in list(StarType)

    def test_determine_type_returns_valid_star_type(self, generator):
        """Type determination returns a valid StarType for any mass and consistent mass."""
        for mass in [0.05, 0.3, 1.0, 5.0, 30.0]:
            star_type, adj_mass, radius, temp, lum, color = generator._determine_type_and_radius(mass)
            assert isinstance(star_type, StarType)
            assert adj_mass > 0
            assert radius >= 0
            assert temp >= 0
            assert lum >= 0

    def test_kelvin_to_rgb_hot_star(self, generator):
        """High temperature produces blue-white RGB values."""
        # Very hot star (25000 K) should have high blue component
        r, g, b = generator._kelvin_to_rgb(25000)

        # Hot stars should have blue >= red
        assert b >= r or (b > 200 and r > 200), (
            f"Hot star should be blue-white, got RGB({r}, {g}, {b})"
        )
        # All components should be valid RGB values
        assert 0 <= r <= 255
        assert 0 <= g <= 255
        assert 0 <= b <= 255

    def test_kelvin_to_rgb_cool_star(self, generator):
        """Low temperature produces red-dominant RGB values."""
        # Cool star (3000 K) should be reddish
        r, g, b = generator._kelvin_to_rgb(3000)

        # Cool stars should have red as the dominant component
        assert r >= g, f"Cool star should have R >= G, got RGB({r}, {g}, {b})"
        assert r >= b, f"Cool star should have R >= B, got RGB({r}, {g}, {b})"
        # Red should be high
        assert r > 200, f"Cool star red should be high, got {r}"

    def test_map_radius_small_star(self, generator):
        """Small radius maps to 1-2 hex radius."""
        # Small star radius
        hex_radius = generator._map_solar_radius_to_hex_radius(0.5, StarType.MAIN_SEQUENCE)
        assert 1 <= hex_radius <= 2, f"Small star should be 1-2 hex radius, got {hex_radius}"

        hex_radius_2 = generator._map_solar_radius_to_hex_radius(1.5, StarType.MAIN_SEQUENCE)
        assert 1 <= hex_radius_2 <= 2, f"Medium-small star should be 1-2 hex radius, got {hex_radius_2}"

    def test_map_radius_compact_remnant(self, generator):
        """Compact remnants (neutron star, black hole, white dwarf) map to 1 hex radius."""
        # Test neutron star
        hex_radius = generator._map_solar_radius_to_hex_radius(0.00002, StarType.NEUTRON_STAR)
        assert hex_radius == 1, f"Neutron star should be 1 hex radius, got {hex_radius}"

        # Test black hole
        hex_radius = generator._map_solar_radius_to_hex_radius(0.0001, StarType.BLACK_HOLE)
        assert hex_radius == 1, f"Black hole should be 1 hex radius, got {hex_radius}"

        # Test white dwarf
        hex_radius = generator._map_solar_radius_to_hex_radius(0.01, StarType.WHITE_DWARF)
        assert hex_radius == 1, f"White dwarf should be 1 hex radius, got {hex_radius}"

    def test_generate_spectrum_has_9_bands(self, generator):
        """Generated spectrum has all 9 bands populated."""
        spectrum = generator._generate_spectrum(temp=5778, luminosity=1.0)

        assert isinstance(spectrum, Spectrum)
        # All bands should be non-negative
        assert spectrum.gamma_ray >= 0
        assert spectrum.xray >= 0
        assert spectrum.ultraviolet >= 0
        assert spectrum.blue >= 0
        assert spectrum.green >= 0
        assert spectrum.red >= 0
        assert spectrum.infrared >= 0
        assert spectrum.microwave >= 0
        assert spectrum.radio >= 0

        # Total output should be positive for a normal star
        assert spectrum.get_total_output() > 0

    def test_generate_system_stars_single(self, generator):
        """Most common case returns exactly 1 star with seeded random."""
        # With the probability distribution:
        # - roll < 0.001: 4 stars
        # - roll < 0.011: 3 stars
        # - roll < 0.111: 2 stars
        # - else: 1 star (88.9% probability)
        # Seed to ensure we hit the single-star case
        random.seed(999)  # This seed should give roll > 0.111

        stars = generator.generate_system_stars("Test System")

        # Verify at least one star is returned
        assert len(stars) >= 1
        # Verify primary star naming
        assert stars[0].name == "Test System A"
        # Verify primary at origin
        assert stars[0].location == HexCoord(0, 0)
        # Verify it's a valid Star object
        assert isinstance(stars[0], Star)
        assert isinstance(stars[0].star_type, StarType)

    def test_generate_system_stars_from_blueprint(self, generator):
        """Blueprint controls star count and mass range."""
        blueprint = {
            'star_count': 2,
            'star_mass': {
                'min': 0.5,
                'max': 2.0
            }
        }
        random.seed(42)

        stars = generator.generate_system_stars("Blueprint System", blueprint=blueprint)

        # Should have exactly 2 stars
        assert len(stars) == 2, f"Expected 2 stars, got {len(stars)}"

        # Primary star
        assert stars[0].name == "Blueprint System A"
        assert stars[0].location == HexCoord(0, 0)
        assert 0.5 <= stars[0].mass <= 2.0, (
            f"Primary mass {stars[0].mass} outside blueprint range [0.5, 2.0]"
        )

        # Companion star
        assert stars[1].name == "Blueprint System B"
        # Companion should not be at origin
        assert stars[1].location != HexCoord(0, 0)
        # Companion mass should be less than primary
        assert stars[1].mass < stars[0].mass, (
            f"Companion mass {stars[1].mass} >= primary {stars[0].mass}"
        )
