# Phase 3: Authoring rule + AST regression + third-party command smoke

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-371 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_2
**Review Mode:** standard
**Files (planned):** `tests/unit/strategy/engine/test_no_specs_tuple_literal.py` (new), `tests/unit/strategy/engine/test_command_registry_thirdparty.py` (new), `tests/fixtures/command_registry.py` (new), `docs/systems/strategy_layer.md`, `docs/02_PATTERNS.md`

**Objective:** Lock in the registry pattern via an AST regression that
prevents anyone from re-introducing a `COMMAND_SPECS = (...)` tuple literal.
Ship a third-party-command smoke test demonstrating that mods can register
new commands cleanly. Document the authoring pattern.

---

## Pre-flight

- [ ] Phase 2 is **verified** (parent gate; specs.py is deleted; consumers migrated; sharded suite green)
- [ ] `git status --short` — clean
- [ ] `find game/strategy/engine/commands -type f` — confirm `specs.py` is gone

---

## Tasks

### Task 3.1: AST regression test (TDD-first) [Medium]

**File:** `tests/unit/strategy/engine/test_no_specs_tuple_literal.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/test_no_specs_tuple_literal.py -v`

- [ ] Create the file with this skeleton:
      ```python
      """AST regression: no COMMAND_SPECS tuple literal in game/.

      PROJ-371: Phase 2 deleted game/strategy/engine/commands/specs.py.
      The CommandRegistry is the single source of truth. Reintroducing a
      module-level tuple of CommandSpec rows would silently bring back the
      pre-PROJ-371 architecture.
      """
      from __future__ import annotations
      import ast
      from pathlib import Path

      GAME_ROOT = Path(__file__).resolve().parents[4] / "game"
      ALLOWED_RELATIVE_PATHS: frozenset[str] = frozenset()  # currently none
      ```
- [ ] Implement a walker that:
      1. Iterates all `*.py` files under `game/` (exclude `__pycache__`).
      2. For each file, parses with `ast.parse`.
      3. Walks the top-level `ast.Module.body` for `ast.Assign` nodes.
      4. Flags any `Assign` whose RHS is `ast.Tuple` with at least one element of shape `ast.Call(func=ast.Name(id='CommandSpec'))`.
      5. Asserts the flagged-list is empty (or matches `ALLOWED_RELATIVE_PATHS` if a future exception is needed).
- [ ] Add a unit test for the walker itself: feed it a synthetic `Assign(value=Tuple(elts=[Call(func=Name('CommandSpec'))]))` AST and assert it flags. Feed an `Assign(value=Tuple(elts=[Call(func=Name('Foo'))]))` and assert it does NOT flag.
- [ ] Run the test; **must pass** (no offending tuple literals exist post-Phase 2).
- [ ] Add a second test that *should fail* if the regression is broken:
      ```python
      def test_walker_would_catch_reintroduction(tmp_path):
          """Synthetic test: write a file with a forbidden tuple literal,
          assert the walker flags it. Proves the test isn't vacuous."""
          ...
      ```
- [ ] **Verify:** the walker correctly flags the synthetic violation.

**Notes:** Keep the walker generic — same idiom as PROJ-273's
`tests/unit/simulation/combat/test_ability_stat_registry.py` glob-driven
coverage check, adapted to AST patterns.

---

### Task 3.2: Test fixture for clean third-party-command registration [Medium]

**File:** `tests/fixtures/command_registry.py` (new)
**Tests:** Indirect (used by Task 3.3)

- [ ] Create the file with a context manager:
      ```python
      """Test helpers for registering commands at test time.

      PROJ-371 Phase 3: third-party-command smoke test machinery.
      """
      from __future__ import annotations
      from contextlib import contextmanager
      from typing import Iterator

      from game.strategy.engine.commands.registry import (
          CommandSpec, command_registry,
      )


      @contextmanager
      def temporary_command(spec: CommandSpec) -> Iterator[None]:
          """Snapshot the registry, register `spec`, restore on exit.

          Use only in tests. Production code never unregisters.
          """
          original = dict(command_registry._specs)
          command_registry.register(spec)
          try:
              yield
          finally:
              command_registry._specs.clear()
              command_registry._specs.update(original)
      ```
- [ ] Add an `__init__.py` next to it if the package doesn't exist yet.
- [ ] **Verify:** `from tests.fixtures.command_registry import temporary_command` works.

**Notes:**

---

### Task 3.3: Third-party command smoke test [Medium]

**File:** `tests/unit/strategy/engine/test_command_registry_thirdparty.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/test_command_registry_thirdparty.py -v`

- [ ] Create the file with a fake mod command + handler defined inside the test module:
      ```python
      """End-to-end smoke: a third-party command registers, dispatches, unregisters cleanly.

      PROJ-371 Phase 3: proves that adding a new command requires only
      one new file (handler module + decorator). This test acts as the
      worked example for mod authors.
      """
      from dataclasses import dataclass

      import pytest

      from game.core.validation import ValidationResult
      from game.strategy.engine.commands import Command
      from game.strategy.engine.commands.registry import CommandSpec, command_registry
      from game.strategy.engine.handlers.base import (
          BaseCommandHandler, ICommandHandler,
      )
      from tests.fixtures.command_registry import temporary_command


      @dataclass
      class FakeModCommand(Command):
          """Synthetic Command DTO for the smoke test."""
          fleet_id: int = 0
          payload: str = ""


      class FakeModCommandHandler(BaseCommandHandler):
          executions = []  # class-level capture for assertions

          def execute(self, session, command):
              type(self).executions.append((session, command))
              return ValidationResult.success()
      ```
