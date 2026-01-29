# Phase 5: BattleEngine & Scattered Compat Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-42 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove legacy controller creation paths, centralize compat code
**Complexity:** Medium

---

## Pre-Phase Checklist
- [ ] Phase 4 complete
- [ ] Read [design.md](design.md) - review "BattleEngine Legacy Paths" and "Scattered Compat Code" sections
- [ ] Verify: `pytest tests/` passes

---

## Task 5.1: Remove BattleEngine Legacy Controller Creation Path [Medium]
**Issue:** LPH-009
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/unit/simulation/test_battle*.py tests/integration/`

### Subtasks
- [ ] Locate legacy controller creation (lines 227-241):
  ```python
  else:
      # Legacy path: create controllers internally (backward compatibility)
      from game.ai.controller import AIController
  ```
- [ ] Make `ai_controllers` parameter required in `start()` method
- [ ] Remove the else branch that creates controllers internally
- [ ] Update any callers that don't provide ai_controllers:
  ```bash
  grep -r "battle_engine\.start\|BattleEngine.*start" game/ --include="*.py"
  ```
- [ ] Ensure BattleOrchestrator is the only path for controller creation
- [ ] Run tests: `pytest tests/unit/simulation/test_battle*.py`

**Notes:**

---

## Task 5.2: Remove Reinforcement Legacy Path [Simple]
**Issue:** LPH-009 (related)
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/unit/simulation/test_battle*.py`

### Subtasks
- [ ] Locate legacy reinforcement path (lines 284-289):
  ```python
  else:
      # Legacy path: create controller internally
  ```
- [ ] Make `ai_controller` parameter required in `add_ship_mid_battle()` method
- [ ] Remove the else branch
- [ ] Update any callers that don't provide ai_controller
- [ ] Run tests: `pytest tests/unit/simulation/test_battle*.py`

**Notes:**

---

## Task 5.3: Centralize PathSegment 'hex' Field Compatibility [Simple]
**Issue:** STR-005 (partial)
**File:** `game/strategy/services/fleet_navigation_service.py`
**Tests:** `pytest tests/strategy/`

### Subtasks
- [ ] Locate 'hex' field in `PathSegment.to_dict()` (lines 84-91):
  ```python
  'hex': self.end  # Legacy field for backward compatibility
  ```
- [ ] Decide on approach:
  - Option A: Keep 'hex' field if UI/other code still uses it (search first)
  - Option B: Remove if no longer used
- [ ] Search for 'hex' field usage:
  ```bash
  grep -r "segment\['hex'\]\|\.get('hex')" game/ --include="*.py"
  ```
- [ ] Implement chosen approach
- [ ] Run tests: `pytest tests/strategy/`

**Notes:**

---

## Task 5.4: Remove _ChaserProxy, Use Proper Adapter [Medium]
**Issue:** STR-005
**File:** `game/strategy/data/pathfinding.py`
**Tests:** `pytest tests/strategy/`

### Subtasks
- [ ] Locate `_ChaserProxy` class (lines 275-283)
- [ ] Understand its purpose: Normalizes Fleet vs NavigationState interface
- [ ] Option A: Define proper protocol/interface that both implement
- [ ] Option B: Create utility function that extracts needed data
- [ ] Refactor `calculate_intercept_point()` to not need proxy class
- [ ] Remove `_ChaserProxy` class
- [ ] Run tests: `pytest tests/strategy/`

**Notes:**

---

## Task 5.5: Simplify Fleet Order Format Deserializer [Medium]
**Issue:** STR-005
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/strategy/test_fleet*.py`

### Subtasks
- [ ] Locate multi-format deserializer (lines 604-616):
  ```python
  if isinstance(target_data, dict):
      if 'q' in target_data and 'r' in target_data:  # Format 1
      elif target_data.get('type') == 'coord':        # Format 2
      elif target_data.get('type') == 'fleet_ref':    # Format 3
      elif target_data.get('type') == 'raw':          # Format 4
  ```
- [ ] Determine which formats are actually used in saves (search test data)
- [ ] Remove support for unused formats
- [ ] Standardize on one canonical format for new saves
- [ ] Add explicit error for unsupported formats
- [ ] Run tests: `pytest tests/strategy/test_fleet*.py`

**Notes:**

---

## Task 5.6: Clean Up Legacy Crew Requirement Pattern [Simple]
**Issue:** BCD-008
**File:** `game/ui/screens/builder/stats_config.py`
**Tests:** `pytest tests/unit/ui/`

### Subtasks
- [ ] Locate `_get_legacy_crew_requirement()` function (lines 67-83)
- [ ] Search for components using negative CrewCapacity:
  ```bash
  grep -r "CrewCapacity.*-\|negative.*crew" data/ game/ --include="*.json" --include="*.py"
  ```
- [ ] If no components use negative CrewCapacity:
  - Remove `_get_legacy_crew_requirement()` function
  - Simplify `_get_total_crew_requirement()` to just use CrewRequired
- [ ] If some components still use it:
  - Document which ones
  - Plan component migration for future
- [ ] Run tests: `pytest tests/unit/ui/`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/` - all tests pass
- [ ] Verify BattleEngine has single controller creation path
- [ ] Verify _ChaserProxy removed or documented why kept
- [ ] Verify fleet order format simplified
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6
- [ ] Commit: "PROJ-42 Phase 5: Clean up BattleEngine and scattered compat code"
