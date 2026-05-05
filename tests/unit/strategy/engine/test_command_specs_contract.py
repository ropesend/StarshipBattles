"""Spec-table contract tests (PROJ-363 Phase 2).

Asserts ``COMMAND_SPECS`` is internally consistent and that every
existing surface (registry, OrderType frozensets, ORDER_TO_ABILITY_MAP)
agrees with what the spec table would derive. After Phase 3 wires the
derivations *back into* those surfaces, these tests act as the
regression contract.
"""
from __future__ import annotations

import pytest

import game.strategy.engine.commands as commands_module
from game.strategy.data.order_types import (
    ACTION_ORDER_TYPES,
    MOVEMENT_ORDER_TYPES,
    OrderType,
    PLANET_ACTION_ORDER_TYPES,
)
from game.strategy.engine.commands.specs import (
    ALLOWED_CATEGORIES,
    ALLOWED_EXECUTION_MODELS,
    COMMAND_SPECS,
    CommandSpec,
    action_order_types,
    movement_order_types,
    order_to_ability_map,
    order_types_for_category,
    planet_action_order_types,
    specs_by_command_name,
    specs_by_facade_helper,
)
from game.strategy.engine.handlers.registry_factory import create_default_registry
from game.strategy.services.action_time_resolver import ORDER_TO_ABILITY_MAP


def _declared_command_classes() -> set[str]:
    return {
        name
        for name in dir(commands_module)
        if name.endswith("Command")
        and not name.startswith("_")
        and isinstance(getattr(commands_module, name), type)
    } - {"Command"}


# ---------------------------------------------------------------------------
# Self-consistency of the table
# ---------------------------------------------------------------------------

def test_every_command_class_has_a_spec() -> None:
    """Every Command DTO declared in commands.py has a CommandSpec entry."""
    declared = _declared_command_classes()
    spec_classes = {s.command_class.__name__ for s in COMMAND_SPECS}
    missing = declared - spec_classes
    assert not missing, (
        f"Command DTOs without a CommandSpec entry: {sorted(missing)}. "
        f"Add an entry in game/strategy/engine/commands/specs.py."
    )


def test_no_orphan_specs() -> None:
    """Every CommandSpec.command_class corresponds to a declared Command."""
    declared = _declared_command_classes()
    spec_classes = {s.command_class.__name__ for s in COMMAND_SPECS}
    orphans = spec_classes - declared
    assert not orphans, (
        f"CommandSpec entries reference unknown Command DTOs: {sorted(orphans)}."
    )


def test_no_duplicate_command_classes_in_specs() -> None:
    """Each Command class appears in at most one spec."""
    seen: dict[str, int] = {}
    for spec in COMMAND_SPECS:
        name = spec.command_class.__name__
        seen[name] = seen.get(name, 0) + 1
    duplicates = {name: count for name, count in seen.items() if count > 1}
    assert not duplicates, f"Duplicate spec entries: {duplicates}"


def test_facade_helper_names_are_unique() -> None:
    """Two specs cannot share the same facade helper name."""
    helpers = [
        s.facade_helper_name for s in COMMAND_SPECS
        if s.facade_helper_name is not None
    ]
    duplicates = {h for h in helpers if helpers.count(h) > 1}
    assert not duplicates, f"Duplicate facade_helper_name values: {sorted(duplicates)}"


def test_facade_helpers_follow_dispatch_prefix_convention() -> None:
    """All facade helper names start with ``dispatch_``."""
    bad = [
        s.facade_helper_name for s in COMMAND_SPECS
        if s.facade_helper_name is not None
        and not s.facade_helper_name.startswith('dispatch_')
    ]
    assert not bad, f"facade_helper_name not starting with 'dispatch_': {bad}"


