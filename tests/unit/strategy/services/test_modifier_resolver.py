"""Tests for modifier_resolver - extracts size_mount scaling from design_data components.

Phase 2: Runtime modifier resolution for strategic ability scaling.
"""
import pytest
from game.strategy.services.modifier_resolver import (
    resolve_size_multiplier,
    resolve_stat_from_size_mount,
)


class TestResolveSizeMultiplier:
    """Test extracting size_mount value from component entries.

    PROJ-323 Task 3.33: 7 resolve_size_multiplier tests parametrized.
    """

    @pytest.mark.parametrize("comp_entry,expected", [
        pytest.param(
            {"id": "metal_harvester", "modifiers": [{"id": "simple_size_mount", "value": 0.2}]},
            0.2,
            id="size_mount_0_2",
        ),
        pytest.param(
            {"id": "metal_harvester", "modifiers": [{"id": "simple_size_mount", "value": 1.0}]},
            1.0,
            id="size_mount_1_0",
        ),
        pytest.param(
            {"id": "metal_harvester"},
            1.0,
            id="no_modifiers_key",
        ),
        pytest.param(
            {"id": "metal_harvester", "modifiers": []},
            1.0,
            id="empty_modifiers_list",
        ),
        pytest.param(
            {"id": "railgun", "modifiers": [{"id": "hardened_mount", "value": 2.0}]},
            1.0,
            id="other_modifiers_only",
        ),
        pytest.param(
            "metal_harvester",
            1.0,
            id="string_entry",
        ),
        pytest.param(
            {
                "id": "metal_harvester",
                "modifiers": [
                    {"id": "hardened_mount", "value": 1.5},
                    {"id": "simple_size_mount", "value": 0.5},
                ],
            },
            0.5,
            id="multiple_modifiers",
        ),
    ])
    def test_resolve_size_multiplier(self, fresh_registries, comp_entry, expected):
        """resolve_size_multiplier extracts simple_size_mount value or returns 1.0 default."""
        result = resolve_size_multiplier(comp_entry)
        assert result == pytest.approx(expected)


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
