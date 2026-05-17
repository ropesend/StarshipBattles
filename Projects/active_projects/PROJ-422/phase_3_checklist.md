# Phase 3: Validate consumers (regression sweep)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-422 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
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

- [ ] Run the focused test surface. All tests pass.
- [ ] If any test fails because of an import path mismatch, **stop** — that is exactly the signal the TD plan calls out as "the split design is wrong; do not silently rewrite consumer imports."

**Notes:** [Filled during implementation]

### Task 3.2: Run the TurnEngine AST guard [Simple]
**Tests:**
```
pytest tests/ -k test_no_function_local_engine_imports_in_TurnEngine_methods -q
```

- [ ] AST guard passes — confirms the split did not introduce new function-local imports in TurnEngine methods.

**Notes:** [Filled during implementation]

### Task 3.3: Run the full sharded baseline [Medium — wall-clock dominated by test runtime]
**Tests:**
```
python Tools/test_sharded/test_sharded.py
```

- [ ] Full sharded baseline is green. Budget: ~several minutes (the dominant cost of this entire project per the TD plan's scope estimate).
- [ ] If the run is flaky, follow the standard flaky-test protocol; do **not** rerun in a tight loop.

**Notes:** [Filled during implementation. Per TD plan §"Per-Phase Success Criteria": Phase 3 is done only when the strategy turn-engine tests pass without any consumer import changes.]

### Task 3.4: Confirm zero consumer source edits [Simple]
**Tests:** `git diff --stat main -- game/strategy/engine/ tests/`

- [ ] Diff shows zero modifications under `game/strategy/engine/`. The 14 concrete engine files are untouched.
- [ ] Diff shows zero modifications to any pre-existing test file under `tests/` (the only test-tree change should be the new `test_engines_package_layout.py`).
- [ ] If either condition is violated, document why in the phase Notes and in `decisions.md`.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Focused strategy-engine tests pass
- [ ] TurnEngine AST guard passes
- [ ] Full sharded baseline passes
- [ ] Zero consumer source files modified
- [ ] `python Projects/scripts/validate_phase.py PROJ-422 3` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
