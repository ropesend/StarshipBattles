"""`create_default_registry()` — composes the default command-handler registry.

PROJ-371 Phase 2: registry contents are now derived from the
self-registering :class:`CommandRegistry` at
``game.strategy.engine.commands.registry``. Adding a command requires
adding a new handler module with a ``@command_spec(...)`` decorator
and a ``register(registry)`` function — not editing this file.

Historical note (PROJ-309 sub-phase 3.5): the original 1076-line
``command_handlers.py`` monolith was decomposed into a package of
sibling modules under ``handlers/``. The two ``*_command_handlers.py``
siblings (superweapon, planet) remain at their original locations
pending a follow-up move that's out of scope for PROJ-309.
"""
from __future__ import annotations

from game.strategy.engine.handlers.base import CommandHandlerRegistry


def create_default_registry() -> CommandHandlerRegistry:
    """Create a registry with all standard command handlers registered.

    Walks ``command_registry`` (self-registering metadata table from
    PROJ-371) and instantiates one handler per spec. The metadata
    registry is the single source of truth.

    Returns:
        CommandHandlerRegistry with all handlers registered.
    """
    # Deferred import: handler modules import the metadata registry at
    # module-load time, so we can't import it at the top of this module
    # (it sits below us in the import graph).
    from game.strategy.engine.commands.registry import (
        command_registry,
        seed_default_commands,
    )

    if len(command_registry) == 0:
        seed_default_commands(command_registry)

    registry = CommandHandlerRegistry()
    for spec in command_registry.all():
        registry.register(spec.command_class.__name__, spec.handler_class())
    return registry
