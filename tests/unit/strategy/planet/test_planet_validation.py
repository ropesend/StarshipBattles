"""Tests for Planet.from_dict validation (PROJ-171 Phase 3)."""
import pytest
from game.core.exceptions import PersistenceException
from game.strategy.data.planet import Planet, PlanetType, PlanetaryFacility, SpeciesPopulation


def _valid_planet_data() -> dict:
    """Return valid planet data for testing."""
    return {
        'name': 'Test Planet',
        'location': {'q': 5, 'r': 0},
        'orbit_distance': 5,
        'mass': 5.97e24,
        'radius': 6.371e6,
        'surface_area': 5.1e14,
        'density': 5514.0,
        'surface_gravity': 9.81,
        'surface_pressure': 101325.0,
        'surface_temperature': 288.0,
        'surface_water': 0.71,
        'tectonic_activity': 0.5,
        'magnetic_field': 1.0,
        'planet_type': 'CONTINENTAL',
        'atmosphere': {'N2': 79000, 'O2': 21000},
        'facilities': [],
        'populations': []
    }


def _valid_facility_data() -> dict:
    """Return valid facility data for testing."""
    return {
        'instance_id': 'facility-001',
        'design_id': 'design-001',
        'name': 'Test Facility',
        'design_data': {'layers': {}},
        'is_operational': True,
        'construction_queue': [],
        'consumable_levels': {}
    }


def _valid_population_data() -> dict:
    """Return valid population data for testing."""
    return {
        'race_id': 'humans',
        'count': 1000,
        'happiness': 0.7
    }


class TestPlanetFromDictValidation:
    """Tests for Planet.from_dict input validation."""

    def test_valid_data_creates_planet(self):
        """Valid planet data should create Planet instance."""
        data = _valid_planet_data()
        planet = Planet.from_dict(data)

        assert planet.name == 'Test Planet'
        assert planet.mass == 5.97e24
        assert planet.planet_type == PlanetType.CONTINENTAL

    @pytest.mark.parametrize('missing_key', [
        'name', 'location', 'orbit_distance', 'mass', 'radius', 'surface_area',
        'density', 'surface_gravity', 'surface_pressure', 'surface_temperature',
        'surface_water', 'tectonic_activity', 'magnetic_field', 'planet_type'
    ])
    def test_missing_key_raises_persistence_exception(self, missing_key):
        """Missing required key should raise PersistenceException."""
        data = _valid_planet_data()
        del data[missing_key]

        with pytest.raises(PersistenceException) as exc_info:
            Planet.from_dict(data)

        assert 'Planet' in str(exc_info.value)
        assert missing_key in str(exc_info.value)

    def test_invalid_planet_type_raises_persistence_exception(self):
        """Invalid planet_type enum should raise PersistenceException with valid values."""
        data = _valid_planet_data()
        data['planet_type'] = 'INVALID_TYPE'

        with pytest.raises(PersistenceException) as exc_info:
            Planet.from_dict(data)

        error_msg = str(exc_info.value)
        assert 'Planet' in error_msg
        assert 'planet_type' in error_msg
        # Should list valid values
        assert 'CONTINENTAL' in error_msg

    @pytest.mark.parametrize('field', ['mass', 'radius', 'surface_area', 'density', 'surface_gravity'])
    def test_negative_positive_field_raises_persistence_exception(self, field):
        """Fields requiring positive values should raise on negative."""
        data = _valid_planet_data()
        data[field] = -1.0

        with pytest.raises(PersistenceException) as exc_info:
            Planet.from_dict(data)

        assert 'Planet' in str(exc_info.value)
        assert field in str(exc_info.value)

    @pytest.mark.parametrize('field', ['orbit_distance', 'surface_pressure', 'surface_water'])
    def test_negative_non_negative_field_raises_persistence_exception(self, field):
        """Fields requiring non-negative values should raise on negative."""
        data = _valid_planet_data()
        data[field] = -1.0

        with pytest.raises(PersistenceException) as exc_info:
            Planet.from_dict(data)

        assert 'Planet' in str(exc_info.value)
        assert field in str(exc_info.value)

    def test_bad_facility_raises_persistence_exception(self):
        """PROJ-251: Bad facility in list raises PersistenceException (strict deserialization)."""
        data = _valid_planet_data()
        data['facilities'] = [
            _valid_facility_data(),
            {'broken': 'data'},  # Missing required fields
        ]

        with pytest.raises(PersistenceException):
            Planet.from_dict(data)

    def test_bad_population_raises_persistence_exception(self):
        """PROJ-251: Bad population in list raises PersistenceException (strict deserialization)."""
        data = _valid_planet_data()
        data['populations'] = [
            _valid_population_data(),
            {'broken': 'data'},  # Missing required fields
        ]

        with pytest.raises(PersistenceException):
            Planet.from_dict(data)

    def test_bad_order_raises_persistence_exception(self):
        """PROJ-251: Bad planet order raises PersistenceException instead of being dropped."""
        data = _valid_planet_data()
        data['orders'] = [
            {
                'type': 'ACTIVATE_ABILITY',
                'target': {
                    'type': 'dict',
                    'value': {
                        'facility_instance_id': 'fac-1',
                        'ability_name': 'PlanetaryShield',
                    },
                },
            },
            {'target': {'type': 'dict', 'value': {'ability_name': 'Broken'}}},
        ]

        with pytest.raises(PersistenceException) as exc_info:
            Planet.from_dict(data)

        assert 'Planet' in str(exc_info.value)
        assert 'order' in str(exc_info.value).lower()
        assert exc_info.value.context.get('order_index') == 1

    def test_corrupt_location_raises_persistence_exception(self):
        """Corrupt location should raise PersistenceException."""
        data = _valid_planet_data()
        data['location'] = {'x': 0}  # Invalid, needs 'q' and 'r'

        with pytest.raises(PersistenceException) as exc_info:
            Planet.from_dict(data)

        assert 'Planet' in str(exc_info.value)
        assert 'location' in str(exc_info.value).lower()


