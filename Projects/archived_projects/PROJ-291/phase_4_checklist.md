# Phase 4: Docs + final suite + PROJ-283..290 sign-off handoff

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-291 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Awaiting User Verification (Tasks 4.1–4.4 complete; 4.5–4.7 require user manual-smoke + Archive sign-off)
**Objective:** Update docs to reflect the engine retrofit + editor migration. Run the full sharded suite. Move PROJ-283..290 to Archived after user manual smoke. Move the dual-audit reports to durable storage.

---

## Tasks

### Task 4.1: Move audit reports to findings/ for durable storage [Simple]
**File:** `Temp Review Docs/` → `Projects/active_projects/PROJ-291/findings/`

- [x] Verify `findings/` exists (created by `create_project.py`).
- [x] Copy each file (do NOT move yet — leave originals in place until user verifies). All 6 audit reports already present in findings/ at project-start (copied during scaffolding).
- [x] Add an `INDEX.md` in `findings/` cross-referencing each file with one-line summaries (already in SUMMARY.md but worth a focused index).
- [x] Confirm with user before deleting the `Temp Review Docs/` directory. Default: leave the originals; user deletes manually after verification.

**Notes:**

### Task 4.2: Update PROJ-287 decisions.md to forward-link the reversal [Simple]
**File:** [Projects/active_projects/PROJ-287/decisions.md](Projects/active_projects/PROJ-287/decisions.md)

- [x] Open the file. Find the line: `2026-04-18 | Do NOT migrate PopulationEngine._get_race_config / HappinessEngine._get_race_config to the new registry. ...`
- [x] Add a new row (stamped `2026-04-19 (PROJ-291 reversal)`) documenting the retrofit + the link to PROJ-291/design.md.
- [x] Verify the link renders.

**Notes:** Preserves the historical record (the original deferral stays in the table) while making the reversal discoverable.

### Task 4.3: Update strategy_layer.md + 04_SERVICES.md [Simple]
**File:** [docs/systems/strategy_layer.md](docs/systems/strategy_layer.md), [docs/04_SERVICES.md](docs/04_SERVICES.md)

- [x] Open `docs/systems/strategy_layer.md` § Demographics Loop. Added a `### Multi-species engine resolution (PROJ-291 Phase 2)` subsection documenting the registry consult, the tightened legacy fallback, and the Session→TurnEngine→engine wiring. Also updated the `FoodAllocationEditor` paragraph (PROJ-291 C2 multi-resource preview) and the `EconomyConfig` paragraph (population_food_resource shim retirement).
- [x] Open `docs/04_SERVICES.md` Race Registry section. Added a new "Consumers" subsection listing all IRaceRegistry consumers including HappinessEngine, PopulationEngine, TurnEngine (via kwarg), and GameSession.race_registry.
- [x] Verify both docs render and cross-link correctly.

**Notes:**

### Task 4.4: Run the full sharded suite [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Run the full suite. Actual outcome: **15113 tests total, 15112 passed, 1 failed** — the expected long-standing `test_copy_designs_without_themes_preserves_original` theme-bleed flake. Within expected envelope.
- [x] Diff the failure list against baseline. 13 food-editor failures GONE (migrated by Phase 3). Only the 1 flake remains — matches the handoff's baseline expectation (baseline was 14 failures: 13 food-editor + 1 flake).
- [x] No NEW failures introduced by PROJ-291.

**Notes:**

### Task 4.5: Manual smoke (DEFERRED TO USER) [Manual]
**Tests:** Manual play-through

- [ ] **User:** open the FoodAllocationEditor on a 2-species colony. Confirm: no AttributeError, per-resource preview rows display, slider responsiveness preserved.
- [ ] **User:** open the Treasury panel on an empire with population. Confirm: Total row equals Tributes + Ships + Complexes + Population Upkeep (cross-check with row magnitudes).
- [ ] **User:** construct a 2-species colony (humans + voidari) with distinct race configs. Run a turn. Confirm: per-species sub-block (PROJ-289) shows DIFFERENT growth rates and DIFFERENT happiness values for the two species.

**Notes:** Headless agent cannot perform pygame UI smokes. User-driven step.

### Task 4.6: Move PROJ-283..290 to Archived + register PROJ-291 + PROJ-292 [Simple]
**File:** [Projects/projects_index.md](Projects/projects_index.md)

- [ ] **User-gated:** After user confirms manual smoke (Task 4.5):
- [ ] **User-gated:** Update each PROJ-283..290 row from `Awaiting Verification` to `Archived` and move to the Archived Projects table.
- [ ] **User-gated:** Confirm PROJ-291 + PROJ-292 entries exist (they were added by `create_project.py`). Update PROJ-291 to `Awaiting Verification`. Leave PROJ-292 at whatever its phase status is.
- [ ] **User-gated:** Fix the line-1 `w# Projects Index` typo while you're there (prior-audit m17).

**Notes:**

### Task 4.7: Final validation [Simple]
**Tests:** `python Projects/scripts/validate_phase.py PROJ-291 4`

- [ ] Validator passes.
- [ ] Phase 4 status updated to `Complete` in this file.
- [ ] plan.md `Current State` updated: "ALL 4 PHASES COMPLETE — awaiting user sign-off + Temp Review Docs/ cleanup".

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
