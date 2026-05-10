# BUG-72: Leader needs a name in Species Setup

## Description

Leader needs a name in Species Setup.

## Priority

**Medium** - Missing UI feature in species configuration.

## Status (Awaiting Confirmation)

## Work Log

### 2026-02-08 - Fix Applied

**Change:** Added `leader_name` text input field to the Species Setup Identity tab, placed between Leader Title dropdown and Society Type dropdown.

**Files Modified:**
- `game/strategy/data/race_config.py` — Added `leader_name: str = ""` field, added to `to_dict()` and `from_dict()` for serialization/deserialization
- `game/ui/panels/race_identity_panel.py` — Added `leader_name_input` (UITextEntryLine) in Government section after Leader Title. Synced in `update_config()` and `set_from_config()`.
- `tests/unit/strategy/data/test_race_config.py` — Added tests for default, custom identity, serialization round-trip, and backward compatibility
- `tests/unit/ui/panels/test_race_identity_panel.py` — Added 3 tests for leader_name_input (attribute exists, update_config reads it, set_from_config populates it)
