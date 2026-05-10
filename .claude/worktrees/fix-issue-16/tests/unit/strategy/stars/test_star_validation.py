"""Tests for Star.from_dict validation (PROJ-171 Phase 3)."""
import pytest
from game.core.exceptions import PersistenceException
from game.strategy.data.stars import Star, StarType


def _valid_spectrum_data() -> dict:
    """Return valid spectrum data."""
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


def _valid_star_data() -> dict:
    """Return valid star data for testing."""
    return {
        'name': 'Test Star',
        'mass': 1.0,
        'radius_hexes': 2,
        'temperature': 5778,
        'luminosity': 1.0,
        'spectrum': _valid_spectrum_data(),
        'star_type': 'MAIN_SEQUENCE',
        'color': [255, 220, 180],
        'age': 4.6e9,
        'location': {'q': 0, 'r': 0}
    }


class TestStarFromDictValidation:
    """Tests for Star.from_dict input validation."""

    def test_valid_data_creates_star(self):
        """Valid star data should create Star instance."""
        data = _valid_star_data()
        star = Star.from_dict(data)

        assert star.name == 'Test Star'
        assert star.mass == 1.0
        assert star.star_type == StarType.MAIN_SEQUENCE

    @pytest.mark.parametrize('missing_key', [
        'name', 'mass', 'radius_hexes', 'temperature', 'luminosity',
        'spectrum', 'star_type', 'color', 'age', 'location'
    ])
    def test_missing_key_raises_persistence_exception(self, missing_key):
        """Missing required key should raise PersistenceException."""
        data = _valid_star_data()
        del data[missing_key]

        with pytest.raises(PersistenceException) as exc_info:
            Star.from_dict(data)

        assert 'Star' in str(exc_info.value)
        assert missing_key in str(exc_info.value)

    def test_invalid_star_type_raises_persistence_exception(self):
        """Invalid star_type enum should raise PersistenceException with valid values."""
        data = _valid_star_data()
        data['star_type'] = 'INVALID_TYPE'

        with pytest.raises(PersistenceException) as exc_info:
            Star.from_dict(data)

        error_msg = str(exc_info.value)
        assert 'Star' in error_msg
        assert 'star_type' in error_msg
        # Should list valid values
        assert 'MAIN_SEQUENCE' in error_msg

    @pytest.mark.parametrize('field', ['mass', 'temperature', 'luminosity'])
    def test_negative_positive_field_raises_persistence_exception(self, field):
        """Fields requiring positive values should raise on negative."""
        data = _valid_star_data()
        data[field] = -1.0

        with pytest.raises(PersistenceException) as exc_info:
            Star.from_dict(data)

        assert 'Star' in str(exc_info.value)
        assert field in str(exc_info.value)

    @pytest.mark.parametrize('field', ['mass', 'luminosity'])
    def test_zero_positive_field_raises_persistence_exception(self, field):
        """Fields requiring strictly positive values should raise on zero."""
        data = _valid_star_data()
        data[field] = 0.0

        with pytest.raises(PersistenceException) as exc_info:
            Star.from_dict(data)

        assert 'Star' in str(exc_info.value)
        assert field in str(exc_info.value)

    def test_zero_temperature_accepted_for_black_holes(self):
        """temperature=0 is valid (BLACK_HOLE event horizons have no temperature)."""
        data = _valid_star_data()
        data['temperature'] = 0.0
        star = Star.from_dict(data)
        assert star.temperature == 0.0

    def test_negative_temperature_raises(self):
        """Negative temperature is always invalid."""
        data = _valid_star_data()
        data['temperature'] = -100.0

        with pytest.raises(PersistenceException) as exc_info:
            Star.from_dict(data)

        assert 'temperature' in str(exc_info.value)

    def test_corrupt_spectrum_raises_persistence_exception(self):
        """Corrupt spectrum data should raise PersistenceException with context."""
        data = _valid_star_data()
        data['spectrum'] = {'blue': 0.5}  # Missing other fields

        with pytest.raises(PersistenceException) as exc_info:
            Star.from_dict(data)

        # Should mention Spectrum context
        assert 'Spectrum' in str(exc_info.value)

    def test_corrupt_location_raises_persistence_exception(self):
        """Corrupt location data should raise PersistenceException."""
        data = _valid_star_data()
        data['location'] = {'x': 0}  # Invalid format, needs 'q' and 'r'

        with pytest.raises(PersistenceException) as exc_info:
            Star.from_dict(data)

        assert 'Star' in str(exc_info.value)
        assert 'location' in str(exc_info.value).lower()
