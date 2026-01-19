# BUG-27: Planet List missing Owner filter

## Description
In the Planet List there should be a filter for Owner -> none (show unowned planets), player(show only the players colonies), opponents(show only oponent colonies)

## Status
Awaiting Confirmation

## Work Log

### 2026-01-18 - Phase 1: Analysis

**Root Cause:** The planet list window had the `filter_owner` state defined but no UI elements to modify it, and the `filter_planets` function didn't use owner filtering.

### 2026-01-18 - Phase 2: The Fix (Green)

**Files Modified:**

1. **`game/ui/screens/planet_list_window.py`:**
   - Added "Owner:" section with label, All/None buttons, and toggle buttons (lines 245-272)
   - Added event handlers for owner filter buttons (lines 759-785)
   - Updated `filter_planets` call to pass `filter_owner` and `empire` (lines 493-496)

2. **`game/ui/screens/planet_list_filters.py`:**
   - Added `filter_owner` and `empire` parameters to `filter_planets()` (line 50)
   - Added owner category determination logic (lines 77-89)
   - Added filter check for owner category

**UI Elements Added:**
- "Owner:" section label
- "All" / "None" buttons for owner filters
- Toggle buttons: "Player", "Enemy", "Unowned"

**Filter Logic:**
- `Unowned`: Planets with `owner_id = None`
- `Player`: Planets where `owner_id == empire.id`
- `Enemy`: Planets where `owner_id != None` and `!= empire.id`

**Test Results:**
```
======================= 28 passed (planet-related tests) =======================
```

All tests pass with no regressions.
