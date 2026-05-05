"""Tests for new strategic abilities: GeologicStabilizer, ResourceHarvestBooster, BuildRateBooster."""
import pytest
from unittest.mock import MagicMock
from game.simulation.components.abilities.planetary import (
    GeologicStabilizerAbility,
    ResourceHarvestBoosterAbility,
    BuildRateBoosterAbility,
    EnvironmentalDamageAbility,
    FuelDrainAbility,
    StrategicSpeedModifierAbility,
    ThrustModifierAbility,
)
from game.simulation.components.abilities.base import AbilityLayer, AbilityScope
from game.core.exceptions import ValidationException


class TestGeologicStabilizerAbility:
    """Tests for GeologicStabilizerAbility."""

    def test_construction_from_dict(self):
        """Should parse all fields from dict data."""
        comp = MagicMock()
        data = {
            "energy_drain_rate": 30.0,
            "activation_time": 50,
            "deactivation_time": 10,
            "scope": "sector",
        }
        ability = GeologicStabilizerAbility(comp, data)

        assert ability.energy_drain_rate == 30.0
        assert ability.activation_time == 50
        assert ability.deactivation_time == 10
        assert ability.scope == AbilityScope.SECTOR

    def test_defaults_when_minimal_data(self):
        """Should use defaults when fields are missing."""
        comp = MagicMock()
        ability = GeologicStabilizerAbility(comp, {})

        assert ability.energy_drain_rate == 0.0
        assert ability.activation_time == 1
        assert ability.deactivation_time == 1
        assert ability.scope == AbilityScope.SECTOR  # default_scope

    def test_system_scope_allowed(self):
        """Should accept system scope."""
        comp = MagicMock()
        ability = GeologicStabilizerAbility(comp, {"scope": "system"})
        assert ability.scope == AbilityScope.SYSTEM

    def test_planet_scope_allowed(self):
        """Should accept planet scope."""
        comp = MagicMock()
        ability = GeologicStabilizerAbility(comp, {"scope": "planet"})
        assert ability.scope == AbilityScope.PLANET

    def test_invalid_scope_rejected(self):
        """Should reject scopes not in allowed_scopes."""
        comp = MagicMock()
        with pytest.raises(ValidationException):
            GeologicStabilizerAbility(comp, {"scope": "empire"})

    def test_get_primary_value(self):
        """Primary value should be energy drain rate."""
        comp = MagicMock()
        ability = GeologicStabilizerAbility(comp, {"energy_drain_rate": 25.0})
        assert ability.get_primary_value() == 25.0

    def test_get_ui_rows(self):
        """Should return UI rows for energy drain and scope."""
        comp = MagicMock()
        ability = GeologicStabilizerAbility(comp, {
            "energy_drain_rate": 25.0, "scope": "system"
        })
        rows = ability.get_ui_rows()
        assert len(rows) >= 2
        labels = [r['label'] for r in rows]
        assert 'Energy Drain' in labels
        assert 'Scope' in labels


class TestResourceHarvestBoosterAbility:
    """Tests for ResourceHarvestBoosterAbility."""

    def test_construction_from_dict(self):
        """Should parse resource_type and multiplier."""
        comp = MagicMock()
        data = {
            "resource_type": "metals",
            "multiplier": 1.5,
            "scope": "planet",
            "stack_group": "harvest_boost_metals",
        }
        ability = ResourceHarvestBoosterAbility(comp, data)

        assert ability.resource_type == "metals"
        assert ability.multiplier == 1.5
        assert ability.scope == AbilityScope.PLANET
        assert ability.stack_group == "harvest_boost_metals"

    def test_defaults(self):
        """Should default to empty resource and 1.0 multiplier."""
        comp = MagicMock()
        ability = ResourceHarvestBoosterAbility(comp, {})

        assert ability.resource_type == ""
        assert ability.multiplier == 1.0

    def test_all_scopes_allowed(self):
        """Should allow SELF, PLANET, SECTOR, SYSTEM, EMPIRE, ALLIED_EMPIRE."""
        comp = MagicMock()
        for scope in ["self", "planet", "sector", "system", "empire", "allied_empire"]:
            ability = ResourceHarvestBoosterAbility(comp, {"scope": scope})
            assert ability.scope == AbilityScope(scope)

    def test_get_primary_value(self):
        """Primary value should be multiplier."""
        comp = MagicMock()
        ability = ResourceHarvestBoosterAbility(comp, {"multiplier": 1.5})
        assert ability.get_primary_value() == 1.5

    def test_get_ui_rows(self):
        """Should show resource type and multiplier."""
        comp = MagicMock()
        ability = ResourceHarvestBoosterAbility(comp, {
            "resource_type": "metals", "multiplier": 1.5
        })
        rows = ability.get_ui_rows()
        labels = [r['label'] for r in rows]
        assert 'Resource' in labels
        assert 'Boost' in labels


