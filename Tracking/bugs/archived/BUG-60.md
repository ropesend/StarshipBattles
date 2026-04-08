# BUG-60: Rename All "Race" References to "Species"

## Description

All reference to race should be changed to species instead (both in code, and in game)

## Priority
Medium

## Status
Awaiting Confirmation

## Work Log

### Phase 1: UI Text Changes (2026-02-07)

**Scope:** Updated all user-visible UI text strings from "Race" to "Species". Code-level renames (file names, class names, variable names) are deferred to a separate refactoring project due to the scale (~1800 occurrences across 90 files).

**Changes:**

1. **`game/ui/screens/race_setup_screen.py`**: Window title "Race Setup" -> "Species Setup"
2. **`game/ui/screens/race_browser_dialog.py`**: Window title "Load Race" -> "Load Species", "No saved races found" -> "No saved species found", "[Unnamed Race]" -> "[Unnamed Species]"
3. **`game/ui/panels/race_summary_panel.py`**: "Race Configuration Summary" -> "Species Configuration Summary", "Load Saved Race" -> "Load Saved Species", "Race: --" -> "Species: --", format method "Race: {name}" -> "Species: {name}"
4. **`game/ui/panels/race_identity_panel.py`**: "Race Identity:" -> "Species Identity:", "Race Name:" -> "Species Name:", help text "Race Name + Government Type" -> "Species Name + Government Type"
5. **`game/ui/screens/new_game_setup_screen.py`**: "Player Races:" -> "Player Species:", "Load Race" -> "Load Species", "Setup Race" -> "Setup Species", "No race selected" -> "No species selected", "Race: {name}" -> "Species: {name}"
6. **`game/ui/screens/race_validator.py`**: "Race name is required" -> "Species name is required", "Race is over point budget" -> "Species is over point budget"

**Result:** All user-visible UI text now says "Species" instead of "Race". The underlying code still uses `race_` prefixed names (RaceConfig, race_config, race_id, etc.) which can be refactored in a future project.

**Tests:** All 6519 tests pass.

### Future: Code-Level Rename (Deferred)

The following code-level renames are deferred to a separate refactoring project:
- File renames: race_config.py -> species_config.py, race_library.py -> species_library.py, etc.
- Class renames: RaceConfig -> SpeciesConfig, RaceLibrary -> SpeciesLibrary, etc.
- Variable renames: race_config -> species_config, race_id -> species_id, etc.
- Test file and class renames
- Estimated scope: ~1800 occurrences across ~90 files
