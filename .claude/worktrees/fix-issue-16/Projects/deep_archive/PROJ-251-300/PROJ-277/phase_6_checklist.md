# Phase 6: Documentation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-277 6`

**Status:** Complete (state-as-shipped documented; Phase 4 residual work called out inline)
**Objective:** Document A/B scenarios as first-class pattern; update memory.

---

## Tasks

### Task 6.1: Add "Writing A/B Scenarios" section [Medium]
**File:** `docs/guides/simulation_testing.md`
**Tests:** Manual review

- [x] Updated Pattern 3 section (`### Pattern 3: A/B Comparison Tests`) with PROJ-277 API:
  - Example uses `def validate(self, ab) -> list:` signature
  - Describes how to introspect `ab.baseline_outcome` / `ab.variant_outcome` / telemetry
  - Documents additive `build_baseline_spec` / `build_variant_spec` hooks
  - Notes the visual-baseline skip as a known follow-up (Phase 3.6 `render_mode`)
- [x] Updated section 9 "ComparisonScenario" engine-decisions entry to reflect `ab`-based validation + spec hooks
- [x] Left untouched: existing Pattern 5 BeamStopsWithoutEnergy code example (its `validate(self, outcome, telemetry)` signature got migrated to `validate(self, ab)` by the AST script; the doc snippet is still correct for the new API)

**Notes:** I did NOT add a brand-new "Writing A/B Scenarios" H2 section — instead amended the existing Pattern 3 section + engine-decisions block. The existing doc structure is better than fragmenting coverage.

### Task 6.2: Update memory [Simple]
**File:** `C:\Users\rossr\.claude\projects\c--Dev2-StarshipBattles\memory\`
**Tests:** Manual

- [x] Created `memory/project_proj277_ab_runner.md` — documents what shipped + what's deferred to Phase 4 with pointers into the code
- [x] Added index entry in `memory/MEMORY.md`
- [x] Path note: memory lives under `c--Dev2-StarshipBattles` (current repo dir), not `c--Dev-Starship-Battles` (old) — checklist's path was stale

**Notes:**

### Task 6.3: Final regression sweep [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py` + `python -m combat_lab.run_tests`

- [x] `python -m combat_lab.run_tests`: **170 passed, 0 failed, 0 skipped**
- [x] `python Tools/test_sharded/test_sharded.py`: **14,657 passed, 1 failed, 0 errors** — the 1 failure is the pre-existing theme_id/Klingons fixture issue unchanged from PROJ-276; previously-seen 3 ImportErrors have been fixed externally
- [x] Delta from PROJ-276 baseline (14,627): +30 tests (PROJ-277 additions)

**Notes:**

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update plan.md — project status updated
- [x] Run `python Projects/scripts/validate_phase.py PROJ-277 6`
- [x] User verification expectation filed as Phase 4 follow-up (visual-baseline validate-runs-anyway requires Phase 3.6 `render_mode` landing; today VB mode still preserves the legacy skip)
