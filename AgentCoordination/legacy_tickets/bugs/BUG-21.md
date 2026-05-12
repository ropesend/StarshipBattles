# BUG-21: Build Queue Drag/Drop Leaves Stale Graphics

## Description
When dragging and dropping in the build queue window there are several cases of old graphics not being properly removed or drawn over.

## Status
Awaiting Confirmation

## Work Log
- 2026-01-18: Ticket created

### 2026-01-18 - Phase 1: Analysis

**Root Cause Identified:**
When an item is picked up from the queue and dropped **outside** the queue panel, the visual wasn't being refreshed. The item was removed from `planet.construction_queue` (line 691) and `_refresh_queue_display()` was called when picking up, but on drop outside, no refresh happened - leaving potential visual inconsistency.

### 2026-01-18 - Phase 2: The Fix (Green)

**File Modified:** `game/ui/screens/build_queue_screen.py`

**Changes Made (lines 707-731):**
```python
# Track if we need to refresh (item came from queue)
came_from_queue = self.dragged_item.get('source') == 'queue'

# ... on drop outside ...
if came_from_queue:
    self._refresh_queue_display()
```

**Technical Approach:**
1. Added `came_from_queue` flag to track item origin
2. On drop outside queue panel, if item originated from queue, call `_refresh_queue_display()` to ensure visual matches data state
3. This ensures the queue visual is always in sync with `planet.construction_queue` after any drag operation

**Test Results:**
```
======================== 5 passed in 1.47s ========================
```

All drag/drop tests pass with no regressions.
