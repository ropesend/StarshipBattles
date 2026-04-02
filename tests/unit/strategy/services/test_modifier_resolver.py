"""Tests for modifier_resolver - extracts size_mount scaling from design_data components.

Phase 2: Runtime modifier resolution for strategic ability scaling.
"""
import pytest
from game.strategy.services.modifier_resolver import (
    resolve_size_multiplier,
    resolve_stat_from_size_mount,
)


class TestResolveSizeMultiplier:
    """Test extracting size_mount value from component entries."""

    def test_component_with_size_mount_0_2(self, fresh_registries):
        """Should return 0.2 when size_mount modifier value is 0.2."""
        comp_entry = {
            "id": "metal_harvester",
            "modifiers": [{"id": "simple_size_mount", "value": 0.2}]
        }
        result = resolve_size_multiplier(comp_entry)
        assert result == pytest.approx(0.2)

    def test_component_with_size_mount_1_0(self, fresh_registries):
        """Should return 1.0 when size_mount modifier value is 1.0."""
        comp_entry = {
            "id": "metal_harvester",
            "modifiers": [{"id": "simple_size_mount", "value": 1.0}]
        }
        result = resolve_size_multiplier(comp_entry)
        assert result == pytest.approx(1.0)

    def test_component_without_modifiers(self):
        """Should return 1.0 when no modifiers present."""
        comp_entry = {"id": "metal_harvester"}
        result = resolve_size_multiplier(comp_entry)
        assert result == pytest.approx(1.0)

    def test_component_with_empty_modifiers(self):
        """Should return 1.0 when modifiers list is empty."""
        comp_entry = {"id": "metal_harvester", "modifiers": []}
        result = resolve_size_multiplier(comp_entry)
        assert result == pytest.approx(1.0)

    def test_component_with_other_modifiers_only(self):
        """Should return 1.0 when only non-size modifiers present."""
        comp_entry = {
            "id": "railgun",
            "modifiers": [{"id": "hardened_mount", "value": 2.0}]
        }
        result = resolve_size_multiplier(comp_entry)
        assert result == pytest.approx(1.0)

    def test_string_component_entry(self):
        """Should return 1.0 for plain string component IDs."""
        result = resolve_size_multiplier("metal_harvester")
        assert result == pytest.approx(1.0)

    def test_component_with_multiple_modifiers(self):
        """Should extract size_mount from among multiple modifiers."""
        comp_entry = {
            "id": "metal_harvester",
            "modifiers": [
                {"id": "hardened_mount", "value": 1.5},
                {"id": "simple_size_mount", "value": 0.5},
            ]
        }
        result = resolve_size_multiplier(comp_entry)
        assert result == pytest.approx(0.5)


class TestResolveStatFromSizeMount:
    """Test resolving specific stat values from size_mount."""

    def test_harvest_rate_mult_at_0_2(self, fresh_registries):
        """harvest_rate_mult should be 0.2 at size 0.2 (linear)."""
        comp_entry = {
            "id": "metal_harvester",
            "modifiers": [{"id": "simple_size_mount", "value": 0.2}]
        }
        result = resolve_stat_from_size_mount(
            comp_entry, "harvest_rate_mult", fresh_registries
        )
        assert result == pytest.approx(0.2, rel=0.01)

    def test_local_storage_mult_at_0_2(self, fresh_registries):
        """local_storage_mult should be 0.2 at size 0.2 (linear)."""
        comp_entry = {
            "id": "resource_vault_metals",
            "modifiers": [{"id": "simple_size_mount", "value": 0.2}]
        }
        result = resolve_stat_from_size_mount(
            comp_entry, "local_storage_mult", fresh_registries
        )
        assert result == pytest.approx(0.2, rel=0.01)

    def test_production_rate_mult_at_0_5(self, fresh_registries):
        """production_rate_mult should be 0.5 at size 0.5."""
        comp_entry = {
            "id": "space_shipyard",
            "modifiers": [{"id": "simple_size_mount", "value": 0.5}]
        }
        result = resolve_stat_from_size_mount(
            comp_entry, "production_rate_mult", fresh_registries
        )
        assert result == pytest.approx(0.5, rel=0.01)

    def test_cost_mult_uses_nonlinear_formula(self, fresh_registries):
        """cost_mult should use param^0.75, not linear."""
        comp_entry = {
            "id": "metal_harvester",
            "modifiers": [{"id": "simple_size_mount", "value": 0.2}]
        }
        result = resolve_stat_from_size_mount(
            comp_entry, "cost_mult", fresh_registries
        )
        expected = 0.2 ** 0.75
        assert result == pytest.approx(expected, rel=0.01)

    def test_no_modifiers_returns_1(self, fresh_registries):
        """Should return 1.0 when no size_mount modifier."""
        comp_entry = {"id": "metal_harvester"}
        result = resolve_stat_from_size_mount(
            comp_entry, "harvest_rate_mult", fresh_registries
        )
        assert result == pytest.approx(1.0)
