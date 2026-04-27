# Phase 6: Dialogs + cancel hook + error popups [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-299 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** 30s "still working" modal (re-armed at 90s). Per-error-type popups. `RaceSetupScreen.kill()` cancel hook for all in-flight calls.

---

## Tasks

### Task 6.1: 30s "still working" modal [Complex]
**File:** `game/ui/screens/race_setup_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_race_setup_screen.py`

- [ ] Write failing tests:
  - Simulate `controller.bio_elapsed_seconds = 31` (mock or via test-only setter) → screen creates the "still working" modal
  - Modal is a `pygame_gui.elements.UIWindow` with two buttons: "Keep Waiting" and "Stop"
  - Modal does NOT show again at 31s if already showed and dismissed
  - Modal RE-shows at `elapsed_seconds == 91s` if `bio_status` is still RUNNING
  - Click "Keep Waiting" → modal closes; controller untouched
  - Click "Stop" → controller's `cancel_all()` called; modal closes
  - If both bio AND socio pass 30s simultaneously, only ONE modal shows (not two)
- [ ] Implement (pattern: copy `_show_save_update_dialog()` template at race_setup_screen.py:1093-1159):
  - Track per-call "modal shown at threshold N" flags so the modal doesn't spam
  - Logic: show at 30s; after dismiss, show again at 90s; never show after 90s (LLM `timeout_seconds=90` will fire shortly)
- [ ] Run tests, confirm pass

**Notes:**

### Task 6.2: Per-error-type popups [Medium]
**File:** `game/ui/screens/race_setup_screen.py`
**Tests:** Same file

- [ ] Write failing tests:
  - When `controller.bio_status` transitions to ERROR with `LLMNetworkError`, popup shows "Network error: could not reach the LLM service"
  - When ERROR with `LLMRateLimited`, popup shows "Rate limited; please wait and try again"
  - When ERROR with `LLMTimeoutError`, popup shows "Timed out after 90 seconds"
  - When ERROR with `LLMConfigError`, popup shows "LLM not configured (DEEPSEEK_API_KEY?)"
  - Popup has a single OK button
  - Dismissing the popup does NOT auto-clear the controller's ERROR state — user must click Generate again
  - If both bio and socio error simultaneously, both popups queue (not overlap)
- [ ] Implement: small helper `_show_llm_error_popup(error: LLMException)` that maps exception type → message and constructs a UIWindow.
- [ ] Run tests, confirm pass

**Notes:**

### Task 6.3: `RaceSetupScreen.kill()` cancel hook [Medium]
**File:** `game/ui/screens/race_setup_screen.py`
**Tests:** Same file

- [ ] Write failing test:
  - Construct screen, call `generate_bio()` on controller, then `screen.kill()`
  - Verify `controller.cancel_all()` was called (mock or spy)
  - Verify no unhandled exceptions are raised
- [ ] Override `kill()`:
  ```python
  def kill(self):
      if self._description_controller is not None:
          self._description_controller.cancel_all()
      super().kill()
  ```
- [ ] Run test, confirm pass

**Notes:**

### Task 6.4: Manual smoke (deferred — user task) [Simple]
**File:** N/A
**Tests:** Manual

- [ ] User: with `DEEPSEEK_API_KEY` set, launch the game → Race Setup → Description tab → click Generate Bio → confirm status label appears, text populates within ~10s
- [ ] User: simulate network slowness (firewall the request) → confirm 30s modal appears, "Keep Waiting" → second modal at 90s → timeout error popup
- [ ] User: click Generate Bio twice rapidly → confirm second click does nothing (button disabled)
- [ ] User: click Generate Bio + Cancel Bio quickly → confirm prior text restored
- [ ] User: close the screen mid-call → confirm no error logs

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] ~6 new tests
- [ ] `pytest tests/unit/ui/screens/test_race_setup_screen.py` — all green
- [ ] No baseline regression
- [ ] Update status at top of this file to `Complete`
- [ ] Update `plan.md` phase table row to `Complete`
- [ ] Update `plan.md` Current State to point to Phase 7
