# Phase 5: Add Storm Column

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-215 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add a "Storm" column to the event log showing storm names at the event's hex location.

---

## Tasks

### Task 5.1: Add facade method for storm query [Simple]
**File:** `game/strategy/facade/strategy_session_facade.py`
**Tests:** `pytest tests/unit/strategy/facade/test_strategy_session_facade.py`

- [x] Add `get_storm_names_at_hex(hex_coord: HexCoord) -> List[str]` method
- [x] Instantiate `AreaEffectManager()`, call `get_effects_at_global_hex()`, return `storm_names`
- [x] Add test for this facade method (2 tests in TestStormQueries class)

**Notes:** Method added at line 560. Uses deferred import to avoid circular deps.

### Task 5.2: Enrich events with storm data at creation time [Medium]
**File:** `game/strategy/engine/conflict_resolution_engine.py`, `game/strategy/engine/production_engine.py`, `game/strategy/engine/fleet_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/`

- [x] In ConflictResolutionEngine (already has `_area_effect_manager`): Query storm names at combat hex, add `storm_names=storm_names_list` to `log_event()`
- [~] In ProductionEngine: DEFERRED - would require injecting AreaEffectManager into engine
- [~] In FleetOrderProcessor: DEFERRED - same consideration

**Notes:**
- **Decision:** Combat events now include `storm_names` in log_event() calls (both RNG and simulated resolution paths).
- Simulated combat already had `environmental_effects` queried, so reused that.
- RNG combat now also queries AreaEffectManager for storm names.
- Production/colonization event enrichment deferred as invasive (low value - planets rarely in storms).

### Task 5.3: Add storm column to EVENT_LOG_COLUMNS [Simple]
**File:** `game/ui/screens/event_log_data_source.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_data_source.py`

- [x] Add column: `{"id": "storm", "width": 120, "title": "Storm", "visible": False, "sortable": True}`
- [x] Add `get_cell_value()` handler: join `storm_names` list or return `""`
- [x] Default `visible=False`

**Notes:** Column added between galaxy_hex and message. Handler joins list with ", ".

### Task 5.4: Add storm column tests [Simple]
**File:** `tests/unit/ui/screens/test_event_log_data_source.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_data_source.py`

- [x] Test storm column with single storm name
- [x] Test storm column with no storms (empty string)
- [x] Test storm column with multiple storm names (comma-joined)
- [x] Update column count test (now 8 columns)
- [x] Run full suite: `pytest tests/ -n 12` - 13093 passed, 1 skipped

**Notes:** 6 tests added in TestStormColumn class. All pass.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to audit