@pytest.mark.parametrize("spec", COMMAND_SPECS, ids=lambda s: s.command_class.__name__)
def test_spec_uses_known_category_and_execution_model(spec: CommandSpec) -> None:
    """Each CommandSpec uses an enum-listed category and execution model."""
    assert spec.category in ALLOWED_CATEGORIES, (
        f"{spec.command_class.__name__}: unknown category {spec.category!r}"
    )
    assert spec.execution_model in ALLOWED_EXECUTION_MODELS, (
        f"{spec.command_class.__name__}: unknown execution_model {spec.execution_model!r}"
    )


@pytest.mark.parametrize("spec", COMMAND_SPECS, ids=lambda s: s.command_class.__name__)
def test_mission_specs_have_no_order_type(spec: CommandSpec) -> None:
    """Mission commands decompose into MOVE+ACTION; they have no own OrderType."""
    if spec.execution_model == 'mission':
        assert spec.order_type is None, (
            f"{spec.command_class.__name__}: mission specs must have order_type=None"
        )


# ---------------------------------------------------------------------------
# Spec table agrees with existing surfaces (pins Phase 3 derivation)
# ---------------------------------------------------------------------------

def test_spec_table_handler_set_matches_registry() -> None:
    """Building the registry from COMMAND_SPECS yields the same handler set
    as the current ``create_default_registry()``."""
    registry = create_default_registry()
    spec_command_names = {s.command_class.__name__ for s in COMMAND_SPECS}
    registered = set(registry._handlers.keys())
    assert spec_command_names == registered


def test_movement_order_types_derivation_matches_constant() -> None:
    """``movement_order_types()`` matches the existing frozenset."""
    assert movement_order_types() == MOVEMENT_ORDER_TYPES


def test_action_order_types_derivation_matches_constant() -> None:
    """``action_order_types()`` matches the existing frozenset."""
    assert action_order_types() == ACTION_ORDER_TYPES


def test_planet_action_order_types_derivation_matches_constant() -> None:
    """``planet_action_order_types()`` matches the existing frozenset."""
    assert planet_action_order_types() == PLANET_ACTION_ORDER_TYPES


def test_order_to_ability_map_derivation_matches_constant() -> None:
    """``order_to_ability_map()`` matches the existing static map."""
    assert order_to_ability_map() == ORDER_TO_ABILITY_MAP


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------

def test_specs_by_command_name_count() -> None:
    """The lookup is total (one entry per spec)."""
    assert len(specs_by_command_name()) == len(COMMAND_SPECS)


def test_specs_by_facade_helper_excludes_none() -> None:
    """The facade-helper lookup omits specs with no helper name."""
    expected = {
        s.facade_helper_name for s in COMMAND_SPECS
        if s.facade_helper_name is not None
    }
    assert set(specs_by_facade_helper().keys()) == expected


def test_order_types_for_category_returns_only_concrete_orders() -> None:
    """``order_types_for_category`` skips mission specs (order_type=None)."""
    for category in ALLOWED_CATEGORIES:
        derived = order_types_for_category(category)
        for ot in derived:
            assert isinstance(ot, OrderType)


# ---------------------------------------------------------------------------
# Action-ability hookup
# ---------------------------------------------------------------------------

def test_specs_with_action_ability_have_order_type() -> None:
    """If a spec declares an action ability, it must also declare its OrderType.

    Without an OrderType the action-time resolver has nothing to key on.
    """
    bad = [
        s.command_class.__name__ for s in COMMAND_SPECS
        if s.action_ability_name is not None and s.order_type is None
    ]
    assert not bad, (
        f"Specs with action_ability_name but no order_type: {bad}"
    )


def test_specs_with_action_ability_use_action_execution_model() -> None:
    """Action-ability specs must use ``execution_model='action'``."""
    bad = [
        s.command_class.__name__ for s in COMMAND_SPECS
        if s.action_ability_name is not None and s.execution_model != 'action'
    ]
    assert not bad, (
        f"Specs with action_ability_name and non-'action' execution_model: {bad}"
    )
