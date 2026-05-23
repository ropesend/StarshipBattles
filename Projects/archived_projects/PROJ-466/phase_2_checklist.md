# Phase 2: Major exception-hygiene fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-466 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace the 10 verified MAJOR generic builtin raises, gratuitous broad catches, silent swallows, and the lost-context wrapper identified by audit `2026-05-20_065518_error-audit` with domain-specific exceptions and explicit handling, so persistence/validation boundaries raise discriminable domain errors and crash dumps carry battle context.

---

## Tasks

### Task 2.1: Domain exceptions at replay serialization boundaries [Simple]
**File:** `game/simulation/replay/replay_serialization.py`
**Tests:** `pytest tests/ -k replay_serial`

- [x] Replace `raise TypeError(...)` (line 115, `boundary_to_dict`) with `PersistenceException(..., code=ErrorCode.CORRUPT_DATA.value, ...)`
- [x] Replace `raise ValueError(...)` (line 139, `boundary_from_dict`) with `PersistenceException(..., code=ErrorCode.CORRUPT_DATA.value, ...)`
- [x] Verify: `pytest` passes; no `raise Exception`/bare builtins remain at these persistence boundaries

### Task 2.2: Merge BattleResolutionError context into EnginePhaseError [Medium]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/ -k "turn_engine and (phase or battle)"`

- [x] In `TurnEngine._time_phase` (EnginePhaseError construction at lines 322-333), inspect `e.__cause__` for a `BattleResolutionError` and merge its context keys (`fleet_ids`, `empire_ids`, `hex_coord`) into the `EnginePhaseError.context` dict
- [x] Add a regression test asserting a `BattleResolutionError`-caused phase failure produces an `EnginePhaseError` whose context includes the battle-identifying keys
- [x] Verify: `pytest` passes; crash-dump context now identifies the failing battle

### Task 2.3: Domain exception for planetary facility resource validation [Simple]
**File:** `game/strategy/data/planetary_facility.py`
**Tests:** `pytest tests/ -k planetary_facility`

- [x] Replace `raise ValueError(f"Unknown resource_id: {resource_id!r}")` (line 149, `_validate_resource_id`) with `ValidationException(..., code=ErrorCode.RESOURCE_NOT_FOUND.value, ...)`
- [x] Verify: `pytest` passes

### Task 2.4: Domain exception for ship-stats missing registries [Simple]
**File:** `game/strategy/data/ship_stats_cache.py`
**Tests:** `pytest tests/ -k ship_stats`

- [x] Replace `raise ValueError("ShipInstance requires registries...")` (line 41, `calculate`) with `ValidationException(..., code=ErrorCode.MISSING_DEPENDENCY.value, ...)`
- [x] Verify: `pytest` passes

### Task 2.5: Domain exception for fleet-capability missing registry [Simple]
**File:** `game/strategy/data/fleet_capability_calculator.py`
**Tests:** `pytest tests/ -k fleet_capability`

- [x] Replace `raise ValueError(...)` at line 70 (`ship_has_spaceyard`) with `ValidationException(..., code=ErrorCode.MISSING_DEPENDENCY.value, ...)`
- [x] Replace `raise ValueError(...)` at line 138 (`_get_registry`) with `ValidationException(..., code=ErrorCode.MISSING_DEPENDENCY.value, ...)`
- [x] Verify: `pytest` passes; both sites use the domain exception

### Task 2.6: Domain exception for battle_runner missing dependency [Simple]
**File:** `game/simulation/battle_runner.py`
**Tests:** `pytest tests/ -k battle_runner`

- [x] Replace `raise RuntimeError(...)` (line 314, `run_battle` — note the audit's claimed second site at 294 does not exist) with `ValidationException(..., code=ErrorCode.MISSING_DEPENDENCY.value, ...)`
- [x] Verify: `pytest` passes

### Task 2.7: Add code= to happiness_engine ValidationException [Simple]
**File:** `game/strategy/engine/happiness_engine.py`
**Tests:** `pytest tests/ -k happiness`

- [x] Add `code=ErrorCode.INVALID_STATE.value` to the `ValidationException` raise (line 96, `_validate_tick_inputs`) to match the other engines' `_validate_tick_inputs` pattern
- [x] Verify: `pytest` passes

### Task 2.8: Remove gratuitous Exception from modifier_icon_service catch [Simple]
**File:** `game/ui/services/modifier_icon_service.py`
**Tests:** `pytest tests/ -k modifier_icon`

- [x] Replace `except (pygame.error, Exception) as e:` (line 81) with a narrowed tuple (e.g. `(pygame.error, OSError)`); if a broad catch is genuinely required, add an `# Intentional broad catch: <reason>` comment instead
- [x] Verify: `pytest` passes; no uncommented broad `Exception` remains

### Task 2.9: Surface JSON decode failure in battle_state_viewer [Simple]
**File:** `game/ui/screens/battle_state_viewer.py`
**Tests:** `pytest tests/ -k battle_state_viewer`

- [x] Replace silent `except json.JSONDecodeError: pass` (line 135) with a `logger.warning(...)` and a visible error-panel state so a malformed diff is not mistaken for "states identical"
- [x] Verify: `pytest` passes

**Phase 2 Notes:** All 9 MAJOR sites swapped to domain exceptions. 2.1 replay boundaries -> `PersistenceException(CORRUPT_DATA)`; 2.2 turn_engine adds `TurnEngine._battle_resolution_context()` that walks the `__cause__` chain and merges `fleet_ids`/`empire_ids`/`hex_coord` from a `BattleResolutionError` into the wrapping `EnginePhaseError.context`; 2.3 planetary_facility -> `ValidationException(RESOURCE_NOT_FOUND)`; 2.4 ship_stats_cache + 2.5 fleet_capability (both sites) + 2.6 battle_runner -> `ValidationException(MISSING_DEPENDENCY)`; 2.7 happiness adds `code=INVALID_STATE`; 2.8 modifier_icon narrowed `(pygame.error, Exception)` -> `(pygame.error, OSError)`; 2.9 battle_state_viewer logs a warning + sets a visible `diff_error` rendered in the legend. New tests: `tests/unit/strategy/test_proj466_exception_hygiene.py`, 2 turn_engine context-merge tests, 2 battle_state_viewer tests, 2 modifier_icon tests. Updated 9 pre-existing tests that asserted the old builtin types (legitimate contract change). Docstrings updated to match new raised types.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-20_065518_error-audit/`. See `findings/source_audit.md` for the link._
