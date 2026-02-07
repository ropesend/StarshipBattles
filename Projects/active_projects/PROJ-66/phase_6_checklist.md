# Phase 6: Tab Reorganization & Summary Update [Medium]

**Objective:** Restructure RaceSetupScreen from 5 tabs to 7 tabs, update Summary panel
**Tests:** `pytest tests/unit/ui/ -v -k "race"`

---

## Task 6.1: Update Tab Constants and Layout [Simple]
**File:** `game/ui/screens/race_setup_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_race_setup_screen.py -v` (if exists)

- [ ] Update TAB constants:
  ```python
  TAB_SUMMARY = 0
  TAB_IDENTITY = 1      # NEW
  TAB_VISUALS = 2        # was 1
  TAB_SHIPS = 3          # was 2
  TAB_ENVIRONMENT = 4    # was 3
  TAB_APTITUDES = 5      # NEW
  TAB_DESCRIPTIONS = 6   # was 4
  ```
- [ ] Update `TAB_NAMES` list to 7 items:
  ```python
  TAB_NAMES = ["Summary", "Identity", "Visuals", "Ships", "Environment", "Aptitudes", "Descriptions"]
  ```
- [ ] Verify tab width calculation still works: `(content_width - 10) // 7` ≈ 252px (OK)
- [ ] Run tests: verify no immediate failures from constant changes
**Notes:** Tab indices will shift — all references to TAB_VISUALS, TAB_SHIPS, TAB_ENVIRONMENT, TAB_DESCRIPTIONS must use the constants (not hardcoded numbers).

---

## Task 6.2: Create Identity and Aptitudes Panels in Screen [Medium]
**File:** `game/ui/screens/race_setup_screen.py`
**Tests:** `pytest tests/unit/ui/ -v -k "race"`

- [ ] Import `RaceIdentityPanel` from `game.ui.panels.race_identity_panel`
- [ ] Import `RaceAptitudesPanel` from `game.ui.panels.race_aptitudes_panel`
- [ ] Add `self._identity_panel = None` in `__init__`
- [ ] Add `self._aptitudes_panel = None` in `__init__`
- [ ] Update `_create_step_panels()` to create 7 panels (insert Identity at index 1, Aptitudes at index 5):
  - Panel 0: Summary (unchanged)
  - Panel 1: Identity (NEW) — `self._create_identity_panel_content(panel)`
  - Panel 2: Visuals (moved from index 1)
  - Panel 3: Ships (moved from index 2)
  - Panel 4: Environment (moved from index 3)
  - Panel 5: Aptitudes (NEW) — `self._create_aptitudes_panel_content(panel)`
  - Panel 6: Descriptions (moved from index 4)
- [ ] Create `_create_identity_panel_content(self, panel)`:
  ```python
  self._identity_panel = RaceIdentityPanel(
      panel=panel, manager=self.ui_manager, race_config=self.race_config
  )
  ```
- [ ] Create `_create_aptitudes_panel_content(self, panel)`:
  ```python
  self._aptitudes_panel = RaceAptitudesPanel(
      panel=panel, manager=self.ui_manager, race_config=self.race_config
  )
  ```
- [ ] Move Race Name input from Visuals tab to Identity tab (remove from `_create_visuals_panel_content`)
- [ ] Run tests: verify panels create without errors
**Notes:** Race Name field moves from Visuals → Identity tab. The `name_input` in Visuals panel is removed.

---

## Task 6.3: Update Event Routing [Medium]
**File:** `game/ui/screens/race_setup_screen.py`
**Tests:** Manual testing + `pytest tests/unit/ui/ -v -k "race"`

- [ ] Add dropdown event handling in `process_event()`:
  ```python
  elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
      # Identity panel dropdowns
      if self._identity_panel:
          self._identity_panel.update_config()
      # Environment panel homeworld dropdown
      if self._environment_panel:
          # Check if homeworld dropdown changed
          self._environment_panel.handle_dropdown_change(event)
      handled = True
  ```
- [ ] Update slider event handler to include aptitudes panel:
  ```python
  elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
      self._update_env_labels()
      self._update_env_from_sliders()
      # Update aptitudes panel budget display when env tolerance sliders change
      if self._aptitudes_panel:
          self._aptitudes_panel.update_config()
          self._aptitudes_panel.update_budget_display()
      handled = True
  ```
- [ ] Update text entry handler to include identity panel:
  ```python
  elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
      if self._identity_panel:
          self._identity_panel.update_config()
      if self._description_panel:
          # existing description handling...
  ```
- [ ] Update `_show_step()` to refresh aptitudes budget when showing Aptitudes tab:
  ```python
  elif step_num == self.TAB_APTITUDES:
      if self._aptitudes_panel:
          self._aptitudes_panel.update_budget_display()
  ```
- [ ] Run tests: verify event routing works
**Notes:**

---

## Task 6.4: Update _populate_ui_from_config [Simple]
**File:** `game/ui/screens/race_setup_screen.py`

- [ ] Update `_populate_ui_from_config()` to include new panels:
  ```python
  # Update identity panel
  if self._identity_panel:
      self._identity_panel.set_from_config()

  # Update aptitudes panel
  if self._aptitudes_panel:
      self._aptitudes_panel.set_from_config()
  ```
- [ ] Update `_validate_for_save()`:
  - Sync race name from identity panel (was previously from name_input on Visuals)
  - Sync aptitudes from aptitudes panel
  - Check point budget: if over budget, return error with tab reference
- [ ] Run tests: verify config loading works
**Notes:**

---

## Task 6.5: Update Summary Panel [Medium]
**File:** `game/ui/panels/race_summary_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_race_summary_panel.py -v`

- [ ] Read current summary panel implementation
- [ ] Add display for new identity fields:
  - Faction Name (prominent, at top)
  - Race Name + Plural
  - Government Type + Organization
  - Leader Title
  - Physical Type
  - Society Type
- [ ] Add display for homeworld type
- [ ] Add display for water preferences
- [ ] Add display for aptitude summary (compact format, e.g., "STR:7 INT:5 CON:8...")
- [ ] Add display for point budget status ("Points: 85/100 used")
- [ ] Update `refresh()` method to update all new labels
- [ ] Write/update test: `test_summary_displays_faction_name`
- [ ] Write/update test: `test_summary_displays_government_info`
- [ ] Write/update test: `test_summary_displays_aptitudes`
- [ ] Write/update test: `test_summary_displays_homeworld_type`
- [ ] Write/update test: `test_summary_displays_budget_status`
- [ ] Run tests: all pass
**Notes:** Summary may need to use scrolling if content exceeds panel height.

---

## Phase 6 Completion Checklist
- [ ] All tasks above checked off
- [ ] 7 tabs display correctly in UI
- [ ] Race Name moved from Visuals to Identity tab
- [ ] All event types routed to correct panels
- [ ] Summary shows all new fields
- [ ] Run `pytest tests/unit/ui/ -v -k "race"` — all pass
- [ ] Run `pytest tests/ --testmon` — no regressions
