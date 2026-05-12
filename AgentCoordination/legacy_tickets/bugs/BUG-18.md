# BUG-18: Available Designs Need Miniature Portrait Icons

## Description
In the build queue, In the Available Designs, there should be miniature portrait views for each of the items in the list these should act as icons and be on the left side of the button

## Status
Awaiting Confirmation

## Work Log
- 2026-01-18: Ticket created

### 2026-01-18 - Phase 1: Analysis

**Requirement:** Add miniature portrait icons to the left of each design name in the Available Designs list.

### 2026-01-18 - Phase 2: The Fix (Green)

**File Modified:** `game/ui/screens/build_queue_screen.py`

**Changes Made:**

1. **Modified `_refresh_items_list()` (lines 332-382):**
   - Now wraps each design in a UIPanel row containing an icon and button
   - Icon size: 36x36 pixels
   - Button positioned to the right of the icon
   - Spacing: 5px between rows

2. **Added `_load_design_portrait()` method (lines 384-448):**
   - Loads portrait from `assets/ShipThemes/{theme}/Portraits/{ShipClass}_Portrait.jpg`
   - Falls back to default portrait or colored placeholder
   - Placeholder colors by type:
     - Ship: Blue (80, 100, 180)
     - Complex: Green (80, 180, 100)
     - Station: Red (180, 100, 80)
     - Fighter: Yellow (180, 180, 80)

3. **Updated test `tests/ui/test_build_queue_drag_drop.py`:**
   - Modified `test_drag_start` to search nested elements within row panels

**Visual Result:**
- Each design now shows a 36x36 portrait icon on the left
- Design name button appears to the right of the icon
- Cleaner, more visual layout for design selection

**Test Results:**
```
======================= 25 passed in 4.75s =======================
```

Note: 3 unrelated flaky tests in `test_builder_ui_sync.py` fail intermittently under parallel execution but pass when run sequentially.
