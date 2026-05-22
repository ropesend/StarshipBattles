"""Command dispatch slice (PROJ-309 sub-phase 3.7; PROJ-363 Phase 4;
PROJ-371 Phase 2).

Holds the universal ``handle_command`` entry point and the
``dispatch_*`` resolver. Each ``dispatch_*_command`` helper has the
same one-line shape: import the command, instantiate it from kwargs,
and forward to ``handle_command``. PROJ-363 collapsed the 31 hand-
written helpers into a single ``__getattr__`` resolver. PROJ-371
Phase 2 retargets the resolver onto ``command_registry`` (the new
self-registering metadata source). The slice routes through a
caller-supplied ``handle_command`` callable so tests that monkey-patch
``facade.handle_command = MagicMock(...)`` still intercept the call.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Dict, Optional

if TYPE_CHECKING:
    from game.core.validation import ValidationResult
    from game.strategy.engine.commands import Command
    from game.strategy.engine.commands.registry import CommandSpec
    from game.strategy.facade.slices._facade_state import FacadeSessionState


# F-A-030: ``command_registry.specs_by_facade_helper()`` walks every
# registered spec on each call. The facade resolves dispatch helpers
# once per UI action so this used to be an O(N) hot-path; cache the
# mapping on first build. Registration is one-shot at app start
# (``seed_default_commands``) so there is no mutation hook to invalidate.
_specs_cache: Optional[Dict[str, "CommandSpec"]] = None


def _invalidate_specs_cache() -> None:
    """Test seam: drop the cached spec lookup."""
    global _specs_cache
    _specs_cache = None


class CommandDispatchSlice:
    """All write-path helpers, isolated from query slices."""

    __slots__ = ("_state", "_handle_command")

    def __init__(
        self,
        state: "FacadeSessionState",
        handle_command: Callable[["Command"], "ValidationResult"],
    ) -> None:
        self._state = state
        # ``handle_command`` is supplied as a callable so dispatchers go
        # through whatever the facade currently exposes (including
        # monkey-patched MagicMocks in tests).
        self._handle_command = handle_command

    # ------------------------------------------------------------------
    # Universal entry point
    # ------------------------------------------------------------------

    def handle_command(self, command: "Command") -> "ValidationResult":
        """Execute a command against the game session."""
        return self._state._session.handle_command(command)

    # ------------------------------------------------------------------
    # Dispatch resolver (PROJ-363 Phase 4)
    # ------------------------------------------------------------------
    #
    # Every legacy ``dispatch_*_command(...)`` helper is now resolved
    # against ``COMMAND_SPECS``. The 31 hand-written one-liners
    # (~200 LOC of pure boilerplate) collapse to this single resolver
    # plus the ``handle_command`` entry point above.
    #
    # ``__getattr__`` is only consulted when normal attribute lookup
    # fails. ``__slots__`` does NOT block ``__getattr__`` resolution; it
    # only blocks setting *instance* attributes whose names aren't in the
    # slots tuple. The resolver returns a fresh closure on every call —
    # there's no caching needed because the closure is cheap and the
    # call sites resolve once per UI action.
    #
    # Naming scheme: ``dispatch_<helper_name>`` where ``<helper_name>``
    # matches the ``facade_helper_name`` field on the relevant
    # ``CommandSpec``. Specs without a ``facade_helper_name`` (currently:
    # SetGravity/Water/RadiationShieldTargetCommand and
    # SetBuildQueuePausedCommand) intentionally have no UI dispatch
    # path; calling those names raises ``AttributeError`` like any
    # missing method.

    def __getattr__(self, name: str):  # noqa: D401 — Python protocol method
        if not name.startswith("dispatch_"):
            raise AttributeError(
                f"{type(self).__name__!r} object has no attribute {name!r}"
            )
        # Deferred import: the registry lives downstream in the engine
        # graph; importing it at module load would couple the facade to
        # engine internals at import time.
        from game.strategy.engine.commands.registry import (
            command_registry,
            seed_default_commands,
        )

        if len(command_registry) == 0:
            seed_default_commands(command_registry)

        global _specs_cache
        if _specs_cache is None:
            _specs_cache = command_registry.specs_by_facade_helper()
        spec = _specs_cache.get(name)
        if spec is None:
            raise AttributeError(
                f"{type(self).__name__!r} object has no attribute {name!r}: "
                f"no CommandSpec entry has facade_helper_name={name!r}."
            )
        command_class = spec.command_class
        handle_command = self._handle_command

        def _dispatch(**kwargs) -> ValidationResult:
            return handle_command(command_class(**kwargs))

        _dispatch.__name__ = name
        _dispatch.__qualname__ = f"{type(self).__name__}.{name}"
        _dispatch.__doc__ = (
            f"Dispatch {command_class.__name__} via the spec-driven resolver "
            f"(PROJ-363)."
        )
        return _dispatch
