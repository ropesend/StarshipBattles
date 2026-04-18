# Phase 1: Audit responsibilities of FleetBattleSetupScreen + study TestLab MVVM exemplar

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-282 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** In Progress (tasks 1.1–1.7 complete; final gate = user approval of migration plan)
**Objective:** Map every method on `FleetBattleSetupScreen` to its target delegate (ViewModel / Renderer / InputHandler / Controller / FleetHierarchyEditor / stays-on-screen). Study the TestLab MVVM exemplar end-to-end. Audit existing test coverage. No code changes — this phase produces the migration map that drives Phases 2-8.

---

## Tasks

### Task 1.1: Read FleetBattleSetupScreen end-to-end [Medium]
**File:** `game/ui/screens/battle_setup_screen.py`
**Tests:** N/A (research)

- [x] Read all 1172 lines, taking notes
- [x] Document every method with: name, line range, purpose, whether it mutates state vs reads it vs renders
- [x] Document every instance attribute with: name, type, whether it's view state, business state, or a delegate reference

**Notes:** Full audit in [.agent_reports/PROJ-282-audit/delegate_map.md](../../../.agent_reports/PROJ-282-audit/delegate_map.md). Largest single methods: `_build_center_panel` (199 LOC), `_build_left_panel` (131 LOC), `_handle_button` (105 LOC), `_duplicate_task_force` (58 LOC). Ship-cloning logic is duplicated across `_duplicate_task_force` and `_duplicate_squadron`. `_complex_toggles` dict (line 118) is data-pretending-to-be-UI-state; moves onto `BattleSetupSide` in Phase 2. **Bug found:** `_sync_complex_toggles_to_state` hardcodes sides 0 and 1 — sides 2-7 lose toggles at battle launch when N > 2. Phase 2 fix naturally resolves it.

### Task 1.2: Build method-to-delegate map [Medium]
**File:** `.agent_reports/PROJ-282-audit/delegate_map.md` (NEW)
**Tests:** N/A

- [x] For each method from Task 1.1, assign target: `screen` / `view_model` / `renderer` / `input_handler` / `controller` / `fleet_hierarchy_editor`
- [x] Flag any method that doesn't fit cleanly (mixed concerns) — these need splitting
- [x] Identify methods that should be deleted entirely (dead code, redundant)
- [x] Quantify expected line count per delegate (target: each ≤300 lines, screen ≤150)

**Notes:** [delegate_map.md](../../../.agent_reports/PROJ-282-audit/delegate_map.md). Total new code ~1430 LOC across 9 files vs 1172 LOC monolith today. Overhead buys: per-delegate testability, N-team UI wiring, `_complex_toggles` data-on-state fix, natural seams for future features.

### Task 1.3: Study TestLab MVVM exemplar [Medium]
**File:** `game/ui/screens/test_lab/` (all files)
**Tests:** N/A

- [x] Read [screen.py](../../../game/ui/screens/test_lab/screen.py) — note the slim shell pattern
- [x] Read the ViewModel — what kind of data lives there?
- [x] Read the Renderer — how is layout calculated?
- [x] Read the InputHandler — what's the event-to-controller dispatch shape?
- [x] Read the Controller — what mutation operations does it expose?
- [x] Document the conventions in `.agent_reports/PROJ-282-audit/testlab_pattern.md`

**Notes:** [testlab_pattern.md](../../../.agent_reports/PROJ-282-audit/testlab_pattern.md). Key conventions: pure ViewModel (no pygame imports), EventBus for state-changed events, custom-tag dispatch on pygame_gui elements, handles on view_model (not renderer). TestLab's renderer is monolithic (1193 LOC); PROJ-282's per-panel split is structurally better.

### Task 1.4: Audit existing test coverage [Simple]
**File:** `.agent_reports/PROJ-282-audit/test_coverage.md` (NEW)
**Tests:** N/A

- [x] Find all tests touching `FleetBattleSetupScreen` / `BattleSetupScreen` (alias)
- [x] Find all tests touching `BattleSetupState`
- [x] Note which screen behaviors are covered vs uncovered
- [x] Flag uncovered behaviors — these get NEW tests during decomposition (regression safety)

