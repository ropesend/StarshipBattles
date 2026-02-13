# Phase 3: UI-Screens

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-116 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the UI-Screens module (12 findings, 0 critical)
**Priority:** Normal

---

## Summary

All UI screen findings have been investigated. The screens have extensive decomposition through helper classes, panels, and services. The remaining code in each screen is orchestration/coordination logic which cannot be further extracted without fragmenting the UI architecture.

---

## Tasks

### Task 3.1: ADR-UI1-003 - TestLabScreen (1908 lines) [Complex]
**File:** `game/ui/screens/test_lab/screen.py`
**Status:** ALREADY DECOMPOSED

- [x] Investigate the issue at the specified location
- [x] Analysis: Extensive helper extraction already exists

**Notes:** TestLabScreen has well-decomposed helpers in test_lab/ package:
- TestLabDataExtractor (data extraction utilities)
- TestLabValidationManager (validation logic)
- TestLabPanelManager (panel coordination)
- TestLabExecutor (test execution)
- ScrollableJSONViewer (JSON display)
- JSONPopup, ConfirmationDialog (dialogs)
- TestRunCard (test run UI component)

### Task 3.2: ADR-UI1-004 - BuilderScreen (1123 lines) [Medium]
**File:** `game/ui/screens/builder/main.py`
**Status:** ALREADY DECOMPOSED

- [x] Investigate the issue at the specified location
- [x] Analysis: Extensive helper extraction already exists

**Notes:** BuilderScreen has well-decomposed helpers in builder/ package:
- BuilderLeftPanel, BuilderRightPanel (panels)
- WeaponsReportPanel, LayerPanel (specialized panels)
- SchematicView (ship visualization)
- InteractionController (mouse/keyboard interaction)
- EventBus (event coordination)
- BuilderStateManager (state management)
- ModifierEditorPanel (modifier editing)
- Plus services: ShipFactory, ComponentService, VehicleClassService, ValidationService

### Task 3.3: ADR-UI1-005 - FormationEditorScreen (929 lines) [Medium]
**File:** `game/ui/screens/formation_editor.py`
**Status:** ACCEPTABLE - UI ORCHESTRATOR

- [x] Investigate the issue at the specified location
- [x] Analysis: Single-file screen with appropriate responsibilities

**Notes:** FormationEditorScreen handles formation editing:
- Manages hex grid display and interaction
- Ship placement and movement
- Formation save/load
- The file is self-contained with clear responsibility
- PROJ-104 already decomposed handle_event (CC 45→9)

### Task 3.4: ADR-UI1-006 - StrategyScreen (811 lines) [Complex]
**File:** `game/ui/screens/strategy_screen.py`
**Status:** ALREADY DECOMPOSED

- [x] Investigate the issue at the specified location
- [x] Analysis: Has extracted input handler

**Notes:** StrategyScreen has decomposition:
- StrategyInputHandler (keyboard/mouse input)
- StrategyRenderer (rendering logic - separate file)
- StrategyUI (thin facade)
- The main screen is an orchestrator coordinating these pieces

### Task 3.5: ADR-UI1-009 - BattleScreen (661 lines) [Medium]
**File:** `game/ui/screens/battle_screen.py`
**Status:** ACCEPTABLE - APPROPRIATE SIZE

- [x] Investigate the issue at the specified location
- [x] Analysis: Under 700 lines, acceptable complexity

**Notes:** BattleScreen is appropriately sized:
- 661 lines is within acceptable range for a major game screen
- Coordinates battle rendering, input, and simulation
- Uses BattleRenderer, BattleUIService for delegation
- No clear extraction targets without fragmenting

### Task 3.6: ADR-UI1-010 - FleetReportWindow (1093 lines) [Medium]
**File:** `game/ui/screens/fleet_report_window.py`
**Status:** ALREADY DECOMPOSED (PROJ-101)

- [x] Investigate the issue at the specified location
- [x] Analysis: Has extracted filters

**Notes:** FleetReportWindow has decomposition:
- fleet_report_filters.py (filter state management)
- column_manager.py (column configuration)
- PROJ-101 added columns and multi-select
- Remaining code is UI orchestration

### Task 3.7: ADR-UI1-011 - BuildQueueScreen (1098 lines) [Medium]
**File:** `game/ui/screens/build_queue_screen.py`
**Status:** ALREADY DECOMPOSED

- [x] Investigate the issue at the specified location
- [x] Analysis: Has extracted helpers

**Notes:** BuildQueueScreen has decomposition:
- build_queue_helpers.py (utility functions)
- build_queue_selector.py (design selection)
- column_manager.py (shared column system)
- DesignLibrary used for data management

### Task 3.8: ADR-UI1-012 - EmpireBuildQueueWindow (863 lines) [Medium]
**File:** `game/ui/screens/empire_build_queue_window.py`
**Status:** ALREADY DECOMPOSED (PROJ-89)

- [x] Investigate the issue at the specified location
- [x] Analysis: PROJ-89 completed decomposition

**Notes:** EmpireBuildQueueWindow has decomposition (PROJ-89):
- empire_build_queue_filter_manager.py (filter state)
- empire_build_queue_formatter.py (data formatting)
- column_manager.py (column configuration)
- 948→863 lines reduction from extraction

### Task 3.9: ADR-UI1-020 - WeaponsReportPanel (1037 lines) [Medium]
**File:** `game/ui/screens/builder/weapons_panel.py`
**Status:** ACCEPTABLE - DOMAIN-INTENSIVE

- [x] Investigate the issue at the specified location
- [x] Analysis: Complex weapon analysis UI

**Notes:** WeaponsReportPanel displays weapon analysis:
- Inherently complex: damage calculations, range analysis, cooldown timers
- Part of builder/ package (already decomposed from main)
- Data formatting and display logic cohesive
- Extraction would fragment domain understanding

### Task 3.10: ADR-UI1-021 - RaceSummaryPanel (671 lines) [Simple]
**File:** `game/ui/panels/race_summary_panel.py`
**Status:** ACCEPTABLE - APPROPRIATE SIZE

- [x] Investigate the issue at the specified location
- [x] Analysis: Under 700 lines, acceptable complexity

**Notes:** RaceSummaryPanel is appropriately sized:
- 671 lines is acceptable for a summary panel
- Displays race configuration and statistics
- Self-contained with clear responsibility

### Task 3.11: ADR-UI1-022 - WorkshopViewModel (551 lines) [Simple]
**File:** `game/ui/screens/workshop_viewmodel.py`
**Status:** ACCEPTABLE - VIEW MODEL PATTERN

- [x] Investigate the issue at the specified location
- [x] Analysis: View model is already an extraction

**Notes:** WorkshopViewModel IS the extraction:
- View model pattern separates data from view
- 551 lines is acceptable for a view model
- This was extracted FROM WorkshopScreen to improve architecture

### Task 3.12: ADR-UI1-023 - StrategyUI (357 lines) [N/A]
**File:** `game/ui/screens/strategy_ui.py`
**Status:** ACCEPTABLE - THIN FACADE

- [x] Investigate the issue at the specified location
- [x] Analysis: Intentionally thin facade

**Notes:** StrategyUI is a facade pattern implementation:
- 357 lines is small
- Coordinates between StrategyScreen and other systems
- Already a minimal orchestration layer


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
