"""Tests for Galaxy.from_dict() input validation.

PROJ-171: Deserialization Input Validation - Phase 2
"""
import pytest
from game.core.exceptions import PersistenceException
from game.core.hex_math import HexCoord
from game.strategy.data.galaxy import Galaxy


class TestGalaxyFromDictValidation:
    """Test validation in Galaxy.from_dict()."""

    def test_valid_data_creates_galaxy(self):
        """Valid data should create Galaxy successfully."""
        data = {
            'radius': 100,
            'systems': [],
            '_next_planet_id': 1
        }
        galaxy = Galaxy.from_dict(data)

        assert galaxy.radius == 100
        assert len(galaxy.systems) == 0

    def test_missing_radius_raises_persistence_exception(self):
        """Missing 'radius' should raise PersistenceException."""
        data = {
            'systems': []
        }

        with pytest.raises(PersistenceException) as exc_info:
            Galaxy.from_dict(data)

        assert 'Galaxy' in str(exc_info.value)
        assert 'radius' in str(exc_info.value)

    def test_radius_zero_raises_persistence_exception(self):
        """Radius of 0 should raise PersistenceException (must be positive)."""
        data = {
            'radius': 0,
            'systems': []
        }

        with pytest.raises(PersistenceException) as exc_info:
            Galaxy.from_dict(data)

        assert 'Galaxy' in str(exc_info.value)
        assert 'radius' in str(exc_info.value)
        assert 'positive' in str(exc_info.value)

    def test_radius_negative_raises_persistence_exception(self):
        """Negative radius should raise PersistenceException."""
        data = {
            'radius': -10,
            'systems': []
        }

        with pytest.raises(PersistenceException) as exc_info:
            Galaxy.from_dict(data)

        assert 'Galaxy' in str(exc_info.value)
        assert 'positive' in str(exc_info.value)

    def test_system_missing_coord_skipped(self, caplog):
        """System entry missing 'coord' should be skipped with warning."""
        data = {
            'radius': 100,
            'systems': [
                {'system': {'name': 'Sol', 'global_location': {'q': 0, 'r': 0}}}
                # Missing 'coord'
            ]
        }

        import logging
        with caplog.at_level(logging.WARNING):
            galaxy = Galaxy.from_dict(data)

        # System should be skipped
        assert len(galaxy.systems) == 0

    def test_system_missing_system_key_skipped(self, caplog):
        """System entry missing 'system' should be skipped with warning."""
        data = {
            'radius': 100,
            'systems': [
                {'coord': {'q': 0, 'r': 0}}
                # Missing 'system'
            ]
        }

        import logging
        with caplog.at_level(logging.WARNING):
            galaxy = Galaxy.from_dict(data)

        # System should be skipped
        assert len(galaxy.systems) == 0

    def test_bad_system_data_skipped_galaxy_loads(self, caplog):
        """Bad system data should be skipped, galaxy still loads."""
        data = {
            'radius': 100,
            'systems': [
                {
                    'coord': {'q': 0, 'r': 0},
                    'system': {'name': 'Valid', 'global_location': {'q': 0, 'r': 0}}
                },
                {
                    'coord': {'q': 5, 'r': -3},
                    'system': {}  # Invalid - missing required fields
                }
            ]
        }

        import logging
        with caplog.at_level(logging.WARNING):
            galaxy = Galaxy.from_dict(data)

        # Should have 1 valid system
        assert len(galaxy.systems) == 1
        assert HexCoord(0, 0) in galaxy.systems
        assert galaxy.systems[HexCoord(0, 0)].name == 'Valid'

    def test_empty_systems_loads_successfully(self):
        """Empty systems list should load successfully."""
        data = {
            'radius': 50,
            'systems': []
        }

        galaxy = Galaxy.from_dict(data)

        assert galaxy.radius == 50
        assert len(galaxy.systems) == 0

    def test_missing_systems_defaults_to_empty(self):
        """Missing 'systems' key should default to empty list."""
        data = {
            'radius': 50
        }

        galaxy = Galaxy.from_dict(data)

        assert galaxy.radius == 50
        assert len(galaxy.systems) == 0