**Notes:** [test_coverage.md](../../../.agent_reports/PROJ-282-audit/test_coverage.md). **Zero existing tests of FleetBattleSetupScreen.** State-level and spec-compiler tests are solid (8 files total). `test_setup_screen.py` and part of `test_scene_protocol.py` actually test the OLD legacy `setup_screen.BattleSetupScreen` (pre-fleet) — separate class, out of PROJ-282 scope. Strategy: TDD each delegate as extracted; don't retro-test the god class.

### Task 1.5: Document save/load shape today [Simple]
**File:** `.agent_reports/PROJ-282-audit/save_load.md` (NEW)
**Tests:** N/A

- [x] Find where `BattleSetupState.to_dict` is called and where `from_dict` is called
- [x] Document the JSON shape currently emitted
- [x] Identify how `_complex_toggles` interacts with save/load today (it currently lives on the screen, not state — is it persisted at all?)
- [x] Plan migration path for moving complex toggles into state without breaking existing save files

**Notes:** [save_load.md](../../../.agent_reports/PROJ-282-audit/save_load.md). Current shape: `_complex_toggles` persisted as TOP-LEVEL key in save, parsed from `f"{side_id}_{scope}_{design_id}"` string keys. State-level `*_complexes` fields are always EMPTY on disk — only populated at battle-launch time by `_sync_complex_toggles_to_state`. **Recommendation (escalate to user):** fold `system_complexes: List[Dict]` → `system_complexes: Dict[str, bool]` on `BattleSetupSide`; discard legacy saves per CLAUDE.md §"Save files are disposable".

### Task 1.6: Confirm N-team support paths [Simple]
**File:** `.agent_reports/PROJ-282-audit/n_team_paths.md` (NEW)
**Tests:** N/A

- [x] Find all places in the screen that branch on `len(state.sides)` or `MIN_SIDES` / `MAX_SIDES`
- [x] Confirm how add_side / remove_side flow through the UI today
- [x] Document the pattern so the new InputHandler/Controller preserves it

**Notes:** [n_team_paths.md](../../../.agent_reports/PROJ-282-audit/n_team_paths.md). **Screen is effectively 2-team:** side dropdown hardcoded, fleet init hardcoded to `side_0`/`side_1`, `_sync_complex_toggles_to_state` hardcoded to sides 0/1. STATE layer fully supports N=2..8 (PROJ-275); SPEC COMPILER supports N teams; but the UI has no Add Side / Remove Side buttons. PROJ-282 must add them to preserve the N-team contract end-to-end. Recommendation: simple dropdown labeled "Side 0", "Side 1", ... (drop "Left"/"Right" cosmetics).

### Task 1.7: Synthesize migration plan [Medium]
**File:** `.agent_reports/PROJ-282-audit/migration_plan.md` (NEW)
**Tests:** N/A

- [x] Combine outputs of 1.2, 1.3, 1.4, 1.5, 1.6
- [x] Order phases 2-8 with dependencies clear
- [x] List per-phase deliverables and file targets
- [x] Recommend any plan adjustments for user review

**Notes:** [migration_plan.md](../../../.agent_reports/PROJ-282-audit/migration_plan.md). **Two decision points to escalate to user before Phase 2 starts:** (1) Save-file handling — discard legacy saves (per CLAUDE.md) vs. migrate. Recommend discard. (2) Data model shape — fold `*_complexes: List[Dict]` into `*_complex_toggles: Dict[str, bool]` (simpler, single-source) vs. keep both fields per current design.md. Recommend fold. Also flagged: add explicit Add-Side / Remove-Side UI subtasks to phases 4, 5, 6.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Audit reports saved to `.agent_reports/PROJ-282-audit/` (6 reports: delegate_map, testlab_pattern, test_coverage, save_load, n_team_paths, migration_plan)
- [ ] Migration plan reviewed by user before Phase 2 starts (**pending user decision on 2 escalated questions**)
- [ ] Update status at top of this file to `Complete` (currently `In Progress` pending user gate)
- [ ] Update plan.md phase table row to `Complete` (currently `Tasks Complete, User Review Pending`)
- [x] Update plan.md Current State to point to Phase 2 (move `_complex_toggles` to state)
