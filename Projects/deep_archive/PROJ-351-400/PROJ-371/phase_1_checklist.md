# Phase 1: Introduce CommandRegistry alongside existing tuple

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-371 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** none
**Review Mode:** standard
**Files (planned):** `game/strategy/engine/commands/registry.py` (new), `game/strategy/engine/commands/specs.py` (modify — keep as redundant pin), `game/strategy/engine/handlers/{build,construction_queue,movement,order_queue,transfer}.py`, `game/strategy/engine/planet_command_handlers.py`, `game/strategy/engine/superweapon_command_handlers.py`, `tests/unit/strategy/engine/test_command_registry_seeding.py` (new)

**Objective:** Create `CommandRegistry` class + `command_registry` global +
`@command_spec(...)` decorator at `game/strategy/engine/commands/registry.py`.
Decorate all 35 handler classes. Keep `specs.py` tuple unchanged. Add a
contract test asserting bit-identity between the tuple and the registry.
**Zero consumer migration; zero behaviour change.**

---

## Pre-flight (TDD baseline)

- [ ] Run `python Tools/test_sharded/test_sharded.py` — capture baseline pass count and pin in plan.md Current State (memory says 15405 passing as of PROJ-311; verify the actual current number)
- [ ] `git status --short` — confirm no unrelated dirty files
- [ ] Read `findings/initial_review.md` — internalize the 35-spec inventory and consumer surface map
- [ ] Read PROJ-273 phase_1_checklist.md (registry-module pattern source)
- [ ] Read PROJ-278 phase_1_checklist.md (decorator + handle pattern source)
- [ ] Read `game/strategy/engine/commands/specs.py` (661 LOC) end-to-end — every CommandSpec field needs to be representable in the decorator
- [ ] Read `game/strategy/engine/handlers/*.py` — confirm handler-class signatures (no `__init__` arguments today)

---

## Tasks

**Task ordering (r004):** Define registry API → metadata-only decorator → import-doesn't-mutate test → per-module `register()` functions → `seed_default_commands` calls them → `reset_command_registry` = clear + seed.

### Task 1.1: Bit-identity contract test (TDD-first) [Simple]

**File:** `tests/unit/strategy/engine/test_command_registry_seeding.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/test_command_registry_seeding.py -v`

- [ ] Create the file with imports of both `COMMAND_SPECS` (from `specs.py`)
      and `command_registry` (from `commands.registry`).
- [ ] Add `test_registry_module_exists`: `from game.strategy.engine.commands import registry; assert hasattr(registry, 'command_registry')`. **Should fail** until Task 1.2 lands.
- [ ] Add `test_registry_yields_same_command_classes_as_tuple` (after seed): assert
      `{s.command_class.__name__ for s in COMMAND_SPECS} == {s.command_class.__name__ for s in command_registry.all()}`.
- [ ] Add `test_registry_specs_are_field_for_field_identical_to_tuple` (after seed):
      iterate by `command_class.__name__`, assert every field on every
      `CommandSpec` matches between the tuple and the registry view.
- [ ] Add `test_registry_count_is_35` (after seed): `assert len(list(command_registry.all())) == 35`.
- [ ] Add `test_decorator_returns_handler_class_unchanged`:
      ```python
      from unittest.mock import Mock
      from game.strategy.engine.commands.registry import command_spec
      Marker = type('Marker', (object,), {'X': 1})
      decorated = command_spec(command_class=Mock, order_type=None, category='action')(Marker)
      assert decorated is Marker  # decorator MUST return the class unchanged
      assert hasattr(decorated, '__command_spec_kwargs__')  # metadata attached
      ```
- [ ] Add `test_round_trip_reset_then_seed`:
      ```python
      from game.strategy.engine.commands.registry import (
          command_registry, reset_command_registry, seed_default_commands, CommandSpec,
      )
      seed_default_commands(command_registry)
      original_count = len(command_registry)
      reset_command_registry()
      assert len(command_registry) == original_count  # both default + replacement entries visible
      ```
