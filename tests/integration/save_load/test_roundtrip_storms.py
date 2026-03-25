"""Round-trip tests for StormEffect and Storm serialization (PROJ-223 Phase 2)."""

import pytest

from game.strategy.data.storm import Storm, StormEffect
from game.core.hex_math import HexCoord
from tests.fixtures.strategy_entities import create_test_storm, create_test_storm_effect
from tests.integration.save_load.conftest import assert_round_trip_fidelity


class TestStormEffectRoundTrip:
    """StormEffect round-trip serialization tests."""

    def test_to_dict_includes_all_5_fields(self):
        e = create_test_storm_effect()
        d = e.to_dict()
        expected = ['shield_capacity_mult', 'thrust_mult', 'strategic_mult',
                    'damage_per_tick', 'fuel_drain_per_tick']
        for key in expected:
            assert key in d, f"Missing key: {key}"

    def test_from_dict_with_defaults_for_missing(self):
        """Missing fields should use defaults (1.0 for mults, 0.0 for rates)."""
        restored = StormEffect.from_dict({})
        assert restored.shield_capacity_mult == 1.0
        assert restored.thrust_mult == 1.0
        assert restored.strategic_mult == 1.0
        assert restored.damage_per_tick == 0.0
        assert restored.fuel_drain_per_tick == 0.0

    def test_round_trip_field_level(self):
        assert_round_trip_fidelity(create_test_storm_effect(), StormEffect)


class TestStormRoundTrip:
    """Storm round-trip serialization tests."""

    def test_to_dict_includes_all_fields(self):
        s = create_test_storm()
        d = s.to_dict()
        expected = ['name', 'storm_type', 'location', 'hex_offsets',
                    'effects', 'image_variant', 'intensity']
        for key in expected:
            assert key in d, f"Missing key: {key}"

    def test_from_dict_restores_all_fields(self):
        original = create_test_storm()
        d = original.to_dict()
        restored = Storm.from_dict(d)
        assert restored.name == original.name
        assert restored.storm_type == original.storm_type
        assert restored.location == original.location
        assert restored.image_variant == original.image_variant
        assert restored.intensity == original.intensity

    def test_nested_storm_effect_round_trip(self):
        original = create_test_storm()
        d = original.to_dict()
        restored = Storm.from_dict(d)
        assert restored.effects.shield_capacity_mult == original.effects.shield_capacity_mult
        assert restored.effects.damage_per_tick == original.effects.damage_per_tick

    def test_hex_offsets_round_trip(self):
        """hex_offsets (frozenset of HexCoords) survives round-trip."""
        offsets = frozenset({HexCoord(0, 0), HexCoord(1, 0), HexCoord(0, 1), HexCoord(-1, 1)})
        s = create_test_storm(hex_offsets=offsets)
        d = s.to_dict()
        restored = Storm.from_dict(d)
        assert restored.hex_offsets == offsets
