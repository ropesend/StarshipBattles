# PROJ-371: Design — Strategy Command Dispatch Registry

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source: strategy-layer tech-debt review

`AgentCoordination/Scratchpad/reviews/strategy_layer_tech_debt_2026-05-05.md:73-91`
flagged `game/strategy/engine/commands/specs.py` (661 LOC, 35 spec rows) as the
#4 extensibility target. Headline issue: "no extension hook for mods" and "8
edits across 3-5 files to add a new command."

## Initial analysis (corrects the review's count)

The review's 8-edit claim **pre-dates PROJ-363**, which already collapsed 7 of
the 8 surfaces into the single `COMMAND_SPECS` tuple. The remaining duplication
is:

1. The `COMMAND_SPECS` tuple itself — a hardcoded literal in `specs.py`. Adding
   a 36th command requires editing `specs.py` to append a row. There is no
   programmatic registration; mods cannot inject a command.
2. `game/strategy/facade/strategy_session_facade.py:186-300` — 31 hand-written
   one-line `dispatch_*` forwarders. The slice has `__getattr__`
   (`game/strategy/facade/slices/command_dispatch_slice.py:72`); the outer
   facade was missed by PROJ-363 Phase 4.
3. Three module-level frozensets (`MOVEMENT_/ACTION_/PLANET_ACTION_ORDER_TYPES`)
   live in `game/strategy/data/order_types.py:58-86` AND a fourth in
   `game/strategy/services/action_time_resolver.py:48` (silently divergent — it
   lacks `WARP`). The `data/order_types.py` set is pinned to `specs.py` via
   `tests/unit/strategy/engine/test_command_specs_contract.py:135-152`. The
   `action_time_resolver.py` local copy is unpinned and dead-coded (line 79
   reads it but the test contract demands it match
   `data/order_types.MOVEMENT_ORDER_TYPES`).

See `findings/initial_review.md` for the full inventory + the line-by-line
"8 edits" mapping.

## Today's vs target registration

### Today

```python
# game/strategy/engine/commands/specs.py — append a row in the literal tuple
COMMAND_SPECS: tuple[CommandSpec, ...] = (
    # ... 35 existing rows ...
    CommandSpec(
        command_class=NewFooCommand,
        order_type=OrderType.FOO,
        handler_class=FooCommandHandler,
        category='action',
        # ... 6 more fields ...
    ),
)
```

Plus: define DTO in `commands/__init__.py`, define handler in
`engine/handlers/<domain>.py`, append OrderType + frozenset entries (if new),
add a one-line forwarder in `strategy_session_facade.py`. Mods cannot extend
this — `tuple` is immutable and `specs.py` is repo-owned code.

### Target

```python
# game/strategy/engine/handlers/foo.py — handler module owns its registration
from game.strategy.engine.commands import NewFooCommand
from game.strategy.engine.commands.registry import command_spec
from game.strategy.engine.handlers.base import BaseCommandHandler, ICommandHandler
from game.strategy.data.order_types import OrderType

@command_spec(
    command_class=NewFooCommand,
    order_type=OrderType.FOO,
    category='action',
    action_ability_name='Foo',
    execution_model='action',
    facade_helper_name='dispatch_issue_foo',
    serializer_codec='planet_ref',
)
class FooCommandHandler(BaseCommandHandler):
    def execute(self, session, command): ...
```

Adding a 36th command is one new file. The decorator instantiates the handler
class and registers a `CommandSpec` into the global `command_registry`. Mods
register the same way.

## Architecture

### Module layout

```
game/strategy/engine/commands/
    __init__.py        # DTOs (unchanged from today)
    specs.py           # CURRENT — tuple literal of 35 CommandSpec rows
    registry.py        # NEW — CommandRegistry class + decorator + global instance
```

After Phase 2, `specs.py` is **deleted**: every `CommandSpec` lives next to its
handler, registered via decorator. Helper functions (`movement_order_types()`,
`order_to_ability_map()`, etc.) move to `registry.py` as instance methods on
the singleton.

