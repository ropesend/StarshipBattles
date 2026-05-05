"""
Unit tests for planet physics validation.
"""
import math

import pytest
from game.strategy.data.planet_physics import (
    validate_planet_parameters,
    calculate_radius_density_from_mass,
    calculate_escape_velocity,
    calculate_surface_gravity,
    calculate_surface_area,
    calculate_blackbody_temperature,
    MASS_EARTH, MASS_JUPITER, MASS_CERES
)


class TestValidatePlanetParameters:
    """Tests for the validate_planet_parameters function."""

    def test_valid_earth_like_planet(self):
        """Earth-like parameters should have no warnings."""
        # Earth: mass=5.97e24 kg, radius=6.37e6 m, density=5515 kg/m^3
        warnings = validate_planet_parameters(
            mass=5.97e24,
            radius=6.37e6,
            density=5515
        )
        assert len(warnings) == 0

    def test_valid_jupiter_like_planet(self):
        """Jupiter-like parameters should have no warnings."""
        # Jupiter: mass=1.89e27 kg, radius=6.99e7 m, density=1326 kg/m^3
        warnings = validate_planet_parameters(
            mass=1.89e27,
            radius=6.99e7,
            density=1326
        )
        assert len(warnings) == 0

    def test_radius_too_small_for_mass(self):
        """Should warn if radius is too small for the mass."""
        # Earth mass but Moon-sized radius (1.7e6 m) - impossibly dense
        warnings = validate_planet_parameters(
            mass=5.97e24,
            radius=1.0e6,  # Too small
            density=100000  # Would need extreme density
        )
        assert len(warnings) > 0
        assert any("radius" in w.lower() for w in warnings)

    def test_radius_too_large_for_mass(self):
        """Should warn if radius is too large for the mass (balloon planet)."""
        # Small mass but giant radius - unrealistic
        warnings = validate_planet_parameters(
            mass=1e22,
            radius=1e8,  # Way too large
            density=0.1  # Impossibly light
        )
        assert len(warnings) > 0

    def test_escape_velocity_check(self):
        """Should warn if escape velocity approaches light speed."""
        # Compact object with extreme parameters
        warnings = validate_planet_parameters(
            mass=1e35,  # Way too massive for a planet
            radius=1e4,  # Extremely small
            density=1e20
        )
        assert len(warnings) > 0
        assert any("escape" in w.lower() or "velocity" in w.lower() for w in warnings)

    def test_surface_gravity_extreme(self):
        """Should warn if surface gravity is unreasonably high."""
        # Very massive but small - extreme gravity
        warnings = validate_planet_parameters(
            mass=1e28,  # Super-Jupiter
            radius=1e6,  # Earth-sized
            density=100000
        )
        assert len(warnings) > 0
        assert any("gravity" in w.lower() for w in warnings)

    def test_density_validation(self):
        """Should warn if density is unrealistic."""
        # Check for unrealistic low density
        warnings = validate_planet_parameters(
            mass=1e24,
            radius=1e8,
            density=10  # Lighter than air
        )
        assert len(warnings) > 0

    def test_returns_list_of_strings(self):
        """Validate return type is list of strings."""
        warnings = validate_planet_parameters(
            mass=5.97e24,
            radius=6.37e6,
            density=5515
        )
        assert isinstance(warnings, list)
        for w in warnings:
            assert isinstance(w, str)


class TestPhysicsConstants:
    """Tests for physics constants and calculations."""

    @pytest.mark.parametrize(
        ("mass", "expected_bounds", "selected_density"),
        [
            (1.1e26, (900, 1600), 1200),
            (5.1e24, (4000, 6000), 5000),
            (1.0e24, (2000, 4500), 3000),
        ],
    )
    def test_radius_density_uses_mass_range_density_model(
        self,
        monkeypatch,
        mass,
        expected_bounds,
        selected_density,
    ):
        """Mass ranges should choose the matching density model."""
        calls = []

        def fake_uniform(low, high):
            calls.append((low, high))
            return selected_density

        monkeypatch.setattr("game.strategy.data.planet_physics.random.uniform", fake_uniform)

        radius, density = calculate_radius_density_from_mass(mass)

        assert calls == [expected_bounds]
        assert density == selected_density
        expected_volume = mass / selected_density
        expected_radius = ((3 * expected_volume) / (4 * math.pi)) ** (1.0 / 3.0)
        assert radius == pytest.approx(expected_radius)

    def test_escape_velocity_earth(self):
        """Test escape velocity calculation for Earth."""
        # Earth: mass=5.97e24 kg, radius=6.37e6 m
        # Expected ~11186 m/s
        v_esc = calculate_escape_velocity(5.97e24, 6.37e6)
        assert 11000 < v_esc < 11500

    def test_surface_gravity_earth(self):
        """Test surface gravity calculation for Earth."""
        # Earth: g ~ 9.8 m/s^2
        g = calculate_surface_gravity(5.97e24, 6.37e6)
        assert 9.5 < g < 10.0

    def test_surface_area_for_spherical_body(self):
        area = calculate_surface_area(2.0)

        assert area == pytest.approx(16.0 * math.pi)

    def test_blackbody_temperature_returns_zero_for_non_positive_flux(self):
        assert calculate_blackbody_temperature(0) == 0.0
        assert calculate_blackbody_temperature(-1) == 0.0

    def test_blackbody_temperature_for_positive_flux(self):
        temperature = calculate_blackbody_temperature(1361)

        assert temperature == pytest.approx(393.58, rel=0.01)

    def test_speed_of_light_constant(self):
        """Verify speed of light constant is available."""
        from game.strategy.data.planet_physics import SPEED_OF_LIGHT
        assert SPEED_OF_LIGHT == pytest.approx(2.998e8, rel=0.01)

    def test_validate_warns_for_radius_above_planet_bounds(self):
        warnings = validate_planet_parameters(
            mass=1e24,
            radius=3e8,
            density=5000,
        )

        assert any("exceeds maximum planet size" in warning for warning in warnings)

    def test_validate_warns_for_density_above_physical_bounds(self):
        warnings = validate_planet_parameters(
            mass=1e24,
            radius=6e6,
            density=40000,
        )

        assert any("exceeds maximum" in warning for warning in warnings)

    def test_validate_warns_for_mass_radius_density_inconsistency(self):
        warnings = validate_planet_parameters(
            mass=1e24,
            radius=6e6,
            density=5000,
        )

        assert any("inconsistent with mass/radius" in warning for warning in warnings)

    def test_validate_zero_radius_skips_derived_checks(self):
        warnings = validate_planet_parameters(
            mass=1e24,
            radius=0,
            density=5000,
        )

        assert any("below minimum planet size" in warning for warning in warnings)
        assert not any("Escape velocity" in warning for warning in warnings)
        assert not any("Surface gravity" in warning for warning in warnings)
        assert not any("inconsistent with mass/radius" in warning for warning in warnings)
