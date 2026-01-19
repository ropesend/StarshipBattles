# BUG-26: Overlapping planet drawn in System and Sector Report panels

## Description
Sometimes there is an overlapping planet drawn in the System ans Sector Report panels.

## Screenshots
- C:\Dev\Starship Battles\screenshots\screenshot_20260118_201346_101436_strategy_viewport.png
- C:\Dev\Starship Battles\screenshots\screenshot_20260118_201443_488200_strategy_viewport.png

## Status
Awaiting Confirmation

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
