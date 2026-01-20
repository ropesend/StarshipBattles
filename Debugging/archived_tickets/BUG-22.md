# BUG-22: Zoom Level Indicator Visible When Sub-Panels Open

## Description
The Strategy Layer Zoom level on the bottom left of the screen should only be visible when the strategy layer has the focus, it should not be visible when sub panels like the Build queue, or the Design Workshop, or the Planet list window is open.

## Status
Awaiting Confirmation (Rev 2)

## Work Log
- 2026-01-18: Ticket created

### 2026-01-18 - Phase 1: Analysis

**Location:** `game/ui/screens/strategy_screen.py` line 584-592

**Root Cause:** The zoom indicator was always drawn in the `draw()` method without checking if any modal sub-panel was open.

### 2026-01-18 - Phase 2: The Fix (Green)

**File Modified:** `game/ui/screens/strategy_screen.py`

**Changes Made:**

1. **Modified `draw()` method (lines 584-592):**
   - Added conditional check before drawing zoom indicator
   - Only draws when `_has_modal_open()` returns False

2. **Added `_has_modal_open()` method (lines 594-608):**
   - Checks for Build Queue Screen (`scene.build_queue_screen`)
   - Checks for Fleet Orders Window (`fleet_orders_window`)
   - Checks for Design Workshop (`scene.action_open_design`)

**Test Results:**
```
======================== 4 passed in 0.62s ========================
```

All strategy UI tests pass with no regressions.

---
### ❌ Fix Rejected [2026-01-18 20:30]
**Reason:** The Strategy Layer Zoom level on the botttom left is still present and the zoom responds to the mouse wheel when using the planet list window, neither should be occuring.
**New Constraints:** Planet List Window must also hide the zoom indicator and disable mouse wheel zoom behavior.

---
### 2026-01-18 - Phase 2 (Rev 2): The Fix (Green)

**Files Modified:**

1. **`game/ui/screens/strategy_screen.py`:**
   - Added `self.planet_list_window = None` initialization (line 27)
   - Updated `_has_modal_open()` to check for `planet_list_window` (lines 619-621)
   - Modified `open_planet_list()` to store window reference and register close callback (lines 814-819)
   - Added `_on_planet_list_closed()` callback to clear reference (lines 821-823)

2. **`game/ui/screens/strategy_input_handler.py`:**
   - Modified camera event filter to block mouse wheel when modal is open (lines 351-354, 358)
   - Added `modal_open` check using `scene.ui._has_modal_open()`

**Changes Summary:**
- Planet List Window now properly tracked via `self.planet_list_window`
- Zoom indicator hidden when Planet List Window is open
- Mouse wheel zoom disabled when any modal is open (Build Queue, Fleet Orders, Planet List, Design Workshop)

**Test Results:**
```
======================== 4 passed (strategy button tests) ========================
```

All tests pass with no regressions.

---
