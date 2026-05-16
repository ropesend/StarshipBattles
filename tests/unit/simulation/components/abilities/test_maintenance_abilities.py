"""
Unit tests for the Maintenance abstraction (QA Observation 5).

Covers ``RequiresMaintenanceAbility`` (renamed from ``CrewRequired``) and the
new ``ProvidesMaintenanceAbility``. The abilities are registry-resolved via
keys ``"RequiresMaintenance"`` and ``"ProvidesMaintenance"``.
"""
from __future__ import annotations

import math
from unittest.mock import MagicMock

import pytest

from game.simulation.components.abilities import (
    ABILITY_REGISTRY,
    create_ability,
)
from game.simulation.components.abilities.crew import (
    RequiresMaintenance,
    ProvidesMaintenance,
)
# Aliases preserved for legacy test naming; the canonical names are above.
RequiresMaintenanceAbility = RequiresMaintenance
ProvidesMaintenanceAbility = ProvidesMaintenance
from game.simulation.components.abilities.stat_keys import StatKey


@pytest.fixture
def mock_component():
    """Component with default empty stats."""
    component = MagicMock()
    component.stats = {}
    component.ability_stats = {}
    return component


@pytest.fixture
def component_factory():
    def _make(stats=None, ability_stats=None):
        component = MagicMock()
        component.stats = stats or {}
        component.ability_stats = ability_stats or {}
        return component
    return _make


class TestRequiresMaintenanceRegistration:
    """The ability is registered under the new key and constructible via the registry."""

    def test_registry_has_requires_maintenance_key(self) -> None:
        assert "RequiresMaintenance" in ABILITY_REGISTRY
        assert ABILITY_REGISTRY["RequiresMaintenance"] is RequiresMaintenanceAbility

    def test_registry_does_not_have_crew_required_legacy_key(self) -> None:
        assert "CrewRequired" not in ABILITY_REGISTRY

    def test_create_ability_via_registry(self, mock_component) -> None:
        ability = create_ability("RequiresMaintenance", mock_component, 5)
        assert ability is not None
        assert isinstance(ability, RequiresMaintenanceAbility)
        assert ability.amount == 5


class TestRequiresMaintenance:
    """Same data semantics as the old CrewRequired class."""

    def test_init_with_numeric_value(self, mock_component) -> None:
        ability = RequiresMaintenanceAbility(mock_component, 5)
        assert ability.amount == 5
        assert ability._base_amount == 5

    def test_init_with_dict_value_key(self, mock_component) -> None:
        ability = RequiresMaintenanceAbility(mock_component, {"value": 8})
        assert ability.amount == 8

    def test_init_with_dict_amount_key(self, mock_component) -> None:
        ability = RequiresMaintenanceAbility(mock_component, {"amount": 12})
        assert ability.amount == 12

    def test_recalculate_with_mass_mult(self, component_factory) -> None:
        comp = component_factory(stats={"mass_mult": 4.0})
        ability = RequiresMaintenanceAbility(comp, 5)
        ability.recalculate()
        # sqrt(4.0) = 2.0, 5 * 2.0 = 10
        assert ability.amount == 10

    def test_get_primary_value(self, mock_component) -> None:
        ability = RequiresMaintenanceAbility(mock_component, 7)
        assert ability.get_primary_value() == 7.0


class TestProvidesMaintenanceRegistration:
    def test_registry_has_provides_maintenance_key(self) -> None:
        assert "ProvidesMaintenance" in ABILITY_REGISTRY
        assert ABILITY_REGISTRY["ProvidesMaintenance"] is ProvidesMaintenanceAbility

    def test_create_ability_via_registry(self, mock_component) -> None:
        ability = create_ability("ProvidesMaintenance", mock_component, 25)
        assert ability is not None
        assert isinstance(ability, ProvidesMaintenanceAbility)
        assert ability.amount == 25


class TestProvidesMaintenance:
    def test_init_with_numeric_value(self, mock_component) -> None:
        ability = ProvidesMaintenanceAbility(mock_component, 10)
        assert ability.amount == 10

    def test_init_with_dict_value_key(self, mock_component) -> None:
        ability = ProvidesMaintenanceAbility(mock_component, {"value": 25})
        assert ability.amount == 25

    def test_init_with_default_zero(self, mock_component) -> None:
        # Mirror CrewCapacity behavior: dicts without 'value' default to zero.
        ability = ProvidesMaintenanceAbility(mock_component, {"other": "ignored"})
        assert ability.amount == 0

    def test_get_primary_value(self, mock_component) -> None:
        ability = ProvidesMaintenanceAbility(mock_component, 30)
        assert ability.get_primary_value() == 30.0


class TestProvidesMaintenanceAggregatesAdditively:
    """ProvidesMaintenance values should sum across components in calculate_ability_totals."""

    def test_two_providers_sum(self) -> None:
        from game.simulation.entities.ability_aggregator import calculate_ability_totals

        # Two distinct components, each providing maintenance, no stack_group.
        comp1 = MagicMock()
        comp1.abilities = {}
        ab1 = MagicMock()
        ab1.__class__ = ProvidesMaintenanceAbility
        ab1.get_primary_value.return_value = 10.0
        ab1.stack_group = None
        comp1.ability_instances = [ab1]

        comp2 = MagicMock()
        comp2.abilities = {}
        ab2 = MagicMock()
        ab2.__class__ = ProvidesMaintenanceAbility
        ab2.get_primary_value.return_value = 25.0
        ab2.stack_group = None
        comp2.ability_instances = [ab2]

        totals = calculate_ability_totals([comp1, comp2])
        assert totals.get("ProvidesMaintenanceAbility", 0) == 35.0 or \
               totals.get("ProvidesMaintenance", 0) == 35.0
