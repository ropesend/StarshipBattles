# BUG-15: Screenshot System Strategy Layer Support

## Description
Modify the integrated Screenshot system so that it works with the strategy_layer, and all sub windows.

## Status
In-Progress

## Work Log

### 2026-01-18 - Phase 1: Reproduction (Red)

**Test File Created:** `tests/repro_issues/test_bug_15_screenshot_strategy.py`

**Test Cases:**
1. `test_capture_galaxy_viewport_region` - Capture viewport excluding sidebar/top bar (PASSED - existing functionality)
2. `test_capture_subwindow_surface` - Capture arbitrary sub-window surface (PASSED - existing functionality)
3. `test_capture_strategy_layer_method_exists` - New method required (FAILED)
4. `test_capture_strategy_layer_renders_all_layers` - Capture full strategy scene (SKIPPED - awaiting method)
5. `test_capture_strategy_layer_viewport_only` - Capture viewport-only via new method (SKIPPED - awaiting method)

**Failing Test Output:**
```
FAILED tests/repro_issues/test_bug_15_screenshot_strategy.py::TestScreenshotStrategyLayerSupport::test_capture_strategy_layer_method_exists
AssertionError: False is not true : ScreenshotManager should have a capture_strategy_layer() method

=================== 1 failed, 2 passed, 2 skipped in 1.78s ====================
```

**Analysis:**
- Existing `capture()` method works for basic region/surface capture
- Missing: `capture_strategy_layer()` method that understands strategy scene layering
- Required parameters:
  - `scene`: StrategyScene instance
  - `include_ui`: Whether to include UI panels (default True)
  - `include_subwindows`: Whether to include modal windows (default True)
  - `label`: Optional filename label

---

### 2026-01-18 - Phase 2: The Fix (Green)

**File Modified:** `game/core/screenshot_manager.py`

**Implementation:**
Added `capture_strategy_layer()` method (lines 143-204) with the following capabilities:

1. **Full Screen Capture (`include_ui=True`):**
   - Creates temporary surface at scene dimensions
   - Renders galaxy map via `scene._renderer.draw()`
   - Renders UI layer via `scene.ui.draw()` if available
   - Renders active sub-windows (e.g., `build_queue_screen`) if `include_subwindows=True`

2. **Viewport-Only Capture (`include_ui=False`):**
   - Calculates viewport dimensions (excluding sidebar and top bar)
   - Renders full scene to temporary surface
   - Blits only the viewport region to capture surface

**Test Results:**
```
============================== 5 passed in 1.49s ==============================
```

**Regression Tests:**
```
tests/unit/test_screenshot_manager.py - 3 passed
```

**Usage Example:**
```python
from game.core.screenshot_manager import ScreenshotManager

sm = ScreenshotManager.instance()

# Capture full strategy screen with UI and sub-windows
sm.capture_strategy_layer(strategy_scene, label="full_view")

# Capture galaxy viewport only (no UI)
sm.capture_strategy_layer(strategy_scene, include_ui=False, label="galaxy_only")

# Capture with UI but without modal sub-windows
sm.capture_strategy_layer(strategy_scene, include_subwindows=False, label="no_modals")
```

---
### ❌ Fix Rejected [2026-01-18 17:45]
**Reason:** The screenshot system dows not appear to work in the strategy layer, no signs of teh screenshot image showing up, and no path to the file theat I can paste.
**New Constraints:** None provided
---
