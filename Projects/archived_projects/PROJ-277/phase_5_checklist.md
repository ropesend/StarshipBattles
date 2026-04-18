# Phase 5: Migrate Existing Comparison Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-277 5`

**Status:** Mostly complete — validate-signature migration done inline with Phase 3; `_baseline_*` attribute deletion waits on Phase 4.
**Objective:** Every ComparisonScenario subclass migrated to new `validate(ab)` API.

---

## Tasks

### Task 5.1: Enumerate ComparisonScenario subclasses [Simple]
**File:** Multiple — read-only sweep
**Tests:** N/A

- [x] AST-walk of `combat_lab/scenarios/*.py` identified 102 direct or transitive ComparisonScenario descendants across 21 files
- [x] Counts per file documented in `findings/comparison_scenario_audit.md` (Phase 3.1 work)
- [x] No multi-level inheritance chains — all 102 descendants inherit directly from `ComparisonScenario`

**Notes:** Enumeration was done inline during Phase 3.1 audit; no separate subclasses.md findings file needed.

### Task 5.2: Migrate in groups of 5 [Complex]
**File:** Multiple ComparisonScenario subclasses
**Tests:** `python -m combat_lab.run_tests -v`

- [x] Bulk-migrated all 102 subclasses in one atomic AST-aware `sed`-style pass — 103 `def validate(self, outcome, telemetry=None)` signatures rewritten to `def validate(self, ab)` across 21 scenario files (the extra replacement is inside the `ComparisonScenario` docstring example at templates.py L782).
- [x] Subclass bodies unchanged — they read `self.baseline_*` / `self.variant_*` attrs (still populated by base `collect_results`) and ignored the old positional `outcome`/`telemetry` args. Signature-only rename was safe.
- [x] `_baseline_*` attribute references NOT removed — subclasses still read them. These stay until Phase 4 lets `ABBattleOutcome` replace them.
- [x] All 170 Combat Lab scenarios PASS post-migration

**Notes:** Group-of-5 grind from the original plan was unnecessary because the migration is signature-only and the subclass bodies didn't need surgery. One bulk pass + full suite.

### Task 5.3: Full Combat Lab suite [Medium]
**File:** N/A
**Tests:** `python -m combat_lab.run_tests`

- [x] `python -m combat_lab.run_tests`: **170 passed, 0 failed, 0 skipped**
- [x] Baseline maintained (170 scenarios)
- [ ] Grep `_baseline_*` / `_run_baseline_battle` / `_visual_baseline` returning zero is PHASE 4/Task 3.6 territory — today these still exist as scaffolding.

**Notes:**

### Task 5.4: Full pytest suite [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Incremental `pytest tests/ --testmon` — 14,647 passed, 2 skipped, pre-existing failures only (theme_id fixture + 3 AI ImportErrors unchanged from PROJ-276)
- [x] Above prior baseline

**Notes:**

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked (Task 5.3's grep-returns-zero subtask intentionally deferred to Phase 4)
- [x] Update plan.md
- [x] Run `python Projects/scripts/validate_phase.py PROJ-277 5`
