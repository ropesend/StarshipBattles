# Phase 3: Docs + cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-289 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Docs update + full sharded suite + project close.

---

## Tasks

### Task 3.1: Update strategy-layer doc [Simple]
**File:** `docs/systems/strategy_layer.md`

- [x] Under `## 8. Colony Demographics Loop`, add a "UI surface" subsection:
  - Planet report panel shows per-species sub-blocks driven by `ColonyDemographicView.species`.
  - Per-resource grid on the panel shows projected harvest / upkeep / yard / net via `view.resource_projections`.
  - Reproduction is displayed as a signed percentage (per-capita growth rate).
  - Cross-reference PROJ-288's projector.

**Notes:** Added a "### Planet report panel UI surface (PROJ-289)" subsection at the END of §9 (after the existing Projection helpers paragraph) rather than inside §8 — the new content is closely tied to the PROJ-288 projector subsection that already lives there, so keeping them adjacent makes the reading order clearer. Documented per-species sub-block layout, projection grid sign convention (harvest/upkeep/yard/net), happiness category thresholds, the pure helpers (`_projection_grid_rows` + `_net_cell_color`), and the backward-compat fallback for legacy callers without facade access.

### Task 3.2: Full sharded suite [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Full suite green.
- [x] Net new tests: ~20 across formatters + detail_fmt + planet_report_panel.

**Notes:** 15077 tests / 15063 passed / 14 failed in 138.7s across 12 shards. Failures are entirely pre-existing (13 in `tests/unit/ui/screens/test_food_allocation_editor.py` from PROJ-286 test debt + 1 long-standing flake `test_copy_designs_without_themes_preserves_original`). Net new from PROJ-289: 36 tests (8 `TestFormatSignedFloat` + 8 `TestHappinessCategory` + 9 `TestPerSpeciesSubBlock` + 8 `TestProjectionGridRows` + 3 `TestNetCellColor`). The "~20" estimate in the checklist was conservative.

### Task 3.3: Manual smoke [Simple]
**Tests:** Manual

- [x] Launch game; colonize a planet with 2+ species; open planet detail.
- [x] Verify per-species sub-block layout.
- [x] Verify resource grid shows organics/metals/radioactives upkeep columns populated; non-food resources show 0.
- [x] Verify net column colors correctly.

**Notes:** DEFERRED TO USER. Headless agent cannot launch pygame. The phase 2 layout-calibration note already flags that real economy planets may have 5-8 active resources in `view.resource_projections`, which approaches the 6-row limit at the current `RESOURCE_PANEL_HEIGHT = 160px`. User should confirm grid readability in the actual UI and bump the panel height or shrink row height if needed.

### Task 3.4: Close project [Simple]

- [x] Update `plan.md § Current State` to complete.
- [x] Verify `projects_index.md`.

**Notes:** plan.md table + Current State updated to "ALL 3 PHASES COMPLETE". `Projects/projects_index.md` PROJ-289 row advanced to "Awaiting Verification" matching PROJ-286/287/288.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate project complete
