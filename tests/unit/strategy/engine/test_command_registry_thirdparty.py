"""End-to-end smoke: a third-party command registers, dispatches, unregisters cleanly.

PROJ-371 Phase 3: proves that adding a new command requires only one
new file (handler module + decorator + per-module ``register()`` —
plus a Command DTO). This test acts as the worked example for mod
authors and as a regression guard against the registry's public
contract.
"""
from __future__ import annotations

from dataclasses import dataclass

import pytest

from game.core.validation import ValidationResult
from game.strategy.engine.commands import Command, CommandType
from game.strategy.engine.commands.registry import (
    CommandSpec,
    command_registry,
    seed_default_commands,
)
from game.strategy.engine.handlers.base import BaseCommandHandler
from game.strategy.engine.handlers.registry_factory import create_default_registry
from tests.fixtures.command_registry import temporary_command


# Synthetic Command DTO + Handler — emulates a mod's registration.
@dataclass
class FakeModCommand(Command):
    """Synthetic Command DTO for the third-party smoke test."""
    fleet_id: int = 0
    payload: str = ""

    def __post_init__(self) -> None:
        super().__post_init__()


class FakeModCommandHandler(BaseCommandHandler):
    """Synthetic handler that captures execute() calls for assertion."""

    executions: list = []

    def execute(self, session, command):
        type(self).executions.append((session, command))
        return ValidationResult.success()


@pytest.fixture(autouse=True)
def _seeded_registry():
    """Snapshot/restore + seed the registry around every test."""
    snapshot = dict(command_registry._specs)
    command_registry._specs.clear()
    seed_default_commands(command_registry)
    FakeModCommandHandler.executions = []
    yield
    command_registry._specs.clear()
    command_registry._specs.update(snapshot)


def _make_fake_spec() -> CommandSpec:
    return CommandSpec(
        command_class=FakeModCommand,
        order_type=None,
        handler_class=FakeModCommandHandler,
        category='action',
        execution_model='instant',
        facade_helper_name=None,
    )


def test_third_party_command_registers_and_dispatches() -> None:
    """A third-party command can be registered, instantiated by
    ``create_default_registry``, and dispatched."""
    spec = _make_fake_spec()
    with temporary_command(spec):
        # Registry sees the new spec.
        assert command_registry.get('FakeModCommand') is spec

        # The handler-instance registry built from the metadata
        # registry includes the new command.
        handler_registry = create_default_registry()
        assert 'FakeModCommand' in handler_registry._handlers

        # Dispatching it executes the synthetic handler.
        cmd = FakeModCommand(fleet_id=42, payload='hello')
        result = handler_registry.dispatch('FakeModCommand', None, cmd)

        assert result.is_valid
        assert len(FakeModCommandHandler.executions) == 1
        captured_session, captured_cmd = FakeModCommandHandler.executions[0]
        assert captured_session is None
        assert captured_cmd is cmd

    # On context exit the spec is gone.
    assert command_registry.get('FakeModCommand') is None


def test_third_party_command_does_not_pollute_other_tests() -> None:
    """``temporary_command`` restores the registry cleanly."""
    baseline = len(command_registry)
    spec = _make_fake_spec()
    with temporary_command(spec):
        assert len(command_registry) == baseline + 1
    assert len(command_registry) == baseline
    assert 'FakeModCommand' not in command_registry


def test_replace_flag_required_for_replacing_a_default(caplog) -> None:
    """Re-registering an existing command without ``replace=True`` raises;
    with ``replace=True`` it succeeds and emits a WARNING.

    PROJ-395 CRIT-002: the duplicate guard now raises
    ``ValidationException(DUPLICATE_COMMAND)`` instead of a bare
    ``ValueError``.
    """
    from game.core.error_codes import ErrorCode
    from game.core.exceptions import ValidationException

    first = next(iter(command_registry.all()))

    # Without replace=True — ValidationException(DUPLICATE_COMMAND).
    with pytest.raises(ValidationException) as exc:
        command_registry.register(first)
    assert exc.value.code == ErrorCode.DUPLICATE_COMMAND.value
    assert exc.value.context.get("command_name") == first.command_class.__name__

    # With replace=True — succeeds + warns.
    snapshot = dict(command_registry._specs)
    try:
        with caplog.at_level('WARNING', logger='game.strategy.engine.commands.registry'):
            command_registry.register(first, replace=True)
        assert any(
            'replacing' in record.getMessage().lower() for record in caplog.records
        ), f"expected a 'replacing' WARNING log; saw: {[r.getMessage() for r in caplog.records]}"
    finally:
        command_registry._specs.clear()
        command_registry._specs.update(snapshot)
