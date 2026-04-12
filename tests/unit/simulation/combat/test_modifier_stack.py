"""Tests for ModifierStack DTO (PROJ-269 Phase 1 Task 1.3).

Phase 1 ships the type shape only. Engine application of the stack
(intra-group MAX + inter-group SUM aggregation against existing
`ability_aggregator` infrastructure) lands in Phase 5 + engine wiring
at end of Phase 1.

Covers:
- `ModifierStack(per_team: Mapping, global_: Tuple)` frozen dataclass shape
- `ModifierEntry(source, stack_group, effect)` frozen dataclass shape
- `ModifierStack.empty()` classmethod returns an empty stack
- `source` strings follow the documented pattern ("species:Terran" etc.)
  — shape only; enforcement lands with compilers in Tasks 1.7-1.9.
"""
import dataclasses

import pytest

from game.simulation.combat.modifier_stack import (
    ModifierEntry,
    ModifierStack,
)
from game.simulation.components.modifier_effects import ModifierEffect


def _minimal_effect(source_id: str = "hardened_mount") -> ModifierEffect:
    return ModifierEffect(
        stat_key="damage_mult",
        value=1.5,
        operation="multiply",
        target_ability=None,
        source_modifier_id=source_id,
        source_modifier_name="Hardened",
        formula_str="param",
        param_value=1.5,
    )


# ---------------------------------------------------------------------------
# Frozen dataclass shape
# ---------------------------------------------------------------------------


def test_modifier_entry_is_frozen_dataclass():
    assert dataclasses.is_dataclass(ModifierEntry)
    params = getattr(ModifierEntry, "__dataclass_params__", None)
    assert params is not None and params.frozen


def test_modifier_stack_is_frozen_dataclass():
    assert dataclasses.is_dataclass(ModifierStack)
    params = getattr(ModifierStack, "__dataclass_params__", None)
    assert params is not None and params.frozen


def test_modifier_entry_fields():
    entry = ModifierEntry(
        source="species:Terran",
        stack_group="sensor",
        effect=_minimal_effect(),
    )
    assert entry.source == "species:Terran"
    assert entry.stack_group == "sensor"
    assert entry.effect.value == pytest.approx(1.5)


def test_modifier_entry_allows_none_stack_group():
    entry = ModifierEntry(
        source="empire:research_xyz",
        stack_group=None,
        effect=_minimal_effect(),
    )
    assert entry.stack_group is None


def test_modifier_entry_is_immutable():
    entry = ModifierEntry(
        source="sector:ion_storm",
        stack_group="storm",
        effect=_minimal_effect(),
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        entry.source = "other"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# ModifierStack shape
# ---------------------------------------------------------------------------


def test_modifier_stack_has_per_team_and_global_fields():
    stack = ModifierStack(per_team={}, global_=())
    assert hasattr(stack, "per_team")
    assert hasattr(stack, "global_")
    assert stack.per_team == {}
    assert stack.global_ == ()


def test_modifier_stack_accepts_entries():
    entry_team = ModifierEntry(
        source="species:Terran",
        stack_group=None,
        effect=_minimal_effect("a"),
    )
    entry_global = ModifierEntry(
        source="system:nebula",
        stack_group="environmental",
        effect=_minimal_effect("b"),
    )
    stack = ModifierStack(
        per_team={0: (entry_team,)},
        global_=(entry_global,),
    )
    assert stack.per_team[0][0] is entry_team
    assert stack.global_[0] is entry_global


def test_modifier_stack_is_immutable():
    stack = ModifierStack(per_team={}, global_=())
    with pytest.raises(dataclasses.FrozenInstanceError):
        stack.global_ = ()  # type: ignore[misc]


# ---------------------------------------------------------------------------
# ModifierStack.empty()
# ---------------------------------------------------------------------------


def test_modifier_stack_empty_classmethod_returns_empty():
    stack = ModifierStack.empty()
    assert isinstance(stack, ModifierStack)
    assert stack.per_team == {} or len(stack.per_team) == 0
    assert stack.global_ == ()


def test_modifier_stack_empty_returns_equal_instances():
    a = ModifierStack.empty()
    b = ModifierStack.empty()
    # Empty stacks should compare equal (frozen dataclass __eq__).
    assert a == b


# ---------------------------------------------------------------------------
# ModifierStack exports
# ---------------------------------------------------------------------------


def test_modifier_stack_importable_from_module():
    # Module-level imports at top of this file succeeded; also check __all__.
    from game.simulation.combat import modifier_stack as ms_mod

    assert hasattr(ms_mod, "ModifierStack")
    assert hasattr(ms_mod, "ModifierEntry")
