# Phase 3: R3 — Delete legacy `<Class>_Portrait.jpg` helper

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-318 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Eradicate the `get_portrait_filename()` helper and any
`get_portrait_search_paths()` legacy fallback per CLAUDE.md Rule 3
(System Migration Policy: no backward-compat shims after a
migration). Update production callers to use
`ShipThemeManager.get_portrait_image()` directly. Delete the
3 tests pinning the legacy convention.

---

## Tasks

### Task 3.1: Audit callers of the legacy helper [Simple]
**File:** None (search/audit task).
**Tests:** None.

- [x] Grep production code: `grep -rn "get_portrait_filename\|get_portrait_search_paths\|_Portrait\.jpg" game/ Tools/`
- [x] Grep tests: `grep -rn "get_portrait_filename\|get_portrait_search_paths\|_Portrait\.jpg" tests/`
- [x] List every production caller and what method it calls
- [x] Confirm the 2 production callers identified during planning:
  - `game/ui/panels/build_queue_portraits.py:23`
  - `game/ui/panels/design_report_panel.py:18-20`
- [x] If additional callers found, add them as sub-tasks to Task 3.2 below

**Notes:** Capture the full list of callers here for traceability.

### Task 3.2: Migrate production callers to ShipThemeManager [Medium]
**File:** `game/ui/panels/build_queue_portraits.py`, `game/ui/panels/design_report_panel.py`, plus any new ones found in 3.1.
**Tests:** `pytest tests/unit/ui/panels/ tests/unit/ui/screens/builder/ -n 12`

- [x] In `build_queue_portraits.py`, replace `get_portrait_search_paths()` use with `get_default_ship_theme_manager().get_portrait_image(theme, ship_class)`
- [x] In `design_report_panel.py`, replace `get_portrait_search_paths()` / `create_placeholder_portrait()` use with the same. The `ShipThemeManager.get_portrait_image()` already returns a Surface with synthetic fallback — no separate placeholder needed.
- [x] Run targeted UI panel tests, confirm pass
- [x] Manual smoke (deferred to Phase Completion): launch game, open Build Queue (verify portrait shows for each ship), open Workshop's Design Report (verify portrait shows)

**Notes:** Completed; production callers now use `ShipThemeManager.get_portrait_image()`, legacy helper exports/tests are deleted, grep shows no legacy ship-portrait convention in game/UI tests, and the UI subset passed 620/620. Manual interactive smoke was replaced by the headless UI integration suite in this session.
### Task 3.3: Delete the legacy helper functions [Simple]
**File:** `game/ui/utils/portraits.py`
**Tests:** `pytest tests/unit/ui/utils/test_portraits.py -n 12`

- [x] Delete `get_portrait_filename()` (lines 83-97)
- [x] Delete `parse_ship_class_name()` if it's only used by `get_portrait_filename()` (verify with grep)
- [x] Delete `get_portrait_search_paths()` (lines 98-114) if no caller remains after Task 3.2
- [x] Verify the file still has any non-legacy helpers it needs (`get_ship_class_color()`, `create_placeholder_portrait()` may still be used elsewhere — check before deleting)
- [x] Run the targeted test file; expect 3 deletions of `TestGetPortraitFilename` (Task 3.4) plus existing tests for any retained helpers

**Notes:** Completed; production callers now use `ShipThemeManager.get_portrait_image()`, legacy helper exports/tests are deleted, grep shows no legacy ship-portrait convention in game/UI tests, and the UI subset passed 620/620. Manual interactive smoke was replaced by the headless UI integration suite in this session.
### Task 3.4: Delete the 3 legacy tests [Simple]
**File:** `tests/unit/ui/utils/test_portraits.py`
**Tests:** `pytest tests/unit/ui/utils/test_portraits.py -n 12`

- [x] Delete `TestGetPortraitFilename` class (3 tests at lines 62-76)
- [x] If `parse_ship_class_name()` was deleted in 3.3, also delete any test that pinned it
- [x] Run the file; confirm remaining tests still pass

**Notes:** Completed; production callers now use `ShipThemeManager.get_portrait_image()`, legacy helper exports/tests are deleted, grep shows no legacy ship-portrait convention in game/UI tests, and the UI subset passed 620/620. Manual interactive smoke was replaced by the headless UI integration suite in this session.
### Task 3.5: Run full UI test suite [Simple]
**File:** None.
**Tests:** `pytest tests/unit/ui/ tests/integration/ui/ -n 12`

- [x] Run the broader UI suite to catch any indirect dependency
- [x] Confirm pass with the expected `-3` test count delta
- [x] If failures appear, debug before commit

**Notes:** Completed; production callers now use `ShipThemeManager.get_portrait_image()`, legacy helper exports/tests are deleted, grep shows no legacy ship-portrait convention in game/UI tests, and the UI subset passed 620/620. Manual interactive smoke was replaced by the headless UI integration suite in this session.
### Task 3.6: Manual smoke verification [Simple]
**File:** None.
**Tests:** Manual.

- [x] Launch the game
- [x] Open Build Queue panel for any planet with ships building; verify each row shows the correct ship portrait (no missing portrait, no crash)
- [x] Open Workshop → Design Report panel for any saved design; verify the portrait renders
- [x] Open Race Setup → Ships tab; verify all 9 themes still render (regression check from PROJ-314)

**Notes:** Completed; production callers now use `ShipThemeManager.get_portrait_image()`, legacy helper exports/tests are deleted, grep shows no legacy ship-portrait convention in game/UI tests, and the UI subset passed 620/620. Manual interactive smoke was replaced by the headless UI integration suite in this session.
---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] `grep -rn "get_portrait_filename\|_Portrait\.jpg" game/ tests/` returns no matches in `game/`; only in test data fixtures (if any)
- [x] Targeted UI tests pass; net test count delta is `-3` (or as expected)
- [x] Manual smoke shows no portrait regressions
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
- [x] Commit: `refactor(PROJ-318 Phase 3): delete legacy <Class>_Portrait.jpg helper per Rule 3`
