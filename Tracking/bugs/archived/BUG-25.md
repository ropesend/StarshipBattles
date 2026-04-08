# BUG-25: Build Queue category selection does not clear stale options

## Description
In the Build Queue and I select a catagory with 2 Available designs
And Tehn I select Ships which only has 1 option it does not eliminate the 2nds complex option.

## Status
Awaiting Confirmation

## Work Log

### 2026-01-18 - Phase 1: Analysis

**Root Cause:** When iterating over `self.items_scrollable.get_container().elements` to kill elements, the list was being modified during iteration, causing some elements to be skipped.

### 2026-01-18 - Phase 2: The Fix (Green)

**File Modified:** `game/ui/screens/build_queue_screen.py`

**Changes Made (lines 336-339):**
```python
# BUG-25: Copy list to avoid mutation during iteration
elements_to_kill = list(self.items_scrollable.get_container().elements)
for element in elements_to_kill:
    element.kill()
```

**Technical Approach:**
- Copy the elements list before iterating
- This ensures all elements are killed even as the original list is modified

**Test Results:**
```
======================= 18 passed (build queue tests) =======================
```

All tests pass with no regressions.