class TestBuildRateBoosterAbility:
    """Tests for BuildRateBoosterAbility."""

    def test_construction_from_dict(self):
        """Should parse multiplier and scope."""
        comp = MagicMock()
        data = {"multiplier": 1.25, "scope": "sector"}
        ability = BuildRateBoosterAbility(comp, data)

        assert ability.multiplier == 1.25
        assert ability.scope == AbilityScope.SECTOR

    def test_defaults(self):
        """Should default to 1.0 multiplier and sector scope."""
        comp = MagicMock()
        ability = BuildRateBoosterAbility(comp, {})
        assert ability.multiplier == 1.0
        assert ability.scope == AbilityScope.SECTOR

    def test_all_scopes_allowed(self):
        """Should allow all strategic scopes."""
        comp = MagicMock()
        for scope in ["self", "planet", "sector", "system", "empire", "allied_empire"]:
            ability = BuildRateBoosterAbility(comp, {"scope": scope})
            assert ability.scope == AbilityScope(scope)

    def test_get_primary_value(self):
        """Primary value should be multiplier."""
        comp = MagicMock()
        ability = BuildRateBoosterAbility(comp, {"multiplier": 1.25})
        assert ability.get_primary_value() == 1.25

    def test_get_ui_rows(self):
        """Should show multiplier and scope."""
        comp = MagicMock()
        ability = BuildRateBoosterAbility(comp, {"multiplier": 1.25, "scope": "sector"})
        rows = ability.get_ui_rows()
        labels = [r['label'] for r in rows]
        assert 'Build Rate' in labels
        assert 'Scope' in labels


class TestProj300SectorSystemAbilities:
    """Tests for PROJ-300 strategic sector/system effect abilities."""

    @pytest.mark.parametrize(
        "ability_cls,data,attr,expected,label,value_fragment",
        [
            (
                ThrustModifierAbility,
                {"multiplier": 0.6, "scope": "system"},
                "multiplier",
                0.6,
                "Thrust Modifier",
                "0.60x",
            ),
            (
                StrategicSpeedModifierAbility,
                {"multiplier": 0.4, "scope": "enemy_sector"},
                "multiplier",
                0.4,
                "Strategic Speed",
                "0.40x",
            ),
            (
                EnvironmentalDamageAbility,
                {"rate": 1.25, "damage_type": "radiation", "scope": "sector"},
                "rate",
                1.25,
                "Damage (radiation)",
                "-1.25 hull/turn",
            ),
            (
                FuelDrainAbility,
                {"rate": 0.75, "scope": "allied_system"},
                "rate",
                0.75,
                "Fuel Drain",
                "-0.75/turn",
            ),
        ],
    )
    def test_parse_dict_primary_value_and_ui_rows(
        self,
        ability_cls,
        data,
        attr,
        expected,
        label,
        value_fragment,
    ):
        comp = MagicMock()

        ability = ability_cls(comp, data)
        rows = ability.get_ui_rows()

        assert ability.layer == AbilityLayer.STRATEGIC
        assert getattr(ability, attr) == expected
        assert ability.get_primary_value() == expected
        assert any(
            row["label"] == label and value_fragment in row["value"]
            for row in rows
        )
        assert any(row["label"] == "Scope" for row in rows)

    @pytest.mark.parametrize(
        "ability_cls,attr,default_value",
        [
            (ThrustModifierAbility, "multiplier", 1.0),
            (StrategicSpeedModifierAbility, "multiplier", 1.0),
            (EnvironmentalDamageAbility, "rate", 0.0),
            (FuelDrainAbility, "rate", 0.0),
        ],
    )
    def test_non_dict_data_uses_defaults(self, ability_cls, attr, default_value):
        comp = MagicMock()

        ability = ability_cls(comp, True)

        assert getattr(ability, attr) == default_value
        assert ability.scope == AbilityScope.SECTOR

    def test_environmental_damage_non_dict_defaults_damage_type(self):
        comp = MagicMock()

        ability = EnvironmentalDamageAbility(comp, True)

        assert ability.damage_type == "environmental"
