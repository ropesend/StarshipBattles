"""Spec-table contract tests (PROJ-363 Phase 2 / PROJ-424 Phase 3).

Asserts ``COMMAND_SPECS`` is internally consistent and that every
existing surface (registry, OrderType frozensets,
``order_metadata.order_to_ability_map``) agrees with what the spec
table would derive. PROJ-424 Phase 3 swapped the original
``ORDER_TO_ABILITY_MAP`` import-time snapshot in
``action_time_resolver.py`` for a live read through ``order_metadata``.
"""
from __future__ import annotations

import pytest

import game.strategy.engine.commands as commands_module
from game.strategy.data.order_types import OrderType
from game.strategy.engine.commands.order_metadata_view import order_metadata
from game.strategy.engine.commands.registry import (
    ALLOWED_CATEGORIES,
    ALLOWED_EXECUTION_MODELS,
    CommandSpec,
    command_registry,
    seed_default_commands,
)
from game.strategy.engine.handlers.registry_factory import create_default_registry


# PROJ-371 Phase 2: COMMAND_SPECS is now ``tuple(command_registry.all())``.
# Seed once at module-load (idempotent).
if len(command_registry) == 0:
    seed_default_commands(command_registry)
COMMAND_SPECS: tuple[CommandSpec, ...] = tuple(command_registry.all())


def specs_by_command_name() -> dict[str, CommandSpec]:
    return command_registry.specs_by_command_name()


def specs_by_facade_helper() -> dict[str, CommandSpec]:
    return command_registry.specs_by_facade_helper()


def order_types_for_category(category: str):
    return command_registry.order_types_for_category(category)


def movement_order_types():
    return command_registry.movement_order_types()


def action_order_types():
    return command_registry.action_order_types()


def planet_action_order_types():
    return command_registry.planet_action_order_types()


def planet_fms_action_order_types():
    return command_registry.planet_fms_action_order_types()


def order_to_ability_map():
    return command_registry.order_to_ability_map()


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
        f"Add a `@command_spec(...)` decorator on the Command DTO and a "
        f"`register(registry)` call in the owning handler module "
        f"(see `docs/systems/orders_system.md`)."
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


def test_movement_order_types_derivation_matches_view() -> None:
    """``movement_order_types()`` matches the live ``order_metadata``
    view. PROJ-424 Phase 5: the duplicated frozensets were deleted; the
    view is the single read facade.
    """
    assert movement_order_types() == order_metadata.movement_order_types


def test_action_order_types_derivation_matches_view() -> None:
    assert action_order_types() == order_metadata.action_order_types


def test_planet_action_order_types_derivation_matches_view() -> None:
    assert planet_action_order_types() == order_metadata.planet_action_order_types


def test_planet_fms_action_order_types_derivation_matches_view() -> None:
    """``planet_fms_action_order_types()`` derives from ``subcategories``
    tags on the FMS handler command specs and matches the live
    ``order_metadata.planet_fms_action_order_types`` view.

    PROJ-424 Phase 1 introduced the derivation; Phase 5 swapped the
    pinned frozenset for the view.
    """
    assert planet_fms_action_order_types() == order_metadata.planet_fms_action_order_types


def test_exactly_five_specs_carry_planet_fms_subcategory() -> None:
    """Exactly five command specs carry ``"planet_fms"`` in subcategories.

    PROJ-424 Phase 1: the FMS-from-planet derivation must be
    data-driven via the ``subcategories`` tag. Adding/removing a tag
    requires touching this test (and the planet_fms order list).
    """
    tagged = [
        s for s in COMMAND_SPECS
        if "planet_fms" in s.subcategories
    ]
    names = sorted(s.command_class.__name__ for s in tagged)
    assert names == sorted([
        "IssueLayMinesCommand",
        "IssueLaunchFightersCommand",
        "IssueLaunchSatellitesCommand",
        "IssueRecoverFightersCommand",
        "IssueRecoverSatellitesCommand",
    ]), (
        f"planet_fms subcategory tag drift: {names}"
    )


def test_order_to_ability_map_derivation_matches_view() -> None:
    """``order_to_ability_map()`` matches the live ``order_metadata`` view.

    PROJ-424 Phase 3: the import-time ``ORDER_TO_ABILITY_MAP`` snapshot in
    ``action_time_resolver.py`` was deleted; consumers now read through
    ``order_metadata.order_to_ability_map`` at call time. This contract
    pins the registry derivation against the view.
    """
    assert order_to_ability_map() == order_metadata.order_to_ability_map


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
