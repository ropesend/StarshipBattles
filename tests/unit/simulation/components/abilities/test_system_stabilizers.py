"""Tests for StellarStabilizer and WarpFieldStabilizer abilities."""
import pytest
from unittest.mock import MagicMock
from game.simulation.components.abilities.planetary import (
    StellarStabilizerAbility,
    WarpFieldStabilizerAbility,
)
from game.simulation.components.abilities.base import AbilityScope
from game.core.exceptions import ValidationException


class TestStellarStabilizerAbility:
    """Tests for StellarStabilizerAbility."""

    def test_construction_from_dict(self):
        comp = MagicMock()
        data = {
            "energy_drain_rate": 250.0,
            "activation_time": 100,
            "deactivation_time": 20,
            "scope": "system",
        }
        ability = StellarStabilizerAbility(comp, data)

        assert ability.energy_drain_rate == 250.0
        assert ability.activation_time == 100
        assert ability.deactivation_time == 20
        assert ability.scope == AbilityScope.SYSTEM

    def test_defaults(self):
        comp = MagicMock()
        ability = StellarStabilizerAbility(comp, {})
        assert ability.energy_drain_rate == 0.0
        assert ability.scope == AbilityScope.SYSTEM  # default_scope

    def test_sector_scope_allowed(self):
        comp = MagicMock()
        ability = StellarStabilizerAbility(comp, {"scope": "sector"})
        assert ability.scope == AbilityScope.SECTOR

    def test_planet_scope_rejected(self):
        comp = MagicMock()
        with pytest.raises(ValidationException):
            StellarStabilizerAbility(comp, {"scope": "planet"})

    def test_get_primary_value(self):
        comp = MagicMock()
        ability = StellarStabilizerAbility(comp, {"energy_drain_rate": 250.0})
        assert ability.get_primary_value() == 250.0

    def test_get_ui_rows(self):
        comp = MagicMock()
        ability = StellarStabilizerAbility(comp, {
            "energy_drain_rate": 250.0, "scope": "system"
        })
        rows = ability.get_ui_rows()
        labels = [r['label'] for r in rows]
        assert 'Energy Drain' in labels
        assert 'Scope' in labels


class TestWarpFieldStabilizerAbility:
    """Tests for WarpFieldStabilizerAbility."""

    def test_construction_from_dict(self):
        comp = MagicMock()
        data = {
            "energy_drain_rate": 150.0,
            "activation_time": 75,
            "deactivation_time": 15,
            "scope": "system",
        }
        ability = WarpFieldStabilizerAbility(comp, data)

        assert ability.energy_drain_rate == 150.0
        assert ability.activation_time == 75
        assert ability.deactivation_time == 15
        assert ability.scope == AbilityScope.SYSTEM

    def test_defaults(self):
        comp = MagicMock()
        ability = WarpFieldStabilizerAbility(comp, {})
        assert ability.energy_drain_rate == 0.0
        assert ability.scope == AbilityScope.SYSTEM

    def test_sector_scope_allowed(self):
        comp = MagicMock()
        ability = WarpFieldStabilizerAbility(comp, {"scope": "sector"})
        assert ability.scope == AbilityScope.SECTOR

    def test_planet_scope_rejected(self):
        comp = MagicMock()
        with pytest.raises(ValidationException):
            WarpFieldStabilizerAbility(comp, {"scope": "planet"})

    def test_get_primary_value(self):
        comp = MagicMock()
        ability = WarpFieldStabilizerAbility(comp, {"energy_drain_rate": 150.0})
        assert ability.get_primary_value() == 150.0

    def test_get_ui_rows(self):
        comp = MagicMock()
        ability = WarpFieldStabilizerAbility(comp, {
            "energy_drain_rate": 150.0, "scope": "system"
        })
        rows = ability.get_ui_rows()
        labels = [r['label'] for r in rows]
        assert 'Energy Drain' in labels
        assert 'Scope' in labels
