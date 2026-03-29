# Phase 1: Decompose SaveGameService.load_game (CC=26 → ~6)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-209 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Decompose `load_game` into 3 phase-based helpers + consolidate exception handling
**Risk Level:** LOW — linear pipeline, all CC from exception handling, natural phase boundaries
**File:** `game/strategy/systems/save_game_service.py`
**Existing Tests:** ~46 tests (unit + integration)

## Review Findings Addressed
- AR-08: Excessive Exception Handling Breadth (Major)
- CQ-019: Excessive Exception Handling - 7 Try/Except Blocks (Major)
- CQ-020: DRY Violation - Duplicate Error Handling Pattern (Major)
- CQ-021: Redundant Outer Exception Handler (Minor, downgraded)
- CX-004: Duplicate Exception Handler Patterns (Major)
- CX-005: Outer Exception Handler Is Defensive Overkill (Major)
- DS-009: CC Driven by Repetitive Exception Handling (Major)
- DS-010: Outer Exception Handlers Are Redundant (Major)
- TC-006: Relative Path Resolution Not Tested (Major)
- TC-007: Outer Exception Handlers Never Triggered (Major)

---

## Tasks

### Task 1.1: Fill Test Gaps Before Decomposing [Simple] ✅
**Tests:** `tests/unit/strategy/save_game_service/`

- [x] Add test for relative path resolution (TC-006): pass `"my_save"` with `SAVES_DIR` patched, verify correct absolute path used
- [x] Add test triggering helper error handling (TC-007): verify _load_json_safe handles PermissionError
- [x] Run targeted tests: `pytest tests/unit/strategy/save_game_service/ tests/integration/save_load/ -v`
- [x] Verify all new + existing tests pass (29 passed)

### Task 1.2: Extract `_load_json_safe` Shared Helper [Simple] ✅
Consolidate the duplicate 4-exception pattern (JSONDecodeError, FileNotFoundError, PermissionError, OSError) into a single helper.

- [x] Create `_load_json_safe(path, description) -> Tuple[Optional[dict], Optional[str]]`
- [x] Helper wraps `load_json_required` with single 4-exception handler using message template
- [x] Verify: all existing tests still pass

### Task 1.3: Extract `_load_save_metadata` [Simple] ✅
Lines 124-159: path resolution, folder validation, metadata loading, key validation, version check.

- [x] Create `@staticmethod _load_save_metadata(save_path) -> Tuple[Optional[dict], Optional[str]]`
- [x] Move path resolution (isabs check + join) into this method
- [x] Move `_validate_save()` call into this method
- [x] Use `_load_json_safe` for metadata loading
- [x] Move metadata key validation and version compatibility check
- [x] Return `(metadata_dict, None)` on success or `(None, error_msg)` on failure
- [x] Verify: all existing tests still pass

### Task 1.4: Extract `_load_turn_data` [Simple] ✅
Lines 162-191: turn number resolution, turn file loading, state key validation.

- [x] Create `@staticmethod _load_turn_data(save_path, metadata) -> Tuple[Optional[dict], Optional[str]]`
- [x] Resolve turn_number from metadata internally (fallback to `latest_turn_number`)
- [x] Use `_load_json_safe` for turn file loading
- [x] Move state key validation
- [x] Return `(game_state, None)` on success or `(None, error_msg)` on failure
- [x] Verify: all existing tests still pass

### Task 1.5: Extract `_reconstruct_game_session` [Simple] ✅
Lines 194-208: GameSession.from_dict with error handling.

- [x] Create `@staticmethod _reconstruct_game_session(game_state, save_path) -> Tuple[Optional[object], Optional[str]]`
- [x] Move lazy import of GameSession into this method
- [x] Consolidate 3 exception handlers (KeyError, TypeError/ValueError/ValidationException, AttributeError/ImportError/RuntimeError/StateException)
- [x] Return `(session, None)` on success or `(None, error_msg)` on failure
- [x] Verify: all existing tests still pass

### Task 1.6: Simplify `load_game` Orchestrator [Simple] ✅
Rewrite the main function as a clean 3-step pipeline calling the extracted helpers.

- [x] Remove outer try/except entirely (DS-010) — each helper handles its own errors
- [x] `load_game` becomes: call `_load_save_metadata` → call `_load_turn_data` → call `_reconstruct_game_session`
- [x] Each step checks for error and returns early if failed
- [x] Verify orchestrator CC <= 6 (CC=5 achieved)
- [x] Run full test suite: `pytest tests/ -n 12`
- [x] Verify: 12944 passed, 4 failed (pre-existing bug_13), 1 skipped

### Task 1.7: Add Targeted Tests for Extracted Methods [Simple] ✅
- [x] Add direct tests for `_load_json_safe` (success, JSONDecodeError, FileNotFoundError, PermissionError, OSError)
- [x] Add direct tests for `_load_save_metadata` (success, invalid folder, missing keys, incompatible version)
- [x] Add direct tests for `_load_turn_data` (success, missing turn file, corrupt turn file, missing state keys)
- [x] Add direct tests for `_reconstruct_game_session` (success, KeyError, ValidationException)
- [x] Run: `pytest tests/unit/strategy/save_game_service/ -v` (48 passed)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `load_game` orchestrator CC <= 6 (CC=5)
- [x] All extracted helpers CC <= 8 (_load_json_safe=5, _load_save_metadata=6, _load_turn_data=5, _reconstruct_game_session=4)
- [x] All tests pass (full suite): 12944 passed, 4 failed (pre-existing), 1 skipped
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
