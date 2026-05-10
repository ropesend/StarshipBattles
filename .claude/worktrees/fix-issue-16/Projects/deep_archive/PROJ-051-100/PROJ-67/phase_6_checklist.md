# PROJ-67 Phase 6: Save/Load & Edge Cases

**Objective:** Ensure fleet build queues persist across save/load and handle edge cases.

## Completion Criteria
- [x] All tasks below checked off
- [x] `pytest tests/integration/strategy/ -k save` passes
- [x] `pytest tests/unit/strategy/production_engine/` passes
- [x] `pytest tests/ -n 12` full suite passes (6388 passed, 2 pre-existing failures)

---

## Task 6.1: Save/Load Integration Testing [Simple]
**Tests:** `pytest tests/integration/strategy/ -k save`

- [x] Write test: save game with fleet that has construction_queue items
- [x] Write test: load game restores fleet construction_queue
- [x] Write test: save game with fleet BUILD order, load, fleet still has BUILD order
- [x] Write test: round-trip save/load preserves full fleet state

**Notes:** Created `tests/integration/strategy/production/test_fleet_save_load.py` with 6 tests.

---

## Task 6.2: Edge Case: Yard Ship Destroyed Mid-Build [Medium]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/`

- [x] In `process_fleet_production()`: if fleet no longer has_space_shipyard, pause production
- [x] Log appropriate warning
- [x] Write test: production pauses when yard ship destroyed
- [x] Write test: production resumes when new yard ship joins fleet

**Notes:** Already implemented in Phase 3. Added new test for production resumption.

---

## Task 6.3: Edge Case: Fleet Enters Combat While Building [Simple]
**File:** `game/strategy/engine/conflict_resolution_engine.py` (review only)
**Tests:** `pytest tests/unit/strategy/ -k conflict`

- [x] Verify: building fleet CAN still be attacked (no special protection)
- [x] After battle: if fleet survives but yard destroyed, production pauses
- [x] Write test: building fleet participates in combat when enemy arrives

**Notes:** Conflict resolution engine has no special handling for BUILD orders - building fleets participate in combat normally. Added tests in `test_core.py`.

---

## Task 6.4: Edge Case: Complex in Queue, Fleet Moves Away [Medium]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/`

- [x] In `process_fleet_production()`: for complex items, validate fleet at planet hex
- [x] If not at planet: skip/pause the complex item (don't decrement turns)
- [x] Non-complex items in queue continue normally
- [x] Write test: complex pauses when fleet not at planet
- [x] Write test: ship items continue even when not at planet

**Notes:** Added planet proximity check before decrementing turns for complex items. Created `TestComplexPauseWhenFleetNotAtPlanet` test class.

---

## Task 6.5: Full Integration Test [Medium]
**Tests:** `pytest tests/integration/strategy/`

- [x] Write end-to-end test: create fleet with yard -> issue BUILD -> advance turns -> ship spawns in fleet
- [x] Write end-to-end test: fleet at planet -> build complex -> complex appears on planet
- [x] Write end-to-end test: fleet with BUILD order -> try to move -> blocked
- [x] Run full test suite: `pytest tests/ -n 12`

**Notes:** Created `tests/integration/strategy/production/test_fleet_production_e2e.py` with 7 E2E tests covering full lifecycle.
