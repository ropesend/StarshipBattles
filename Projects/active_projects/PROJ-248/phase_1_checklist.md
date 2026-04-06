# PROJ-248 Phase 1: Fix Mutable Cache Return and Update Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> Run: `pytest tests/unit/simulation/entities/test_ship_component_manager.py -x`

## Objective
Return defensive copy from weapon cache, prove mutation safety.

## Status: Not Started

---

### Task 1.1: Return Defensive Copy [Simple]
**File:** `game/simulation/components/ship_component_manager.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_component_manager.py -x`

- [ ] Line 239: Change `return self._weapons_cache` to `return list(self._weapons_cache)`
- [ ] Add comment: `# Defensive copy — callers must not mutate (see get_all_components pattern at line 188)`

### Task 1.2: Update Identity Test [Simple]
**File:** `tests/unit/simulation/entities/test_ship_component_manager.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_component_manager.py -x`

- [ ] Line 254: Change `assert weapons1 is weapons2` to `assert weapons1 == weapons2`
- [ ] Add new test `test_weapon_cache_mutation_does_not_corrupt`:
  ```python
  def test_weapon_cache_mutation_does_not_corrupt(self, ship_with_weapons):
      weapons = ship_with_weapons.component_manager.get_weapon_components_cached(tick=1)
      weapons.clear()  # Mutate the returned list
      weapons2 = ship_with_weapons.component_manager.get_weapon_components_cached(tick=1)
      assert len(weapons2) > 0  # Cache unaffected
  ```

### Task 1.3: Verify No Regressions [Simple]
- [ ] Run `pytest tests/ --testmon` — all pass
- [ ] Run `python -m simulation_tests.run_tests --fast --no-history` — all pass
