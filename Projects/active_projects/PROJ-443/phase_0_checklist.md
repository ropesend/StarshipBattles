# Phase 0: Capture hidden-test baseline

**Status:** Not Started
**Depends on:** none
**Review Mode:** lightweight
**Files (planned):** `Projects/active_projects/PROJ-443/findings/hidden_test_baseline.md` (new)

**Objective:** Document the current pass/fail count and exact list of failing test IDs in every `tests/.../data/` directory currently hidden from the sharded suite. No code changes. Establishes the baseline ledger Phases 1-3 work against.

---

## Tasks

### Task 0.1: Enumerate hidden test directories [Simple]

- [ ] `find tests -type d -name data -not -path '*/__pycache__/*'` to list every test directory pytest's `norecursedirs = ... data ...` matches.
- [ ] Record the directory list in `findings/hidden_test_baseline.md` §"Hidden directories."

### Task 0.2: Capture pass/fail counts per hidden directory [Simple]

- [ ] Per hidden directory `<dir>`, run `pytest <dir> -q -n 4 --no-header > /tmp/<dirname>.out 2>&1` and extract the final `N passed, M failed` line.
- [ ] Record counts in `findings/hidden_test_baseline.md` §"Per-directory counts."

### Task 0.3: Capture exact failing test IDs [Simple]

- [ ] For each hidden directory, extract the `FAILED tests/...::test_*` lines into `findings/hidden_test_baseline.md` §"Failing test inventory."
- [ ] Tag each by likely cluster: `test_cargo_tracking.py` / `test_mutator_boundary_ast_guard.py` / other.

### Task 0.4: Verify sharded-baseline count is current [Simple]

- [ ] `python Tools/test_sharded/test_sharded.py 2>&1 | tail -5` — record TOTAL line.
- [ ] Record at the top of `findings/hidden_test_baseline.md` for context.

### Task 0.5: Commit the baseline ledger [Simple]

- [ ] `git add Projects/active_projects/PROJ-443/findings/hidden_test_baseline.md plan.md decisions.md phase_state.json`
- [ ] Commit message: `PROJ-443 Phase 0: capture hidden-test baseline`

---

## Phase Completion Checklist
- [ ] `findings/hidden_test_baseline.md` committed with directory list + counts + failing IDs
- [ ] `plan.md` Current State updated
- [ ] `phase_state.json` phase_0.status = `complete`, `phase_head_sha` recorded
