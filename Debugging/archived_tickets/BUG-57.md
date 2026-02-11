# BUG-57: Race Setup Window Too Small

## Description

In the Race Setup, the window should be larger

## Priority
Low

## Status
Awaiting Confirmation

## Work Log

### Fix Applied (2026-02-07)

**Root Cause:** When opened from the New Game Setup screen, `RaceSetupScreen` was created at 1400x900, while the main menu version (app.py) already uses 1800x1200.

**Changes:**

1. **`game/ui/screens/new_game_setup_screen.py`** (line 429-430):
   - Changed `setup_width` from 1400 to 1800
   - Changed `setup_height` from 900 to 1200
   - Now matches the main menu race setup window size

**No test changes needed** - purely UI sizing.
