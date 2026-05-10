# PROJ-67 Phase 2: BUILD Order & Movement Blocking

**Objective:** Add OrderType.BUILD, integrate with fleet order processing, block movement while building.

## Completion Criteria
- [x] All tasks below checked off
- [x] `pytest tests/unit/strategy/ -k order` passes
- [x] `pytest tests/unit/strategy/ -k movement` passes
- [x] `pytest tests/ --testmon` passes (no regressions)

---

## Task 2.1: Add OrderType.BUILD [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/ -k order`

- [x] Add `BUILD = auto()` to `OrderType` enum (after line 14)
- [x] Update `FleetOrder.to_dict()` - BUILD orders don't need a target (line ~27) - Already works (target=None)
- [x] Update `Fleet.from_dict()` order restoration to handle BUILD type (line ~615) - Already works
- [x] Write test: BUILD order serializes/deserializes correctly

**Notes:** Existing serialization code already handles BUILD correctly - no changes needed

---

## Task 2.2: Movement Blocking for BUILD Order [Medium]
**File:** `game/strategy/engine/fleet_movement_engine.py`
**Tests:** `pytest tests/unit/strategy/ -k movement`

- [x] In `collect_movements()`: skip fleets whose current order is BUILD
- [x] Write test: fleet with BUILD order is NOT included in movement collection
- [x] Write test: fleet with MOVE order IS still included
- [x] Write test: fleet with BUILD order followed by MOVE doesn't move until BUILD is popped

**Notes:** Tests in tests/unit/strategy/engine/test_movement_build_blocking.py

---

## Task 2.3: BUILD Order Processing in FleetOrderProcessor [Medium]
**File:** `game/strategy/engine/fleet_order_processor.py`
**Tests:** `pytest tests/unit/strategy/ -k "order_processor and build"`

- [x] Add BUILD handling in `process_end_turn_orders()` method
- [x] BUILD order should NOT be auto-completed (it stays until player cancels or queue empties)
- [x] If fleet's construction_queue becomes empty, auto-complete the BUILD order
- [x] Write test: BUILD order persists across turns while queue has items
- [x] Write test: BUILD order auto-completes when queue empties
- [x] Write test: BUILD order can be manually cancelled (pop_order)

**Notes:** Tests in tests/unit/strategy/engine/test_build_order_processor.py

---

## Task 2.4: Prevent Movement Orders While Building [Medium]
**File:** `game/strategy/data/fleet.py` (or fleet validation service)
**Tests:** `pytest tests/unit/strategy/ -k "fleet and order"`

- [x] Add `is_building` property to Fleet: `return self.get_current_order() and self.get_current_order().type == OrderType.BUILD`
- [x] Determine where to block MOVE orders (UI layer vs data layer) - UI layer preferred
- [x] Write test: `is_building` returns True when BUILD is current order
- [x] Write test: `is_building` returns False when no order or MOVE order

**Notes:** Decision: UI layer will check is_building before allowing MOVE orders (Phase 5)

---

## Task 2.5: Update Fleet DTO [Simple]
**File:** `game/strategy/facade/dto/fleet_dto.py`
**Tests:** `pytest tests/unit/strategy/facade/ -k fleet`

- [x] Add `is_building: bool` to `FleetInfo` dataclass
- [x] Add `has_space_shipyard: bool` to `FleetInfo` dataclass
- [x] Add `construction_queue_size: int` to `FleetInfo` dataclass
- [x] Update `FleetInfo.from_fleet()` to populate new fields
- [x] Write tests for new DTO fields

**Notes:** Tests in tests/unit/strategy/facade/test_fleet_dto_build.py
