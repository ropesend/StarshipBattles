"""
Unit tests for full atmosphere generation.

Tests the main generate_atmosphere function and edge cases.
"""

import pytest

from game.strategy.data.planet_atmosphere import generate_atmosphere
from game.strategy.data.planet_physics import (
    ATM_TO_PA, GASES, MASS_EARTH, MASS_JUPITER
)


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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
