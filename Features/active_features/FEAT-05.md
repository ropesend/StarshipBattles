## Description
Modifying an existing, loaded species and saving/updating it should prompt a dialog giving the option to either overwrite the old species or save as a new species.

## Priority
Medium

## Status
Awaiting Confirmation

## Work Log
- 2026-02-28: Feature created from QA Triage Session 20260228_143536.
- 2026-03-14: **Implemented.** Added save/update dialog to species setup workflow.
  - **Phase 0:** Reviewed `race_setup_screen.py`, `race_library.py`, and `docs/` — no conflicts. Existing save flow: `_on_save()` → `race_library.save_race()` which overwrites if `race_id` exists or generates new `race_id` if not.
  - **Phase 1:** Identified integration points: `_on_save()` method, `process_event()` handler, `is_editing` flag.
  - **Phase 2:** Added 5 tests in `TestSaveUpdateDialog`: new species saves directly, editing shows dialog, overwrite preserves race_id, save-as-new clears race_id, cancel doesn't save.
  - **Phase 3:** Implementation:
    - Modified `_on_save()` to detect `is_editing` + existing `race_id` and show dialog instead of saving directly
    - Extracted `_do_save()` for the actual save logic (called by both paths)
    - Added `_show_save_update_dialog()` — creates a `UIWindow` with "Overwrite", "Save as New", and "Cancel" buttons
    - Added `_on_overwrite_save()` — keeps `race_id`, saves, closes dialog
    - Added `_on_save_as_new()` — clears `race_id` and `is_editing`, reverts button text to "Save", saves with fresh ID
    - Added `_on_save_dialog_cancel()` — closes dialog without saving
    - Added dialog button handling in `process_event()` (checked before other buttons)
  - **Files modified:** `game/ui/screens/race_setup_screen.py`, `tests/unit/ui/screens/test_race_setup_screen.py`
  - **Tests:** 32/32 race setup screen tests pass. 13179/13179 full suite passes.
