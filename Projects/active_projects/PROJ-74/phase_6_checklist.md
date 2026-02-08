# Phase 6: End-to-End Testing

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-74 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Verify complete resupply flow with integration and save/load tests

---

## Tasks

### Task 6.1: Create integration test scenario [Simple]
**File:** `tests/integration/strategy/test_resupply_system.py` (NEW)
**Tests:** `pytest tests/integration/strategy/test_resupply_system.py`

- [ ] Create test file with comprehensive fixtures

- [ ] Write `test_complete_resupply_flow`:
  ```python
  def test_complete_resupply_flow(empire_with_colony, galaxy, registries):
      """Test the complete fuel synthesis and resupply workflow."""
      # 1. Create empire with colony
      empire = empire_with_colony
      colony = empire.colonies[0]

      # 2. Build complex with fuel synthesizer + fuel tank
      # (Use test fixtures to add facility with design_data)

      # 3. Create fleet at colony location with partial fuel

      # 4. Process multiple turns

      # 5. Verify:
      #    - Fuel accumulated in complex
      #    - Fleet refueled
      #    - Range equalization worked
  ```

- [ ] Write `test_range_equalization_example`:
  - Create fleet with ships of different fuel profiles
  - Process resupply
  - Verify all ships have same effective range
  - Verify tanker partially fueled, combat ships full

- [ ] Verify: All tests pass

**Notes:**

---

### Task 6.2: Save/load integration test [Simple]
**File:** `tests/integration/save_load/test_resupply_persistence.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_resupply_persistence.py`

- [ ] Write `test_facility_fuel_persists_across_save_load`:
  ```python
  def test_facility_fuel_persists_across_save_load(game_session, save_path):
      """Verify facility fuel levels survive save/load cycle."""
      # 1. Create facility with fuel
      # 2. Save game
      # 3. Load game
      # 4. Verify fuel level matches
  ```

- [ ] Write `test_partial_fuel_ships_persist_across_save_load`:
  ```python
  def test_partial_fuel_ships_persist_across_save_load(game_session, save_path):
      """Verify partial ship fuel levels survive save/load cycle."""
      # 1. Create fleet with partial fuel
      # 2. Save game
      # 3. Load game
      # 4. Verify fuel levels match
  ```

- [ ] Verify: All tests pass

**Notes:**

---

### Task 6.3: Manual verification [Simple]
**Tests:** Manual testing in game

- [ ] Start new game
- [ ] Colonize a planet
- [ ] Build complex with fuel_synthesizer and fuel_tank components
- [ ] Wait several turns, verify fuel accumulates in complex
- [ ] Create fleet at planet with ships that have partial fuel
- [ ] Verify fleet gets refueled when at planet
- [ ] Move fleet away, verify fuel consumed normally
- [ ] Save and load game, verify fuel levels persist

**Notes:**

---

### Task 6.4: Full test suite verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify: All tests pass (6651+ passed)
- [ ] Document any new tests added

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ -n 12` - full suite passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete"
- [ ] Update plan.md Verification section - all items checked
