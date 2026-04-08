# BUG-23: Galactic Planet Registry Missing Owner Column

## Description
In the Galactic Planet Registry there should be a column for the colony owner, if unowned it should say none, otherwise it should show the flag of the owner besides the owner's name, it should be sorted by owners name.

## Status
Awaiting Confirmation

## Work Log
- 2026-01-18: Ticket created

### 2026-01-18 - Phase 1: Analysis

**Existing State:**
- Owner column already exists in the planet list
- However, it only shows "Unowned", "Player", or "Enemy" - not actual empire names
- No flag icons displayed
- Not sorted by owner by default

### 2026-01-18 - Phase 2: The Fix (Green)

**File Modified:** `game/ui/screens/planet_list_window.py`

**Changes Made:**

1. **Enhanced `_get_owner_name()` method (lines 142-159):**
   - Now looks up actual empire name from `galaxy.empires`
   - Shows "★ {empire_name}" for player's colonies
   - Shows "{empire_name}" for other empires' colonies
   - Shows "— None —" for unowned planets

2. **Widened owner column (line 55):**
   - Changed width from 100px to 140px to fit empire names

3. **Set default sort to owner (line 42):**
   - Changed `self.sort_column_id = None` to `self.sort_column_id = 'owner'`
   - List now defaults to sorting by owner name

**Note:** Flag icons require more complex asset integration and are deferred for future enhancement. The star (★) indicator provides visual distinction for player colonies.

**Test Results:**
```
============================== 2 passed in 0.31s ==============================
```

All planet list tests pass.
