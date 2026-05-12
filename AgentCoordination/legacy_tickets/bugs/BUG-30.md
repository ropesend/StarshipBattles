# BUG-30: Load Game buttons non-functional

## Description
When Loading a game, I'm unable to Load, show turns, or Delete the game. I can only cancel.

**Screenshot:**
![Load Game Dialog](../../screenshots/2026-01-20%2007-38-48.png)

The screenshot shows the Load Game dialog with a save selected ("Terran_Command_20260118_074141 - Turn 1"), but the Load, Show Turns, and Delete buttons appear to be non-responsive. Only Cancel works.

## Status
Awaiting Confirmation

## Work Log
- 2026-01-20: Ticket created from user report.
- 2026-01-20: Root cause identified: In `_handle_selection_change()`, the code incorrectly accessed `item.text` (dot notation) when `UISelectionList.item_list` returns dictionaries with a `"text"` key. The `hasattr(item, 'text')` check returned False for dicts, causing `str(item)` to convert the entire dictionary to a string, which never matched the `selected_item` text.
- 2026-01-20: Fix applied in [save_selection_window.py](../../game/ui/screens/save_selection_window.py) line 230: Changed from `hasattr(item, 'text')` pattern to `item["text"] if isinstance(item, dict)`.
- 2026-01-20: Added regression test `test_buttons_enable_after_selection` in `tests/unit/ui/test_save_selection.py` - all 11 tests pass.
