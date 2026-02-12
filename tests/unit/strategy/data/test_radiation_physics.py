"""
Unit tests for game.strategy.data.physics module.

TCG-STR-001: Radiation physics calculations.
"""

import pytest
import math
from unittest.mock import Mock

from game.core.hex_math import HexCoord
from game.strategy.data.physics import SectorEnvironment, calculate_incident_radiation
from game.strategy.data.stars import Spectrum


class TestSectorEnvironment:
    """Tests for SectorEnvironment class."""

    def test_sector_environment_init(self):
        """SectorEnvironment stores local_hex and system."""
        local_hex = HexCoord(5, 3)
        mock_system = Mock()

        env = SectorEnvironment(local_hex, mock_system)

        assert env.local_hex == local_hex
        assert env.system is mock_system

    def test_sector_environment_calculate_radiation_delegates(self):
        """calculate_radiation delegates to calculate_incident_radiation."""
        local_hex = HexCoord(2, 1)
        mock_star = Mock()
        mock_star.location = HexCoord(0, 0)
        mock_star.spectrum = Spectrum(1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0)

        mock_system = Mock()
        mock_system.stars = [mock_star]

        env = SectorEnvironment(local_hex, mock_system)
        result = env.calculate_radiation()

        # Should return a Spectrum object
        assert isinstance(result, Spectrum)
        # Verify non-zero result (star contributes radiation)
        assert result.get_total_output() > 0


class TestCalculateIncidentRadiation:
    """Tests for calculate_incident_radiation function."""

    def _make_star(self, location: HexCoord, spectrum: Spectrum):
        """Create a mock star with location and spectrum."""
        star = Mock()
        star.location = location
        star.spectrum = spectrum
        return star

    def test_single_star_at_same_hex(self):
        """Star at same hex as target: distance clamped to 1.0, full intensity."""
        star = self._make_star(
            HexCoord(0, 0),
            Spectrum(10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0)
        )

        result = calculate_incident_radiation(HexCoord(0, 0), [star])

        # Distance is 0, clamped to 1.0, so falloff = 1/1^2.1 = 1.0
        # All bands should be at full intensity
        assert result.gamma_ray == pytest.approx(10.0)
        assert result.xray == pytest.approx(10.0)
        assert result.ultraviolet == pytest.approx(10.0)
        assert result.blue == pytest.approx(10.0)
        assert result.green == pytest.approx(10.0)
        assert result.red == pytest.approx(10.0)
        assert result.infrared == pytest.approx(10.0)
        assert result.microwave == pytest.approx(10.0)
        assert result.radio == pytest.approx(10.0)

    def test_single_star_distance_2(self):
        """Star at distance 2: falloff = 1/2^2.1."""
        # Create star at origin, target at (2, 0) which is distance 2
        star = self._make_star(
            HexCoord(0, 0),
            Spectrum(10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0)
        )

        result = calculate_incident_radiation(HexCoord(2, 0), [star])

        # falloff = 1 / 2^2.1 = 1 / 4.287... ≈ 0.2332
        expected_falloff = 1.0 / (2.0 ** 2.1)
        expected_value = 10.0 * expected_falloff

        assert result.gamma_ray == pytest.approx(expected_value, rel=1e-4)
        assert result.blue == pytest.approx(expected_value, rel=1e-4)
        assert result.infrared == pytest.approx(expected_value, rel=1e-4)

    def test_single_star_distance_5(self):
        """Star at distance 5: falloff = 1/5^2.1."""
        # Star at origin, target at (5, 0) which is distance 5
        star = self._make_star(
            HexCoord(0, 0),
            Spectrum(100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0)
        )

        result = calculate_incident_radiation(HexCoord(5, 0), [star])

        # falloff = 1 / 5^2.1 ≈ 0.0347
        expected_falloff = 1.0 / (5.0 ** 2.1)
        expected_value = 100.0 * expected_falloff

        assert result.gamma_ray == pytest.approx(expected_value, rel=1e-4)
        assert result.get_total_output() == pytest.approx(9 * expected_value, rel=1e-4)

    def test_two_stars_sum_contributions(self):
        """Total radiation is sum of contributions from multiple stars."""
        star1 = self._make_star(
            HexCoord(0, 0),
            Spectrum(10.0, 0, 0, 0, 0, 0, 0, 0, 0)  # Only gamma_ray
        )
        star2 = self._make_star(
            HexCoord(3, 0),  # Distance 3 from target at (0, 0)
            Spectrum(0, 0, 0, 0, 0, 0, 10.0, 0, 0)  # Only infrared
        )

        target = HexCoord(0, 0)
        result = calculate_incident_radiation(target, [star1, star2])

        # star1 at distance 0 (clamped to 1): falloff = 1.0, gamma_ray = 10.0
        # star2 at distance 3: falloff = 1/3^2.1 ≈ 0.0962, infrared = 10.0 * 0.0962
        falloff_star2 = 1.0 / (3.0 ** 2.1)

        assert result.gamma_ray == pytest.approx(10.0)
        assert result.infrared == pytest.approx(10.0 * falloff_star2, rel=1e-4)

    def test_zero_distance_clamped(self):
        """Star at target hex (zero distance) clamped to r=1.0."""
        star = self._make_star(
            HexCoord(3, 4),
            Spectrum(5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0)
        )

        # Target at same location as star
        result = calculate_incident_radiation(HexCoord(3, 4), [star])

        # Distance = 0, clamped to 1.0, full intensity
        assert result.gamma_ray == pytest.approx(5.0)
        assert result.blue == pytest.approx(5.0)
        assert result.radio == pytest.approx(5.0)

    def test_all_spectrum_bands_scaled(self):
        """All 9 spectrum bands get the falloff applied correctly."""
        star = self._make_star(
            HexCoord(0, 0),
            Spectrum(
                gamma_ray=1.0,
                xray=2.0,
                ultraviolet=3.0,
                blue=4.0,
                green=5.0,
                red=6.0,
                infrared=7.0,
                microwave=8.0,
                radio=9.0
            )
        )

        # Distance 2
        result = calculate_incident_radiation(HexCoord(2, 0), [star])

        falloff = 1.0 / (2.0 ** 2.1)

        assert result.gamma_ray == pytest.approx(1.0 * falloff, rel=1e-4)
        assert result.xray == pytest.approx(2.0 * falloff, rel=1e-4)
        assert result.ultraviolet == pytest.approx(3.0 * falloff, rel=1e-4)
        assert result.blue == pytest.approx(4.0 * falloff, rel=1e-4)
        assert result.green == pytest.approx(5.0 * falloff, rel=1e-4)
        assert result.red == pytest.approx(6.0 * falloff, rel=1e-4)
        assert result.infrared == pytest.approx(7.0 * falloff, rel=1e-4)
        assert result.microwave == pytest.approx(8.0 * falloff, rel=1e-4)
        assert result.radio == pytest.approx(9.0 * falloff, rel=1e-4)

    def test_empty_stars_list(self):
        """Empty stars list returns zero spectrum (all bands 0)."""
        result = calculate_incident_radiation(HexCoord(5, 5), [])

        assert result.gamma_ray == 0.0
        assert result.xray == 0.0
        assert result.ultraviolet == 0.0
        assert result.blue == 0.0
        assert result.green == 0.0
        assert result.red == 0.0
        assert result.infrared == 0.0
        assert result.microwave == 0.0
        assert result.radio == 0.0
        assert result.get_total_output() == 0.0
