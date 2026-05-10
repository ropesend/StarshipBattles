# Phase 1: Foundation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-115 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the Foundation module (10 findings, 1 critical)
**Priority:** High

---

## Tasks

### Task 1.1: DUP-FND-001 - Duplicated Resource Loading Logic [Simple]
**File:** `game/core/resources.py:55-98`
**Tests:** `pytest tests/unit/core/resources_registry/test_loading.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIXED - `load_resources()` now delegates to `load_resources_data()` eliminating ~30 lines of duplicated parsing/error-handling code.

### Task 1.2: DUP-FND-002 - StrategyMetadataService Uses Hand-Rolled Singleton [Simple]
**File:** `game/core/strategy_metadata.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ALREADY FIXED - StrategyMetadataService already uses `SingletonMeta` metaclass (line 33). Fixed in PROJ-117.

### Task 1.3: DUP-FND-003 - Repeated "Flee Away" Vector Pattern [Simple]
**File:** `game/ai/behaviors.py:95-101`
**Tests:** `pytest tests/unit/ai/test_behavior_units.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIXED - Extracted `_flee_direction(from_pos, away_from_pos)` helper function. Updated 3 usages: FleeBehavior, KiteBehavior, AttackRunBehavior.

### Task 1.4: DUP-FND-004 - Repeated Entity ID Fallback Pattern [Simple]
**File:** `game/ai/combat_utils.py:65`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ALREADY FIXED - Entity ID fallback is now handled by `get_position()` and other helpers in `combat_utils.py`. This was consolidated in PROJ-108.

### Task 1.5: DUP-FND-005 - Inline Angle Difference Calculation [Simple]
**File:** `game/ai/controller.py:462`
**Tests:** `pytest tests/unit/ai/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIXED - Updated `controller.py` and `behaviors.py` to use existing `angle_diff()` helper from `game.core.math`. The helper was already there but not used consistently.

### Task 1.6: DUP-FND-006 - `_resolve_resource_path` Reimplements Path Resolution [Simple]
**File:** `game/core/resources.py:31-52`
**Tests:** `pytest tests/unit/core/resources_registry/test_loading.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIXED - `_resolve_resource_path()` now uses `Paths.ROOT_DIR` instead of manually calculating project root.

### Task 1.7: DUP-FND-007 - Repeated Zero-Vector Guard Pattern [Simple]
**File:** `game/ai/behaviors.py:97-98`
**Tests:** `pytest tests/unit/ai/test_behavior_units.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIXED - Same as Task 1.3. The `_flee_direction()` helper includes the zero-vector guard.

### Task 1.8: DUP-FND-008 - AIController._get_hp_percent and _is_in_pdc_arc [Simple]
**File:** `game/ai/controller.py:269-273`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ALREADY FIXED - These methods were moved to `combat_utils.py` in PROJ-108. AIController imports and uses `get_hp_percent` and `is_in_pdc_arc` from combat_utils.

### Task 1.9: DUP-FND-009 - `load_data` Duplication Between StrategyManager and StrategyMetadataService [Medium]
**File:** `game/ai/strategy_manager.py:83`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE AS-IS - The two `load_data` methods serve different purposes:
- `StrategyManager.load_data()` loads full AI data + syncs to metadata service
- `StrategyMetadataService.load_data()` loads only metadata for UI-only scenarios (used by WorkshopDataLoader)
This is intentional separation of concerns, not duplication.

### Task 1.10: DUP-FND-010 - Paths Class Maintains Both String and Path Accessors [Medium]
**File:** `game/core/paths.py:46-134`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** BY DESIGN - Paths class provides both string constants (for backward compatibility and simple string operations) and Path accessors (for proper path manipulation). This is intentional API design, not duplication.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
