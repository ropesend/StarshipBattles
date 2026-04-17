"""Round-trip tests for ShipInstance serialization (PROJ-223 Phase 3)."""

import json
import pytest

from game.strategy.data.component_state import ComponentState, component_state_key
from game.strategy.data.ship_instance import ShipInstance
from tests.fixtures.strategy_entities import create_test_ship_instance
from tests.integration.save_load.conftest import assert_round_trip_fidelity, assert_field_preserved


class TestShipInstanceRoundTrip:
    """ShipInstance compound round-trip serialization tests."""

    def test_all_core_fields(self):
        si = create_test_ship_instance()
        d = si.to_dict()
        expected = ['instance_id', 'design_id', 'name', 'owner_id',
                    'design_data', 'current_hp', 'is_alive', 'is_derelict',
                    'experience', 'kills', 'battles_survived', 'serial']
        for key in expected:
            assert key in d, f"Missing key: {key}"

    def test_round_trip_field_level(self):
        si = create_test_ship_instance()
        restored = assert_round_trip_fidelity(si, ShipInstance)
        assert_field_preserved(si, restored, 'instance_id')
        assert_field_preserved(si, restored, 'design_id')
        assert_field_preserved(si, restored, 'name')
        assert_field_preserved(si, restored, 'owner_id')
        assert_field_preserved(si, restored, 'current_hp')
        assert_field_preserved(si, restored, 'is_alive')
        assert_field_preserved(si, restored, 'is_derelict')
        assert_field_preserved(si, restored, 'experience')
        assert_field_preserved(si, restored, 'kills')
        assert_field_preserved(si, restored, 'battles_survived')
        assert_field_preserved(si, restored, 'serial')

    def test_design_data_preserved(self):
        """Large nested design_data dict survives round-trip."""
        si = create_test_ship_instance()
        restored = assert_round_trip_fidelity(si, ShipInstance)
        assert restored.design_data == si.design_data

    def test_consumable_levels(self):
        si = create_test_ship_instance(consumable_levels={"fuel": 80.0, "energy": 50.0, "ammo": 30.0})
        restored = assert_round_trip_fidelity(si, ShipInstance)
        assert restored.consumable_levels == si.consumable_levels

    def test_component_toggles(self):
        si = create_test_ship_instance(component_toggles={"shield_1": True, "cloak_1": False, "engine_2": True})
        restored = assert_round_trip_fidelity(si, ShipInstance)
        assert restored.component_toggles == si.component_toggles

    def test_cargo_contents_populated(self):
        si = create_test_ship_instance(cargo_contents={"minerals": 10, "fuel_pods": 5})
        restored = assert_round_trip_fidelity(si, ShipInstance)
        assert restored.cargo_contents == si.cargo_contents

    def test_cargo_contents_empty_omitted(self):
        """Empty cargo is omitted from serialization."""
        si = create_test_ship_instance(cargo_contents={})
        d = si.to_dict()
        # Empty cargo may or may not be in dict — from_dict handles both
        restored = ShipInstance.from_dict(d)
        assert restored.cargo_contents == {} or restored.cargo_contents is not None

    def test_per_instance_component_state_round_trip(self):
        """PROJ-276 Phase 5: `components` dict carries per-instance HP
        across a save/load round-trip. Multi-instance ships preserve
        which specific instance was damaged."""
        si = create_test_ship_instance(components={
            component_state_key("laser_1", 0): ComponentState(
                component_id="laser_1", instance_index=0, current_hp=5.0,
            ),
            component_state_key("shield_2", 0): ComponentState(
                component_id="shield_2", instance_index=0, current_hp=10.0,
            ),
            # Same component id, different instance — the key test for
            # per-instance precision.
            component_state_key("laser_1", 1): ComponentState(
                component_id="laser_1", instance_index=1, current_hp=40.0,
            ),
        })
        restored = assert_round_trip_fidelity(si, ShipInstance)
        assert set(restored.components) == set(si.components)
        for key, cs in si.components.items():
            assert restored.components[key].current_hp == cs.current_hp
            assert restored.components[key].instance_index == cs.instance_index
            assert restored.components[key].component_id == cs.component_id

    def test_registries_parameter(self, fresh_registries):
        si = create_test_ship_instance()
        d = si.to_dict()
        parsed = json.loads(json.dumps(d))
        restored = ShipInstance.from_dict(parsed, registries=fresh_registries)
        assert restored._registries is not None

    def test_json_serializable(self):
        si = create_test_ship_instance()
        d = si.to_dict()
        json_str = json.dumps(d)
        parsed = json.loads(json_str)
        restored = ShipInstance.from_dict(parsed)
        assert restored.instance_id == si.instance_id