- [ ] Add `test_explicit_duplicate_registration_raises`:
      ```python
      reset_command_registry()
      first = next(iter(command_registry.all()))
      import pytest
      with pytest.raises(ValueError):
          command_registry.register(first)  # default replace=False
      ```
- [ ] Run the file; **confirm Tasks 1.1's tests fail** with the right error
      (registry module does not exist yet).
- [ ] **Verify:** failures are for the right reason (ImportError on `registry` module).

**Notes:**

---

### Task 1.2: Create `CommandRegistry` module skeleton [Medium]

**File:** `game/strategy/engine/commands/registry.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/test_command_registry_seeding.py::test_registry_module_exists -v`

- [ ] Move the `CommandSpec` dataclass from `specs.py:152-210` to
      `registry.py` (verbatim — the dataclass shape is unchanged). Re-export it
      from `specs.py` as `from .registry import CommandSpec` so back-compat
      callers (the existing `COMMAND_SPECS` literal, the existing test imports)
      keep working through Phase 1.
- [ ] Move `ALLOWED_CATEGORIES` and `ALLOWED_EXECUTION_MODELS` frozensets
      (`specs.py:143-149`) to `registry.py`. Re-export from `specs.py`.
- [ ] Implement `class CommandRegistry` per `design.md` § "Architecture":
      - `__slots__ = ("_specs",)` — but ONLY if instance-level mutation never
        happens outside `register`/`unregister`. Verify in code review.
      - `__init__` — `self._specs: dict[str, CommandSpec] = {}`
      - `register(spec, *, replace=False)` — registers; raises `ValueError` on
        duplicate when `replace=False`; emits `logger.warning(...)` when
        `replace=True` AND the entry exists.
      - `unregister(command_name: str) -> CommandSpec | None` — returns the
        removed spec, or None if not present. Public for test fixtures.
      - `all() -> Iterable[CommandSpec]` — `return self._specs.values()`.
      - `get(command_name) -> CommandSpec | None`.
      - `__len__` — `return len(self._specs)`.
      - `__contains__(command_name)` — `return command_name in self._specs`.
- [ ] Migrate the 7 helper functions from `specs.py:544-645` as instance
      methods on `CommandRegistry`:
      `specs_by_command_name`, `specs_by_facade_helper`,
      `order_types_for_category`, `movement_order_types`, `action_order_types`,
      `planet_action_order_types`, `order_to_ability_map`. Keep the
      module-level functions in `specs.py` as one-line shims that read the
      registry (`return command_registry.movement_order_types()`) — back-compat
      for the duration of Phase 1.
- [ ] Implement `IMPLICIT_ACTION_ORDER_TYPES` move (`specs.py:581-586`) —
      stays as a module-level constant in `registry.py` (it's not derived from
      registry contents).
- [ ] Implement `command_registry = CommandRegistry()` at module scope.
- [ ] Implement `def command_spec(**fields)` decorator factory — **METADATA-ONLY** (r004 refinement). The decorator attaches `__command_spec_kwargs__` to the handler class and returns the class **unchanged**. It does NOT call `command_registry.register(...)` at class-definition time:
      ```python
      def command_spec(**fields):
          """Metadata-only sugar: attach kwargs, return class unchanged.
          NO registry mutation at import time.
          """
          def _wrap(handler_cls):
              handler_cls.__command_spec_kwargs__ = fields
              return handler_cls
          return _wrap
      ```
- [ ] Implement `seed_default_commands(registry)` — imports modules then calls each module's `register(registry)`. No `_SEEDED` flag; the function may be called multiple times (after `reset`):
      ```python
      def seed_default_commands(registry: 'CommandRegistry') -> None:
          """Import handler modules (forces decorator metadata to attach) and
          call each module's register(registry) function.

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
      ```
- [ ] Implement `reset_command_registry()` (test helper, NOT exported in
      production `__all__`): `command_registry._specs.clear(); seed_default_commands(command_registry)`. **No `_SEEDED` flag, no `importlib.reload`.**
