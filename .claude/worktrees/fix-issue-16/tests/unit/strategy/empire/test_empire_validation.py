"""Tests for Empire.from_dict validation.

PROJ-171: Deserialization Input Validation
"""
import pytest
from game.core.exceptions import PersistenceException
from game.strategy.data.empire import Empire


def make_valid_empire_data():
    """Create minimal valid Empire data."""
    return {
        'id': 'empire-001',
        'name': 'Federation',
        'color': (0, 100, 255),
    }


def make_valid_fleet_data(fleet_id='fleet-001'):
    """Create minimal valid Fleet data."""
    return {
        'id': fleet_id,
        'owner_id': 'empire-001',
        'location': [0, 0],
        'ships': [],
        'orders': [],
    }


class TestEmpireValidation:
    """Tests for Empire.from_dict validation."""

    def test_valid_data_creates_empire(self):
        """Valid data creates Empire successfully."""
        data = make_valid_empire_data()
        empire = Empire.from_dict(data)
        assert empire.id == 'empire-001'
        assert empire.name == 'Federation'
        assert empire.color == (0, 100, 255)

    def test_missing_id_raises_persistence_exception(self):
        """Missing id raises PersistenceException."""
        data = make_valid_empire_data()
        del data['id']

        with pytest.raises(PersistenceException) as exc_info:
            Empire.from_dict(data)

        assert 'id' in str(exc_info.value)
        assert 'Empire' in str(exc_info.value)
        assert 'missing_keys' in exc_info.value.context

    def test_missing_name_raises_persistence_exception(self):
        """Missing name raises PersistenceException."""
        data = make_valid_empire_data()
        del data['name']

        with pytest.raises(PersistenceException) as exc_info:
            Empire.from_dict(data)

        assert 'name' in str(exc_info.value)
        assert 'Empire' in str(exc_info.value)

    def test_missing_color_raises_persistence_exception(self):
        """Missing color raises PersistenceException."""
        data = make_valid_empire_data()
        del data['color']

        with pytest.raises(PersistenceException) as exc_info:
            Empire.from_dict(data)

        assert 'color' in str(exc_info.value)
        assert 'Empire' in str(exc_info.value)

    def test_valid_empire_with_fleets(self):
        """Empire with valid fleets loads correctly."""
        data = make_valid_empire_data()
        data['fleets'] = [
            make_valid_fleet_data('fleet-001'),
            make_valid_fleet_data('fleet-002'),
        ]

        empire = Empire.from_dict(data)
        assert len(empire.fleets) == 2
        assert empire.fleets[0].id == 'fleet-001'
        assert empire.fleets[1].id == 'fleet-002'
        # Owner ID should be set to empire ID
        assert empire.fleets[0].owner_id == 'empire-001'

    def test_bad_fleet_raises_persistence_exception(self):
        """PROJ-251: Corrupt fleet in list raises PersistenceException (strict deserialization)."""
        data = make_valid_empire_data()
        data['fleets'] = [
            make_valid_fleet_data('fleet-001'),
            {'corrupt': 'data'},  # Missing required fields
            make_valid_fleet_data('fleet-002'),
        ]

        with pytest.raises(PersistenceException) as exc_info:
            Empire.from_dict(data)
        assert exc_info.value.context.get('fleet_index') == 1

    def test_race_config_loads_with_defaults(self):
        """Race config loads with .get() defaults (fully defensive)."""
        data = make_valid_empire_data()
        data['race_config'] = {'name': 'Humans'}  # Minimal data - rest get defaults

        empire = Empire.from_dict(data)
        # RaceConfig.from_dict is fully defensive with .get() defaults
        assert empire.race_config is not None
        assert empire.race_config.name == 'Humans'

    def test_optional_fields_have_defaults(self):
        """Optional fields work with defaults when not provided."""
        data = make_valid_empire_data()
        empire = Empire.from_dict(data)

        # Verify defaults are applied
        assert empire.theme_path is None
        assert empire.empire_theme_id == 'Federation'
        assert empire.flag_id == ''
        assert empire.portrait_id == ''
        assert empire.race_config is None
        assert empire.fleets == []
        assert empire.colonies == []

    def test_empire_with_built_ship_designs(self):
        """Empire restores built_ship_designs set."""
        data = make_valid_empire_data()
        data['built_ship_designs'] = ['design-001', 'design-002']

        empire = Empire.from_dict(data)
        assert empire.built_ship_designs == {'design-001', 'design-002'}

    def test_empire_with_resource_pool(self):
        """Empire restores resource economy data."""
        data = make_valid_empire_data()
        data['resource_pool'] = {'energy': 1000, 'minerals': 500}
        data['max_storage'] = {'energy': 5000, 'minerals': 2000}

        empire = Empire.from_dict(data)
        assert empire.resource_pool == {'energy': 1000, 'minerals': 500}
        assert empire.max_storage == {'energy': 5000, 'minerals': 2000}


class TestEmpireSerializationDeterminism:
    """PROJ-223: Verify deterministic serialization output."""

    def test_built_ship_designs_sorted_in_to_dict(self):
        """built_ship_designs should be sorted for deterministic JSON output."""
        empire = Empire(empire_id=0, name="Test", color=(0, 0, 255))
        empire.built_ship_designs = {"frigate", "escort", "dreadnought", "battleship"}

        result = empire.to_dict()
        designs = result['built_ship_designs']

        assert designs == sorted(designs), (
            f"built_ship_designs not sorted: {designs}"
        )
        assert designs == ["battleship", "dreadnought", "escort", "frigate"]

    def test_built_ship_designs_deterministic_across_calls(self):
        """Multiple to_dict calls produce identical output."""
        empire = Empire(empire_id=0, name="Test", color=(0, 0, 255))
        empire.built_ship_designs = {"z_design", "a_design", "m_design"}

        results = [empire.to_dict()['built_ship_designs'] for _ in range(10)]
        assert all(r == results[0] for r in results)
