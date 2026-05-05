"""Tests for declarative builder stat definitions."""
from __future__ import annotations

from types import SimpleNamespace

from game.ui.screens.builder.stat_definitions import SectionDefinition, StatDefinition


def test_stat_definition_defaults_key_and_attr_key_from_id() -> None:
    stat = StatDefinition(id="mass", label="Mass")
    ship = SimpleNamespace(mass=123)

    assert stat.key == "mass"
    assert stat.attr_key == "mass"
    assert stat.get_value(ship) == 123


def test_stat_definition_uses_explicit_attr_key_and_missing_attrs_return_zero() -> None:
    stat = StatDefinition(id="display_mass", label="Mass", key="mass")
    ship = SimpleNamespace(mass=123)

    assert stat.get_value(ship) == 123
    assert StatDefinition(id="missing", label="Missing").get_value(ship) == 0


def test_get_value_supports_callable_and_named_getters() -> None:
    ship = SimpleNamespace(mass=100, get_double=lambda: 200)
    callable_stat = StatDefinition(
        id="callable",
        label="Callable",
        getter=lambda item: item.mass * 3,
    )
    named_stat = StatDefinition(id="named", label="Named", getter="get_double")

    assert callable_stat.get_value(ship) == 300
    assert named_stat.get_value(ship) == ship.get_double


def test_format_value_supports_format_strings_and_callables() -> None:
    decimal_stat = StatDefinition(id="mass", label="Mass", formatter="{:.1f}")
    callable_stat = StatDefinition(id="flag", label="Flag", formatter=lambda value: f"x{value}")

    assert decimal_stat.format_value(12.25) == "12.2"
    assert callable_stat.format_value(3) == "x3"


def test_get_display_unit_supports_static_and_callable_units() -> None:
    static_unit = StatDefinition(id="mass", label="Mass", unit="kg")
    callable_unit = StatDefinition(
        id="mass_ratio",
        label="Mass",
        unit=lambda ship, value: f"/ {ship.max_mass}",
    )
    ship = SimpleNamespace(max_mass=500)

    assert static_unit.get_display_unit(ship, 100) == "kg"
    assert callable_unit.get_display_unit(ship, 100) == "/ 500"


def test_get_status_uses_validator_or_default_ok_status() -> None:
    default_stat = StatDefinition(id="mass", label="Mass")
    validated_stat = StatDefinition(
        id="mass",
        label="Mass",
        validator=lambda ship, value: (value <= ship.max_mass, "ok"),
    )
    ship = SimpleNamespace(max_mass=100)

    assert default_stat.get_status(ship, 500) == (True, "")
    assert validated_stat.get_status(ship, 50) == (True, "ok")
    assert validated_stat.get_status(ship, 150) == (False, "ok")


def test_section_definition_has_independent_default_item_lists() -> None:
    first = SectionDefinition("core", "Core", 0, 1, "always")
    second = SectionDefinition("weapons", "Weapons", 1, 2, "always")
    item = StatDefinition("mass", "Mass")

    first.items.append(item)

    assert first.items == [item]
    assert second.items == []


def test_section_definition_stores_visibility_and_generator_metadata() -> None:
    visibility = {"type": "dynamic", "generator": "get_rows"}
    section = SectionDefinition(
        key="logistics",
        title="Logistics",
        column=1,
        order=3,
        visibility=visibility,
        generator="get_rows",
    )

    assert section.visibility is visibility
    assert section.generator == "get_rows"

