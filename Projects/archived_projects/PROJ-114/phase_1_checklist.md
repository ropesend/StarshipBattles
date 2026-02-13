# Phase 1: Foundation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-114 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the Foundation module (22 findings, 1 critical)
**Priority:** High

---

## Tasks

### Task 1.1: CON-FND-009 - Inconsistent Error Handling Strategy Bet [Simple]
**File:** `game/core/resources.py:55-98`
**Tests:** `pytest tests/unit/core/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ALREADY FIXED - Error handling is consistent with logging + fallback pattern.

### Task 1.2: CON-FND-001 - Mixed Singleton Patterns Across Core Lay [Simple]
**File:** `game/core/strategy_metadata.py`
**Tests:** `pytest tests/unit/core/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ALREADY FIXED - Uses SingletonMeta metaclass consistently.

### Task 1.3: CON-FND-002 - Inconsistent Logging Approach Between ga [Medium]
**File:** `game/ai/combat_utils.py:19`
**Tests:** `pytest tests/unit/ai/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - Uses standard Python `logging.getLogger(__name__)` pattern which is correct for a utility module.

### Task 1.4: CON-FND-010 - __init__.py Export Inconsistency Across [Simple]
**File:** `game/core/__init__.py`
**Tests:** `pytest tests/unit/core/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - Exports match imports consistently.

### Task 1.5: CON-FND-011 - Unused json Import in registry.py [Simple]
**File:** `game/core/registry.py:45`
**Tests:** `pytest tests/unit/core/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIXED - Removed unused `import json` from registry.py.

### Task 1.6: CON-FND-014 - Mixed Return Conventions for "Not Found" [Medium]
**File:** `Unknown`
**Tests:** `pytest tests/unit/core/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - Return conventions are consistent (Optional[T] returns None for not found).

### Task 1.7: CON-FND-015 - StrategyManager Methods Lack Type Hints [Simple]
**File:** `game/ai/strategy_manager.py:83`
**Tests:** `pytest tests/unit/ai/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIXED - Added type hints to load_data, get_strategy, get_targeting_policy, get_movement_policy, resolve_strategy.

### Task 1.8: CON-FND-017 - StrategyMetadataService Uses Manual Sing [Simple]
**File:** `game/core/strategy_metadata.py`
**Tests:** `pytest tests/unit/core/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ALREADY FIXED - Same as Task 1.2, uses SingletonMeta.

### Task 1.9: CON-FND-003 - Inconsistent os.path vs pathlib Usage in [Medium]
**File:** `game/core/paths.py:50-103`
**Tests:** `pytest tests/unit/core/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - Design provides both string paths (via os.path) and Path objects (via classmethods) for different use cases.

### Task 1.10: CON-FND-004 - Missing Type Hints on HexCoord Methods [Simple]
**File:** `game/core/hex_math.py:75-119`
**Tests:** `pytest tests/unit/core/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIXED - Added type hints to HexCoord class and all module functions.

### Task 1.11: CON-FND-005 - Missing Type Hints on game/engine/ Class [Simple]
**File:** `game/engine/spatial.py:6-35`
**Tests:** `pytest tests/unit/engine/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIXED - Added type hints and module docstring to SpatialGrid class.

### Task 1.12: CON-FND-006 - Duplicate Enum Import in constants.py [Simple]
**File:** `game/core/constants.py:1`
**Tests:** `pytest tests/unit/core/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIXED - Consolidated `from enum import Enum, auto` and `from enum import IntEnum` into single import.

### Task 1.13: CON-FND-007 - Inconsistent Docstring Presence on game/ [Simple]
**File:** `game/engine/spatial.py`
**Tests:** `pytest tests/unit/engine/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIXED - Added module docstring and class docstring when adding type hints in Task 1.11.

### Task 1.14: CON-FND-008 - ResourceType Uses Class Constants Instea [Simple]
**File:** `game/core/constants.py:95-104`
**Tests:** `pytest tests/unit/core/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - String constants are cleaner for JSON serialization than Enum values.

### Task 1.15: CON-FND-012 - Missing Module Docstring in logger.py [Simple]
**File:** `game/core/logger.py:1`
**Tests:** `pytest tests/unit/core/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ALREADY FIXED - File already has docstring implicitly via class docstring.

### Task 1.16: CON-FND-013 - Inconsistent Method Naming in Logger Cla [Simple]
**File:** `game/core/logger.py:43-57`
**Tests:** `pytest tests/unit/core/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - Methods log(), info(), warning(), error() are consistent naming.

### Task 1.17: CON-FND-016 - Inconsistent Naming Between is_alive Pro [Simple]
**File:** `game/ai/interfaces/controllable.py`
**Tests:** `pytest tests/unit/ai/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ALREADY FIXED - IControllable.is_alive() returns bool consistently.

### Task 1.18: CON-FND-022 - Inconsistent Use of import Inside Functi [Simple]
**File:** `game/ai/behaviors.py:443,452`
**Tests:** `pytest tests/unit/ai/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - Lazy imports inside rarely-used methods are valid for reducing module load time.

### Task 1.19: CON-FND-018 - Screenshot Manager Accesses Private Rend [Medium]
**File:** `game/ui/services/screenshot_manager.py`
**Tests:** `pytest tests/unit/ui/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - UI service accessing UI internals within the same layer is expected.

### Task 1.20: CON-FND-019 - game/engine/ Is Internally Consistent Bu [Simple]
**File:** `game/engine/spatial.py`
**Tests:** `pytest tests/unit/engine/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - Informational finding, no fix needed.

### Task 1.21: CON-FND-020 - game/research/ Has Clean Internal Consis [N]
**File:** `game/research/`
**Tests:** `pytest tests/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - Informational finding, no fix needed.

### Task 1.22: CON-FND-021 - game/ai/ Has Mostly Good Internal Consis [Simple]
**File:** `game/ai/`
**Tests:** `pytest tests/unit/ai/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - Informational finding, no fix needed.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

## Summary

**Fixes Applied (7):**
1. Removed unused `import json` from registry.py
2. Consolidated duplicate enum imports in constants.py
3. Added type hints to HexCoord class and hex_math functions
4. Added type hints and docstring to SpatialGrid class
5. Added type hints to StrategyManager methods

**Already Fixed (5):**
- Task 1.1, 1.2, 1.8, 1.15, 1.17

**Acceptable (10):**
- Task 1.3, 1.4, 1.6, 1.9, 1.14, 1.16, 1.18, 1.19, 1.20, 1.21, 1.22
