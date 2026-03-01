# Phase 3: Remove Redundant Calls

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-219 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove explicit registration/unregistration calls that are now automatic

---

## Tasks

### Task 3.1: Clean up ProductionEngine [Simple]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/integration/strategy/production/`

- [x] Remove lines 641-643 (the conditional galaxy.register_fleet call)
- [x] Verify: Fleet production still creates fleets that appear in galaxy registry

**Notes:** Removed 3-line conditional `if galaxy: galaxy.register_fleet(new_fleet)` block. Now handled by `empire.add_fleet()` auto-registration.

---

### Task 3.2: Clean up CommandHandlers [Simple]
**File:** `game/strategy/engine/command_handlers.py`
**Tests:** `pytest tests/unit/strategy/test_command_handlers.py`

- [x] Remove line 692 (the explicit registration call)
- [x] Verify: Split fleet command still creates fleets that appear in galaxy registry

**Notes:** Removed `session.galaxy.register_fleet(new_fleet)` line. Now handled by `empire.add_fleet()` auto-registration.

---

### Task 3.3: Clean up SuperweaponOrderProcessor (stellarate) [Simple]
**File:** `game/strategy/engine/superweapon_order_processor.py`
**Tests:** `pytest tests/integration/strategy/test_superweapon_integration.py`

- [x] Remove line 239 (the explicit unregister - now automatic)
- [x] Note: `pop(id, None)` is idempotent, so double-unregister would be safe anyway
- [x] Verify: Stellarate superweapon still destroys fleets correctly

**Notes:** Removed `galaxy.unregister_fleet(victim_fleet)` line. Now handled by `empire.remove_fleet()` auto-unregistration.

---

## Phase Completion Checklist

When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/integration/strategy/production/` - all pass
- [x] Run `pytest tests/unit/strategy/test_command_handlers.py` - all pass
- [x] Run `pytest tests/ --testmon` - no regressions
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
