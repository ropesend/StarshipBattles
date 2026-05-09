# Audit Findings Root-Cause Analysis — Part 2

## Summary

This report covers four audit areas: (1) broad-catch comment normalization across 13 files, (2) B-11 GameSession init null-object recovery, (3) B-7 modifier-collection log promotion, and (4) ERR-03-004 design-validator surface. Overall quality is high — the PROJ-381 cleanup has moved most broad-catch comments to substantive form, narrowed several cath-blocks, and added targeted tests. Two systematic issues remain: tkinter_utils.py comments are boilerplate, and GameSession init recovery is missing an ERROR-level log call.

## Broad-Catch Comment Analysis (site-by-site table)

| File:Line | Comment text | Substantive? | Tested? |
|---|---|---|---|
| `turn_engine.py:286` | `wraps unknown phase failures as EnginePhaseError(T001) and re-raises with phase_name + tick context; documented strategy-layer pattern.` | **YES** — identifies failure domain (unknown phase failures), action (wrap + re-raise), rationale (strategy-layer pattern). Also includes B-2 context enrichment (turn_number + save_path). Uses `from e` chain. | EnginePhaseError contract tested via snapshot/rollback integration tests. |
| `turn_engine.py:320` | N/A — narrow `except (AttributeError, TypeError)` for debug-only logging | N/A (narrow) | N/A |
| `turn_engine.py:538` | N/A — narrow `except PersistenceException`, re-raises for turn abort | N/A (narrow) | N/A |
| `turn_engine.py:591` | N/A — narrow `except EnginePhaseError`, rollback + re-raise | N/A (narrow) | N/A |
| `turn_engine.py:702` | `UI callback must never break turn processing (PROJ-308)` | **YES** — identifies failure domain (UI callback), rationale (never break turn processing), references project. | No dedicated unit test found. Integration tests exercise callback suppression. |
| `conflict_resolution_engine.py:567` | `external collector may raise any type from non-engine empire/system extensions; ERROR-log and proceed with degraded modifier stack so battle still resolves. Hex + empire context included to allow log-side debugging.` | **YES** — identifies domain (non-engine extensions), action (degraded modifiers), context (hex + empire). B-7 promoted from WARNING to ERROR. | **YES** — `test_conflict_resolution_modifier_logging.py` verifies ERROR level, hex "(3, 4)", empire "[0, 1]" in log message. |
| `asset_manager.py:88,91` | N/A — narrow `except FileNotFoundError` / `except pygame.error` | N/A (narrow) | N/A |
| `asset_manager.py:113,115` | N/A — narrow `except FileNotFoundError` / `except pygame.error` (group loader) | N/A (narrow) | N/A |
| `asset_manager.py:154` | N/A — narrow `except (FileNotFoundError, pygame.error, ValueError, OSError)` — ERR-02-001 narrowed star image catch to exclude genuinely fatal types (MemoryError, KeyboardInterrupt) | N/A (narrow) | No dedicated test for narrowed catch seen; existing star-image tests exercise resolution chain. |
| `asset_manager.py:211,214` | N/A — narrow `except FileNotFoundError` / `except pygame.error` (external load) | N/A (narrow) | N/A |
| `asset_manager.py:303` | N/A — narrow `except (FileNotFoundError, pygame.error, ValueError)` (planet load) | N/A (narrow) | N/A |
| `background.py:203,210` | N/A — narrow `except ImageCancelled` / `except ImageException` | N/A (narrow) | N/A |
| `background.py:217` | `provider escape — wrap as ImageUnexpectedError so worker-thread crashes don't leave caller polling forever.` | **YES** — identifies failure domain (provider escape), action (wrap as ImageUnexpectedError), rationale (prevent caller polling). Mirrors LLMUnexpectedError treatment. `_done_event.set()` in outer finally (line 259) ensures `wait()` terminates. | No dedicated unit test for ImageUnexpectedError wrapping found; mirror of tested LLMBackgroundCall pattern. |
| `tkinter_utils.py:69` | `Tkinter init is platform-dependent` | **BORDERLINE** — area is legitimate per docs §215 (platform-dependent UI init) but comment omits expected failure types and continuation rationale beyond "unavailable". | N/A |
| `tkinter_utils.py:100` | `Tk widget .destroy() raises various TclError subclasses if already destroyed or interpreter is gone` | **YES** — identifies expected failure types (TclError subclasses), condition (already destroyed/interpreter gone), reason (cleanup-only). | N/A |
| `tkinter_utils.py:142` | `file dialog is platform-dependent` | **BORDERLINE** — same issue as line 69; legitimate area, pro-forma rationale. | N/A |
| `tkinter_utils.py:175` | `file dialog is platform-dependent` | **BORDERLINE** — same. | N/A |
| `tkinter_utils.py:206` | `dialog is platform-dependent` | **BORDERLINE** — same. | N/A |
| `tkinter_utils.py:229` | `clipboard is platform-dependent` | **BORDERLINE** — same. | N/A |
| `controller.py:56` | `registry provider may be uninitialized (tests) or partially loaded; None signals "no registries" to callers` | **YES** — identifies failure domain (uninitialized tests / partial load), action (None sentinel), rationale (callers detect). | N/A |
| `controller.py:123` | `corrupt design data must not poison the design library scan — log and skip per file.` | **YES** — identifies failure domain (corrupt data), action (log + skip), rationale (prevent poisoning). | N/A |
| `turn_state_snapshot.py:56` | `any to_dict() failure must become SNAPSHOT_FAILED PersistenceException for the turn rollback contract.` | **YES** — identifies domain (to_dict failure), action (wrap as PersistenceException), rationale (rollback contract). Uses `from e` chain. ERR-02-005 routes crash dump through `save_json` for atomic writes. | Tested via snapshot capture integration tests. |
| `colony_output.py:85` | `race_registry may raise any type from duck-typed get_race; warn-log and skip species to avoid poisoning colony output calculation` | **YES** — identifies domain (duck-typed registry), action (skip species), rationale (avoid poisoning). | N/A |
| `ship_instance.py:69` | `ShipSerializer.from_dict() may raise various exception types on corrupt/incomplete design data; falling back to empty components is safe — callers treat empty dict as "no per-component data available".` | **YES** — identifies domain (corrupt data), action (empty fallback), rationale (callers treat as no data). | N/A |
| `ship_instance.py:570` | `registry may be absent in legacy save context` | **BORDERLINE** — uses "legacy" which is an invalid reason per docs §225, but identifies specific context (legacy save). Falls back to `None`. | N/A |
| `economy_config.py` | No except blocks — `load_json()` with `default={}` handles gracefully | N/A (clean) | N/A |
| `galaxy_system_generator.py` | No except blocks | N/A (clean) | N/A |
| `galaxy_warp_generator.py` | No except blocks | N/A (clean) | N/A |
| `star_generation_config.py:192` | N/A — narrow `except (ImportError, FileNotFoundError, OSError, TypeError)` — ERR-04-007 intentionally dropped ValueError + KeyError to surface data-integrity bugs | N/A (narrow) | No dedicated test for narrowed tuple found. |

