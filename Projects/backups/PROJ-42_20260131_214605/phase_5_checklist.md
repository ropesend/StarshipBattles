# Phase 5: BattleEngine & Scattered Compat Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-42 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove legacy controller creation paths, centralize compat code
**Complexity:** Medium

---

## Pre-Phase Checklist
- [x] Phase 4 complete
- [x] Read [design.md](design.md) - review "BattleEngine Legacy Paths" and "Scattered Compat Code" sections
- [x] Verify: `pytest tests/` passes

---

## Task 5.1: BattleEngine Legacy Controller Creation Path [Medium]
**Issue:** LPH-009
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/unit/simulation/test_battle*.py tests/integration/`

### Subtasks
- [x] Locate legacy controller creation (lines 257-280)
- [x] Decision: Keep legacy path but add DeprecationWarning
  - Making it required would break ~100 test files
  - Proper path is via BattleOrchestrator or ai_factory
- [x] Added deprecation warning pointing to PROJ-17/PROJ-43
- [x] Run tests: All pass with deprecation warnings

**Notes:** Legacy path kept with deprecation warning. Tests use this path for simplicity,
but production code should use BattleOrchestrator.

---

## Task 5.2: Reinforcement Legacy Path [Simple]
**Issue:** LPH-009 (related)
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/unit/simulation/test_battle*.py`

### Subtasks
- [x] Locate legacy reinforcement path (lines 319-333)
- [x] Added deprecation warning pointing to PROJ-17/PROJ-43
- [x] Also documented fighter launch path (acceptable during battle)
- [x] Run tests: All pass

**Notes:** Same approach as Task 5.1 - deprecation warning added.
Fighter launch path documented as acceptable (no orchestrator available during battle).

---

## Task 5.3: PathSegment 'hex' Field [Simple]
**Issue:** STR-005 (partial)
**File:** `game/strategy/services/fleet_navigation_service.py`
**Tests:** `pytest tests/strategy/`

### Subtasks
- [x] Locate 'hex' field in `PathSegment.to_dict()` (line 91)
- [x] Search for usage: Found in `pathfinding.py` lines 336, 428
- [x] Decision: Keep - used internally by intercept calculation
- [x] Updated docstring to clarify it's internal API consistency, not external compat
- [x] Run tests: All pass

**Notes:** The 'hex' field IS used internally by pathfinding.py for intercept
calculations. Kept with updated documentation clarifying this is internal
consistency, not external backward compatibility.

---

## Task 5.4: _ChaserProxy Adapter [Medium]
**Issue:** STR-005
**File:** `game/strategy/data/pathfinding.py`
**Tests:** `pytest tests/strategy/`

### Subtasks
- [x] Locate `_ChaserProxy` class (lines 275-291)
- [x] Understand purpose: Adapter for Fleet/NavigationState -> fleet-like interface
- [x] Decision: Keep as proper adapter pattern
  - It's not legacy code - it's a clean adapter allowing NavigationState
    to work with find_hybrid_path()
- [x] Enhanced docstring documenting the adapter pattern
- [x] Run tests: All pass

**Notes:** _ChaserProxy is a legitimate adapter pattern, not legacy compat.
It normalizes Fleet and NavigationState objects for pathfinding functions.
Documented and kept.

---

## Task 5.5: Fleet Order Format Deserializer [Medium]
**Issue:** STR-005
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/strategy/test_fleet*.py`

### Subtasks
- [x] Locate multi-format deserializer (lines 604-623)
- [x] Analyze formats:
  1. `{'q': x, 'r': y}` - HexCoord.to_dict() format
  2. `{'type': 'coord', 'value': [x, y]}` - Tuple coordinate format
  3. `{'type': 'fleet_ref', 'id': xxx}` - Fleet reference
  4. `{'type': 'raw', 'value': str}` - Fallback string
- [x] Decision: Keep all formats for save file compatibility
  - All formats are valid serialization outputs
  - Removing would break existing save files
- [x] Added documentation explaining all formats
- [x] Run tests: All pass

**Notes:** Multi-format support is intentional for save game compatibility.
All formats are produced by FleetOrder.to_dict() under different conditions.
Documented and kept.

---

## Task 5.6: Legacy Crew Requirement Pattern [Simple]
**Issue:** BCD-008
**File:** `game/ui/screens/builder/stats_config.py`
**Tests:** `pytest tests/unit/ui/`

### Subtasks
- [x] Locate `_get_legacy_crew_requirement()` function (lines 67-78)
- [x] Search for negative CrewCapacity in components.json: None found
  - All CrewCapacity values are positive (10, 1, 10)
- [x] Removed `_get_legacy_crew_requirement()` function
- [x] Simplified `_get_total_crew_requirement()` to just use CrewRequired
- [x] Added note about removal in PROJ-42
- [x] Run tests: All pass

**Notes:** No components use negative CrewCapacity. Removed legacy function
and simplified to use only CrewRequired ability.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/` - 5360 passed, 3 skipped
- [x] BattleEngine legacy paths have deprecation warnings
- [x] _ChaserProxy documented as proper adapter pattern
- [x] Fleet order formats documented for save compatibility
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 6
- [ ] Commit: "PROJ-42 Phase 5: Clean up BattleEngine and scattered compat code"
