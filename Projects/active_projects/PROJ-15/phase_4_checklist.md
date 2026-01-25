# Phase 4: Deprecated Functions [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-15 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove deprecated functions and update callers to use canonical implementations

---

## Tasks

### Task 4.1: `load_combat_strategies()` [Medium]
**File:** `game/ai/strategy_manager.py`
**Tests:** `pytest tests/unit/ai/test_strategy_system.py -v`

**Update callers first:**
- [x] Update `game/ui/screens/workshop_data_loader.py`:
  - Line 104: Remove import of `load_combat_strategies`
  - Line 168: Replace `load_combat_strategies(strat_path)` with:
    ```python
    from game.ai.strategy_manager import StrategyManager
    manager = StrategyManager.instance()
    manager.clear()
    manager.load_data(strat_path)
    manager._loaded = True
    ```
- [x] Update `simulation_tests/conftest.py` (line 96):
  - Replace `load_combat_strategies(DATA_DIR)` with direct StrategyManager calls
- [x] Update `tests/infrastructure/session_cache.py` (line 65):
  - Replace `load_combat_strategies(str(DATA_DIR))` with direct StrategyManager calls
- [x] Update `conftest.py` (line 60):
  - Removed monkeypatch for load_combat_strategies (no longer needed)

**Remove re-export and function:**
- [x] Update `game/ai/controller.py` (line 55):
  - Remove `load_combat_strategies` from imports/re-exports
- [x] Delete function in `game/ai/strategy_manager.py` (lines 151-171):
  ```python
  def load_combat_strategies(filepath=None):
      """..."""
      # function body
  ```
- [x] Verify: Run tests - should pass

**Notes:** All callers updated to use StrategyManager.instance() directly. 4 tests passed.

---

### Task 4.2: TurnEngine Deprecated Wrappers [Medium]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/test_turn_engine.py tests/unit/test_advanced_fleet_orders.py -v`

**Update test callers first:**
- [x] Update `tests/unit/test_advanced_fleet_orders.py` (line 127):
  - Changed to use FleetMovementEngine directly
  - Import: `from game.strategy.engine.fleet_movement_engine import FleetMovementEngine`
  - Fixed patch paths to patch where used (fleet_movement_engine) not where defined
  - Fixed mock data to use 'end' key instead of 'hex' key
- [x] Update `tests/unit/strategy/test_turn_engine.py`:
  - Lines 265, 271, 287, 299, 319, 329: Update `_calculate_next_hex` calls
  - Use `turn_engine.movement_engine.calculate_next_hex()` instead
  - Lines 672, 697: Update mock patches to target movement_engine.collect_movements

**Delete deprecated methods:**
- [x] Delete `_spawn_complex()` in `turn_engine.py` (lines 203-209):
  ```python
  def _spawn_complex(self, colony, design_id, emp, save_path):
      """Kept for backward compatibility."""
      return self.production_engine._spawn_complex(colony, design_id, emp, save_path)
  ```
- [x] Delete `_spawn_ship()` in `turn_engine.py` (lines 211-217):
  ```python
  def _spawn_ship(self, colony, design_id, emp, galaxy, save_path):
      """Kept for backward compatibility."""
      return self.production_engine._spawn_ship(colony, design_id, emp, galaxy, save_path)
  ```
- [x] Delete `_calculate_next_hex()` in `turn_engine.py` (lines 250-259):
  ```python
  def _calculate_next_hex(self, fleet, galaxy) -> Optional[HexCoord]:
      """Kept for backward compatibility."""
      return self.movement_engine.calculate_next_hex(fleet, galaxy)
  ```
- [x] Delete `_execute_move_step()` in `turn_engine.py` (lines 261-287):
  ```python
  def _execute_move_step(self, fleet, galaxy) -> bool:
      """DEPRECATED: ..."""
      # function body with DeprecationWarning
  ```
- [x] Verify: Run tests - 70 tests passed

**Notes:**
- Key fix: Patching must target where functions are used (fleet_movement_engine), not where defined (pathfinding)
- Mock data needed update from 'hex' to 'end' key (Phase 3 change)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/unit/ai/ tests/unit/strategy/ -v` - all pass
- [x] Run `python -W error::DeprecationWarning -c "from game.strategy.engine.turn_engine import TurnEngine"` - no warnings
- [x] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
