"""
Tests for habitability scoring system.

Tests cover individual factor calculations and the overall scoring function
that determines how suitable a planet is for a given species.
"""
import pytest
from game.strategy.formulas.habitability import (
    calculate_gravity_factor,
    calculate_temperature_factor,
    calculate_water_factor,
    calculate_atmosphere_factor,
    calculate_radiation_factor,
    calculate_habitability,
    score_planet_for_race,
)
from game.strategy.data.planet import Planet
from game.core.hex_math import HexCoord
from game.strategy.data.race_config import RaceConfig


# --- Gravity Factor Tests ---

class TestGravityFactor:
    """Tests for gravity habitability factor."""

    def test_perfect_match_returns_1(self):
        """Planet gravity exactly matching ideal returns 1.0."""
        # Race wants 1.0g (9.81 m/s²)
        factor = calculate_gravity_factor(
            planet_gravity_ms2=9.81,
            ideal_gravity_g=1.0,
            tolerance_g=0.3
        )
        assert factor == pytest.approx(1.0, abs=0.01)

    def test_within_tolerance_returns_high(self):
        """Gravity within tolerance range returns high factor."""
        # Race wants 1.0g ± 0.3g, planet is 1.2g
        factor = calculate_gravity_factor(
            planet_gravity_ms2=1.2 * 9.81,
            ideal_gravity_g=1.0,
            tolerance_g=0.3
        )
        assert factor > 0.5  # Still livable
        assert factor < 1.0  # Not perfect

    def test_outside_tolerance_reduces_score(self):
        """Gravity outside tolerance reduces score significantly."""
        # Race wants 1.0g ± 0.3g, planet is 2.0g (way outside)
        factor = calculate_gravity_factor(
            planet_gravity_ms2=2.0 * 9.81,
            ideal_gravity_g=1.0,
            tolerance_g=0.3
        )
        assert factor < 0.3  # Significantly reduced

    def test_extreme_gravity_approaches_zero(self):
        """Extreme gravity difference approaches zero."""
        # Race wants 1.0g, planet is 5.0g
        factor = calculate_gravity_factor(
            planet_gravity_ms2=5.0 * 9.81,
            ideal_gravity_g=1.0,
            tolerance_g=0.3
        )
        assert factor < 0.1

    def test_low_gravity_species_on_low_g_planet(self):
        """Low-g species on low-g planet is comfortable."""
        # Race wants 0.5g ± 0.2g, planet is 0.4g
        factor = calculate_gravity_factor(
            planet_gravity_ms2=0.4 * 9.81,
            ideal_gravity_g=0.5,
            tolerance_g=0.2
        )
        assert factor > 0.8


# --- Temperature Factor Tests ---

class TestTemperatureFactor:
    """Tests for temperature habitability factor."""

    def test_perfect_match_returns_1(self):
        """Planet temp exactly matching ideal returns 1.0."""
        factor = calculate_temperature_factor(
            planet_temp_k=293.0,
            ideal_temp_k=293.0,
            tolerance_k=50.0
        )
        assert factor == pytest.approx(1.0, abs=0.01)

    def test_within_tolerance_returns_high(self):
        """Temperature within tolerance range returns high factor."""
        # Race wants 293K ± 50K, planet is 310K
        factor = calculate_temperature_factor(
            planet_temp_k=310.0,
            ideal_temp_k=293.0,
            tolerance_k=50.0
        )
        assert factor > 0.5
        assert factor < 1.0

    def test_outside_tolerance_reduces_score(self):
        """Temperature outside tolerance reduces score."""
        # Race wants 293K ± 50K, planet is 400K (hot)
        factor = calculate_temperature_factor(
            planet_temp_k=400.0,
            ideal_temp_k=293.0,
            tolerance_k=50.0
        )
        assert factor < 0.3

    def test_ice_planet_for_tropical_species(self):
        """Ice planet is harsh for tropical species."""
        # Tropical species (ideal 310K), ice planet (150K)
        factor = calculate_temperature_factor(
            planet_temp_k=150.0,
            ideal_temp_k=310.0,
            tolerance_k=30.0
        )
        assert factor < 0.1

    def test_ice_species_on_ice_planet(self):
        """Ice-adapted species on ice planet is comfortable."""
        # Ice species (ideal 200K ± 40K), ice planet (180K)
        factor = calculate_temperature_factor(
            planet_temp_k=180.0,
            ideal_temp_k=200.0,
            tolerance_k=40.0
        )
        assert factor > 0.7


