import pytest
from game.strategy.data.physics import calculate_incident_radiation, FLUX_SCALE, FALLOFF_EXPONENT
from game.strategy.data.stars import Star, Spectrum, StarType
from game.core.hex_math import HexCoord


@pytest.fixture
def flat_star():
    """Create a star with uniform spectrum for easy math."""
    flat_spec = Spectrum(100, 100, 100, 100, 100, 100, 100, 100, 100)
    return Star(
        name="Test Star",
        mass=1.0,
        radius_hexes=1,
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
        # At distance 1 (adjacent), falloff = FLUX_SCALE / 1^exp = FLUX_SCALE
        target = HexCoord(1, 0)  # 1 hex away
        result = calculate_incident_radiation(target, [flat_star])

        expected = 100.0 * FLUX_SCALE
        assert result.gamma_ray == pytest.approx(expected)
        assert result.red == pytest.approx(expected)

    def test_falloff_distance_2(self, flat_star):
        # At distance 2, falloff = FLUX_SCALE / 2^exp
        target = HexCoord(2, 0)  # 2 hexes away
        result = calculate_incident_radiation(target, [flat_star])

        expected = 100.0 * FLUX_SCALE / (2.0 ** FALLOFF_EXPONENT)
        assert result.gamma_ray == pytest.approx(expected)

    def test_falloff_distance_10(self, flat_star):
        # At distance 10, falloff = FLUX_SCALE / 10^exp
        target = HexCoord(10, 0)
        result = calculate_incident_radiation(target, [flat_star])

        expected = 100.0 * FLUX_SCALE / (10.0 ** FALLOFF_EXPONENT)
        assert result.gamma_ray == pytest.approx(expected)

    def test_clamping(self, flat_star):
        # At distance 0 (inside star), should clamp to 1.0, full FLUX_SCALE
        target = HexCoord(0, 0)
        result = calculate_incident_radiation(target, [flat_star])

        expected = 100.0 * FLUX_SCALE
        assert result.gamma_ray == pytest.approx(expected)

    def test_additive_measure(self, flat_star):
        # Two stars at same location (0,0)
        target = HexCoord(1, 0)
        result = calculate_incident_radiation(target, [flat_star, flat_star])

        # Should be double
        expected = 200.0 * FLUX_SCALE
        assert result.gamma_ray == pytest.approx(expected)
