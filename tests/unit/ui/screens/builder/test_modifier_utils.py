"""Tests for shared modifier utilities."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from game.ui.screens.builder.modifier_utils import copy_modifiers


class _Modifier:
    def __init__(self, definition: Any, value: float) -> None:
        self.definition = definition
        self.value = value


class _SpecialModifier(_Modifier):
    pass


@dataclass
class _Component:
    modifiers: list[_Modifier] = field(default_factory=list)
    recalculate_count: int = 0

    def recalculate_stats(self) -> None:
        self.recalculate_count += 1


def test_copy_modifiers_replaces_target_modifiers_with_new_instances() -> None:
    definition_a = object()
    definition_b = object()
    source = _Component(
        modifiers=[
            _Modifier(definition_a, 2.5),
            _SpecialModifier(definition_b, 7.0),
        ]
    )
    old_modifier = _Modifier(object(), 99.0)
    target = _Component(modifiers=[old_modifier])
    original_target_list = target.modifiers

    copy_modifiers(source, target)

    assert target.modifiers is not original_target_list
    assert old_modifier not in target.modifiers
    assert [type(mod) for mod in target.modifiers] == [_Modifier, _SpecialModifier]
    assert [mod.definition for mod in target.modifiers] == [definition_a, definition_b]
    assert [mod.value for mod in target.modifiers] == [2.5, 7.0]
    assert target.modifiers[0] is not source.modifiers[0]
    assert target.modifiers[1] is not source.modifiers[1]
    assert target.recalculate_count == 1


def test_copy_modifiers_empty_source_clears_target_and_recalculates() -> None:
    source = _Component()
    target = _Component(modifiers=[_Modifier(object(), 3.0)])

    copy_modifiers(source, target)

    assert target.modifiers == []
    assert target.recalculate_count == 1

