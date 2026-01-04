---
### 📝 User Update 2026-01-03 15:33
BUG-04

Stats Panel:
Immediately after a resource storage component is added the stats panel shows a bunch of -- for the values, see this image: 
C:\Dev\Starship Battles\screenshots\screenshot_20260103_135415_322590_mouse_focus.png
---

## Work Log
*   [2026-01-03 16:05] **Phase 2 & 3: Fix & Verify**: Analyzed `ui/builder/right_panel.py` and found `on_ship_updated` returned early after `rebuild_stats`, preventing `update_stats_display` from running. Removed early returns to ensure updates always occur. Verified with `tests/repro_issues/test_bug_04_display.py` and regression tests.
