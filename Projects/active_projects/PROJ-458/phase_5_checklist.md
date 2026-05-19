# PROJ-458 Phase 5: RadiationShieldEditor (231 LOC)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-458 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** Phase 4 complete (the recipe is now proven on 3 of 4 PlanetTargetEditor subclasses).
**Review Mode:** standard
**Objective:** Apply Pattern #33 two-stage `bypass_init` retrofit to `RadiationShieldEditor` (231 LOC). Final phase — PROJ-458 closes when this lands.

**Source-of-truth finding:** F-C-017 (RadiationShieldEditor row) in [`findings/PROJ-458_findings.md`](findings/PROJ-458_findings.md).

**Existing structure (verified 2026-05-19):**
- Inherits from `PlanetTargetEditor` (`game/ui/screens/planet_target_editor_base.py`).
- 231 LOC.

---

## Tasks

### Task 5.1: Read RadiationShieldEditor + plan retrofit [Simple]
**File:** `game/ui/screens/radiation_shield_editor.py` (read-only)

- [ ] Read `radiation_shield_editor.py` end-to-end. Note radiation-shield-specific state fields (shield strength target, shielding tech tier, etc.), widget construction, callback shapes.
- [ ] Note any differences from the other 3 PlanetTargetEditor subclasses — e.g. radiation shield may have different unit ranges, may not have a species-ideal preset (radiation is a hazard, not a preference).

### Task 5.2: Write dedicated characterization tests (RED) [Medium]
**File:** `tests/unit/ui/screens/test_radiation_shield_editor.py` (new)
**Tests:** `pytest tests/unit/ui/screens/test_radiation_shield_editor.py -q`

- [ ] Mirror Phase 2-4 test classes; adjust for radiation-specific surface.
- [ ] **Test class: TestConstruction** — bypass-init + production + window-manager-required.
- [ ] **Test class: TestRadiationSliderInteraction** — initial values from `planet.radiation_shield_target`; slider→label updates.
- [ ] **Test class: TestSpeciesIdealPreset** — only if applicable; if radiation has no species-ideal preset, drop this class.
- [ ] **Test class: TestApplyCallback** — Apply emits `(planet_id, radiation_value)`.
- [ ] **Test class: TestCloseCallback** — Close calls `on_close_callback`.
- [ ] Run; expect all to FAIL initially.

### Task 5.3: Apply the two-stage retrofit (GREEN) [Medium]
**File:** `game/ui/screens/radiation_shield_editor.py`
**Tests:** `pytest tests/unit/ui/screens/test_radiation_shield_editor.py tests/unit/ui/screens/test_strategy_modal_window.py::TestStrategyOnlyWindowsRequireExplicitWindowManager -q`

- [ ] Rewrite `__init__` to two-stage shape.
- [ ] Move widget construction into `DefaultRadiationShieldEditorUiBuilder`.
- [ ] Run characterization tests; all GREEN.
- [ ] Run parametrized window-manager test; no regression.

### Task 5.4: Final PROJ-458 verification [Simple]

- [ ] Run targeted tests; sharded suite green.
- [ ] All 5 windows now retrofitted:
  - [ ] `settings_window.py` (Phase 1)
  - [ ] `atmosphere_target_editor.py` (Phase 2)
  - [ ] `gravity_target_editor.py` (Phase 3)
  - [ ] `water_target_editor.py` (Phase 4)
  - [ ] `radiation_shield_editor.py` (Phase 5)
- [ ] All 5 dedicated test files exist at `tests/unit/ui/screens/test_<window>.py`.
- [ ] F-C-017 and F-C-016 fully closed in `findings/PROJ-458_findings.md`.
- [ ] Verify no regression on incidental coverage:
  - `tests/unit/ui/screens/test_strategy_modal_window.py:367-398` (parametrized test for the 4 PlanetTargetEditor subclasses + FoodAllocationEditor).
  - `tests/unit/ui/screens/strategy_windows/test_empire_panel_ctrl.py:100-127` (SettingsRegistrar → SettingsWindow).
- [ ] Update `Projects/projects_index.md` PROJ-458 row to `Complete`.

### Task 5.5: Codex end-of-project consult (recommended) [Simple]

- [ ] Invoke `/claude-consult codex` with a prompt like:
  ```
  Review PROJ-458's 5-window UIWindow retrofit. Verify (a) all 5 retrofits land Pattern #33's two-stage shape end-to-end (Stage 1 above guard / bypass guard / Stage 2 below); (b) every dedicated characterization test file locks behavior (state transitions, validation, callbacks) not just structural concerns; (c) the F-C-016 docs touch points at the right pattern reference; (d) the parametrized incidental-coverage test at test_strategy_modal_window.py:367-398 still passes for all 4 PlanetTargetEditor subclasses; (e) no regression in the 6 already-retrofitted UIWindow subclasses (race_setup, new_game_setup, etc.).
  ```
- [ ] Verify findings against code; remediate MUST-FIX-NOW items in a new commit before closing.

---

## Phase Completion Checklist

When all 5 tasks are checked off:
- [ ] F-C-017 (RadiationShieldEditor) flipped to `Status: resolved` in `findings/PROJ-458_findings.md`.
- [ ] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green.
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-458 5` — PASSED.
- [ ] Update status at top of this file to `Complete`.
- [ ] Update plan.md phase table row to `Complete` (and mark PROJ-458 as Project Complete in `plan.md` Current State).
- [ ] Update `Projects/projects_index.md` PROJ-458 row to `Complete`.
- [ ] Commit message: `PROJ-458 Phase 5: retrofit RadiationShieldEditor to two-stage bypass-init + dedicated characterization tests; PROJ-458 complete`.
- [ ] No new entries in `AgentCoordination/discovered_issues/log.jsonl` unless they are genuine out-of-scope discoveries.

## Project Completion Checklist (last phase)

When all 5 phases complete:
- [ ] All 5 phase checklists complete.
- [ ] Final sharded-suite green run.
- [ ] All 5 target windows have two-stage `__init__` with `if getattr(type(self), 'bypass_init', False): return` guard.
- [ ] All 5 dedicated characterization test files exist and pass.
- [ ] No regression on the incidental coverage tests at `test_strategy_modal_window.py:367-398` and `test_empire_panel_ctrl.py:100-127`.
- [ ] F-C-017 + F-C-016 closed in `findings/PROJ-458_findings.md`.
- [ ] `docs/known-issues.md:37` stale-doc warning paragraph removed by Phase 1 (F-C-016). The `tests/fixtures/README.md` half was already resolved at HEAD as of 2026-05-19 (codex r5 audit) — no edit needed there.
- [ ] Codex end-of-project consult landed; verified findings remediated.
- [ ] User applies the `verified` label and closes the project.
