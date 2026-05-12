# BUG-16: Atmosphere Raw Data Button Mispositioned

## Description
The button to go to the Raw Data for the atmosphere is in the wrong place, it should be in the upper right of the box that contains the graph of the atmosphere data, but instead it is in the upper left of the entire planet detail panel

## Status
Awaiting Confirmation

## Work Log
- 2026-01-18: Ticket created

### 2026-01-18 - Phase 1: Reproduction (Red)

**Test File Created:** `tests/repro_issues/test_bug_16_raw_data_button.py`

**Root Cause Identified:**
In `game/ui/screens/strategy_screen.py`, the Raw Data button was initialized with position `(0, 0)`:
```python
# BUGGY CODE (line 139-140):
self.btn_raw_data = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(0, 0, 20, 20),  # <-- Wrong: top-left of panel
    ...
)
```

The button only got repositioned during `handle_resize()`, but not during initial construction.

### 2026-01-18 - Phase 2: The Fix (Green)

**File Modified:** `game/ui/screens/strategy_screen.py`

**Changes Made (lines 133-139):**
```python
# FIXED CODE:
# Raw Data Button (Top Right of Graph Box)
btn_x = self.graph_rect.right - 22  # Inside right edge of graph
btn_y = self.graph_rect.top + 2     # Inside top edge of graph

self.btn_raw_data = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(btn_x, btn_y, 20, 20),  # Correct position from start
    ...
)
```

**Technical Approach:**
- Calculate button position based on `graph_rect` during initialization
- Position is now `(138, 172)` instead of `(0, 0)` for standard layout
- Button appears in top-right of the atmosphere/spectrum graph box

**Test Results:**
```
========================= 2 passed in 1.33s =========================
```

**Regression Tests:**
```
===================== 1421 passed, 401 warnings in 12.04s =====================
```

All tests pass with no regressions.
