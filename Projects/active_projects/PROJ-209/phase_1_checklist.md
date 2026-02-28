# Phase 1: Decompose SaveGameService.load_game (CC=26 → ~6)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-209 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
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

### Task 1.1: Fill Test Gaps Before Decomposing [Simple]
**Tests:** `tests/unit/strategy/save_game_service/`

- [ ] Add test for relative path resolution (TC-006): pass `"my_save"` with `SAVES_DIR` patched, verify correct absolute path used
- [ ] Add test triggering outer PermissionError handler (TC-007): cause error before inner try blocks
- [ ] Run targeted tests: `pytest tests/unit/strategy/save_game_service/ tests/integration/save_load/ -v`
- [ ] Verify all new + existing tests pass

### Task 1.2: Extract `_load_json_safe` Shared Helper [Simple]
Consolidate the duplicate 4-exception pattern (JSONDecodeError, FileNotFoundError, PermissionError, OSError) into a single helper.

- [ ] Create `_load_json_safe(path, description) -> Tuple[Optional[dict], Optional[str]]`
- [ ] Helper wraps `load_json_required` with single 4-exception handler using message template
- [ ] Verify: all existing tests still pass

### Task 1.3: Extract `_load_save_metadata` [Simple]
Lines 124-159: path resolution, folder validation, metadata loading, key validation, version check.

- [ ] Create `@staticmethod _load_save_metadata(save_path) -> Tuple[Optional[dict], Optional[str]]`
- [ ] Move path resolution (isabs check + join) into this method
- [ ] Move `_validate_save()` call into this method
- [ ] Use `_load_json_safe` for metadata loading
- [ ] Move metadata key validation and version compatibility check
- [ ] Return `(metadata_dict, None)` on success or `(None, error_msg)` on failure
- [ ] Verify: all existing tests still pass

### Task 1.4: Extract `_load_turn_data` [Simple]
Lines 162-191: turn number resolution, turn file loading, state key validation.

- [ ] Create `@staticmethod _load_turn_data(save_path, metadata) -> Tuple[Optional[dict], Optional[str]]`
- [ ] Resolve turn_number from metadata internally (fallback to `latest_turn_number`)
- [ ] Use `_load_json_safe` for turn file loading
- [ ] Move state key validation
- [ ] Return `(game_state, None)` on success or `(None, error_msg)` on failure
- [ ] Verify: all existing tests still pass

### Task 1.5: Extract `_reconstruct_game_session` [Simple]
Lines 194-208: GameSession.from_dict with error handling.

- [ ] Create `@staticmethod _reconstruct_game_session(game_state, save_path) -> Tuple[Optional[object], Optional[str]]`
- [ ] Move lazy import of GameSession into this method
- [ ] Consolidate 3 exception handlers (KeyError, TypeError/ValueError/ValidationException, AttributeError/ImportError/RuntimeError/StateException)
- [ ] Return `(session, None)` on success or `(None, error_msg)` on failure
- [ ] Verify: all existing tests still pass

### Task 1.6: Simplify `load_game` Orchestrator [Simple]
Rewrite the main function as a clean 3-step pipeline calling the extracted helpers.

- [ ] Remove outer try/except entirely (DS-010) — each helper handles its own errors
- [ ] `load_game` becomes: call `_load_save_metadata` → call `_load_turn_data` → call `_reconstruct_game_session`
- [ ] Each step checks for error and returns early if failed
- [ ] Verify orchestrator CC <= 6 (manual count or radon)
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify: all 7353+ tests pass, 0 failures

### Task 1.7: Add Targeted Tests for Extracted Methods [Simple]
- [ ] Add direct tests for `_load_json_safe` (success, JSONDecodeError, FileNotFoundError, PermissionError, OSError)
- [ ] Add direct tests for `_load_save_metadata` (success, invalid folder, missing keys, incompatible version)
- [ ] Add direct tests for `_load_turn_data` (success, missing turn file, corrupt turn file, missing state keys)
- [ ] Add direct tests for `_reconstruct_game_session` (success, KeyError, ValidationException)
- [ ] Run: `pytest tests/unit/strategy/save_game_service/ -v`

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `load_game` orchestrator CC <= 6
- [ ] All extracted helpers CC <= 8
- [ ] All tests pass (full suite)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
