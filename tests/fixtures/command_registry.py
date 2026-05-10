"""Test helpers for registering commands at test time.

PROJ-371 Phase 3: third-party-command smoke test machinery. Snapshots
the registry, registers a one-off ``CommandSpec``, restores the
snapshot on context exit. Production code never unregisters; this is
strictly a test isolation helper.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from game.strategy.engine.commands.registry import (
    CommandSpec,
    command_registry,
)


@contextmanager
def temporary_command(spec: CommandSpec) -> Iterator[None]:
    """Snapshot the registry, register ``spec``, restore on exit.

    Use only in tests. Idempotent across nested contexts because the
    snapshot/restore is symmetric.
    """
    original = dict(command_registry._specs)
    command_registry.register(spec)
    try:
        yield
    finally:
        command_registry._specs.clear()
        command_registry._specs.update(original)
