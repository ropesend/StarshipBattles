# PROJ-458 Phase 4: WaterTargetEditor (227 LOC)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-458 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** Phase 3 complete (the recipe is now proven on 2 of 4 PlanetTargetEditor subclasses).
**Review Mode:** standard
**Objective:** Apply Pattern #33 two-stage `bypass_init` retrofit to `WaterTargetEditor` (227 LOC). Same recipe as Phases 2-3.

**Source-of-truth finding:** F-C-017 (WaterTargetEditor row) in [`findings/PROJ-458_findings.md`](findings/PROJ-458_findings.md).

**Existing structure (verified 2026-05-19):**
- Inherits from `PlanetTargetEditor` (`game/ui/screens/planet_target_editor_base.py`).
- 227 LOC.

---

## Tasks

### Task 4.1: Read WaterTargetEditor + plan retrofit [Simple]
**File:** `game/ui/screens/water_target_editor.py` (read-only)

- [x] Read `water_target_editor.py` end-to-end. Note water-specific state fields, widget construction, callback shapes, validation rules (water-specific: total + per-form / liquid / ice / vapor breakdown if applicable).

### Task 4.2: Write dedicated characterization tests (RED) [Medium]
**File:** `tests/unit/ui/screens/test_water_target_editor.py` (new)
**Tests:** `pytest tests/unit/ui/screens/test_water_target_editor.py -q`

- [x] Mirror the Phase 2/3 test classes. Adjust to water-specific surface.
- [x] **Test class: TestConstruction** — bypass-init + production + window-manager-required.
- [x] **Test class: TestWaterSliderInteraction** — initial values from `planet.water_target`; slider→label updates.
- [x] **Test class: TestSpeciesIdealPreset** — set-to-ideal populates from `race_config.water_preference`.
- [x] **Test class: TestApplyCallback** — Apply emits `(planet_id, water_dict)`.
- [x] **Test class: TestCloseCallback** — Close calls `on_close_callback`.
- [x] Run; expect all to FAIL initially.

### Task 4.3: Apply the two-stage retrofit (GREEN) [Medium]
**File:** `game/ui/screens/water_target_editor.py`
**Tests:** `pytest tests/unit/ui/screens/test_water_target_editor.py tests/unit/ui/screens/test_strategy_modal_window.py::TestStrategyOnlyWindowsRequireExplicitWindowManager -q`

- [x] Rewrite `__init__` to two-stage shape.
- [x] Move widget construction into `DefaultWaterTargetEditorUiBuilder`.
- [x] Run characterization tests; all GREEN.
- [x] Run parametrized window-manager test; no regression.

### Task 4.4: Verify + commit [Simple]

- [x] Run targeted tests; sharded suite green.
- [x] Update `findings/PROJ-458_findings.md` to mark F-C-017 (WaterTargetEditor row) `Status: resolved`.

---

## Phase Completion Checklist

When all 4 tasks are checked off:
- [x] F-C-017 (WaterTargetEditor) flipped to `Status: resolved` in `findings/PROJ-458_findings.md`.
- [x] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green.
- [x] Run `python Projects/scripts/validate_phase.py PROJ-458 4` — PASSED.
- [x] Update status at top of this file to `Complete`.
- [x] Update plan.md phase table row to `Complete`.
- [x] Update plan.md Current State to point to Phase 5.
- [x] Commit message: `PROJ-458 Phase 4: retrofit WaterTargetEditor to two-stage bypass-init + dedicated characterization tests`.
- [x] No new entries in `AgentCoordination/discovered_issues/log.jsonl` unless they are genuine out-of-scope discoveries.
