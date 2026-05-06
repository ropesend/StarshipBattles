# Phase 4: Refactor TestLabUIController + Delete Orphan Services [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-342 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Drop `game` parameter from `TestLabUIController`. Delete `handle_run_visual` / `handle_run_headless` along with the now-orphan `TestExecutionService` and `TestResultsService`. Stop and reconsider if implementation discovers a non-test caller missed by grep.

---

## Tasks

### Task 4.1: Pre-flight grep for missed callers [Simple]
**Tests:** Manual grep verification

Before any deletion, run a wider grep than the one in the design doc to catch anything dynamic-dispatch-based:

- [ ] `git grep -nE "handle_run_visual|handle_run_headless"` — production hits should be only in `combat_lab/services/test_lab_controller.py` (the methods themselves) and tests
- [ ] `git grep -nE "TestExecutionService|test_execution_service"` — production hits should be `__init__.py` exports + `test_lab_controller.py` imports/usage + the service file itself + docstring references in `combat_lab/runner.py` and `game/simulation/battle_controller.py`
- [ ] `git grep -nE "TestResultsService|test_results_service"` — production hits should be `__init__.py` exports + `test_lab_controller.py` imports/usage + the service file itself
- [ ] `git grep -nE "getattr.*handle_run|getattr.*test_execution|getattr.*test_results"` — must be empty
- [ ] If any unexpected production caller surfaces, **STOP**. Update `decisions.md` with the finding, narrow the scope to controller-method deletion only, and park service deletion as follow-up.

**Notes:** [Filled during implementation. This is the safety gate.]

### Task 4.2: Refactor `TestLabUIController.__init__` [Medium]
**File:** `combat_lab/services/test_lab_controller.py`
**Tests:** `pytest tests/unit/combat_lab/services -x` (will fail until Phase 5 updates the tests)

- [ ] Change [line 27](../../../combat_lab/services/test_lab_controller.py#L27) `def __init__(self, game, registry: TestRegistry, test_history: TestHistory):` to:
  ```python
  def __init__(self, registry: TestRegistry, test_history: TestHistory) -> None:
  ```
- [ ] Update docstring (lines 28-35) to drop the `game:` parameter description
- [ ] Delete [line 36](../../../combat_lab/services/test_lab_controller.py#L36) `self.game = game`
- [ ] Delete [lines 41-43](../../../combat_lab/services/test_lab_controller.py#L41-L43):
  ```python
  self.test_execution = TestExecutionService()
  self.ui_state = UIStateService()
  self.test_results = TestResultsService(test_history, registry)
  ```
  Replace with just `self.ui_state = UIStateService()` — the other two are removed when their services are deleted in Task 4.4.
- [ ] Delete imports of `TestExecutionService` and `TestResultsService` from [lines 9-14](../../../combat_lab/services/test_lab_controller.py#L9-L14)

**Notes:** [Filled during implementation]

### Task 4.3: Delete `handle_run_visual` and `handle_run_headless` [Simple]
**File:** `combat_lab/services/test_lab_controller.py`
**Tests:** `pytest tests/unit/combat_lab/services -x`

- [ ] Delete [`handle_run_visual` (lines ~87-111)](../../../combat_lab/services/test_lab_controller.py#L87-L111) entirely
- [ ] Delete [`handle_run_headless` (lines ~113-158)](../../../combat_lab/services/test_lab_controller.py#L113-L158) entirely
- [ ] Verify with `git grep -n "handle_run_visual\|handle_run_headless" combat_lab/` — must return zero hits in production code

**Notes:** [Filled during implementation]

### Task 4.4: Delete orphan services [Simple]
**Files:** `combat_lab/services/test_execution_service.py` (DELETE), `combat_lab/services/test_results_service.py` (DELETE), `combat_lab/services/__init__.py` (UPDATE)
**Tests:** `pytest tests/unit/combat_lab/services -x` (Phase 5 cleans up affected tests)

- [ ] `git rm combat_lab/services/test_execution_service.py`
- [ ] `git rm combat_lab/services/test_results_service.py`
- [ ] In [`combat_lab/services/__init__.py`](../../../combat_lab/services/__init__.py): remove the `from .test_execution_service import TestExecutionService` and `from .test_results_service import TestResultsService` imports (lines 10, 12); remove `'TestExecutionService'` and `'TestResultsService'` from the `__all__` list (lines 16, 18)
- [ ] Verify with `git grep -n "TestExecutionService\|TestResultsService" combat_lab/ game/` — only acceptable hits should be docstrings flagged for cleanup in Phase 6 (`combat_lab/runner.py:62-64, 88-90` and `game/simulation/battle_controller.py:113-116, 254-260`)

**Notes:** [Filled during implementation]

### Task 4.5: Check `combat_lab/services/scenario_run_helper.py` references [Simple]
**File:** `combat_lab/services/scenario_run_helper.py`
**Tests:** `pytest tests/unit/combat_lab/services -x`

This file references `test_execution_service.run_headless` and `TestExecutionService` in *comments/docstrings* (lines 4 and 68 per Codex's grep). Confirm and update:

- [ ] Read `combat_lab/services/scenario_run_helper.py:1-80` to confirm references are comments/docstrings only (no `import`, no live call)
- [ ] If they are live calls, **STOP** and re-evaluate: this would mean a hidden production caller was missed. Update decisions.md and narrow scope per Task 4.1's escape hatch.
- [ ] If they are comments/docstrings, update them to reference `TestLabExecutor` (the surviving in-game caller) instead of `TestExecutionService`

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist

- [ ] `TestLabUIController.__init__` no longer takes `game`
- [ ] `handle_run_visual` and `handle_run_headless` are gone
- [ ] `test_execution_service.py` and `test_results_service.py` are deleted
- [ ] `combat_lab/services/__init__.py` exports updated
- [ ] No production code (outside docstrings) references the deleted symbols
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
