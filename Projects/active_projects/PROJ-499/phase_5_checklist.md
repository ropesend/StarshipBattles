# Phase 5: Documentation + closeout

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-499 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Finalize the harness survey doc, fix the now-stale `tests/README.md` claim, and check `docs/` for any references that need updating. Audit F5 (audit response.md:23) expanded this beyond `docs/` to include `tests/README.md` which currently misdescribes the modifier-snapshot harness as "skip on first run."

---

## Tasks

### Task 5.1: Finalize harness survey doc [Simple]
**File:** `Projects/active_projects/PROJ-499/findings/harness_survey.md`
**Tests:** none (documentation)

- [ ] Open `findings/harness_survey.md` (written during planning).
- [ ] Confirm the table lists every harness checked (Codex's first consult + audit added perf benches at `tests/performance/bench_turn_processing.py:206-270` and `tests/performance/bench_galaxy_planet_star.py:143-204`, plus `tests/fixtures/strategy/galaxy_repro_baseline.py:247-249`).
- [ ] Add the perf-bench harnesses to the table (verdict: numeric thresholds, not dict walks; not affected).
- [ ] Add a closing note: "PROJ-499 only modifies `tests/regression/modifier_ability_snapshots/conftest.py`. No other harness needs the same treatment."
- [ ] Reference both Codex consult responses at `AgentCoordination/Scratchpad/Consult/20260523T125809Z_plan-snapshot-harness-fix/response.md` and `AgentCoordination/Scratchpad/Consult/20260523T131241Z_audit-PROJ-499/response.md`.

**Notes:** [Filled during execution]

### Task 5.2: Fix the stale `tests/README.md` claim [Simple]
**File:** `tests/README.md:552-555`
**Tests:** none (documentation)

- [ ] Open `tests/README.md`, locate the "Snapshot Regression Tests (`tests/regression/`)" subsection at lines 552-555. Current text says baselines "skip on first run."
- [ ] Update to reflect actual behavior: `fail_missing_baseline()` at `conftest.py:201-217` writes the missing baseline AND fails the test loudly. The "skip" wording predates PROJ-446 Phase 1 Task 1.4 (F-C-025).
- [ ] Suggested replacement: "Tests in `modifier_ability_snapshots/` LOUDLY FAIL on missing baselines via `fail_missing_baseline()`; the helper writes the fresh baseline to disk so the maintainer can inspect, accept, and commit before re-running. There is no silent skip."

**Notes:** [Filled during execution]

### Task 5.3: Cross-reference from `docs/` if appropriate [Simple]
**File:** `docs/` (if a test-infrastructure doc exists that mentions snapshot harnesses)
**Tests:** none

- [ ] Search `docs/` for any reference to `compare_snapshots` or `modifier_ability_snapshots`.
- [ ] If found, update to reflect the new symmetric behavior. If not found, no doc edit required.
- [ ] If a snapshot/golden-test convention doc exists, add a one-line cross-reference to PROJ-499.

**Notes:** [Filled during execution]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Survey doc finalized + perf benches added
- [ ] `tests/README.md` "skip on first run" claim corrected
- [ ] `docs/` cross-references checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State — project complete; dispatch end-of-project codex audit per protocol §10
