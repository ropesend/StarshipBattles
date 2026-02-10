import pytest
import random
from game.strategy.data.stars import StarGenerator, StarType, Star


@pytest.fixture
def generator():
    return StarGenerator()


class TestBlueprintGeneration:
    """Tests for blueprint-based star system generation."""

    @pytest.fixture
    def loader(self):
        """Load system blueprints."""
        from game.strategy.generation.loaders.system_blueprints_loader import SystemBlueprintsLoader
        return SystemBlueprintsLoader()

    def test_generate_from_blueprint_solar_like(self, generator, loader):
        """Test generating a solar-like system from blueprint."""
        data = loader.load()
        blueprint = loader.get_blueprint("solar_like", data)

        random.seed(42)
        stars = generator.generate_from_blueprint("Test", blueprint)

        # Solar-like should have 1 star
        assert len(stars) == 1
        # Mass should be in G/K range (0.5-1.5 solar masses)
        assert 0.5 <= stars[0].mass <= 1.5

    def test_generate_from_blueprint_binary(self, generator, loader):
        """Test generating a binary system from blueprint."""
        data = loader.load()
        blueprint = loader.get_blueprint("binary_no_planets", data)

        random.seed(42)
        stars = generator.generate_from_blueprint("Test", blueprint)

        # Binary should have 2 stars
        assert len(stars) == 2

    def test_generate_from_blueprint_red_dwarf(self, generator, loader):
        """Test generating a red dwarf system from blueprint."""
        data = loader.load()
        blueprint = loader.get_blueprint("red_dwarf_pack", data)

        random.seed(42)
        stars = generator.generate_from_blueprint("Test", blueprint)

        # Should have 1 star
        assert len(stars) == 1
        # Mass should be in red dwarf range (0.08-0.5 solar masses)
        assert 0.08 <= stars[0].mass <= 0.5

    def test_generate_system_stars_with_blueprint(self, generator, loader):
        """Test that generate_system_stars can accept a blueprint."""
        data = loader.load()
        blueprint = loader.get_blueprint("solar_like", data)

        random.seed(42)
        stars = generator.generate_system_stars("TestSys", blueprint=blueprint)

        assert len(stars) == 1

    def test_generate_system_stars_without_blueprint(self, generator):
        """Test that generate_system_stars works without blueprint (backward compat)."""
        random.seed(42)
        stars = generator.generate_system_stars("TestSys")

        # Should still work and generate 1-4 stars
        assert 1 <= len(stars) <= 4


class TestStarGeneration:
    def test_star_mass_distribution(self, generator):
        """Verify that mass distribution generally follows expectations."""
        masses = []
        for _ in range(1000):
            masses.append(generator._generate_mass(is_primary=True))

        # Check median ~1.0
        masses.sort()
        median = masses[500]
        assert 0.5 < median < 2.0, f"Median mass {median} should be near 1.0"

        # Check range
        assert min(masses) >= 0.1
        assert max(masses) <= 100.0

    def test_multi_star_probabilities(self, generator):
        """Verify generation of multiple stars."""
        counts = {1: 0, 2: 0, 3: 0, 4: 0}
        n = 2000
        for i in range(n):
            stars = generator.generate_system_stars(f"Sys-{i}")
            c = len(stars)
            if c in counts:
                counts[c] += 1

            # Check hierarchy
            primary = stars[0]
            for companion in stars[1:]:
                # Primary should be more massive (or at least generated first and primary logic holds)
                # My generator logic enforces companions are generated with primary_mass cap?
                # Actually _generate_mass loops until < primary_mass.
                assert primary.mass >= companion.mass * 0.99, "Primary should be ~largest"

                # Check distances
                # Primary is at 0,0,0
                # Companion location magnitude should be > primary radius
                # hex_distance between (0,0) and companion.location
                from game.core.hex_math import hex_distance, HexCoord
                dist = hex_distance(HexCoord(0, 0), companion.location)

                assert dist > primary.diameter_hexes, "Companion inside primary?"

        # Approx 10% binary -> ~200
        # Wide tolerance because random
        assert 150 < counts[2] < 250, "Binary count deviation"

    def test_physical_properties(self, generator):
        """Check mapping of mass to radius/hexes."""
        seen_giants = False
        seen_dwarfs = False

        for i in range(100):
            stars = generator.generate_system_stars(f"Sys-{i}")
            for star in stars:
                if star.star_type in (StarType.RED_GIANT, StarType.BLUE_GIANT):
                    seen_giants = True
                    assert star.diameter_hexes > 2.0
                if star.star_type == StarType.RED_DWARF:
                    seen_dwarfs = True
                    assert star.diameter_hexes <= 3.0

                # Check Spectrum
                spec = star.spectrum
                assert spec is not None
                total = spec.get_total_output()
                assert total > 0

                # Verify 9 bands are present and non-negative
                assert spec.gamma_ray >= 0
                assert spec.xray >= 0
                assert spec.ultraviolet >= 0
                assert spec.blue >= 0
                assert spec.green >= 0
                assert spec.red >= 0
                assert spec.infrared >= 0
                assert spec.microwave >= 0
                assert spec.radio >= 0

        assert seen_giants, "Should have seen at least one giant"
        assert seen_dwarfs, "Should have seen at least one dwarf"
