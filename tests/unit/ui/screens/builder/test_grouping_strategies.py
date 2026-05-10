"""Tests for builder component grouping strategies."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from game.ui.screens.builder.grouping_strategies import (
    DefaultGroupingStrategy,
    FlatGroupingStrategy,
    TypeGroupingStrategy,
    get_component_group_key,
)


@dataclass(frozen=True)
class _ModifierDefinition:
    id: str
    readonly: bool = False


@dataclass(frozen=True)
class _Modifier:
    definition: _ModifierDefinition
    value: Any


@dataclass
class _Component:
    id: str
    name: str
    mass: float
    modifiers: list[_Modifier]


def _component(
    component_id: str,
    name: str,
    mass: float,
    modifiers: list[_Modifier] | None = None,
) -> _Component:
    return _Component(component_id, name, mass, modifiers or [])


def test_group_key_ignores_readonly_modifiers_and_sorts_remaining_mods() -> None:
    readonly = _Modifier(_ModifierDefinition("mass_scaling", readonly=True), 2.0)
    range_mod = _Modifier(_ModifierDefinition("range_mount"), 4.0)
    turret_mod = _Modifier(_ModifierDefinition("turret_mount"), 90)
    component = _component("laser", "Laser", 10, [turret_mod, readonly, range_mod])

    key = get_component_group_key(component)

    assert key == (
        "laser",
        (
            ("range_mount", 4.0),
            ("turret_mount", 90),
        ),
    )


def test_default_grouping_combines_matching_ids_and_non_readonly_modifiers() -> None:
    readonly_a = _Modifier(_ModifierDefinition("mass_scaling", readonly=True), 1.0)
    readonly_b = _Modifier(_ModifierDefinition("mass_scaling", readonly=True), 9.0)
    range_mod = _Modifier(_ModifierDefinition("range_mount"), 2.0)
    components = [
        _component("engine", "Ion Engine", 3.0),
        _component("laser", "Beam Laser", 10.0, [readonly_a, range_mod]),
        _component("laser", "Beam Laser", 12.5, [readonly_b, range_mod]),
    ]

    groups = DefaultGroupingStrategy().group_components(components)

    assert [(group[0][0].id, group[1], group[2]) for group in groups] == [
        ("laser", 2, 22.5),
        ("engine", 1, 3.0),
    ]


def test_default_grouping_separates_different_non_readonly_modifiers() -> None:
    components = [
        _component(
            "laser",
            "Beam Laser",
            10.0,
            [_Modifier(_ModifierDefinition("range_mount"), 2.0)],
        ),
        _component(
            "laser",
            "Beam Laser",
            12.5,
            [_Modifier(_ModifierDefinition("range_mount"), 3.0)],
        ),
    ]

    groups = DefaultGroupingStrategy().group_components(components)

    assert [group[1] for group in groups] == [1, 1]


def test_type_grouping_ignores_modifiers_and_sorts_by_component_id() -> None:
    components = [
        _component("laser", "Beam Laser", 10.0, [_Modifier(_ModifierDefinition("range"), 2)]),
        _component("engine", "Ion Engine", 3.0),
        _component("laser", "Beam Laser", 12.5, [_Modifier(_ModifierDefinition("range"), 9)]),
    ]

    groups = TypeGroupingStrategy().group_components(components)

    assert [(group[3], group[1], group[2]) for group in groups] == [
        ("engine", 1, 3.0),
        ("laser", 2, 22.5),
    ]


def test_flat_grouping_preserves_each_component_with_unique_key() -> None:
    components = [
        _component("laser", "Beam Laser", 10.0),
        _component("laser", "Beam Laser", 12.5),
    ]

    groups = FlatGroupingStrategy().group_components(components)

    assert [group[0] for group in groups] == [[components[0]], [components[1]]]
    assert [group[1] for group in groups] == [1, 1]
    assert [group[2] for group in groups] == [10.0, 12.5]
    assert groups[0][3] != groups[1][3]

