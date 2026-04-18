# Phase 1: Audit responsibilities of FleetBattleSetupScreen + study TestLab MVVM exemplar

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-282 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Map every method on `FleetBattleSetupScreen` to its target delegate (ViewModel / Renderer / InputHandler / Controller / FleetHierarchyEditor / stays-on-screen). Study the TestLab MVVM exemplar end-to-end. Audit existing test coverage. No code changes — this phase produces the migration map that drives Phases 2-8.

---

## Tasks

### Task 1.1: Read FleetBattleSetupScreen end-to-end [Medium]
**File:** `game/ui/screens/battle_setup_screen.py`
**Tests:** N/A (research)

- [ ] Read all 1172 lines, taking notes
- [ ] Document every method with: name, line range, purpose, whether it mutates state vs reads it vs renders
- [ ] Document every instance attribute with: name, type, whether it's view state, business state, or a delegate reference

**Notes:**

### Task 1.2: Build method-to-delegate map [Medium]
**File:** `.agent_reports/PROJ-282-audit/delegate_map.md` (NEW)
**Tests:** N/A

- [ ] For each method from Task 1.1, assign target: `screen` / `view_model` / `renderer` / `input_handler` / `controller` / `fleet_hierarchy_editor`
- [ ] Flag any method that doesn't fit cleanly (mixed concerns) — these need splitting
- [ ] Identify methods that should be deleted entirely (dead code, redundant)
- [ ] Quantify expected line count per delegate (target: each ≤300 lines, screen ≤150)

**Notes:**

### Task 1.3: Study TestLab MVVM exemplar [Medium]
**File:** `game/ui/screens/test_lab/` (all files)
**Tests:** N/A

- [ ] Read [screen.py](../../../game/ui/screens/test_lab/screen.py) — note the slim shell pattern
- [ ] Read the ViewModel — what kind of data lives there?
- [ ] Read the Renderer — how is layout calculated?
- [ ] Read the InputHandler — what's the event-to-controller dispatch shape?
- [ ] Read the Controller — what mutation operations does it expose?
- [ ] Document the conventions in `.agent_reports/PROJ-282-audit/testlab_pattern.md`

**Notes:**

### Task 1.4: Audit existing test coverage [Simple]
**File:** `.agent_reports/PROJ-282-audit/test_coverage.md` (NEW)
**Tests:** N/A

- [ ] Find all tests touching `FleetBattleSetupScreen` / `BattleSetupScreen` (alias)
- [ ] Find all tests touching `BattleSetupState`
- [ ] Note which screen behaviors are covered vs uncovered
- [ ] Flag uncovered behaviors — these get NEW tests during decomposition (regression safety)

**Notes:**

### Task 1.5: Document save/load shape today [Simple]
**File:** `.agent_reports/PROJ-282-audit/save_load.md` (NEW)
**Tests:** N/A

- [ ] Find where `BattleSetupState.to_dict` is called and where `from_dict` is called
- [ ] Document the JSON shape currently emitted
- [ ] Identify how `_complex_toggles` interacts with save/load today (it currently lives on the screen, not state — is it persisted at all?)
- [ ] Plan migration path for moving complex toggles into state without breaking existing save files

**Notes:**

### Task 1.6: Confirm N-team support paths [Simple]
**File:** `.agent_reports/PROJ-282-audit/n_team_paths.md` (NEW)
**Tests:** N/A

- [ ] Find all places in the screen that branch on `len(state.sides)` or `MIN_SIDES` / `MAX_SIDES`
- [ ] Confirm how add_side / remove_side flow through the UI today
- [ ] Document the pattern so the new InputHandler/Controller preserves it

**Notes:**

### Task 1.7: Synthesize migration plan [Medium]
**File:** `.agent_reports/PROJ-282-audit/migration_plan.md` (NEW)
**Tests:** N/A

- [ ] Combine outputs of 1.2, 1.3, 1.4, 1.5, 1.6
- [ ] Order phases 2-8 with dependencies clear
- [ ] List per-phase deliverables and file targets
- [ ] Recommend any plan adjustments for user review

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Audit reports saved to `.agent_reports/PROJ-282-audit/`
- [ ] Migration plan reviewed by user before Phase 2 starts
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2 (move `_complex_toggles` to state)
