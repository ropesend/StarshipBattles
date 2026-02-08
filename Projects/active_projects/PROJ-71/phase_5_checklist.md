# Phase 5: Verification & Polish

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-71 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Full test pass, manual verification of all hotkeys, edge case handling, final polish.

---

## Tasks

### Task 5.1: Full automated test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run `pytest tests/ -n 12` - all tests pass (baseline: 6519+)
- [ ] Run `pytest tests/unit/core/test_input_mapper.py tests/unit/core/test_input_actions.py -v` - all new tests pass
- [ ] Run `pytest tests/unit/ui/ -v` - all UI tests pass
- [ ] No warnings or deprecation issues from new code

**Notes:**

---

### Task 5.2: Manual verification - Strategy hotkeys [Medium]
**Tests:** Manual in-game

- [ ] Launch game, Quickstart 1P
- [ ] Test fleet commands: M (move), J (join), C (colonize), T (transfer), ESC (cancel)
- [ ] Test camera: Shift+G (galaxy zoom), Shift+S (system zoom)
- [ ] Test screenshots: F12 (full), F11 (viewport)
- [ ] Test navigation: Prev/Next Colony, Prev/Next Fleet hotkeys
- [ ] Test top bar: P (planets), D (design), Ctrl+S (save), Space/Enter (end turn)
- [ ] Test fleet detail: O (orders), F (fleet report) when fleet selected
- [ ] Test global: ALT+X (exit dialog), F9 (profiler toggle)

**Notes:**

---

### Task 5.3: Manual verification - Tooltips [Simple]
**Tests:** Manual in-game

- [ ] Hover over End Turn button - tooltip shows hotkey
- [ ] Hover over Planets button - tooltip shows hotkey
- [ ] Hover over Design button - tooltip shows hotkey
- [ ] Hover over Save Game button - tooltip shows hotkey
- [ ] Hover over nav buttons (<, >) - tooltips show hotkeys
- [ ] Hover over Colonize button (when shown) - tooltip shows hotkey
- [ ] Hover over Orders button (when shown) - tooltip shows hotkey
- [ ] Hover over Fleet Report button (when shown) - tooltip shows hotkey

**Notes:**

---

### Task 5.4: Manual verification - Sub-window hotkeys [Medium]
**Tests:** Manual in-game

- [ ] Fleet Orders: Open, Ctrl+Z undo works, tooltip shows on Undo button
- [ ] Build Queue: Open, ESC closes, 1-4 switch categories, Delete removes item
- [ ] Transfer Dialog: Open, Enter confirms, ESC cancels
- [ ] Build Queue List: Open, ESC closes

**Notes:**

---

### Task 5.5: Manual verification - Keybinding editor [Medium]
**Tests:** Manual in-game

- [ ] Open keybindings scene (via direct call or temporary test button)
- [ ] All actions displayed, grouped correctly
- [ ] Click Rebind on "Move Fleet" - overlay appears
- [ ] Press N - binding changes to N, display updates
- [ ] Verify: pressing N in strategy screen now triggers move mode (M no longer works)
- [ ] Click Rebind on another action, press N - conflict dialog appears
- [ ] Accept conflict - previous action unbinds, new action binds to N
- [ ] Click Reset on modified action - reverts to default
- [ ] Click Reset All - all bindings revert
- [ ] Click Save & Close - file saved to output/settings/keybindings.json
- [ ] Restart game - customized bindings persist
- [ ] Close without saving - changes discarded, confirmation prompt shown

**Notes:**

---

### Task 5.6: Edge case handling [Simple]
**Tests:** Manual + automated

- [ ] No output/settings/ directory exists - save creates it automatically
- [ ] Corrupt user keybindings.json - graceful fallback to defaults
- [ ] Empty user keybindings.json - falls back to defaults
- [ ] All actions unbound - no crashes, tooltips show empty
- [ ] Modifier-only keypress during capture - ignored, capture continues

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All automated tests pass
- [ ] All manual verification passed
- [ ] Edge cases handled gracefully
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"
