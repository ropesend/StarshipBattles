# Phase 1: Quick Wins & Deprecated Module Removal

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-42 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove obviously dead code and simple compatibility shims with no dependencies
**Complexity:** Simple

---

## Pre-Phase Checklist
- [ ] Read [design.md](design.md) for context
- [ ] Verify baseline: `pytest tests/` passes (5199 tests)

---

## Task 1.1: Delete FleetMovementSimulator Module [Simple]
**Issues:** LPH-002, STR-001
**File:** `game/strategy/engine/fleet_movement.py`
**Tests:** `pytest tests/strategy/`

### Subtasks
- [ ] Verify no imports of `FleetMovementSimulator` exist in production code:
  ```bash
  grep -r "from game.strategy.engine.fleet_movement import" game/
  grep -r "FleetMovementSimulator" game/ --include="*.py"
  ```
- [ ] Delete file: `game/strategy/engine/fleet_movement.py` (331 LOC)
- [ ] Search for any remaining references in comments/docs and update them
- [ ] Run `pytest tests/strategy/` - verify all pass
- [ ] Run `pytest tests/` - verify no regressions

**Notes:**

---

## Task 1.2: Remove GameState Aliases in app.py [Simple]
**Issue:** BCD-007
**File:** `game/app.py`
**Tests:** `pytest tests/`

### Subtasks
- [ ] Remove lines 49-58 (the 9 GameState aliases):
  ```python
  # REMOVE THESE LINES:
  MENU = GameState.MENU
  BUILDER = GameState.BUILDER
  BATTLE = GameState.BATTLE
  BATTLE_SETUP = GameState.BATTLE_SETUP
  FORMATION = GameState.FORMATION
  TEST_LAB = GameState.TEST_LAB
  STRATEGY = GameState.STRATEGY
  RACE_SETUP = GameState.RACE_SETUP
  RESEARCH_TREE = GameState.RESEARCH_TREE
  ```
- [ ] Search for any code using these aliases:
  ```bash
  grep -r "from game.app import MENU\|BUILDER\|BATTLE" game/
  ```
- [ ] Update any found references to use `GameState.X` directly
- [ ] Run `pytest tests/` - verify all pass

**Notes:**

---

## Task 1.3: Remove V1 Modifier Format Detection Code [Simple]
**Issue:** LPH-005
**Files:**
- `game/simulation/components/modifier_schema.py` (lines 42-47)
- `game/simulation/components/modifier_effects.py` (lines 188-195)
**Tests:** `pytest tests/unit/refactor/test_modifier_loader_v2.py`

### Subtasks
- [ ] In `modifier_schema.py`, remove V1 format detection (dict-based effects check)
- [ ] In `modifier_effects.py`, remove V1 format handling branch
- [ ] Add explicit error if non-list effects encountered:
  ```python
  if not isinstance(mod_def.get('effects'), list):
      raise ValueError(f"Modifier '{mod_id}': effects must be a list (V2 format required)")
  ```
- [ ] Run `pytest tests/unit/refactor/test_modifier_loader_v2.py`
- [ ] Run `pytest tests/` - verify all pass

**Notes:**

---

## Task 1.4: Clean Up Commented Migration Code in SaveGameService [Simple]
**Issue:** BCD-005 (partial)
**File:** `game/strategy/systems/save_game_service.py`
**Tests:** `pytest tests/unit/strategy/test_save_game_service.py`

### Subtasks
- [ ] Remove commented-out `_migrate_temp_designs()` method (lines ~114-147)
- [ ] Remove the BUG-29 comment referencing the disabled migration
- [ ] Keep `MIGRATABLE_VERSIONS` list intact (player data protection)
- [ ] Run `pytest tests/unit/strategy/test_save_game_service.py`

**Notes:**

---

## Task 1.5: Document Remaining Minor Patterns for Future Cleanup [Simple]
**Issues:** LPH-011 through LPH-020 (documentation only)
**File:** `decisions.md`
**Tests:** None

### Subtasks
- [ ] Add entry to `decisions.md` documenting patterns kept for now:
  - LPH-011: ShipControllableAdapter (needed for IControllable interface)
  - LPH-012: ShipCombatMixin (thin facade, low priority)
  - LPH-014: ComponentRef tuple methods (backward compat, low priority)
  - LPH-017: total_defense_score alias (UI compatibility)
  - LPH-020: _ProfilerProxy (thread-safety, KEEP)
- [ ] Add entry documenting patterns explicitly kept:
  - _ValidatorProxy (circular import prevention, KEEP)
  - WIDTH/HEIGHT re-exports (64 dependents, KEEP)
  - ValidationResult dual patterns (cross-layer bridge, KEEP)
  - MIGRATABLE_VERSIONS (player data, KEEP)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/` - all tests pass
- [ ] Count deprecation warnings (should be slightly reduced from 28,319)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
- [ ] Commit: "PROJ-42 Phase 1: Remove deprecated FleetMovementSimulator and quick cleanup"
