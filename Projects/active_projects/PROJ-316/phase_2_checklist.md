# Phase 2: Tighten `window_manager` to required on strategy-screen-only windows

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-316 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Restore the structural guarantee — make forgotten
registration impossible at strategy-screen spawn sites by removing the
`= None` default on the 13 windows that are only opened from the
strategy screen. Closes audit finding P2.4 (bypass risk).

---

## Tasks

### Task 2.1: Inventory call sites [Simple]
**Goal:** confirm each of the 13 candidate windows is opened ONLY from
strategy-screen contexts.
**Tests:** Grep verification.

- [x] For each of these 14 windows, grep the codebase (excluding test files and the class definition) for constructor calls:
      - `PlanetListWindow`
      - `StarListWindow`
      - `BuildQueueListWindow`
      - `EmpireBuildQueueWindow`
      - `EventLogWindow`
      - `EmpirePanelWindow`
      - `FleetReportWindow`
      - `PlanetAbilitiesWindow`
      - `MoveChoiceWindow`
      - `FoodAllocationEditor`
      - `AtmosphereTargetEditor`
      - `GravityTargetEditor`
      - `WaterTargetEditor`
      - `RadiationShieldEditor`
      - `PlanetSelectionWindow` (control case — known dual-caller)
- [x] Categorise each as STRATEGY-ONLY or DUAL-CALLER. Per PROJ-313 implementation, only `PlanetSelectionWindow` is dual-caller (also opened from `BuildQueueScreen` at `game/ui/screens/build_queue_screen.py:623`).
- [x] Document the inventory in `decisions.md` for future reference.

**Notes:**

---

### Task 2.2: Tighten the base class signature [Simple]
**File:** `game/ui/screens/strategy_modal_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_modal_window.py`

- [x] Locate `StrategyModalWindow.__init__` signature.
- [x] Change `window_manager: "StrategyWindowManager | None" = None` → `window_manager: "StrategyWindowManager | None"` (keyword-only, no default). Type stays `Optional` so `PlanetSelectionWindow` can still pass `None` from `BuildQueueScreen`.
- [x] Update the docstring to say "Pass `None` only when the window is being opened outside the strategy screen (e.g., from `BuildQueueScreen`)".
- [x] Run the test. All existing tests should still pass since they pass `window_manager=` explicitly.

**Notes:**

---

### Task 2.3: Tighten each of the 13 strategy-screen-only windows [Medium]
**Files:** the 13 window class files identified in Task 2.1.
**Tests:** `pytest tests/unit/ui/screens/ tests/integration/ui/`

For each of the 13 windows:

- [x] `PlanetListWindow` ([game/ui/screens/planet_list_window.py](../../game/ui/screens/planet_list_window.py)) — remove `= None` default.
- [x] `StarListWindow` ([game/ui/screens/star_list_window.py](../../game/ui/screens/star_list_window.py)) — remove `= None` default.
- [x] `BuildQueueListWindow` ([game/ui/screens/build_queue_list_window.py](../../game/ui/screens/build_queue_list_window.py)) — remove `= None` default.
- [x] `EmpireBuildQueueWindow` ([game/ui/screens/empire_build_queue_window.py](../../game/ui/screens/empire_build_queue_window.py)) — remove `= None` default.
- [x] `EventLogWindow` ([game/ui/screens/event_log_window.py](../../game/ui/screens/event_log_window.py)) — remove `= None` default.
- [x] `EmpirePanelWindow` ([game/ui/screens/empire_panel_window.py](../../game/ui/screens/empire_panel_window.py)) — remove `= None` default.
- [x] `FleetReportWindow` ([game/ui/screens/fleet_report_window.py](../../game/ui/screens/fleet_report_window.py)) — remove `= None` default.
- [x] `PlanetAbilitiesWindow` ([game/ui/screens/planet_abilities_window.py](../../game/ui/screens/planet_abilities_window.py)) — remove `= None` default.
- [x] `MoveChoiceWindow` ([game/ui/screens/strategy_windows/move_choice_dialog.py](../../game/ui/screens/strategy_windows/move_choice_dialog.py)) — remove `= None` default.
- [x] `FoodAllocationEditor` ([game/ui/screens/food_allocation_editor.py](../../game/ui/screens/food_allocation_editor.py)) — remove `= None` default.
- [x] `AtmosphereTargetEditor` ([game/ui/screens/atmosphere_target_editor.py](../../game/ui/screens/atmosphere_target_editor.py)) — remove `= None` default.
- [x] `GravityTargetEditor` ([game/ui/screens/gravity_target_editor.py](../../game/ui/screens/gravity_target_editor.py)) — remove `= None` default.
- [x] `WaterTargetEditor` ([game/ui/screens/water_target_editor.py](../../game/ui/screens/water_target_editor.py)) — remove `= None` default.
- [x] `RadiationShieldEditor` ([game/ui/screens/radiation_shield_editor.py](../../game/ui/screens/radiation_shield_editor.py)) — remove `= None` default.

For each, also:
- [x] Verify spawn site already passes `window_manager=` (per PROJ-313 it does). Audit if not.
- [x] Run `pytest tests/unit/ui/screens/` after each change. Find tests that constructed the window without `window_manager=` and add either `window_manager=None` (acceptable in test contexts where modal-tracking is not under test) or a real `Mock()` fixture.

**Notes:** When the type stays `Optional` but the default is removed, callers MUST pass `window_manager=` (with either a real manager or `None` explicitly). This makes "I forgot it" impossible.

**Implementation note:** Strategy-screen-only windows use `"StrategyWindowManager"` where they define their own constructor. `MoveChoiceWindow` inherits the required base constructor. Cross-screen `PlanetSelectionWindow` remains explicit at both callers, including `window_manager=None` from `BuildQueueScreen`.

---

### Task 2.4: Update `docs/06_UI_STYLE_GUIDE.md` Window Management section [Simple]
**File:** `docs/06_UI_STYLE_GUIDE.md`
**Tests:** Manual re-read.

- [x] Update the example code template under "Window Management" to show the strategy-screen-only adopter pattern: `window_manager: "StrategyWindowManager"` (required, no default). Add a separate "Cross-screen reuse" subsection covering `Optional[...]` + explicit `None` for windows like `PlanetSelectionWindow`.
- [x] Bump `Last verified:` blockquote.

**Notes:**

**Verification:** Signature probe confirmed all 14 strategy-only windows have no default for `window_manager`; `pytest tests/unit/ui/ tests/integration/ui/ -q` passed with 3883 passed, 1 skipped.

---

### Task 2.5: Verification [Simple]
**Tests:** Manual REPL test + sharded UI tests.

- [x] Construct each of the 13 windows in a Python REPL without `window_manager=`. Confirm `TypeError: missing required keyword-only argument` is raised.
- [x] `pytest tests/unit/ui/ tests/integration/ui/` clean.
- [x] `python Tools/test_sharded/test_sharded.py` — only PROJ-315 failures remain (the 8 from `test_ship_instance_damage.py` recorded at PROJ-316 kick-off).

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All 14 windows audited; 13 categorised as STRATEGY-ONLY and tightened
- [x] `pytest tests/unit/ui/ tests/integration/ui/` no regression
- [x] Manual REPL verification confirms TypeError on missing `window_manager=`
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
