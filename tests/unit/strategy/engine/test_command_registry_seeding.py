"""Bit-identity contract: COMMAND_SPECS tuple == command_registry view.

PROJ-371 Phase 1: introduces ``CommandRegistry`` alongside the existing
``COMMAND_SPECS`` tuple. Both surfaces enumerate the same set of
``CommandSpec`` rows. This module pins that invariant for the duration
of Phase 1 — Phase 2 deletes the tuple and this file goes away (or
migrates the still-relevant tests onto ``test_command_specs_contract``).

Decorator-as-metadata-only invariant (r004): importing a handler
module must NOT mutate ``command_registry._specs``. Mutation only
happens via ``seed_default_commands(registry)`` calling each module's
``register()`` function.
"""
from __future__ import annotations

import importlib
from unittest.mock import Mock

import pytest

from game.strategy.engine.commands.registry import (
    CommandSpec,
    command_registry,
    command_spec,
    reset_command_registry,
    seed_default_commands,
)
from game.strategy.engine.commands.specs import COMMAND_SPECS


@pytest.fixture(autouse=True)
def _seeded_registry():
    """Snapshot/restore + seed the registry around every test in this file."""
    snapshot = dict(command_registry._specs)
    command_registry._specs.clear()
    seed_default_commands(command_registry)
    yield
    command_registry._specs.clear()
    command_registry._specs.update(snapshot)


# ---------------------------------------------------------------------------
# Module-existence smoke
# ---------------------------------------------------------------------------

def test_registry_module_exists() -> None:
    """``commands.registry`` exposes a ``command_registry`` global."""
    from game.strategy.engine.commands import registry as registry_mod
    assert hasattr(registry_mod, "command_registry")
    assert isinstance(registry_mod.command_registry, registry_mod.CommandRegistry)


# ---------------------------------------------------------------------------
# Bit-identity (post-seed)
# ---------------------------------------------------------------------------

def test_registry_yields_same_command_classes_as_tuple() -> None:
    tuple_names = {s.command_class.__name__ for s in COMMAND_SPECS}
    registry_names = {s.command_class.__name__ for s in command_registry.all()}
    assert tuple_names == registry_names


def test_registry_specs_are_field_for_field_identical_to_tuple() -> None:
    """Every CommandSpec field matches between the tuple and the registry."""
    by_name_tuple = {s.command_class.__name__: s for s in COMMAND_SPECS}
    by_name_reg = {s.command_class.__name__: s for s in command_registry.all()}
    assert set(by_name_tuple) == set(by_name_reg)
    for name, spec_t in by_name_tuple.items():
        spec_r = by_name_reg[name]
        assert spec_t.command_class is spec_r.command_class, name
        assert spec_t.handler_class is spec_r.handler_class, name
        assert spec_t.order_type == spec_r.order_type, name
        assert spec_t.category == spec_r.category, name
        assert spec_t.subcategories == spec_r.subcategories, name
        assert spec_t.action_ability_name == spec_r.action_ability_name, name
        assert spec_t.execution_model == spec_r.execution_model, name
        assert spec_t.facade_helper_name == spec_r.facade_helper_name, name
        assert spec_t.serializer_codec == spec_r.serializer_codec, name


def test_registry_count_is_35() -> None:
    assert len(command_registry) == 35
    assert len(list(command_registry.all())) == 35


# ---------------------------------------------------------------------------
# Decorator contract — METADATA-ONLY (r004)
# ---------------------------------------------------------------------------

def test_decorator_returns_handler_class_unchanged() -> None:
    """``@command_spec`` returns the wrapped class unchanged.

    The decorator must NOT register on import; it only attaches
    ``__command_spec_kwargs__`` for later use by the per-module
    ``register(registry)`` function.
    """
    Marker = type("Marker", (object,), {"X": 1})
    decorated = command_spec(
        command_class=Mock(__name__="MockCmd"),
        order_type=None,
        category="action",
    )(Marker)
    assert decorated is Marker
    assert hasattr(decorated, "__command_spec_kwargs__")
    assert decorated.__command_spec_kwargs__["category"] == "action"


def test_import_handler_module_does_not_register() -> None:
    """Importing a handler module must NOT mutate the registry.

    Pins the metadata-only decorator contract from r004. If anyone
    re-introduces import-time registration (decorator calls
    ``command_registry.register(...)``), this test fails.
    """
    before = dict(command_registry._specs)
    # Re-import / fresh-import a handler module.
    importlib.import_module("game.strategy.engine.handlers.build")
    after = dict(command_registry._specs)
    assert before == after, (
        "Importing a handler module mutated command_registry._specs. "
        "The @command_spec decorator must be metadata-only (r004); "
        "registration only happens via seed_default_commands()."
    )


# ---------------------------------------------------------------------------
# Round-trip: reset clears + reseeds
# ---------------------------------------------------------------------------

def test_round_trip_reset_then_seed() -> None:
    """``reset_command_registry`` clears and re-seeds without leaking state."""
    original_count = len(command_registry)
    assert original_count == 35
    reset_command_registry()
    assert len(command_registry) == original_count


# ---------------------------------------------------------------------------
# Duplicate-registration guard
# ---------------------------------------------------------------------------

def test_explicit_duplicate_registration_raises() -> None:
    first = next(iter(command_registry.all()))
    with pytest.raises(ValueError):
        command_registry.register(first)  # default replace=False


def test_explicit_duplicate_registration_with_replace_succeeds() -> None:
    first = next(iter(command_registry.all()))
    # Register again with replace=True — should succeed; emits warning.
    command_registry.register(first, replace=True)
    assert command_registry.get(first.command_class.__name__) is first


# ---------------------------------------------------------------------------
# Sanity: every spec carries a per-module register() bridge
# ---------------------------------------------------------------------------

def test_every_handler_module_has_register_function() -> None:
    """Every handler module must expose ``register(registry)``."""
    from game.strategy.engine.handlers import (
        build,
        construction_queue,
        movement,
        order_queue,
        transfer,
    )
    from game.strategy.engine import (
        planet_command_handlers,
        superweapon_command_handlers,
    )
    for module in (
        build,
        construction_queue,
        movement,
        order_queue,
        transfer,
        planet_command_handlers,
        superweapon_command_handlers,
    ):
        assert hasattr(module, "register"), (
            f"{module.__name__} missing required register(registry) entry point"
        )
        assert callable(module.register)
