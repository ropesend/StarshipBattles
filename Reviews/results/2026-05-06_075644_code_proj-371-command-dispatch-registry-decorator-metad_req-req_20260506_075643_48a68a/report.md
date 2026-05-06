# Review Report: PROJ-371 Command Dispatch Registry

**Request ID:** req_20260506_075643_48a68a
**Review Type:** code
**Review Mode:** normal
**Scope:** Three commits on `feat/03c-phase-aware-execution` — full Phase 1-3 implementation of PROJ-371
**Completed:** 2026-05-06T08:15:00Z

## Findings Summary

| Severity | Count |
|----------|-------|
| CRIT | 0 |
| MAJ | 0 |
| MIN | 3 |
| INFO | 8 |

---

## Focus Area 1: Decorator-as-metadata-only contract

**INFO: Verified clean.** `command_spec()` at `game/strategy/engine/commands/registry.py:283` attaches `handler_cls.__command_spec_kwargs__ = spec_kwargs` and returns the class unchanged — no call to `command_registry.register()`. The TDD test `test_import_handler_module_does_not_register` at `tests/unit/strategy/engine/test_command_registry_seeding.py:85` snapshots `command_registry._specs`, imports `game.strategy.engine.handlers.build`, and asserts the dict is identical before/after. A second test `test_decorator_returns_handler_class_unchanged` at line 67 explicitly confirms the decorator returns the same class object (`assert decorated is Marker`) and attaches `__command_spec_kwargs__`. If the decorator did register at import time, both tests would fail — the first because `_specs` would gain entries, the second because the class identity check passes regardless (the decorator is transparent), but the side-effect mutation would be caught by the import test.

**Confirmed invariant:** Importing any handler module does not mutate `command_registry._specs`. Registration is gated behind `seed_default_commands()`.

---

## Focus Area 2: Reset/seed cycle correctness

**INFO: Verified clean.** `reset_command_registry()` at `registry.py:362` clears `command_registry._specs.clear()` and calls `seed_default_commands(command_registry)`, which imports 7 handler modules via local imports (line 339-349) and calls each module's `register(registry)`. No `_SEEDED` flag, no `importlib.reload`. The round-trip test `test_round_trip_reset_then_seed` at `test_command_registry_seeding.py:107` asserts `len(command_registry) == 35` both before and after reset.

**Test fixture isolation:** The test module's autouse `_seeded_registry` fixture (line 35-43) snapshots `command_registry._specs` before each test, clears the registry, seeds defaults, and restores the snapshot after `yield`. This provides per-test isolation within the seeding test file. However, no equivalent autouse fixture exists in the global `tests/conftest.py` or `tests/unit/strategy/conftest.py`. Tests in other modules that mutate the registry (e.g. the third-party smoke test via `temporary_command()` context manager) rely on their own cleanup — `temporary_command()` at `tests/fixtures/command_registry.py:20` does snapshot/restore correctly. Cross-module registry state leakage is theoretically possible (Test A mutates, Test B doesn't reset before use) but in practice is contained because:
- The registry is import-time-seeded once (via `_install_dispatch_forwarders()` at facade import); seeds only when a consumer calls `seed_default_commands`.
- Most tests use the registry as a read-only data source.
- Tests that write use snapshot/restore.

No reset-to-default fixture found in global conftest; this is acceptable since the registry is seeded once at import and tests that modify it do their own cleanup.

---

## Focus Area 3: Facade forwarder collapse — class-level `_install_dispatch_forwarders` vs `__getattr__`

**INFO: Verified functionally clean.** The implementation at `strategy_session_facade.py:390-434` uses a module-level `_install_dispatch_forwarders()` call (line 434) that iterates `command_registry.all()`, extracts `spec.facade_helper_name`, and does `setattr(StrategySessionFacade, helper, _make_forwarder(helper))`. This creates 31 real bound methods on the class — not via `__getattr__` as the design.md recommended.

