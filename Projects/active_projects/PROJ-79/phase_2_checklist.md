# Phase 2: Build Time from Cost + Tick-Granular Production

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-79 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace hardcoded `turns=1` with cost-based build time calculation. Move production completion from end-of-turn into per-tick processing so items complete mid-turn. Newly spawned facilities produce proportionally for remaining ticks.

---

## Tasks

### Task 2.1: Add build time calculation to controller [Medium]
**File:** `game/ui/panels/build_queue_controller.py`
**Tests:** `pytest tests/unit/ui/panels/test_build_queue_controller.py`

- [ ] Add `import math` at top
- [ ] Add module constant `PLANETARY_YARD_BUILD_RATE = 2000.0`
- [ ] Add method `_calculate_build_turns(self, design_id: str, build_rate: float) -> int`:
  ```python
  def _calculate_build_turns(self, design_id: str, build_rate: float) -> int:
      """Calculate build turns from design resource cost and build rate.
      Formula: turns = max(1, ceil(max_resource_cost / build_rate))
      """
      designs = self.design_library.scan_designs()
      design = next((d for d in designs if d.design_id == design_id), None)
      if not design or not design.resource_cost:
          return 1
      max_cost = max(design.resource_cost.values()) if design.resource_cost else 0
      if max_cost <= 0:
          return 1
      return max(1, math.ceil(max_cost / build_rate))
  ```
- [ ] Add method `_build_cost_tracking(self, design_id: str, turns: int) -> dict`:
  ```python
  def _build_cost_tracking(self, design_id: str, turns: int) -> dict:
      """Create cost tracking fields for a queue item."""
      designs = self.design_library.scan_designs()
      design = next((d for d in designs if d.design_id == design_id), None)
      total_cost = dict(design.resource_cost) if design and design.resource_cost else {}
      total_ticks = turns * 100
      cost_per_tick = {res: amount / total_ticks for res, amount in total_cost.items()} if total_ticks > 0 else {}
      return {
          "total_cost": total_cost,
          "cost_per_tick": cost_per_tick,
          "resources_consumed": {res: 0.0 for res in total_cost},
          "ticks_in_current_turn": 0,
      }
  ```
- [ ] Verify: Both methods work with mock design library

**Notes:**

### Task 2.2: Use calculated build time when adding to queue [Medium]
**File:** `game/ui/panels/build_queue_controller.py`
**Tests:** `pytest tests/unit/ui/panels/test_build_queue_controller.py`

- [ ] Make `turns` parameter optional in `add_to_queue()` signature: `turns: Optional[int] = None`
- [ ] In `_add_to_single_queue()`:
  - Get `build_rate` from `self.active_queue_source.build_rate` (add `build_rate` attribute access)
  - If `turns` not provided, call `turns = self._calculate_build_turns(design_id, build_rate)`
  - After creating `queue_item`, merge cost tracking: `queue_item.update(self._build_cost_tracking(design_id, turns))`
- [ ] In `_add_to_multiple_queues()`:
  - Per-source: calculate turns using `source.build_rate`
  - Merge cost tracking per-item
- [ ] In `_add_to_fallback()`:
  - Use `PLANETARY_YARD_BUILD_RATE` as build_rate
  - Calculate turns and merge cost tracking
- [ ] Verify: Queue items have correct `turns_remaining` and cost tracking fields

**Notes:**

### Task 2.3: Remove hardcoded turns=1 from callers [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/integration/ui/`

- [ ] Line 852: Change `self.controller.add_to_queue(self.drag_handler.selected_design, turns=1)` to `self.controller.add_to_queue(self.drag_handler.selected_design)`
- [ ] Line 944: Same change
- [ ] Verify: Adding items uses calculated turns, not 1

**Notes:**

### Task 2.4: Rework tick-based production for completion + spawning [Complex]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/`

- [ ] Update `process_construction_tick()` signature to accept `galaxy` and `save_path`:
  ```python
  def process_construction_tick(self, tick: int, empires: List, galaxy,
                                  save_path: Optional[str] = None,
                                  harvesting_engine=None) -> None:
  ```