### `CommandRegistry`

```python
# game/strategy/engine/commands/registry.py
from __future__ import annotations
from dataclasses import dataclass
import logging
from typing import Callable, Iterable, Type

from game.strategy.engine.commands import Command
from game.strategy.engine.handlers.base import ICommandHandler
from game.strategy.data.order_types import OrderType


logger = logging.getLogger(__name__)


# Reuse the existing CommandSpec dataclass (today at specs.py:152). Move the
# class declaration into registry.py at Phase 1 Task 1.2; specs.py keeps the
# data tuple for one phase of overlap before being deleted at Phase 2.

@dataclass(frozen=True)
class CommandSpec:
    command_class: Type[Command]
    order_type: OrderType | None
    handler_class: Type[ICommandHandler]
    category: str
    subcategories: frozenset[str] = frozenset()
    action_ability_name: str | None = None
    execution_model: str = 'action'
    facade_helper_name: str | None = None
    serializer_codec: str | None = None
    # ... __post_init__ unchanged from specs.py:198-210


class CommandRegistry:
    """Mutable registry for CommandSpec rows.

    Self-registration via @command_spec decorator at handler module import time.
    Helper functions (movement_order_types, etc.) are instance methods.
    Iteration order = registration order (insertion-ordered dict, Python 3.7+).
    """

    __slots__ = ("_specs",)

    def __init__(self) -> None:
        self._specs: dict[str, CommandSpec] = {}

    def register(self, spec: CommandSpec, *, replace: bool = False) -> None:
        name = spec.command_class.__name__
        if name in self._specs and not replace:
            raise ValueError(
                f"Command {name!r} already registered. Pass replace=True to "
                f"override (e.g. for mod overlays)."
            )
        if name in self._specs and replace:
            logger.warning(
                "CommandRegistry: replacing %r (was %r, now %r)",
                name, self._specs[name].handler_class.__name__,
                spec.handler_class.__name__,
            )
        self._specs[name] = spec

    def all(self) -> Iterable[CommandSpec]:
        return self._specs.values()

    def get(self, command_name: str) -> CommandSpec | None:
        return self._specs.get(command_name)

    # Existing helper functions migrate from specs.py as instance methods:
    def specs_by_command_name(self) -> dict[str, CommandSpec]: ...
    def specs_by_facade_helper(self) -> dict[str, CommandSpec]: ...
    def order_types_for_category(self, category: str) -> frozenset[OrderType]: ...
    def movement_order_types(self) -> frozenset[OrderType]: ...
    def action_order_types(self) -> frozenset[OrderType]: ...
    def planet_action_order_types(self) -> frozenset[OrderType]: ...
    def order_to_ability_map(self) -> dict[OrderType, str]: ...


# Global singleton — commands are global concepts, no DI needed.
command_registry = CommandRegistry()


def command_spec(**spec_kwargs):
    """Decorator: attach metadata to the decorated handler class.

    METADATA-ONLY. Does NOT call command_registry.register at import time.
    Each handler module exposes def register(registry) that reads the
    metadata and calls registry.register(...) explicitly. seed_default_commands
    drives those per-module register() functions.

    Usage:
        @command_spec(command_class=FooCommand, order_type=OrderType.FOO,
                      category='action', execution_model='action', ...)
        class FooCommandHandler(BaseCommandHandler):
            ...
    """
    def _wrap(handler_cls: Type[ICommandHandler]) -> Type[ICommandHandler]:
        # Metadata-only: attach kwargs, return class unchanged. No registry mutation.
        handler_cls.__command_spec_kwargs__ = spec_kwargs
        return handler_cls
    return _wrap
```

