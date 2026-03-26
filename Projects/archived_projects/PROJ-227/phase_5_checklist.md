# Phase 5: Consolidate Portrait Call Sites & Cleanup

## Task 5.1: Consolidate design_report_panel portrait placeholder [Simple]
**File:** `game/ui/panels/design_report_panel.py`
**Tests:** `pytest tests/ --testmon`
- [x] Import utilities from `game.ui.utils.portraits`
- [x] Replace inline placeholder generation with `create_placeholder_portrait`
- [x] Replace ship class parsing with `get_portrait_search_paths`
- [x] Run tests
**Notes:** Removed ~60 lines of inline portrait code. Removed unused `get_font` import and all SHIP_CLASS_* color imports. Now delegates to 3 shared functions.

## Task 5.2: Consolidate build_queue_portraits portrait loading [Simple]
**File:** `game/ui/panels/build_queue_portraits.py`
**Tests:** `pytest tests/ --testmon`
- [x] Import utilities from `game.ui.utils.portraits`
- [x] Replace inline ship class parsing and path construction with `get_portrait_search_paths`
- [x] Run tests
**Notes:** Removed ~10 lines of inline regex parsing and path construction. Removed unused `re` import.

## Task 5.3: Final full test suite [Simple]
- [x] Run: `pytest tests/ -n 12`
- [x] Verify no regressions from baseline (13470 passed)
**Notes:** 13513 passed, 2 skipped. 43 new tests added. Zero regressions.
