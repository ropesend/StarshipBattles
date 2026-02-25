# Phase 3: Workshop Init-Order & Self-Checks

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-194 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix init-order issues by declaring all instance attributes in __init__ before they are used. Eliminate hasattr(self, ...) and hasattr(gui, ...) defensive checks.

---

## Tasks

### Task 3.1: workshop_screen.py — Pre-declare button attributes [Medium]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** `pytest tests/ --testmon`

The `_get_button_definitions()` method (line 546) returns button names that are set via `setattr(self, attr_name, btn)` at line 286. This means mode-dependent buttons may not exist. Fix by pre-declaring all possible button attrs as `None` in `__init__` before `_create_ui()` is called.

- [ ] In `__init__` (after line 123, before `self._create_ui()` at line 128), add declarations:
  ```python
  # Pre-declare all button attributes (mode-dependent buttons may not be created)
  self.clear_btn: Optional[UIButton] = None
  self.save_btn: Optional[UIButton] = None
  self.load_btn: Optional[UIButton] = None
  self.arc_toggle_btn: Optional[UIButton] = None
  self.target_btn: Optional[UIButton] = None
  self.hull_toggle_btn: Optional[UIButton] = None
  self.std_data_btn: Optional[UIButton] = None
  self.test_data_btn: Optional[UIButton] = None
  self.select_data_btn: Optional[UIButton] = None
  self.verbose_btn: Optional[UIButton] = None
  self.obsolete_btn: Optional[UIButton] = None
  self.start_btn: Optional[UIButton] = None
  self.pending_action = None
  ```
- [ ] Add `Optional` import if not already present
- [ ] Verify: Run tests

**Notes:** The `setattr` at line 286 will still overwrite these defaults for buttons that are created. This just ensures the attrs exist even for mode-dependent buttons not created.

---

### Task 3.2: workshop_event_router.py — Button hasattr removal [Simple]
**File:** `game/ui/screens/workshop_event_router.py`
**Tests:** `pytest tests/ --testmon`

After Task 3.1, all button attrs are always present (None when not created). Replace hasattr checks with None checks:
- [ ] Line 307: `hasattr(gui, 'hull_toggle_btn') and event.ui_element == gui.hull_toggle_btn` → `gui.hull_toggle_btn is not None and event.ui_element == gui.hull_toggle_btn`
- [ ] Line 313: `hasattr(gui, 'std_data_btn') and ...` → `gui.std_data_btn is not None and ...`
- [ ] Line 315: `hasattr(gui, 'test_data_btn') and ...` → `gui.test_data_btn is not None and ...`
- [ ] Line 317: `hasattr(gui, 'select_data_btn') and ...` → `gui.select_data_btn is not None and ...`
- [ ] Line 319: `hasattr(gui, 'verbose_btn') and ...` → `gui.verbose_btn is not None and ...`
- [ ] Verify: Run tests

**Notes:**

---

### Task 3.3: workshop_event_router.py — Panel hasattr removal [Simple]
**File:** `game/ui/screens/workshop_event_router.py`
**Tests:** `pytest tests/ --testmon`

These panels are always created in `_create_ui()`:
- [ ] Line 76: `if hasattr(gui, 'component_modifier_grid_panel'):` → remove check (always created at workshop_screen.py line 253)
- [ ] Line 334: `hasattr(gui, 'right_panel')` → remove check (always created at line 200)
- [ ] Line 334: `hasattr(gui.right_panel, 'vehicle_type_dropdown')` → keep or remove based on whether vehicle_type_dropdown is always created in right_panel.__init__
- [ ] Line 336: `hasattr(gui.right_panel, 'theme_dropdown')` → keep or remove (check if always created)
- [ ] Verify: Run tests

**Notes:** Verify right_panel dropdowns are always created before removing those hasattr checks.

---

### Task 3.4: workshop_screen.py — Self-attribute hasattr removal [Simple]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** `pytest tests/ --testmon`

After Task 3.1 (pending_action pre-declared):
- [ ] Line 399: `if hasattr(self, 'pending_action') and self.pending_action:` → `if self.pending_action:`
- [ ] Line 439: `if hasattr(self.modifier_panel, 'update'):` → remove check (ModifierEditorPanel always has update method)
- [ ] Line 483: `if not hovered and hasattr(self, 'weapons_report_panel'):` → `if not hovered:` (weapons_report_panel always created in _create_ui at line 240)
- [ ] Line 597: `if hasattr(self, 'weapons_report_panel'):` → remove check (always exists)
- [ ] Line 612: `if hasattr(self, 'ui_manager') and self.ui_manager:` → `if self.ui_manager:` (always set in __init__)
- [ ] Verify: Run tests

**Notes:**

---

### Task 3.5: right_panel.py — Self-attribute hasattr removal [Simple]
**File:** `game/ui/screens/builder/right_panel.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Line 56: `if hasattr(self, 'stats_panel') and self.stats_panel.needs_rebuild(ship):` → ensure stats_panel is declared in __init__, then remove hasattr
- [ ] Line 332: `if hasattr(self, 'stats_panel'):` → remove check (ensure declared in __init__)
- [ ] Verify: Run tests

**Notes:** Check right_panel.__init__ — if stats_panel is created inside a method called from __init__, it may need to be pre-declared as None.

---

### Task 3.6: design_report_panel.py — Self-attribute hasattr removal [Simple]
**File:** `game/ui/panels/design_report_panel.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Line 102: `if hasattr(self, 'name_label'):` → ensure name_label is declared in __init__, remove hasattr
- [ ] Line 104: `if hasattr(self, 'type_class_label'):` → ensure type_class_label is declared in __init__, remove hasattr
- [ ] Line 287: `if hasattr(self, 'panel'):` → ensure panel is declared in __init__, remove hasattr
- [ ] Verify: Run tests

**Notes:** These are likely created in a `_build_ui()` method. Pre-declare as None in __init__.

---

### Task 3.7: modifier_impact_grid.py — Self-attribute hasattr removal [Simple]
**File:** `game/ui/panels/modifier_impact_grid.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Line 438: `if hasattr(self, '_stat_summary'):` → ensure _stat_summary is declared in __init__ (as None), remove hasattr
- [ ] Verify: Run tests

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