**Why the deviation is correct:**
- `hasattr(StrategySessionFacade, name)` works because the methods are actual class attributes.
- `inspect.getmembers` and `inspect.isfunction` both see them.
- `test_strategy_session_facade_public_api.py` passes because its `hasattr` and `inspect.getmembers` checks find the forwarders.
- Monkey-patching at instance scope works because Python's descriptor protocol creates bound methods from `setattr` on the class — `facade.dispatch_issue_move = MagicMock(...)` shadows the class method with an instance attribute.
- Self-binding works: `dispatch_method(**kwargs)` correctly proxies to `self._command_slice.<helper_name>(**kwargs)`.
- Docstrings are set (`_dispatch.__doc__` = f"Helper to dispatch..."), though they're brief. No return-type annotation on the generated `_dispatch` closure (see MIN-003).

**MIN-001 (MIN): Deviation from `__getattr__` to `_install_dispatch_forwarders()` not documented in `decisions.md`.**
- **File:** `Projects/active_projects/PROJ-371/decisions.md` (line 21 entry still says `__getattr__`)
- **Detail:** The 2026-05-05 decision entry at line 21 states "collapses to `__getattr__`" and the plan.md lines 62, 78 also prescribe `__getattr__`. The actual implementation uses module-level `setattr` on the class. While the choice is justified (hasattr/inspect visibility), the deviation was not recorded.
- **Remediation:** Add a decisions.md entry noting the deviation and rationale: "2026-05-06: Used `_install_dispatch_forwarders()` (class-level `setattr` loop) instead of `__getattr__` because `hasattr(StrategySessionFacade, name)` and `inspect.getmembers` require class-level visibility for the public-API contract test."

---

## Focus Area 4: `COMMAND_SPECS` tuple deletion (`specs.py` deleted)

**INFO: Verified clean.** `game/strategy/engine/commands/specs.py` does not exist (`ls` returns "No such file or directory"). Grep of `game/` finds only comment references to `COMMAND_SPECS` — no imports of `specs.py`, no runtime references to the module. In `tests/`, the variable name `COMMAND_SPECS` is used as a local derived value: `COMMAND_SPECS: tuple[CommandSpec, ...] = tuple(command_registry.all())` (in `test_command_specs_contract.py:35` and `test_command_dispatch_slice_getattr.py:31`).

**AST regression test:** `test_no_specs_tuple_literal.py:47` walks every `*.py` under `game/` and scans for `ast.Assign` with a `Tuple` RHS containing `Call(func=Name(id='CommandSpec'))` elements. Self-tests prove:
- `test_walker_flags_synthetic_command_spec_tuple` (line 77): positive tuple IS flagged.
- `test_walker_does_not_flag_unrelated_tuple` (line 89): non-CommandSpec tuples NOT flagged.
- `test_walker_does_not_flag_command_spec_in_other_context` (line 96): `CommandSpec(...)` in `register()` function calls NOT flagged.

The walker skips `__pycache__` dirs and ignores `SyntaxError` files. It correctly operates only on `game/` production code, not `tests/`.

---

## Focus Area 5: Consumer migrations

**INFO: Verified clean.** All three consumers migrated correctly:

1. **`registry_factory.py`** (handlers/registry_factory.py:20-44): Imports `command_registry` from `registry.py`, calls `seed_default_commands()` if empty (0-length guard at line 38-39), then iterates `command_registry.all()` to build the runtime `CommandHandlerRegistry`. The 0-length guard provides idempotency. Equivalent to old behavior: `for spec in COMMAND_SPECS:` → `for spec in command_registry.all():`.

2. **`action_time_resolver.py`** (services/action_time_resolver.py:39-50): `ORDER_TO_ABILITY_MAP` is built via `_build_order_to_ability_map()` which imports `command_registry`, seeds if empty, and calls `command_registry.order_to_ability_map()`. The old redundant local `MOVEMENT_ORDER_TYPES` frozenset (previously at line 48, missing WARP) is **deleted** — the module now imports `MOVEMENT_ORDER_TYPES` from `data/order_types.py:24` (the canonical authoritative set). `order.type in MOVEMENT_ORDER_TYPES` check at line 86 uses the canonical set.

3. **`command_dispatch_slice.py`** (facade/slices/command_dispatch_slice.py:73-107): `__getattr__` resolver imports `command_registry`, seeds if empty (line 86-87), then looks up `command_registry.specs_by_facade_helper().get(name)`. Equivalent to old behavior which read from `specs.specs_by_facade_helper().get(name)`.

