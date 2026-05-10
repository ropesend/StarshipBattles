"""Tests for AtmosphereModifier and QualityImprovement abilities."""
import pytest
from unittest.mock import MagicMock
from game.simulation.components.abilities.planetary import (
    AtmosphereModifierAbility,
    QualityImprovementAbility,
)
from game.simulation.components.abilities.base import AbilityScope


class TestAtmosphereModifierAbility:

    def test_construction_from_dict(self):
        comp = MagicMock()
        data = {"modification_rate": 1e12}
        ability = AtmosphereModifierAbility(comp, data)
        assert ability.modification_rate == 1e12

    def test_defaults(self):
        comp = MagicMock()
        ability = AtmosphereModifierAbility(comp, {})
        assert ability.modification_rate == 0.0
        assert ability.scope == AbilityScope.SELF

    def test_get_primary_value(self):
        comp = MagicMock()
        ability = AtmosphereModifierAbility(comp, {"modification_rate": 1e12})
        assert ability.get_primary_value() == 1e12

    def test_get_ui_rows(self):
        comp = MagicMock()
        ability = AtmosphereModifierAbility(comp, {"modification_rate": 1e12})
        rows = ability.get_ui_rows()
        labels = [r['label'] for r in rows]
        assert 'Modification Rate' in labels


class TestQualityImprovementAbility:

    def test_construction_from_dict(self):
        comp = MagicMock()
        data = {"resource_type": "metals", "improvement_rate": 0.1}
        ability = QualityImprovementAbility(comp, data)
        assert ability.resource_type == "metals"
        assert ability.improvement_rate == 0.1

    def test_defaults(self):
        comp = MagicMock()
        ability = QualityImprovementAbility(comp, {})
        assert ability.resource_type == ""
        assert ability.improvement_rate == 0.0
        assert ability.scope == AbilityScope.SELF

    def test_get_primary_value(self):
        comp = MagicMock()
        ability = QualityImprovementAbility(comp, {"improvement_rate": 0.1})
        assert ability.get_primary_value() == 0.1

    def test_get_ui_rows(self):
        comp = MagicMock()
        ability = QualityImprovementAbility(comp, {
            "resource_type": "metals", "improvement_rate": 0.1
        })
        rows = ability.get_ui_rows()
        labels = [r['label'] for r in rows]
        assert 'Resource' in labels
        assert 'Improvement' in labels
