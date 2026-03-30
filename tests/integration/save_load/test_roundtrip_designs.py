"""Round-trip tests for DesignMetadata serialization (PROJ-223 Phase 2)."""

import pytest

from game.strategy.data.design_metadata import DesignMetadata
from tests.fixtures.strategy_entities import create_test_design_metadata
from tests.integration.save_load.conftest import assert_round_trip_fidelity


class TestDesignMetadataRoundTrip:
    """DesignMetadata round-trip serialization tests."""

    def test_to_dict_includes_all_12_fields(self):
        dm = create_test_design_metadata()
        d = dm.to_dict()
        expected = ['design_id', 'name', 'ship_class', 'vehicle_type', 'mass',
                    'combat_power', 'construction_cost', 'created_date', 'last_modified',
                    'is_obsolete', 'times_built', 'theme_id']
        for key in expected:
            assert key in d, f"Missing key: {key}"

    def test_from_dict_restores_all_fields(self):
        original = create_test_design_metadata()
        d = original.to_dict()
        restored = DesignMetadata.from_dict(d)
        assert restored.design_id == original.design_id
        assert restored.name == original.name
        assert restored.ship_class == original.ship_class
        assert restored.vehicle_type == original.vehicle_type
        assert restored.mass == original.mass
        assert restored.combat_power == original.combat_power
        assert restored.construction_cost == original.construction_cost
        assert restored.created_date == original.created_date
        assert restored.last_modified == original.last_modified
        assert restored.is_obsolete == original.is_obsolete
        assert restored.times_built == original.times_built
        assert restored.theme_id == original.theme_id

    def test_round_trip_field_level(self):
        assert_round_trip_fidelity(create_test_design_metadata(), DesignMetadata)

    def test_optional_field_defaults(self):
        """Only design_id and name are required."""
        minimal = {'design_id': 'minimal', 'name': 'Minimal Ship'}
        restored = DesignMetadata.from_dict(minimal)
        assert restored.ship_class == "Unknown"
        assert restored.vehicle_type == "Ship"
        assert restored.mass == 0.0
        assert restored.is_obsolete is False
        assert restored.times_built == 0
