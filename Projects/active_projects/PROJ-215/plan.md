# PROJ-215: Fix Event Log Location Display and Navigation

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-215` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-215 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Expand Event Columns & Data Source | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Enrich Event Location Data at Creation | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Add Sidebar with Column Toggles | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Fix Double-Click Navigation | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Add Storm Column | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-28
**Active Phase:** Phase 4
**Last Action:** Phase 3 complete - EventLogSidebar with column toggles integrated into EventLogWindow
**Next Action:** Phase 4 - Fix double-click navigation
**Blockers:** None

## Overview
The Event Log window has two bugs and missing features: (1) The "Location" column shows only planet names without system context, (2) double-clicking an event row doesn't navigate the camera to the event location. Additionally, the user wants the single Location column replaced with multiple granular columns (System, Planet, Local Hex, Galaxy Hex, Storm) and a sidebar for column visibility toggles.

## Goals
- Replace the single "Location" column with granular location columns: System, Planet, Local Hex, Galaxy Hex
- Add a "Storm" column showing storm names at event locations
- Add a sidebar panel with column visibility toggles (matching FleetReport/PlanetList pattern)
- Fix double-click navigation so clicking an event row navigates the camera to that hex
- Enrich event data at creation time so all location fields are populated

## Scope
**In:**
- Event log column expansion (system, planet, local hex, galaxy hex, storm)
- EventLogDataSource updates to extract new column data
- Sidebar with column toggle checkboxes
- Enriching event creation sites with system name and storm data
- Facade query method for storm info at a hex
- Fixing double-click navigation
- Tests for all changes

**Out:**
- Column sorting by new columns (existing sort infrastructure handles this automatically)
- Column reordering (already supported by TableColumnManager/TableHeader)
- Environmental hazard events in the event log (separate feature)
- Persistence of column visibility preferences across sessions

## Key Files
| Component | File Path |
|-----------|-----------|
| Event Log Data Source | `game/ui/screens/event_log_data_source.py` |
| Event Log Window | `game/ui/screens/event_log_window.py` |
| Window Manager (navigate callback) | `game/ui/screens/strategy_window_manager.py` |
| Camera Navigator | `game/ui/screens/strategy_camera_nav.py` |
| Event Model | `game/strategy/events/event_log.py` |
| Production Engine (events) | `game/strategy/engine/production_engine.py` |
| Conflict Resolution Engine (events) | `game/strategy/engine/conflict_resolution_engine.py` |
| Fleet Order Processor (events) | `game/strategy/engine/fleet_order_processor.py` |
| Strategy Session Facade | `game/strategy/facade/strategy_session_facade.py` |
| Area Effect Manager | `game/strategy/services/area_effect_manager.py` |
| Column Manager | `game/ui/components/table/column_manager.py` |
| VirtualTable | `game/ui/components/table/virtual_table.py` |
| Fleet Report Sidebar (reference) | `game/ui/screens/fleet_report_sidebar.py` |
| Data Source Tests | `tests/unit/ui/screens/test_event_log_data_source.py` |
| Window Tests | `tests/unit/ui/screens/test_event_log_window.py` |
| Triage Finding | `findings/event_log_navigation.md` |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-28 | Replace single Location column with System, Planet, Local Hex, Galaxy Hex columns | User wants granular location data with column toggles |
| 2026-02-28 | Add Storm column showing storm names at event hex | User wants environmental context visible |
| 2026-02-28 | Use sidebar for column toggles (match FleetReport/PlanetList) | Established pattern in codebase |
| 2026-02-28 | All three workstreams in scope | User confirmed full solution |
| 2026-02-28 | Enrich events at creation time (not lazy UI lookup) | Events persist in save data; enriching at creation ensures data is always available without galaxy reference at render time |
| 2026-02-28 | Use facade `get_system_at_hex()` / `get_system_near_hex()` for system resolution | Already exists, returns SystemInfo DTO |

## Initial Analysis

### Current Location Column Logic
`event_log_data_source.py:94-102` — shows `details.location_name` (planet name) or falls back to `(q, r)` hex coords. No system name context.

### Event Details Fields (current)
- `location_name`: Planet name (set by production/colony events, NOT set by combat events)
- `location_hex`: `[q, r]` global hex coordinates (set by all events with location)

### Navigation Wiring
- `event_log_window.py:253-273`: Double-click detection implemented
- `strategy_window_manager.py:240-255`: Navigate callback calls `_camera_nav.center_on_hex()`
- The code looks correctly wired — need to verify if the issue is that `find_clicked_row()` returns -1 due to coordinate space mismatch or if `_camera_nav` attribute doesn't exist on the scene

### Column Toggle Infrastructure
- `TableColumnManager.toggle_column()` — already exists and tested
- `TableColumnManager.get_toggleable_columns()` — filters image columns
- `FleetReportSidebar._build_column_section()` — reference pattern at lines 347-375
- `VirtualTable.rebuild_row_pool()` + `rebuild_headers()` — handles visibility changes

### Area Effect Access
- `AreaEffectManager.get_effects_at_global_hex(galaxy, hex)` returns `EnvironmentalEffects` with `storm_names: List[str]`
- Facade has NO storm query method yet — need to add one
- ConflictResolutionEngine already HAS `_area_effect_manager` and `_galaxy`
- ProductionEngine and FleetOrderProcessor do NOT have area_effect_manager access

---

## Phases

### Phase 1: Expand Event Columns & Data Source [Medium]
**Objective:** Replace the single "Location" column with four granular columns and update the data source to extract values from event details.

#### Task 1.1: Update EVENT_LOG_COLUMNS definition [Simple]
**File:** `game/ui/screens/event_log_data_source.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_data_source.py`
- [ ] Remove the `"location"` column entry (line 16)
- [ ] Add new column: `{"id": "system", "width": 120, "title": "System", "visible": True, "sortable": True}`
- [ ] Add new column: `{"id": "planet", "width": 120, "title": "Planet", "visible": True, "sortable": True}`
- [ ] Add new column: `{"id": "local_hex", "width": 80, "title": "Local Hex", "visible": False, "sortable": True}`
- [ ] Add new column: `{"id": "galaxy_hex", "width": 80, "title": "Galaxy Hex", "visible": False, "sortable": True}`
- [ ] Verify column count is now 7 (category, turn, system, planet, local_hex, galaxy_hex, message)
**Notes:** Local Hex and Galaxy Hex default to hidden (visible=False) since most users want system/planet.

#### Task 1.2: Update get_cell_value() for new columns [Simple]
**File:** `game/ui/screens/event_log_data_source.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_data_source.py`
- [ ] Replace the `if column_id == "location":` block (lines 94-102) with new column handlers:
  ```python
  if column_id == "system":
      return event.get("details", {}).get("system_name", "")

  if column_id == "planet":
      return event.get("details", {}).get("location_name", "")

  if column_id == "local_hex":
      details = event.get("details", {})
      local = details.get("local_hex")
      if local and len(local) == 2:
          return f"({local[0]}, {local[1]})"
      return ""

  if column_id == "galaxy_hex":
      details = event.get("details", {})
      hex_coords = details.get("location_hex")
      if hex_coords and len(hex_coords) == 2:
          return f"({hex_coords[0]}, {hex_coords[1]})"
      return ""
  ```
**Notes:** `system_name` and `local_hex` are new fields we'll add to event details in Phase 2.

#### Task 1.3: Update data source tests [Medium]
**File:** `tests/unit/ui/screens/test_event_log_data_source.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_data_source.py`
- [ ] Update `test_column_count_includes_location` → rename to `test_column_count` and assert 7 columns
- [ ] Update `test_location_column_definition` → replace with tests for system, planet, local_hex, galaxy_hex columns
- [ ] Replace `test_location_cell_value_from_details` with `test_system_cell_value` — event with `details={"system_name": "Lincoln"}` → returns `"Lincoln"`
- [ ] Replace `test_location_cell_value_empty_when_no_location` with `test_system_cell_value_empty` — event with `details={}` → returns `""`
- [ ] Replace `test_location_cell_value_hex_fallback` with `test_planet_cell_value` — event with `details={"location_name": "Lincoln I"}` → returns `"Lincoln I"`
- [ ] Add `test_local_hex_cell_value` — event with `details={"local_hex": [2, -1]}` → returns `"(2, -1)"`
- [ ] Add `test_local_hex_cell_value_empty` — event with `details={}` → returns `""`
- [ ] Add `test_galaxy_hex_cell_value` — event with `details={"location_hex": [5, 3]}` → returns `"(5, 3)"`
- [ ] Add `test_galaxy_hex_cell_value_empty` — event with `details={}` → returns `""`
- [ ] Run tests, verify all pass

---

### Phase 2: Enrich Event Location Data at Creation [Medium]
**Objective:** Add `system_name` and `local_hex` fields to all event creation sites so the new columns have data.

#### Task 2.1: Enrich production events (planet-based) [Simple]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_production_engine.py`
- [ ] In `_spawn_complex()` (lines 560-577): After computing `location_hex`, also store `system_name` from `parent_sys.name` and `local_hex` from `[planet.location.q, planet.location.r]`:
  ```python
  system_name = parent_sys.name if parent_sys else ""
  local_hex = [planet.location.q, planet.location.r]
  ```
  Add `system_name=system_name, local_hex=local_hex` to the `log_event()` call
