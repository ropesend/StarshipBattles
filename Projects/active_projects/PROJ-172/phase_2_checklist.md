# Phase 2: WeaponsPanel MVVM Extraction

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-172 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract WeaponsReportPanel (1,037 lines) into MVVM architecture: ViewModel owns weapon data + threshold calculations, Renderer owns all drawing. Panel becomes thin coordinator.

---

## Tasks

### Task 2.1: Create WeaponsViewModel [Medium]
**File:** `game/ui/screens/builder/weapons_panel.py` (read)
**New File:** `game/ui/screens/builder/weapons_viewmodel.py`
**Tests:** Write new tests in `tests/unit/ui/builder/test_weapons_viewmodel.py`

- [ ] Read `weapons_panel.py` fully, catalog all mutable state and calculation methods
- [ ] Identify state that should move to ViewModel:
  - [ ] Weapon grouping data
  - [ ] Threshold range calculations
  - [ ] Points of interest computation
  - [ ] Weapon name/icon caching
  - [ ] Tooltip hover state
- [ ] Create `game/ui/screens/builder/weapons_viewmodel.py` with:
  - [ ] `WeaponsViewModel` class following WorkshopViewModel pattern
  - [ ] `WeaponsEvents` class with event constants (WEAPONS_UPDATED, HOVER_CHANGED, etc.)
  - [ ] Use EventBus from `game/ui/screens/builder/event_bus.py`
  - [ ] Methods: `load_weapons(ship)`, `calculate_thresholds()`, `get_points_of_interest()`, `group_weapons()`
  - [ ] Properties: `weapon_groups`, `threshold_ranges`, `points_of_interest`, `hovered_weapon`
  - [ ] NO Pygame imports — pure data + calculations
- [ ] Write tests in `tests/unit/ui/builder/test_weapons_viewmodel.py`:
  - [ ] Test weapon grouping with mock weapon data
  - [ ] Test threshold calculation correctness
  - [ ] Test POI computation
  - [ ] Test event emission on state changes
- [ ] Run new tests: `pytest tests/unit/ui/builder/test_weapons_viewmodel.py -v`

**Notes:**

---

### Task 2.2: Create WeaponsRenderer [Medium]
**File:** `game/ui/screens/builder/weapons_panel.py` (read)
**New File:** `game/ui/screens/builder/weapons_renderer.py`
**Tests:** `pytest tests/unit/ui/test_weapons_report_layout.py`

- [ ] Identify all `_draw_*` methods in WeaponsReportPanel
- [ ] Create `game/ui/screens/builder/weapons_renderer.py` with:
  - [ ] `WeaponsRenderer` class
  - [ ] Move methods: `_draw_unified_weapon_bar()`, `_draw_direction_indicator()`, `_draw_scale_markers()`, `_draw_tooltip()`
  - [ ] Renderer takes ViewModel data as input — NOT a reference to the panel
  - [ ] `draw(surface, viewmodel_data)` — pure function of data, no queries back
  - [ ] Move rendering constants (colors, font sizes, bar dimensions)
- [ ] Renderer should accept data structures from ViewModel, not the ViewModel itself:
  ```python
  def draw(self, surface, weapon_groups, threshold_ranges, points_of_interest, hover_info):
      # Pure rendering — no queries back to panel or ViewModel
  ```
- [ ] Run layout tests: `pytest tests/unit/ui/test_weapons_report_layout.py -v`
- [ ] Run bug repro tests: `pytest tests/repro_issues/test_bug_13_weapons_report.py -v`

**Notes:**

---

### Task 2.3: Refactor WeaponsReportPanel to coordinator [Medium]
**File:** `game/ui/screens/builder/weapons_panel.py`
**Tests:** `pytest tests/unit/ui/test_weapons_report_layout.py tests/repro_issues/test_bug_13_weapons_report.py`

- [ ] Refactor WeaponsReportPanel to use ViewModel + Renderer:
  - [ ] In `__init__`: create EventBus, WeaponsViewModel, WeaponsRenderer
  - [ ] Subscribe to ViewModel events for UI refresh
  - [ ] Remove all calculation methods (now in ViewModel)
  - [ ] Remove all draw methods (now in Renderer)
  - [ ] Keep: `update()` (delegates to ViewModel), `draw()` (delegates to Renderer), `handle_event()` (routes input)
- [ ] Verify panel API unchanged (constructor signature, draw/update/handle_event)
- [ ] Run all weapon tests: `pytest tests/unit/ui/test_weapons_report_layout.py tests/repro_issues/test_bug_13_weapons_report.py -v`
- [ ] Verify: WeaponsReportPanel < 300 lines

**Notes:**

---

### Task 2.4: Phase 2 verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify: 12,023+ tests pass, 0 failures
- [ ] Verify line counts:
  - [ ] `weapons_panel.py` < 300 lines
  - [ ] `weapons_viewmodel.py` exists, no Pygame imports
  - [ ] `weapons_renderer.py` exists
- [ ] Verify: WeaponsViewModel independently testable (new tests pass)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
