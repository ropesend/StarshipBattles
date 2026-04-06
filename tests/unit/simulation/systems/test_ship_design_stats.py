"""
Tests for calculate_design_stats() — the single source of truth for
computing ship stats from design JSON data.

This function replaces the strategy layer's ShipStatsCalculator by
using Ship.from_dict() + recalculate_stats() and returning a dict
with the same interface contract that ShipInstance.get_calculated_stats()
callers expect.
"""
import pytest
from game.core.json_utils import load_json
from game.simulation.entities.ship_design_stats import calculate_design_stats
from tests.fixtures.paths import get_project_root


FIXTURES_DIR = get_project_root() / "tests" / "fixtures" / "quickstart" / "designs"


class TestCalculateDesignStatsInterface:
    """The returned dict must have all keys consumers expect."""

    REQUIRED_KEYS = [
        'max_hp', 'mass', 'resource_storage', 'cargo_storage',
        'pod_storage_mass', 'strategic_movement', 'warp_max_tonnage',
        'warp_resource_costs',
    ]

    def test_returns_dict(self, fresh_registries):
        data = load_json(str(FIXTURES_DIR / "qs_escort.json"))
        result = calculate_design_stats(data, fresh_registries)
        assert isinstance(result, dict)

    @pytest.mark.parametrize("key", REQUIRED_KEYS)
    def test_has_required_key(self, key, fresh_registries):
        data = load_json(str(FIXTURES_DIR / "qs_escort.json"))
        result = calculate_design_stats(data, fresh_registries)
        assert key in result, f"Missing required key: {key}"

    def test_max_hp_is_positive_int(self, fresh_registries):
        data = load_json(str(FIXTURES_DIR / "qs_escort.json"))
        result = calculate_design_stats(data, fresh_registries)
        assert isinstance(result['max_hp'], int)
        assert result['max_hp'] > 0

    def test_mass_is_positive_float(self, fresh_registries):
        data = load_json(str(FIXTURES_DIR / "qs_escort.json"))
        result = calculate_design_stats(data, fresh_registries)
        assert isinstance(result['mass'], (int, float))
        assert result['mass'] > 0

    def test_resource_storage_is_dict(self, fresh_registries):
        data = load_json(str(FIXTURES_DIR / "qs_escort.json"))
        result = calculate_design_stats(data, fresh_registries)
        assert isinstance(result['resource_storage'], dict)

    def test_cargo_storage_is_dict(self, fresh_registries):
        data = load_json(str(FIXTURES_DIR / "qs_escort.json"))
        result = calculate_design_stats(data, fresh_registries)
        assert isinstance(result['cargo_storage'], dict)

    def test_warp_resource_costs_is_dict(self, fresh_registries):
        data = load_json(str(FIXTURES_DIR / "qs_escort.json"))
        result = calculate_design_stats(data, fresh_registries)
        assert isinstance(result['warp_resource_costs'], dict)


class TestCalculateDesignStatsValues:
    """Stats values should match Ship.from_dict() + recalculate_stats()."""

    def test_escort_has_fuel_storage(self, fresh_registries):
        data = load_json(str(FIXTURES_DIR / "qs_escort.json"))
        result = calculate_design_stats(data, fresh_registries)
        assert result['resource_storage'].get('fuel', 0) > 0

    def test_escort_has_strategic_movement(self, fresh_registries):
        data = load_json(str(FIXTURES_DIR / "qs_escort.json"))
        result = calculate_design_stats(data, fresh_registries)
        assert result['strategic_movement'] > 0

    def test_escort_has_warp(self, fresh_registries):
        data = load_json(str(FIXTURES_DIR / "qs_escort.json"))
        result = calculate_design_stats(data, fresh_registries)
        assert result['warp_max_tonnage'] > 0
        assert result['warp_resource_costs'].get('energy', 0) > 0

    def test_complex_has_no_movement(self, fresh_registries):
        data = load_json(str(FIXTURES_DIR / "qs_geologic_stabilizer_complex.json"))
        result = calculate_design_stats(data, fresh_registries)
        assert result['strategic_movement'] == 0
        assert result['warp_max_tonnage'] == 0
        assert result['warp_resource_costs'] == {}

    def test_cargo_freighter_has_cargo(self, fresh_registries):
        data = load_json(str(FIXTURES_DIR / "qs_cargo_freighter.json"))
        result = calculate_design_stats(data, fresh_registries)
        assert len(result['cargo_storage']) > 0

    def test_colony_ship_has_pod_storage(self, fresh_registries):
        data = load_json(str(FIXTURES_DIR / "qs_colony_ship.json"))
        result = calculate_design_stats(data, fresh_registries)
        assert result['pod_storage_mass'] > 0


class TestCalculateDesignStatsWithDamage:
    """Stats should respect component damage when provided."""

    def test_undamaged_returns_full_hp(self, fresh_registries):
        data = load_json(str(FIXTURES_DIR / "qs_escort.json"))
        result = calculate_design_stats(data, fresh_registries)
        assert result['max_hp'] > 0

    def test_damage_does_not_affect_mass(self, fresh_registries):
        """Mass is dead weight — damage shouldn't change it."""
        data = load_json(str(FIXTURES_DIR / "qs_escort.json"))
        undamaged = calculate_design_stats(data, fresh_registries)
        damaged = calculate_design_stats(
            data, fresh_registries,
            component_damage={'bridge': 0}
        )
        assert damaged['mass'] == undamaged['mass']