- [ ] In `_spawn_ship()` (lines 596-647): Same pattern — extract `parent_sys.name` and `planet.location` coords, add to `log_event()` call (line 637)
- [ ] In `_spawn_fleet_ship()` — fleet-based production has no planet/system context readily. Add `system_name=""` and `local_hex=None` (fleet in deep space has no local hex)
- [ ] In `_build_fleet_yard_complex()` — similar to `_spawn_complex()`, add system/local hex if galaxy available

#### Task 2.2: Enrich combat events [Simple]
**File:** `game/strategy/engine/conflict_resolution_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_conflict_resolution_engine.py`
- [ ] In RNG combat event (lines 206-214): Look up system from fleet location:
  ```python
  system_name = ""
  if self._galaxy:
      sys = self._galaxy.get_system_at_location(f1.location)
      if sys:
          system_name = sys.name
  ```
  Add `system_name=system_name` to `log_event()`. Combat events don't have a specific planet, so no `location_name` or `local_hex`.
- [ ] In simulated combat event (lines 267-275): Same system lookup pattern, add `system_name=system_name`

#### Task 2.3: Enrich colonization events [Simple]
**File:** `game/strategy/engine/fleet_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_fleet_order_processor.py`
- [ ] In `_execute_colonize_order()` (lines 220-230): Add system lookup:
  ```python
  system_name = ""
  local_hex = None
  if galaxy:
      sys = galaxy.get_system_of_planet(final_planet)
      if sys:
          system_name = sys.name
          local_hex = [final_planet.location.q, final_planet.location.r]
  ```
  Add `system_name=system_name, local_hex=local_hex` to `log_event()` call
