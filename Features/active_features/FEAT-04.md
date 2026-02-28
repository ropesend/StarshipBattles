## Description

**Category:** Feature
**Title:** Event Log 'Go To Location' Navigation
**Description:** Enhance the Event Log by adding clickable links or double-click functionality to event entries. Interacting with an event (e.g., production completion, combat, colony events) should automatically move the camera to the corresponding location on the map. The log should include a column specifying the exact location. For events that correspond only to a star system generally, navigating should select the center of that star system.
**Screenshot:**
[![Screenshot](c:\Developer\StarshipBattles\tools\qa_observer\session_data\20260228_125515\images\bug_capture_125820.png)](c:\Developer\StarshipBattles\tools\qa_observer\session_data\20260228_125515\images\bug_capture_125820.png)
*Screenshot demonstrates the Event Log UI panel where click-to-navigate functionality should be added to the event rows.*

## Priority
Medium

## Status (Awaiting Confirmation)

## Work Log

### Implementation [2026-02-28]

**Approach:** Added location data to all game events at creation time, added a Location column to the event log table, and implemented double-click-to-navigate functionality.

**Changes by layer:**

**Strategy Layer — Event Location Data:**
- `game/strategy/engine/production_engine.py` — Added `location_hex=[q,r]` and `location_name` to all 4 `log_event()` calls (planet ship, planet complex, fleet ship, fleet complex). Added `galaxy` parameter to `_spawn_complex()` for global hex resolution.
- `game/strategy/engine/conflict_resolution_engine.py` — Added `location_hex` to both combat resolution `log_event()` calls (RNG and simulated).
- `game/strategy/engine/fleet_order_processor.py` — Added `location_hex` and `location_name` to colony founded `log_event()`.
- `game/strategy/engine/superweapon_order_processor.py` — Added `location_hex` to `_finalize_superweapon()`, `star_destroyed`, and `ships_self_destructed` events. Captures fleet location before fleet may be consumed.

**UI Layer — Location Column:**
- `game/ui/screens/event_log_data_source.py` — Added `location` column (150px) to `EVENT_LOG_COLUMNS`. Added `get_cell_value` handling that shows `location_name` from details, with fallback to formatted hex coords `(q, r)`.

**UI Layer — Double-Click Navigation:**
- `game/ui/screens/event_log_window.py` — Added `on_navigate_callback` parameter. Implemented double-click detection (400ms threshold) on table rows via `process_event()`. Added `_handle_row_navigate()` that extracts `location_hex` from event details and calls the callback.
- `game/ui/screens/strategy_window_manager.py` — Passes `on_navigate_callback` when creating EventLogWindow. Callback closes the event log window and navigates camera to the hex coordinate.

**Camera Navigation:**
- `game/ui/screens/strategy_camera_nav.py` — Added `center_on_hex(hex_coord)` method for direct hex coordinate navigation (used by the event log navigate callback).

**Tests:**
- `tests/unit/ui/screens/test_event_log_data_source.py` — 5 new tests for location column (definition, cell values, fallback).
- `tests/unit/ui/screens/test_event_log_window.py` — 5 new tests for navigation (callback storage, constructor param, navigate behavior, no-callback safety, no-location safety).
- `tests/unit/ui/screens/test_camera_navigator.py` — 3 new tests for `center_on_hex`.
- `tests/unit/strategy/test_engine_event_emission.py` — Updated 2 existing mocks with `.location` attribute, added `location_hex` assertion.

**Test Results:** 13,035 passed, 0 failed, 1 skipped.