**Implementation note (r004 refinement).** Earlier draft (r001) relied on import-side-effect registration via `@command_spec`. Re-importing already-imported modules does not re-run decorators (Python caches via `sys.modules`), so `reset_command_registry()` could not actually reseed. r004 switches to explicit per-module `register()` functions called by `seed_default_commands()`, with the decorator metadata-only. If `@command_spec` had also registered at import time, `seed_default_commands(registry)` after reset would double-register. The metadata-only decorator + explicit `register()` is the only shape that survives reset cleanly.

### Seeding the registry — explicit per-module register()

The registry is populated by `seed_default_commands()` calling each handler
module's `register(registry)` function explicitly. The decorator is
metadata-only; it does not register at import time. This is the
duplicate-registration foot-gun mitigation: if the decorator ALSO registered
at import time AND `seed_default_commands()` called `register()`, a second
`seed_default_commands()` after a `reset_command_registry()` would
double-register. r004 makes the decorator metadata-only.

```python
# Each handler module owns a register(registry) function.
# Example for build.py:
def register(registry: CommandRegistry) -> None:
    registry.register(CommandSpec(
        handler_class=BuildOrderCommandHandler,
        **BuildOrderCommandHandler.__command_spec_kwargs__,
    ))
    registry.register(CommandSpec(
        handler_class=RemoveBuildOrderCommandHandler,
        **RemoveBuildOrderCommandHandler.__command_spec_kwargs__,
    ))

# registry.py
def seed_default_commands(registry: CommandRegistry) -> None:
    """Import handler modules (forces decorator metadata to attach) and
    call each module's register(registry).

    The metadata-only decorator means importing a handler module does NOT
    mutate the registry. Mutation happens here, exactly once per call.
    """
    from game.strategy.engine.handlers import (
        build, construction_queue, movement, order_queue, transfer,
    )
    from game.strategy.engine import (
        planet_command_handlers, superweapon_command_handlers,
    )
    for module in (
        build, construction_queue, movement, order_queue, transfer,
        planet_command_handlers, superweapon_command_handlers,
    ):
        module.register(registry)


def reset_command_registry() -> None:
    """Clear all entries and reseed via seed_default_commands.

    No _SEEDED flag, no importlib.reload, no import side effects.
    """
    command_registry._specs.clear()
    seed_default_commands(command_registry)
```

`registry_factory.py::create_default_registry` calls
`seed_default_commands(command_registry)` once at strategy-engine boot.

**This mirrors PROJ-367 conftest.py concern:** if a test resets the registry,
re-seeding must work. `reset_command_registry()` clears + re-seeds (same
idiom as `reset_stat_contributor_registry` per PROJ-367 decision-log entry
2026-05-05). r004 refinement: the decorator stays for human readability but
is *not* the wiring path — the wiring path is the per-module `register()`
function called by `seed_default_commands()`.

### Migration of consumer surfaces (Phase 2)

| File | Today | After Phase 2 |
|------|-------|--------------|
| `registry_factory.py:32-37` | `from .specs import COMMAND_SPECS; for spec in COMMAND_SPECS: ...` | `from .commands.registry import command_registry; for spec in command_registry.all(): ...` |
| `action_time_resolver.py:36-40` | `from .specs import order_to_ability_map; ORDER_TO_ABILITY_MAP = order_to_ability_map()` | `from .commands.registry import command_registry; ORDER_TO_ABILITY_MAP = command_registry.order_to_ability_map()` |
| `command_dispatch_slice.py:80-82` | `from .specs import specs_by_facade_helper; spec = specs_by_facade_helper().get(name)` | `from .commands.registry import command_registry; spec = command_registry.specs_by_facade_helper().get(name)` |
| `strategy_session_facade.py:186-300` | 31 hand-written `dispatch_*` forwarders | `__getattr__` that proxies to `self._command_slice.dispatch_*` (~10 LOC) |
| `data/order_types.py:58-86` | Three module-level frozensets pinned by contract test | UNCHANGED — kept as leaf-layer constants for import-graph reasons (`order_types.py` cannot import `commands.registry` without a cycle). The pin contract migrates from `specs.py` derivation to `command_registry.X()` derivation. |

