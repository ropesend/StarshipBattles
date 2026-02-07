# PROJ-67 Phase 2: BUILD Order & Movement Blocking

**Objective:** Add OrderType.BUILD, integrate with fleet order processing, block movement while building.

## Completion Criteria
- [ ] All tasks below checked off
- [ ] `pytest tests/unit/strategy/ -k order` passes
- [ ] `pytest tests/unit/strategy/ -k movement` passes
- [ ] `pytest tests/ --testmon` passes (no regressions)

---

## Task 2.1: Add OrderType.BUILD [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/ -k order`

- [ ] Add `BUILD = auto()` to `OrderType` enum (after line 14)
- [ ] Update `FleetOrder.to_dict()` - BUILD orders don't need a target (line ~27)
- [ ] Update `Fleet.from_dict()` order restoration to handle BUILD type (line ~615)
- [ ] Write test: BUILD order serializes/deserializes correctly

**Notes:**

---

## Task 2.2: Movement Blocking for BUILD Order [Medium]
**File:** `game/strategy/engine/fleet_movement_engine.py`
**Tests:** `pytest tests/unit/strategy/ -k movement`

- [ ] In `collect_movements()`: skip fleets whose current order is BUILD
- [ ] Write test: fleet with BUILD order is NOT included in movement collection
- [ ] Write test: fleet with MOVE order IS still included
- [ ] Write test: fleet with BUILD order followed by MOVE doesn't move until BUILD is popped

**Notes:**

---

## Task 2.3: BUILD Order Processing in FleetOrderProcessor [Medium]
**File:** `game/strategy/engine/fleet_order_processor.py`
**Tests:** `pytest tests/unit/strategy/ -k "order_processor and build"`

- [ ] Add BUILD handling in `process_end_turn_orders()` method
- [ ] BUILD order should NOT be auto-completed (it stays until player cancels or queue empties)
- [ ] If fleet's construction_queue becomes empty, auto-complete the BUILD order
- [ ] Write test: BUILD order persists across turns while queue has items
- [ ] Write test: BUILD order auto-completes when queue empties
- [ ] Write test: BUILD order can be manually cancelled (pop_order)

**Notes:**

---

## Task 2.4: Prevent Movement Orders While Building [Medium]
**File:** `game/strategy/data/fleet.py` (or fleet validation service)
**Tests:** `pytest tests/unit/strategy/ -k "fleet and order"`

- [ ] Add `is_building` property to Fleet: `return self.get_current_order() and self.get_current_order().type == OrderType.BUILD`
- [ ] Determine where to block MOVE orders (UI layer vs data layer) - UI layer preferred
- [ ] Write test: `is_building` returns True when BUILD is current order
- [ ] Write test: `is_building` returns False when no order or MOVE order

**Notes:**

---

## Task 2.5: Update Fleet DTO [Simple]
**File:** `game/strategy/facade/dto/fleet_dto.py`
**Tests:** `pytest tests/unit/strategy/facade/ -k fleet`

- [ ] Add `is_building: bool` to `FleetInfo` dataclass
- [ ] Add `has_space_shipyard: bool` to `FleetInfo` dataclass
- [ ] Add `construction_queue_size: int` to `FleetInfo` dataclass
- [ ] Update `FleetInfo.from_fleet()` to populate new fields
- [ ] Write tests for new DTO fields

**Notes:**
