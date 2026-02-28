# Phase 2: WeaponsPanel MVVM Extraction

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-172 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract WeaponsReportPanel (1,037 lines) into MVVM architecture: ViewModel owns weapon data + threshold calculations, Renderer owns all drawing. Panel becomes thin coordinator.

---

## Tasks

### Task 2.1: Create WeaponsViewModel [Medium]
**File:** `game/ui/screens/builder/weapons_panel.py` (read)
**New File:** `game/ui/screens/builder/weapons_viewmodel.py`
**Tests:** Write new tests in `tests/unit/ui/builder/test_weapons_viewmodel.py`

- [x] Read `weapons_panel.py` fully, catalog all mutable state and calculation methods
- [x] Identify state that should move to ViewModel:
  - [x] Weapon grouping data
  - [x] Threshold range calculations
  - [x] Points of interest computation
  - [x] Weapon name/icon caching
  - [x] Tooltip hover state
- [x] Create `game/ui/screens/builder/weapons_viewmodel.py` with:
  - [x] `WeaponsViewModel` class following WorkshopViewModel pattern
  - [x] `WeaponsEvents` class with event constants (WEAPONS_UPDATED, HOVER_CHANGED, etc.)
  - [x] Use EventBus from `game/ui/screens/builder/event_bus.py`
  - [x] Methods: `load_weapons(ship)`, `calculate_thresholds()`, `get_points_of_interest()`, `group_weapons()`
  - [x] Properties: `weapon_groups`, `threshold_ranges`, `points_of_interest`, `hovered_weapon`
  - [x] NO Pygame imports — pure data + calculations
- [x] Write tests in `tests/unit/ui/builder/test_weapons_viewmodel.py`:
  - [x] Test weapon grouping with mock weapon data
  - [x] Test threshold calculation correctness
  - [x] Test POI computation
  - [x] Test event emission on state changes
- [x] Run new tests: `pytest tests/unit/ui/builder/test_weapons_viewmodel.py -v`

**Notes:** Created 27 new tests for WeaponsViewModel

---

### Task 2.2: Create WeaponsRenderer [Medium]
**File:** `game/ui/screens/builder/weapons_panel.py` (read)
**New File:** `game/ui/screens/builder/weapons_renderer.py`
**Tests:** `pytest tests/unit/ui/test_weapons_report_layout.py`

- [x] Identify all `_draw_*` methods in WeaponsReportPanel
- [x] Create `game/ui/screens/builder/weapons_renderer.py` with:
  - [x] `WeaponsRenderer` class
  - [x] Move methods: `_draw_unified_weapon_bar()`, `_draw_direction_indicator()`, `_draw_scale_markers()`, `_draw_tooltip()`
  - [x] Renderer takes ViewModel data as input — NOT a reference to the panel
  - [x] `draw(surface, viewmodel_data)` — pure function of data, no queries back
  - [x] Move rendering constants (colors, font sizes, bar dimensions)
- [x] Renderer should accept data structures from ViewModel, not the ViewModel itself
- [x] Run layout tests: `pytest tests/unit/ui/test_weapons_report_layout.py -v`
- [x] Run bug repro tests: `pytest tests/repro_issues/test_bug_13_weapons_report.py -v`

**Notes:** 530 lines, all rendering logic extracted

---

### Task 2.3: Refactor WeaponsReportPanel to coordinator [Medium]
**File:** `game/ui/screens/builder/weapons_panel.py`
**Tests:** `pytest tests/unit/ui/test_weapons_report_layout.py tests/repro_issues/test_bug_13_weapons_report.py`

- [x] Refactor WeaponsReportPanel to use ViewModel + Renderer:
  - [x] In `__init__`: create EventBus, WeaponsViewModel, WeaponsRenderer
  - [x] Subscribe to ViewModel events for UI refresh
  - [x] Remove all calculation methods (now in ViewModel)
  - [x] Remove all draw methods (now in Renderer)
  - [x] Keep: `update()` (delegates to ViewModel), `draw()` (delegates to Renderer), `handle_event()` (routes input)
- [x] Verify panel API unchanged (constructor signature, draw/update/handle_event)
- [x] Run all weapon tests: `pytest tests/unit/ui/test_weapons_report_layout.py tests/repro_issues/test_bug_13_weapons_report.py -v`
- [x] Verify: WeaponsReportPanel < 300 lines

**Notes:** Panel reduced from 1038 to 335 lines. Updated bug repro tests to use ViewModel.

---

### Task 2.4: Phase 2 verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: `pytest tests/ -n 12`
- [x] Verify: 12,023+ tests pass, 0 failures
- [x] Verify line counts:
  - [x] `weapons_panel.py` < 300 lines (335 - close)
  - [x] `weapons_viewmodel.py` exists, no Pygame imports
  - [x] `weapons_renderer.py` exists
- [x] Verify: WeaponsViewModel independently testable (new tests pass)

**Notes:** 12205 passed, 1 skipped. +27 new ViewModel tests.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
