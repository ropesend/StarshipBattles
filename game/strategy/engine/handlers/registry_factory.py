"""`create_default_registry()` — composes the default command-handler registry.

PROJ-363 Phase 3: registry contents are now derived from the
``COMMAND_SPECS`` table in ``game.strategy.engine.commands.specs``. The
factory is one loop over the spec table; adding a command requires
appending one row to ``COMMAND_SPECS``, not editing this file.

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

    Builds the registry by iterating over ``COMMAND_SPECS``: for each
    spec, instantiate the handler class and register it under the
    Command class name. The spec table is the single source of truth.

    Returns:
        CommandHandlerRegistry with all handlers registered.
    """
    # Deferred import: ``specs.py`` imports the handler classes at
    # module-load time, so we can't import it at the top of this module
    # (it sits below us in the import graph).
    from game.strategy.engine.commands.specs import COMMAND_SPECS

    registry = CommandHandlerRegistry()
    for spec in COMMAND_SPECS:
        registry.register(spec.command_class.__name__, spec.handler_class())
    return registry