- [ ] Verify the `galaxy` parameter is accessible in this method (check method signature and callers)

#### Task 2.4: Add tests for enriched event data [Medium]
**Tests:** `pytest tests/unit/strategy/engine/`
- [ ] Add test verifying production events include `system_name` in details
- [ ] Add test verifying production events include `local_hex` in details
- [ ] Add test verifying combat events include `system_name` in details
- [ ] Add test verifying colonization events include `system_name` and `local_hex` in details
- [ ] Run full test suite to verify no regressions: `pytest tests/ -n 12`

---

### Phase 3: Add Sidebar with Column Toggles [Medium]
**Objective:** Create a sidebar panel for the Event Log window with column visibility checkboxes, following the FleetReport/PlanetList pattern.

#### Task 3.1: Create EventLogSidebar class [Medium]
**File:** `game/ui/screens/event_log_sidebar.py` (new file)
**Tests:** `pytest tests/unit/ui/screens/test_event_log_sidebar.py`
- [ ] Create `EventLogSidebar` class following `fleet_report_sidebar.py` pattern
- [ ] Constructor takes: `panel` (UIPanel container), `manager`, `column_manager` (TableColumnManager), `on_column_toggle` callback
- [ ] Implement `_build_column_section()` using `column_manager.get_toggleable_columns()`
- [ ] Use `[x]`/`[ ]` button pattern with `object_id=f"#column_{col_id}"` and `btn.col_ref = col`
- [ ] Store column buttons dict: `self.column_buttons: Dict[str, UIButton]`
- [ ] Add `COLUMNS` label header
- [ ] Implement `handle_button_click(ui_element)` → returns column_id if it was a column toggle, else None
- [ ] Implement `refresh_button_labels()` to update `[x]`/`[ ]` text after toggle

