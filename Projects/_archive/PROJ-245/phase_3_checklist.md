# Phase 3 Checklist: Replace Full Rebuild with Incremental Updates in BattleEngine
**Status:** Not Started

## Task 3.1: Write integration tests [Medium]
**File:** `tests/integration/simulation/test_grid_incremental.py`
**Tests:** `pytest tests/integration/simulation/test_grid_incremental.py -v`
- [ ] Test: run 100-tick battle with 2 ships, verify grid contains exactly the alive entities after each tick
- [ ] Test: run battle with ship death, verify dead ship is not in grid queries after death tick
- [ ] Test: run battle with projectiles, verify projectile positions in grid are current
- [ ] Test: compare grid query results between incremental and full-rebuild for a 50-tick 4v4 battle
- [ ] Run: tests fail (implementation not done yet)
**Notes:**

## Task 3.2: Extract grid update into helper method [Simple]
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/unit/simulation/systems/test_battle_engine_tick.py -v`
- [ ] Extract L416-423 (the grid rebuild block) into `_update_grid(self) -> None` method
- [ ] Call `self._update_grid()` where the inline code was
- [ ] Run existing battle engine tests -- no regressions
**Notes:**

## Task 3.3: Implement incremental _update_grid() [Medium]
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/integration/simulation/test_grid_incremental.py -v`
- [ ] Replace `_update_grid()` body with incremental logic:
  ```python
  def _update_grid(self) -> None:
      """Update spatial grid incrementally. Only moves entities that changed cells."""
      # Remove dead ships
      for s in self.ships:
          if not s.is_alive:
              self.grid.remove(s)

      # Update alive ships (only those with dirty positions)
      for s in self.ships:
          if s.is_alive and s.grid_dirty:
              self.grid.update(s)
              s.clear_grid_dirty()

      # Update alive projectiles (always move)
      for p in self.projectiles:
          if p.is_alive:
              self.grid.update(p)
          else:
              self.grid.remove(p)
  ```
- [ ] Note: dead entities are removed first, then alive entities updated
- [ ] Note: `grid.update()` handles untracked entities (new projectiles) via insert fallthrough
- [ ] Run: `pytest tests/integration/simulation/test_grid_incremental.py -v` -- pass
- [ ] Run: `pytest tests/unit/simulation/systems/test_battle_engine_tick.py -v` -- pass
**Notes:**

## Task 3.4: Update start() for initial grid population [Simple]
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/unit/simulation/systems/test_battle_engine_tick.py -v`
- [ ] After L300 (end of `start()` method), add initial grid population:
  ```python
  # Initial grid population
  self.grid.clear()
  for s in self.ships:
      self.grid.insert(s)
      s.clear_grid_dirty()
  ```
- [ ] This ensures grid is populated before first tick and all ships start clean
- [ ] Run: `pytest tests/unit/simulation/systems/ -v` -- pass
**Notes:**

## Task 3.5: Run comprehensive test suites [Simple]
- [ ] `pytest tests/unit/ -n 12` -- all unit tests pass
- [ ] `pytest tests/integration/ -n 12` -- all integration tests pass
- [ ] `python -m simulation_tests.run_tests --fast` -- all simulation tests pass
**Notes:**