- [ ] Add `test_third_party_command_registers_and_dispatches`:
      - Build a `CommandSpec(command_class=FakeModCommand, handler_class=FakeModCommandHandler, order_type=None, category='action', execution_model='instant', facade_helper_name=None)`.
      - Wrap in `with temporary_command(spec):` block.
      - Assert `command_registry.get('FakeModCommand') is spec`.
      - Build `create_default_registry()` (which now reads from the registry); assert `'FakeModCommand'` is registered.
      - Dispatch via `registry.dispatch('FakeModCommand', mock_session, FakeModCommand(fleet_id=1, payload='x'))`. Assert it returns `is_valid=True`. Assert `FakeModCommandHandler.executions` captured the call.
      - On exit from the context manager, assert `command_registry.get('FakeModCommand') is None`.
- [ ] Add `test_third_party_command_does_not_pollute_other_tests`:
      - Run the registration block once; on exit assert `len(command_registry) == 35` (the default count from Phase 1+2). Verifies clean restore.
- [ ] Add `test_replace_flag_is_required_for_replacing_a_default`:
      - Try `command_registry.register(default_spec_for_IssueMoveCommand_clone)` without `replace=True`; assert `ValueError`.
      - Try with `replace=True`; assert it succeeds and emits a `WARNING` log (use `caplog`).
      - Restore via the temporary-command context manager.
- [ ] Run the test file; **all green**.

**Notes:** This is the worked example for the docs in Task 3.4.

---

### Task 3.4: Documentation — `docs/systems/strategy_layer.md` [Medium]

**File:** `docs/systems/strategy_layer.md`
**Tests:** None (documentation)

- [ ] Read the current file to find the right section. Likely a "Commands and Handlers" or "Strategy Engine" section.
- [ ] Add a new subsection "Adding a new command (PROJ-371 authoring rule)":
      - Step 1: Define the Command DTO in `game/strategy/engine/commands/__init__.py`.
      - Step 2: Define the handler class in `game/strategy/engine/handlers/<domain>.py` (or a new domain module). Decorate with `@command_spec(...)`.
      - Step 3: If a NEW `OrderType` is required, add it to `game/strategy/data/order_types.py` and the relevant frozenset (`MOVEMENT_/ACTION_/PLANET_ACTION_ORDER_TYPES`). Pinned by contract test — drift fails the build.
      - Step 4: Add tests at `tests/unit/strategy/engine/...`.
- [ ] Include a worked-example code block lifted from the smoke test in
      Task 3.3, with the `FakeModCommand` example.
- [ ] Note explicitly: "No need to edit `specs.py` (deleted), `registry_factory.py`, `action_time_resolver.py`, `command_dispatch_slice.py`, or `strategy_session_facade.py`."
- [ ] Update the `> **Last verified:** YYYY-MM-DD` blockquote to today's date.

**Notes:**

---

### Task 3.5: Documentation — `docs/02_PATTERNS.md` [Simple]

**File:** `docs/02_PATTERNS.md`
**Tests:** None (documentation)

- [ ] Read the current file. Find the existing spec-driven registry pattern (PROJ-273 added "Pattern 26: Ability-Stat Registry" per memory).
- [ ] Either extend that pattern with a "Self-Registering Command Registry" cross-reference, OR add a new pattern (e.g. "Pattern N: Self-Registering Command Registry") that:
      - Cross-references PROJ-273 (the `dict[str, AbilityStatMapping]` shape) and PROJ-278 (the `RoleRegistry` shape).
      - Documents the PROJ-371 variant: class with `__slots__`, `@command_spec(...)` decorator, idempotent `seed_default_commands()`, `reset_*_registry()` test helper.
      - Documents the trade-off: decorator-based registration is ergonomic but requires module imports; module-level dict literal is simpler but less extensible.
- [ ] Update the `> **Last verified:** YYYY-MM-DD` blockquote.

**Notes:**

---

### Task 3.6: Full sharded suite green [Medium]

**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run sharded suite. Pass count grows by:
      - Task 3.1: 2 tests (the AST walker test + the synthetic-violation test)
      - Task 3.3: 3 tests (registers/dispatches/clean-restore + replace-flag)
- [ ] Zero regressions.

**Notes:**

---

### Task 3.7: Commit Phase 3 [Simple]

- [ ] `git status --short` — verify only in-scope files.
- [ ] `git add` only listed files.
- [ ] Commit message:
      ```
      docs(PROJ-371): Phase 3 — authoring rule + AST regression + third-party-command smoke test

      - tests/unit/strategy/engine/test_no_specs_tuple_literal.py — AST regression forbidding COMMAND_SPECS tuple literal in game/
      - tests/unit/strategy/engine/test_command_registry_thirdparty.py — end-to-end smoke (FakeModCommand)
      - tests/fixtures/command_registry.py — temporary_command context manager
      - docs/systems/strategy_layer.md — "Adding a new command" authoring section
      - docs/02_PATTERNS.md — self-registering command registry pattern (cross-refs PROJ-273, PROJ-278)

      Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
      ```
- [ ] Do NOT push.

**Notes:**

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All task checkboxes above are checked
- [ ] AST regression test passes — `COMMAND_SPECS = (CommandSpec(...), ...)` cannot be reintroduced to `game/`
- [ ] Third-party-command smoke test passes — registers, dispatches, restores cleanly
- [ ] `docs/systems/strategy_layer.md` has the authoring rule
- [ ] `docs/02_PATTERNS.md` cross-references PROJ-273, PROJ-278, PROJ-371
- [ ] Sharded suite green; pass count ≥ baseline + 5
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to "Project verified" / audit gate
