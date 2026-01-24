# Phase 2: Data Integrity Issues

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-10 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix data loss and integrity issues in save/load system
**Priority:** CRITICAL - Player data at risk

---

## Tasks

### Task 2.1: MOD-STR-01 - Implement Fleet Order Deserialization [Medium]
**File:** `game/strategy/data/fleet.py:669-670`
**Tests:** `pytest tests/unit/strategy/test_fleet.py tests/integration/test_save_load.py`

**Issue:** Fleet orders are saved but never restored from save files. Players lose all pending movement orders when reloading a game. Code has TODO comment indicating this is known incomplete.

**Implementation:**
- [ ] Review Fleet.to_dict() to see how orders are serialized
- [ ] Review Fleet.from_dict() to understand current deserialization
- [ ] Implement two-pass loading:
  - Pass 1: Create fleet stubs with order data
  - Pass 2: Resolve fleet references in orders (for INTERCEPT, JOIN)
- [ ] Handle edge cases: deleted fleets, invalid references
- [ ] Add unit tests for order serialization round-trip
- [ ] Add integration test: save game with orders → load → verify orders intact

**Notes:** This is a data loss bug. Players have likely lost progress due to this.

---

### Task 2.2: MOD-STR-13 - Fix Save Metadata Mismatch Risk [Medium]
**File:** `game/strategy/systems/save_game_service.py:82-100`
**Tests:** `pytest tests/unit/strategy/test_save_game_service.py`

**Issue:** Metadata and game state saved in separate files. If one write fails (disk full, permissions), the save becomes inconsistent. Could corrupt player saves.

**Implementation:**
- [ ] Review current save_game() implementation
- [ ] Option A: Embed metadata in game state JSON (single file)
- [ ] Option B: Use atomic writes (write to temp, rename on success)
- [ ] Add verification after save (read back and validate)
- [ ] Add recovery for partial saves (detect and warn user)
- [ ] Test with simulated disk full / permission denied

**Notes:** Prefer Option B (atomic writes) for backward compatibility.

---

### Task 2.3: ERR-13 - Fix Race Condition in Design Migration [Medium]
**File:** `game/strategy/systems/save_game_service.py:147`
**Tests:** `pytest tests/unit/strategy/test_save_game_service.py`

**Issue:** Design migration failure doesn't prevent save continuation. Could leave game in inconsistent state where designs are lost but save appears successful.

**Implementation:**
- [ ] Review _migrate_temp_designs() and its error handling
- [ ] Return success/failure status from migration
- [ ] Check status before marking save complete
- [ ] If migration fails, rollback or warn user
- [ ] Add test for migration failure scenario

**Notes:** Related to Task 2.2 - both involve save integrity.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Save/load round-trip tests passing
- [ ] Fleet orders persist across save/load
- [ ] No data loss scenarios in testing
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
