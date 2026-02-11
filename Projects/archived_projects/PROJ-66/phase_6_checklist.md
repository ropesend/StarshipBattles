# Phase 6: Tab Reorganization & Summary Update [Medium]

**Objective:** Restructure RaceSetupScreen from 5 tabs to 7 tabs, update Summary panel
**Tests:** `pytest tests/unit/ui/ -v -k "race"`
**Status:** COMPLETE

---

## Task 6.1: Update Tab Constants and Layout [Simple]
**File:** `game/ui/screens/race_setup_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_race_setup_screen.py -v` (if exists)

- [x] Update TAB constants:
  ```python
  TAB_SUMMARY = 0
  TAB_IDENTITY = 1      # NEW
  TAB_VISUALS = 2        # was 1
  TAB_SHIPS = 3          # was 2
  TAB_ENVIRONMENT = 4    # was 3
  TAB_APTITUDES = 5      # NEW
  TAB_DESCRIPTIONS = 6   # was 4
  ```
- [x] Update `TAB_NAMES` list to 7 items:
  ```python
  TAB_NAMES = ["Summary", "Identity", "Visuals", "Ships", "Environment", "Aptitudes", "Descriptions"]
  ```
- [x] Verify tab width calculation still works: `(content_width - 10) // 7` ≈ 252px (OK)
- [x] Run tests: verify no immediate failures from constant changes
**Notes:** Tab indices shift correctly - all use TAB_* constants.

---

## Task 6.2: Create Identity and Aptitudes Panels in Screen [Medium]
**File:** `game/ui/screens/race_setup_screen.py`
**Tests:** `pytest tests/unit/ui/ -v -k "race"`

- [x] Import `RaceIdentityPanel` from `game.ui.panels.race_identity_panel`
- [x] Import `RaceAptitudesPanel` from `game.ui.panels.race_aptitudes_panel`
- [x] Add `self._identity_panel = None` in `__init__`
- [x] Add `self._aptitudes_panel = None` in `__init__`
- [x] Update `_create_step_panels()` to create 7 panels (insert Identity at index 1, Aptitudes at index 5)
- [x] Create `_create_identity_panel_content(self, panel)`
- [x] Create `_create_aptitudes_panel_content(self, panel)`
- [x] Move Race Name input from Visuals tab to Identity tab (removed from `_create_visuals_panel_content`)
- [x] Run tests: verify panels create without errors
**Notes:** Race Name field now in Identity tab. name_input removed from Visuals.

---

## Task 6.3: Update Event Routing [Medium]
**File:** `game/ui/screens/race_setup_screen.py`
**Tests:** Manual testing + `pytest tests/unit/ui/ -v -k "race"`

- [x] Add dropdown event handling in `process_event()` for identity and environment panels
- [x] Update slider event handler to include aptitudes panel budget display update
- [x] Update text entry handler to include identity panel
- [x] Update `_show_step()` to refresh aptitudes budget when showing Aptitudes tab
- [x] Added `handle_dropdown_change()` to RaceEnvironmentPanel
- [x] Run tests: verify event routing works
**Notes:** All event types properly routed to new panels.

---

## Task 6.4: Update _populate_ui_from_config [Simple]
**File:** `game/ui/screens/race_setup_screen.py`

- [x] Update `_populate_ui_from_config()` to include new panels
- [x] Update `_validate_for_save()`:
  - Sync race name from identity panel
  - Sync aptitudes from aptitudes panel
  - Check point budget: if over budget, return error with tab reference
- [x] Run tests: verify config loading works
**Notes:** Budget validation added before save.

---

## Task 6.5: Update Summary Panel [Medium]
**File:** `game/ui/panels/race_summary_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_race_summary_panel.py -v`

- [x] Read current summary panel implementation
- [x] Add display for new identity fields:
  - Faction Name (prominent, at top)
  - Race Name
  - Government Type + Organization
  - Physical Type
  - Society Type
- [x] Add display for homeworld type
- [x] Add display for water preferences
- [x] Add display for aptitude summary (compact 3-line format)
- [x] Add display for point budget status
- [x] Update `refresh()` method to update all new labels
- [x] Update tests for new summary field names (faction_value instead of name_value)
- [x] Run tests: all 20 summary panel tests pass
**Notes:** Column 1 now shows identity info. Column 3 expanded with homeworld, water, aptitudes, budget.

---

## Phase 6 Completion Checklist
- [x] All tasks above checked off
- [x] 7 tabs display correctly in UI
- [x] Race Name moved from Visuals to Identity tab
- [x] All event types routed to correct panels
- [x] Summary shows all new fields
- [x] Run `pytest tests/unit/ui/ -v -k "race"` — 210 passed
- [x] Run `pytest tests/ -n 12` — 6210 passed (excl. 3 pre-existing failures)
