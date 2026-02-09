# Phase 1: Create DesignStatsPanel + Move StatRow

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-80 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create the shared `DesignStatsPanel` widget that encapsulates the two-column stats display, and move `StatRow` to the new module.

---

## Tasks

### Task 1.1: Move StatRow to new module [Simple]
**File:** `game/ui/panels/design_stats_panel.py` (new)
**Source:** `game/ui/screens/builder/right_panel.py` lines 15-56
**Tests:** `pytest tests/unit/ui/test_stats_render.py tests/integration/ui/test_build_queue_design_report.py`

- [ ] Create `game/ui/panels/design_stats_panel.py`
- [ ] Copy `StatRow` class from `game/ui/screens/builder/right_panel.py` (lines 15-56)
- [ ] Add necessary imports: `pygame`, `pygame_gui.elements.UILabel`
- [ ] Verify `StatRow` has `__init__`, `update`, `set_visible` methods
- [ ] Add module docstring explaining this is the shared stats widget

**Notes:**

### Task 1.2: Create DesignStatsPanel class [Medium]
**File:** `game/ui/panels/design_stats_panel.py`
**Tests:** `pytest tests/unit/ui/test_stats_render.py tests/integration/ui/test_build_queue_design_report.py`

- [ ] Add imports: `pygame_gui.elements` (UIPanel, UILabel, UITextBox, UIScrollingContainer), `stats_config` (STATS_CONFIG, get_logistics_rows, get_construction_rows), `LayerType` from `game.core.constants`
- [ ] Create `DesignStatsPanel.__init__(self, manager, rect, container, ship=None, show_requirements=False)`:
  - Store `self.manager`, `self.rect`, `self.container`, `self.show_requirements`
  - Initialize `self.rows_map = {}`, `self.current_logistics_keys = set()`, `self.layer_rows = []`
  - Initialize `self.req_box_left = None`, `self.req_box_right = None`
  - Initialize `self.stats_scroll = None`
  - If `ship` provided, call `self._build_layout(ship)`
- [ ] Implement `_build_layout(self, ship)`:
  - Kill existing `self.stats_scroll` if present
  - Create `UIScrollingContainer` at `self.rect` position within `self.container`
  - Call `self._build_sections(ship)`
- [ ] Implement `_build_sections(self, ship)` - extract from `BuilderRightPanel.setup_stats()` (lines 397-496):
  - Calculate two-column layout: `col_gap=10, margin=10, avail_w = full_w - 2*margin - col_gap, col_w = avail_w // 2`
  - Column 1 (col1_x = margin): Main Systems, Maneuvering, Shields, Armor, Layers (dynamic 4 slots), Targeting
  - Column 2 (col2_x = margin + col_w + col_gap): Logistics (via `get_logistics_rows(ship)`), Crew Logistics, Fighter Support, Build Cost (via `get_construction_rows(ship)`)
  - Store `self.current_logistics_keys = set(r.key for r in log_rows)`
  - If `show_requirements`: add Requirements + Recommendations UITextBox below both columns (same as `right_panel.py` lines 479-496)
  - Set scrollable area dimensions
- [ ] Extract `_build_section(self, title, stats_list, x, start_y, col_w)` helper:
  - Create section header UILabel: `f"── {title} ──"`
  - Create `StatRow` for each `stat_def`, attach `definition` attribute
  - Return updated y position
- [ ] Implement `update_stats(self, ship)` - extract from `BuilderRightPanel.update_stats_display()` (lines 558-639):
  - Iterate `rows_map`, get value from `stat_def`, format, update row
  - Update layer rows (hide all, then show populated ones)
  - If `show_requirements`: update requirements text box (missing reqs + mass limits)
  - If `show_requirements`: update recommendations text box (validation warnings)
- [ ] Implement `needs_rebuild(self, ship)` - extract dirty-check from `BuilderRightPanel.on_ship_updated()` (lines 96-128):
  - Get new logistics rows via `get_logistics_rows(ship)`
  - Compare keys to `self.current_logistics_keys`
  - Return `True` if mismatch
- [ ] Implement `rebuild(self, ship)`:
  - Call `_build_layout(ship)`
- [ ] Implement `kill(self)`:
  - Kill `self.stats_scroll` if present
  - Clear `self.rows_map`

**Notes:**

### Task 1.3: Verify DesignStatsPanel works standalone [Simple]
**Tests:** `pytest tests/unit/ui/test_stats_render.py tests/integration/ui/test_build_queue_design_report.py`

- [ ] Run targeted tests to verify no import errors
- [ ] Run `pytest tests/ --testmon` to check for regressions
- [ ] Verify `StatRow` is importable from `game.ui.panels.design_stats_panel`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `DesignStatsPanel` class exists in `game/ui/panels/design_stats_panel.py`
- [ ] `StatRow` class exists in `game/ui/panels/design_stats_panel.py`
- [ ] All existing tests still pass (no code consumers changed yet)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
