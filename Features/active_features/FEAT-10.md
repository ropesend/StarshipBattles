# FEAT-10: Add "Fleet Operations" filter tab to Event Log window

## Description
The Event Log window currently has filter tabs for All, Combat, Production, and Colonies. Fleet operation events (joins, redirects, cancellations) only appear under "All". Add a "Fleet Operations" tab so these events can be filtered independently.

[![Event Log showing only All, Combat, Production, Colonies tabs](../../Tools/qa_observer/session_data/20260324_163416/images/bug_capture_165340.png)](../../Tools/qa_observer/session_data/20260324_163416/images/bug_capture_165340.png)
*Current Event Log window — fleet operation events visible under "All" but no dedicated filter tab.*

The backend infrastructure is already complete:
- `EventCategory.FLEET_OPERATIONS` is defined in `game/strategy/events/event_types.py`
- Fleet events (`FLEET_JOINED`, `FLEET_JOIN_REDIRECTED`, `FLEET_JOIN_CANCELLED`) already use this category
- Data source filtering in `event_log_data_source.py` works generically for any category

### Implementation
1. Add a "Fleet Ops" button in `game/ui/screens/event_log_window.py:_create_filter_buttons()`
2. Add a category icon for `"fleet_operations"` in `game/ui/screens/event_log_data_source.py:CATEGORY_ICONS`

## Priority
Low

## Status
Awaiting Confirmation

## Analysis Report

### Architecture Impact
- **Pure UI-layer change** — no strategy, simulation, or core layer modifications needed
- Backend fully complete: `EventCategory.FLEET_OPERATIONS` defined, fleet events already categorized, facade queries generic
- Data flow: `FleetOrderProcessor`/`Fleet`/`Empire` → `EventLog` → `StrategySessionFacade` → `EventLogWindow` — all stages already handle fleet_operations
- No cross-layer dependencies introduced; no layer boundary violations

### Dependency Map
- **Files requiring changes:** 2 implementation + 2-4 test files
- **Blast radius:** Very small (~15-20 LOC implementation, ~30-50 LOC tests)
- `event_log_window.py:_create_filter_buttons()` — add button + dict entry
- `event_log_data_source.py:CATEGORY_ICONS` — add icon mapping
- Filter logic in `_recompute_filtered()` and `process_event()` is generic — works automatically with new buttons
- No regression risk: existing filters unaffected, all additions are purely additive

### Similar Patterns Found
- Existing buttons follow sequential creation pattern: `UIButton` → `x += FILTER_BTN_WIDTH + FILTER_GAP` → add to `self.filter_buttons` dict
- Layout math: 5 buttons × 100px + 4 gaps × 8px = 532px — well within 2560px minimum width
- CATEGORY_ICONS format: `"category_name": "[Abbrev]"` (e.g., `"combat": "[Combat]"`, `"production": "[Prod]"`)
- Button click handling iterates `filter_buttons` dict dynamically — no hardcoded category list

### Scope Assessment
- **Rating: Simple** — 2 files, single layer, existing patterns, <50 LOC total
- **Recommendation: Proceed as Feature** — not a project
- No new abstractions, patterns, or test infrastructure needed
- Estimated effort: 1-2 hours including tests

### Documentation Discrepancy Found
- `docs/systems/strategy_layer.md` lists EventCategory values but omits `FLEET_OPERATIONS` — needs update
- `EventLogWindow` class docstring mentions only 4 filter tabs — needs update after implementation

## Work Log
- 2026-03-24: Created from QA Session 20260324_163416.
- 2026-03-24: Deep dive analysis complete (Protocol 02b). 4 exploration agents confirmed: pure UI change, backend complete, Simple complexity rating.
- 2026-03-24: Implemented via TDD. Changes:
  - `game/ui/screens/event_log_window.py` — Added "Fleet Ops" filter button + dict entry
  - `game/ui/screens/event_log_data_source.py` — Added `"fleet_operations": "[FleetOps]"` to CATEGORY_ICONS
  - `docs/systems/strategy_layer.md` — Added missing FLEET_OPERATIONS to EventCategory enum docs
  - Updated docstrings in both files to include fleet_operations
  - Tests: Added fleet_operations event to sample data, 5 new test cases across both test files
  - All 111 event log tests pass (1 pre-existing failure in `_has_modal_open` unrelated)