### Phase plan rationale

**Phase 1 — Introduce the registry alongside the existing tuple.** Both
populate identically. Contract test asserts `set(specs_by_command_name()) ==
{spec.command_class.__name__ for spec in command_registry.all()}`. Zero
consumer migration; zero behaviour change. The decorator is *added* to handler
modules but the literal tuple in `specs.py` is *kept* as a redundancy, and a
new test asserts the two views are bit-identical.

**Phase 2 — Migrate consumers to the registry; delete the tuple.** Three
production consumers + the facade forwarder collapse + the AST regression test
forbidding any new `COMMAND_SPECS = (...)` tuple literal. After this phase,
`specs.py` is deleted; every `CommandSpec` row lives next to its handler.

**Phase 3 — Authoring rule + third-party command smoke test.** Document in
`docs/systems/strategy_layer.md` how mods register a command. Ship a smoke
test that registers a fake third-party command (`FakeModCommand` +
`FakeModCommandHandler`) at test setup time, dispatches it, asserts the
handler ran, and unregisters cleanly.

## Pattern source: PROJ-273 + PROJ-278

| Decision | PROJ-273 | PROJ-278 | PROJ-371 |
|---|---|---|---|
| Spec shape | Frozen dataclass | Frozen dataclass | Frozen dataclass (existing — `CommandSpec`) |
| Storage | Module-level `dict[str, AbilityStatMapping]` | `RoleRegistry` instance | `CommandRegistry` instance (singleton) |
| Registration | Hand-coded dict literal | `load_from_file(...)` + `add_user_role(...)` | Decorator on handler class |
| Conflict policy | None (single source) | `RegistrationConflictPolicy` enum | Boolean `replace=True` flag (commands are unique by DTO class; full enum is overkill) |
| Runtime add | No | `allow_runtime_add: bool` per instance | Yes — mods import their handler module |
| Coverage test | Glob-driven over `data/designs/qs_*_complex.json` | AST regression on `_role_from_instance_id` | AST regression forbidding `COMMAND_SPECS = (...)` tuple literal |
| Unknown-key WARN | `_log_unknown_stat_key_once` in `FleetAuraManager` | Sentinel "unknown role" with WARN log | `dispatch()` returns `ValidationResult.error("Unknown command type: ...")` (already exists at `handlers/base.py:389`) |
| Cache invalidation | None | `register_invalidation_callback` | None — registry is import-time-stable; no derived caches |

What transfers cleanly: the spec dataclass shape, the AST regression, the
decorator-based registration idiom (precedent in `STAT_CONTRIBUTOR_REGISTRY`).

What's command-specific: no need for `phase_order` (commands fan out 1-to-1),
no need for `RegistrationConflictPolicy` enum (boolean `replace=True` is
sufficient), no DI / cache invalidation (singleton + import-time-stable).

## Alternatives considered

### A. Leave as-is — accept the tuple, document the "append a row" workflow.
- Pro: no work.
- Con: closes the door on mod extension; the strategy-layer review explicitly
  flagged this. PROJ-363's consolidation is incomplete without a programmatic
  hook.
- **Rejected.**

### B. Decorator-only with no explicit `register()` call.
- Pro: minimal surface; one way to do it.
- Con: tests that need to register a one-off mock command for isolation
  (PROJ-371 Phase 3 smoke test) need a programmatic entry point. Decorator
  syntax forces a handler-class definition at module scope, which is wrong for
  test fixtures.
- **Rejected** — both `@command_spec(...)` decorator AND
  `command_registry.register(spec)` are public.

### C. Plugin-style entry-point loader (`importlib.metadata.entry_points`).
- Pro: separation between game and mod packages; mod ships a wheel.
- Con: massive over-engineering for a game with no current mod ecosystem. The
  existing pattern (mods are folders with JSON + Python files loaded at startup
  by `ApplicationContext`) doesn't use entry-points anywhere. PROJ-278 is the
  precedent; it loads from a folder.
