"""Tests for GravityModifier, WaterModifier, and RadiationShield abilities."""
import pytest
from unittest.mock import MagicMock
from game.simulation.components.abilities.planetary import (
    GravityModifierAbility,
    WaterModifierAbility,
    RadiationShieldAbility,
)
from game.simulation.components.abilities.base import AbilityScope, AbilityLayer
from game.core.exceptions import ValidationException


class TestGravityModifierAbility:
    """Tests for GravityModifierAbility (activatable, reverts on deactivation)."""

    def test_construction_from_dict(self):
        """Should parse all activatable fields."""
        comp = MagicMock()
        data = {
            "energy_drain_rate": 30.0,
            "activation_time": 15,
            "deactivation_time": 5,
        }
        ability = GravityModifierAbility(comp, data)

        assert ability.energy_drain_rate == 30.0
        assert ability.activation_time == 15
        assert ability.deactivation_time == 5

    def test_defaults(self):
        """Should use sensible defaults."""
        comp = MagicMock()
        ability = GravityModifierAbility(comp, {})

        assert ability.energy_drain_rate == 0.0
        assert ability.activation_time == 1
        assert ability.deactivation_time == 1
        assert ability.scope == AbilityScope.SELF

    def test_layer_is_strategic(self):
        """Should be a strategic-layer ability."""
        comp = MagicMock()
        ability = GravityModifierAbility(comp, {})
        assert ability.layer == AbilityLayer.STRATEGIC

    def test_only_self_scope_allowed(self):
        """Should only allow SELF scope."""
        comp = MagicMock()
        ability = GravityModifierAbility(comp, {"scope": "self"})
        assert ability.scope == AbilityScope.SELF

    def test_system_scope_rejected(self):
        """Should reject non-SELF scopes."""
        comp = MagicMock()
        with pytest.raises(ValidationException):
            GravityModifierAbility(comp, {"scope": "system"})

    def test_get_primary_value(self):
        """Primary value should be energy drain rate."""
        comp = MagicMock()
        ability = GravityModifierAbility(comp, {"energy_drain_rate": 30.0})
        assert ability.get_primary_value() == 30.0

    def test_get_ui_rows(self):
        """Should show energy drain and activation time."""
        comp = MagicMock()
        ability = GravityModifierAbility(comp, {
            "energy_drain_rate": 30.0, "activation_time": 15
        })
        rows = ability.get_ui_rows()
        labels = [r['label'] for r in rows]
        assert 'Energy Drain' in labels
        assert 'Activation' in labels

    def test_no_stat_bindings(self):
        """Should have no stat bindings."""
        assert GravityModifierAbility.STAT_BINDINGS == []


class TestWaterModifierAbility:
    """Tests for WaterModifierAbility (passive, gradual, permanent)."""

    def test_construction_from_dict(self):
        """Should parse modification_rate."""
        comp = MagicMock()
        data = {"modification_rate": 0.005}
        ability = WaterModifierAbility(comp, data)
        assert ability.modification_rate == 0.005

    def test_defaults(self):
        """Should default to 0.0 rate."""
        comp = MagicMock()
        ability = WaterModifierAbility(comp, {})
        assert ability.modification_rate == 0.0
        assert ability.scope == AbilityScope.SELF

    def test_layer_is_strategic(self):
        """Should be a strategic-layer ability."""
        comp = MagicMock()
        ability = WaterModifierAbility(comp, {})
        assert ability.layer == AbilityLayer.STRATEGIC

    def test_only_self_scope_allowed(self):
        """Should only allow SELF scope."""
        comp = MagicMock()
        ability = WaterModifierAbility(comp, {"scope": "self"})
        assert ability.scope == AbilityScope.SELF

    def test_system_scope_rejected(self):
        """Should reject non-SELF scopes."""
        comp = MagicMock()
        with pytest.raises(ValidationException):
            WaterModifierAbility(comp, {"scope": "system"})

    def test_get_primary_value(self):
        """Primary value should be modification_rate."""
        comp = MagicMock()
        ability = WaterModifierAbility(comp, {"modification_rate": 0.005})
        assert ability.get_primary_value() == 0.005

    def test_get_ui_rows(self):
        """Should show modification rate."""
        comp = MagicMock()
        ability = WaterModifierAbility(comp, {"modification_rate": 0.005})
        rows = ability.get_ui_rows()
        labels = [r['label'] for r in rows]
        assert 'Modification Rate' in labels

    def test_no_stat_bindings(self):
        """Should have no stat bindings."""
        assert WaterModifierAbility.STAT_BINDINGS == []


class TestRadiationShieldAbility:
    """Tests for RadiationShieldAbility (activatable, reverts on deactivation)."""

    def test_construction_from_dict(self):
        """Should parse activatable fields and max_shielding."""
        comp = MagicMock()
        data = {
            "energy_drain_rate": 20.0,
            "activation_time": 15,
            "deactivation_time": 5,
            "max_shielding": 1.5,
        }
        ability = RadiationShieldAbility(comp, data)

        assert ability.energy_drain_rate == 20.0
        assert ability.activation_time == 15
        assert ability.deactivation_time == 5
        assert ability.max_shielding == 1.5

    def test_defaults(self):
        """Should use sensible defaults."""
        comp = MagicMock()
        ability = RadiationShieldAbility(comp, {})

        assert ability.energy_drain_rate == 0.0
        assert ability.activation_time == 1
        assert ability.deactivation_time == 1
        assert ability.max_shielding == 1.0
        assert ability.scope == AbilityScope.SELF

    def test_layer_is_strategic(self):
        """Should be a strategic-layer ability."""
        comp = MagicMock()
        ability = RadiationShieldAbility(comp, {})
        assert ability.layer == AbilityLayer.STRATEGIC

    def test_only_self_scope_allowed(self):
        """Should only allow SELF scope."""
        comp = MagicMock()
        ability = RadiationShieldAbility(comp, {"scope": "self"})
        assert ability.scope == AbilityScope.SELF

    def test_system_scope_rejected(self):
        """Should reject non-SELF scopes."""
        comp = MagicMock()
        with pytest.raises(ValidationException):
            RadiationShieldAbility(comp, {"scope": "system"})

    def test_get_primary_value(self):
        """Primary value should be energy drain rate."""
        comp = MagicMock()
        ability = RadiationShieldAbility(comp, {"energy_drain_rate": 20.0})
        assert ability.get_primary_value() == 20.0

    def test_get_ui_rows(self):
        """Should show energy drain, shielding, and activation time."""
        comp = MagicMock()
        ability = RadiationShieldAbility(comp, {
            "energy_drain_rate": 20.0, "max_shielding": 1.0, "activation_time": 15
        })
        rows = ability.get_ui_rows()
        labels = [r['label'] for r in rows]
        assert 'Energy Drain' in labels
        assert 'Max Shielding' in labels
        assert 'Activation' in labels

    def test_no_stat_bindings(self):
        """Should have no stat bindings."""
        assert RadiationShieldAbility.STAT_BINDINGS == []
