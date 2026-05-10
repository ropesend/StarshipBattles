# Phase 1: Expand Event Columns & Data Source

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-215 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace the single "Location" column with four granular columns (System, Planet, Local Hex, Galaxy Hex) and update the data source to extract values from event details.

---

## Tasks

### Task 1.1: Update EVENT_LOG_COLUMNS definition [Simple]
**File:** `game/ui/screens/event_log_data_source.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_data_source.py`

- [x] Remove the `"location"` column entry (line 16)
- [x] Add new column: `{"id": "system", "width": 120, "title": "System", "visible": True, "sortable": True}`
- [x] Add new column: `{"id": "planet", "width": 120, "title": "Planet", "visible": True, "sortable": True}`
- [x] Add new column: `{"id": "local_hex", "width": 80, "title": "Local Hex", "visible": False, "sortable": True}`
- [x] Add new column: `{"id": "galaxy_hex", "width": 80, "title": "Galaxy Hex", "visible": False, "sortable": True}`
- [x] Verify column count is now 7 (category, turn, system, planet, local_hex, galaxy_hex, message)

**Notes:**

### Task 1.2: Update get_cell_value() for new columns [Simple]
**File:** `game/ui/screens/event_log_data_source.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_data_source.py`

- [x] Replace the `if column_id == "location":` block (lines 94-102) with handlers for system, planet, local_hex, galaxy_hex
- [x] `"system"` → `event.get("details", {}).get("system_name", "")`
- [x] `"planet"` → `event.get("details", {}).get("location_name", "")`
- [x] `"local_hex"` → format `details.get("local_hex")` as `"(q, r)"` or `""`
- [x] `"galaxy_hex"` → format `details.get("location_hex")` as `"(q, r)"` or `""`

**Notes:**

### Task 1.3: Update data source tests [Medium]
**File:** `tests/unit/ui/screens/test_event_log_data_source.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_data_source.py`

- [x] Update `test_column_count_includes_location` → `test_column_count` asserting 7 columns
- [x] Update `test_location_column_definition` → tests for system, planet, local_hex, galaxy_hex column definitions
- [x] Replace `test_location_cell_value_from_details` with `test_system_cell_value`
- [x] Replace `test_location_cell_value_empty_when_no_location` with `test_system_cell_value_empty`
- [x] Replace `test_location_cell_value_hex_fallback` with `test_planet_cell_value`
- [x] Add `test_local_hex_cell_value` and `test_local_hex_cell_value_empty`
- [x] Add `test_galaxy_hex_cell_value` and `test_galaxy_hex_cell_value_empty`
- [x] Run tests, verify all pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
