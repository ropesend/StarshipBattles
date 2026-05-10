"""Tests for StellarStabilizer and WarpFieldStabilizer abilities."""
import pytest
from unittest.mock import MagicMock
from game.simulation.components.abilities.planetary import (
    StellarStabilizerAbility,
    WarpFieldStabilizerAbility,
)
from game.simulation.components.abilities.base import AbilityScope
from game.core.exceptions import ValidationException


# PROJ-323 Task 3.16: Stellar/Warp Stabilizer near-identical test classes
# collapsed into one parametrized class.
@pytest.mark.parametrize(
    "ability_cls,drain,activation,deactivation",
    [
        pytest.param(StellarStabilizerAbility, 250.0, 100, 20, id="StellarStabilizer"),
        pytest.param(WarpFieldStabilizerAbility, 150.0, 75, 15, id="WarpFieldStabilizer"),
    ],
)
class TestStabilizerAbility:
    """Tests for StellarStabilizer and WarpFieldStabilizer abilities."""

    def test_construction_from_dict(self, ability_cls, drain, activation, deactivation):
        comp = MagicMock()
        data = {
            "energy_drain_rate": drain,
            "activation_time": activation,
            "deactivation_time": deactivation,
            "scope": "system",
        }
        ability = ability_cls(comp, data)

        assert ability.energy_drain_rate == drain
        assert ability.activation_time == activation
        assert ability.deactivation_time == deactivation
        assert ability.scope == AbilityScope.SYSTEM

    def test_defaults(self, ability_cls, drain, activation, deactivation):
        comp = MagicMock()
        ability = ability_cls(comp, {})
        assert ability.energy_drain_rate == 0.0
        assert ability.scope == AbilityScope.SYSTEM  # default_scope

    def test_sector_scope_allowed(self, ability_cls, drain, activation, deactivation):
        comp = MagicMock()
        ability = ability_cls(comp, {"scope": "sector"})
        assert ability.scope == AbilityScope.SECTOR

    def test_planet_scope_rejected(self, ability_cls, drain, activation, deactivation):
        comp = MagicMock()
        with pytest.raises(ValidationException):
            ability_cls(comp, {"scope": "planet"})

    def test_get_primary_value(self, ability_cls, drain, activation, deactivation):
        comp = MagicMock()
        ability = ability_cls(comp, {"energy_drain_rate": drain})
        assert ability.get_primary_value() == drain

    def test_get_ui_rows(self, ability_cls, drain, activation, deactivation):
        comp = MagicMock()
        ability = ability_cls(comp, {
            "energy_drain_rate": drain, "scope": "system"
        })
        rows = ability.get_ui_rows()
        labels = [r['label'] for r in rows]
        assert 'Energy Drain' in labels
        assert 'Scope' in labels