## B-11 GameSession Init Recovery

**Location:** `game/strategy/engine/game_session.py:152-174`

### Mechanism

The `__init__` wraps `GameInitializer.initialize(...)` in a broad `except Exception` catch. On failure, it sets deterministic null-object state (`galaxy=None, empires=[], systems=[], human_player_ids=[], active_empire=None`) and re-raises as `SessionInitializationError` with `from e` exception chaining.

### Analysis

1. **Does the null-object represent a usable degraded state?** No — it is not "usable" in the sense of continuing gameplay. The null-object pattern here is a *deterministic crash-landing*: every attribute is set to a safe value so that if an outer handler catches the exception and inspects the session, it finds defined attributes rather than `AttributeError` on a partially constructed object. The re-raised exception prevents the caller from silently proceeding.

2. **Does the recovery log at ERROR level?** **NO — this is a gap.** The except block (`lines 165-174`) sets null-object state and re-raises, but there is no `logger.error()` call. Compare `process_turn()` (`game_session.py:319-321`) which logs `logger.error(f"Turn {self.turn_number} failed: {e}")`. The init failure chain is:
   - Inner exception → caught broad → wrapped as `SessionInitializationError` → raised
   - The *only* diagnostic is the chained `__cause__` on the exception object.

3. **Does the recovered GameSession surface its degraded status?** The session does not carry a `degraded` flag. Detection relies entirely on exception propagation — the caller receives `SessionInitializationError`. Since the exception is always re-raised (never swallowed), the session is never silently handed back to a caller in a degraded state. This is defensible but brittle: if a future refactor adds a caller that catches and discards the exception, the degraded state would be undetectable.

