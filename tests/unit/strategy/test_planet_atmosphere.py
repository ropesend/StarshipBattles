"""
Unit tests for planet atmosphere generation.

Tests atmospheric composition, pressure calculations,
gas retention, and greenhouse effects.
"""

import pytest
import math
from unittest.mock import patch

from game.strategy.data.planet_atmosphere import (
    generate_atmosphere,
    _calculate_retained_gases,
    _calculate_base_pressure,
    _distribute_gas_composition,
    _calculate_greenhouse_effect,
)
from game.strategy.data.planet_physics import (
    BOLTZMANN_K, ATM_TO_PA, GASES, MASS_EARTH,
    MASS_JUPITER, MASS_MARS
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def earth_like_params():
    """Parameters for an Earth-like planet."""
    return {
        "mass": MASS_EARTH,
        "escape_vel": 11186.0,  # m/s
        "base_temp": 255.0,  # K (blackbody temp)
        "flux_wm2": 1361.0,  # W/m^2 (solar constant)
    }


@pytest.fixture
def gas_giant_params():
    """Parameters for a Jupiter-like gas giant."""
    return {
        "mass": MASS_JUPITER,
        "escape_vel": 59500.0,  # m/s
        "base_temp": 110.0,  # K
        "flux_wm2": 50.0,  # W/m^2
    }


@pytest.fixture
def small_body_params():
    """Parameters for a small body like the Moon."""
    return {
        "mass": 7.34e22,  # Moon mass
        "escape_vel": 2380.0,  # m/s
        "base_temp": 270.0,  # K
        "flux_wm2": 1361.0,  # W/m^2
    }


@pytest.fixture
def hot_small_body_params():
    """Parameters for a hot Mercury-like body."""
    return {
        "mass": 3.30e23,  # Mercury mass
        "escape_vel": 4250.0,  # m/s
        "base_temp": 700.0,  # K (high temp)
        "flux_wm2": 9000.0,  # W/m^2
    }


# =============================================================================
# Test: Gas Retention Calculation
# =============================================================================


class TestGasRetention:
    """Tests for _calculate_retained_gases function."""

    def test_high_escape_velocity_retains_all_gases(self):
        """High escape velocity (gas giant) retains all gases."""
        escape_vel = 60000.0  # m/s
        retention_temp = 150.0  # K

        retained = _calculate_retained_gases(escape_vel, retention_temp)

        # Should retain all gases including light H2
        assert "H2" in retained
        assert "He" in retained
        assert "CO2" in retained
        assert "N2" in retained

    def test_earth_like_loses_hydrogen(self):
        """Earth-like escape velocity loses H2 but keeps heavier gases."""
        escape_vel = 11200.0  # m/s (Earth)
        retention_temp = 400.0  # K (exosphere temp)

        retained = _calculate_retained_gases(escape_vel, retention_temp)

        # Should NOT retain H2 (too light/fast)
        assert "H2" not in retained
        # Should retain heavier gases
        assert "CO2" in retained or "N2" in retained

    def test_low_escape_velocity_loses_most_gases(self):
        """Very low escape velocity loses most atmospheric gases."""
        escape_vel = 2000.0  # m/s (Moon-like)
        retention_temp = 400.0  # K

        retained = _calculate_retained_gases(escape_vel, retention_temp)

        # Should lose light gases
        assert "H2" not in retained
        assert "He" not in retained
        # May retain very heavy gases or none at all
        light_gas_count = sum(1 for g in ["H2", "He", "CH4", "NH3", "H2O"] if g in retained)
        assert light_gas_count == 0 or len(retained) < 5

    def test_cold_temperature_helps_retention(self):
        """Lower temperature means slower gas molecules, better retention."""
        escape_vel = 5000.0  # m/s

        # Cold temperature
        retained_cold = _calculate_retained_gases(escape_vel, 50.0)
        # Hot temperature
        retained_hot = _calculate_retained_gases(escape_vel, 500.0)

        # Cold should retain more gases
        assert len(retained_cold) >= len(retained_hot)

    def test_retention_formula_correctness(self):
        """Verify the retention formula: v_rms < escape_vel / 6."""
        escape_vel = 10000.0  # m/s
        retention_temp = 300.0  # K

        retained = _calculate_retained_gases(escape_vel, retention_temp)

        # Manually verify each retained gas meets criterion
        for gas_name in retained:
            molar_kg = GASES[gas_name]
            molecular_mass_kg = molar_kg / 6.022e23
            v_rms = math.sqrt(3 * BOLTZMANN_K * retention_temp / molecular_mass_kg)
            assert v_rms < (escape_vel / 6.0), f"{gas_name} should not be retained"

    def test_empty_retention_returns_empty_list(self):
        """Very low escape velocity returns empty list."""
        escape_vel = 100.0  # m/s (asteroid)
        retention_temp = 500.0  # K

        retained = _calculate_retained_gases(escape_vel, retention_temp)

        assert isinstance(retained, list)
        # May be empty or have only heaviest gases
        assert len(retained) <= 2  # At most heaviest gases

    def test_zero_escape_velocity(self):
        """Zero escape velocity retains nothing."""
        retained = _calculate_retained_gases(0.0, 300.0)

        assert len(retained) == 0

    def test_very_cold_temperature(self):
        """Very cold temperature (near absolute zero) maximizes retention."""
        escape_vel = 5000.0  # m/s
        retention_temp = 10.0  # K (very cold)

        retained = _calculate_retained_gases(escape_vel, retention_temp)

        # Should retain more gases than at room temperature
        retained_warm = _calculate_retained_gases(escape_vel, 300.0)
        assert len(retained) >= len(retained_warm)


# =============================================================================
# Test: Base Pressure Calculation
# =============================================================================


class TestBasePressure:
    """Tests for _calculate_base_pressure function."""

    @patch('game.strategy.data.planet_atmosphere.random.lognormvariate')
    def test_pressure_scales_with_mass_squared(self, mock_lognorm):
        """Pressure scales with mass^2."""
        mock_lognorm.return_value = 1.0  # Fixed volatile richness

        pressure_earth = _calculate_base_pressure(MASS_EARTH, ["N2", "CO2"], 300.0)
        pressure_half = _calculate_base_pressure(MASS_EARTH / 2, ["N2", "CO2"], 300.0)

        # mass^2 scaling means 0.5^2 = 0.25
        expected_ratio = 4.0  # (1/0.5)^2
        actual_ratio = pressure_earth / pressure_half
        assert abs(actual_ratio - expected_ratio) < 0.1

    @patch('game.strategy.data.planet_atmosphere.random.lognormvariate')
    def test_gas_giant_h2_multiplier(self, mock_lognorm):
        """H2 retention triggers 1000x pressure multiplier."""
        mock_lognorm.return_value = 1.0

        pressure_rocky = _calculate_base_pressure(MASS_EARTH * 3, ["N2", "CO2"], 100.0)
        pressure_gas_giant = _calculate_base_pressure(MASS_EARTH * 3, ["H2", "He", "N2"], 100.0)

        # H2 presence should multiply by 1000
        assert pressure_gas_giant >= pressure_rocky * 500  # Allow some tolerance

    @patch('game.strategy.data.planet_atmosphere.random.lognormvariate')
    def test_hot_small_body_atmosphere_stripped(self, mock_lognorm):
        """Hot body below Earth mass has atmosphere stripped (0.1x multiplier)."""
        mock_lognorm.return_value = 1.0

        # Hot body below Earth mass
        pressure_hot = _calculate_base_pressure(MASS_MARS, ["CO2"], 600.0)
        # Same body but cool
        pressure_cool = _calculate_base_pressure(MASS_MARS, ["CO2"], 300.0)

        # Hot body should have ~10% of cool body's pressure
        assert pressure_hot < pressure_cool

    @patch('game.strategy.data.planet_atmosphere.random.lognormvariate')
    def test_volatile_richness_affects_pressure(self, mock_lognorm):
        """Volatile richness roll affects final pressure."""
        mock_lognorm.return_value = 2.0
        pressure_rich = _calculate_base_pressure(MASS_EARTH, ["N2"], 300.0)

        mock_lognorm.return_value = 0.5
        pressure_poor = _calculate_base_pressure(MASS_EARTH, ["N2"], 300.0)

        assert pressure_rich > pressure_poor
        assert abs(pressure_rich / pressure_poor - 4.0) < 0.1

    @patch('game.strategy.data.planet_atmosphere.random.lognormvariate')
    def test_boundary_temperature_stripping(self, mock_lognorm):
        """Temperature at exactly 500K boundary doesn't strip atmosphere."""
        mock_lognorm.return_value = 1.0

        # Exactly 500K (boundary) - should NOT be stripped
        pressure_boundary = _calculate_base_pressure(MASS_MARS, ["CO2"], 500.0)
        # Just above 500K - should be stripped
        pressure_hot = _calculate_base_pressure(MASS_MARS, ["CO2"], 501.0)

        # Hot should be 10% of boundary
        assert pressure_hot < pressure_boundary


# =============================================================================
# Test: Gas Composition Distribution
# =============================================================================


class TestGasComposition:
    """Tests for _distribute_gas_composition function."""

    @patch('game.strategy.data.planet_atmosphere.random.uniform')
    def test_gas_giant_composition(self, mock_uniform):
        """Gas giant has H2/He dominated composition."""
        mock_uniform.return_value = 0.5

        # Large mass with H2
        composition = _distribute_gas_composition(
            ["H2", "He", "CH4"], MASS_EARTH * 3, 1e8
        )

        # H2 should be dominant
        total = sum(composition.values())
        if total > 0:
            h2_fraction = composition.get("H2", 0) / total
            he_fraction = composition.get("He", 0) / total
            # H2 should be ~75%, He ~24%
            assert h2_fraction > 0.5  # H2 dominant

    @patch('game.strategy.data.planet_atmosphere.random.uniform')
    def test_rocky_planet_co2_dominant(self, mock_uniform):
        """Rocky planet has CO2-dominated composition."""
        mock_uniform.return_value = 1.0  # Max weight

        composition = _distribute_gas_composition(
            ["CO2", "N2", "O2"], MASS_EARTH, 1e5
        )

        total = sum(composition.values())
        if total > 0:
            co2_fraction = composition.get("CO2", 0) / total
            # CO2 weight is 50 vs N2=20, O2=0.1
            # So CO2 should dominate
            assert co2_fraction > 0.3  # CO2 significant

    def test_composition_sums_to_total_pressure(self):
        """Partial pressures sum to total pressure."""
        pressure_pa = 100000.0

        # Use several runs with random
        for _ in range(5):
            composition = _distribute_gas_composition(
                ["CO2", "N2", "H2O"], MASS_EARTH, pressure_pa
            )

            total = sum(composition.values())
            # Should sum to input pressure (with small tolerance for rounding)
            assert abs(total - pressure_pa) < 1.0

    def test_empty_gas_list_returns_empty(self):
        """Empty retained gases returns empty composition."""
        composition = _distribute_gas_composition([], MASS_EARTH, 1e5)

        assert composition == {}

    @patch('game.strategy.data.planet_atmosphere.random.uniform')
    def test_single_gas_gets_full_pressure(self, mock_uniform):
        """Single gas gets entire pressure."""
        mock_uniform.return_value = 10.0
        pressure_pa = 50000.0

        composition = _distribute_gas_composition(["CO2"], MASS_EARTH, pressure_pa)

        assert "CO2" in composition
        assert abs(composition["CO2"] - pressure_pa) < 1.0

    def test_all_gases_positive_pressure(self):
        """All retained gases get positive partial pressure."""
        composition = _distribute_gas_composition(
            ["CO2", "N2", "O2", "Ar"], MASS_EARTH, 1e5
        )

        for gas, pressure in composition.items():
            assert pressure >= 0, f"{gas} has negative pressure"


# =============================================================================
# Test: Greenhouse Effect Calculation
# =============================================================================


class TestGreenhouseEffect:
    """Tests for _calculate_greenhouse_effect function."""

    def test_zero_pressure_no_greenhouse(self):
        """Zero pressure means no greenhouse effect."""
        result = _calculate_greenhouse_effect({}, 0, 0)

        assert result == 0

    def test_negative_pressure_no_greenhouse(self):
        """Negative pressure (invalid) returns zero."""
        result = _calculate_greenhouse_effect({"CO2": 1000}, -100, -0.001)

        assert result == 0

    def test_very_low_pressure_no_greenhouse(self):
        """Pressure below 0.01 atm gives no greenhouse effect."""
        composition = {"CO2": 500}  # Some CO2
        result = _calculate_greenhouse_effect(composition, 500, 0.005)

        assert result == 0

    def test_co2_increases_greenhouse(self):
        """CO2 presence increases greenhouse effect."""
        pressure_pa = ATM_TO_PA
        pressure_atm = 1.0

        # No greenhouse gases
        no_ghg = _calculate_greenhouse_effect({}, pressure_pa, pressure_atm)

        # With CO2
        with_co2 = _calculate_greenhouse_effect(
            {"CO2": pressure_pa * 0.04},  # 4% CO2
            pressure_pa,
            pressure_atm
        )

        assert with_co2 > no_ghg

    def test_h2o_stronger_than_co2(self):
        """H2O has 2x greenhouse factor vs CO2."""
        pressure_pa = ATM_TO_PA
        pressure_atm = 1.0

        # Same partial pressure of CO2 vs H2O
        partial = pressure_pa * 0.01  # 1%

        co2_effect = _calculate_greenhouse_effect(
            {"CO2": partial}, pressure_pa, pressure_atm
        )
        h2o_effect = _calculate_greenhouse_effect(
            {"H2O": partial}, pressure_pa, pressure_atm
        )

        # H2O should contribute ~2x as much
        assert h2o_effect > co2_effect

    def test_ch4_strongest_greenhouse(self):
        """CH4 has 5x greenhouse factor vs CO2."""
        pressure_pa = ATM_TO_PA
        pressure_atm = 1.0
        partial = pressure_pa * 0.01

        co2_effect = _calculate_greenhouse_effect(
            {"CO2": partial}, pressure_pa, pressure_atm
        )
        ch4_effect = _calculate_greenhouse_effect(
            {"CH4": partial}, pressure_pa, pressure_atm
        )

        # CH4 should contribute more than CO2
        # The 5x factor is applied to the GH contribution (fraction of pressure)
        # but the final temp increase also depends on base formula
        assert ch4_effect > co2_effect  # CH4 stronger than CO2

    def test_pressure_scaling(self):
        """Higher pressure increases greenhouse effect (pressure^0.2)."""
        composition = {"CO2": 0}  # No GHG, just base effect

        effect_1atm = _calculate_greenhouse_effect({}, ATM_TO_PA, 1.0)
        effect_10atm = _calculate_greenhouse_effect({}, ATM_TO_PA * 10, 10.0)

        # 10^0.2 = ~1.58
        expected_ratio = 10 ** 0.2
        if effect_1atm > 0:
            actual_ratio = effect_10atm / effect_1atm
            assert abs(actual_ratio - expected_ratio) < 0.2

    def test_combined_greenhouse_gases(self):
        """Multiple greenhouse gases combine additively."""
        pressure_pa = ATM_TO_PA
        pressure_atm = 1.0
        partial = pressure_pa * 0.01

        co2_only = _calculate_greenhouse_effect(
            {"CO2": partial}, pressure_pa, pressure_atm
        )
        h2o_only = _calculate_greenhouse_effect(
            {"H2O": partial}, pressure_pa, pressure_atm
        )
        combined = _calculate_greenhouse_effect(
            {"CO2": partial, "H2O": partial}, pressure_pa, pressure_atm
        )

        # Combined should be greater than either alone
        assert combined > co2_only
        assert combined > h2o_only


# =============================================================================
# Test: Full Atmosphere Generation
# =============================================================================


class TestGenerateAtmosphere:
    """Tests for the main generate_atmosphere function."""

    def test_returns_tuple_of_three(self, earth_like_params):
        """Returns (composition, pressure, temperature) tuple."""
        result = generate_atmosphere(**earth_like_params)

        assert isinstance(result, tuple)
        assert len(result) == 3
        composition, pressure, temperature = result
        assert isinstance(composition, dict)
        assert isinstance(pressure, (int, float))
        assert isinstance(temperature, (int, float))

    def test_earth_like_has_atmosphere(self, earth_like_params):
        """Earth-like planet has non-zero atmosphere."""
        composition, pressure, temperature = generate_atmosphere(**earth_like_params)

        assert pressure > 0
        assert temperature > 0
        assert len(composition) > 0

    def test_gas_giant_high_pressure(self, gas_giant_params):
        """Gas giant has very high atmospheric pressure."""
        composition, pressure, temperature = generate_atmosphere(**gas_giant_params)

        # Should be much higher than Earth
        assert pressure > ATM_TO_PA * 100

    def test_small_body_minimal_atmosphere(self, small_body_params):
        """Small body has minimal or no atmosphere."""
        # Run multiple times due to randomness
        total_pressure = 0
        for _ in range(10):
            composition, pressure, _ = generate_atmosphere(**small_body_params)
            total_pressure += pressure

        avg_pressure = total_pressure / 10
        # Should be much less than Earth
        assert avg_pressure < ATM_TO_PA

    def test_final_temperature_includes_greenhouse(self, earth_like_params):
        """Final temperature is base_temp + greenhouse effect."""
        composition, pressure, temperature = generate_atmosphere(**earth_like_params)

        # Temperature should be >= base_temp (greenhouse adds heat)
        assert temperature >= earth_like_params["base_temp"]

    def test_hot_small_body_stripped_atmosphere(self, hot_small_body_params):
        """Hot small body has atmosphere stripped."""
        # Run multiple times to average out randomness
        pressures = []
        for _ in range(10):
            _, pressure, _ = generate_atmosphere(**hot_small_body_params)
            pressures.append(pressure)

        avg_pressure = sum(pressures) / len(pressures)
        # Should be relatively low due to stripping
        assert avg_pressure < ATM_TO_PA * 0.5

    def test_no_gases_retained_returns_empty(self):
        """If no gases retained, returns empty composition."""
        # Very low escape velocity
        params = {
            "mass": 1e20,  # Tiny asteroid
            "escape_vel": 50.0,  # Very low
            "base_temp": 500.0,  # Hot
            "flux_wm2": 5000.0,
        }

        composition, pressure, temperature = generate_atmosphere(**params)

        assert composition == {}
        assert pressure == 0.0
        assert temperature == params["base_temp"]

    def test_deterministic_with_seed(self, earth_like_params):
        """Same random seed produces same results."""
        import random

        random.seed(42)
        result1 = generate_atmosphere(**earth_like_params)

        random.seed(42)
        result2 = generate_atmosphere(**earth_like_params)

        assert result1 == result2

    def test_zero_base_temp_handled(self):
        """Zero base temperature is handled gracefully."""
        params = {
            "mass": MASS_EARTH,
            "escape_vel": 11000.0,
            "base_temp": 0.0,  # Zero
            "flux_wm2": 0.0,
        }

        composition, pressure, temperature = generate_atmosphere(**params)

        # Should not crash
        assert isinstance(temperature, (int, float))
        # Retention temp calculation uses 50K as fallback for zero

    def test_negative_values_handled(self):
        """Negative input values handled gracefully."""
        params = {
            "mass": -1e24,  # Invalid but shouldn't crash
            "escape_vel": -5000.0,
            "base_temp": -100.0,
            "flux_wm2": -1000.0,
        }

        # Should not raise exception
        result = generate_atmosphere(**params)
        assert isinstance(result, tuple)

    def test_gas_composition_uses_correct_gases(self, earth_like_params):
        """Composition only contains gases from GASES constant."""
        composition, _, _ = generate_atmosphere(**earth_like_params)

        for gas in composition:
            assert gas in GASES, f"Unknown gas {gas} in composition"

    def test_partial_pressures_match_total(self, earth_like_params):
        """Sum of partial pressures equals total pressure."""
        composition, total_pressure, _ = generate_atmosphere(**earth_like_params)

        if composition:
            partial_sum = sum(composition.values())
            assert abs(partial_sum - total_pressure) < 1.0  # Small tolerance

    def test_greenhouse_warming(self):
        """Greenhouse gases increase temperature above base."""
        # Force high CO2 atmosphere
        params = {
            "mass": MASS_EARTH * 2,  # Bigger to retain more
            "escape_vel": 15000.0,
            "base_temp": 200.0,
            "flux_wm2": 1000.0,
        }

        # Run multiple times to find one with CO2
        temps = []
        for _ in range(20):
            composition, pressure, temperature = generate_atmosphere(**params)
            if "CO2" in composition and pressure > ATM_TO_PA * 0.1:
                temps.append((params["base_temp"], temperature))

        if temps:
            # At least one should show warming
            warming_found = any(final > base for base, final in temps)
            assert warming_found or len(temps) == 0  # Skip if no valid runs

    def test_retention_temp_calculation(self, earth_like_params):
        """Retention temp is 1.5x base temp or 50K for zero."""
        # This is implicitly tested via gas retention
        # Low base temp should use 50K minimum
        params = earth_like_params.copy()
        params["base_temp"] = 20.0  # Very low

        # Should still calculate retention at reasonable temp
        composition, _, _ = generate_atmosphere(**params)
        # Function should complete without error


# =============================================================================
# Test: Edge Cases and Boundary Conditions
# =============================================================================


class TestAtmosphereEdgeCases:
    """Edge case tests for atmosphere generation."""

    def test_very_large_mass(self):
        """Very large mass (super-jupiter) handled."""
        params = {
            "mass": MASS_JUPITER * 10,
            "escape_vel": 100000.0,
            "base_temp": 50.0,
            "flux_wm2": 10.0,
        }

        composition, pressure, temperature = generate_atmosphere(**params)

        assert pressure > 0
        assert "H2" in composition  # Should retain hydrogen

    def test_very_small_mass(self):
        """Very small mass (asteroid) handled."""
        params = {
            "mass": 1e18,  # Small asteroid
            "escape_vel": 10.0,
            "base_temp": 200.0,
            "flux_wm2": 500.0,
        }

        composition, pressure, temperature = generate_atmosphere(**params)

        # Should have minimal/no atmosphere
        assert pressure <= ATM_TO_PA

    def test_extreme_temperature(self):
        """Extreme temperatures (hot/cold) handled."""
        # Very hot
        hot_params = {
            "mass": MASS_EARTH,
            "escape_vel": 11000.0,
            "base_temp": 2000.0,  # Very hot
            "flux_wm2": 50000.0,
        }

        composition_hot, pressure_hot, temp_hot = generate_atmosphere(**hot_params)
        assert isinstance(temp_hot, (int, float))

        # Very cold
        cold_params = {
            "mass": MASS_EARTH,
            "escape_vel": 11000.0,
            "base_temp": 10.0,  # Very cold
            "flux_wm2": 1.0,
        }

        composition_cold, pressure_cold, temp_cold = generate_atmosphere(**cold_params)
        assert isinstance(temp_cold, (int, float))

    def test_extremely_high_escape_velocity(self):
        """Very high escape velocity retains all gases."""
        params = {
            "mass": MASS_JUPITER * 100,
            "escape_vel": 500000.0,  # Super high
            "base_temp": 100.0,
            "flux_wm2": 10.0,
        }

        composition, pressure, temperature = generate_atmosphere(**params)

        # Should retain all light gases
        assert "H2" in composition
        assert "He" in composition

    def test_float_precision(self):
        """Very small float values handled without precision issues."""
        params = {
            "mass": 1e-10,  # Tiny
            "escape_vel": 1e-5,
            "base_temp": 1e-3,
            "flux_wm2": 1e-8,
        }

        # Should not raise exceptions
        result = generate_atmosphere(**params)
        assert isinstance(result, tuple)

    def test_inf_values_handled(self):
        """Infinite values don't crash the system."""
        params = {
            "mass": float('inf'),
            "escape_vel": float('inf'),
            "base_temp": 300.0,
            "flux_wm2": 1000.0,
        }

        # May produce inf results but shouldn't crash
        try:
            result = generate_atmosphere(**params)
            assert isinstance(result, tuple)
        except (ValueError, OverflowError):
            # These exceptions are acceptable for invalid input
            pass
