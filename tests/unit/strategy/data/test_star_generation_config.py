"""
Unit tests for StarGenerationConfig.

Tests cover:
- StarGenerationConfig defaults
- StarGenerationConfig from JSON
- get_star_generation_config caching behavior
"""
import pytest
from unittest.mock import patch

from game.strategy.data.star_generation_config import (
    StarGenerationConfig,
    get_star_generation_config,
)


class TestStarGenerationConfigDefaults:
    """Tests for StarGenerationConfig initialization with defaults."""

    def test_init_no_data_uses_defaults(self):
        """Test that init with None uses default values."""
        config = StarGenerationConfig(None)

        # Type weights
        assert config.type_weights["MAIN_SEQUENCE"] == 0.525
        assert config.type_weights["RED_DWARF"] == 0.250
        assert config.type_weights["RED_GIANT"] == 0.070
        assert config.type_weights["BLUE_GIANT"] == 0.060
        assert config.type_weights["BROWN_DWARF"] == 0.030
        assert config.type_weights["WHITE_DWARF"] == 0.030
        assert config.type_weights["NEUTRON_STAR"] == 0.020
        assert config.type_weights["BLACK_HOLE"] == 0.015

        # Mass generation
        assert config.mass_sigma == 0.8
        assert config.mass_min == 0.1
        assert config.mass_max == 100.0
        assert config.mass_max_attempts == 1000

        # System probabilities
        assert config.age_min == 0.1
        assert config.age_max == 10.0
        assert config.age_unit == 1e9

    def test_type_weights_sum_to_one(self):
        """Test that default type weights sum to approximately 1.0."""
        config = StarGenerationConfig(None)
        total = sum(config.type_weights.values())
        assert abs(total - 1.0) < 0.01

    def test_type_weights_has_all_types(self):
        """Test that type weights has entries for all 8 star types."""
        config = StarGenerationConfig(None)
        expected_types = {
            "MAIN_SEQUENCE", "RED_DWARF", "RED_GIANT", "BLUE_GIANT",
            "BROWN_DWARF", "WHITE_DWARF", "NEUTRON_STAR", "BLACK_HOLE",
        }
        assert set(config.type_weights.keys()) == expected_types

    def test_default_system_count_thresholds(self):
        """Test system count probability thresholds."""
        config = StarGenerationConfig(None)
        assert len(config.system_count_thresholds) == 3
        # Thresholds: 4 stars at 0.001, 3 at 0.011, 2 at 0.111
        assert config.system_count_thresholds[0] == {"count": 4, "cumulative": 0.001}
        assert config.system_count_thresholds[1] == {"count": 3, "cumulative": 0.011}
        assert config.system_count_thresholds[2] == {"count": 2, "cumulative": 0.111}
        assert config.system_default_count == 1

    def test_default_companion_spacing(self):
        """Test companion placement parameters."""
        config = StarGenerationConfig(None)
        assert config.companion_ring_multiplier == 10
        assert config.companion_jitter_min == 2
        assert config.companion_jitter_max == 8
        assert config.companion_min_offset == 2
        assert config.companion_collision_limit == 100

    def test_default_stefan_boltzmann_types(self):
        """Test Stefan-Boltzmann type property tables."""
        config = StarGenerationConfig(None)
        sb = config.stefan_boltzmann_types

        # Should have exactly 3 types
        assert set(sb.keys()) == {"RED_GIANT", "BROWN_DWARF", "WHITE_DWARF"}

        # RED_GIANT
        rg = sb["RED_GIANT"]
        assert rg["temp_range"] == (3000, 4500)
        assert rg["color"] == (255, 60, 60)

        # BROWN_DWARF
        bd = sb["BROWN_DWARF"]
        assert bd["temp_range"] == (500, 2500)
        assert bd["color"] == (140, 60, 40)

        # WHITE_DWARF
        wd = sb["WHITE_DWARF"]
        assert wd["temp_range"] == (8000, 40000)
        assert wd["color"] == (220, 220, 255)


