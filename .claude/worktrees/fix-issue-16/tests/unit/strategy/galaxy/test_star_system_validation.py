"""Tests for StarSystem.from_dict() input validation.

PROJ-171: Deserialization Input Validation - Phase 2
"""
import pytest
from game.core.exceptions import PersistenceException
from game.core.hex_math import HexCoord
from game.strategy.data.galaxy import StarSystem


class TestStarSystemFromDictValidation:
    """Test validation in StarSystem.from_dict()."""

    def test_valid_data_creates_star_system(self):
        """Valid data should create StarSystem successfully."""
        data = {
            'name': 'Sol',
            'global_location': {'q': 10, 'r': -5},
            'stars': [],
            'warp_points': [],
            'planets': [],
            'region_id': 1
        }
        system = StarSystem.from_dict(data)

        assert system.name == 'Sol'
        assert system.global_location == HexCoord(10, -5)
        assert system.region_id == 1

    def test_missing_name_raises_persistence_exception(self):
        """Missing 'name' should raise PersistenceException."""
        data = {
            'global_location': {'q': 10, 'r': -5},
            'stars': [],
            'warp_points': [],
            'planets': []
        }

        with pytest.raises(PersistenceException) as exc_info:
            StarSystem.from_dict(data)

        assert 'StarSystem' in str(exc_info.value)
        assert 'name' in str(exc_info.value)

    def test_missing_global_location_raises_persistence_exception(self):
        """Missing 'global_location' should raise PersistenceException."""
        data = {
            'name': 'Sol',
            'stars': [],
            'warp_points': [],
            'planets': []
        }

        with pytest.raises(PersistenceException) as exc_info:
            StarSystem.from_dict(data)

        assert 'StarSystem' in str(exc_info.value)
        assert 'global_location' in str(exc_info.value)

    def test_bad_star_raises_persistence_exception(self):
        """PROJ-251: Bad star in list raises PersistenceException (strict deserialization)."""
        data = {
            'name': 'Sol',
            'global_location': {'q': 10, 'r': -5},
            'stars': [
                {
                    'name': 'Sol',
                    'mass': 1.0,
                    'radius_hexes': 1,
                    'temperature': 5778,
                    'luminosity': 1.0,
                    'spectrum': {
                        'gamma_ray': 0, 'xray': 0, 'ultraviolet': 0.1,
                        'blue': 0.2, 'green': 0.3, 'red': 0.25,
                        'infrared': 0.1, 'microwave': 0.05, 'radio': 0
                    },
                    'star_type': 'MAIN_SEQUENCE',
                    'color': [255, 255, 0],
                    'age': 4.6,
                    'location': {'q': 0, 'r': 0}
                },
                {'name': 'BadStar'}  # Invalid - missing required fields
            ],
            'warp_points': [],
            'planets': []
        }

        with pytest.raises(PersistenceException):
            StarSystem.from_dict(data)

    def test_bad_planet_raises_persistence_exception(self):
        """PROJ-251: Bad planet in list raises PersistenceException (strict deserialization)."""
        data = {
            'name': 'Sol',
            'global_location': {'q': 10, 'r': -5},
            'stars': [],
            'warp_points': [],
            'planets': [
                {'name': 'BadPlanet'}  # Invalid - missing required fields
            ]
        }

        with pytest.raises(PersistenceException):
            StarSystem.from_dict(data)

    def test_bad_warp_point_raises_persistence_exception(self):
        """PROJ-251: Bad warp point in list raises PersistenceException (strict deserialization)."""
        data = {
            'name': 'Sol',
            'global_location': {'q': 10, 'r': -5},
            'stars': [],
            'warp_points': [
                {'destination_id': 'valid', 'location': {'q': 1, 'r': 2}},
                {'destination_id': 'invalid'}  # Missing location
            ],
            'planets': []
        }

        with pytest.raises(PersistenceException):
            StarSystem.from_dict(data)

    def test_empty_children_lists_loads_successfully(self):
        """Empty children lists should load successfully."""
        data = {
            'name': 'EmptySystem',
            'global_location': {'q': 0, 'r': 0},
            'stars': [],
            'warp_points': [],
            'planets': []
        }

        system = StarSystem.from_dict(data)

        assert system.name == 'EmptySystem'
        assert len(system.stars) == 0
        assert len(system.warp_points) == 0
        assert len(system.planets) == 0

    def test_missing_optional_children_defaults_to_empty(self):
        """Missing optional children lists should default to empty."""
        data = {
            'name': 'MinimalSystem',
            'global_location': {'q': 0, 'r': 0}
            # No stars, warp_points, or planets keys
        }

        system = StarSystem.from_dict(data)

        assert system.name == 'MinimalSystem'
        assert len(system.stars) == 0
        assert len(system.warp_points) == 0
        assert len(system.planets) == 0
