# Phase 4: UI-Screens

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-121 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the UI-Screens module (12 findings, 1 critical)
**Priority:** High

---

## Tasks

### Task 4.1: LEG-UI1-001 - Backward Compatibility Aliases in RacePo [Simple]
**File:** `game/ui/panels/race_portrait_gallery.py`
**Tests:** `pytest tests/unit/ui/test_race_portrait_gallery.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Tests used legacy aliases (portrait_buttons, portrait_scroll, portrait_preview_panel, on_portrait_selected). Updated tests to use BaseGallery API (asset_buttons, scroll_container, preview_panel, on_asset_selected). Removed legacy aliases from source.

### Task 4.2: LEG-UI1-002 - Legacy BuilderScreen (builder/main.py) P [Complex]
**File:** `game/ui/screens/builder/main.py`
**Tests:** `pytest tests/unit/builder/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** MAJOR - BuilderScreen was DEAD CODE (never instantiated). Deleted: builder/main.py, builder/state_manager.py, tests/unit/builder/test_builder_state_manager.py. Updated builder/__init__.py and tests/unit/_verify_builder_imports.py. DesignWorkshopScreen in workshop_screen.py is the active implementation.

### Task 4.3: LEG-UI1-003 - Legacy Tuple Format Support in Component [Medium]
**File:** `game/ui/screens/builder/detail_panel.py`
**Tests:** `pytest tests/unit/builder/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Analysis showed tuple format is the CURRENT standard (viewmodel emits tuples), ComponentRef was never adopted. REVERSED: Removed dead ComponentRef import/handling, kept tuple handling (active implementation). Also deleted dead ComponentRef class and its tests.

### Task 4.4: LEG-UI1-004 - Legacy API Comment in FleetReportWindow [Simple]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Review validation report

**Notes:** REJECTED in validation report - "no legacy API comments found... finding appears to be outdated or inaccurate." FALSE POSITIVE.

### Task 4.5: LEG-UI1-005 - Legacy Single-Selection Fields in Empire [Medium]
**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Review validation report

**Notes:** DOWNGRADED to MINOR in validation - "The class supports multi-select via self.selected_indices: set". Multi-select functionality already exists.

### Task 4.6: LEG-UI1-006 - Fallback Mode in BuildQueueController [Medium]
**File:** `game/ui/panels/build_queue_controller.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Review implementation

**Notes:** REVIEWED - Fallback mode is INTENTIONAL defensive coding. build_context is passed as constructor argument and fallback handles case when no explicit queue sources are set. This is not legacy - it's valid design pattern.

### Task 4.7: LEG-UI1-007 - Backward Compat Attribute Exposure in Ri [Simple]
**File:** `game/ui/screens/builder/right_panel.py`
**Tests:** `pytest tests/unit/builder/`

- [x] Investigate the issue at the specified location
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Misleading comment "backward compat" - actually exposes rows_map for tests and update methods. Updated comment to be accurate: "Expose rows_map for tests and update methods".

### Task 4.8: LEG-UI1-008 - Backward Compatibility in WorkshopEventR [Simple]
**File:** `game/ui/screens/workshop_event_router.py`
**Tests:** `pytest tests/unit/builder/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ALL callers use tuple format (component, layer_type). Removed dead backward compat paths from _handle_remove_group, _handle_remove_individual, _handle_add_component. Deleted dead backward compat tests. Updated other tests to use tuple format.

### Task 4.9: LEG-UI1-009 - Test Lab Screen Legacy Game Parameter [Medium]
**File:** `game/ui/screens/test_lab/screen.py`
**Tests:** `pytest tests/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** RESOLVED - Misleading comment "(for legacy compatibility)" was inaccurate. The game parameter is ACTIVELY USED (34 usages for screen, battle_scene, state). Updated docstring to accurate description.

### Task 4.10: LEG-UI1-010 - Compatibility Setter in BuilderStateMana [Simple]
**File:** `game/ui/screens/builder/state_manager.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Implement the fix

**Notes:** ALREADY RESOLVED - state_manager.py was deleted in Task 4.2 (part of dead BuilderScreen code).

### Task 4.11: LEG-UI1-011 - Deprecated Properties in StrategyScreen [Complex]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** RESOLVED - Properties are NOT deprecated (no external callers). They're internal convenience properties delegating to session. Updated misleading comment to accurate description: "delegate to session for internal convenience, external callers should use facade".

### Task 4.12: LEG-UI1-012 - Legacy Keys Filtering in stats_config.py [Simple]
**File:** `game/ui/screens/builder/stats_config.py`
**Tests:** `pytest tests/unit/builder/`

- [x] Investigate the issue at the specified location
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** STATS_LOGISTICS was empty (no "logistics" key in JSON). The legacy key filtering was dead code filtering an empty list. Removed the dead filtering code.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
