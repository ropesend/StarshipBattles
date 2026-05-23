"""Tests for colony_has_planetary_yard() registry lookup path.

Regression tests for the crash at strategy_detail_formatter.py:326 where
DefaultRegistryProvider was passed instead of GameRegistries.

Critical: These tests exercise Path B (registry lookup), which is the path
real gameplay ALWAYS uses. Design JSONs store component IDs without inline
abilities, so the function MUST look up abilities via registries.components.
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.planetary_facility import PlanetaryFacility
from game.strategy.data.build_queue_source import colony_has_planetary_yard


def _make_facility_registry_only(comp_id="planetary_yard_module", is_operational=True):
    """Create a facility with component ID only — no inline abilities.

    This matches real gameplay: design JSONs store {"id": "..."} without
    an "abilities" key. Abilities are only in the component registry.
    """
    return PlanetaryFacility(
        instance_id="yard_1",
        design_id="colony_hub",
        name="Colony Hub",
        design_data={
            "layers": {"CORE": [{"id": comp_id}]}
        },
        is_operational=is_operational,
    )


def _make_facility_inline_abilities():
    """Create a facility with inline abilities (test-only pattern)."""
    return PlanetaryFacility(
        instance_id="yard_1",
        design_id="colony_hub",
        name="Colony Hub",
        design_data={
            "layers": {"CORE": [{"id": "hub", "abilities": {"PlanetaryYard": True}}]}
        },
    )


class TestColonyYardRegistryLookup:
    """Tests for Path B: finding PlanetaryYard via registries.components."""

    def test_finds_yard_via_registry_lookup(self, fresh_registries):
        """With real registries, finds PlanetaryYard through component lookup."""
        colony = MagicMock()
        colony.facilities = [_make_facility_registry_only("planetary_yard_module")]

        result = colony_has_planetary_yard(colony, fresh_registries)
        assert result is True

    def test_no_registries_misses_registry_components(self):
        """Without registries, cannot find PlanetaryYard that's only in registry."""
        colony = MagicMock()
        colony.facilities = [_make_facility_registry_only("planetary_yard_module")]

        result = colony_has_planetary_yard(colony, registries=None)
        assert result is False

    def test_inline_abilities_work_without_registries(self):
        """Inline abilities (Path A) still work without registries."""
        colony = MagicMock()
        colony.facilities = [_make_facility_inline_abilities()]

        result = colony_has_planetary_yard(colony, registries=None)
        assert result is True

    def test_non_yard_component_returns_false(self, fresh_registries):
        """Component without PlanetaryYard ability returns False."""
        colony = MagicMock()
        colony.facilities = [_make_facility_registry_only("crew_quarters")]

        result = colony_has_planetary_yard(colony, fresh_registries)
        assert result is False

    def test_empty_facilities_returns_false(self, fresh_registries):
        """Colony with no facilities returns False."""
        colony = MagicMock()
        colony.facilities = []

        result = colony_has_planetary_yard(colony, fresh_registries)
        assert result is False

    def test_crashes_with_default_registry_provider(self):
        """Reproduces the crash: passing DefaultRegistryProvider instead of GameRegistries.

        This is the exact bug from strategy_detail_formatter.py:326.
        After the fix, this test should pass (provider should NOT be passed directly).
        """
        from game.core.registry import get_default_registry_provider

        colony = MagicMock()
        colony.facilities = [_make_facility_registry_only("planetary_yard_module")]

        provider = get_default_registry_provider()
        # This should NOT crash — but currently does because DefaultRegistryProvider
        # has get_components() not .components
        with pytest.raises(AttributeError, match="components"):
            colony_has_planetary_yard(colony, provider)
