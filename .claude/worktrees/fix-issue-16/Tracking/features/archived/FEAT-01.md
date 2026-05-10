## Description
For a new game setup, the save name field should automatically pre-populate with "save game" appended with the current timestamp.

## Priority
High

## Status
Awaiting Confirmation

## Work Log
- 2026-02-28: Feature created from QA session log.
- 2026-02-28: Implemented pre-populated save name.
  - **Analysis:** Clean implementation — only two changes needed in `NewGameSetupScreen`.
  - **Test (Red):** Added `TestNewGameSetupDefaultSaveName` class with 3 tests: prefix check, timestamp pattern check, validation pass-through.
  - **Implementation (Green):** Added `generate_default_save_name()` static method returning `"save game YYYY-MM-DD HHMM"` format. Called `set_text()` on the input after creation.
  - **Design note:** Timestamp uses `HHMM` format (no colon) because colons are invalid filesystem characters rejected by save name validation.
  - **Files modified:**
    - `game/ui/screens/new_game_setup_screen.py` — Added `datetime` import, `generate_default_save_name()` static method, and `set_text()` call in `_create_ui()`.
    - `tests/unit/ui/test_new_game_setup.py` — Added `TestNewGameSetupDefaultSaveName` class (3 tests).
  - **Regression:** 12,912 passed, 0 failures.
