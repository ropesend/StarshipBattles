# Phase 1: Lazy Init — True Missing Inits

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-199 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add `__init__` declarations for 9 attributes that are currently set late/conditionally, then replace `hasattr` checks with direct access.

---

## Tasks

### Task 1.1: App — showing_new_game_setup [Simple]
**File:** `game/app.py`
**Tests:** `pytest tests/unit/ui/ -k app --testmon`

- [ ] Add `self.showing_new_game_setup: bool = False` in `__init__` (near L148, with other state flags)
- [ ] L565: Replace `if hasattr(self, 'showing_new_game_setup') and self.showing_new_game_setup:` with `if self.showing_new_game_setup:`

**Notes:**

### Task 1.2: App — return_state [Simple]
**File:** `game/app.py`
**Tests:** `pytest tests/unit/ui/ -k app --testmon`

- [ ] Add `self.return_state: Optional[GameState] = None` in `__init__` (near L148)
- [ ] L598: Replace `if hasattr(self, 'return_state') and self.return_state == GameState.TEST_LAB:` with `if self.return_state == GameState.TEST_LAB:`

**Notes:**

### Task 1.3: BuilderWidgets — clear_settings_btn [Simple]
**File:** `game/ui/panels/builder_widgets.py`
**Tests:** `pytest tests/unit/ui/panels/ --testmon`

- [ ] Add `self.clear_settings_btn = None` in `__init__` (before conditional layout code)
- [ ] L273: Replace `if hasattr(self, 'clear_settings_btn') and event.ui_element == self.clear_settings_btn:` with `if self.clear_settings_btn and event.ui_element == self.clear_settings_btn:`

**Notes:**

### Task 1.4: FormationEditor — rotation_mode_btn & renumber_slider [Simple]
**File:** `game/ui/screens/formation_editor.py`
**Tests:** `pytest tests/unit/ui/screens/ -k formation --testmon`

- [ ] Add `self.rotation_mode_btn = None` in `__init__` or `FormationCore.__init__`
- [ ] Add `self.renumber_slider = None` in `__init__` or `FormationCore.__init__`
- [ ] L778: Replace `if hasattr(self, 'rotation_mode_btn'):` with `if self.rotation_mode_btn:`
- [ ] L797: Replace `if hasattr(self, 'renumber_slider'):` with `if self.renumber_slider:`

**Notes:** Check class hierarchy — may need to init in base class

### Task 1.5: PlanetListWindow — last_preset_selection [Simple]
**File:** `game/ui/screens/planet_list_window.py`
**Tests:** `pytest tests/unit/ui/screens/ -k planet --testmon`

- [ ] Add `self.last_preset_selection = None` in `__init__`
- [ ] L366: Replace `if not hasattr(self, 'last_preset_selection'):` with `if self.last_preset_selection is None:`

**Notes:**

### Task 1.6: RaceSetupScreen — preview elements & btn_load [Simple]
**File:** `game/ui/screens/race_setup_screen.py`
**Tests:** `pytest tests/unit/ui/screens/ -k race --testmon`

- [ ] Add `self._ship_preview_elements: list = []` in `__init__`
- [ ] Add `self.ship_preview_scroll = None` in `__init__`
- [ ] Add `self.btn_load = None` in `__init__`
- [ ] L384: Remove hasattr guard, use direct loop: `for elem in self._ship_preview_elements: elem.kill()`
- [ ] L389: Replace `if not hasattr(self, 'ship_preview_scroll'):` with `if self.ship_preview_scroll is None:`
- [ ] L889: Replace `elif hasattr(self, 'btn_load') and self.btn_load and event.ui_element == self.btn_load:` with `elif self.btn_load and event.ui_element == self.btn_load:`

**Notes:**

### Task 1.7: Run targeted tests [Simple]
**Tests:** `pytest tests/ --testmon`

- [ ] All affected tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