# --- Water Factor Tests ---

class TestWaterFactor:
    """Tests for water coverage habitability factor."""

    def test_perfect_match_returns_1(self):
        """Water coverage exactly matching ideal returns 1.0."""
        factor = calculate_water_factor(
            planet_water=0.5,
            ideal_water=0.5,
            tolerance=0.2
        )
        assert factor == pytest.approx(1.0, abs=0.01)

    def test_within_tolerance_returns_high(self):
        """Water within tolerance returns high factor."""
        # Race wants 50% ± 20%, planet has 60%
        factor = calculate_water_factor(
            planet_water=0.6,
            ideal_water=0.5,
            tolerance=0.2
        )
        assert factor > 0.7

    def test_desert_planet_for_aquatic_species(self):
        """Desert planet is harsh for aquatic species."""
        # Aquatic species (wants 80% water), desert planet (5%)
        factor = calculate_water_factor(
            planet_water=0.05,
            ideal_water=0.8,
            tolerance=0.1
        )
        assert factor < 0.1

    def test_ocean_planet_for_desert_species(self):
        """Ocean planet is harsh for desert species."""
        # Desert species (wants 10% water), ocean planet (95%)
        factor = calculate_water_factor(
            planet_water=0.95,
            ideal_water=0.1,
            tolerance=0.1
        )
        assert factor < 0.1

    def test_outside_tolerance_reduces_score(self):
        """Water outside tolerance reduces score."""
        factor = calculate_water_factor(
            planet_water=0.9,
            ideal_water=0.5,
            tolerance=0.2
        )
        assert factor < 0.5


# --- Atmosphere Factor Tests ---

class TestAtmosphereFactor:
    """Tests for atmosphere composition habitability factor."""

    def test_neutral_atmosphere_returns_base(self):
        """Neutral atmosphere preferences return ~0.5 baseline."""
        factor = calculate_atmosphere_factor(
            planet_atmosphere={"Oxygen": 21000.0, "Nitrogen": 78000.0},
            atmosphere_preferences={"Oxygen": 0.0, "Nitrogen": 0.0}
        )
        # Neutral should be around 0.5 (neither beneficial nor harmful)
        assert 0.4 <= factor <= 0.6

    def test_beneficial_atmosphere_boosts_score(self):
        """Beneficial gas boosts habitability score."""
        # Species loves oxygen (+80)
        factor = calculate_atmosphere_factor(
            planet_atmosphere={"Oxygen": 21000.0},  # ~21% at 1 atm
            atmosphere_preferences={"Oxygen": 80.0}
        )
        assert factor > 0.7

    def test_toxic_atmosphere_reduces_score(self):
        """Toxic gas reduces habitability score."""
        # Species hates methane (-80)
        factor = calculate_atmosphere_factor(
            planet_atmosphere={"Methane": 50000.0},  # High methane
            atmosphere_preferences={"Methane": -80.0, "Oxygen": 0.0}
        )
        assert factor < 0.3

    def test_mixed_atmosphere_balanced(self):
        """Mixed beneficial and toxic gases balance out."""
        # Equal parts beneficial and toxic at same pressure
        factor = calculate_atmosphere_factor(
            planet_atmosphere={"Oxygen": 50000.0, "Methane": 50000.0},
            atmosphere_preferences={"Oxygen": 50.0, "Methane": -50.0}
        )
        # Should be middling (close to 0.5 when equal parts)
        assert 0.4 <= factor <= 0.6

    def test_empty_atmosphere(self):
        """Empty/vacuum atmosphere."""
        factor = calculate_atmosphere_factor(
            planet_atmosphere={},
            atmosphere_preferences={"Oxygen": 80.0}
        )
        # No beneficial gas present = lower score
        assert factor <= 0.5


# --- Radiation Factor Tests ---

