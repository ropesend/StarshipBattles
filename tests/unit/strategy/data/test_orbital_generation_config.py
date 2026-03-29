"""
Unit tests for OrbitalGenerationConfig.

Tests cover:
- OrbitalGenerationConfig defaults
- OrbitalGenerationConfig from JSON
- get_orbital_generation_config caching behavior
"""
import pytest
from unittest.mock import patch

from game.strategy.data.orbital_generation_config import (
    OrbitalGenerationConfig,
    get_orbital_generation_config,
)


class TestOrbitalGenerationConfigDefaults:
    """Tests for OrbitalGenerationConfig initialization with defaults."""

    def test_init_no_data_uses_defaults(self):
        """Test that init with None uses default values."""
        config = OrbitalGenerationConfig(None)

        # Orbital parameters
        assert config.safe_start_offset == 2
        assert config.max_orbital_distance == 20
        assert config.default_planet_min == 3
        assert config.default_planet_max == 10
        assert config.orbital_distribution_mode == 0.3
        assert config.max_placement_attempts == 20
        assert config.hot_jupiter_log_mass_min == 26.7
        assert config.hot_jupiter_log_mass_max == 28.0
        assert config.hot_jupiter_orbit_min == 2
        assert config.hot_jupiter_orbit_max == 3

    def test_default_mass_generation(self):
        """Test mass generation distribution defaults."""
        config = OrbitalGenerationConfig(None)
        assert config.small_bias_mu == 24.0
        assert config.small_bias_sigma == 0.8
        assert config.large_bias_mu == 26.5
        assert config.large_bias_sigma == 0.8
        assert config.default_mu == 24.0
        assert config.default_sigma == 1.0
        assert config.mass_max_iterations == 100

    def test_default_moon_system(self):
        """Test moon system thresholds and probabilities."""
        config = OrbitalGenerationConfig(None)
        assert config.jupiter_threshold_log == 27.27
        assert config.earth_threshold_log == 24.77
        assert config.ceres_threshold_log == 20.97
        assert config.jupiter_chance == 0.88
        assert config.earth_chance == 0.35
        assert config.ceres_chance == 0.02
        assert config.max_chance_cap == 0.95
        assert config.mass_ratio_min == 0.00001
        assert config.mass_ratio_max == 0.05
        assert config.max_moons_per_body == 50

    def test_default_surface(self):
        """Test surface flag generation defaults."""
        config = OrbitalGenerationConfig(None)
        assert config.active_body_activity_min == 0.1
        assert config.active_body_activity_max == 0.8
        assert config.active_body_mag_min == 0.5
        assert config.active_body_mag_max == 2.0
        assert config.small_body_activity_min == 0.0
        assert config.small_body_activity_max == 0.2
        assert config.small_body_mag_min == 0.0
        assert config.small_body_mag_max == 0.5
        assert config.water_temp_min == 250
        assert config.water_temp_max == 350


class TestOrbitalGenerationConfigFromJson:
    """Tests for OrbitalGenerationConfig initialization from JSON data."""

    def test_init_with_json_data(self):
        """Test that init with valid JSON data loads values correctly."""
        data = {
            "orbital_generation": {
                "orbital": {
                    "safe_start_offset": 3,
                    "max_orbital_distance": 25,
                },
                "mass_generation": {
                    "small_bias_mu": 23.5,
                    "default_sigma": 1.2,
                },
                "moon_system": {
                    "jupiter_chance": 0.90,
                    "max_moons_per_body": 40,
                },
                "surface": {
                    "water_temp_min": 260,
                },
            }
        }

        config = OrbitalGenerationConfig(data)

        assert config.safe_start_offset == 3
        assert config.max_orbital_distance == 25
        assert config.small_bias_mu == 23.5
        assert config.default_sigma == 1.2
        assert config.jupiter_chance == 0.90
        assert config.max_moons_per_body == 40
        assert config.water_temp_min == 260

    def test_json_overrides_defaults(self):
        """Test that JSON values override default values."""
        data = {
            "orbital_generation": {
                "moon_system": {
                    "max_chance_cap": 0.99,
                },
            }
        }

        config = OrbitalGenerationConfig(data)

        # JSON override
        assert config.max_chance_cap == 0.99
        # Non-overridden values use defaults
        assert config.jupiter_chance == 0.88
        assert config.safe_start_offset == 2

    def test_partial_json_falls_back_to_defaults(self):
        """Test that missing JSON keys fall back to default values."""
        data = {
            "orbital_generation": {
                "orbital": {
                    "safe_start_offset": 4,
                },
            }
        }

        config = OrbitalGenerationConfig(data)

        assert config.safe_start_offset == 4
        assert config.max_orbital_distance == 20  # Default
        assert config.small_bias_mu == 24.0  # Default
        assert config.jupiter_chance == 0.88  # Default

    def test_no_orbital_generation_key_uses_defaults(self):
        """Test that data without 'orbital_generation' key uses defaults."""
        data = {"other_key": {"some_value": 123}}

        config = OrbitalGenerationConfig(data)

        assert config.safe_start_offset == 2
        assert config.small_bias_mu == 24.0
        assert config.jupiter_chance == 0.88
        assert config.water_temp_min == 250


class TestGetOrbitalGenerationConfig:
    """Tests for the get_orbital_generation_config cached function."""

    def test_cached_config_returns_instance(self):
        """Test that get_orbital_generation_config returns an instance."""
        get_orbital_generation_config.cache_clear()

        config = get_orbital_generation_config()

        assert isinstance(config, OrbitalGenerationConfig)
        assert hasattr(config, 'safe_start_offset')
        assert hasattr(config, 'jupiter_chance')
        assert hasattr(config, 'water_temp_min')

        get_orbital_generation_config.cache_clear()

    def test_cached_config_fallback_on_error(self):
        """Test that get_orbital_generation_config falls back to defaults on error."""
        get_orbital_generation_config.cache_clear()

        with patch(
            'game.strategy.generation.loaders.astrophysics_loader.AstrophysicsLoader'
        ) as mock_loader:
            mock_loader.return_value.load.side_effect = FileNotFoundError("Test error")

            config = get_orbital_generation_config()

            assert isinstance(config, OrbitalGenerationConfig)
            assert config.safe_start_offset == 2
            assert config.jupiter_chance == 0.88

        get_orbital_generation_config.cache_clear()