class TestPlanetaryFacilityFromDictValidation:
    """Tests for PlanetaryFacility.from_dict input validation (PROJ-178 Phase 2)."""

    def test_valid_data_creates_facility(self):
        """Valid facility data should create PlanetaryFacility instance."""
        data = _valid_facility_data()
        facility = PlanetaryFacility.from_dict(data)

        assert facility.instance_id == 'facility-001'
        assert facility.design_id == 'design-001'
        assert facility.name == 'Test Facility'
        assert facility.design_data == {'layers': {}}
        assert facility.is_operational is True

    @pytest.mark.parametrize('missing_key', [
        'instance_id', 'design_id', 'name', 'design_data'
    ])
    def test_missing_required_key_raises_persistence_exception(self, missing_key):
        """Missing required key should raise PersistenceException."""
        data = _valid_facility_data()
        del data[missing_key]

        with pytest.raises(PersistenceException) as exc_info:
            PlanetaryFacility.from_dict(data)

        assert 'PlanetaryFacility' in str(exc_info.value)
        assert missing_key in str(exc_info.value)

    def test_optional_fields_default_correctly(self):
        """Optional fields should default to expected values."""
        data = {
            'instance_id': 'fac-001',
            'design_id': 'design-001',
            'name': 'Minimal Facility',
            'design_data': {'layers': {}}
        }
        facility = PlanetaryFacility.from_dict(data)

        assert facility.is_operational is True
        assert facility.construction_queue == []
        assert facility.consumable_levels == {}


class TestSpeciesPopulationFromDictValidation:
    """Tests for SpeciesPopulation.from_dict input validation (PROJ-178 Phase 2)."""

    def test_valid_data_creates_population(self):
        """Valid population data should create SpeciesPopulation instance."""
        data = _valid_population_data()
        population = SpeciesPopulation.from_dict(data)

        assert population.race_id == 'humans'
        assert population.count == 1000
        assert population.happiness == 0.7

    @pytest.mark.parametrize('missing_key', ['race_id', 'count'])
    def test_missing_required_key_raises_persistence_exception(self, missing_key):
        """Missing required key should raise PersistenceException."""
        data = _valid_population_data()
        del data[missing_key]

        with pytest.raises(PersistenceException) as exc_info:
            SpeciesPopulation.from_dict(data)

        assert 'SpeciesPopulation' in str(exc_info.value)
        assert missing_key in str(exc_info.value)

    def test_happiness_defaults_to_half(self):
        """Happiness should default to 0.5 when not provided."""
        data = {
            'race_id': 'aliens',
            'count': 500
        }
        population = SpeciesPopulation.from_dict(data)

        assert population.happiness == 0.5
