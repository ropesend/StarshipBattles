## Description
Please make the cornfirm refit dialog larger so that the full message can be seen without scrolling.
C:\Dev\Starship Battles\screenshots\screenshot_20260103_180741_820864_mouse_focus.png

## Status
[Fixed]

## Work Log
### 2026-01-03 19:35 - Phase 1: Reproduction
- **Test File:** `tests/repro_issues/test_bug_11_dialog_size.py`
- **Result:** CONFIRMED FAILURE
- **Assertion:** `assert has_scroll`
- **Analysis:** The `UIConfirmationDialog` size is hardcoded to `(400, 200)` in `builder_screen.py:622`. With the theme's font settings (Arial 14) and the multi-line message, the text exceeds the available view height of the internal `UITextBox`, forcing a vertical scrollbar.

### 2026-01-03 19:40 - Phase 2: Execution
- **Modification:** Changed `UIConfirmationDialog` dimensions in `game/ui/screens/builder_screen.py` from `(400, 200)` to `(600, 400)`.
- **Verification:** Ran `tests/repro_issues/test_bug_11_dialog_size.py`. Confirmed `has_scroll` is now `False`.
- **Conclusion:** Fix verified. Dialog is now large enough to show the refit message without scrolling.

Status updated to [Awaiting Confirmation].
