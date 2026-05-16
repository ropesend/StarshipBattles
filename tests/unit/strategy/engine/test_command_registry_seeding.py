"""Registry-seeding contract tests.

PROJ-371 Phase 1 introduced these alongside ``COMMAND_SPECS`` to assert
bit-identity. Phase 2 deleted ``commands.specs`` (the registry is now the
single source of truth), so the bit-identity check has nothing to compare
against; what's left are the invariants that DON'T depend on the legacy
tuple:

- The metadata-only decorator contract (r004): importing a handler
  module must NOT mutate ``command_registry._specs``. Mutation only
  happens via ``seed_default_commands(registry)``.
- ``reset_command_registry()`` clears + reseeds round-trip cleanly.
- Duplicate registration is guarded.
- Every handler module exposes ``register(registry)``.
- The decorator returns the wrapped class unchanged and attaches
  ``__command_spec_kwargs__``.
- The seeded registry contains exactly 35 specs (the count is the
  PROJ-371 baseline; pin moves with future spec additions).
"""
from __future__ import annotations

import importlib
from unittest.mock import Mock

import pytest

from game.strategy.engine.commands.registry import (
    command_registry,
    command_spec,
    reset_command_registry,
    seed_default_commands,
)


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


def test_registry_count_is_35() -> None:
    """The seeded default registry contains 40 specs.

    Baseline was 35 (PROJ-371); PROJ-FMS-B Phase 1 added
    ``IssueLayMinesCommand`` -> ``LayMinesCommandHandler``, bumping to 36.
    PROJ-FMS-C Phase 1+3 added ``IssueLaunchFightersCommand`` and
    ``IssueRecoverFightersCommand``, bumping to 38. PROJ-FMS-D Phase 1+2
    added ``IssueLaunchSatellitesCommand`` and
    ``IssueRecoverSatellitesCommand``, bumping to 40.
    """
    assert len(command_registry) == 40
    assert len(list(command_registry.all())) == 40


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
    assert original_count == 40  # PROJ-FMS-D Phase 1+2 added launch + recover satellites
    reset_command_registry()
    assert len(command_registry) == original_count


# ---------------------------------------------------------------------------
# Duplicate-registration guard
# ---------------------------------------------------------------------------

def test_explicit_duplicate_registration_raises() -> None:
    """PROJ-395 CRIT-002: duplicate registration now raises
    ``ValidationException(DUPLICATE_COMMAND)`` so callers catching
    ``ValidationException`` from registration cover this path too.
    """
    from game.core.error_codes import ErrorCode
    from game.core.exceptions import ValidationException

    first = next(iter(command_registry.all()))
    with pytest.raises(ValidationException) as exc:
        command_registry.register(first)  # default replace=False
    assert exc.value.code == ErrorCode.DUPLICATE_COMMAND.value
    assert exc.value.context.get("command_name") == first.command_class.__name__
    assert exc.value.context.get("existing_handler") == first.handler_class.__name__
    assert exc.value.context.get("duplicate_handler") == first.handler_class.__name__


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
