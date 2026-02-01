"""
Unit tests for planet physics validation.
"""
import pytest
from game.strategy.data.planet_physics import (
    validate_planet_parameters,
    calculate_escape_velocity,
    calculate_surface_gravity,
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

    def test_speed_of_light_constant(self):
        """Verify speed of light constant is available."""
        from game.strategy.data.planet_physics import SPEED_OF_LIGHT
        assert SPEED_OF_LIGHT == pytest.approx(2.998e8, rel=0.01)
