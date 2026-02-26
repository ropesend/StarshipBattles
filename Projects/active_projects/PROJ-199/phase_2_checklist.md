# Phase 2: Lazy Init — Unnecessary Guards

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-199 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove 16 `hasattr(self, ...)` guards where the attribute is always initialized in `__init__`. Pure deletion — no new code.

---

## Tasks

### Task 2.0: FormationEditor — rotation_mode_btn & renumber_slider [MOVED FROM PHASE 1]
**File:** `game/ui/screens/formation_editor.py`
**Tests:** `pytest tests/unit/ui/screens/ -k formation --testmon`

- [ ] L778: Replace `if hasattr(self, 'rotation_mode_btn'):` with `if self.rotation_mode_btn:`
- [ ] L797: Replace `if hasattr(self, 'renumber_slider'):` with `if self.renumber_slider:`

**Notes:** Code review showed these are NOT true lazy inits — they're assigned unconditionally at L292 and L301 from toolbar builder. The hasattr checks are unnecessary guards.

### Task 2.1: PlanetReportPanel [Simple]
**File:** `game/ui/panels/planet_report_panel.py`
**Tests:** `pytest tests/unit/ui/panels/ --testmon`

- [ ] L448: Replace `if hasattr(self, 'resource_panel') and self.resource_panel:` with `if self.resource_panel:`
- [ ] L452: Replace `if hasattr(self, 'panel'):` with `if self.panel:`

**Notes:**

### Task 2.2: FleetReportWindow [Simple]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** `pytest tests/unit/ui/screens/ -k fleet --testmon`

- [ ] L158: Replace `if hasattr(self, 'ship_detail_panel') and self.ship_detail_panel.process_event(event):` with `if self.ship_detail_panel and self.ship_detail_panel.process_event(event):`
- [ ] L356: Replace `if hasattr(self, 'virtual_table') and self.virtual_table:` with `if self.virtual_table:`
- [ ] L360: Replace `if hasattr(self, 'ship_detail_panel') and self.ship_detail_panel:` with `if self.ship_detail_panel:`

**Notes:**

### Task 2.3: PlanetListWindow [Simple]
**File:** `game/ui/screens/planet_list_window.py`
**Tests:** `pytest tests/unit/ui/screens/ -k planet --testmon`

- [ ] L441: Replace `if hasattr(self, 'asset_resolver') and self.asset_resolver:` with `if self.asset_resolver:`
- [ ] L496: Replace `if hasattr(self, 'virtual_table'):` with `if self.virtual_table:`

**Notes:**

### Task 2.4: StrategyScreen [Simple]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/unit/ui/screens/ -k strategy --testmon`

- [ ] L338: Replace `self.session.player_empire if hasattr(self, 'session') else None` with `self.session.player_empire`
- [ ] L339: Replace `self.session if hasattr(self, 'session') else None` with `self.session`

**Notes:**

### Task 2.5: StrategyUI [Simple]
**File:** `game/ui/screens/strategy_ui.py`
**Tests:** `pytest tests/unit/ui/screens/ -k strategy --testmon`

- [ ] L212: Replace `if hasattr(self, 'system_tree'):` with `if self.system_tree:`
- [ ] L214: Replace `if hasattr(self, 'sector_tree'):` with `if self.sector_tree:`

**Notes:**

### Task 2.6: StrategyWindowManager [Simple]
**File:** `game/ui/screens/strategy_window_manager.py`
**Tests:** `pytest tests/unit/ui/screens/ -k strategy --testmon`

- [ ] L531: Replace `hasattr(self, "_pending_confirmation_dialog")` with `self._pending_confirmation_dialog is not None`

**Notes:**

### Task 2.7: TestLab Dialogs [Simple]
**File:** `game/ui/screens/test_lab/dialogs.py`
**Tests:** `pytest tests/unit/ui/screens/test_lab/ --testmon`

- [ ] L61: Replace `if hasattr(self, 'close_button') and self.close_button:` with `if self.close_button:`
- [ ] L194: Replace `if hasattr(self, 'confirm_button') and self.confirm_button:` with `if self.confirm_button:`
- [ ] L196: Replace `if hasattr(self, 'cancel_button') and self.cancel_button:` with `if self.cancel_button:`

**Notes:**

### Task 2.8: TransferDialog [Simple]
**File:** `game/ui/screens/transfer_dialog.py`
**Tests:** `pytest tests/unit/ui/screens/ --testmon`

- [ ] L158: Replace `if hasattr(self, 'lbl_debug'):` with direct call `self.lbl_debug.set_text(debug_msg)` (always initialized in `_setup_ui()`)

**Notes:**

### Task 2.9: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] All 12724 tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
