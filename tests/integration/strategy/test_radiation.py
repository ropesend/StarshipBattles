import pytest
from game.strategy.data.physics import calculate_incident_radiation
from game.strategy.data.stars import Star, Spectrum, StarType
from game.strategy.data.hex_math import HexCoord


@pytest.fixture
def flat_star():
    """Create a star with uniform spectrum for easy math."""
    flat_spec = Spectrum(100, 100, 100, 100, 100, 100, 100, 100, 100)
    return Star(
        name="Test Star",
        mass=1.0,
        diameter_hexes=1.0,
        temperature=5000,
        luminosity=1.0,
        spectrum=flat_spec,
        star_type=StarType.MAIN_SEQUENCE,
        color=(255, 255, 255),
        age=1.0,
        location=HexCoord(0, 0)
    )


class TestRadiation:

    def test_falloff_distance_1(self, flat_star):
        # At distance 1 (adjacent), factor should be 1/1^3 = 1.0
        target = HexCoord(1, 0)  # 1 hex away
        result = calculate_incident_radiation(target, [flat_star])

        assert result.gamma_ray == pytest.approx(100.0)
        assert result.red == pytest.approx(100.0)

    def test_falloff_distance_2(self, flat_star):
        # At distance 2, factor should be 1/2^2.1 = 1/4.287 = 0.23325
        target = HexCoord(2, 0)  # 2 hexes away
        result = calculate_incident_radiation(target, [flat_star])

        # 100 * (1 / 2**2.1) = 23.325824788
        assert result.gamma_ray == pytest.approx(23.3258248)

    def test_falloff_distance_10(self, flat_star):
        # At distance 10, factor should be 1/10^2.1 = 1/125.89 = 0.007943
        target = HexCoord(10, 0)
        result = calculate_incident_radiation(target, [flat_star])

        # 100 * (1 / 10**2.1) = 0.79432823
        assert result.gamma_ray == pytest.approx(0.7943282)

    def test_clamping(self, flat_star):
        # At distance 0 (inside star), should clamp to 1.0
        target = HexCoord(0, 0)
        result = calculate_incident_radiation(target, [flat_star])

        assert result.gamma_ray == pytest.approx(100.0)

    def test_additive_measure(self, flat_star):
        # Two stars at same location (0,0)
        target = HexCoord(1, 0)
        result = calculate_incident_radiation(target, [flat_star, flat_star])

        # Should be double (200.0)
        assert result.gamma_ray == pytest.approx(200.0)
