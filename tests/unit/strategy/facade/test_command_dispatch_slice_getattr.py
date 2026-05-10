"""Tests for the spec-driven ``__getattr__`` resolver on CommandDispatchSlice.

PROJ-363 Phase 4: the 31 hand-written ``dispatch_*_command`` helpers
collapsed to one ``__getattr__`` that resolves names against
``COMMAND_SPECS``. These tests pin the resolver's behavior:

- Every spec with a ``facade_helper_name`` resolves to a callable that
  forwards to ``handle_command`` with the right Command instance.
- Unknown ``dispatch_*`` names raise AttributeError.
- Non-``dispatch_`` attribute access raises AttributeError without
  consulting the spec table.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.strategy.engine.commands.registry import (
    command_registry,
    seed_default_commands,
)
from game.strategy.facade.slices.command_dispatch_slice import (
    CommandDispatchSlice,
)


# PROJ-371 Phase 2: COMMAND_SPECS is now ``tuple(command_registry.all())``.
if len(command_registry) == 0:
    seed_default_commands(command_registry)
COMMAND_SPECS = tuple(command_registry.all())


def _make_slice() -> tuple[CommandDispatchSlice, MagicMock]:
    """Build a slice instance with a stub handle_command callable.

    We bypass ``__init__`` to avoid needing a real ``FacadeSessionState``;
    the resolver only reads ``self._handle_command``.
    """
    handle = MagicMock(name="handle_command")
    inst = object.__new__(CommandDispatchSlice)
    # ``__slots__`` lets us set these because they're declared.
    inst._state = None  # type: ignore[attr-defined]
    inst._handle_command = handle  # type: ignore[attr-defined]
    return inst, handle


_SPECS_WITH_HELPER = [
    s for s in COMMAND_SPECS if s.facade_helper_name is not None
]


@pytest.mark.parametrize(
    "spec", _SPECS_WITH_HELPER, ids=lambda s: s.facade_helper_name
)
def test_every_spec_with_facade_helper_resolves_to_callable(spec) -> None:
    """``getattr(slice, spec.facade_helper_name)`` returns a callable."""
    slice_inst, _ = _make_slice()
    resolved = getattr(slice_inst, spec.facade_helper_name)
    assert callable(resolved)
    assert resolved.__name__ == spec.facade_helper_name


def test_resolver_forwards_to_handle_command_with_command_instance() -> None:
    """Calling the resolved helper invokes ``_handle_command`` once with a
    Command instance whose class matches the spec.
    """
    from game.strategy.engine.commands import IssueMoveCommand
    from game.core.hex_math import HexCoord

    slice_inst, handle = _make_slice()
    handle.return_value = "RESULT"
    target = HexCoord(1, 2)

    result = slice_inst.dispatch_issue_move(fleet_id=42, target_hex=target)

    assert result == "RESULT"
    handle.assert_called_once()
    (cmd,), _ = handle.call_args
    assert isinstance(cmd, IssueMoveCommand)
    assert cmd.fleet_id == 42
    assert cmd.target_hex == target


def test_unknown_dispatch_name_raises_attribute_error() -> None:
    slice_inst, _ = _make_slice()
    with pytest.raises(AttributeError) as excinfo:
        slice_inst.dispatch_unknown_command_xyz  # noqa: B018 — attribute access
    assert "dispatch_unknown_command_xyz" in str(excinfo.value)


def test_non_dispatch_attribute_raises_attribute_error() -> None:
    """Non-``dispatch_*`` access falls through ``__getattr__`` cleanly."""
    slice_inst, _ = _make_slice()
    with pytest.raises(AttributeError):
        slice_inst.random_attr  # noqa: B018 — attribute access


def test_dispatch_method_appears_callable_on_class_via_instance() -> None:
    """The resolver-produced callable supports ``hasattr`` introspection."""
    slice_inst, _ = _make_slice()
    assert hasattr(slice_inst, "dispatch_issue_move")
    assert not hasattr(slice_inst, "dispatch_does_not_exist")
