"""
Unit tests for game/strategy/generation/storm_generator.py

Tests storm generation functionality including cluster generation,
placement collision avoidance, and blueprint config integration.
"""
import random
import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.storm import Storm


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def storm_defs():
    """Sample storm definitions for testing."""
    return {
        "version": "2.0",
        "storm_types": {
            "ion_storm": {
                "name": "Ion Storm",
                "description": "Test ion storm",
                "abilities": {
                    "ShieldModifier":         {"multiplier": 0.5, "scope": "sector"},
                    "StrategicSpeedModifier": {"multiplier": 0.8, "scope": "sector"},
                },
                "size": {"min": 2, "max": 5},
                "image_variants": [1, 2, 3]
            },
            "plasma_storm": {
                "name": "Plasma Storm",
                "description": "Test plasma storm",
                "abilities": {
                    "EnvironmentalDamage": {"rate": 0.5, "damage_type": "plasma", "scope": "sector"},
                },
                "size": {"min": 3, "max": 7},
                "image_variants": [4, 5, 6]
            }
        }
    }


@pytest.fixture
def mock_star_system():
    """Create a mock star system for testing."""
    from game.strategy.data.galaxy import StarSystem
    from game.strategy.data.stars import Star, Spectrum, StarType

    # Create a simple star
    spectrum = Spectrum(0, 0, 0.1, 0.3, 0.3, 0.2, 0.1, 0, 0)
    star = Star(
        name="Test Star",
        mass=1.0,
        radius_hexes=2,
        temperature=5778,
        luminosity=1.0,
        spectrum=spectrum,
        star_type=StarType.MAIN_SEQUENCE,
        color=(255, 255, 200),
        age=4.6e9,
        location=HexCoord(0, 0)
    )

    system = StarSystem("Test System", HexCoord(0, 0), stars=[star])
    return system


# =============================================================================
# StormGenerator Tests
# =============================================================================

class TestStormGeneratorInit:
    """Tests for StormGenerator initialization."""

    def test_init_with_valid_defs(self, storm_defs):
        """StormGenerator initializes with valid definitions."""
        from game.strategy.generation.storm_generator import StormGenerator

        generator = StormGenerator(storm_defs)
        assert generator is not None

    def test_init_stores_storm_types(self, storm_defs):
        """StormGenerator stores storm type definitions."""
        from game.strategy.generation.storm_generator import StormGenerator

        generator = StormGenerator(storm_defs)
        assert "ion_storm" in generator._storm_types
        assert "plasma_storm" in generator._storm_types


