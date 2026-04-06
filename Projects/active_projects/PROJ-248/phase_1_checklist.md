# PROJ-248 Phase 1: Fix Mutable Cache Return and Update Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> Run: `pytest tests/unit/simulation/entities/test_ship_component_manager.py -x`

## Objective
Return defensive copy from weapon cache, prove mutation safety.

## Status: COMPLETE

---

### Task 1.1: Return Defensive Copy [Simple]
**File:** `game/simulation/entities/ship_component_manager.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_component_manager.py -x`

- [x] Line 239: Change `return self._weapons_cache` to `return list(self._weapons_cache)`
- [x] Add comment: `# Defensive copy (see get_all_components)`

### Task 1.2: Update Identity Test [Simple]
**File:** `tests/unit/simulation/entities/test_ship_component_manager.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_component_manager.py -x`

- [x] Line 254: Change `assert weapons1 is weapons2` to `assert weapons1 == weapons2`
- [x] Add new test `test_weapon_cache_mutation_does_not_corrupt`

### Task 1.3: Verify No Regressions [Simple]
- [x] Run `pytest tests/unit/simulation/entities/test_ship_component_manager.py -x` — 25 passed
- [x] Run `python -m simulation_tests.run_tests --fast --no-history` — 162 passed, 0 failed
