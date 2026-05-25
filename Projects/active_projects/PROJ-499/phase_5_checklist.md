# Phase 5: Documentation + closeout

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-499 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Finalize the harness survey doc, fix the now-stale `tests/README.md` claim, and check `docs/` for any references that need updating. Audit F5 (audit response.md:23) expanded this beyond `docs/` to include `tests/README.md` which currently misdescribes the modifier-snapshot harness as "skip on first run."

---

## Tasks

### Task 5.1: Finalize harness survey doc [Simple]
**File:** `Projects/active_projects/PROJ-499/findings/harness_survey.md`
**Tests:** none (documentation)

- [x] Open `findings/harness_survey.md` (written during planning).
- [x] Confirm the table lists every harness checked (Codex's first consult + audit added perf benches at `tests/performance/bench_turn_processing.py:206-270` and `tests/performance/bench_galaxy_planet_star.py:143-204`, plus `tests/fixtures/strategy/galaxy_repro_baseline.py:247-249`).
- [x] Add the perf-bench harnesses to the table (verdict: numeric thresholds, not dict walks; not affected).
- [x] Add a closing note: "PROJ-499 only modifies `tests/regression/modifier_ability_snapshots/conftest.py`. No other harness needs the same treatment."
- [x] Reference both Codex consult responses at `AgentCoordination/Scratchpad/Consult/20260523T125809Z_plan-snapshot-harness-fix/response.md` and `AgentCoordination/Scratchpad/Consult/20260523T131241Z_audit-PROJ-499/response.md`.

**Notes:**
- Survey table now has 11 rows: 1 gap (the modifier-ability harness itself), 7 strict harnesses (deep_compare, state_snapshot, save_load, save_round_trip, galaxy_reproducibility, ship_stats_golden, golden_fixture_field_coverage), 2 perf benches (bench_turn_processing, bench_galaxy_planet_star), 1 fixture writer (galaxy_repro_baseline), 1 PROJ-498 boolean pair-check (test_allowance_matrix).
- Closing note + both consult-response references present.
- Phase 0 Task 0.2 re-verified the survey via `Grep compare_snapshots|deep_compare|json.load`. No new asymmetric comparators surfaced.

### Task 5.2: Fix the stale `tests/README.md` claim [Simple]
**File:** `tests/README.md:552-555`
**Tests:** none (documentation)

- [x] Open `tests/README.md`, locate the "Snapshot Regression Tests (`tests/regression/`)" subsection at lines 552-555. Current text says baselines "skip on first run."
- [x] Update to reflect actual behavior: `fail_missing_baseline()` at `conftest.py:201-217` writes the missing baseline AND fails the test loudly. The "skip" wording predates PROJ-446 Phase 1 Task 1.4 (F-C-025).
- [x] Suggested replacement: "Tests in `modifier_ability_snapshots/` LOUDLY FAIL on missing baselines via `fail_missing_baseline()`; the helper writes the fresh baseline to disk so the maintainer can inspect, accept, and commit before re-running. There is no silent skip."

**Notes:**
- Updated `tests/README.md` lines 552-555. Added a second bullet noting PROJ-499 symmetric comparator behavior so future readers see the full contract.

### Task 5.3: Cross-reference from `docs/` if appropriate [Simple]
**File:** `docs/` (if a test-infrastructure doc exists that mentions snapshot harnesses)
**Tests:** none

- [x] Search `docs/` for any reference to `compare_snapshots` or `modifier_ability_snapshots`.
- [x] If found, update to reflect the new symmetric behavior. If not found, no doc edit required.
- [x] If a snapshot/golden-test convention doc exists, add a one-line cross-reference to PROJ-499.

**Notes:**
- `Grep compare_snapshots|modifier_ability_snapshots` over `docs/` returned 2 files (`docs/guides/modifier_system.md` and `docs/guides/adding_modifiers.md`), but BOTH only reference the test PATH (`pytest tests/regression/modifier_ability_snapshots/...`) — neither makes any behavioral claim about `compare_snapshots()` or "skip on first run." No doc edit required.
- No snapshot/golden-test convention doc exists in `docs/` (Grep over `docs/` for snapshot/golden testing conventions returns no matches). No cross-reference needed.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Survey doc finalized + perf benches added
- [x] `tests/README.md` "skip on first run" claim corrected
- [x] `docs/` cross-references checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State — project complete; dispatch end-of-project codex audit per protocol §10
