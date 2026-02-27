"""Tests for WarpPoint.from_dict() input validation.

PROJ-171: Deserialization Input Validation - Phase 2
"""
import pytest
from game.core.exceptions import PersistenceException
from game.core.hex_math import HexCoord
from game.strategy.data.galaxy import WarpPoint


class TestWarpPointFromDictValidation:
    """Test validation in WarpPoint.from_dict()."""

    def test_valid_data_creates_warp_point(self):
        """Valid data should create WarpPoint successfully."""
        data = {
            'destination_id': 'system_alpha',
            'location': {'q': 5, 'r': -3}
        }
        wp = WarpPoint.from_dict(data)

        assert wp.destination_id == 'system_alpha'
        assert wp.location == HexCoord(5, -3)

    def test_missing_destination_id_raises_persistence_exception(self):
        """Missing 'destination_id' should raise PersistenceException."""
        data = {
            'location': {'q': 5, 'r': -3}
        }

        with pytest.raises(PersistenceException) as exc_info:
            WarpPoint.from_dict(data)

        assert 'WarpPoint' in str(exc_info.value)
        assert 'destination_id' in str(exc_info.value)

    def test_missing_location_raises_persistence_exception(self):
        """Missing 'location' should raise PersistenceException."""
        data = {
            'destination_id': 'system_alpha'
        }

        with pytest.raises(PersistenceException) as exc_info:
            WarpPoint.from_dict(data)

        assert 'WarpPoint' in str(exc_info.value)
        assert 'location' in str(exc_info.value)

    def test_malformed_location_raises_persistence_exception(self):
        """Malformed location (missing 'r') should raise PersistenceException."""
        data = {
            'destination_id': 'system_alpha',
            'location': {'q': 5}  # Missing 'r'
        }

        with pytest.raises(PersistenceException) as exc_info:
            WarpPoint.from_dict(data)

        assert 'WarpPoint' in str(exc_info.value)

    def test_null_location_raises_persistence_exception(self):
        """Null location dict should raise PersistenceException."""
        data = {
            'destination_id': 'system_alpha',
            'location': None
        }

        with pytest.raises(PersistenceException) as exc_info:
            WarpPoint.from_dict(data)

        assert 'WarpPoint' in str(exc_info.value)
