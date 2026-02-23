# Phase 3: TurnEngine Wiring & Legacy Removal

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-161 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Move harvesting and maintenance from turn-start into the per-tick loop, and remove `_apply_partial_harvest` and `harvesting_engine` parameter from ProductionEngine.

---

## Tasks

### Task 3.1: Move Harvesting Into `_process_tick` [Medium]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/integration/strategy/turn_engine/test_harvesting.py` (will fail until Phase 4 updates)

- [x] Remove line 258: `self.harvesting_engine.process_harvesting(empires)` from `process_turn()`
- [x] Add to `_process_tick()`, as the FIRST phase (before current Phase 0 resource consumption):
  ```python
  # --- Phase 0: Harvesting (1/100th of per-turn extraction) ---
  # PROJ-161: Spread harvesting across 100 ticks
  self.harvesting_engine.process_harvesting_tick(tick, empires)
  ```
- [x] Verify: harvesting runs before resource consumption and construction in each tick

**Notes:** Implemented at line ~317 in _process_tick()

---

### Task 3.2: Move Maintenance Into `_process_tick` [Medium]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/integration/strategy/turn_engine/test_maintenance.py` (will fail until Phase 4 updates)

- [x] Remove line 261: `self.last_scuttle_events = self.maintenance_engine.process_maintenance(empires)` from `process_turn()`
- [x] Add `self.last_scuttle_events = []` at start of `process_turn()` (initialize accumulator)
- [x] Add to `_process_tick()`, after harvesting but before resource consumption:
  ```python
  # --- Phase 0a: Maintenance (1/100th of per-turn costs, immediate scuttle) ---
  # PROJ-161: Spread maintenance across 100 ticks
  tick_scuttles = self.maintenance_engine.process_maintenance_tick(tick, empires)
  self.last_scuttle_events.extend(tick_scuttles)
  ```
- [x] Verify: maintenance runs after harvesting, before construction in each tick
- [x] Verify: `last_scuttle_events` accumulates across all 100 ticks

**Notes:** Implemented at lines ~321-323 in _process_tick(). The UI at `game/ui/screens/strategy_screen.py:344` reads `last_scuttle_events` at turn end -- no UI changes needed.

---

### Task 3.3: Remove `_apply_partial_harvest` from ProductionEngine [Medium]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/test_tick_consumption.py` (will fail until Phase 4 updates)

- [x] Delete `_apply_partial_harvest` method entirely (lines 386-441)
- [x] Remove the partial harvest call block in `_complete_item` (lines 378-382)
- [x] Remove `harvesting_engine` parameter from `process_construction_tick` signature (line 90)
- [x] Remove `harvesting_engine` from docstring of `process_construction_tick` (line 104)
- [x] Remove `harvesting_engine=harvesting_engine` from all 3 calls to `_process_queue_tick_dynamic`:
  - Line 115 (base queue call)
  - Line 126 (facility queue call)
  - Line 175 (fleet queue call)
- [x] Remove `harvesting_engine` from `_process_queue_tick_dynamic` signature (line 188)
- [x] Remove `harvesting_engine` from both calls to `_complete_item`:
  - Line 276 (first call)
  - Line 350 (second call)
- [x] Remove `harvesting_engine` from `_complete_item` signature (line 353)
- [x] Verify: no references to `_apply_partial_harvest` or `harvesting_engine` remain in production_engine.py

**Notes:** Also deleted obsolete tests `test_mid_turn_complex_triggers_partial_harvest` and `test_storage_recalculated_on_mid_turn_complex` from test_tick_consumption.py since they tested the removed functionality.

---

### Task 3.4: Update TurnEngine Call to ProductionEngine [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/integration/strategy/turn_engine/`

- [x] Remove `harvesting_engine=self.harvesting_engine` from `process_construction_tick` call (line 333)
- [x] Verify: no references to `harvesting_engine` in the `_process_tick` production call

**Notes:** Done as part of phase comment updates.

---

### Task 3.5: Update `_process_tick` Phase Comments [Simple]
**File:** `game/strategy/engine/turn_engine.py`

- [x] Renumber/rename phase comments in `_process_tick` to reflect new order:
  ```
  Phase 0:  Harvesting (1/100th extraction)               -- NEW
  Phase 0a: Maintenance (1/100th cost, immediate scuttle)  -- MOVED
  Phase 0b: Per-turn Resource Consumption (ship costs)
  Phase 0c: Fuel Generation at Facilities
  Phase 0d: Fleet Resupply from Facilities
  Phase 0e: Construction Resource Consumption + Mid-turn Completion
  Phase 1:  Instant Orders (JOIN_FLEET)
  Phase 2:  Calculate Moves
  Phase 3:  Apply Moves
  Phase 4:  Combat
  ```
- [x] Update `_process_tick` docstring to document new phase order
- [x] Update `process_turn` docstring to remove harvesting/maintenance from turn-level phases

**Notes:** Updated module docstring and _process_tick docstring.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `grep -r "_apply_partial_harvest" game/` returns no results
- [x] `grep -r "harvesting_engine" game/strategy/engine/production_engine.py` returns only docstring references (documenting removal)
- [x] Note: 4 integration tests fail (expected, will be fixed in Phase 4)
- [x] Deleted obsolete production tests that tested removed functionality
- [x] 32 production engine tests pass, 308 unit engine tests pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