- [ ] Add fleet queue tick processing (currently only colony queues are processed):
  ```python
  # Fleet queues
  for fleet in empire.fleets:
      if not fleet.is_building or not fleet.has_space_shipyard:
          continue
      if fleet.construction_queue:
          self._process_queue_tick_with_completion(
              fleet.construction_queue, empire, tick, galaxy, save_path,
              colony_or_fleet=fleet, harvesting_engine=harvesting_engine
          )
  ```
- [ ] Create new method `_process_queue_tick_with_completion()` that:
  1. Processes the first item's cost_per_tick (existing logic)
  2. Checks if all `resources_consumed[res] >= total_cost[res]` for all resources
  3. If complete: pops item, spawns ship/complex (calling existing `_spawn_*` methods)
  4. For complexes: calls partial harvest logic for newly spawned facility
  5. If queue has more items after pop, starts processing next item in same tick
  6. Also decrements `turns_remaining` for display purposes when `ticks_in_current_turn >= 100`
- [ ] Keep existing `_process_queue_tick()` for backward compat with legacy items (no cost tracking)
- [ ] Update `_process_queue_tick_with_completion()` to handle complex items on fleet queues:
  - Check `target_planet_id` on queue item
  - If fleet is at planet hex, proceed; otherwise pause
- [ ] Verify: Items complete mid-turn, next item starts on next tick

**Notes:**

### Task 2.5: Update TurnEngine to pass galaxy/save_path to tick processing [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/`

- [ ] Line 344: Update call to pass additional params:
  ```python
  self.production_engine.process_construction_tick(
      tick, empires, galaxy,
      save_path=save_path,
      harvesting_engine=self.harvesting_engine
  )
  ```
- [ ] Ensure `save_path` is accessible in `_process_tick()` - it's passed to `process_turn()` at line 245, store as instance var or pass through
- [ ] Verify: No signature errors at runtime

**Notes:**

### Task 2.6: Mid-turn facility activation with proportional production [Complex]
**File:** `game/strategy/engine/production_engine.py`
**Existing pattern:** `game/strategy/engine/harvesting_engine.py`

- [ ] After spawning a complex mid-turn at tick N in `_process_queue_tick_with_completion()`:
  - Call `harvesting_engine.recalculate_storage(empires)` to update storage capacity immediately
  - Call new helper `_apply_partial_harvest(facility, colony, empire, tick, harvesting_engine)`:
    ```python
    def _apply_partial_harvest(self, facility, colony, empire, tick, harvesting_engine):
        """Apply proportional harvest for a facility spawned mid-turn."""
        remaining_fraction = (100 - tick) / 100.0
        if remaining_fraction <= 0:
            return
        # Use harvesting engine's component scanning to find harvesters
        # Call _harvest_resource with modified rate for each harvester found
    ```
  - This needs to scan the spawned facility's components for ResourceHarvester abilities and apply `base_rate * quality * remaining_fraction`
  - Reuse `HarvestingEngine._get_harvester_info()` pattern for scanning
- [ ] Verify: Facility spawned at tick 67 produces ~33% of normal harvest

**Notes:**

### Task 2.7: Tests [Complex]
**Tests:** `pytest tests/unit/strategy/production_engine/ tests/unit/ui/panels/test_build_queue_controller.py`

- [ ] Test `_calculate_build_turns()`: {Metals: 100000, Org: 10000} at 2000/turn = 50 turns
- [ ] Test `_calculate_build_turns()`: {Metals: 6000} at 3000/turn = 2 turns
- [ ] Test `_calculate_build_turns()`: zero-cost design = 1 turn
- [ ] Test `_build_cost_tracking()`: proportional cost_per_tick calculation
- [ ] Test queue item has cost tracking fields after `add_to_queue()`
- [ ] Test tick-based completion: item completes when resources_consumed >= total_cost
- [ ] Test mid-tick chain: completion on tick 50 starts next item on tick 51
- [ ] Test fleet tick-based production works
- [ ] Test mid-turn complex spawn triggers proportional harvest
- [ ] Test mid-turn storage facility increases empire capacity immediately
- [ ] Test legacy items (no cost tracking) still work via end-of-turn processing
- [ ] Run: `pytest tests/ --testmon`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ --testmon` passes
- [ ] Manual test: Add item to queue, verify turns > 1 based on cost
- [ ] Manual test: Process turns, verify item completes at correct tick
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