class TestRadiationFactor:
    """Tests for radiation/magnetic field habitability factor."""

    def test_strong_field_high_score(self):
        """Strong magnetic field gives high score for most species."""
        # Normal sensitivity (0), strong field (1.0 = Earth-like)
        factor = calculate_radiation_factor(
            magnetic_field=1.0,
            radiation_tolerance=0.0
        )
        assert factor > 0.8

    def test_low_field_penalizes_sensitive_species(self):
        """Low magnetic field penalizes radiation-sensitive species."""
        # Sensitive species (-50), weak field (0.1)
        factor = calculate_radiation_factor(
            magnetic_field=0.1,
            radiation_tolerance=-50.0
        )
        assert factor < 0.5

    def test_low_field_ok_for_resistant_species(self):
        """Low magnetic field is fine for radiation-resistant species."""
        # Resistant species (+80), weak field (0.1)
        factor = calculate_radiation_factor(
            magnetic_field=0.1,
            radiation_tolerance=80.0
        )
        assert factor > 0.7

    def test_zero_field_harsh_for_normal(self):
        """Zero magnetic field is harsh for normal species."""
        factor = calculate_radiation_factor(
            magnetic_field=0.0,
            radiation_tolerance=0.0
        )
        assert factor < 0.5


# --- Full Habitability Score Tests ---

class TestCalculateHabitability:
    """Tests for the full habitability calculation."""

    def test_perfect_match_returns_near_1(self):
        """Planet conditions matching race ideal returns near 1.0."""
        score = calculate_habitability(
            gravity_ms2=9.81,  # 1.0g
            temperature_k=293.0,
            water_coverage=0.5,
            atmosphere={"Oxygen": 21000.0, "Nitrogen": 78000.0},
            magnetic_field=1.0,
            gravity_ideal=1.0,
            gravity_tolerance=0.3,
            temp_ideal=293.0,
            temp_tolerance=50.0,
            water_ideal=0.5,
            water_tolerance=0.2,
            atmosphere_preferences={"Oxygen": 50.0, "Nitrogen": 20.0},
            radiation_tolerance=0.0
        )
        assert score > 0.8

    def test_completely_incompatible_returns_near_0(self):
        """Extreme mismatch returns near 0.0."""
        # Ice species on magma planet
        score = calculate_habitability(
            gravity_ms2=3.0 * 9.81,  # 3.0g (crushing)
            temperature_k=1500.0,  # Magma temps
            water_coverage=0.0,  # No water
            atmosphere={"Sulfur Dioxide": 90000.0},  # Toxic
            magnetic_field=0.0,  # No protection
            gravity_ideal=0.5,  # Wants low g
            gravity_tolerance=0.1,
            temp_ideal=200.0,  # Wants ice
            temp_tolerance=30.0,
            water_ideal=0.8,  # Wants water
            water_tolerance=0.1,
            atmosphere_preferences={"Oxygen": 80.0, "Sulfur Dioxide": -100.0},
            radiation_tolerance=-50.0  # Radiation sensitive
        )
        assert score < 0.1

    def test_one_zero_factor_tanks_score(self):
        """One completely incompatible factor tanks overall score."""
        # Everything perfect except temperature (magma)
        score = calculate_habitability(
            gravity_ms2=9.81,
            temperature_k=2000.0,  # Magma!
            water_coverage=0.5,
            atmosphere={"Oxygen": 21000.0},
            magnetic_field=1.0,
            gravity_ideal=1.0,
            gravity_tolerance=0.3,
            temp_ideal=293.0,
            temp_tolerance=50.0,
            water_ideal=0.5,
            water_tolerance=0.2,
            atmosphere_preferences={"Oxygen": 50.0},
            radiation_tolerance=0.0
        )
        # Geometric mean should pull this down significantly
        assert score < 0.3


# --- Convenience Wrapper Tests ---