4. **Is this "fail loudly with degraded state" or "silently mask a broken init"?** This is genuinely **"fail loudly with deterministic null-object state"** — the exception propagates, `__cause__` preserves the root cause, and session attributes are predictable for debugging. The missing ERROR log is the only soft spot.

### Test Coverage

`tests/unit/strategy/test_game_session.py:271-317` (`TestGameSessionInitializationErrorBoundary`) validates:
- Exception is raised as `SessionInitializationError`
- `__cause__` chains to the original `ValidationException`
- Null-object state: `galaxy=None`, `empires=[]`, `systems=[]`, `human_player_ids=[]`, `active_empire=None`

Test does NOT validate that an ERROR log is emitted (because there is none).

## B-7 Modifier Collection Log Promotion

**Location:** `game/strategy/engine/conflict_resolution_engine.py:567-574`

### Mechanism

The `_collect_team_modifiers()` method calls the external `combat_modifier_collector.collect_combat_modifiers()`. Before PROJ-381, failures were logged at `logger.warning` and the modifier stack was degraded silently. B-7 promoted to `logger.error` with hex + empire context.

### Analysis

1. **Does the ERROR log surface to the right channel?** The log uses Python's standard `logging` module (`logger.error(...)`), not `EventBus.log_event()`. This is **correct** per Pattern #10 — the `game/core/event_logging.py::EventBus` is for structured simulation events (replay, analytics), not diagnostic logging. The standard `logging` output flows to log handlers (file, stderr), which is the appropriate channel for error diagnosis. The workshop-scoped UI EventBus is irrelevant here.

2. **Is the log structured with context?** The log line is:
   ```
   "Failed to collect combat modifiers at hex=%s empires=%s: %s", location, empire_order, e
   ```
   This includes hex coordinates and empire IDs as positional format arguments. It is **not** structured in the sense of `extra={"context": {...}}` dict passed to `logging.Logger`. The context is embedded in the message string, which is grep-able but not programmatically queryable like the structured context dicts used elsewhere (e.g., `EnginePhaseError.context`). This is a minor inconsistency.

3. **Does the test verify the actual log/event behavior?** `tests/unit/strategy/engine/test_conflict_resolution_modifier_logging.py` validates:
   - Log is at **ERROR** level (was WARNING before fix)
   - Hex location "(3, 4)" appears in the message
   - Empire list "[0, 1]" appears in the message
   - Result is `None` (degraded modifier stack, battle resolves)
   - Test does NOT validate EventBus interaction — correctly, since this is standard logging.

## ERR-03-004 Design Validator Surface

**Location:** `game/strategy/services/design_validator.py:92-98`

### Mechanism

The `validate()` method runs `ShipDesignValidator.validate_design(ship)`. Before PROJ-381, a crash in this sub-validator was caught, logged as `logger.warning`, and **discarded** — the result object retained `is_valid=True`, silently passing invalid designs. ERR-03-004 changed the catch to add the failure as a result error: `result.add_error(f"Sim validation failed: {e}")`, making `is_valid=False`.

### Analysis

1. **Does it properly surface sim-validator failures rather than swallowing?** **YES.** The fix adds an error to the `DesignValidationResult` with `result.add_error(...)`, which sets `is_valid=False`. The caller receives a result object with the error. The test at `test_design_validator.py:241-281` validates:
   - `result.is_valid` is `False`
   - Error message contains "Sim validation failed"

2. **Does it chain exceptions with `raise from`?** **NO — and that is correct** for this pattern. The catch does not re-raise; it collects the failure in a `DesignValidationResult` object and returns it. Exception chaining (`raise from`) is for re-raised exceptions. The two catch sites (lines 76 and 92) both follow the "collect as result, don't re-raise" pattern, which is appropriate for a validator that aggregates errors rather than failing fast.

   However, note that the inner exception object `e` is stringified into the error message via `f"Sim validation failed: {e}"`, losing the exception chain. If the caller needed to inspect the original exception type, it would need to parse a string. This is a mild loss of diagnostic fidelity, but acceptable for a validation-result pattern.

