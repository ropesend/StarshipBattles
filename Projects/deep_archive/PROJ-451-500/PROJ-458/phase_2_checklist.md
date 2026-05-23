# PROJ-458 Phase 2: AtmosphereTargetEditor (273 LOC, largest of the 4 planet-target editors)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-458 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** Phase 1 complete (SettingsWindow retrofit + characterization tests; established the recipe).
**Review Mode:** standard
**Objective:** Apply Pattern #33 two-stage `bypass_init` retrofit to `AtmosphereTargetEditor` (273 LOC). This is the largest of the 4 `PlanetTargetEditor` subclasses; tackling it first lets the executing agent discover the shared base-class retrofit pattern (if needed) so Phases 3-5 share a proven approach.

**Source-of-truth finding:** F-C-017 (AtmosphereTargetEditor row) in [`findings/PROJ-458_findings.md`](findings/PROJ-458_findings.md).

**Pattern reference:** `docs/02_PATTERNS.md` §33.

**Existing structure (verified 2026-05-19):**
- Inherits from `PlanetTargetEditor` (`game/ui/screens/planet_target_editor_base.py`).
- Constructor: `__init__(self, rect, manager, planet, *, window_manager, on_apply_callback=None, on_close_callback=None, race_config=None)`.
- Calls `super().__init__(rect, manager, window_display_title=f"Atmosphere Target: {planet.name}", resizable=True, window_manager=window_manager)` at lines 74-79.
- Builds 10-gas slider grid (`ALL_GASES` constant at line 26 lists `N2`, `O2`, `CO2`, `H2O`, `CH4`, `H2`, `He`, `Ar`, `NH3`, `SO2`) — each gas has slider + label + spin = ~30 widgets total.
- Species-ideal preset wiring imports `build_species_selector` from `game.ui.screens.species_selector_mixin`.

---

## Tasks

### Task 2.1: Read PlanetTargetEditor base class [Medium]
**File:** `game/ui/screens/planet_target_editor_base.py` (read-only)
**Tests:** none — read-only.

- [x] Read the `PlanetTargetEditor` base class end-to-end. Note its `__init__` signature, what state it owns, what `super().__init__` it calls (probably to `StrategyModalWindow`).
- [x] **Decision point**: does the base class need to participate in the two-stage retrofit (i.e. does it have heavy widget construction that should also be behind a bypass guard), or can the subclass do all the bypass-init work?
  - **If the base only sets pure-Python state**, subclass-only retrofit is sufficient — the base's `super().__init__(...)` ladder reaches `StrategyModalWindow.__init__`, which itself already has a bypass guard (verified 2026-05-19).
  - **If the base does heavy widget construction**, the base also needs a two-stage shape — every subclass benefits.
- [x] Record the decision in `decisions.md` with a rationale paragraph.

### Task 2.2: Write dedicated characterization tests (RED) [Medium]
**File:** `tests/unit/ui/screens/test_atmosphere_target_editor.py` (new)
**Tests:** `pytest tests/unit/ui/screens/test_atmosphere_target_editor.py -q`

- [x] Create the test file. Mirror Phase 1's test_settings_window.py + the planet-target-editor incidental coverage at `test_strategy_modal_window.py:367-398`.
- [x] **Test class: TestConstruction**
  - `test_bypass_init_yields_instance_without_widgets`: with `bypass_init(AtmosphereTargetEditor)`, instance has `_planet`, `_race_config`, etc. set but widgets absent.
  - `test_production_init_constructs_gas_grid`: full construction creates the 10-gas slider grid.
  - `test_window_manager_required`: confirms the existing contract (matches `test_strategy_modal_window.py:367-398`).
- [x] **Test class: TestGasSliderInteraction**
  - `test_slider_initial_value_matches_planet_target`: each gas slider's initial value comes from `planet.atmosphere_target[gas]` (or 0.0 if absent).
  - `test_slider_update_updates_label`: moving a slider updates the matching numeric display.
- [x] **Test class: TestSpeciesIdealPreset**
  - `test_set_to_species_ideal_populates_targets_from_race_config`: clicking "Set to Species Ideal" populates the targets from `race_config.atmosphere_preference`.
  - `test_species_ideal_disabled_when_no_race_config`: when `race_config=None`, the button is disabled or not visible.
- [x] **Test class: TestApplyCallback**
  - `test_apply_emits_callback_with_planet_id_and_target_dict`: pressing Apply emits `on_apply_callback(planet.id, {gas: value, ...})`.
- [x] **Test class: TestCloseCallback**
  - `test_close_calls_on_close_callback`: pressing Close calls `on_close_callback()` and `kill()`.
- [x] Run; all should FAIL initially. Confirm.

### Task 2.3: Apply the two-stage retrofit (GREEN) [Medium]
**File:** `game/ui/screens/atmosphere_target_editor.py`
**Tests:** `pytest tests/unit/ui/screens/test_atmosphere_target_editor.py tests/unit/ui/screens/test_strategy_modal_window.py::TestWindowManagerSignature::test_strategy_only_windows_require_explicit_window_manager -q`

> **Codex r5 audit (2026-05-19):** Earlier drafts cited a non-existent class `TestStrategyOnlyWindowsRequireExplicitWindowManager`. The actual target is the method `test_strategy_only_windows_require_explicit_window_manager` inside class `TestWindowManagerSignature` at `tests/unit/ui/screens/test_strategy_modal_window.py:291, 397-400`.

- [x] Rewrite `AtmosphereTargetEditor.__init__` to the two-stage shape. Stage 1: store `planet`, `race_config`, `on_apply_callback`, `on_close_callback`, `_ui_builder = ui_builder or DefaultAtmosphereTargetEditorUiBuilder()`. Bypass guard. Stage 2: `super().__init__(...)` + `self._ui_builder.build(self)`.
- [x] Move all widget-construction code (the gas slider grid, the species selector, the Apply/Reset buttons) into the new builder class.
- [x] If Task 2.1 decided the base class needs adjustment, edit `planet_target_editor_base.py` accordingly.
- [x] Run new characterization tests; all GREEN.
- [x] Run the parametrized window-manager test at `test_strategy_modal_window.py:367-398`; confirm no regression.

### Task 2.4: Verify + commit [Simple]

- [x] Run targeted tests: `pytest tests/unit/ui/screens/test_atmosphere_target_editor.py tests/unit/ui/screens/test_strategy_modal_window.py -q`. Green.
- [x] Run sharded suite: `python Tools/test_sharded/test_sharded.py`. Green.
- [x] (PowerShell-safe) `(Get-Content game/ui/screens/atmosphere_target_editor.py | Measure-Object -Line).Lines` — note new LOC.
- [x] Update `findings/PROJ-458_findings.md` to mark F-C-017 (AtmosphereTargetEditor row) `Status: resolved`.

---

## Phase Completion Checklist

When all 4 tasks are checked off:
- [x] F-C-017 (AtmosphereTargetEditor) flipped to `Status: resolved` in `findings/PROJ-458_findings.md`.
- [x] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green.
- [x] Run `python Projects/scripts/validate_phase.py PROJ-458 2` — PASSED.
- [x] Update status at top of this file to `Complete`.
- [x] Update plan.md phase table row to `Complete`.
- [x] Update plan.md Current State to point to Phase 3.
- [x] Commit message: `PROJ-458 Phase 2: retrofit AtmosphereTargetEditor to two-stage bypass-init + dedicated characterization tests`.
- [x] If `planet_target_editor_base.py` was modified, commit message also mentions the base-class adjustment.
- [x] No new entries in `AgentCoordination/discovered_issues/log.jsonl` unless they are genuine out-of-scope discoveries.
