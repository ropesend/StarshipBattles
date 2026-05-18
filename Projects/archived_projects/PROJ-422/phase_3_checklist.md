# Phase 3: Validate consumers (regression sweep)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-422 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_2
**Review Mode:** standard
**Files (planned):** none (validation phase — no source edits expected)
**Objective:** Prove the split is symbol-preserving — every existing consumer (production engines, TurnEngine, tests, mocks) works without source-file edits.

---

## Tasks

### Task 3.1: Run focused strategy-engine test surface [Simple]
**Tests:**
```
pytest tests/unit/strategy/turn_engine tests/integration/strategy tests/unit/strategy/interfaces -q
```

- [x] Run the focused test surface. All tests pass.
- [x] If any test fails because of an import path mismatch, **stop** (N/A — none did).

**Notes:** 681 passed in 11.76s.

### Task 3.2: Run the TurnEngine AST guard [Simple]
**Tests:**
```
pytest tests/ -k test_no_function_local_engine_imports_in_TurnEngine_methods -q
```

- [x] AST guard passes — confirms the split did not introduce new function-local imports in TurnEngine methods.

**Notes:** 1 passed in 11.22s.

### Task 3.3: Run the full sharded baseline [Medium — wall-clock dominated by test runtime]
**Tests:**
```
python Tools/test_sharded/test_sharded.py
```

- [x] Full sharded baseline is green. **20857/20857 passed**, wall 142.2s.
- [x] No flakes observed.

**Notes:** Test baseline updated at `AgentCoordination/generated/test_baseline.json`.

### Task 3.4: Confirm zero consumer source edits [Simple]
**Tests:** `git diff --stat main -- game/strategy/engine/ tests/`

- [x] Diff shows zero modifications under `game/strategy/engine/`. The 14 concrete engine files are untouched.
- [x] Diff shows zero modifications to any pre-existing test file under `tests/` (the only test-tree change is the new `test_engines_package_layout.py`).
- [x] If either condition is violated, document why. (N/A — both conditions satisfied.)

**Notes:** `git diff --stat main..HEAD -- game/strategy/engine/ tests/` shows only `test_engines_package_layout.py | 131 +++`.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Focused strategy-engine tests pass
- [x] TurnEngine AST guard passes
- [x] Full sharded baseline passes
- [x] Zero consumer source files modified
- [x] `python Projects/scripts/validate_phase.py PROJ-422 3` passes
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
