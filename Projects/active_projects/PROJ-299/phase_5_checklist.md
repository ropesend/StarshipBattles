# Phase 5: Description tab UI integration [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-299 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Two Generate buttons + two Re-roll buttons (initially hidden) + two status labels (below text boxes) + dual-button cancel UI. Wire `RaceSetupScreen.update()` to poll the controller. Lock text boxes during generation. Inject controller state changes into the panel via the `on_change` callback.

**See `design.md` § "UI integration" for the button visibility table.**

---

## Tasks

### Task 5.1: Add buttons + status labels to `RaceDescriptionPanel` [Complex]
**File:** `game/ui/panels/race_description_panel.py`
**Tests:** `pytest tests/unit/ui/test_race_description_panel.py`

- [x] Write failing tests:
  - Panel exposes `btn_generate_bio`, `btn_cancel_bio`, `btn_re_roll_bio`, `lbl_bio_status` widgets after `_create_content()`
  - Same for socio (`_socio` suffix)
  - `set_state(controller)` reads `controller.bio_status` and toggles button visibility per design.md table
  - `set_state(controller)` updates `lbl_bio_status` text based on status: hidden when IDLE, "Generating Bio… 12s" when RUNNING, hidden when DONE/CANCELLED, error message when ERROR
  - `set_state(controller)` disables `bio_text_box` while bio_status == RUNNING; re-enables otherwise
- [x] Add the new widgets to `_create_content()` (Generate / Cancel / Re-roll buttons; status label between text box and char-count). Initial visibility: Generate visible; Cancel and Re-roll hidden.
- [x] Add `set_state(controller)` method that takes a `RaceDescriptionLLMController` and reconciles widget state per design.md table.
- [x] Run tests, confirm pass

**Notes:**

### Task 5.2: Wire button events to the controller [Medium]
**File:** `game/ui/screens/race_setup_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_race_setup_screen.py`

- [x] Write failing tests:
  - Construct `RaceSetupScreen` with a stub provider injected via context
  - Verify a `RaceDescriptionLLMController` instance is created and held on the screen
  - Click Generate Bio → controller's `generate_bio()` is called
  - Click Cancel Bio → controller's `cancel_bio()` is called
  - Click Re-roll Bio → controller's `re_roll_bio()` is called
  - Same for socio
- [x] Add `self._description_controller = RaceDescriptionLLMController(...)` to `RaceSetupScreen.__init__` (or wherever the description panel is constructed). Pass `on_change=self._rebuild_description_panel`.
- [x] In `process_event()`, route the new button clicks to the controller methods.
- [x] Add `_rebuild_description_panel()` method that calls `self.description_panel.set_state(self._description_controller)`.
- [x] Run tests, confirm pass

**Notes:**

### Task 5.3: Wire `RaceSetupScreen.update()` for polling [Medium]
**File:** `game/ui/screens/race_setup_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_race_setup_screen.py`

- [x] Write failing tests:
  - `RaceSetupScreen.update(time_delta)` is overridden (does NOT exist today per Phase A finding)
  - The override calls `self._description_controller.update()` each frame
  - When the controller's state changes from RUNNING to DONE, the panel's text box reflects the new content
- [x] Add `update(time_delta)` method to RaceSetupScreen:
  ```python
  def update(self, time_delta):
      super().update(time_delta)
      if self._description_controller is not None:
          self._description_controller.update()
  ```
- [x] Run tests, confirm pass

**Notes:**

### Task 5.4: Update navigation button visibility filter [Simple]
**File:** `game/ui/screens/race_setup_screen.py` line ~707-722
**Tests:** Same as 5.2

- [x] In `_update_navigation_buttons()`, ensure the existing "Generate Random" bottom-bar button stays HIDDEN on TAB_DESCRIPTIONS. Our buttons live in the panel itself, not in the bottom bar.
- [x] Verify by reading current code that no extra logic is needed beyond keeping the current TAB_DESCRIPTIONS exclusion.

**Notes:**

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] ~12 new tests across `test_race_description_panel.py` + `test_race_setup_screen.py`
- [x] `pytest tests/unit/ui/` — all green
- [x] No baseline regression
- [x] Update status at top of this file to `Complete`
- [x] Update `plan.md` phase table row to `Complete`
- [x] Update `plan.md` Current State to point to Phase 6