#### Task 3.2: Integrate sidebar into EventLogWindow [Medium]
**File:** `game/ui/screens/event_log_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py`
- [ ] Add `SIDEBAR_WIDTH = 180` constant
- [ ] In `_init_layout()`: Create a left sidebar UIPanel of width `SIDEBAR_WIDTH`
- [ ] Shift table panel right by `SIDEBAR_WIDTH` and reduce its width
- [ ] Create `EventLogSidebar` instance in the sidebar panel, passing `self.column_manager`
- [ ] In `process_event()`: Add handling for sidebar column toggle button clicks:
  ```python
  col_id = self.sidebar.handle_button_click(clicked)
  if col_id:
      self.column_manager.toggle_column(col_id)
      self.sidebar.refresh_button_labels()
      self.virtual_table.rebuild_headers()
      self.virtual_table.rebuild_row_pool()
      self.virtual_table.force_update()
      self.virtual_table.update_visible_rows()
  ```
- [ ] Move filter buttons into sidebar (above column toggles) or keep in header — match the existing layout with sidebar for columns only

#### Task 3.3: Write sidebar tests [Medium]
**File:** `tests/unit/ui/screens/test_event_log_sidebar.py` (new file)
**Tests:** `pytest tests/unit/ui/screens/test_event_log_sidebar.py`
- [ ] Test sidebar creates correct number of column toggle buttons
- [ ] Test `handle_button_click()` returns column_id for column buttons
- [ ] Test `handle_button_click()` returns None for non-column buttons
- [ ] Test `refresh_button_labels()` updates text to reflect visibility state

#### Task 3.4: Update EventLogWindow tests [Simple]
**File:** `tests/unit/ui/screens/test_event_log_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py`
- [ ] Update any tests that depend on window layout (table positioning)
- [ ] Add test verifying column toggle integration works end-to-end
- [ ] Run tests, verify all pass

---

### Phase 4: Fix Double-Click Navigation [Medium]
**Objective:** Investigate and fix the broken double-click → camera navigation.

#### Task 4.1: Investigate navigation callback chain [Medium]
**File:** `game/ui/screens/event_log_window.py`, `game/ui/screens/strategy_window_manager.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py`
- [ ] Add debug logging to `_handle_row_navigate()` (line 277) to confirm it fires
- [ ] Verify `find_clicked_row()` returns valid index (check coordinate space: `event.pos` may be screen-space but table expects container-relative)
- [ ] Verify `on_navigate_callback` is set (not None) when window is created
- [ ] Check `_on_event_log_navigate()` in strategy_window_manager.py: verify `self.scene` has `_camera_nav` attribute
- [ ] Check if `center_on_hex()` is actually moving the camera (could be zoom level issue)

