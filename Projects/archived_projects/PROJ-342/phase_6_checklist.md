# Phase 6: Documentation Cleanup [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-342 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update Combat Lab documentation and stale docstrings to reflect the post-Phase-4 architecture (`TestLabExecutor` is the in-game caller, not `TestExecutionService`). Per CLAUDE.md rule 2, code and docs must stay in sync.

---

## Tasks

### Task 6.1: Update `combat_lab/COMBAT_LAB_DOCUMENTATION.md` [Simple]
**File:** `combat_lab/COMBAT_LAB_DOCUMENTATION.md`
**Tests:** Manual review

Four sections describe the deleted service architecture. Update each:

- [ ] [Lines 73-74](../../../combat_lab/COMBAT_LAB_DOCUMENTATION.md#L73-L74) (file-list comments): remove `test_execution_service.py` and `test_results_service.py` entries
- [ ] [Lines 161-162](../../../combat_lab/COMBAT_LAB_DOCUMENTATION.md#L161-L162) (architecture diagram boxes): remove `TestExecutionService` and `TestResultsService` boxes; replace with `TestLabExecutor` if appropriate to the diagram
- [ ] [Lines 222-226](../../../combat_lab/COMBAT_LAB_DOCUMENTATION.md#L222-L226) (run-flow diagram step 4): replace `TestLabUIController.handle_run_headless() / handle_run_visual()` and `TestExecutionService.run_headless(...)` with the actual production path: click → `TestLabInputHandler` → `TestLabExecutor.run_headless / run_visual / run_all`
- [ ] [Line 259](../../../combat_lab/COMBAT_LAB_DOCUMENTATION.md#L259) (results-storage step): replace `TestResultsService.add_run(...)` with `TestHistory.add_run(...)` (the actual surviving caller — `TestExecutor` writes directly through `test_history`)
- [ ] Read the full document and search for any remaining references to the deleted symbols: `grep -nE "TestExecutionService|TestResultsService|handle_run_(visual|headless)"` — must return zero hits in this file after edits

**Notes:** [Filled during implementation. Diagram updates may need ASCII-art adjustment beyond simple text replacement.]

### Task 6.2: Update `combat_lab/runner.py` docstrings [Simple]
**File:** `combat_lab/runner.py`
**Tests:** `pytest tests/unit/combat_lab -x`

- [ ] [Lines 62-64](../../../combat_lab/runner.py#L62-L64): replace docstring reference to `TestExecutionService` with `TestLabExecutor`
- [ ] [Lines 88-90](../../../combat_lab/runner.py#L88-L90): same — `TestExecutionService` → `TestLabExecutor` in docstring
- [ ] Verify with `git grep -n "TestExecutionService" combat_lab/runner.py` — zero hits after edit

**Notes:** [Filled during implementation. Docstring-only changes; no behavioral impact.]

### Task 6.3: Update `game/simulation/battle_controller.py` docstrings [Simple]
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation -x`

- [ ] [Lines 113-116](../../../game/simulation/battle_controller.py#L113-L116): docstring comment lists `test_execution_service.py` as a caller. Update to remove the deleted service.
- [ ] [Lines 254-260](../../../game/simulation/battle_controller.py#L254-L260): same — duplicated-block history references `test_execution_service.py`. Update accordingly.
- [ ] Verify with `git grep -n "test_execution_service" game/simulation/battle_controller.py` — zero hits after edit

**Notes:** [Filled during implementation]

### Task 6.4: Verify no other stale references [Simple]
**Tests:** Manual grep

Final sweep for stragglers:

- [ ] `git grep -nE "TestExecutionService|test_execution_service" -- combat_lab game docs` — must return zero hits in production code or docs (acceptable: matches in `Projects/deep_archive/` or `_marked_for_deletion_*`)
- [ ] `git grep -nE "TestResultsService|test_results_service" -- combat_lab game docs` — same standard
- [ ] `git grep -nE "handle_run_visual|handle_run_headless" -- combat_lab game docs` — same standard
- [ ] If anything turns up, fix it or document in `decisions.md` why it's acceptable to leave

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist

- [ ] `combat_lab/COMBAT_LAB_DOCUMENTATION.md` describes the current architecture (no references to deleted services)
- [ ] `combat_lab/runner.py` and `game/simulation/battle_controller.py` docstrings updated
- [ ] No stale references to deleted symbols in `combat_lab/`, `game/`, or `docs/`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 7
