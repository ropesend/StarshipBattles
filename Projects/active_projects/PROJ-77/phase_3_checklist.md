# Phase 3: Engine Event Emission

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-77 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add log_event() calls to engines for key events

---

## Tasks

### Task 3.1: Production Events - Ship Building [Medium]
**File:** `game/strategy/engine/production_engine.py`

**Tests:** `pytest tests/unit/strategy/production_engine/ -v`

- [ ] Add import: `from game.core.logger import log_event`
- [ ] In `_spawn_ship()` after ship spawned (~line 230), add:
  ```python
  log_event("ship_built",
      category="production",
      empire_id=empire.id,
      message=f"Built {design_name} at {planet.name}",
      design_id=design_id,
      planet_id=planet.id,
      fleet_id=new_fleet.id)
  ```
- [ ] In `_spawn_fleet_ship()` after fleet production (~line 335), add:
  ```python
  log_event("ship_built",
      category="production",
      empire_id=empire.id,
      message=f"Fleet {fleet.id} built {design_name}",
      design_id=design_id,
      fleet_id=fleet.id,
      is_fleet_production=True)
  ```
- [ ] Verify: building a ship creates an event

**Notes:**

---

### Task 3.2: Production Events - Complex Building [Medium]
**File:** `game/strategy/engine/production_engine.py`

**Tests:** `pytest tests/unit/strategy/production_engine/ -v`

- [ ] In `_spawn_complex()` after complex built (~line 175), add:
  ```python
  log_event("complex_built",
      category="production",
      empire_id=empire.id,
      message=f"Built {facility.name} on {planet.name}",
      design_id=design_id,
      planet_id=planet.id)
  ```
- [ ] Verify: building a complex creates an event

**Notes:**

---

### Task 3.3: Colony Events [Medium]
**File:** `game/strategy/engine/fleet_order_processor.py`

**Tests:** `pytest tests/unit/strategy/test_fleet_order_processor.py -v`

- [ ] Add import: `from game.core.logger import log_event`
- [ ] In `process_colonize()` after successful colonization (~line 260), add:
  ```python
  log_event("colony_founded",
      category="colonies",
      empire_id=empire.id,
      message=f"Founded colony on {planet.name}",
      planet_id=planet.id,
      planet_name=planet.name,
      fleet_id=fleet.id)
  ```
- [ ] Verify: founding a colony creates an event

**Notes:**

---

### Task 3.4: Combat Events [Medium]
**File:** `game/strategy/engine/conflict_resolution_engine.py`

**Tests:** `pytest tests/unit/strategy/conflict_resolution/ -v`

- [ ] Add import: `from game.core.logger import log_event`
- [ ] In `_resolve_combat_simulated()` after battle resolution, add:
  ```python
  log_event("combat_resolved",
      category="combat",
      empire_id=winner.owner_id,
      message=f"Battle at {hex_location}: Victory for Fleet {winner.id}",
      location=str(hex_location),
      winner_fleet_id=winner.id,
      loser_fleet_id=loser.id)
  ```
- [ ] In RNG combat fallback (`_resolve_combat_at_hex`), add similar event
- [ ] Verify: combat resolution creates an event

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/ -v` passes
- [ ] Ship building triggers "ship_built" event
- [ ] Complex building triggers "complex_built" event
- [ ] Colony founding triggers "colony_founded" event
- [ ] Combat resolution triggers "combat_resolved" event
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
