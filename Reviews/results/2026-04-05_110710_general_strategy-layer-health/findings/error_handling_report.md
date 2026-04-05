# Error Handling Audit: game/strategy/

**Date:** 2026-04-05
**Scope:** `game/strategy/` -- 131 Python files, ~30,600 lines
**Reference:** `docs/05_ERROR_HANDLING.md`, `docs/03_CONVENTIONS.md`

---

### Summary
- Total issues found: 14
- Critical: 1, Major: 5, Minor: 6, Info: 2

**Overall assessment:** The strategy layer demonstrates generally good error handling practices. Most exception handlers log the error, use specific exception types, and apply `raise from` chaining where appropriate. The custom exception hierarchy (`ValidationException`, `PersistenceException`) is used correctly throughout, with proper error codes and context dictionaries. The command handler system correctly uses `ValidationResult` for command validation. The main areas for improvement are: (1) a few `except Exception` catches without the required `# Intentional broad catch:` annotation, (2) several silent `pass` handlers in non-debug code, (3) inconsistent use of `ValueError` vs project-specific exceptions, and (4) missing error handling around the turn processing tick loop.

---

### Findings

#### CRITICAL: No error handling around turn tick processing loop
**ID:** ERR-001
**Location:** `game/strategy/engine/turn_engine.py:369-370`
**Issue:** The `process_turn` method iterates 100 ticks, calling `_process_tick` which orchestrates 12+ sub-engine phases. There is zero exception handling around the tick loop or within `_process_tick`. If any sub-engine raises an unexpected exception during tick 37 of 100, the entire turn crashes with no recovery, no partial state logging, and no indication of which phase or tick failed.
**Impact:** A single error in any sub-engine (movement, combat, production, harvesting, etc.) during any of the 100 ticks causes complete turn failure. The game state may be left partially modified (e.g., some fleets moved, some resources consumed) with no way to diagnose which tick/phase failed. This is the highest-risk error handling gap in the strategy layer.
**Recommendation:** Add a try/except around the tick loop body in `_process_tick` or around the loop in `process_turn`. At minimum, log which tick and phase failed with `logger.error()`. Consider whether partial turn state should be rolled back or preserved. Given the complexity, an `# Intentional broad catch:` with detailed logging would be appropriate here.
**Effort:** Medium

#### MAJOR: `except Exception` without intentional broad catch annotation
**ID:** ERR-002
**Location:** `game/strategy/data/fleet.py:394`, `game/strategy/data/empire.py:329`, `game/strategy/data/order_serializer.py:57`
**Issue:** Three deserialization `from_dict` methods catch `except Exception as e` without the `# Intentional broad catch:` annotation required by `docs/05_ERROR_HANDLING.md`. While these are arguably justified (deserialization should be resilient to corrupt data), they violate the documented convention.
**Impact:** Reviewers and automated audits cannot distinguish intentional broad catches from accidental ones. The doc convention exists specifically to prevent silent acceptance of overly broad catches.
**Recommendation:** Add the `# Intentional broad catch: resilient deserialization - skip corrupt items` annotation to all three locations. The catches themselves are appropriate behavior (log + skip corrupt items).
**Effort:** Simple

#### MAJOR: ValueError used instead of ValidationException in domain code
**ID:** ERR-003
**Location:** `game/strategy/data/fleet_capability_calculator.py:72,135`, `game/strategy/data/ship_instance.py:249`, `game/strategy/engine/command_handlers.py:158,161,202`
**Issue:** Six locations raise `ValueError` for domain validation failures (missing registries, fleet not found, ownership validation). Per `docs/05_ERROR_HANDLING.md`, these should use `ValidationException` with appropriate error codes (`MISSING_DEPENDENCY`, `MISSING_ENTITY`). The `ValueError` is a Python built-in, not part of the project's exception hierarchy.
**Impact:** Code catching `GameException` or `ValidationException` will miss these errors. Callers cannot use error codes for programmatic handling. Inconsistent with the rest of the strategy layer which properly uses the custom hierarchy.
**Recommendation:** Replace `ValueError` with `ValidationException` using appropriate error codes. For `fleet_capability_calculator.py`, use `ErrorCode.MISSING_DEPENDENCY`. For `command_handlers.py` resolution methods, use `ErrorCode.MISSING_ENTITY`. Note: `_resolve_fleet_required` and `_resolve_planet_optional` appear to be dead code (no call sites found), so these may be candidates for removal instead.
**Effort:** Simple