class TestScorePlanetForRace:
    """Tests for the convenience wrapper function."""

    @pytest.fixture
    def earth_like_planet(self):
        """Create an Earth-like test planet."""
        return Planet(
            name="Terra",
            location=HexCoord(0, 0),
            orbit_distance=1,
            mass=5.97e24,
            radius=6.371e6,
            surface_area=5.1e14,
            density=5515.0,
            surface_gravity=9.81,
            surface_pressure=101325.0,
            surface_temperature=288.0,
            surface_water=0.71,
            tectonic_activity=0.5,
            magnetic_field=1.0,
            atmosphere={"Oxygen": 21000.0, "Nitrogen": 78000.0}
        )

    @pytest.fixture
    def human_race_config(self):
        """Create a human-like race configuration."""
        return RaceConfig(
            race_id="humans",
            name="Humans",
            gravity_ideal=1.0,
            gravity_tolerance=0.3,
            temperature_ideal=288.0,
            temperature_tolerance=50.0,
            water_ideal=0.7,
            water_tolerance=0.3,
            atmosphere_preferences={"Oxygen": 80.0, "Nitrogen": 20.0, "Carbon Dioxide": -20.0},
            radiation_tolerance=0.0
        )

    @pytest.fixture
    def ice_dweller_config(self):
        """Create an ice-dwelling species configuration."""
        return RaceConfig(
            race_id="cryonians",
            name="Cryonians",
            gravity_ideal=0.5,
            gravity_tolerance=0.2,
            temperature_ideal=180.0,
            temperature_tolerance=40.0,
            water_ideal=0.1,  # Frozen water, not liquid
            water_tolerance=0.1,
            atmosphere_preferences={"Nitrogen": 50.0, "Oxygen": -30.0},
            radiation_tolerance=50.0  # Radiation resistant
        )

    def test_score_planet_for_race_convenience(self, earth_like_planet, human_race_config):
        """Integration test with real Planet and RaceConfig objects."""
        score = score_planet_for_race(earth_like_planet, human_race_config)
        # Humans on Earth should score very high
        assert score > 0.7
        assert score <= 1.0

    def test_ice_species_on_earth(self, earth_like_planet, ice_dweller_config):
        """Ice species on Earth-like planet should score poorly."""
        score = score_planet_for_race(earth_like_planet, ice_dweller_config)
        # Too warm, too much gravity, wrong atmosphere
        assert score < 0.3

    def test_returns_float_in_range(self, earth_like_planet, human_race_config):
        """Score is always a float between 0 and 1."""
        score = score_planet_for_race(earth_like_planet, human_race_config)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0


class TestEdgeCases:
    """Edge case tests for habitability scoring."""

    def test_zero_tolerance_exact_match(self):
        """Zero tolerance with exact match still works."""
        factor = calculate_gravity_factor(
            planet_gravity_ms2=9.81,
            ideal_gravity_g=1.0,
            tolerance_g=0.0  # No tolerance
        )
        assert factor == pytest.approx(1.0, abs=0.01)

    def test_zero_tolerance_any_deviation(self):
        """Zero tolerance with any deviation penalizes heavily."""
        factor = calculate_gravity_factor(
            planet_gravity_ms2=9.82,  # Tiny difference
            ideal_gravity_g=1.0,
            tolerance_g=0.0
        )
        # Should still be lower than perfect
        assert factor < 1.0

    def test_very_high_tolerance_forgiving(self):
        """Very high tolerance is very forgiving."""
        factor = calculate_temperature_factor(
            planet_temp_k=400.0,
            ideal_temp_k=293.0,
            tolerance_k=200.0  # Very tolerant
        )
        assert factor > 0.5

    def test_none_race_config_fields_use_defaults(self):
        """Missing atmosphere preferences handled gracefully."""
        # RaceConfig with empty atmosphere preferences
        config = RaceConfig(
            race_id="test",
            name="Test",
            atmosphere_preferences={}
        )
        planet = Planet(
            name="Test",
            location=HexCoord(0, 0),
            orbit_distance=1,
            mass=5.97e24,
            radius=6.371e6,
            surface_area=5.1e14,
            density=5515.0,
            surface_gravity=9.81,
            surface_pressure=101325.0,
            surface_temperature=288.0,
            surface_water=0.5,
            tectonic_activity=0.5,
            magnetic_field=1.0,
            atmosphere={"Oxygen": 21000.0}
        )
        # Should not crash
        score = score_planet_for_race(planet, config)
        assert 0.0 <= score <= 1.0
