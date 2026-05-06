"""Tests for ability package registry helpers."""
import logging

import pytest

from game.simulation.components.abilities import (
    ABILITY_REGISTRY,
    _contains_unevaluated_formula,
    get_ability_default_scope,
)
from game.simulation.components.abilities.base import AbilityScope


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param("=ship_class_mass", True, id="formula-string"),
        pytest.param("ship_class_mass", False, id="non-formula-string"),
        pytest.param(
            {"outer": [{"inner": "plain"}, {"amount": "=ceil(ship_class_mass)"}]},
            True,
            id="nested-dict-list-formula",
        ),
        pytest.param(
            {
                "empty_dict": {},
                "empty_list": [],
                "number": 10,
                "flag": True,
                "none": None,
                "strings": ["plain", ""],
            },
            False,
            id="mixed-primitives-empty-data",
        ),
    ],
)
def test_contains_unevaluated_formula_detects_recursive_formula_data(data, expected) -> None:
    assert _contains_unevaluated_formula(data) is expected


def test_get_ability_default_scope_uses_class_enum_default() -> None:
    """Strategic abilities can declare non-self defaults via AbilityScope enums."""
    assert get_ability_default_scope("ShieldModifier") == AbilityScope.ALLIED_SYSTEM.value


def test_get_ability_default_scope_defaults_to_self_for_base_ability() -> None:
    assert get_ability_default_scope("WeaponAbility") == AbilityScope.SELF.value


def test_get_ability_default_scope_defaults_to_self_when_entry_has_no_default() -> None:
    """The Armor registry entry is a lambda and has no class default_scope."""
    assert get_ability_default_scope("Armor") == AbilityScope.SELF.value


def test_get_ability_default_scope_string_default(monkeypatch) -> None:
    """Non-enum default_scope values are stringified for registry consumers."""

    class StringDefaultScopeAbility:
        default_scope = "sector"

    monkeypatch.setitem(ABILITY_REGISTRY, "StringDefaultScope", StringDefaultScopeAbility)

    assert get_ability_default_scope("StringDefaultScope") == "sector"


def test_get_ability_default_scope_unknown_logs_and_defaults_to_self(caplog) -> None:
    caplog.set_level(logging.WARNING, logger="game.simulation.components.abilities")

    assert get_ability_default_scope("MissingAbility") == AbilityScope.SELF.value
    assert "MissingAbility" in caplog.text
