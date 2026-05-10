# Phase 2: Migrate consumers; delete tuple; collapse facade forwarders

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-371 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_1
**Review Mode:** standard
**Files (planned):** `game/strategy/engine/handlers/registry_factory.py`, `game/strategy/services/action_time_resolver.py`, `game/strategy/facade/slices/command_dispatch_slice.py`, `game/strategy/facade/strategy_session_facade.py`, `game/strategy/engine/commands/specs.py` (DELETE), `tests/unit/strategy/engine/test_command_specs_contract.py`, `tests/unit/strategy/facade/test_command_dispatch_slice_getattr.py`, `tests/unit/strategy/services/test_superweapon_registry_contract.py`, `tests/unit/strategy/engine/test_command_registry_seeding.py` (DELETE or migrate)

**Objective:** Three production consumers migrate from `COMMAND_SPECS` to
`command_registry`. The 31 hand-written `dispatch_*` forwarders in
`strategy_session_facade.py` collapse into `__getattr__`. `specs.py` is
**deleted**. Three contract tests update imports. Sharded suite green.

---

## Pre-flight

- [ ] Phase 1 is **verified** (parent gate; the bit-identity contract test passed)
- [ ] `git status --short` — clean
- [ ] Re-read `findings/initial_review.md` § "Consumer surfaces of `COMMAND_SPECS`"
- [ ] Verify the bit-identity contract from Phase 1 still holds: `pytest tests/unit/strategy/engine/test_command_registry_seeding.py -v`

---

## Tasks

### Task 2.1: Migrate `registry_factory.py` to read from `command_registry` [Simple]

**File:** `game/strategy/engine/handlers/registry_factory.py`
**Tests:** `pytest tests/unit/strategy/engine/test_command_registry_contract.py tests/unit/strategy/engine/test_command_specs_contract.py -v`

- [ ] Replace the deferred `from game.strategy.engine.commands.specs import COMMAND_SPECS` (line 32) with `from game.strategy.engine.commands.registry import command_registry, seed_default_commands`.
- [ ] Replace the loop body (line 35-36):
      ```python
      seed_default_commands()  # idempotent
      for spec in command_registry.all():
          registry.register(spec.command_class.__name__, spec.handler_class())
      ```
- [ ] Update the docstring (lines 1-13) to reference the registry instead of `COMMAND_SPECS`.
- [ ] Run the test command above; **all green**.
- [ ] **Verify:** zero behaviour change — registry contents are identical.

**Notes:**

---

### Task 2.2: Migrate `action_time_resolver.py` to read from `command_registry` [Simple]

**File:** `game/strategy/services/action_time_resolver.py`
**Tests:** `pytest tests/unit/strategy/engine/test_command_registry_contract.py tests/unit/strategy/services/ -v`

- [ ] Replace `_build_order_to_ability_map()` (lines 35-37):
      ```python
      def _build_order_to_ability_map() -> Dict[OrderType, str]:
          from game.strategy.engine.commands.registry import (
              command_registry, seed_default_commands,
          )
          seed_default_commands()
          return command_registry.order_to_ability_map()
      ```
- [ ] **Delete** the redundant local `MOVEMENT_ORDER_TYPES` frozenset (line 48):
      `MOVEMENT_ORDER_TYPES: frozenset = frozenset({OrderType.MOVE, OrderType.MOVE_TO_FLEET})` — this lacks `WARP` and is superseded by the canonical set in `data/order_types.py`.
- [ ] Replace the use site at line 79: `from game.strategy.data.order_types import MOVEMENT_ORDER_TYPES`. The canonical set IS imported at top of file via `from game.strategy.data.order_types import OrderType, PLANET_ACTION_ORDER_TYPES` — extend the import to include `MOVEMENT_ORDER_TYPES`.
- [ ] Update docstring (lines 1-16) to reference the registry.
- [ ] Run the test commands above; **all green**.
- [ ] **Verify:** the contract test asserting `ORDER_TO_ABILITY_MAP` matches the existing static map (`test_command_specs_contract.py:150-152`) still passes.

**Notes:** The local `MOVEMENT_ORDER_TYPES` deletion is a one-line dead-code cleanup along the way.

---

### Task 2.3: Migrate `command_dispatch_slice.py` to read from `command_registry` [Simple]

**File:** `game/strategy/facade/slices/command_dispatch_slice.py`
**Tests:** `pytest tests/unit/strategy/facade/test_command_dispatch_slice_getattr.py -v`

