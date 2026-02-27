"""Tests for Spectrum.from_dict validation (PROJ-171 Phase 3)."""
import pytest
from game.core.exceptions import PersistenceException
from game.strategy.data.stars import Spectrum


def _valid_spectrum_data() -> dict:
    """Return valid spectrum data for testing."""
    return {
        'gamma_ray': 0.001,
        'xray': 0.01,
        'ultraviolet': 0.1,
        'blue': 0.3,
        'green': 0.35,
        'red': 0.25,
        'infrared': 0.1,
        'microwave': 0.01,
        'radio': 0.001
    }


class TestSpectrumFromDictValidation:
    """Tests for Spectrum.from_dict input validation."""

    def test_valid_data_creates_spectrum(self):
        """Valid spectrum data should create Spectrum instance."""
        data = _valid_spectrum_data()
        spectrum = Spectrum.from_dict(data)

        assert spectrum.gamma_ray == 0.001
        assert spectrum.blue == 0.3
        assert spectrum.radio == 0.001

    def test_zero_values_valid(self):
        """Zero is valid for spectrum bands."""
        data = _valid_spectrum_data()
        data['gamma_ray'] = 0.0
        data['xray'] = 0.0

        spectrum = Spectrum.from_dict(data)

        assert spectrum.gamma_ray == 0.0
        assert spectrum.xray == 0.0

    @pytest.mark.parametrize('missing_key', [
        'gamma_ray', 'xray', 'ultraviolet', 'blue', 'green',
        'red', 'infrared', 'microwave', 'radio'
    ])
    def test_missing_key_raises_persistence_exception(self, missing_key):
        """Missing any required spectrum band should raise PersistenceException."""
        data = _valid_spectrum_data()
        del data[missing_key]

        with pytest.raises(PersistenceException) as exc_info:
            Spectrum.from_dict(data)

        assert 'Spectrum' in str(exc_info.value)
        assert missing_key in str(exc_info.value)

    @pytest.mark.parametrize('field', [
        'gamma_ray', 'xray', 'ultraviolet', 'blue', 'green',
        'red', 'infrared', 'microwave', 'radio'
    ])
    def test_negative_value_raises_persistence_exception(self, field):
        """Negative spectrum values should raise PersistenceException."""
        data = _valid_spectrum_data()
        data[field] = -0.5

        with pytest.raises(PersistenceException) as exc_info:
            Spectrum.from_dict(data)

        assert 'Spectrum' in str(exc_info.value)
        assert field in str(exc_info.value)
        assert 'non-negative' in str(exc_info.value).lower()
