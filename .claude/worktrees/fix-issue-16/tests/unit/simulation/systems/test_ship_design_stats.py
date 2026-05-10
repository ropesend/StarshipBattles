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
from game.core.paths import Paths


FIXTURES_DIR = Paths.get_starter_designs_dir()


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
    """Stats should respect per-component damage when provided."""

    def test_undamaged_returns_full_hp(self, fresh_registries):
        data = load_json(str(FIXTURES_DIR / "qs_escort.json"))
        result = calculate_design_stats(data, fresh_registries)
        assert result['max_hp'] > 0

    def test_damage_does_not_affect_mass(self, fresh_registries):
        """Mass is dead weight — damage shouldn't change it."""
        from game.core.component_state import (
            ComponentState, component_state_key,
        )
        data = load_json(str(FIXTURES_DIR / "qs_escort.json"))
        undamaged = calculate_design_stats(data, fresh_registries)
        damaged = calculate_design_stats(
            data, fresh_registries,
            components={
                component_state_key('bridge', 0): ComponentState(
                    component_id='bridge', instance_index=0, current_hp=0,
                ),
            },
        )
        assert damaged['mass'] == undamaged['mass']

    def test_per_instance_damage_applied_via_component_state(
        self, fresh_registries
    ):
        """PROJ-276 Phase 4: per-instance damage keyed by
        `component_state_key(component_id, instance_index)` flows
        through to the underlying Ship component's HP.

        Uses `warp_drive`, which contributes zero `warp_max_tonnage`
        when inactive — an observable downstream effect.
        """
        from game.core.component_state import (
            ComponentState, component_state_key,
        )
        data = load_json(str(FIXTURES_DIR / "qs_escort.json"))

        undamaged = calculate_design_stats(data, fresh_registries)
        assert undamaged['warp_max_tonnage'] > 0

        # Set warp_drive#0 to 0 HP — component becomes inactive and
        # contributes no warp tonnage.
        damaged = calculate_design_stats(
            data, fresh_registries,
            components={
                component_state_key('warp_drive', 0): ComponentState(
                    component_id='warp_drive',
                    instance_index=0,
                    current_hp=0,
                ),
            },
        )

        assert damaged['warp_max_tonnage'] == 0
        # Mass unchanged (dead weight).
        assert damaged['mass'] == undamaged['mass']

    def test_missing_component_state_entry_leaves_hp_unchanged(
        self, fresh_registries
    ):
        """Components without a `ComponentState` entry keep full HP."""
        from game.core.component_state import (
            ComponentState, component_state_key,
        )
        data = load_json(str(FIXTURES_DIR / "qs_escort.json"))

        baseline = calculate_design_stats(data, fresh_registries)
        # Provide a `components` dict that only covers warp_drive, not
        # the other components.
        partial = calculate_design_stats(
            data, fresh_registries,
            components={
                component_state_key('warp_drive', 0): ComponentState(
                    component_id='warp_drive',
                    instance_index=0,
                    current_hp=999,  # cap at max_hp internally
                ),
            },
        )

        # All other stats should match baseline — only warp_drive was
        # touched (and it's still at full HP).
        assert partial['max_hp'] == baseline['max_hp']
        assert partial['warp_max_tonnage'] == baseline['warp_max_tonnage']
