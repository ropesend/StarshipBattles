# Phase 5: Test Reorganization

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-36 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Ensure test organization matches new architecture

---

## Tasks

### Task 5.1: Reorganize test files [Simple]
**Tests:** `pytest tests/`

- [ ] Verify `test_turn_engine.py` only tests orchestration:
  - Should have ~100 lines of tests (down from 1,207)
  - Should test `process_turn` calls all phases
  - Should test tick loop runs 100 times
  - Should NOT have combat, resource, or validation tests
- [ ] Verify `test_conflict_resolution_engine.py` has all combat tests:
  - All `TestCombatResolution` tests
  - All `TestBattleResolverInjection` tests
  - New multi-empire combat tests
- [ ] Verify `test_resource_management_engine.py` has all resource tests:
  - All `TestPerTurnResources` tests
  - All auto-disable tests
  - New cascade/edge case tests
- [ ] Verify `tests/unit/strategy/validation/test_colonize_validator.py` has colonize tests:
  - All colonize validation tests
  - New stale validation tests
- [ ] Remove any orphaned tests from `test_turn_engine.py`
- [ ] Run `pytest tests/ --cov=game/strategy/engine` to check coverage

**Notes:**

---

### Task 5.2: Add missing edge case tests [Simple]
**Tests:** Various test files

- [ ] Add battle seed determinism test (same seed = same result):
  **File:** `test_conflict_resolution_engine.py`
  ```python
  def test_battle_seed_determinism():
      """Same seed should produce same battle results."""
      engine1 = ConflictResolutionEngine(mock_resolver)
      engine2 = ConflictResolutionEngine(mock_resolver)
      # Both should return same result with same seed
  ```

- [ ] Add resource rounding error test (100 ticks, verify no phantom loss):
  **File:** `test_resource_management_engine.py`
  ```python
  def test_no_rounding_errors_over_100_ticks():
      """Resource consumption should not lose or gain resources to rounding."""
      # Ship with 100 fuel, costs 7 per turn
      # After 100 ticks: should have exactly 93 fuel
  ```

- [ ] Add multi-empire combat ordering test:
  **File:** `test_conflict_resolution_engine.py`
  ```python
  def test_three_empire_combat_at_same_hex():
      """Three empires at same hex should all participate in combat."""
  ```

- [ ] Add component cascade disable test:
  **File:** `test_resource_management_engine.py`
  ```python
  def test_multiple_resources_deplete_same_tick():
      """Multiple resource types depleting same tick should disable all relevant components."""
  ```

**Notes:**

---

### Task 5.3: Integration test verification [Simple]
**Tests:** `pytest tests/integration/ tests/strategy/`

- [ ] Run `test_gameplay_loop.py`:
  ```bash
  pytest tests/integration/test_gameplay_loop.py -v
  ```
  - Verify full turn cycle works
  - Verify all 100 ticks process correctly
  - Verify end-of-turn orders execute

- [ ] Run `test_colonization.py`:
  ```bash
  pytest tests/integration/test_colonization.py -v
  ```
  - Verify colonization workflow end-to-end
  - Verify validation → execution flow

- [ ] Run `test_resource_system.py`:
  ```bash
  pytest tests/strategy/test_resource_system.py -v
  ```
  - Verify resource consumption
  - Verify auto-disable on depletion

- [ ] Run `test_fleet_combat.py`:
  ```bash
  pytest tests/integration/test_fleet_combat.py -v
  ```
  - Verify battle resolution
  - Verify damage application

- [ ] Verify no test failures across full suite:
  ```bash
  pytest tests/ -v --tb=short
  ```

**Notes:**

---

### Task 5.4: Final verification [Simple]
**Tests:** Full test suite

- [ ] Run full test suite with coverage:
  ```bash
  pytest tests/ --cov=game/strategy/engine --cov-report=term-missing
  ```
- [ ] Verify coverage is maintained (should be same or better than before)
- [ ] Manual test: Load strategy game, play 5 turns:
  - Start new game or load existing
  - Advance 5 turns
  - Verify no crashes
  - Verify combat resolves correctly
  - Verify resource consumption works
  - Verify colonization works
- [ ] Document any issues found in Notes section

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Test organization matches architecture
- [ ] All edge case tests added
- [ ] All integration tests pass
- [ ] Coverage maintained or improved
- [ ] Manual testing passed
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"
