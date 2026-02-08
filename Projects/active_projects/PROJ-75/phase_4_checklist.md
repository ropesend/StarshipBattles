# Phase 4: Production Resource Consumption

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-75 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Make build queues consume resources proportionally over 100 ticks

---

## Tasks

### Task 4.1: Write TDD tests for design cost calculation [Medium]
**File:** `tests/unit/strategy/production_engine/test_resource_costs.py` (NEW)
**Tests:** `pytest tests/unit/strategy/production_engine/test_resource_costs.py -v`

- [ ] Create test file with TestDesignCostCalculation class
- [ ] Test: calculate cost from single component
- [ ] Test: calculate cost from multiple components (sum)
- [ ] Test: calculate cost with missing resource_cost (defaults to empty)
- [ ] Test: calculate cost from complex design layers
- [ ] Test: ship design cost calculation
- [ ] Test: cost cached in design_data

**Notes:**

---

### Task 4.2: Implement design cost calculation [Medium]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/test_resource_costs.py -v`

- [ ] Add `_calculate_design_cost(design_data: Dict) -> Dict[str, float]` method:
  ```python
  def _calculate_design_cost(self, design_data: Dict) -> Dict[str, float]:
      """Calculate total resource cost from all components in design."""
      if 'total_resource_cost' in design_data:
          return design_data['total_resource_cost']

      total_cost = {}
      for layer in design_data.get('layers', {}).values():
          for component in layer.get('components', []):
              comp_cost = component.get('resource_cost', {})
              for res, amount in comp_cost.items():
                  total_cost[res] = total_cost.get(res, 0) + amount

      design_data['total_resource_cost'] = total_cost
      return total_cost
  ```
- [ ] Verify cost calculation works with existing designs

**Notes:**

---

### Task 4.3: Write TDD tests for queue item cost tracking [Medium]
**File:** `tests/unit/strategy/production_engine/test_resource_costs.py`
**Tests:** `pytest tests/unit/strategy/production_engine/test_resource_costs.py -v`

- [ ] Test: queue item populated with total_cost
- [ ] Test: queue item has cost_per_tick calculated
- [ ] Test: cost_per_tick = total_cost / (turns * 100)
- [ ] Test: queue item tracks resources_consumed

**Notes:**

---

### Task 4.4: Add cost tracking to queue items [Medium]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/test_resource_costs.py -v`

- [ ] Modify queue item creation to include cost fields:
  ```python
  queue_item = {
      "design_id": design_id,
      "type": vehicle_type,
      "turns_remaining": turns,
      "total_cost": self._calculate_design_cost(design_data),
      "cost_per_tick": {},  # Calculated below
      "resources_consumed": {},
      "ticks_in_current_turn": 0
  }
  # Calculate cost_per_tick
  for res, amount in queue_item["total_cost"].items():
      queue_item["cost_per_tick"][res] = amount / (turns * 100)
      queue_item["resources_consumed"][res] = 0.0
  ```
- [ ] Update all queue item creation points

**Notes:**

---

### Task 4.5: Write TDD tests for per-tick consumption [Complex]
**File:** `tests/unit/strategy/production_engine/test_tick_consumption.py` (NEW)
**Tests:** `pytest tests/unit/strategy/production_engine/test_tick_consumption.py -v`

- [ ] Create test file with TestTickConsumption class
- [ ] Test: successful per-tick consumption deducts from empire
- [ ] Test: resources_consumed incremented each tick
- [ ] Test: ticks_in_current_turn incremented
- [ ] Test: pause on insufficient resources (no consumption, no tick increment)
- [ ] Test: resume when resources available
- [ ] Test: after 100 ticks, turns_remaining decremented
- [ ] Test: item completed and removed when turns_remaining reaches 0
- [ ] Test: multiple queue items - only first processes

**Notes:**

---

### Task 4.6: Implement per-tick resource consumption [Complex]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/test_tick_consumption.py -v`

- [ ] Add `process_construction_tick(tick: int, empires, galaxy) -> None`:
  ```python
  def process_construction_tick(self, tick: int, empires, galaxy) -> None:
      """Process per-tick resource consumption for all construction."""
      for empire in empires:
          for colony in empire.colonies:
              self._process_queue_tick(colony.construction_queue, empire)
              for facility in colony.facilities:
                  if hasattr(facility, 'construction_queue'):
                      self._process_queue_tick(facility.construction_queue, empire)

  def _process_queue_tick(self, queue: List[Dict], empire) -> None:
      if not queue:
          return
      item = queue[0]
      cost_per_tick = item.get('cost_per_tick', {})

      # Check if empire has resources for this tick
      if not empire.has_resources(cost_per_tick):
          return  # Paused - insufficient resources

      # Consume resources
      for res, amount in cost_per_tick.items():
          empire.consume_resources(res, amount)
          item['resources_consumed'][res] = item.get('resources_consumed', {}).get(res, 0) + amount

      # Track tick progress
      item['ticks_in_current_turn'] = item.get('ticks_in_current_turn', 0) + 1
      if item['ticks_in_current_turn'] >= 100:
          item['ticks_in_current_turn'] = 0
          item['turns_remaining'] -= 1
  ```

**Notes:**

---

### Task 4.7: Integrate into TurnEngine [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/integration/strategy/turn_engine/ -v`

- [ ] Call `production_engine.process_construction_tick(tick, empires, galaxy)` in subturn loop
- [ ] Place after resource consumption, before movement

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
