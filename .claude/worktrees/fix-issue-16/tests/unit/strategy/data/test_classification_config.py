"""
Unit tests for ClassificationConfig.

Tests cover:
- ClassificationConfig defaults
- ClassificationConfig from JSON
- get_classification_config caching behavior
"""
import pytest
from unittest.mock import patch, MagicMock

from game.strategy.data.classification_config import (
    ClassificationConfig,
    get_classification_config,
)


class TestClassificationConfigDefaults:
    """Tests for ClassificationConfig initialization with defaults."""

    def test_init_no_data_uses_defaults(self):
        """Test that init with None uses default values."""
        config = ClassificationConfig(None)

        # Mass thresholds
        assert config.dwarf_max == 2.0e23
        assert config.giant_min == 6.0e24
        assert config.gas_giant_min == 1.0e26

        # Temperature thresholds
        assert config.ice_dwarf_max == 170
        assert config.cryo_max == 255
        assert config.cold_limit == 200
        assert config.magma == 700
        assert config.magma_activity == 350
        assert config.hot_limit == 400
        assert config.continental_temp_min == 255
        assert config.continental_temp_max == 330

        # Pressure thresholds
        assert config.vacuum == 500
        assert config.chthonian_max == 10000
        assert config.continental_pressure_min == 5000

        # Water thresholds
        assert config.arid == 0.20
        assert config.ocean_world == 0.85
        assert config.continental_water_min == 0.10

        # Activity threshold
        assert config.activity_magma_threshold == 0.7



class TestClassificationConfigFromJson:
    """Tests for ClassificationConfig initialization from JSON data."""

    def test_init_with_json_data(self):
        """Test that init with valid JSON data loads values correctly."""
        data = {
            "classification": {
                "mass_thresholds": {
                    "dwarf_max": 1.0e23,
                    "giant_min": 5.0e24,
                    "gas_giant_min": 8.0e25,
                },
                "temperature_thresholds": {
                    "ice_dwarf_max": 150,
                    "cryo_max": 240,
                    "cold_limit": 180,
                    "magma": 650,
                    "magma_activity": 300,
                    "hot_limit": 380,
                    "continental_min": 260,
                    "continental_max": 320,
                },
                "pressure_thresholds": {
                    "vacuum": 400,
                    "chthonian_max": 8000,
                    "continental_min": 4500,
                },
                "water_coverage_thresholds": {
                    "arid": 0.15,
                    "ocean_world": 0.90,
                    "continental_min": 0.12,
                },
            }
        }

        config = ClassificationConfig(data)

        # Verify JSON values are loaded
        assert config.dwarf_max == 1.0e23
        assert config.giant_min == 5.0e24
        assert config.gas_giant_min == 8.0e25
        assert config.ice_dwarf_max == 150
        assert config.cryo_max == 240
        assert config.vacuum == 400
        assert config.arid == 0.15
        assert config.ocean_world == 0.90

    def test_json_overrides_defaults(self):
        """Test that JSON values override default values."""
        data = {
            "classification": {
                "mass_thresholds": {
                    "dwarf_max": 3.0e23,  # Different from default 2.0e23
                },
                "temperature_thresholds": {
                    "ice_dwarf_max": 200,  # Different from default 170
                },
            }
        }

        config = ClassificationConfig(data)

        # JSON overrides
        assert config.dwarf_max == 3.0e23
        assert config.ice_dwarf_max == 200

        # Non-overridden values use defaults
        assert config.giant_min == 6.0e24  # Default
        assert config.cryo_max == 255  # Default

    def test_partial_json_falls_back_to_defaults(self):
        """Test that missing JSON keys fall back to default values."""
        data = {
            "classification": {
                "mass_thresholds": {
                    "dwarf_max": 1.5e23,
                    # giant_min and gas_giant_min missing
                },
                # temperature_thresholds, pressure_thresholds, water_coverage_thresholds missing
            }
        }

        config = ClassificationConfig(data)

        # Provided value
        assert config.dwarf_max == 1.5e23

        # Missing mass thresholds fall back to defaults
        assert config.giant_min == 6.0e24
        assert config.gas_giant_min == 1.0e26

        # Missing sections fall back to defaults
        assert config.ice_dwarf_max == 170
        assert config.vacuum == 500
        assert config.arid == 0.20

    def test_no_classification_key_uses_defaults(self):
        """Test that data without 'classification' key uses defaults."""
        data = {
            "other_key": {"some_value": 123},
        }

        config = ClassificationConfig(data)

        # All values should be defaults
        assert config.dwarf_max == 2.0e23
        assert config.ice_dwarf_max == 170
        assert config.vacuum == 500
        assert config.arid == 0.20
        assert config.activity_magma_threshold == 0.7


class TestGetClassificationConfig:
    """Tests for the get_classification_config cached function."""

    def test_cached_config_fallback_on_error(self):
        """Test that get_classification_config falls back to defaults on error."""
        # Clear cache before test
        get_classification_config.cache_clear()

        # Mock the loader to raise an error
        with patch(
            'game.strategy.generation.loaders.astrophysics_loader.AstrophysicsLoader'
        ) as mock_loader:
            mock_loader.return_value.load.side_effect = FileNotFoundError("Test error")

            config = get_classification_config()

            assert isinstance(config, ClassificationConfig)
            # Should use default values
            assert config.dwarf_max == 2.0e23
            assert config.ice_dwarf_max == 170
            assert config.vacuum == 500
            assert config.arid == 0.20

        # Clear cache after test to not affect other tests
        get_classification_config.cache_clear()