- [ ] Define `__all__` listing all public names.
- [ ] Run `pytest tests/unit/strategy/engine/test_command_registry_seeding.py::test_registry_module_exists -v` — **must now pass**.
- [ ] **Verify:** `from game.strategy.engine.commands.registry import command_registry; assert len(command_registry) == 0` BEFORE any handler module is imported. The decorators have not run yet.

**Notes:** The `__slots__` choice is a minor perf win; if it complicates
testing-fixture monkey-patching, drop it. Document the choice in this
file's `Notes:` section.

---

### Task 1.2.5: Decorator-contract test — importing a handler module does NOT change `command_registry._specs` [Simple]

**File:** `tests/unit/strategy/engine/test_command_registry_seeding.py` (extend)
**Tests:** `pytest tests/unit/strategy/engine/test_command_registry_seeding.py::test_import_handler_module_does_not_register -v`

- [ ] Add a test that imports a handler module fresh and asserts the registry
      is unchanged across that import. The test pins the metadata-only
      decorator contract (r004 refinement) and is the regression guard
      against accidental "decorator registers at import time" reintroduction.
      ```python
      def test_import_handler_module_does_not_register():
          from game.strategy.engine.commands.registry import command_registry
          # Snapshot state BEFORE importing a handler module.
          before = dict(command_registry._specs)
          # Importing the module should attach decorator metadata to the
          # classes but NOT mutate the registry (decorator is metadata-only).
          import importlib
          importlib.import_module('game.strategy.engine.handlers.build')
          after = dict(command_registry._specs)
          assert before == after, (
              "Importing a handler module mutated command_registry._specs. "
              "The @command_spec decorator must be metadata-only (r004); "
              "registration only happens via seed_default_commands()."
          )
      ```
- [ ] **Verify:** test passes after Task 1.2 and BEFORE Task 1.3 lands (the decorator alone, with no per-module `register()` yet, must not register).

**Notes:**

---

### Task 1.3: Decorate handler classes in `engine/handlers/` (5 modules) [Medium]

**Files:**
- `game/strategy/engine/handlers/build.py`
- `game/strategy/engine/handlers/construction_queue.py`
- `game/strategy/engine/handlers/movement.py`
- `game/strategy/engine/handlers/order_queue.py`
- `game/strategy/engine/handlers/transfer.py`

**Tests:** `pytest tests/unit/strategy/engine/test_command_registry_seeding.py -v`

- [ ] In each module, `from game.strategy.engine.commands.registry import command_spec, CommandSpec, CommandRegistry`. Add the import deferred-import-style if needed to avoid cycles (deferred should NOT be needed because `registry.py` does not import these modules eagerly — only `seed_default_commands()` does, and it runs lazily).
- [ ] Add `@command_spec(...)` above each handler class with the EXACT field
      values from the corresponding `CommandSpec` row in `specs.py`. Source of
      truth: `specs.py:219-537`. **Field-for-field copy. No interpretation.** The decorator stays for human readability but is *not* the wiring path — the wiring path is the per-module `register()` function (next bullet).
- [ ] **Add `def register(registry: CommandRegistry) -> None:` to each module** that calls `registry.register(CommandSpec(handler_class=HandlerClass, **HandlerClass.__command_spec_kwargs__))` for each handler the module owns. This is the wiring path called by `seed_default_commands(registry)`.
- [ ] `engine/handlers/build.py` — decorate `BuildOrderCommandHandler` (`specs.py:427-434`), `RemoveBuildOrderCommandHandler` (`specs.py:435-442`); `register()` registers both.
- [ ] `engine/handlers/construction_queue.py` — decorate 4 handlers (`specs.py:444-477`); `register()` registers all 4.
- [ ] `engine/handlers/movement.py` — decorate 5 handlers (`specs.py:220-266`). NB: `ColonizeCommandHandler` is `category='action'`, not `'movement'` — copy from `specs.py:257-266`. `register()` registers all 5.
- [ ] `engine/handlers/order_queue.py` — decorate 5 handlers (`specs.py:281-322`). NB: includes `ColonizeMissionCommandHandler` (`specs.py:281-288`, `category='action'`, `execution_model='mission'`). `register()` registers all 5.
- [ ] `engine/handlers/transfer.py` — decorate `TransferCommandHandler` (`specs.py:269-277`); `register()` registers it.
- [ ] **Verify each module loads cleanly:** `python -c "from game.strategy.engine.handlers import build, construction_queue, movement, order_queue, transfer"`.
- [ ] **Verify Task 1.2.5 still passes:** importing any of these modules must NOT mutate the registry. Mutation only happens via `seed_default_commands(registry)` calling each module's `register()`.