- [ ] Replace the deferred `from game.strategy.engine.commands.specs import specs_by_facade_helper` at line 80 with `from game.strategy.engine.commands.registry import command_registry, seed_default_commands; seed_default_commands()`.
- [ ] Replace `spec = specs_by_facade_helper().get(name)` (line 82) with `spec = command_registry.specs_by_facade_helper().get(name)`.
- [ ] Update the module docstring (lines 1-12) — replace `COMMAND_SPECS` references with `command_registry`.
- [ ] Run the test command; **all green**.
- [ ] **Verify:** `dispatch_issue_move(...)` still resolves to `IssueMoveCommand` via the new path.

**Notes:**

---

### Task 2.4: Collapse `strategy_session_facade.py` `dispatch_*` forwarders to `__getattr__` [Medium]

**File:** `game/strategy/facade/strategy_session_facade.py`
**Tests:** `pytest tests/unit/strategy/facade/ -v`

- [ ] Locate the 31 hand-written `dispatch_*` forwarders (lines 186-end). Confirm with `grep -c "def dispatch_" game/strategy/facade/strategy_session_facade.py` — should be 31 (memory says ~31 today).
- [ ] **Delete** the 31 method definitions in one block.
- [ ] Add at the same location:
      ```python
      def __getattr__(self, name: str):
          if not name.startswith("dispatch_"):
              raise AttributeError(
                  f"{type(self).__name__!r} object has no attribute {name!r}"
              )
          # Proxy to the slice; the slice's __getattr__ resolves against
          # command_registry.specs_by_facade_helper().
          return getattr(self._command_slice, name)
      ```
- [ ] Run the test command; **all green** — the slice-level `__getattr__` and bound-method semantics handle the proxy. Verify with a smoke call.
- [ ] Add new test `test_facade_dispatch_proxies_to_slice` to `tests/unit/strategy/facade/test_command_dispatch_slice_getattr.py`:
      ```python
      def test_facade_dispatch_helper_proxies_to_slice():
          # Build a facade with a stubbed session; assert facade.dispatch_issue_move
          # is callable, and a call routes through to slice's __getattr__ which
          # routes to command_registry.specs_by_facade_helper.
          ...
      ```
- [ ] **Verify:** every existing test that calls `facade.dispatch_<name>(...)` still works. There are likely many across the test suite — sharded suite is the safety net.

**Notes:** Save the deleted line count (~150 LOC) for the final commit message.

---

### Task 2.5: Update PROJ-364 cross-link test [Simple]

**File:** `tests/unit/strategy/services/test_superweapon_registry_contract.py`
**Tests:** `pytest tests/unit/strategy/services/test_superweapon_registry_contract.py -v`

- [ ] Find the 2 occurrences of `from game.strategy.engine.commands.specs import COMMAND_SPECS` (lines 149, 167 per the grep).
- [ ] Replace with `from game.strategy.engine.commands.registry import command_registry, seed_default_commands` and call `seed_default_commands()` once in the relevant test setup.
- [ ] Replace `COMMAND_SPECS` use sites with `list(command_registry.all())` (or `tuple(command_registry.all())` if positional indexing is needed).
- [ ] Run the test command; **all green**.

**Notes:**

---

### Task 2.6: Update `test_command_specs_contract.py` imports [Simple]

**File:** `tests/unit/strategy/engine/test_command_specs_contract.py`
**Tests:** `pytest tests/unit/strategy/engine/test_command_specs_contract.py -v`

- [ ] Replace the import block (lines 20-32):
      ```python
      from game.strategy.engine.commands.registry import (
          ALLOWED_CATEGORIES, ALLOWED_EXECUTION_MODELS,
          CommandSpec, command_registry, seed_default_commands,
      )
      ```
- [ ] Add `seed_default_commands()` at module scope (or in a session-scoped fixture).
- [ ] Replace every `COMMAND_SPECS` reference with `tuple(command_registry.all())` (or save it once: `COMMAND_SPECS = tuple(command_registry.all())` after `seed_default_commands()`).
- [ ] Replace function-call references (`movement_order_types()` → `command_registry.movement_order_types()`, etc.).
- [ ] Run the test command; **all green**.
- [ ] **Verify:** the test names did not change. Test count is preserved.

**Notes:**

---

### Task 2.7: Update `test_command_dispatch_slice_getattr.py` imports [Simple]

**File:** `tests/unit/strategy/facade/test_command_dispatch_slice_getattr.py`
**Tests:** `pytest tests/unit/strategy/facade/test_command_dispatch_slice_getattr.py -v`

- [ ] Replace `from game.strategy.engine.commands.specs import COMMAND_SPECS` (line 19) with `from game.strategy.engine.commands.registry import command_registry, seed_default_commands; seed_default_commands(); COMMAND_SPECS = tuple(command_registry.all())`.
- [ ] Run the test command; **all green**.

