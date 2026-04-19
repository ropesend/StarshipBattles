# Phase 4: Docs + final suite + PROJ-283..290 sign-off handoff

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-291 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update docs to reflect the engine retrofit + editor migration. Run the full sharded suite. Move PROJ-283..290 to Archived after user manual smoke. Move the dual-audit reports to durable storage.

---

## Tasks

### Task 4.1: Move audit reports to findings/ for durable storage [Simple]
**File:** `Temp Review Docs/` → `Projects/active_projects/PROJ-291/findings/`

- [ ] Verify `findings/` exists (created by `create_project.py`).
- [ ] Copy each file (do NOT move yet — leave originals in place until user verifies):
  ```bash
  cp "Temp Review Docs/SUMMARY.md" Projects/active_projects/PROJ-291/findings/
  cp "Temp Review Docs/pipeline_reachability_skeptic.md" Projects/active_projects/PROJ-291/findings/
  cp "Temp Review Docs/state_cache_skeptic.md" Projects/active_projects/PROJ-291/findings/
  cp "Temp Review Docs/architecture_shims_skeptic.md" Projects/active_projects/PROJ-291/findings/
  cp "Temp Review Docs/merge_hazards_skeptic.md" Projects/active_projects/PROJ-291/findings/
  cp "Temp Review Docs/tests_docs_skeptic.md" Projects/active_projects/PROJ-291/findings/
  ```
- [ ] Add an `INDEX.md` in `findings/` cross-referencing each file with one-line summaries (already in SUMMARY.md but worth a focused index).
- [ ] Confirm with user before deleting the `Temp Review Docs/` directory. Default: leave the originals; user deletes manually after verification.

**Notes:**

### Task 4.2: Update PROJ-287 decisions.md to forward-link the reversal [Simple]
**File:** [Projects/active_projects/PROJ-287/decisions.md](Projects/active_projects/PROJ-287/decisions.md)

- [ ] Open the file. Find the line: `2026-04-18 | Do NOT migrate PopulationEngine._get_race_config / HappinessEngine._get_race_config to the new registry. ...`
- [ ] Add a new row:
  ```
  | 2026-04-18 (PROJ-291 update) | REVERSAL: PROJ-291 Phase 2 retrofitted both engines to consume `IRaceRegistry` per the standard PROJ-285 pattern. The original deferral was made before multi-species colonies were a reachable game state; post-PROJ-284/286/289 they are, exposing the silent dual-return bug in `_get_race_config`. See PROJ-291 design.md § Architecture for the retrofit shape. |
  ```
- [ ] Verify the link renders.

**Notes:** Preserves the historical record (the original deferral stays in the table) while making the reversal discoverable.

### Task 4.3: Update strategy_layer.md + 04_SERVICES.md [Simple]
**File:** [docs/systems/strategy_layer.md](docs/systems/strategy_layer.md), [docs/04_SERVICES.md](docs/04_SERVICES.md)

- [ ] Open `docs/systems/strategy_layer.md` § Demographics Loop (search for `Demographics`). Add a paragraph:
  ```
  ### Multi-species engine resolution (PROJ-291)

  HappinessEngine + PopulationEngine accept an optional `race_registry: IRaceRegistry` kwarg. When supplied, the engines resolve `pop.race_id → RaceConfig` via `registry.get_race(race_id)`, allowing multi-species colonies to compute happiness + growth using each species' OWN `base_happiness` / `base_reproduction_rate`. When the kwarg is None (legacy callers, MagicMock test fixtures), the engines fall back to the empire's primary `race_config` and gracefully skip non-matching species. PROJ-291 closed a silent dual-return bug where the legacy fallback returned the wrong race_config for non-primary species.
  ```
- [ ] Open `docs/04_SERVICES.md` Race Registry section. Add HappinessEngine + PopulationEngine to the consumers list (alongside the existing UI panel + projector consumers).
- [ ] Verify both docs render and cross-link correctly.

**Notes:**

### Task 4.4: Run the full sharded suite [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run the full suite. Expected outcome:
  - Total: ~15080 tests (15077 baseline + ~30 net new minus ~13 fixed = net ~+17).
  - Pass: ~15079.
  - Fail: 1 (the long-standing `test_copy_designs_without_themes_preserves_original` flake — pre-existing, not caused by PROJ-291).
- [ ] Diff the failure list against baseline (the dual-audit baseline was 14 failures: 13 PROJ-286 test debt + 1 flake). Confirm the 13 food-editor failures are gone.
- [ ] If any NEW failures appear, STOP and triage. Don't proceed to Task 4.5 with regressions.

**Notes:**

### Task 4.5: Manual smoke (DEFERRED TO USER) [Manual]
**Tests:** Manual play-through

- [ ] User opens the FoodAllocationEditor on a 2-species colony. Confirm: no AttributeError, per-resource preview rows display, slider responsiveness preserved.
- [ ] User opens the Treasury panel on an empire with population. Confirm: Total row equals Tributes + Ships + Complexes + Population Upkeep (cross-check with row magnitudes).
- [ ] User constructs a 2-species colony (humans + voidari) with distinct race configs. Run a turn. Confirm: per-species sub-block (PROJ-289) shows DIFFERENT growth rates and DIFFERENT happiness values for the two species.

**Notes:** Headless agent cannot perform pygame UI smokes. User-driven step.

### Task 4.6: Move PROJ-283..290 to Archived + register PROJ-291 + PROJ-292 [Simple]
**File:** [Projects/projects_index.md](Projects/projects_index.md)

- [ ] After user confirms manual smoke (Task 4.5):
- [ ] Update each PROJ-283..290 row from `Awaiting Verification` to `Archived` and move to the Archived Projects table.
- [ ] Confirm PROJ-291 + PROJ-292 entries exist (they were added by `create_project.py`). Update PROJ-291 to `Awaiting Verification`. Leave PROJ-292 at whatever its phase status is.
- [ ] Fix the line-1 `w# Projects Index` typo while you're there (prior-audit m17).

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
