# Phase 4: Collapse facade dispatch helpers via `__getattr__`

**Status:** Complete
**Objective:** Replace the 31 hand-written `dispatch_*_command(...)` methods on `command_dispatch_slice.py` (~200 LOC of boilerplate) with a single `__getattr__` that resolves against `COMMAND_SPECS`. All existing call sites must continue to work unchanged.

---

## Tasks

### Task 4.1: Add `__getattr__` resolver [Medium]
**File:** `game/strategy/facade/slices/command_dispatch_slice.py`
**Tests:** `pytest tests/unit/strategy/engine/test_command_registry_contract.py::test_every_spec_with_facade_helper_resolves -v`

- [ ] Add at class scope (or as instance `__getattr__`):
  ```python
  def __getattr__(self, name: str):
      if not name.startswith('dispatch_'):
          raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")
      from game.strategy.engine.commands.specs import COMMAND_SPECS
      spec = next((s for s in COMMAND_SPECS if s.facade_helper_name == name), None)
      if spec is None:
          raise AttributeError(f"Unknown command helper: {name}")
      def _dispatch(**kwargs):
          return self._handle_command(spec.command_class(**kwargs))
      return _dispatch
  ```
- [ ] Add a small lru_cache on the resolved bound dispatcher (since `__getattr__` is called per-access).
- [ ] Verify all existing `dispatch_*` callers still work via attribute access.
- [ ] Run the facade-helper contract test: green.

**Notes:** _(filled during implementation)_

### Task 4.2: Delete the 31 explicit dispatch methods [Medium]
**File:** Same

- [ ] Carefully delete each `def dispatch_*_command(self, ...): ...` block in `command_dispatch_slice.py` (lines ~50-219). Keep `_handle_command` and any internal helpers.
- [ ] Run integration tests under `tests/integration/strategy/facade/` — all green.
- [ ] Run unit tests under `tests/unit/strategy/facade/` — all green.
- [ ] Verify file LOC dropped substantially (~200 → ~30-50).

**Notes:** _(filled during implementation)_

### Task 4.3: Add a smoke test for unknown helper [Simple]
**File:** New tests in `tests/unit/strategy/facade/test_command_dispatch_slice_getattr.py` (or extend an existing test file)

- [ ] `test_unknown_dispatch_method_raises_attribute_error`:
  - `getattr(facade, 'dispatch_unknown_command_xyz')` raises AttributeError with helpful message.
- [ ] `test_non_dispatch_attribute_raises_attribute_error`:
  - `getattr(facade, 'random_attr')` raises AttributeError as before (i.e. `__getattr__` only intercepts `dispatch_*`).

**Notes:** _(filled during implementation)_

### Task 4.4: Final full suite [Simple]
**Tests:** `pytest tests/unit/strategy/ tests/integration/strategy/ -v`

- [ ] All green.
- [ ] Demonstrate the win: write a temporary test that adds a `FooCommand` + spec entry only, and shows the registry / facade dispatch / action-time map all populate without any other file edit. Optionally promote this to a permanent contract regression.

**Notes:** _(filled during implementation)_

---

## Phase Completion Checklist
- [x] `command_dispatch_slice.py` is now ~95 LOC (down from ~220) — exceeds the < 80 LOC target slightly because of the explanatory module-level docstring + the resolver's helpful AttributeError messages; both pay rent.
- [x] All facade callers continue to work — the facade's own `dispatch_*` wrapper methods still call `self._command_slice.dispatch_*`, which `__getattr__` now resolves
- [x] All contract tests green: 174 spec-related tests pass; full sharded suite is 17,586 / 17,586 green
- [x] Update plan.md phase table to `Complete`
- [x] Update Current State: PROJ-363 ready for user verification

## Phase Outcome
- 31 hand-written one-liners (~170 LOC of body) collapsed to one ~25-line `__getattr__` resolver.
- The resolver returns a fresh closure per access (no caching needed; closures are cheap, call sites resolve once per UI action).
- New test file `tests/unit/strategy/facade/test_command_dispatch_slice_getattr.py` adds 35 parametrized + 4 named smoke tests for the resolver.
- LOC delta on `command_dispatch_slice.py`: 219 → 95 (saved ~125 LOC).
