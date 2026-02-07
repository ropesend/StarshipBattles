# PROJ-67 Phase 6: Save/Load & Edge Cases

**Objective:** Ensure fleet build queues persist across save/load and handle edge cases.

## Completion Criteria
- [ ] All tasks below checked off
- [ ] `pytest tests/integration/strategy/ -k save` passes
- [ ] `pytest tests/unit/strategy/production_engine/` passes
- [ ] `pytest tests/ -n 12` full suite passes (final verification)

---

## Task 6.1: Save/Load Integration Testing [Simple]
**Tests:** `pytest tests/integration/strategy/ -k save`

- [ ] Write test: save game with fleet that has construction_queue items
- [ ] Write test: load game restores fleet construction_queue
- [ ] Write test: save game with fleet BUILD order, load, fleet still has BUILD order
- [ ] Write test: round-trip save/load preserves full fleet state

**Notes:**

---

## Task 6.2: Edge Case: Yard Ship Destroyed Mid-Build [Medium]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/`

- [ ] In `process_fleet_production()`: if fleet no longer has_space_shipyard, pause production
- [ ] Log appropriate warning
- [ ] Write test: production pauses when yard ship destroyed
- [ ] Write test: production resumes when new yard ship joins fleet

**Notes:**

---

## Task 6.3: Edge Case: Fleet Enters Combat While Building [Simple]
**File:** `game/strategy/engine/conflict_resolution_engine.py` (review only)
**Tests:** `pytest tests/unit/strategy/ -k conflict`

- [ ] Verify: building fleet CAN still be attacked (no special protection)
- [ ] After battle: if fleet survives but yard destroyed, production pauses
- [ ] Write test: building fleet participates in combat when enemy arrives

**Notes:**

---

## Task 6.4: Edge Case: Complex in Queue, Fleet Moves Away [Medium]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/`

- [ ] In `process_fleet_production()`: for complex items, validate fleet at planet hex
- [ ] If not at planet: skip/pause the complex item (don't decrement turns)
- [ ] Non-complex items in queue continue normally
- [ ] Write test: complex pauses when fleet not at planet
- [ ] Write test: ship items continue even when not at planet

**Notes:**

---

## Task 6.5: Full Integration Test [Medium]
**Tests:** `pytest tests/integration/strategy/`

- [ ] Write end-to-end test: create fleet with yard → issue BUILD → advance turns → ship spawns in fleet
- [ ] Write end-to-end test: fleet at planet → build complex → complex appears on planet
- [ ] Write end-to-end test: fleet with BUILD order → try to move → blocked
- [ ] Run full test suite: `pytest tests/ -n 12`

**Notes:**