**Notes:**

---

### Task 2.8: DELETE `game/strategy/engine/commands/specs.py` [Medium]

**File:** `game/strategy/engine/commands/specs.py` (DELETE)
**Tests:** Full sharded suite

- [ ] `grep -rn "from game.strategy.engine.commands.specs" game/ tests/` — every use site MUST already be migrated by Tasks 2.1–2.7. Print the grep result; the only remaining hits should be inside `tests/` files that already migrated. If anything in `game/` remains, fix it before deleting.
- [ ] `grep -rn "from game.strategy.engine.commands import specs" game/ tests/` — same check.
- [ ] **Delete** `game/strategy/engine/commands/specs.py`.
- [ ] Run sharded suite: `python Tools/test_sharded/test_sharded.py`.
- [ ] If anything fails, **do not restore the file**. Diagnose root cause; either the migration missed a consumer (fix) or a test had a stale import (fix). The root-cause-fixes-only rule applies.

**Notes:** This is the destructive step. Keep the deletion in its own task so the diff is bisectable.

---

### Task 2.9: DELETE bit-identity test (no longer meaningful) [Simple]

**File:** `tests/unit/strategy/engine/test_command_registry_seeding.py` (DELETE or migrate)
**Tests:** `pytest tests/unit/strategy/engine/ -v`

- [ ] Decision: with `specs.py` deleted, the bit-identity contract has nothing to assert against. Delete the file.
- [ ] If any of the tests inside it (e.g. `test_decorator_returns_handler_class_unchanged`, `test_registry_count_is_35`) still have value, migrate them to `test_command_specs_contract.py` first, then delete the seeding file.
- [ ] **Verify:** test file count is correct after the deletion.

**Notes:**

---

### Task 2.10: Verify `data/order_types.py` frozensets still match the registry [Simple]

**File:** (read-only) `game/strategy/data/order_types.py`
**Tests:** `pytest tests/unit/strategy/engine/test_command_specs_contract.py::test_movement_order_types_derivation_matches_constant -v`

- [ ] Confirm the contract tests at `test_command_specs_contract.py:135-152` (Task 2.6 migrated their imports) still pass against the registry. They pin the three frozensets to the registry's derived sets.
- [ ] **Verify:** `data/order_types.py:58-86` is **unchanged** by Phase 2 — it remains a leaf-layer constant set, pinned by the migrated test.

**Notes:** This is a read-only check; nothing to edit.

---

### Task 2.11: Full sharded suite green [Medium]

**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run sharded suite; pass count ≥ baseline + 1 (the Task 2.4 new test) − 5 (Task 2.9 deleted tests). Net change is small but positive.
- [ ] Zero regressions.
- [ ] **Acceptance:** every legacy `dispatch_*` callsite still works through the facade-level `__getattr__` proxy.

**Notes:**

---

### Task 2.12: Commit Phase 2 [Simple]

- [ ] `git status --short` — verify in-scope files only.
- [ ] `git add` only listed files. Note: `specs.py` is deleted (`git rm`).
- [ ] Commit message:
      ```
      refactor(PROJ-371): Phase 2 — migrate consumers to command_registry; delete specs.py; collapse facade forwarders

      - registry_factory, action_time_resolver, command_dispatch_slice now read command_registry
      - strategy_session_facade.py 31 dispatch_* forwarders collapsed into __getattr__ (~150 LOC removed)
      - game/strategy/engine/commands/specs.py deleted (logic moved to registry.py in Phase 1)
      - tests/unit/strategy/engine/test_command_registry_seeding.py deleted (bit-identity assertion no longer meaningful)
      - PROJ-364 superweapon-registry cross-link test reads command_registry.all()
      - Redundant local MOVEMENT_ORDER_TYPES frozenset at action_time_resolver.py:48 deleted

      Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
      ```
- [ ] Do NOT push.

**Notes:**

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All task checkboxes above are checked
- [ ] `game/strategy/engine/commands/specs.py` does not exist (`git ls-files game/strategy/engine/commands/specs.py` returns nothing)
- [ ] `command_registry` is the single source of truth
- [ ] All 4 production consumers read from `command_registry`
- [ ] `strategy_session_facade.py` has zero hand-written `dispatch_*` methods (only `__getattr__`)
- [ ] Local `MOVEMENT_ORDER_TYPES` at `action_time_resolver.py:48` is deleted
- [ ] PROJ-364 cross-link test reads `command_registry.all()`
- [ ] Sharded suite green
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
