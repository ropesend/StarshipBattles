# Phase 6: Docs + final suite + project close

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-292 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update docs to reflect H1 + M1 + H3 changes. Run the full sharded suite. Close PROJ-292 and update projects_index.md.

---

## Tasks

### Task 6.1: Update docs/04_SERVICES.md with EmpireEconomyService [Simple]
**File:** [docs/04_SERVICES.md](docs/04_SERVICES.md)

- [ ] Find the strategy-layer service catalogue. Add an entry for `EmpireEconomyService` (PROJ-292 M1):
  - Location: `game/strategy/services/empire_economy_service.py`.
  - Public surface: `get_snapshot(empire) -> EmpireEconomySnapshot`.
  - Replaces direct UI imports of `EmpireEconomyCalculator` from the engine layer. Closes the layer-violation backlog from the dual cross-project audit.
- [ ] Confirm cross-references render.

**Notes:**

### Task 6.2: Update docs/systems/strategy_layer.md for H1 view-threading completion [Simple]
**File:** [docs/systems/strategy_layer.md](docs/systems/strategy_layer.md)

- [ ] Find the existing PROJ-289 Planet Report Panel section. Add a paragraph noting that PROJ-292 H1 backfilled the `view` kwarg into PlanetListWindow + BuildQueuePanelFactory, so the per-species sub-block now displays in all colonized contexts.
- [ ] Verify links.

**Notes:**

### Task 6.3: Run the full sharded suite [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run the full suite. Expected outcome:
  - Total: ~15090 tests (15080 from PROJ-291 close + ~10 net new from this project).
  - Pass: ~15089.
  - Fail: 1 (the long-standing flake).
- [ ] No new failures from PROJ-292 changes.

**Notes:**

### Task 6.4: Manual smoke (DEFERRED TO USER) [Manual]
**Tests:** Manual play-through

- [ ] H1: open a colonized planet from PlanetListWindow. Confirm the per-species sub-block renders.
- [ ] H1: open a colonized planet from BuildQueuePanelFactory. Confirm same.
- [ ] H3: trigger a forced exception in net-cell colour code (or just confirm no regressions in normal play).
- [ ] M1: open the Treasury panel. Confirm no regression after the facade migration.

**Notes:** Headless agent cannot perform pygame UI smokes. User-driven. Combine with PROJ-291 Phase 4 Task 4.5 in a single sitting per the MANUAL_SMOKE_CHECKLIST.md (Phase 5 Task 5.9 deliverable).

### Task 6.5: Update projects_index.md [Simple]
**File:** [Projects/projects_index.md](Projects/projects_index.md)

- [ ] Update PROJ-292 row to `Awaiting Verification` (or `Archived` if the user has already confirmed manual smoke).
- [ ] Verify the typo from Phase 5 Task 5.1 is gone.

**Notes:**

### Task 6.6: Final validation [Simple]
**Tests:** `python Projects/scripts/validate_phase.py PROJ-292 6`

- [ ] Validator passes.
- [ ] Phase 6 status updated to `Complete` in this file.
- [ ] plan.md `Current State` updated: "ALL 6 PHASES COMPLETE — awaiting user sign-off".

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