**Tuple-specific features preserved:** Insertion order is maintained (Python 3.7+ `dict` preserves insertion order). The `command_registry.all()` iterator yields specs in registration order, matching the old tuple's iteration semantics. No consumer relied on slicing or length checks beyond iteration; the registry exposes `__len__` and `all()` for those cases.

---

## Focus Area 6: WARP silent-drift cleanup

**INFO: Verified clean.** Before PROJ-371, `action_time_resolver.py:48` held a local `MOVEMENT_ORDER_TYPES = frozenset({MOVE, MOVE_TO_FLEET})` that was missing `WARP`. This was silently divergent from `data/order_types.py:58-62` which correctly includes `WARP`. After Phase 2 migration:
- The local frozenset at `action_time_resolver.py:48` is deleted. ✓
- `action_time_resolver.py:24-27` imports `MOVEMENT_ORDER_TYPES` directly from `data/order_types` (the canonical source). ✓
- Line 86: `if order.type in MOVEMENT_ORDER_TYPES: return 0` now correctly includes WARP — movement engine handling of WARP orders is accurately reflected. ✓

**Stale copies elsewhere:** A quick scan of the codebase did not find other stale local copies of these frozensets. The three frozensets at `data/order_types.py:58-86` are the canonical sources, imported directly by consumers.

---

## Focus Area 7: Cross-project handler-file overlap

**INFO: Verified clean.** PROJ-371 touches handler files also in PROJ-370's scope (`handlers/base.py`, `handlers/build.py`, `handlers/movement.py`, `handlers/order_queue.py`, `planet_command_handlers.py`). The changes are limited to:
- Adding an `@command_spec(...)` decorator above each handler class (metadata-only, attaches `__command_spec_kwargs__`).
- Adding a `register(registry: CommandRegistry) -> None` function that reads the metadata and calls `registry.register(CommandSpec(handler_class=H, **H.__command_spec_kwargs__))`.

No new write paths, no business-logic changes, no mutator-protocol additions. PROJ-370 can proceed without conflicts.

---

## Focus Area 8: General code hygiene

**MIN-002 (MIN): `command_spec()` missing return-type annotation.**
- **File:** `game/strategy/engine/commands/registry.py:283`
- **Detail:** Public function `command_spec(**spec_kwargs)` returns a callable (decorator factory). Return type should be `Callable[[type[ICommandHandler]], type[ICommandHandler]]` or at minimum `Callable[[type], type]`.
- **Remediation:** Add return-type annotation. Example: `def command_spec(**spec_kwargs) -> Callable[[type], type]:`

**MIN-003 (MIN): Generated `_dispatch` closures in `_install_dispatch_forwarders()` lack return-type annotation.**
- **File:** `game/strategy/facade/strategy_session_facade.py:415`
- **Detail:** The auto-generated `_dispatch` closures installed as `dispatch_*` methods lack an explicit `-> ValidationResult` return-type annotation. Since `mypy` and static analysis tools only see `Callable[..., Any]` here, the facade's public API contract is weakening.
- **Remediation:** Add `-> ValidationResult` to the `_dispatch` signature: `def _dispatch(self, **kwargs) -> ValidationResult:`

**INFO: LOC limits.** `registry.py` is 382 lines — under the 500 LOC ceiling. `strategy_session_facade.py` is 434 lines — under 500 LOC ceiling. No production file in scope exceeds 500 LOC.

**INFO: Exception hygiene.** No broad `except Exception` without `# Intentional` comment found in the changed files.

**INFO: Layering.** No layering violations found. The decorator/registry lives in `game/strategy/engine/commands/` (strategy engine layer). Consumers import from there via deferred imports where necessary (e.g., `registry_factory.py:33`, `action_time_resolver.py:40`, `command_dispatch_slice.py:81`).

**INFO: `__init__.py` module export.** `game/strategy/engine/commands/__init__.py` defines DTO dataclasses. `registry.py` lives alongside but is imported separately. No `__all__` or re-export issue — the DTO module and registry module are cleanly separated.

---

## Verification Matrix

Not applicable — this is an initial review, not a follow-up.