- **Rejected.**

### D. Move handlers' `@command_spec` registration to a separate "registration
manifest" module (e.g. `commands/manifest.py`) instead of decorating handler
classes in their domain modules.
- Pro: decorator clutter stays out of the handler files; one file lists every
  registration call.
- Con: that's just `specs.py` with a slightly different idiom. The whole point
  is "metadata lives next to the handler so a single edit suffices."
- **Rejected.**

### E. Allow mods to register handlers WITHOUT a Command DTO (raw callable
handler).
- Pro: more flexible for tiny mods.
- Con: breaks the type contract. Today every dispatch goes through
  `command_class(__name__)` lookup; the DTO is required for serialization
  identity (even though commands aren't persisted today, `command.name`
  property at `commands/__init__.py:40` is read by logging hooks).
- **Rejected** — DTOs are mandatory.

### F. Make `CommandSpec.handler_class` optional and accept a `handler_factory`
callable instead.
- Pro: lets mods register stateful handlers (closure over mod-state).
- Con: today every handler is stateless and instantiated fresh per
  registration. Adding optionality complicates the type signature with no
  current consumer.
- **Deferred** — `handler_class` stays mandatory; future mod work can add
  `handler_factory: Callable[[], ICommandHandler] | None` if needed.

## Risks

- **R1: Save/replay determinism — N/A.** Verified: commands are NOT persisted
  to save files. Only `Order` objects are persisted
  (`game/strategy/data/order_types.py:108-181`). Registry insertion order
  matters only for human-readable logging and test reproducibility, not save
  correctness.
- **R2: Registry-not-seeded-at-import bugs.** PROJ-367 saw this concern with
  `reset_*_registry` in conftest. PROJ-371 mitigates by:
  - `seed_default_commands()` is idempotent (boolean guard).
  - `command_registry` is singleton-instantiated at module import.
  - `reset_command_registry()` (test helper) clears AND re-seeds.
  - Contract test asserts `len(command_registry.all()) == 35` immediately after
    `from game.strategy.engine.commands.registry import command_registry` —
    catches "imported the registry but didn't seed" mistakes at test start.
