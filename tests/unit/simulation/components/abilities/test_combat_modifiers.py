"""Tests for ShieldModifier, DamageModifier, and expanded ShieldProjection scopes."""
import pytest
from unittest.mock import MagicMock
from game.simulation.components.abilities.planetary import (
    ShieldModifierAbility,
    DamageModifierAbility,
)
from game.simulation.components.abilities.defense import ShieldProjection
from game.simulation.components.abilities.base import AbilityScope, AbilityLayer
from game.core.exceptions import ValidationException


class TestShieldModifierAbility:
    """Tests for ShieldModifierAbility."""

    def test_construction_from_dict(self):
        """Should parse multiplier, scope, and stack_group."""
        comp = MagicMock()
        data = {
            "multiplier": 0.75,
            "scope": "enemy_system",
            "stack_group": "shield_suppress_system",
        }
        ability = ShieldModifierAbility(comp, data)

        assert ability.multiplier == 0.75
        assert ability.scope == AbilityScope.ENEMY_SYSTEM
        assert ability.stack_group == "shield_suppress_system"

    def test_defaults(self):
        """Should default to 1.0 multiplier and allied_system scope."""
        comp = MagicMock()
        ability = ShieldModifierAbility(comp, {})

        assert ability.multiplier == 1.0
        assert ability.scope == AbilityScope.ALLIED_SYSTEM

    def test_layer_is_strategic(self):
        """Should be a strategic-layer ability."""
        comp = MagicMock()
        ability = ShieldModifierAbility(comp, {})
        assert ability.layer == AbilityLayer.STRATEGIC

    def test_allowed_scopes(self):
        """Should allow all combat-relevant strategic scopes."""
        comp = MagicMock()
        for scope in [
            "self", "fleet", "sector", "allied_sector", "player_sector",
            "enemy_sector", "system", "allied_system", "player_system",
            "enemy_system",
        ]:
            ability = ShieldModifierAbility(comp, {"scope": scope})
            assert ability.scope == AbilityScope(scope)

    def test_planet_scope_rejected(self):
        """Should reject planet scope."""
        comp = MagicMock()
        with pytest.raises(ValidationException):
            ShieldModifierAbility(comp, {"scope": "planet"})

    def test_empire_scope_rejected(self):
        """Should reject empire scope."""
        comp = MagicMock()
        with pytest.raises(ValidationException):
            ShieldModifierAbility(comp, {"scope": "empire"})

    def test_get_primary_value(self):
        """Primary value should be multiplier."""
        comp = MagicMock()
        ability = ShieldModifierAbility(comp, {"multiplier": 0.75})
        assert ability.get_primary_value() == 0.75

    def test_get_ui_rows(self):
        """Should show modifier value and scope."""
        comp = MagicMock()
        ability = ShieldModifierAbility(comp, {
            "multiplier": 1.25, "scope": "allied_system"
        })
        rows = ability.get_ui_rows()
        labels = [r['label'] for r in rows]
        assert 'Shield Modifier' in labels
        assert 'Scope' in labels

    def test_no_stat_bindings(self):
        """Strategic ability should have no stat bindings."""
        assert ShieldModifierAbility.STAT_BINDINGS == []


class TestDamageModifierAbility:
    """Tests for DamageModifierAbility."""

    def test_construction_from_dict(self):
        """Should parse multiplier, scope, and stack_group."""
        comp = MagicMock()
        data = {
            "multiplier": 1.50,
            "scope": "allied_sector",
            "stack_group": "damage_boost_sector",
        }
        ability = DamageModifierAbility(comp, data)

        assert ability.multiplier == 1.50
        assert ability.scope == AbilityScope.ALLIED_SECTOR
        assert ability.stack_group == "damage_boost_sector"

    def test_defaults(self):
        """Should default to 1.0 multiplier and allied_system scope."""
        comp = MagicMock()
        ability = DamageModifierAbility(comp, {})

        assert ability.multiplier == 1.0
        assert ability.scope == AbilityScope.ALLIED_SYSTEM

    def test_layer_is_strategic(self):
        """Should be a strategic-layer ability."""
        comp = MagicMock()
        ability = DamageModifierAbility(comp, {})
        assert ability.layer == AbilityLayer.STRATEGIC

    def test_allowed_scopes(self):
        """Should allow all combat-relevant strategic scopes."""
        comp = MagicMock()
        for scope in [
            "self", "fleet", "sector", "allied_sector", "player_sector",
            "enemy_sector", "system", "allied_system", "player_system",
            "enemy_system",
        ]:
            ability = DamageModifierAbility(comp, {"scope": scope})
            assert ability.scope == AbilityScope(scope)

    def test_planet_scope_rejected(self):
        """Should reject planet scope."""
        comp = MagicMock()
        with pytest.raises(ValidationException):
            DamageModifierAbility(comp, {"scope": "planet"})

    def test_get_primary_value(self):
        """Primary value should be multiplier."""
        comp = MagicMock()
        ability = DamageModifierAbility(comp, {"multiplier": 0.50})
        assert ability.get_primary_value() == 0.50

    def test_get_ui_rows(self):
        """Should show modifier value and scope."""
        comp = MagicMock()
        ability = DamageModifierAbility(comp, {
            "multiplier": 0.75, "scope": "enemy_system"
        })
        rows = ability.get_ui_rows()
        labels = [r['label'] for r in rows]
        assert 'Damage Modifier' in labels
        assert 'Scope' in labels

    def test_no_stat_bindings(self):
        """Strategic ability should have no stat bindings."""
        assert DamageModifierAbility.STAT_BINDINGS == []


class TestShieldProjectionExpandedScopes:
    """Tests for ShieldProjection with expanded strategic scopes."""

    def test_self_scope_still_works(self):
        """SELF scope should still be valid (combat use)."""
        comp = MagicMock()
        ability = ShieldProjection(comp, {"value": 100, "scope": "self"})
        assert ability.scope == AbilityScope.SELF

    def test_fleet_scope_allowed(self):
        """Should accept fleet scope."""
        comp = MagicMock()
        ability = ShieldProjection(comp, {"value": 100, "scope": "fleet"})
        assert ability.scope == AbilityScope.FLEET

    def test_allied_sector_scope_allowed(self):
        """Should accept allied_sector scope."""
        comp = MagicMock()
        ability = ShieldProjection(comp, {"value": 100, "scope": "allied_sector"})
        assert ability.scope == AbilityScope.ALLIED_SECTOR

    def test_allied_system_scope_allowed(self):
        """Should accept allied_system scope."""
        comp = MagicMock()
        ability = ShieldProjection(comp, {"value": 50, "scope": "allied_system"})
        assert ability.scope == AbilityScope.ALLIED_SYSTEM

    def test_player_sector_scope_allowed(self):
        """Should accept player_sector scope."""
        comp = MagicMock()
        ability = ShieldProjection(comp, {"value": 100, "scope": "player_sector"})
        assert ability.scope == AbilityScope.PLAYER_SECTOR

    def test_player_system_scope_allowed(self):
        """Should accept player_system scope."""
        comp = MagicMock()
        ability = ShieldProjection(comp, {"value": 50, "scope": "player_system"})
        assert ability.scope == AbilityScope.PLAYER_SYSTEM

    def test_enemy_system_scope_rejected(self):
        """Should reject enemy scopes (shield projection is friendly only)."""
        comp = MagicMock()
        with pytest.raises(ValidationException):
            ShieldProjection(comp, {"value": 50, "scope": "enemy_system"})

    def test_layer_is_both(self):
        """Should operate at both combat and strategic layers."""
        assert ShieldProjection.layer == AbilityLayer.BOTH