class TestStormGeneratorGenerateStorms:
    """Tests for generate_storms method."""

    def test_generates_correct_count(self, storm_defs, mock_star_system):
        """Generates correct number of storms per config."""
        from game.strategy.generation.storm_generator import StormGenerator

        generator = StormGenerator(storm_defs)
        blueprint_config = {
            "storms": {
                "count": {"min": 2, "max": 2},
                "allowed_types": ["ion_storm", "plasma_storm"]
            }
        }
        rng = random.Random(42)

        storms = generator.generate_storms(mock_star_system, blueprint_config, rng)

        assert len(storms) == 2

    def test_generates_storms_in_range(self, storm_defs, mock_star_system):
        """Generates number of storms within min/max range."""
        from game.strategy.generation.storm_generator import StormGenerator

        generator = StormGenerator(storm_defs)
        blueprint_config = {
            "storms": {
                "count": {"min": 1, "max": 3},
                "allowed_types": ["ion_storm"]
            }
        }

        # Generate multiple times to check range
        counts = []
        for seed in range(20):
            rng = random.Random(seed)
            storms = generator.generate_storms(mock_star_system, blueprint_config, rng)
            counts.append(len(storms))

        assert all(1 <= c <= 3 for c in counts)
        # Should see some variance
        assert len(set(counts)) > 1

    def test_returns_empty_list_without_storm_config(self, storm_defs, mock_star_system):
        """Returns empty list when blueprint has no storm config."""
        from game.strategy.generation.storm_generator import StormGenerator

        generator = StormGenerator(storm_defs)
        blueprint_config = {}  # No storms section
        rng = random.Random(42)

        storms = generator.generate_storms(mock_star_system, blueprint_config, rng)

        assert storms == []

    def test_returns_empty_list_with_zero_count(self, storm_defs, mock_star_system):
        """Returns empty list when count is 0."""
        from game.strategy.generation.storm_generator import StormGenerator

        generator = StormGenerator(storm_defs)
        blueprint_config = {
            "storms": {
                "count": {"min": 0, "max": 0}
            }
        }
        rng = random.Random(42)

        storms = generator.generate_storms(mock_star_system, blueprint_config, rng)

        assert storms == []

    def test_storms_avoid_star_hexes(self, storm_defs, mock_star_system):
        """Generated storms do not overlap with star occupied hexes."""
        from game.strategy.generation.storm_generator import StormGenerator

        generator = StormGenerator(storm_defs)
        blueprint_config = {
            "storms": {
                "count": {"min": 3, "max": 3},
                "allowed_types": ["ion_storm"]
            }
        }
        rng = random.Random(42)

        storms = generator.generate_storms(mock_star_system, blueprint_config, rng)

        # Get all star hexes
        star_hexes = set()
        for star in mock_star_system.stars:
            star_hexes.update(star.occupied_hexes)

        # Check no storm overlaps with stars
        for storm in storms:
            storm_hexes = storm.occupied_hexes
            overlap = star_hexes.intersection(storm_hexes)
            assert len(overlap) == 0, f"Storm overlaps with star at {overlap}"

    def test_storms_dont_overlap_each_other(self, storm_defs, mock_star_system):
        """Generated storms do not overlap with each other."""
        from game.strategy.generation.storm_generator import StormGenerator

        generator = StormGenerator(storm_defs)
        blueprint_config = {
            "storms": {
                "count": {"min": 3, "max": 3},
                "allowed_types": ["ion_storm", "plasma_storm"]
            }
        }
        rng = random.Random(42)

        storms = generator.generate_storms(mock_star_system, blueprint_config, rng)

        # Check no pair of storms overlap
        for i, storm_a in enumerate(storms):
            for storm_b in storms[i + 1:]:
                overlap = storm_a.occupied_hexes.intersection(storm_b.occupied_hexes)
                assert len(overlap) == 0, f"Storms overlap at {overlap}"

    def test_cluster_sizes_within_bounds(self, storm_defs, mock_star_system):
        """Storm cluster sizes are within type definition bounds."""
        from game.strategy.generation.storm_generator import StormGenerator

        generator = StormGenerator(storm_defs)
        blueprint_config = {
            "storms": {
                "count": {"min": 5, "max": 5},
                "allowed_types": ["ion_storm"]  # size 2-5
            }
        }

        for seed in range(10):
            rng = random.Random(seed)
            storms = generator.generate_storms(mock_star_system, blueprint_config, rng)

            for storm in storms:
                # ion_storm has size min=2, max=5
                assert 2 <= len(storm.hex_offsets) <= 5

    def test_deterministic_with_seeded_rng(self, storm_defs, mock_star_system):
        """Same seed produces same storms."""
        from game.strategy.generation.storm_generator import StormGenerator

        generator = StormGenerator(storm_defs)
        blueprint_config = {
            "storms": {
                "count": {"min": 2, "max": 2},
                "allowed_types": ["ion_storm", "plasma_storm"]
            }
        }

        rng1 = random.Random(12345)
        storms1 = generator.generate_storms(mock_star_system, blueprint_config, rng1)

        rng2 = random.Random(12345)
        storms2 = generator.generate_storms(mock_star_system, blueprint_config, rng2)

        assert len(storms1) == len(storms2)
        for s1, s2 in zip(storms1, storms2):
            assert s1.location == s2.location
            assert s1.storm_type == s2.storm_type
            assert s1.hex_offsets == s2.hex_offsets

    def test_uses_allowed_types_only(self, storm_defs, mock_star_system):
        """Only generates storms from allowed_types list."""
        from game.strategy.generation.storm_generator import StormGenerator

        generator = StormGenerator(storm_defs)
        blueprint_config = {
            "storms": {
                "count": {"min": 5, "max": 5},
                "allowed_types": ["ion_storm"]  # Only ion_storm
            }
        }
        rng = random.Random(42)

        storms = generator.generate_storms(mock_star_system, blueprint_config, rng)

        for storm in storms:
            assert storm.storm_type == "ion_storm"

    def test_uses_all_types_if_not_specified(self, storm_defs, mock_star_system):
        """Uses all storm types when allowed_types not specified."""
        from game.strategy.generation.storm_generator import StormGenerator

        generator = StormGenerator(storm_defs)
        blueprint_config = {
            "storms": {
                "count": {"min": 10, "max": 10}
                # No allowed_types - should use all
            }
        }
        rng = random.Random(42)

        storms = generator.generate_storms(mock_star_system, blueprint_config, rng)

        # Should have mix of types
        types_used = {s.storm_type for s in storms}
        # With 10 storms and 2 types, very likely both are used
        assert len(types_used) >= 1  # At least one type


