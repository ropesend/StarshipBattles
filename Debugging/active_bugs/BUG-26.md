# BUG-26: Overlapping planet drawn in System and Sector Report panels

## Description
Sometimes there is an overlapping planet drawn in the System ans Sector Report panels.

## Screenshots
- C:\Dev\Starship Battles\screenshots\screenshot_20260118_201346_101436_strategy_viewport.png
- C:\Dev\Starship Battles\screenshots\screenshot_20260118_201443_488200_strategy_viewport.png

## Status
Awaiting Confirmation (Rev 2)

## Work Log

### 2026-01-18 - Phase 1: Analysis

**Root Cause:** Same issue as BUG-25 - when iterating over `self.items` to call `kill()` on each element, the list was being modified during iteration, causing some items to be skipped and leaving "ghost" elements visible.

### 2026-01-18 - Phase 2: The Fix (Green)

**File Modified:** `game/ui/panels/system_tree_panel.py`

**Changes Made (lines 145-148):**
```python
# BUG-26: Copy list to avoid mutation during iteration
items_to_kill = list(self.items)
for item in items_to_kill:
    item.kill()
```

**Technical Approach:**
- Copy the items list before iterating
- This ensures all items are properly killed when refreshing the tree panel

**Test Results:**
```
156 passed (strategy tests)
```

All tests pass with no regressions.

---
### ❌ Fix Rejected [2026-01-18 21:25]
**Reason:** There are still overlaping graphical elements in the system View At times, it doesn't always happen.
**New Constraints:** Intermittent issue - see screenshot: C:\Dev\Starship Battles\screenshots\screenshot_20260118_212112_372169_strategy_viewport.png
---
### 2026-01-18 - Phase 2 (Rev 2): The Fix (Green)

**Root Cause Analysis:** The same list mutation during iteration bug existed in multiple locations:
1. `planet_report_panel.py:_update_complexes_list()` - iterating `self.complex_items` while calling `kill()`
2. `build_queue_screen.py:_refresh_queue_display()` - iterating `elements` while calling `kill()`

Both of these can cause intermittent ghost elements when the underlying list is modified during iteration.

**Files Modified:**
1. `game/ui/panels/planet_report_panel.py`
2. `game/ui/screens/build_queue_screen.py`

**Changes Made:**

1. **planet_report_panel.py (lines 192-195):**
```python
# Clear existing items - copy list to avoid mutation during iteration (BUG-26)
items_to_kill = list(self.complex_items)
for item in items_to_kill:
    item.kill()
```

2. **build_queue_screen.py (lines 455-458):**
```python
# Clear existing queue items - copy list to avoid mutation during iteration (BUG-26)
elements_to_kill = list(self.queue_scrollable.get_container().elements)
for element in elements_to_kill:
    element.kill()
```

**Technical Approach:**
- Copy lists before iterating and calling `kill()` to prevent mutation during iteration
- This ensures all elements are properly killed without skipping any

**Test Results:**
```
223 passed (strategy and build queue tests)
```

All tests pass with no regressions.

---
