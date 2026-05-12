# BUG-56: New Game Setup - Star System Count Selector

## Description

In the New Game Setup, I need to be able to select number of star systems in the starting galaxy should be 25 to 150 (can be a slider)

## Priority
Medium

## Status
Awaiting Confirmation

## Work Log

### Fix Applied (2026-02-07)

**Root Cause:** No UI control existed for selecting star system count. `GameConfig.system_count` defaulted to 25.

**Changes:**

1. **`game/ui/screens/new_game_setup_screen.py`**:
   - Added `UIHorizontalSlider` (range 25-150, default 50, click_increment=5) between Galaxy Type dropdown and Player Races section
   - Added value label showing current slider value
   - Added `UI_HORIZONTAL_SLIDER_MOVED` event handler to update `self.system_count` and label text
   - Updated `build_game_config()` to accept and pass `system_count` parameter
   - Updated `_on_start_clicked()` to pass `self.system_count` through to config builder

**Result:** Slider value flows through to `GameConfig.system_count`, controlling galaxy generation.

**Tests:** All 13 new game setup tests pass.
