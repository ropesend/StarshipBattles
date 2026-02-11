# Phase 4: Multi-Select + Remove Ships

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-101 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add Ctrl+click multi-selection and "Remove Selected" button that creates a new fleet from all removed ships.

---

## Tasks

### Task 4.1: Thread Empire Reference [Simple]
**Files:** `game/ui/screens/fleet_report_window.py`, `game/ui/screens/strategy_window_manager.py`
**Tests:** `pytest tests/unit/ui/ -k fleet_report`

- [ ] Add `empire=None` parameter to `FleetReportWindow.__init__` (line 27):
  ```python
  def __init__(self, rect, manager, fleet, empire=None, on_close_callback=None):
  ```
- [ ] Store: `self.empire = empire` (after line 45)
- [ ] In `strategy_window_manager.py:open_fleet_report_window()` (line 256), pass empire:
  ```python
  empire = self.scene.current_empire
  self.fleet_report_window = FleetReportWindow(
      rect, self.manager, fleet,
      empire=empire,
      on_close_callback=self._on_fleet_report_closed,
  )
  ```

**Notes:**

### Task 4.2: Add Multi-Select State [Simple]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** `pytest tests/unit/ui/ -k fleet_report`

- [ ] Add `self.selected_indices: set = set()` in `__init__` (after line 58)
- [ ] Replace `self.selected_ship = None` usage — selected_ship derived from selected_indices

**Notes:**

### Task 4.3: Implement Ctrl+Click Multi-Select [Medium]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** `pytest tests/unit/ui/ -k fleet_report`

- [ ] Rewrite `_handle_row_click()` (line 732) to support multi-select:
  ```python
  def _handle_row_click(self, pos):
      list_rect = self.list_view_panel.get_abs_rect()
      if not list_rect.collidepoint(pos):
          return False

      filtered_ships = self.view_model.get_filtered_ships()
      for row in self.row_pool:
          if not row['bg'].visible:
              continue
          row_rect = row['bg'].get_abs_rect()
          if row_rect.collidepoint(pos):
              ship_index = row.get('ship_index', -1)
              if 0 <= ship_index < len(filtered_ships):
                  mods = pygame.key.get_mods()
                  ctrl_held = bool(mods & pygame.KMOD_CTRL)

                  if ctrl_held:
                      if ship_index in self.selected_indices:
                          if len(self.selected_indices) > 1:
                              self.selected_indices.discard(ship_index)
                      else:
                          self.selected_indices.add(ship_index)
                  else:
                      self.selected_indices = {ship_index}

                  # Update detail panel
                  if len(self.selected_indices) == 1:
                      sole_idx = next(iter(self.selected_indices))
                      self.selected_ship = filtered_ships[sole_idx]
                  else:
                      self.selected_ship = None
                  self._update_detail_panel()
                  self._update_remove_button()
                  self._update_visible_rows()  # Refresh row highlighting
                  return True
      return False
  ```

**Notes:**

### Task 4.4: Add Visual Selection Highlighting [Simple]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** Manual test — visual verification

- [ ] In `_update_visible_rows()` (line 506), after showing/positioning a row, apply highlight:
  ```python
  # After row['bg'].show() and data update:
  if row['ship_index'] in self.selected_indices:
      # Apply selection color (e.g., darker blue tint)
      # Use row['bg'].background_colour or similar pygame_gui API
  ```
- [ ] Choose appropriate highlight color that works with both light and dark themes

**Notes:** Investigate pygame_gui panel background color API. May need to use object_id styling or direct colour property.

### Task 4.5: Add "Remove Selected" Button [Simple]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** `pytest tests/unit/ui/ -k fleet_report`

- [ ] Add a UIButton in the sidebar or below the ship list:
  ```python
  self.btn_remove_selected = UIButton(
      relative_rect=pygame.Rect(...),
      text="Remove Selected",
      manager=self.ui_manager,
      container=self.sidebar_panel,  # or self.list_panel
      object_id="#btn_remove_selected"
  )
  self.btn_remove_selected.disable()  # Disabled until selection exists
  ```
- [ ] Add `_update_remove_button()` method to enable/disable and update text:
  ```python
  def _update_remove_button(self):
      count = len(self.selected_indices)
      if count > 0 and self.empire:
          self.btn_remove_selected.enable()
          self.btn_remove_selected.set_text(f"Remove Selected ({count})")
      else:
          self.btn_remove_selected.disable()
          self.btn_remove_selected.set_text("Remove Selected")
  ```
- [ ] Add button press check in `update()` method:
  ```python
  if hasattr(self, 'btn_remove_selected') and self.btn_remove_selected.check_pressed():
      self._on_remove_selected_ships()
  ```

**Notes:**

### Task 4.6: Implement Ship Removal Logic [Medium]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** `pytest tests/unit/ui/ -k fleet_report`

- [ ] Add import: `from game.strategy.data.fleet import Fleet`
- [ ] Implement `_on_remove_selected_ships()`:
  ```python
  def _on_remove_selected_ships(self):
      if not self.empire or not self.selected_indices:
          return

      filtered_ships = self.view_model.get_filtered_ships()
      ships_to_remove = [filtered_ships[i] for i in sorted(self.selected_indices)
                         if 0 <= i < len(filtered_ships)]
      if not ships_to_remove:
          return

      # Create one new fleet with all removed ships
      new_fleet_id = self.empire.get_next_fleet_id()
      new_fleet = Fleet(new_fleet_id, self.fleet.owner_id, self.fleet.location, speed=0)

      for ship in ships_to_remove:
          self.fleet.remove_ship(ship)
          new_fleet.add_ship(ship)

      self.empire.add_fleet(new_fleet)
      self._post_removal_refresh()
  ```
- [ ] Implement `_post_removal_refresh()`:
  ```python
  def _post_removal_refresh(self):
      self.selected_indices.clear()
      self.selected_ship = None
      self.view_model.update_ships(self.fleet.ships)
      self._update_detail_panel()
      self.refresh_list()
      self._update_summary()
      self._update_remove_button()
  ```
- [ ] Update existing `_on_remove_ship()` (line 771) to also use `_post_removal_refresh()` pattern and to create a new single-ship fleet (if empire is available)

**Notes:**

### Task 4.7: Write Unit Tests [Medium]
**Tests:** `pytest tests/unit/ui/ -k fleet_report`

- [ ] Test single click selects one ship (selected_indices = {index})
- [ ] Test Ctrl+click adds to selection
- [ ] Test Ctrl+click removes from selection (if more than 1 selected)
- [ ] Test Ctrl+click cannot deselect last ship
- [ ] Test remove creates new fleet with removed ships at same location
- [ ] Test source fleet no longer contains removed ships
- [ ] Test new fleet added to empire
- [ ] Test UI refresh after removal (selected_indices cleared)

**Notes:**

### Task 4.8: Run Tests [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite
- [ ] All tests pass (baseline + all new tests)
- [ ] No regressions

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