**Notes:** Run through the spec rows in order; check each off as decorated.
Total: 5 + 4 + 5 + 5 + 1 = 20 handlers across 5 modules.

---

### Task 1.4: Decorate handler classes in `engine/planet_command_handlers.py` + add `register()` [Simple]

**File:** `game/strategy/engine/planet_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_command_registry_seeding.py -v`

- [ ] Add `from game.strategy.engine.commands.registry import command_spec, CommandSpec, CommandRegistry` import.
- [ ] Add `@command_spec(...)` above each of 7 handlers (`specs.py:481-536`):
      `IssuePlanetOrderCommandHandler`, `ClearPlanetOrdersCommandHandler`,
      `DeletePlanetOrderCommandHandler`, `SetAtmosphereTargetCommandHandler`,
      `SetGravityTargetCommandHandler`, `SetWaterTargetCommandHandler`,
      `SetRadiationShieldTargetCommandHandler`.
- [ ] Add `def register(registry: CommandRegistry) -> None:` that calls `registry.register(CommandSpec(handler_class=H, **H.__command_spec_kwargs__))` for each of the 7 handlers.
- [ ] **Verify:** module loads cleanly; spec field values match `specs.py:481-536` exactly; importing the module does NOT mutate the registry (Task 1.2.5 invariant holds).

**Notes:**

---

### Task 1.5: Decorate handler classes in `engine/superweapon_command_handlers.py` + add `register()` [Medium]

**File:** `game/strategy/engine/superweapon_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_command_registry_seeding.py -v`

- [ ] Add `from game.strategy.engine.commands.registry import command_spec, CommandSpec, CommandRegistry` import.
- [ ] Add `@command_spec(...)` above each of 11 handlers (`specs.py:325-424`):
      6 immediate (`IssueImplodePlanet/StellerateStar/Open/Close/CreateDyson/SelfDestruct`) + 5 mission variants (`Queue*Mission`).
- [ ] Add `def register(registry: CommandRegistry) -> None:` that calls `registry.register(CommandSpec(handler_class=H, **H.__command_spec_kwargs__))` for each of the 11 handlers.
- [ ] **Verify:** module loads cleanly; spec field values match `specs.py:325-424` exactly; importing the module does NOT mutate the registry (Task 1.2.5 invariant holds).

**Notes:**

---

### Task 1.6: Wire `seed_default_commands()` into the strategy-engine boot path [Medium]

**File:** `game/strategy/engine/handlers/registry_factory.py`
**Tests:** `pytest tests/unit/strategy/engine/test_command_registry_seeding.py -v` AND `pytest tests/unit/strategy/engine/test_command_specs_contract.py -v`

- [ ] In `create_default_registry()`, ensure `seed_default_commands(command_registry)` is
      called BEFORE the existing `for spec in COMMAND_SPECS: ...` loop. Since
      `COMMAND_SPECS` and the registry are bit-identical at this phase, the
      seed call's only side effect is populating the registry. **Important:**
      this is a no-op for the runtime dispatch path (we still iterate
      `COMMAND_SPECS` — that's Phase 2's migration target), but it ensures the
      registry IS populated when consumers query it during the same import
      cycle.
