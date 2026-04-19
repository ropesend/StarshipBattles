# Phase 3: Docs + cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-289 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Docs update + full sharded suite + project close.

---

## Tasks

### Task 3.1: Update strategy-layer doc [Simple]
**File:** `docs/systems/strategy_layer.md`

- [ ] Under `## 8. Colony Demographics Loop`, add a "UI surface" subsection:
  - Planet report panel shows per-species sub-blocks driven by `ColonyDemographicView.species`.
  - Per-resource grid on the panel shows projected harvest / upkeep / yard / net via `view.resource_projections`.
  - Reproduction is displayed as a signed percentage (per-capita growth rate).
  - Cross-reference PROJ-288's projector.

**Notes:**

### Task 3.2: Full sharded suite [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full suite green.
- [ ] Net new tests: ~20 across formatters + detail_fmt + planet_report_panel.

**Notes:**

### Task 3.3: Manual smoke [Simple]
**Tests:** Manual

- [ ] Launch game; colonize a planet with 2+ species; open planet detail.
- [ ] Verify per-species sub-block layout.
- [ ] Verify resource grid shows organics/metals/radioactives upkeep columns populated; non-food resources show 0.
- [ ] Verify net column colors correctly.

**Notes:** DEFERRED TO USER if the agent cannot run pygame.

### Task 3.4: Close project [Simple]

- [ ] Update `plan.md § Current State` to complete.
- [ ] Verify `projects_index.md`.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
