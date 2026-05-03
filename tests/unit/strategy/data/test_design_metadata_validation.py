"""Tests for DesignMetadata deserialization validation.

PROJ-171: Phase 5 - DesignMetadata.from_dict() validation.
"""

import pytest
from game.strategy.data.design_metadata import DesignMetadata
from game.core.exceptions import PersistenceException


class TestDesignMetadataValidation:
    """Tests for DesignMetadata.from_dict() validation."""

    @pytest.fixture
    def valid_metadata_data(self):
        """Minimal valid DesignMetadata data."""
        return {
            'design_id': 'cruiser_mk1',
            'name': 'Cruiser Mark I',
            'ship_class': 'Cruiser',
            'vehicle_type': 'Ship',
            'mass': 5000.0,
            'combat_power': 150.0,
            'construction_cost': {'minerals': 100, 'energy': 50}
        }

    def test_valid_data_creates_design_metadata(self, valid_metadata_data):
        """Valid data should create DesignMetadata successfully."""
        meta = DesignMetadata.from_dict(valid_metadata_data)
        assert meta.design_id == 'cruiser_mk1'
        assert meta.name == 'Cruiser Mark I'
        assert meta.ship_class == 'Cruiser'

    def test_missing_design_id_raises_persistence_exception(self, valid_metadata_data):
        """Missing design_id should raise PersistenceException."""
        del valid_metadata_data['design_id']
        with pytest.raises(PersistenceException) as exc_info:
            DesignMetadata.from_dict(valid_metadata_data)
        assert 'design_id' in str(exc_info.value)
        assert 'DesignMetadata' in str(exc_info.value)

    def test_missing_name_raises_persistence_exception(self, valid_metadata_data):
        """Missing name should raise PersistenceException."""
        del valid_metadata_data['name']
        with pytest.raises(PersistenceException) as exc_info:
            DesignMetadata.from_dict(valid_metadata_data)
        assert 'name' in str(exc_info.value)

    # PROJ-323 Task 3.24: 5 missing-field default tests parametrized.
    @pytest.mark.parametrize("field,attr,default", [
        pytest.param('ship_class', 'ship_class', 'Unknown', id='ship_class'),
        pytest.param('vehicle_type', 'vehicle_type', 'Ship', id='vehicle_type'),
        pytest.param('mass', 'mass', 0.0, id='mass'),
        pytest.param('combat_power', 'combat_power', 0.0, id='combat_power'),
        pytest.param('construction_cost', 'construction_cost', {}, id='construction_cost'),
    ])
    def test_missing_field_uses_default(self, valid_metadata_data, field, attr, default):
        """Missing optional field should fall back to its documented default."""
        del valid_metadata_data[field]
        meta = DesignMetadata.from_dict(valid_metadata_data)
        assert getattr(meta, attr) == default

    def test_minimal_required_fields_only(self):
        """Only design_id and name are required."""
        data = {'design_id': 'test_ship', 'name': 'Test Ship'}
        meta = DesignMetadata.from_dict(data)
        assert meta.design_id == 'test_ship'
        assert meta.name == 'Test Ship'
        # All other fields should have defaults
        assert meta.ship_class == 'Unknown'
        assert meta.vehicle_type == 'Ship'
        assert meta.mass == 0.0
        assert meta.combat_power == 0.0
