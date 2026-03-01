# Phase 5: Add Storm Column

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-215 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add a "Storm" column to the event log showing storm names at the event's hex location.

---

## Tasks

### Task 5.1: Add facade method for storm query [Simple]
**File:** `game/strategy/facade/strategy_session_facade.py`
**Tests:** `pytest tests/unit/strategy/facade/test_strategy_session_facade.py`

- [ ] Add `get_storm_names_at_hex(hex_coord: HexCoord) -> List[str]` method
- [ ] Instantiate `AreaEffectManager()`, call `get_effects_at_global_hex()`, return `storm_names`
- [ ] Add test for this facade method

**Notes:**

### Task 5.2: Enrich events with storm data at creation time [Medium]
**File:** `game/strategy/engine/conflict_resolution_engine.py`, `game/strategy/engine/production_engine.py`, `game/strategy/engine/fleet_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/`

- [ ] In ConflictResolutionEngine (already has `_area_effect_manager`): Query storm names at combat hex, add `storm_names=storm_names_list` to `log_event()`
- [ ] In ProductionEngine: Determine approach — inject area_effect_manager or defer to UI lookup. If injecting, query at production hex.
- [ ] In FleetOrderProcessor: Same consideration.
- [ ] **Alternative approach:** If engine injection is too invasive, have EventLogDataSource accept a facade reference for lazy storm lookup. Document decision.

**Notes:**

### Task 5.3: Add storm column to EVENT_LOG_COLUMNS [Simple]
**File:** `game/ui/screens/event_log_data_source.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_data_source.py`

- [ ] Add column: `{"id": "storm", "width": 120, "title": "Storm", "visible": False, "sortable": True}`
- [ ] Add `get_cell_value()` handler: join `storm_names` list or return `""`
- [ ] Default `visible=False`

**Notes:**

### Task 5.4: Add storm column tests [Simple]
**File:** `tests/unit/ui/screens/test_event_log_data_source.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_data_source.py`

- [ ] Test storm column with single storm name
- [ ] Test storm column with no storms (empty string)
- [ ] Test storm column with multiple storm names (comma-joined)
- [ ] Update column count test (now 8 columns)
- [ ] Run full suite: `pytest tests/ -n 12`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