#### MAJOR: Silent pass in debug logging helper
**ID:** ERR-004
**Location:** `game/strategy/engine/turn_engine.py:223-224`
**Issue:** `_log_empire_state` catches `(AttributeError, TypeError)` with a bare `pass`. While this is a debug helper, silently swallowing exceptions in the turn engine masks potential bugs in empire state management (e.g., `empire.resource_pool` being None or missing `.id`). The method is called at turn start and end, so any issue would be silently ignored every turn.
**Impact:** If an empire object is malformed (missing `id` or `resource_pool`), the bug will never surface through this diagnostic path. The docs explicitly state: "Never silently swallow exceptions. At minimum, log a warning."
**Recommendation:** Add `logger.debug(f"Could not log empire state: {e}")` instead of bare `pass`. This preserves the non-failure intent while making issues diagnosable.
**Effort:** Simple

#### MAJOR: DesignLibrary PermissionError handler missing fallback recovery
**ID:** ERR-005
**Location:** `game/strategy/systems/design_library.py:56-57`
**Issue:** When `os.makedirs` raises `PermissionError`, the error is logged but no fallback occurs -- the `designs_folder` remains set to the inaccessible path. The `OSError` handler (line 58-65) correctly falls back to a temp directory, but `PermissionError` does not get this treatment (even though `PermissionError` is a subclass of `OSError`, the more specific `PermissionError` clause matches first and short-circuits).
**Impact:** If the designs folder has permission issues, the DesignLibrary will be initialized with an unusable path, causing all subsequent operations (scan, save, load) to fail. The temp directory fallback exists but is unreachable for the most common permission scenario.
**Recommendation:** Remove the separate `PermissionError` handler so it falls through to the `OSError` handler which already includes the fallback. Or duplicate the temp-folder fallback logic in the `PermissionError` handler.
**Effort:** Simple

#### MAJOR: Missing error logging in design_library mark_obsolete JSONDecodeError handler
**ID:** ERR-006
**Location:** `game/strategy/systems/design_library.py:255-256`
**Issue:** The `JSONDecodeError` handler in `mark_obsolete` returns `False, "Design file is corrupted"` without logging the error. Other `JSONDecodeError` handlers in the same file (lines 94, 214, 294) all log the error with file path context. This one silently returns a user-facing message with no diagnostic information in the logs.
**Impact:** When a design file becomes corrupted, there is no log entry to help diagnose which file or what corruption occurred. Operators cannot troubleshoot the issue.
**Recommendation:** Add `logger.error(f"DesignLibrary: Corrupt JSON in design '{design_id}': {e}")` before the return statement, consistent with the other handlers in the same file.
**Effort:** Simple

#### MINOR: build_queue_source silent fallback to empty dict
**ID:** ERR-007
**Location:** `game/strategy/data/build_queue_source.py:36-37`
**Issue:** `_load_production_rates` catches `(FileNotFoundError, ValueError)` and falls back to an empty dict without any logging. Per docs, recoverable failures should log at `warning` level.
**Impact:** If `production_rates.json` is missing or malformed, production rates will silently default to empty, causing all build queues to have zero production rate. This would be extremely difficult to diagnose in a running game.
**Recommendation:** Add `logger.warning(f"Failed to load production rates: {e}")` in the except handler.
**Effort:** Simple

#### MINOR: game_initializer silently ignores invalid homeworld_type
**ID:** ERR-008
**Location:** `game/strategy/engine/game_initializer.py:218-219`
**Issue:** When `race_config.homeworld_type` is not a valid `PlanetType` enum member, the `KeyError` is caught with a bare `pass`. The planet keeps its existing type with no logging.
**Impact:** A misconfigured race config silently produces a planet with the wrong type. This could affect gameplay balance and would be very hard to debug. The comment "Keep existing type if invalid" acknowledges the behavior but doesn't log it.
**Recommendation:** Add `logger.warning(f"Invalid homeworld_type '{race_config.homeworld_type}' for race, keeping default")`.
**Effort:** Simple

#### MINOR: ship_stats_calculator silent ValueError pass
**ID:** ERR-009
**Location:** `game/strategy/services/ship_stats_calculator.py:636-637`
**Issue:** In `_get_component_hp`, a `ValueError` from `int()` parsing is caught with bare `pass`. This is in a loop looking for indexed component damage keys.
**Impact:** Low -- this is genuinely expected behavior (checking if a suffix is numeric). However, per project conventions, even expected failures should have at minimum a comment explaining why the pass is intentional.
**Recommendation:** Add a comment: `# Expected: suffix is not a numeric index, continue searching`. No logging needed for this case.
**Effort:** Simple

