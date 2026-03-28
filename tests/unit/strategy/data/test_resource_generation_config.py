"""
Unit tests for ResourceGenerationConfig.

Tests configuration loading from JSON and fallback to defaults.
"""
import pytest

from game.strategy.data.resource_generation_config import ResourceGenerationConfig


class TestResourceGenerationConfigDefaults:
    """Tests for default configuration when no JSON is provided."""

    def test_defaults_when_no_data(self):
        """Config uses defaults when initialized with None."""
        cfg = ResourceGenerationConfig(None)

        assert cfg.min_log_mass == 20.0
        assert cfg.max_log_mass == 28.0
        assert cfg.earth_mass_baseline == 10_000_000
        assert cfg.qty_determinism == 0.7
        assert cfg.qty_randomness == 0.3
        assert cfg.qty_minimum_floor == 10_000
        assert cfg.max_quality == 100.0
        assert cfg.qual_determinism == 0.7
        assert cfg.qual_randomness == 0.3
        assert cfg.qual_minimum_floor == 5.0

    def test_defaults_when_empty_data(self):
        """Config uses defaults when data has no resource_generation key."""
        cfg = ResourceGenerationConfig({"classification": {}})

        assert cfg.earth_mass_baseline == 10_000_000
        assert cfg.min_log_mass == 20.0

    def test_affinity_default_is_one(self):
        """Missing affinities default to 1.0."""
        cfg = ResourceGenerationConfig(None)

        assert cfg.get_affinity("MAGMA", "Metals") == 1.0
        assert cfg.get_affinity("NONEXISTENT", "Metals") == 1.0


class TestResourceGenerationConfigFromJson:
    """Tests for configuration loaded from JSON data."""

    @pytest.fixture
    def sample_json(self):
        """Sample astrophysics.json data with resource_generation."""
        return {
            "resource_generation": {
                "mass_scaling": {
                    "min_log_mass": 19.0,
                    "max_log_mass": 29.0
                },
                "quantity": {
                    "earth_mass_baseline": 5_000_000,
                    "determinism_weight": 0.6,
                    "randomness_weight": 0.4,
                    "minimum_floor": 5000
                },
                "quality": {
                    "max_quality": 80.0,
                    "determinism_weight": 0.8,
                    "randomness_weight": 0.2,
                    "minimum_floor": 10.0
                },
                "planet_type_affinities": {
                    "MAGMA": {
                        "Metals": 2.0,
                        "Organics": 0.3
                    }
                }
            }
        }

    def test_loads_mass_scaling(self, sample_json):
        """Mass scaling parameters loaded from JSON."""
        cfg = ResourceGenerationConfig(sample_json)

        assert cfg.min_log_mass == 19.0
        assert cfg.max_log_mass == 29.0

    def test_loads_quantity_params(self, sample_json):
        """Quantity parameters loaded from JSON."""
        cfg = ResourceGenerationConfig(sample_json)

        assert cfg.earth_mass_baseline == 5_000_000
        assert cfg.qty_determinism == 0.6
        assert cfg.qty_randomness == 0.4
        assert cfg.qty_minimum_floor == 5000

    def test_loads_quality_params(self, sample_json):
        """Quality parameters loaded from JSON."""
        cfg = ResourceGenerationConfig(sample_json)

        assert cfg.max_quality == 80.0
        assert cfg.qual_determinism == 0.8
        assert cfg.qual_randomness == 0.2
        assert cfg.qual_minimum_floor == 10.0

    def test_loads_affinities(self, sample_json):
        """Planet type affinities loaded from JSON."""
        cfg = ResourceGenerationConfig(sample_json)

        assert cfg.get_affinity("MAGMA", "Metals") == 2.0
        assert cfg.get_affinity("MAGMA", "Organics") == 0.3

    def test_missing_affinity_defaults_to_one(self, sample_json):
        """Unspecified affinities default to 1.0."""
        cfg = ResourceGenerationConfig(sample_json)

        # MAGMA has no Vapors entry
        assert cfg.get_affinity("MAGMA", "Vapors") == 1.0
        # CONTINENTAL has no entries at all
        assert cfg.get_affinity("CONTINENTAL", "Metals") == 1.0

    def test_partial_json_uses_defaults_for_missing(self):
        """Partial JSON falls back to defaults for missing fields."""
        partial = {
            "resource_generation": {
                "mass_scaling": {},
                "quantity": {"earth_mass_baseline": 8_000_000},
                "quality": {},
                "planet_type_affinities": {}
            }
        }
        cfg = ResourceGenerationConfig(partial)

        assert cfg.earth_mass_baseline == 8_000_000
        # Missing fields use defaults
        assert cfg.min_log_mass == 20.0
        assert cfg.qty_determinism == 0.7
        assert cfg.max_quality == 100.0
