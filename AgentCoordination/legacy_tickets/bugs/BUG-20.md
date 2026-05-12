# BUG-20: Build Queue Items Need Miniature Portrait Icons

## Description
In the actual build queue there should be miniature portrait views of the item in the queue on the left side of the line.

## Status
Awaiting Confirmation

## Work Log
- 2026-01-18: Ticket created

### 2026-01-18 - Phase 1: Analysis

**Requirement:** Add miniature portrait icons to the left of each item in the Build Queue display (not Available Designs - that was BUG-18).

### 2026-01-18 - Phase 2: The Fix (Green)

**File Modified:** `game/ui/screens/build_queue_screen.py`

**Changes Made:**

1. **Modified `_refresh_queue_display()` (lines 450-516):**
   - Added portrait icon size constant: 50x50 pixels
   - Loads portrait using new `_load_queue_item_portrait()` method
   - Displays icon on left side of panel (5, 5)
   - Shifted design name and turns labels to right of icon

2. **Added `_load_queue_item_portrait()` method (lines 518-551):**
   - Looks up design metadata by design_id from design library
   - If found, delegates to `_load_design_portrait()` for proper portrait
   - Fallback: Creates colored placeholder based on item type
   - Color scheme matches BUG-18 implementation

**Visual Result:**
- Each queue item now shows a 50x50 portrait icon on the left
- Design name and turns remaining appear to the right of the icon
- Provides visual consistency with Available Designs list (BUG-18)

**Test Results:**
```
======================= 18 passed in 4.57s =======================
```

All build queue tests pass with no regressions.
