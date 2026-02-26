# Phase 1: Lazy Init — True Missing Inits

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-199 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add `__init__` declarations for attributes that are currently set late/conditionally, then replace `hasattr` checks with direct access.

---

## Tasks

### Task 1.1: App — showing_new_game_setup [Simple]
**File:** `game/app.py`
**Tests:** `pytest tests/unit/ui/ -k app --testmon`

- [x] Add `self.showing_new_game_setup: bool = False` in `__init__` (near L148, with other state flags)
- [x] L565: Replace `if hasattr(self, 'showing_new_game_setup') and self.showing_new_game_setup:` with `if self.showing_new_game_setup:`

**Notes:** Also added `from typing import Optional` for return_state type hint.

### Task 1.2: App — return_state [Simple]
**File:** `game/app.py`
**Tests:** `pytest tests/unit/ui/ -k app --testmon`

- [x] Add `self.return_state: Optional[GameState] = None` in `__init__` (near L148)
- [x] L598: Replace `if hasattr(self, 'return_state') and self.return_state == GameState.TEST_LAB:` with `if self.return_state == GameState.TEST_LAB:`

**Notes:** Complete.

### Task 1.3: BuilderWidgets — clear_settings_btn [Simple]
**File:** `game/ui/panels/builder_widgets.py`
**Tests:** `pytest tests/unit/ui/panels/ --testmon`

- [x] Add `self.clear_settings_btn = None` in `__init__` (before conditional layout code)
- [x] L273: Replace `if hasattr(self, 'clear_settings_btn') and event.ui_element == self.clear_settings_btn:` with `if self.clear_settings_btn and event.ui_element == self.clear_settings_btn:`

**Notes:** Complete.

### Task 1.4: FormationEditor — rotation_mode_btn & renumber_slider [MOVED TO PHASE 2]

**Notes:** Code review showed these are NOT true lazy inits — they're assigned unconditionally at L292 and L301 from toolbar builder. The hasattr checks at L778/L797 are unnecessary guards. Moved to Phase 2.

### Task 1.5: PlanetListWindow — last_preset_selection [Simple]
**File:** `game/ui/screens/planet_list_window.py`
**Tests:** `pytest tests/unit/ui/screens/ -k planet --testmon`

- [x] Add `self.last_preset_selection = None` in `__init__`
- [x] L366: Replace `if not hasattr(self, 'last_preset_selection'):` with `if self.last_preset_selection is None:`

**Notes:** Complete.

### Task 1.6: RaceSetupScreen — preview elements & btn_load [Simple]
**File:** `game/ui/screens/race_setup_screen.py`
**Tests:** `pytest tests/unit/ui/screens/ -k race --testmon`

- [x] Add `self._ship_preview_elements: list = []` in `__init__`
- [x] Add `self.ship_preview_scroll = None` in `__init__`
- [x] Add `self.btn_load = None` in `__init__` — **ALREADY EXISTS at L129**
- [x] L384: Remove hasattr guard, use direct loop: `for elem in self._ship_preview_elements: elem.kill()`
- [x] L389: Replace `if not hasattr(self, 'ship_preview_scroll'):` with `if self.ship_preview_scroll is None:`
- [x] L889: Replace `elif hasattr(self, 'btn_load') and self.btn_load and event.ui_element == self.btn_load:` with `elif self.btn_load and event.ui_element == self.btn_load:`

**Notes:** Complete.

### Task 1.7: Run targeted tests [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] All affected tests pass (12724 passed, 1 skipped)

**Notes:** Full test suite verified.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