#### MINOR: fleet_dto silent capability resolution failure
**ID:** ERR-010
**Location:** `game/strategy/facade/dto/fleet_dto.py:184-186`
**Issue:** When `fleet.capabilities.list_abilities()` raises `(ValueError, AttributeError)`, the exception is caught and capabilities defaults to an empty tuple. No logging occurs.
**Impact:** If a fleet has a broken capabilities calculator, the UI will show no capabilities with no indication of a problem. Given this is a DTO builder for the UI layer, silent degradation is somewhat appropriate, but a debug log would help troubleshoot.
**Recommendation:** Add `logger.debug(f"Could not resolve capabilities for fleet {fleet.id}: {e}")`.
**Effort:** Simple

#### MINOR: design_library delete_design PermissionError not logged
**ID:** ERR-011
**Location:** `game/strategy/systems/design_library.py:383-384`
**Issue:** The `PermissionError` handler returns a user-facing error message but does not log the error with file path context. The `OSError` handler on line 385 similarly does not log. Only the `(RuntimeError, IOError)` handler on line 387 logs.
**Impact:** Operators cannot see which file had permission issues or what OS error occurred when design deletion fails.
**Recommendation:** Add `logger.error(f"DesignLibrary: Permission denied deleting design '{design_id}': {e}")` and similar for the OSError handler.
**Effort:** Simple

#### MINOR: _resolve_build_entity returns None silently for unknown entity_type
**ID:** ERR-012
**Location:** `game/strategy/engine/command_handlers.py:222-226`
**Issue:** `_resolve_build_entity` returns `None` for any `entity_type` other than "planet" or "fleet" without logging. While callers should validate entity_type before calling, a defensive log would catch programming errors.
**Impact:** Low -- this is an internal helper. But an unexpected entity_type silently producing None could lead to confusing NoneType errors downstream.
**Recommendation:** Add `logger.warning(f"Unknown entity_type: {entity_type}")` before the final `return None`.
**Effort:** Simple

#### INFO: Dead code -- _resolve_fleet_required and _resolve_planet_optional
**ID:** ERR-013
**Location:** `game/strategy/engine/command_handlers.py:140-205`
**Issue:** `_resolve_fleet_required` and `_resolve_planet_optional` are defined in `BaseCommandHandler` but have no call sites anywhere in the codebase. They were added in PROJ-204 Phase 3 but no handler uses them. They also raise `ValueError` (non-project exception), compounding the inconsistency.
**Impact:** Dead code that adds maintenance burden and confusion. Their ValueError-raising pattern is inconsistent with the ValidationResult pattern used by the other resolution methods.
**Recommendation:** Remove both methods. If a handler needs them in the future, they can be re-added with `ValidationException` instead of `ValueError`.
**Effort:** Simple

#### INFO: Performance logging uses logger.warning instead of logger.info
**ID:** ERR-014
**Location:** `game/strategy/engine/turn_engine.py:387-401`
**Issue:** The turn performance timing summary is logged at `logger.warning()` level. Per the logging level guidelines in `docs/05_ERROR_HANDLING.md`, performance diagnostics should use `logger.info()` (notable events during normal operation) or `logger.debug()` (detailed diagnostic information). `logger.warning()` is for "recoverable problems where operation continues with fallback."
**Impact:** Performance logs appear in warning-filtered outputs, adding noise. Not an error handling issue per se, but misuse of logging levels can mask real warnings.
**Recommendation:** Change to `logger.info()` or `logger.debug()`.
**Effort:** Simple

---

### Top 5 Priority Issues

1. **ERR-001 (CRITICAL):** No error handling around turn tick processing loop -- a single sub-engine exception crashes the entire turn with partial state corruption and no diagnostics.

2. **ERR-005 (MAJOR):** DesignLibrary PermissionError handler missing fallback recovery -- the temp directory fallback is unreachable for the most common failure mode, leaving the library in an unusable state.

3. **ERR-003 (MAJOR):** ValueError used instead of ValidationException in 6 locations -- breaks the project's exception hierarchy contract and prevents programmatic error handling.

4. **ERR-002 (MAJOR):** Three `except Exception` catches missing the required `# Intentional broad catch:` annotation -- violates the documented convention.

5. **ERR-007 (MINOR):** build_queue_source silently falls back to empty production rates with no logging -- could cause all production to silently stop working with zero diagnostic information.