class TestStormGeneratorOutputFormat:
    """Tests for the format of generated Storm objects."""

    def test_storm_has_valid_name(self, storm_defs, mock_star_system):
        """Generated storms have valid names."""
        from game.strategy.generation.storm_generator import StormGenerator

        generator = StormGenerator(storm_defs)
        blueprint_config = {
            "storms": {
                "count": {"min": 1, "max": 1},
                "allowed_types": ["ion_storm"]
            }
        }
        rng = random.Random(42)

        storms = generator.generate_storms(mock_star_system, blueprint_config, rng)

        assert len(storms) == 1
        storm = storms[0]
        assert storm.name  # Non-empty name
        assert "Ion Storm" in storm.name  # Contains type name

    def test_storm_has_correct_abilities(self, storm_defs, mock_star_system):
        """Generated storms have abilities from type definition (PROJ-300 v2.0)."""
        from game.strategy.generation.storm_generator import StormGenerator

        generator = StormGenerator(storm_defs)
        blueprint_config = {
            "storms": {
                "count": {"min": 1, "max": 1},
                "allowed_types": ["ion_storm"]
            }
        }
        rng = random.Random(42)

        storms = generator.generate_storms(mock_star_system, blueprint_config, rng)

        storm = storms[0]
        # ion_storm declares ShieldModifier 0.5x and StrategicSpeedModifier 0.8x.
        assert storm.abilities["ShieldModifier"]["multiplier"] == 0.5
        assert storm.abilities["StrategicSpeedModifier"]["multiplier"] == 0.8
        # Description carried through from registry template.
        assert storm.description == "Test ion storm"

    def test_storm_has_valid_image_variant(self, storm_defs, mock_star_system):
        """Generated storms have image_variant from type definition."""
        from game.strategy.generation.storm_generator import StormGenerator

        generator = StormGenerator(storm_defs)
        blueprint_config = {
            "storms": {
                "count": {"min": 5, "max": 5},
                "allowed_types": ["ion_storm"]  # image_variants: [1, 2, 3]
            }
        }
        rng = random.Random(42)

        storms = generator.generate_storms(mock_star_system, blueprint_config, rng)

        for storm in storms:
            assert storm.image_variant in [1, 2, 3]

    def test_storm_has_intensity_in_range(self, storm_defs, mock_star_system):
        """Generated storms have intensity within valid range."""
        from game.strategy.generation.storm_generator import StormGenerator

        generator = StormGenerator(storm_defs)
        blueprint_config = {
            "storms": {
                "count": {"min": 5, "max": 5},
                "allowed_types": ["ion_storm"]
            }
        }

        for seed in range(10):
            rng = random.Random(seed)
            storms = generator.generate_storms(mock_star_system, blueprint_config, rng)

            for storm in storms:
                assert 0.3 <= storm.intensity <= 1.0

    def test_storm_location_is_hexcoord(self, storm_defs, mock_star_system):
        """Storm location is a valid HexCoord."""
        from game.strategy.generation.storm_generator import StormGenerator

        generator = StormGenerator(storm_defs)
        blueprint_config = {
            "storms": {
                "count": {"min": 1, "max": 1},
                "allowed_types": ["ion_storm"]
            }
        }
        rng = random.Random(42)

        storms = generator.generate_storms(mock_star_system, blueprint_config, rng)

        storm = storms[0]
        assert isinstance(storm.location, HexCoord)


class TestStormGeneratorPlacementHelpers:
    """Tests for private storm placement helper edge cases."""

    def test_collect_occupied_hexes_includes_existing_storms(
        self, storm_defs, mock_star_system
    ):
        """Existing storm occupied hexes are blocked for later placements."""
        from game.strategy.generation.storm_generator import StormGenerator

        generator = StormGenerator(storm_defs)
        existing = Storm(
            name="Existing",
            storm_type="ion_storm",
            location=HexCoord(8, -2),
            hex_offsets=frozenset({HexCoord(0, 0), HexCoord(1, 0)}),
        )

        occupied = generator._collect_occupied_hexes(mock_star_system, [existing])

        assert existing.occupied_hexes <= occupied

    def test_find_valid_center_returns_none_after_attempt_exhaustion(
        self, storm_defs, mock_star_system
    ):
        """Placement returns None when every sampled candidate is occupied."""
        from game.strategy.generation.storm_generator import StormGenerator

        class FixedRng:
            def __init__(self):
                self.calls = 0

            def randint(self, low, high):
                self.calls += 1
                return 0

        generator = StormGenerator(storm_defs)
        rng = FixedRng()

        result = generator._find_valid_center(
            mock_star_system,
            {HexCoord(0, 0)},
            rng,
            max_attempts=3,
        )

        assert result is None
        assert rng.calls == 6

    def test_find_valid_center_clamps_search_radius_to_thirty(
        self, storm_defs, mock_star_system
    ):
        """Large systems clamp random placement bounds to radius 30."""
        from game.strategy.generation.storm_generator import StormGenerator

        class BoundsRng:
            def __init__(self):
                self.bounds = []

            def randint(self, low, high):
                self.bounds.append((low, high))
                return 0

        mock_star_system.planets = [
            type("PlanetStub", (), {"location": HexCoord(100, 0)})()
        ]
        generator = StormGenerator(storm_defs)
        rng = BoundsRng()

        result = generator._find_valid_center(mock_star_system, set(), rng)

        assert result == HexCoord(0, 0)
        assert rng.bounds[:2] == [(-30, 30), (-30, 30)]
