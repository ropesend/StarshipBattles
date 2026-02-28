# BUG-90: Incorrect atmosphere coloring in planet details box

## Description
Atmosphere gas composition colors appear uniform for some planet types instead of reflecting distinct gases (e.g., Ice Dwarfs correctly show varied colors, but other planets do not). *Note: This may be related to whether the planet is a colony or not, but the exact cause is uncertain.*
- [![Screenshot](../../tools/qa_observer/session_data/20260228_104923/images/bug_capture_105301.png)](../../tools/qa_observer/session_data/20260228_104923/images/bug_capture_105301.png) - Shows incorrect uniform atmosphere color on a colony planet.
- [![Screenshot](../../tools/qa_observer/session_data/20260228_104923/images/bug_capture_105330.png)](../../tools/qa_observer/session_data/20260228_104923/images/bug_capture_105330.png) - Shows correct varied atmosphere colors on an Ice Dwarf.
- [![Screenshot](../../tools/qa_observer/session_data/20260228_104923/images/bug_capture_105428.png)](../../tools/qa_observer/session_data/20260228_104923/images/bug_capture_105428.png) - Close-up highlighting the incorrect atmosphere coloration on an image from in the build queue window.

## Priority
Medium

## Status (Awaiting Confirmation)

## Work Log

### 2026-02-28 — Root Cause & Fix

**Root Cause:** Data naming mismatch. Homeworld/colony atmospheres were set using full gas names ("Oxygen", "Nitrogen") from `atmosphere_preferences`, but the `AtmosphereGraph` UI maps colors by chemical formulas ("O2", "N2"). Full names fell through to `GAS_UNKNOWN` (uniform color).

- `_adjust_homeworld_to_race()` in `game_initializer.py` copied preference keys (full names) directly into `planet.atmosphere`
- `superweapon_order_processor.py` (Dyson Sphere creation) had the same issue
- `habitability.py` also had a lookup mismatch between formula-keyed atmospheres and name-keyed preferences

**Fix Applied:**
1. Added `GAS_NAME_TO_FORMULA` and `GAS_FORMULA_TO_NAME` mappings to `game/strategy/data/race_config.py`
2. `game/strategy/engine/game_initializer.py:228` — translates gas names to formulas when setting `planet.atmosphere`
3. `game/strategy/engine/superweapon_order_processor.py:503` — same translation for Dyson Sphere atmosphere
4. `game/strategy/formulas/habitability.py:152` — reverse-translates formula keys to match display-name preferences

**Tests Added:**
- `test_adjust_homeworld_translates_gas_names_to_formulas` in `test_game_initializer.py`
- `test_formula_keys_match_display_name_preferences` in `test_habitability.py`
- `test_formula_keys_toxic_match` in `test_habitability.py`
- Updated Dyson Sphere test to expect chemical formula keys

**Full suite: 13,003 passed, 1 skipped, 0 failed.**
