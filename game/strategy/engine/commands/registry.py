"""Self-registering command dispatch registry (PROJ-371).

Single source of truth for the metadata that previously lived in the
hardcoded ``COMMAND_SPECS`` tuple at ``commands.specs``. PROJ-371
turns the table into a self-registering :class:`CommandRegistry`
populated by the :func:`command_spec` decorator on each handler class
plus an explicit per-module ``register(registry)`` function.

**Decorator-as-metadata-only contract (r004).** ``@command_spec(...)``
attaches ``__command_spec_kwargs__`` to the decorated handler class and
returns the class **unchanged**. It does NOT call
``command_registry.register(...)`` at class-definition time. Each
handler module exposes a ``register(registry)`` function that calls
``registry.register(CommandSpec(handler_class=H,
**H.__command_spec_kwargs__))``. :func:`seed_default_commands` imports
the handler modules (forces the decorator metadata to attach) and then
calls each module's ``register()``. :func:`reset_command_registry`
clears all entries and reseeds via :func:`seed_default_commands`.

The metadata-only design avoids a duplicate-registration foot-gun
where the decorator AND ``seed_default_commands`` would both register
after a reset (decorators do not re-run on cached imports, so importing
again is a no-op for registration).

Naming note: this is *different* from
:class:`game.strategy.engine.handlers.base.CommandHandlerRegistry`,
which is the runtime dispatch table that maps Command DTO names to
handler instances. The registry here is the *metadata* registry that
records which handler class owns which Command DTO.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Iterable, Type, TypeVar

# Bound to ``type`` (rather than ``type[ICommandHandler]``) so test fixtures
# can decorate plain marker classes without forcing the full handler protocol.
_HandlerT = TypeVar("_HandlerT", bound=type)

from game.strategy.data.order_types import OrderType

if TYPE_CHECKING:
    from game.strategy.engine.commands import Command
    from game.strategy.engine.handlers.base import ICommandHandler


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Allowed values (moved from specs.py).
# ---------------------------------------------------------------------------

ALLOWED_CATEGORIES = frozenset({
    'movement', 'action', 'superweapon', 'planet',
    'build', 'construction', 'fleet_management',
})
ALLOWED_EXECUTION_MODELS = frozenset({
    'action', 'production', 'instant', 'mission', 'planet',
})


# ---------------------------------------------------------------------------
# CommandSpec (moved from specs.py).
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CommandSpec:
    """Declarative metadata for a single Command DTO.

    Args:
        command_class: The Command DTO type (e.g. ``IssueMoveCommand``).
        order_type: The OrderType this command emits, or ``None`` for
            mission commands (which decompose into MOVE+ACTION at
            handler-execution time and have no single OrderType).
        handler_class: The handler type registered for this command.
        category: One of ``ALLOWED_CATEGORIES``. Drives the order-type
            frozensets generated in ``order_types.py``.
        subcategories: Free-form tags for cross-cutting groupings.
        action_ability_name: The component-ability name in
            components.json that supplies ``action_time``. ``None`` for
            commands that don't go through ActionExecutionEngine.
        execution_model: One of ``ALLOWED_EXECUTION_MODELS``.
        facade_helper_name: The ``dispatch_*_command`` method name on
            ``CommandDispatchSlice``. ``None`` for commands without a
            UI dispatch entry point.
        serializer_codec: Documentation-only tag identifying the
            ``Order.target`` codec used for save serialization.
    """
    command_class: Type["Command"]
    order_type: OrderType | None
    handler_class: Type["ICommandHandler"]
    category: str
    subcategories: frozenset[str] = field(default_factory=frozenset)
    action_ability_name: str | None = None
    execution_model: str = 'action'
    facade_helper_name: str | None = None
    serializer_codec: str | None = None

    def __post_init__(self) -> None:
        if self.category not in ALLOWED_CATEGORIES:
            raise ValueError(
                f"CommandSpec({self.command_class.__name__}): "
                f"category {self.category!r} not in ALLOWED_CATEGORIES."
            )
        if self.execution_model not in ALLOWED_EXECUTION_MODELS:
            raise ValueError(
                f"CommandSpec({self.command_class.__name__}): "
                f"execution_model {self.execution_model!r} not in "
                f"ALLOWED_EXECUTION_MODELS."
            )


# ---------------------------------------------------------------------------
# IMPLICIT_ACTION_ORDER_TYPES (moved from specs.py).
# ---------------------------------------------------------------------------
#
# OrderTypes that are *implicitly* action orders even though no Command
# DTO carries them as a primary ``order_type``. These get folded into
# ``ACTION_ORDER_TYPES`` but have their own dispatch path:
# - LOAD_POPULATION / UNLOAD_POPULATION: emitted by IssueTransferCommand
#   handler when direction='load'/'unload' (transfer-based, but
#   classified as their own action order types for engine routing).
# - ACTIVATE_ABILITY / DEACTIVATE_ABILITY: multiplexed by
#   IssuePlanetOrderCommand based on the order_type string field.
IMPLICIT_ACTION_ORDER_TYPES: frozenset[OrderType] = frozenset({
    OrderType.LOAD_POPULATION,
    OrderType.UNLOAD_POPULATION,
    OrderType.ACTIVATE_ABILITY,
    OrderType.DEACTIVATE_ABILITY,
})


# ---------------------------------------------------------------------------
# CommandRegistry.
# ---------------------------------------------------------------------------

class CommandRegistry:
    """Mutable registry for :class:`CommandSpec` rows.

    Populated by :func:`seed_default_commands`. Iteration order =
    insertion order (Python dict, 3.7+). The decorator-metadata-only
    contract means importing handler modules does NOT mutate this
    registry — only :func:`seed_default_commands` does, and it can be
    called any number of times via :func:`reset_command_registry`.
    """

    __slots__ = ("_specs",)

    def __init__(self) -> None:
        self._specs: dict[str, CommandSpec] = {}

    # ------------------------------------------------------------------
    # Mutation API.
    # ------------------------------------------------------------------

    def register(self, spec: CommandSpec, *, replace: bool = False) -> None:
        """Add ``spec`` to the registry.

        Args:
            spec: The CommandSpec to register.
            replace: If False (default), raise :class:`ValueError` when
                a spec is already registered for ``spec.command_class``.
                If True, overwrite the existing entry and emit a WARNING.
        """
        name = spec.command_class.__name__
        if name in self._specs and not replace:
            raise ValueError(
                f"Command {name!r} already registered. Pass replace=True "
                f"to override (e.g. for mod overlays)."
            )
        if name in self._specs and replace:
            logger.warning(
                "CommandRegistry: replacing %r (was %r, now %r)",
                name,
                self._specs[name].handler_class.__name__,
                spec.handler_class.__name__,
            )
        self._specs[name] = spec

    def unregister(self, command_name: str) -> CommandSpec | None:
        """Remove the spec for ``command_name`` and return it.

        Returns ``None`` if no entry exists. Public for test fixtures;
        production code never unregisters.
        """
        return self._specs.pop(command_name, None)

    # ------------------------------------------------------------------
    # Read API.
    # ------------------------------------------------------------------

    def all(self) -> Iterable[CommandSpec]:
        """Iterate every registered :class:`CommandSpec`."""
        return self._specs.values()

    def get(self, command_name: str) -> CommandSpec | None:
        return self._specs.get(command_name)

    def __len__(self) -> int:
        return len(self._specs)

    def __contains__(self, command_name: object) -> bool:
        return command_name in self._specs

    # ------------------------------------------------------------------
    # Derived views (migrated from specs.py module functions).
    # ------------------------------------------------------------------

    def specs_by_command_name(self) -> dict[str, CommandSpec]:
        """Map ``CommandClass.__name__`` -> CommandSpec."""
        return dict(self._specs)

    def specs_by_facade_helper(self) -> dict[str, CommandSpec]:
        """Map ``facade_helper_name`` -> CommandSpec.

        Excludes specs without a facade helper (None entries).
        """
        return {
            s.facade_helper_name: s
            for s in self._specs.values()
            if s.facade_helper_name is not None
        }

    def order_types_for_category(self, category: str) -> frozenset[OrderType]:
        """All non-None OrderTypes for specs in ``category``."""
        return frozenset(
            s.order_type for s in self._specs.values()
            if s.category == category and s.order_type is not None
        )

    def movement_order_types(self) -> frozenset[OrderType]:
        """Derive the ``MOVEMENT_ORDER_TYPES`` set.

        Includes only specs in the 'movement' category whose
        ``execution_model`` is 'action'.
        """
        return frozenset(
            s.order_type for s in self._specs.values()
            if s.category == 'movement'
            and s.order_type is not None
            and s.execution_model == 'action'
        )

    def action_order_types(self) -> frozenset[OrderType]:
        """Derive the ``ACTION_ORDER_TYPES`` set.

        Includes 'action'/'superweapon' specs plus the implicit
        order types for population transfers and ability toggles.
        """
        explicit = frozenset(
            s.order_type for s in self._specs.values()
            if s.category in ('action', 'superweapon')
            and s.order_type is not None
            and s.execution_model == 'action'
        )
        return explicit | IMPLICIT_ACTION_ORDER_TYPES

    def planet_action_order_types(self) -> frozenset[OrderType]:
        """OrderTypes routed through ``PlanetActionEngine``."""
        return frozenset({
            OrderType.ACTIVATE_ABILITY,
            OrderType.DEACTIVATE_ABILITY,
        })

    def order_to_ability_map(self) -> dict[OrderType, str]:
        """Map OrderType -> ability name for action-time lookups."""
        return {
            s.order_type: s.action_ability_name
            for s in self._specs.values()
            if s.order_type is not None and s.action_ability_name is not None
        }


# ---------------------------------------------------------------------------
# Global singleton — commands are global, no DI required.
# ---------------------------------------------------------------------------

command_registry = CommandRegistry()


# ---------------------------------------------------------------------------
# @command_spec decorator (METADATA-ONLY — r004 refinement).
# ---------------------------------------------------------------------------

def command_spec(**spec_kwargs) -> Callable[[_HandlerT], _HandlerT]:
    """Attach :class:`CommandSpec` kwargs to the decorated handler class.

    **METADATA-ONLY.** Returns the class unchanged. Does NOT call
    :meth:`CommandRegistry.register` at class-definition time.

    Each handler module exposes ``def register(registry)`` that reads
    the metadata from ``HandlerClass.__command_spec_kwargs__`` and
    invokes ``registry.register(CommandSpec(handler_class=HandlerClass,
    **HandlerClass.__command_spec_kwargs__))``.
    :func:`seed_default_commands` calls those per-module ``register()``
    functions in turn.

    Why metadata-only?

    - Re-importing already-imported modules does not re-run decorators
      (Python caches via ``sys.modules``). If the decorator registered
      at import time, :func:`reset_command_registry` could not actually
      reseed the registry after a clear.
    - If both the decorator AND ``seed_default_commands()`` registered,
      a second seed call after a clear would double-register entries.

    The metadata-only decorator + explicit per-module ``register()`` is
    the only shape that survives clear-and-reseed cleanly.

    Usage:
        @command_spec(command_class=IssueFooCommand,
                      order_type=OrderType.FOO,
                      category='action',
                      execution_model='action',
                      facade_helper_name='dispatch_issue_foo')
        class FooCommandHandler(BaseCommandHandler):
            ...
    """
    def _wrap(handler_cls: _HandlerT) -> _HandlerT:
        handler_cls.__command_spec_kwargs__ = spec_kwargs
        return handler_cls
    return _wrap


# ---------------------------------------------------------------------------
# Seeding / reset helpers.
# ---------------------------------------------------------------------------

def seed_default_commands(registry: CommandRegistry) -> None:
    """Import handler modules and call each module's ``register(registry)``.

    The metadata-only :func:`command_spec` decorator means importing a
    handler module does NOT mutate ``registry``. Mutation happens here,
    once per call to this function. Safe to call repeatedly only in
    combination with a preceding clear (see
    :func:`reset_command_registry`).
    """
    # Local imports to avoid module-load-time cycles. The handler
    # modules import from this module (for the decorator), so importing
    # them at the top of registry.py would create a circle.
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
        module.register(registry)


def reset_command_registry() -> None:
    """Test helper: clear the global registry and reseed defaults.

    Mirrors PROJ-367's ``reset_stat_contributor_registry``. No
    ``_SEEDED`` flag, no ``importlib.reload``.
    """
    command_registry._specs.clear()
    seed_default_commands(command_registry)


__all__ = [
    'ALLOWED_CATEGORIES',
    'ALLOWED_EXECUTION_MODELS',
    'CommandSpec',
    'CommandRegistry',
    'IMPLICIT_ACTION_ORDER_TYPES',
    'command_registry',
    'command_spec',
    'seed_default_commands',
    'reset_command_registry',
]