#### Task 4.2: Fix identified issues [Simple-Medium]
**File:** Depends on findings from 4.1
**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py`
- [ ] Fix coordinate space issue if `find_clicked_row()` fails (likely need to convert `event.pos` to table-relative coords)
- [ ] Or fix whatever issue is identified in Task 4.1
- [ ] Add/update test for the fix

#### Task 4.3: Add navigation integration test [Simple]
**File:** `tests/unit/ui/screens/test_event_log_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py`
- [ ] Add test verifying double-click detection triggers navigate callback with correct hex coords
- [ ] Add test verifying navigation callback closes the event log window
- [ ] Verify existing navigation tests still pass

---

### Phase 5: Add Storm Column [Medium]
**Objective:** Add a "Storm" column to the event log that shows storm names at the event's location.

#### Task 5.1: Add facade method for storm query [Simple]
**File:** `game/strategy/facade/strategy_session_facade.py`
**Tests:** `pytest tests/unit/strategy/facade/test_strategy_session_facade.py`
- [ ] Add `get_storm_names_at_hex(hex_coord: HexCoord) -> List[str]` method:
  ```python
  def get_storm_names_at_hex(self, hex_coord: HexCoord) -> List[str]:
      from game.strategy.services.area_effect_manager import AreaEffectManager
      manager = AreaEffectManager()
      effects = manager.get_effects_at_global_hex(self._session.galaxy, hex_coord)
      return effects.storm_names if effects.in_storm else []
  ```
- [ ] Add test for this facade method

#### Task 5.2: Enrich events with storm data at creation time [Medium]
**File:** `game/strategy/engine/conflict_resolution_engine.py`, `game/strategy/engine/production_engine.py`, `game/strategy/engine/fleet_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/`
- [ ] In ConflictResolutionEngine (already has `_area_effect_manager`): Query storm names at combat hex, add `storm_names=storm_names_list` to `log_event()` kwargs
- [ ] In ProductionEngine: Need access to area_effect_manager or accept it as parameter. Query storm at production hex, add to `log_event()`. If too invasive, use a lighter approach: just store the `location_hex` and let the UI query the facade when rendering.
- [ ] In FleetOrderProcessor: Same consideration — inject area_effect_manager or defer to UI-time lookup
- [ ] **Decision needed during implementation:** If injecting area_effect_manager into all engines is too invasive, an alternative is to have EventLogDataSource accept a facade reference and do lazy lookups for the storm column. This avoids engine-level changes but means storm data is computed at display time (which is fine since storms don't move).

#### Task 5.3: Add storm column to EVENT_LOG_COLUMNS [Simple]
**File:** `game/ui/screens/event_log_data_source.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_data_source.py`
- [ ] Add column: `{"id": "storm", "width": 120, "title": "Storm", "visible": False, "sortable": True}`
- [ ] Add `get_cell_value()` handler:
  ```python
  if column_id == "storm":
      details = event.get("details", {})
      storm_names = details.get("storm_names", [])
      return ", ".join(storm_names) if storm_names else ""
  ```
- [ ] Default to `visible=False` (most events won't be in storms)

#### Task 5.4: Add storm column tests [Simple]
**File:** `tests/unit/ui/screens/test_event_log_data_source.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_data_source.py`
- [ ] Test storm column returns joined storm names: `details={"storm_names": ["Ion Storm Alpha"]}` → `"Ion Storm Alpha"`
- [ ] Test storm column returns empty for no storms: `details={}` → `""`
- [ ] Test storm column with multiple storms: `details={"storm_names": ["Ion Storm", "Plasma Storm"]}` → `"Ion Storm, Plasma Storm"`
- [ ] Update column count test (now 8 columns)
- [ ] Run full suite: `pytest tests/ -n 12`

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/ -n 12` — 13,040 passed, 1 skipped (baseline established)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` — all affected tests pass
- [ ] Manual test: Open Event Log in game, verify column display
- [ ] Verify column toggle sidebar works

### Final Verification
- [ ] Open Event Log: System and Planet columns show correct data
- [ ] Toggle columns on/off via sidebar: Table rebuilds correctly
- [ ] Double-click an event with location: Camera navigates to hex
- [ ] Double-click an event without location: Nothing happens (no crash)
- [ ] Storm column shows storm names for events in storm hexes
- [ ] Run full test suite: `pytest tests/ -n 12` (NOT --testmon, full verification)

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All Phase 4 tasks checked off
- [ ] All Phase 5 tasks checked off
- [ ] All tests passing
- [ ] Regression tests passing
- [ ] Audit passed (no significant issues)
- [ ] User verified