- **R3: Module circular imports.** `specs.py` already navigates this carefully
  (file:line `specs.py:14-22`); `registry.py` inherits the same constraint.
  `data/order_types.py` cannot import the registry (it's a leaf). The
  three frozensets there stay as plain constants pinned by contract test.
- **R4: `strategy_session_facade.py` `__getattr__` collapse and test
  monkey-patching.** Some tests do `facade.dispatch_issue_move = MagicMock(...)`
  at instance scope. With `__getattr__`, attribute *write* still works
  (Python's normal attribute machinery handles writes; `__getattr__` only
  intercepts misses on read). Verified by reading
  `command_dispatch_slice.py:27` — it has `__slots__` but `__getattr__`
  resolution still works for reads. The facade has no `__slots__`, so writes
  are even safer.
- **R5: AST regression false positives.** The "no tuple literal of CommandSpec
  rows" test must distinguish between the legitimate registration-result
  reading (e.g. `tests` that build a parametrize list) and the forbidden
  `COMMAND_SPECS = (CommandSpec(...), ...)` literal. Mitigation: walk only
  `game/` (production code), exclude `tests/`. Match the AST shape: an
  `ast.Assign` with a `Tuple` value of >0 `Call(func=Name('CommandSpec'))`
  elements at module scope.
- **R6: `specs.py` deletion timing.** During Phase 1 both surfaces coexist —
  the tuple in `specs.py` AND the decorator-driven registry. The spec module
  is deleted at Phase 2 close. If Phase 1 commits the decorator additions but
  Phase 2 stalls, the codebase is in an inconsistent state (two sources of
  truth). Mitigation: Phase 1 ALSO contains a contract test asserting
  bit-identity between the two views, so the inconsistency would surface
  immediately if either side drifted.

## Dependencies

- **PROJ-273** (closed) — pattern source for shared-registry idiom.
- **PROJ-278** (closed) — pattern source for `RoleRegistry` shape and AST
  regression test idiom.
- **PROJ-363** (closed) — landed the `COMMAND_SPECS` tuple. PROJ-371 is the
  natural sequel.
- **PROJ-364** (active) — `superweapon_registry.SUPERWEAPONS` is a sibling
  spec table for the 5 strategic superweapons. Cross-link asserted by
  `tests/unit/strategy/services/test_superweapon_registry_contract.py:149`.
  PROJ-371 must preserve this — the cross-link reads `COMMAND_SPECS` directly,
  so Phase 2's migration must update that test to read `command_registry.all()`.
- **PROJ-368** (planning) — sibling project, OrderProcessor decomposition into
  per-`OrderType` handlers. Different layer (one tier deeper than PROJ-371's
  per-Command handlers). PROJ-368 introduces an `OrderHandlerRegistry`
  per-`OrderType`; PROJ-371's `CommandRegistry` is per-Command. They do NOT
  share infrastructure; both are independently scoped. PROJ-371 should land
  first (smaller surface), or in parallel — there is no file-level conflict
  (PROJ-368 owns `order_processor.py` and a new `order_handlers/` package;
  PROJ-371 owns `commands/registry.py` and the `commands/specs.py` deletion).

## Open questions for the user

1. **Register decorator on handler class, or on a separate `@command_spec(...)`
   decorator that takes the handler as an argument?** The design above wraps
   the handler class. Alternative: factory function `register_command_handler(
   spec, handler_class)` called at module bottom. The decorator is more
   idiomatic; the function call is more explicit. **Recommendation:** decorator.
2. **Is "boolean `replace=True`" enough, or do we want the full PROJ-278
   `RegistrationConflictPolicy` enum?** Today there's no use case for APPEND
   semantics on commands (a Command DTO can have only one handler). The
   boolean is simpler. **Recommendation:** boolean for now; expand to enum
   only if a mod requires it.
3. **Should the global instance be `command_registry` (lower-case, singleton)
   or `COMMAND_REGISTRY` (upper-case, drop-in replacement for `COMMAND_SPECS`)?**
   PROJ-273 used UPPER (`ABILITY_STAT_REGISTRY`). PROJ-278 used lower
   (`design_role_registry`). PROJ-360 used UPPER (`STAT_CONTRIBUTOR_REGISTRY`).
   **Recommendation:** lower-case `command_registry` since it's a mutable
   stateful object, not an immutable constant. UPPER is misleading.
4. **Should the registry support `unregister(command_name)` for tests?** Yes,
   but only as a test helper at `tests/fixtures/`. Production code never
   unregisters. **Recommendation:** yes, gated behind a clear "test fixture"
   module name.
5. **Is the `action_time_resolver.py:48` local `MOVEMENT_ORDER_TYPES` frozenset
   in scope for deletion?** It's redundant with `data/order_types.py:58` and
   silently divergent (lacks `WARP`). Out of scope per the project description
   (PROJ-371 is registry-only) but it's a 3-line free-find. **Recommendation:**
   delete it in Phase 2 as part of the `action_time_resolver.py` migration —
   one extra line of test coverage.
6. **Phase count: 2 or 3?** Two phases (introduce registry + migrate consumers,
   then docs + smoke test) is tight. Three phases (introduce alongside,
   migrate, docs+smoke) gives a clean SHA-pinned review boundary between the
   "new infrastructure exists" and "old infrastructure deleted" states. The
   project description says "2-3 phases (this is smaller than its siblings)."
   **Recommendation:** 3 phases — the cumulative-review value of a midpoint
   gate outweighs the rigidity cost.
