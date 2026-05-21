# Phase 3: Minor hardening

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-466 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Apply the 15 verified MINOR hardening items from audit `2026-05-20_065518_error-audit`: domain-exception swaps, safe DTO `__repr__` overrides, defensive logging, base-class consistency, and a file-I/O JSON swap. None change observable behavior beyond improved diagnosability and contract compliance.

---

## Tasks

### Task 3.1: Domain exceptions in component_activation_state [Simple]
**File:** `game/strategy/data/component_activation_state.py`
**Tests:** `pytest tests/ -k component_activation`

- [x] In `from_dict` (lines 136-144), use `require_keys(data, ['phase'], 'ComponentActivationState')` and raise `PersistenceException(..., code=ErrorCode.CORRUPT_DATA.value, ...)` instead of the implicit bare `KeyError` on `data['phase']`
- [x] In `start_activating` (line 77) and `start_deactivating` (line 93), replace the generic `raise ValueError(...)` with `StateException(...)` carrying `current_phase`/`expected_phase` context
- [x] Verify: `pytest` passes

### Task 3.2: Domain exception in fleet_write_service [Simple]
**File:** `game/strategy/services/fleet_write_service.py`
**Tests:** `pytest tests/ -k fleet_write`

- [x] Replace `raise NotImplementedError(...)` at lines 57 (`set_location`) and 65 (`set_path`) with `ValidationException(..., code=ErrorCode.MISSING_DEPENDENCY.value, ...)` (or `StateException(NOT_INITIALIZED)`)
- [x] Verify: `pytest` passes

### Task 3.3: Safe __repr__ for LLM DTOs [Simple]
**File:** `game/services/llm/types.py`
**Tests:** `pytest tests/ -k "llm and types"` or `pytest tests/unit/services/llm/`

- [x] Add a `__repr__` to `CompletionResult` (line 63) that reports `text_len`/`model`/`finish_reason`/`latency`/`tokens` instead of the full response `text`
- [x] Add a `__repr__` to `Message` (line 41) that reports `role` + `content_len` instead of the full prompt `content`
- [x] Verify: `pytest` passes; `repr()` of these DTOs no longer exposes text/content

### Task 3.4: Safe __repr__ for Image DTO [Simple]
**File:** `game/ui/services/image/types.py`
**Tests:** `pytest tests/unit/ui/services/image/`

- [x] Add a `__repr__` to `ImageResult` (line 14) that reports `model`/`size`/`latency_ms`/`provider`/`bytes_len` instead of dumping raw `image_bytes` + `revised_prompt`
- [x] Verify: `pytest` passes

### Task 3.5: %r -> %s in worker-thread exception logs [Simple]
**File:** `game/services/llm/background.py`
**Tests:** `pytest tests/unit/services/llm/`

- [x] Change `logger.exception("...: %r", e)` (line 293) to `%s`
- [x] Apply the same `%r` -> `%s` change in `game/ui/services/image/background.py` (line 226) — covered here so both worker logs land in one task
- [x] Verify: `pytest` passes

### Task 3.6: asset_manager OSError parity + manifest log level [Simple]
**File:** `game/assets/asset_manager.py`
**Tests:** `pytest tests/ -k asset_manager`

- [x] Add `OSError` to the `load_planet_image` except tuple (line 319) for parity with `load_star_image` (PROJ-381 ERR-02-001)
- [x] In `load_manifest` (lines 58-60), downgrade the missing-manifest `logger.error` to `logger.warning` (optional asset) or raise `MissingResourceException` (if treated as required config) — pick one and document the choice in the task notes
- [x] Verify: `pytest` passes

### Task 3.7: Log unknown TelemetryLevel in replay deserialization [Simple]
**File:** `game/simulation/replay/replay_serialization.py`
**Tests:** `pytest tests/ -k replay_serial`

- [x] Add a `logger.warning(...)` in the `except KeyError` (lines 558-561, `battle_outcome_from_dict`) before the opaque string fallback for an unrecognized telemetry level name
- [x] Verify: `pytest` passes

### Task 3.8: GameException base class for RoleRegistryReadOnlyError [Simple]
**File:** `game/core/roles.py`
**Tests:** `pytest tests/ -k roles`

- [x] Change `RoleRegistryReadOnlyError(Exception)` (line 61) to inherit from `GameException` (or a narrower `StateException`) so it participates in the `code`/`context` contract
- [x] Verify: `pytest` passes

### Task 3.9: Log swallowed validation failure in construction_queue [Simple]
**File:** `game/strategy/engine/handlers/construction_queue.py`
**Tests:** `pytest tests/ -k construction_queue`

- [x] Add a `logger.warning(...)` inside `except (ValueError, KeyError): return True` (line 160, `_check_design_valid`) so a corrupt design that silently passes validation is surfaced
- [x] Verify: `pytest` passes

### Task 3.10: Route minefield_balance JSON through json_utils [Simple]
**File:** `game/strategy/engine/minefield_balance.py`
**Tests:** `pytest tests/ -k minefield`

- [x] Replace the direct `json.load(fh)` file read (line 162, `load_minefield_balance`) with `json_utils.load_json(path)`, preserving the existing fallback-to-defaults behavior on missing/corrupt data
- [x] Verify: `pytest` passes; no direct `json.load`/`json.dump` file I/O remains in this file

### Task 3.11: Use shared Tk root in workshop_data_reloader [Simple]
**File:** `game/ui/screens/workshop_data_reloader.py`
**Tests:** `pytest tests/ -k workshop`

- [x] Replace the module-level duplicate Tk init (lines 22-27) with the canonical `get_tk_root()` from `game/ui/services/tkinter_utils.py` so a second, never-destroyed Tk root is not created at import time
- [x] Verify: `pytest` passes

### Task 3.12: Diagnostic log for silent satellite get_position catch [Simple]
**File:** `game/ai/satellite_controller.py`
**Tests:** `pytest tests/ -k satellite`

- [x] Add a `logger.debug(...)` in the `except AttributeError: return None` around `self.ship.get_position()` (lines 106-109, `_find_nearest_enemy`) — the only one of the three `AttributeError` swallows lacking a rationale/diagnostic (the two in `update()` already carry comments)
- [x] Verify: `pytest` passes

**Phase 3 Notes:** 3.1 component_activation_state (`require_keys` + `PersistenceException(CORRUPT_DATA)` in from_dict; `StateException(INVALID_STATE)` with current/expected-phase context in start_activating/deactivating); 3.2 fleet_write_service set_location/set_path -> `ValidationException(MISSING_DEPENDENCY)`; 3.3 `Message.__repr__` + `CompletionResult.__repr__` (length/metadata only); 3.4 `ImageResult.__repr__` (bytes_len + metadata, no bytes/revised_prompt); 3.5 `%r`->`%s` in both LLM/Image worker logs; 3.6 added `OSError` to load_planet_image except tuple + downgraded missing-manifest log to warning (recoverable; missing-texture fallback); 3.7 logger.warning on unknown TelemetryLevel (both deserializers); 3.8 `RoleRegistryReadOnlyError(StateException)`; 3.9 logger.warning on construction_queue swallowed-validation; 3.10 minefield_balance routed through `json_utils.load_json` (no direct json.load); 3.11 workshop_data_reloader uses shared `get_tk_root()` (removed leaked module-level Tk root); 3.12 logger.debug on satellite get_position AttributeError swallow. New tests: `tests/unit/test_proj466_phase3_hardening.py`; updated 3 pre-existing tests (asset_manager log level, 2 workshop tk_root->get_tk_root).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-20_065518_error-audit/`. See `findings/source_audit.md` for the link._
