# Phase 2: Local Migration & Full Regression

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-295 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate the local dev environment to the target Python version. Run the full test suite. Investigate and fix any regressions. Run a manual game smoke. Confirm Google FutureWarnings are gone.

---

## Tasks

### Task 2.1: Resolve any wheel gaps from Phase 1 [Simple-Medium]
**File:** [requirements.txt](../../../requirements.txt) and/or [requirements-dev.txt](../../../requirements-dev.txt)
**Tests:** Re-run Phase 1 dry-run for sanity

- [ ] Apply each resolution from [findings/wheel_gaps.md](findings/wheel_gaps.md)
- [ ] If a pin was added/changed, commit the change to a fresh feature branch (e.g. `proj-295-py-upgrade`)

**Notes:** Skip this task entirely if Phase 1 reported "No gaps."

---

### Task 2.2: (Optional, per Phase 0 Q5) Create root-level `.venv` [Simple]
**File:** N/A — env creation
**Tests:** N/A

- [ ] `py -<TARGET> -m venv .venv`
- [ ] On Windows: `.\.venv\Scripts\Activate.ps1` (and document this in CLAUDE.md update later)
- [ ] `.\.venv\Scripts\python.exe -m pip install --upgrade pip`

**Notes:** Skip if Phase 0 Q5 said no to introducing `.venv`.

---

### Task 2.3: (Optional, per Phase 0 Q5) Create `pyproject.toml` with `requires-python` [Simple]
**File:** [pyproject.toml](../../../pyproject.toml) (new file at repo root)
**Tests:** N/A

- [ ] Create with minimal content:
  ```toml
  [project]
  name = "starship-battles"
  requires-python = ">=<TARGET>"
  ```
- [ ] No need for full PEP 621 metadata; this single declaration prevents accidental 3.10 installs

**Notes:** Skip if Phase 0 Q5 said no.

---

### Task 2.4: Install runtime + dev requirements [Simple]
**File:** N/A
**Tests:** N/A

- [ ] `pip install -r requirements.txt`
- [ ] `pip install -r requirements-dev.txt`
- [ ] `pip list` to confirm versions
- [ ] Save versions: `pip freeze > Projects/active_projects/PROJ-295/findings/installed_versions.txt`

**Notes:**

---

### Task 2.5: Run full sharded test suite [Medium]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run the sharded suite. Baseline expectation: 15109+ tests, ~70s wall time on 16 shards.
- [ ] If any test fails:
  - Investigate root cause (3.11+ behavior change in stdlib? changed library behavior?)
  - Categorize: (a) genuine regression we must fix, (b) flaky/order-dependent (re-run to confirm), (c) test-side assumption that broke
  - Fix the root cause; do NOT mask via test changes unless the test was wrong
- [ ] Iterate until 100% green
- [ ] Save final pass output: `python Tools/test_sharded/test_sharded.py | tee Projects/active_projects/PROJ-295/findings/regression_run.log`

**Notes:** Per CLAUDE.md Rule 1 (TDD), failing tests are the regression detector. The 15K-test suite is the verification surface.

---

### Task 2.6: Manual game smoke [Simple]
**File:** N/A — runtime check
**Tests:** Manual

- [ ] Launch: `python launcher.py`
- [ ] Start a quickstart game
- [ ] Run a battle
- [ ] Confirm no new warnings/errors in stderr that weren't there on 3.10
- [ ] Quit cleanly

**Notes:**

---

### Task 2.7: Manual qa_launcher smoke (verify Google FutureWarnings gone) [Simple]
**File:** N/A
**Tests:** Manual

- [ ] Launch: `python qa_launcher.py`
- [ ] Run a brief play session, quit
- [ ] Confirm in stderr that **none** of these warnings appear:
  - `FutureWarning: You are using a Python version (3.10.11) which Google will stop supporting...` (× 2)
- [ ] If any *new* warnings appear, log them to [findings/post_upgrade_warnings.md](findings/post_upgrade_warnings.md) for follow-up

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Full sharded suite is green on the target Python
- [ ] Game launches and runs cleanly
- [ ] Google FutureWarnings absent
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Phase 3 — documentation"
