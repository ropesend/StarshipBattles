# PROJ-458 Phase 3: GravityTargetEditor (220 LOC)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-458 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** Phase 2 complete (PlanetTargetEditor base-class adjustments — if any — have landed; the per-subclass retrofit pattern is proven).
**Review Mode:** standard
**Objective:** Apply Pattern #33 two-stage `bypass_init` retrofit to `GravityTargetEditor` (220 LOC). Same recipe as Phase 2; smaller scope.

**Source-of-truth finding:** F-C-017 (GravityTargetEditor row) in [`findings/PROJ-458_findings.md`](findings/PROJ-458_findings.md).

**Existing structure (verified 2026-05-19):**
- Inherits from `PlanetTargetEditor` (`game/ui/screens/planet_target_editor_base.py`).
- 220 LOC; smaller than `AtmosphereTargetEditor` because gravity has fewer dimensions than atmosphere.

---

## Tasks

### Task 3.1: Read GravityTargetEditor + plan retrofit [Simple]
**File:** `game/ui/screens/gravity_target_editor.py` (read-only)
**Tests:** none yet.

- [x] Read `gravity_target_editor.py` end-to-end. Note the specific state fields, widget construction calls, callback signatures.
- [x] Identify what differs from `AtmosphereTargetEditor` Phase 2 (gravity slider value range, axis count, validation rules, species-ideal preset shape).

### Task 3.2: Write dedicated characterization tests (RED) [Medium]
**File:** `tests/unit/ui/screens/test_gravity_target_editor.py` (new)
**Tests:** `pytest tests/unit/ui/screens/test_gravity_target_editor.py -q`

- [x] Mirror the Phase 2 test classes (Construction / SliderInteraction / SpeciesIdealPreset / ApplyCallback / CloseCallback). Adjust assertions to the gravity-specific surface.
- [x] **Test class: TestConstruction** — bypass-init + production + window-manager-required.
- [x] **Test class: TestGravitySliderInteraction** — initial value from `planet.gravity_target`; slider→label updates.
- [x] **Test class: TestSpeciesIdealPreset** — set-to-ideal populates from `race_config.gravity_preference`.
- [x] **Test class: TestApplyCallback** — Apply emits `(planet_id, gravity_value)` (or whatever shape Gravity uses — verify by reading).
- [x] **Test class: TestCloseCallback** — Close calls `on_close_callback`.
- [x] Run; expect all to FAIL initially.

### Task 3.3: Apply the two-stage retrofit (GREEN) [Medium]
**File:** `game/ui/screens/gravity_target_editor.py`
**Tests:** `pytest tests/unit/ui/screens/test_gravity_target_editor.py tests/unit/ui/screens/test_strategy_modal_window.py::TestStrategyOnlyWindowsRequireExplicitWindowManager -q`

- [x] Rewrite `__init__` to the two-stage shape, same recipe as Phase 2.
- [x] Move widget construction into `DefaultGravityTargetEditorUiBuilder`.
- [x] Run characterization tests; all GREEN.
- [x] Run parametrized window-manager test; no regression.

### Task 3.4: Verify + commit [Simple]

- [x] Run targeted tests; sharded suite green.
- [x] Update `findings/PROJ-458_findings.md` to mark F-C-017 (GravityTargetEditor row) `Status: resolved`.

---

## Phase Completion Checklist

When all 4 tasks are checked off:
- [x] F-C-017 (GravityTargetEditor) flipped to `Status: resolved` in `findings/PROJ-458_findings.md`.
- [x] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green.
- [x] Run `python Projects/scripts/validate_phase.py PROJ-458 3` — PASSED.
- [x] Update status at top of this file to `Complete`.
- [x] Update plan.md phase table row to `Complete`.
- [x] Update plan.md Current State to point to Phase 4.
- [x] Commit message: `PROJ-458 Phase 3: retrofit GravityTargetEditor to two-stage bypass-init + dedicated characterization tests`.
- [x] No new entries in `AgentCoordination/discovered_issues/log.jsonl` unless they are genuine out-of-scope discoveries.
