# BUG-32: Planet Filter Sliders Should Have Dynamic Min/Max Values

## Description
In the planets window - All of the sliders for filtering planets should have minimums and maximums based on the values of the planets, if the hottest planet is 576 kelvin and the coldest it 33 then the slider should go from 33 to 576. All of the sliders should be like that (mass, Gravity, and any new ones that get added).

## Priority
Low

## Status
Awaiting Confirmation

## Work Log
### 2026-01-23 - Fix Implemented
**Root Cause:** The planet list filter sliders (Gravity, Temperature, Mass) were created with hardcoded min/max limits (e.g., 0-10g, 0-2000K, 0-500 Earth masses) instead of calculating ranges from actual planet data in the galaxy.

**Solution:**
1. Added `_compute_planet_ranges()` method that iterates through all planets and calculates actual min/max values for gravity, temperature, and mass
2. Ranges include 5% padding for better usability
3. Updated `filter_ranges` initialization to use computed values
4. Updated slider creation to use dynamic ranges from `_planet_ranges`

**Files Modified:**
- `game/ui/screens/planet_list_window.py`:
  - Added `_compute_planet_ranges()` method (lines 183-232)
  - Modified `filter_ranges` initialization to use computed ranges (lines 38-44)
  - Updated slider creation to use dynamic ranges (lines 375-381)

**Testing:** All planet list tests pass. Manual testing required to confirm sliders show appropriate ranges based on galaxy data.
