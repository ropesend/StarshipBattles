# Phase 7: Harden lazy-import AST guard (Codex follow-up)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-424 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete

**Depends on:** phase_6
**Review Mode:** lightweight
**Files (planned):**
- `tests/unit/strategy/engine/commands/test_order_metadata_view.py`

**Objective:** harden the Phase 2 cycle-safety regression guard so that it cannot be bypassed by class-body imports or dynamic `importlib.import_module` / `__import__` calls at module scope.

**Codex consult finding:** the original `_module_level_imports()` helper inspected only `tree.body` and only `ast.Import` / `ast.ImportFrom` nodes. That left two classes of bypasses unguarded:

1. **Class-body imports** — a top-level `class _X:` whose body contains `from game.strategy.engine.commands.registry import command_registry`. Class bodies execute at module load, so this reintroduces the cycle while satisfying the old guard.
2. **Dynamic imports at module scope** — `importlib.import_module("game.strategy.engine.commands.registry")` and `__import__("game.strategy.engine.commands.registry")` evaluated at module top.

Function-body imports are NOT bypasses (they only execute when the function is called) and the hardened guard correctly leaves them alone.

---

## Tasks

### Task 7.1: Write the failing negative tests first [Simple]
**File:** `tests/unit/strategy/engine/commands/test_order_metadata_view.py`
**Tests:**
- `test_guard_detects_class_body_import_of_registry`
- `test_guard_detects_top_level_importlib_import_module_call`
- `test_guard_detects_top_level_dunder_import_call`
- `test_guard_ignores_function_body_import`

- [x] Add four synthetic-source-string tests covering each vector
- [x] Confirm they fail against the original weak `_module_level_imports`

**Notes:** Verified each of the three "must detect" cases returned False under the original implementation; the one "must ignore" case correctly returned False under both implementations.

### Task 7.2: Harden the helper [Simple]
**File:** `tests/unit/strategy/engine/commands/test_order_metadata_view.py`
**Tests:** all 12 tests in the file

- [x] Add `_module_load_evaluated_imports(source)` that walks module-top + top-level class bodies for static imports
- [x] Scan the same locations for `importlib.import_module(...)` / `__import__(...)` calls and collect string-literal arguments
- [x] Keep `_module_level_imports(path)` as a thin file wrapper delegating to the source-string helper
- [x] Update `test_view_is_lazy_at_import_time` failure message and docstring to reflect the wider guard

**Notes:** No production file changes — this phase only hardens the regression test.

### Task 7.3: Run focused tests [Simple]
**File:** n/a
**Tests:**
- `pytest tests/unit/strategy/engine/commands/test_order_metadata_view.py -v`

- [x] All 12 tests green (8 prior + 4 new)
- [x] `test_view_is_lazy_at_import_time` still green against the production `order_metadata_view.py`

**Notes:** Local run: `12 passed in 1.70s`.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Hardened helper handles class-body imports and dynamic imports
- [x] Function-body imports still correctly ignored
- [x] `test_view_is_lazy_at_import_time` green against the production view
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State