3. **Edge case:** The broad catch at line 76 (`except Exception`) wraps `Ship.from_dict` failures. If `.from_dict` were to raise a fatal error (e.g., `SystemError`, `MemoryError`), it would be caught and presented as a validation error rather than crashing. The catch at line 92 for the sim-validator follows the same pattern. Both are consistent with each other and with the validator's "never crash, always return result" contract.

## Findings

### CRIT-381-B11-001: GameSession init recovery emits no ERROR log

`game_session.py:165-174` — The `except Exception` block that catches `GameInitializer.initialize` failures sets null-object state and re-raises as `SessionInitializationError`, but **never calls `logger.error()`**. This means the root cause is only visible through the exception chain, not in log files. Operators/developers grep'ing logs for "SessionInitializationError" or init failures will find nothing.

Compare `process_turn()` at line 319 which properly logs `logger.error(f"Turn {self.turn_number} failed: {e}")` before re-raising.

**Recommendation:** Add `logger.error("GameSession initialization failed: %s", e, exc_info=True)` immediately after the null-object attribute assignments (between line 170 and line 171).

### MAJ-381-BC-001: tkinter_utils.py broad-catch comments are pro-forma boilerplate

`tkinter_utils.py:69, 142, 175, 206, 229` — Five broad-catch comments read `"<operation> is platform-dependent"`. While the domain (platform-dependent Tkinter operations) is listed as legitimate in docs §215, the comments violate ER §205-206: they do not state **what failures are expected** nor **why continuing/fallback is correct**.

The `line 100` comment is the counterexample of what these should look like: `"Tk widget .destroy() raises various TclError subclasses if already destroyed or interpreter is gone"` — it names the expected failure types AND the condition.

**Recommendation:** Rewrite the five boilerplate comments to follow the `line 100` pattern, naming specific expected exception classes and why the fallback path (return `None` / `False`, disable Tkinter) is safe.

### MIN-381-BC-001: ship_instance.py uses "legacy" in broad-catch comment

`ship_instance.py:570` — Comment reads `"registry may be absent in legacy save context"`. The docs §225 list "legacy" as an invalid reason for broad catches. The specific context ("absent in legacy save context") partially redeems it, but the word "legacy" remains.

**Recommendation:** Rewrite to `"registry may be absent when deserializing from corrupted or legacy save data"` or remove "legacy" entirely and state the concrete condition: `"registry may be absent when component registry provider is not wired at construction time"`.

### MIN-381-BC-002: conflict_resolution_engine.py ERROR log lacks structured context dict

`conflict_resolution_engine.py:571-573` — The B-7 log uses positional format arguments (`%s`) for hex and empire IDs, embedding context in the message string. Elsewhere in the codebase (e.g., `EnginePhaseError.context`, `ValidationException.context`), structured `context={...}` dicts are used, which are programmatically queryable by log aggregators.

**Recommendation:** Consider passing context as structured extra:
```python
logger.error(
    "Failed to collect combat modifiers",
    extra={"context": {"hex": str(location), "empires": empire_order}},
    exc_info=True,
)
```
Priority is low because the current message is grep-able.

### MIN-381-BC-003: background.py broad-catch lacks dedicated unit test

`background.py:217-231` — The `ImageUnexpectedError` wrapping path has no dedicated unit test. The pattern is a known mirror of the tested `LLMBackgroundCall` `LLMUnexpectedError` path (PROJ-321..328), and the `_done_event.set()` in the outer `finally` is structurally correct. However, the wrapping itself (that `ImageUnexpectedError` is created, that `__cause__` is set, that `_status` transitions to ERROR) has no direct test coverage.

**Recommendation:** Low priority — the structural mirror of a tested pattern provides reasonable confidence. Add a test when touching this file for other maintenance.

### INFO-381-CLEAN-001: Three files with zero except blocks

`economy_config.py`, `galaxy_system_generator.py`, `galaxy_warp_generator.py` declare zero `except` blocks. All three use `load_json()` with `default={}` for graceful degradation, which absorbs errors internally. Clean.

### INFO-381-CLEAN-002: asset_manager.py entirely narrow-caught

All nine except blocks in `asset_manager.py` use narrow exception types (`FileNotFoundError`, `pygame.error`, `ValueError`, `OSError`). The star image load path at line 154 was specifically narrowed from `except Exception` to a four-type tuple by ERR-02-001 to exclude fatal types. No broad catches remain.
