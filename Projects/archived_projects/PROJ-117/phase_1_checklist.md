# Phase 1: Foundation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-117 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the Foundation module (14 findings, 1 critical)
**Priority:** High

---

## Tasks

### Task 1.1: LEG-FND-001 - Backward Compatibility Wrapper `load_res [Medium]
**File:** `game/core/resources.py:101-143`
**Tests:** `pytest tests/unit/core/test_resource_loading.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - `load_resources()` is actively called by `app.py` on line 97. Not dead code.

### Task 1.2: LEG-FND-002 - StrategyMetadataService Uses Hand-Rolled [Simple]
**File:** `game/core/strategy_metadata.py`
**Tests:** `pytest tests/unit/core/test_strategy_metadata.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Converted from hand-rolled double-checked locking to SingletonMeta metaclass. Updated test that expected exception on direct instantiation.

### Task 1.3: LEG-FND-003 - Dead Instance Attributes `attack_state` [Simple]
**File:** `game/ai/controller.py:90-91`
**Tests:** `pytest tests/unit/ai/test_ai.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Deleted `self.attack_state` and `self.attack_timer` from AIController.__init__. These were duplicates of attributes in AttackRunBehavior class and never used by AIController.

### Task 1.4: LEG-FND-004 - Duplicate Path Resolution Logic in resou [Simple]
**File:** `game/core/resources.py:31-52`
**Tests:** `pytest tests/unit/core/test_resource_loading.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** NOT DEAD CODE - `_resolve_resource_path` is a utility function that supports optional path override parameter. While Paths module exists, this function enables DI via different file paths.

### Task 1.5: LEG-FND-005 - Unused Protocol Classes and TypeGuard Fu [Simple]
**File:** `game/core/protocols.py:85-110,`
**Tests:** `pytest tests/unit/core/test_protocols.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** NOT DEAD CODE - `ILocatable`, `INamed`, `IOwnable` are composable base protocols. Have tests and are documented as building blocks for future protocol composition.

### Task 1.6: LEG-FND-006 - `LayerType.from_string()` Static Method [Simple]
**File:** `game/core/constants.py:117-119`
**Tests:** `pytest tests/unit/core/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Deleted `LayerType.from_string()` - zero callers found in codebase.

### Task 1.7: LEG-FND-007 - `ScreenshotManager.capture_step()` Never [Simple]
**File:** `game/ui/services/screenshot_manager.py`
**Tests:** `pytest tests/unit/test_screenshot_manager.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** KEEP - `capture_step()` is called in tests (`test_screenshot_manager.py`). It's a debug utility method for capturing draw order debugging.

### Task 1.8: LEG-FND-008 - Python 3.9 Compatibility Shim for TypeGu [Simple]
**File:** `game/core/protocols.py:32-36`
**Tests:** `pytest tests/unit/core/test_protocols.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Removed try/except fallback for `typing_extensions.TypeGuard`. Codebase is Python 3.10+ only.

### Task 1.9: LEG-FND-009 - Color Constants (WHITE, BLACK, BLUE, RED [Simple]
**File:** `game/core/constants.py:42-46`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ALREADY DONE - Colors were moved to `game/ui/colors.py` by PROJ-113. Only a comment remains in constants.py referencing this migration.

### Task 1.10: LEG-FND-010 - `json` Import in resources.py Only Neede [Simple]
**File:** `game/core/resources.py:13`
**Tests:** `pytest tests/unit/core/test_resource_loading.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** NOT DEAD CODE - `json` import is needed for `json.JSONDecodeError` in exception handlers (lines 89, 133).

### Task 1.11: LEG-FND-011 - `_get_hp_percent` and `_is_in_pdc_arc` W [Simple]
**File:** `game/ai/controller.py:269-273`
**Tests:** `pytest tests/unit/ai/ tests/integration/ai_strategy/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Deleted thin wrapper methods. Updated call site to use `get_hp_percent()` directly from `combat_utils`. Fixed 2 integration tests that patched the removed methods.

### Task 1.12: LEG-FND-012 - `FONT_MAIN` Constant Defined but Unused [Simple]
**File:** `game/core/constants.py:49`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ALREADY DONE - `FONT_MAIN` was moved to `game/ui/colors.py` by PROJ-113 and is actively used by 8 files.

### Task 1.13: LEG-FND-013 - `DEBUG_SCREENSHOTS = True` Always Enable [Simple]
**File:** `game/core/constants.py:53`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** INTENTIONAL - `DEBUG_SCREENSHOTS` is a user debug feature. Leaving as `True` is the intended default to enable screenshot functionality.

### Task 1.14: LEG-FND-014 - `profiling.py` Comment References "backw [Simple]
**File:** `game/core/profiling.py:104`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Updated stale comment from "Global accessor for backwards compatibility" to "Module-level decorators and context managers for convenient profiling".


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