class TestStarGenerationConfigFromJson:
    """Tests for StarGenerationConfig initialization from JSON data."""

    def test_init_with_json_data(self):
        """Test that init with valid JSON data loads values correctly."""
        data = {
            "star_generation": {
                "type_weights": {
                    "MAIN_SEQUENCE": 0.500,
                    "RED_DWARF": 0.300,
                },
                "mass_generation": {
                    "sigma": 0.9,
                    "min_mass": 0.2,
                    "max_mass": 80.0,
                    "max_attempts": 500,
                },
                "system_probabilities": {
                    "age_min": 0.2,
                    "age_max": 12.0,
                },
            }
        }

        config = StarGenerationConfig(data)

        # JSON values loaded
        assert config.type_weights["MAIN_SEQUENCE"] == 0.500
        assert config.type_weights["RED_DWARF"] == 0.300
        assert config.mass_sigma == 0.9
        assert config.mass_min == 0.2
        assert config.mass_max == 80.0
        assert config.mass_max_attempts == 500
        assert config.age_min == 0.2
        assert config.age_max == 12.0

    def test_json_overrides_defaults(self):
        """Test that JSON values override default values."""
        data = {
            "star_generation": {
                "mass_generation": {
                    "sigma": 1.2,
                },
            }
        }

        config = StarGenerationConfig(data)

        # JSON override
        assert config.mass_sigma == 1.2

        # Non-overridden values use defaults
        assert config.mass_min == 0.1
        assert config.mass_max == 100.0

    def test_partial_json_falls_back_to_defaults(self):
        """Test that missing JSON keys fall back to default values."""
        data = {
            "star_generation": {
                "mass_generation": {
                    "sigma": 0.6,
                },
                # All other sections missing
            }
        }

        config = StarGenerationConfig(data)

        assert config.mass_sigma == 0.6
        # All other values should be defaults
        assert config.type_weights["MAIN_SEQUENCE"] == 0.525
        assert config.age_min == 0.1
        assert config.companion_ring_multiplier == 10

    def test_no_star_generation_key_uses_defaults(self):
        """Test that data without 'star_generation' key uses defaults."""
        data = {"other_key": {"some_value": 123}}

        config = StarGenerationConfig(data)

        assert config.type_weights["MAIN_SEQUENCE"] == 0.525
        assert config.mass_sigma == 0.8
        assert config.age_min == 0.1


class TestGetStarGenerationConfig:
    """Tests for the get_star_generation_config cached function."""

    def test_cached_config_returns_instance(self):
        """Test that get_star_generation_config returns an instance."""
        get_star_generation_config.cache_clear()

        config = get_star_generation_config()

        assert isinstance(config, StarGenerationConfig)
        assert hasattr(config, 'type_weights')
        assert hasattr(config, 'mass_sigma')
        assert hasattr(config, 'stefan_boltzmann_types')

        get_star_generation_config.cache_clear()

    def test_cached_config_fallback_on_error(self):
        """Test that get_star_generation_config falls back to defaults on error."""
        get_star_generation_config.cache_clear()

        with patch(
            'game.strategy.generation.loaders.astrophysics_loader.AstrophysicsLoader'
        ) as mock_loader:
            mock_loader.return_value.load.side_effect = FileNotFoundError("Test error")

            config = get_star_generation_config()

            assert isinstance(config, StarGenerationConfig)
            assert config.type_weights["MAIN_SEQUENCE"] == 0.525
            assert config.mass_sigma == 0.8

        get_star_generation_config.cache_clear()


class TestStarGenerationConfigCatchNarrowing:
    """PROJ-381 Phase 3 (ERR-04-007): ValueError / KeyError must NOT
    be silently masked behind the defaults fallback — they indicate
    data-integrity bugs that should surface."""

    def test_value_error_in_loader_propagates(self):
        """A ValueError from the loader must propagate, not be swallowed."""
        get_star_generation_config.cache_clear()
        try:
            with patch(
                "game.strategy.generation.loaders.astrophysics_loader.AstrophysicsLoader"
            ) as MockLoader:
                MockLoader.return_value.load.side_effect = ValueError("bad config dict")
                with pytest.raises(ValueError, match="bad config dict"):
                    get_star_generation_config()
        finally:
            get_star_generation_config.cache_clear()

    def test_key_error_in_loader_propagates(self):
        """A KeyError from the loader must propagate, not be swallowed."""
        get_star_generation_config.cache_clear()
        try:
            with patch(
                "game.strategy.generation.loaders.astrophysics_loader.AstrophysicsLoader"
            ) as MockLoader:
                MockLoader.return_value.load.side_effect = KeyError("missing_key")
                with pytest.raises(KeyError):
                    get_star_generation_config()
        finally:
            get_star_generation_config.cache_clear()

    def test_file_not_found_still_returns_defaults(self):
        """FileNotFoundError stays in the catch tuple — defaults returned."""
        get_star_generation_config.cache_clear()
        try:
            with patch(
                "game.strategy.generation.loaders.astrophysics_loader.AstrophysicsLoader"
            ) as MockLoader:
                MockLoader.return_value.load.side_effect = FileNotFoundError("no file")
                config = get_star_generation_config()
                # Defaults: MAIN_SEQUENCE weight is 0.525.
                assert isinstance(config, StarGenerationConfig)
                assert config.type_weights["MAIN_SEQUENCE"] == 0.525
        finally:
            get_star_generation_config.cache_clear()
