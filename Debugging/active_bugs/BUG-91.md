# BUG-91: Missing planet portrait in build yard UI

## Description
The planet portrait view is missing/not rendering in the upper left corner of the build yard queue window. *Note: The code responsible for this panel should be largely the same code as the same panel in the strategy view when a planet is selected on the bottom right. Investigate why the image shows correctly in one and incorrectly in the other.*
- [![Screenshot](../../tools/qa_observer/session_data/20260228_104923/images/bug_capture_105405.png)](../../tools/qa_observer/session_data/20260228_104923/images/bug_capture_105405.png)

## Priority
Medium

## Status (Awaiting Confirmation)

## Work Log

### 2026-02-28 — Root Cause & Fix

**Root Cause:** Data flow break. `BuildQueueScreen` receives `portrait_surface` from `strategy_build_queue_manager.py`, but never forwards it to `BuildQueuePanelFactory`. The factory then hardcodes `portrait_surface=None` when creating `PlanetReportPanel`, leaving the portrait blank.

The strategy view works because `strategy_detail_formatter.py` passes the portrait directly to `PlanetReportPanel`.

**Fix Applied:**
1. `game/ui/screens/build_queue_panel_factory.py:69` — Added `portrait_surface` parameter to constructor
2. `game/ui/screens/build_queue_panel_factory.py:165` — Changed `portrait_surface=None` to `portrait_surface=self.portrait_surface`
3. `game/ui/screens/build_queue_screen.py:118` — Forwards `portrait_surface=self.portrait_surface` to factory

**Tests Added:**
- `test_portrait_surface_passed_to_panel_factory` in `test_build_queue_screen.py` — verifies factory accepts the parameter

**Full suite: 13,004 passed, 1 skipped, 0 failed.**
