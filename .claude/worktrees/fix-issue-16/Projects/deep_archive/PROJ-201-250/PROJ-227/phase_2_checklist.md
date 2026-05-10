# Phase 2: Consolidate Compact Number Call Sites

## Task 2.1: Replace planet_report_panel._format_compact_number [Simple]
**File:** `game/ui/panels/planet_report_panel.py`
**Tests:** `pytest tests/ --testmon`
- [x] Import `format_compact_number` from `game.ui.utils.formatters`
- [x] Replace `self._format_compact_number(...)` calls with `format_compact_number(...)`
- [x] Delete `_format_compact_number` method
- [x] Run tests
**Notes:** Also updated tests in test_planet_report_panel.py to test shared utility directly.

## Task 2.2: Replace empire_build_queue_formatter inline formatting [Simple]
**File:** `game/ui/screens/empire_build_queue_formatter.py`
**Tests:** `pytest tests/ --testmon`
- [x] Import `format_compact_number` from `game.ui.utils.formatters`
- [x] Replace inline K/M formatting with `format_compact_number(amount)`
- [x] Run tests
**Notes:** Removed 4 lines of inline formatting, replaced with single function call.

## Task 2.3: Replace planet_list_filters inline formatting [Simple]
**File:** `game/ui/screens/planet_list_filters.py`
**Tests:** `pytest tests/ --testmon`
- [x] Import `format_compact_number` from `game.ui.utils.formatters`
- [x] Replace inline K/M formatting with `format_compact_number(quantity)`
- [x] Run tests
**Notes:** Removed 5 lines of inline formatting.

## Task 2.4: Replace strategy_detail_fmt inline formatting [Simple]
**File:** `game/ui/screens/strategy_detail_fmt.py`
**Tests:** `pytest tests/ --testmon`
- [x] Import `format_compact_number` from `game.ui.utils.formatters`
- [x] Replace all inline K/M formatting (population, max_pop, species count)
- [x] Run tests
**Notes:** Replaced 3 inline formatting blocks (total_pop, max_pop, per-species count). Changed from uppercase "K" to lowercase "k" for consistency. Updated test assertion accordingly.

## Task 2.5: Run full regression [Simple]
- [x] Run: `pytest tests/ --testmon`
**Notes:** 35 affected tests, all passing.