- [ ] Verify `python -c "from game.strategy.engine.commands.registry import command_registry; print(len(command_registry))"` prints `0` (no auto-seed at module import — only when `create_default_registry()` is called or a test explicitly calls `seed_default_commands(command_registry)`). The metadata-only decorator (Task 1.2.5 invariant) means importing handler modules also does not seed.
- [ ] Update `tests/unit/strategy/engine/test_command_registry_seeding.py` to
      explicitly call `seed_default_commands(command_registry)` in a module-scoped fixture
      before the bit-identity assertions run. Do NOT seed at module import in
      `registry.py` itself — that creates an import-order trap.
- [ ] **Verify:** the bit-identity tests now pass.

**Notes:**

---

### Task 1.7: Conftest test-isolation hook [Simple]

**File:** `tests/unit/strategy/conftest.py` (verify; modify if needed)
**Tests:** `pytest tests/unit/strategy/engine/ -v`

- [ ] Read the current `tests/unit/strategy/conftest.py`. Identify whether any
      registry-state-clearing fixtures already exist.
- [ ] Add (or extend) a `_command_registry_clean` autouse fixture for tests
      that import `command_registry`. The fixture should:
      ```python
      @pytest.fixture(autouse=True)
      def _command_registry_clean():
          from game.strategy.engine.commands.registry import (
              command_registry, reset_command_registry,
          )
          snapshot = dict(command_registry._specs)
          yield
          command_registry._specs.clear()
          command_registry._specs.update(snapshot)
      ```
- [ ] Run `pytest tests/unit/strategy/engine/test_command_registry_seeding.py tests/unit/strategy/engine/test_command_specs_contract.py -v` — both files green.
- [ ] **Verify:** running the bit-identity test in isolation AND in suite both pass (no test pollution).

**Notes:** This is the PROJ-367 / PROJ-360 lesson — registry-state fixtures
matter. Keep the snapshot-restore pattern symmetric.

---

### Task 1.8: Run the full PROJ-371 unit test scope [Simple]

**Tests:**
```
pytest tests/unit/strategy/engine/test_command_registry_seeding.py \
       tests/unit/strategy/engine/test_command_specs_contract.py \
       tests/unit/strategy/engine/test_command_registry_contract.py \
       tests/unit/strategy/facade/test_command_dispatch_slice_getattr.py \
       tests/unit/strategy/services/test_superweapon_registry_contract.py \
       -v
```

- [ ] Every existing PROJ-363 / PROJ-364 contract test continues to pass.
- [ ] The new bit-identity test passes.
- [ ] **Verify:** the test file count grew by exactly 1 (the new seeding test).

**Notes:**

---

### Task 1.9: Full sharded suite green [Medium]

**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run sharded suite; pass count = baseline + new tests added; zero regressions.
- [ ] **Acceptance:** pass count ≥ baseline + 5 (Tasks 1.1's new tests).
- [ ] If anything fails, do NOT proceed to Task 1.10 — diagnose and fix root cause.

**Notes:**

---

### Task 1.10: Commit Phase 1 [Simple]

- [ ] `git status --short` — verify only in-scope files are dirty (manifest entries from Tasks 1.2–1.7).
- [ ] `git add` only the listed files.
- [ ] Commit message:
      ```
      feat(PROJ-371): Phase 1 — CommandRegistry + @command_spec decorator (alongside existing tuple)

      Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
      ```
- [ ] Do NOT push.
- [ ] **Verify:** `git show --stat HEAD` shows only in-scope files.

**Notes:**

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All task checkboxes above are checked
- [ ] `command_registry` populates 35 entries when `seed_default_commands()` is called
- [ ] `COMMAND_SPECS` tuple is **unchanged** (still 35 entries; the literal at `specs.py:219-537` is intact)
- [ ] Bit-identity contract test passes: `set(s.command_class.__name__ for s in COMMAND_SPECS) == set(s.command_class.__name__ for s in command_registry.all())`
- [ ] All field values match field-for-field
- [ ] All 35 handler classes carry an `@command_spec(...)` decorator
- [ ] `CommandSpec` dataclass + `ALLOWED_CATEGORIES` + `ALLOWED_EXECUTION_MODELS` live in `registry.py`; `specs.py` re-exports them for back-compat
- [ ] Sharded suite green; pass count ≥ baseline + 5
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
