# Phase 3: Remove Redundant Calls

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-219 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove explicit registration/unregistration calls that are now automatic

---

## Tasks

### Task 3.1: Clean up ProductionEngine [Simple]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/integration/strategy/production/`

- [ ] Remove lines 641-643 (the conditional galaxy.register_fleet call):
  ```python
  # BEFORE:
  empire.add_fleet(new_fleet)
  # PROJ-216: Register fleet with galaxy for O(1) lookup
  if galaxy:
      galaxy.register_fleet(new_fleet)

  # AFTER:
  empire.add_fleet(new_fleet)  # PROJ-219: Auto-registers via empire._galaxy
  ```
- [ ] Verify: Fleet production still creates fleets that appear in galaxy registry

**Notes:**

---

### Task 3.2: Clean up CommandHandlers [Simple]
**File:** `game/strategy/engine/command_handlers.py`
**Tests:** `pytest tests/unit/strategy/test_command_handlers.py`

- [ ] Remove line 692 (the explicit registration call):
  ```python
  # BEFORE:
  empire.add_fleet(new_fleet)
  session.galaxy.register_fleet(new_fleet)  # PROJ-216: O(1 lookup

  # AFTER:
  empire.add_fleet(new_fleet)  # PROJ-219: Auto-registers via empire._galaxy
  ```
- [ ] Verify: Split fleet command still creates fleets that appear in galaxy registry

**Notes:**

---

### Task 3.3: Clean up SuperweaponOrderProcessor (stellarate) [Simple]
**File:** `game/strategy/engine/superweapon_order_processor.py`
**Tests:** `pytest tests/integration/strategy/test_superweapon_integration.py`

- [ ] Remove line 239 (the explicit unregister - now automatic):
  ```python
  # BEFORE (lines 238-241):
  galaxy.unregister_fleet(victim_fleet)
  owner_empire.remove_fleet(victim_fleet)

  # AFTER:
  owner_empire.remove_fleet(victim_fleet)  # PROJ-219: Auto-unregisters via empire._galaxy
  ```
- [ ] Note: `pop(id, None)` is idempotent, so double-unregister would be safe anyway
- [ ] Verify: Stellarate superweapon still destroys fleets correctly

**Notes:**

---

## Phase Completion Checklist

When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/integration/strategy/production/` - all pass
- [ ] Run `pytest tests/unit/strategy/test_command_handlers.py` - all pass
- [ ] Run `pytest tests/ --testmon` - no regressions
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
