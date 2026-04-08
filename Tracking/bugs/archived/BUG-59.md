# BUG-59: Game Setup + Race Setup Visual Theme Mismatch

## Description

Game Setup + Race Setup should follow the same visual themes as the strategy layer, and design workshop

## Priority
Medium

## Status
Awaiting Confirmation

## Work Log

### Fix Applied (2026-02-07)

**Root Cause:** The `MenuScene` (which hosts the NewGameSetupScreen and RaceSetupScreen as overlay windows) was creating its `UIManager` without loading `builder_theme.json`. The strategy layer and design workshop both load this theme, giving them a consistent dark blue/gray visual style. The menu scene used pygame_gui's default unstyled appearance.

**Changes:**

1. **`game/ui/screens/menu_scene.py`**:
   - Added `os` and `Paths` imports
   - Changed UIManager creation from plain `UIManager((width, height))` to load `builder_theme.json` from `Paths.DATA_DIR`, matching the strategy and workshop screens
   - Uses conditional loading with fallback to `None` if theme file doesn't exist

**Result:** Main menu, New Game Setup, and Race Setup screens now use the same dark blue/gray theme as the strategy layer and design workshop.

**Tests:** All 6519 tests pass.
