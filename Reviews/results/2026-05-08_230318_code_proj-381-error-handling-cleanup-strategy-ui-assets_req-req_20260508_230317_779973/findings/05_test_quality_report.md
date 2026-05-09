# Test Quality Review

## Summary

All 11 test files reviewed. **No CRITICAL anti-patterns found.** No test mocks exception classes — every failure path is exercised by triggering a real raise (via stub providers, monkeypatched dependencies, or MagicMock side_effects). Exception-type assertions and structured context checks dominate, especially in `test_base_command_handler.py`, `test_game_session.py`, `test_star_generation_config.py`, `test_simulation_adapter.py`, and `test_turn_engine_snapshot_integration.py`. 

**Overall quality: HIGH.** The PROJ-381 test additions consistently test behavior (dialog appearance, null-object state, exception wrapping, error codes in context) rather than internal implementation details. 

Three MAJOR and four MINOR findings flagged below.

---

## Per-File Analysis

### test_strategy_turn_error_boundary.py (New — 185 lines)

- **Exercised paths:**
  1. Baseline success — no error dialog
  2. `EnginePhaseError` raised by facade → caught, modal dialog shown
  3. `TurnFailedError` raised by facade → caught, modal dialog shown
  4. Finally block runs in error path → `current_tick`/`total_ticks` cleared
  5. Finally block runs in success path → `current_tick`/`total_ticks` cleared

- **Mock vs real trigger:** Real exception instances (`EnginePhaseError`, `TurnFailedError`) constructed with proper error codes and context dicts, assigned to mock facade's `process_turn.side_effect`. The real `StrategyGameStateManager.process_full_turn` runs and hits its `except TurnFailedError` / `except EnginePhaseError` clauses. Does NOT mock the exception class. **Good.**

- **Assertion quality:**
  - `mock_msg.assert_called_once()` — verifies dialog was created (behavior). **Good.**
  - `assert screen.current_tick is None` / `assert screen.total_ticks is None` — state cleanup check. **Good.**
  - `assert "harvesting" in body` / `assert "ValueError" in body` / `assert "rolled back" in body.lower() or "preserved" in body.lower()` — partial string matches on dialog HTML body. **Moderately brittle** — these test the user-facing message contract, but a wording change to "preserved" → "protected" or similar cosmetic adjustment would break the test. The assertions match the production template in `_show_turn_failed_dialog` (line 301–307), so they are correct today but fragile to refactors.
  - The phase-name and original-type checks (`"harvesting"`, `"ValueError"`) are injected from `error.context` into the template. These are value-based (the test provides those values). **Acceptable.**
  - The rollback reassurance check (`"rolled back" ... "preserved"`) tests that the user-facing template includes the rollback message. This is the right level (user-facing string) but fragile to copy edits.

- **Robustness:** Moderate. The dialog-string assertions would survive a dialog library swap but not a wording change. The state-cleanup assertions are very robust.

- **Missing edge cases:**
  1. **No test for a bare `RuntimeError` or other unhandled exception escaping the facade.** The boundary catches only `TurnFailedError` and `EnginePhaseError`. If a `TypeError` or `ValueError` escapes `process_turn`, it propagates past `process_full_turn` uncaught. This is the original B-5 failure mode for non-standard exceptions.
  2. No test for when `pygame.display.get_surface()` returns a real surface (non-None path).
  3. No test for when `_screen.ui.manager` is `None` (headless fallback path in `_show_turn_failed_dialog`).

- **Rating: STRONG** — Exercises real error boundaries with real exception instances. Tests both dialog display and state cleanup. Missing the bare-exception escape path (see MAJ-001).

---

### test_background.py (New — 95 lines)

- **Exercised paths:**
  1. Non-ImageException from provider → wrapped as `ImageUnexpectedError`, status = ERROR
  2. `wait()` returns False during active work, True after completion
  3. `wait()` returns True after cancel-before-start
  4. `wait()` returns True after error terminal state

- **Mock vs real trigger:** `_BoomProvider` raises real `RuntimeError`; `_SlowSuccessProvider` uses `time.sleep` to simulate async work. Both are injected as real provider objects. `ImageBackgroundCall` runs in a real background thread via `.start()`. **Excellent — exercises real threading behavior.**

- **Assertion quality:**
  - `assert call.status == CallStatus.ERROR` — enum comparison. **Excellent.**
  - `assert isinstance(call.error, ImageException)` and `assert isinstance(call.error, ImageUnexpectedError)` — exception type hierarchy check. **Excellent.**
  - `assert ctx.get("original_exception_type") == "RuntimeError"` — structured context check. **Excellent.**
  - `assert call.wait(timeout=2.0) is True` — boolean return value. **Good.**
  - No string-based assertions. **All assertions are on types, enums, and structured data.**

- **Robustness:** Very high. No string-match assertions. Thread timing tests use generous timeouts (200ms worker delay, 2s wait timeout) — low flakiness risk on reasonable CI hardware.

- **Missing edge cases:**
  1. **No test for when the provider raises an `ImageException` (should NOT be wrapped).** The wrapping logic likely passes `ImageException` through unchanged; this is a distinct code path that should be verified.
  2. No test for calling `start()` when already started.
  3. No test for `wait()` without calling `start()` first.
  4. No test for the `result` property after DONE state.

- **Rating: STRONG** — Minimal, focused, robust. All assertions are structural (enums, type checks). See MAJ-003 for missing edge case.

---

### test_conflict_resolution_modifier_logging.py (New — 71 lines)

- **Exercised paths:**
  1. Collector raises `RuntimeError` → error logged at ERROR level with hex coord and empire IDs; result is `None` (degraded modifier stack).

- **Mock vs real trigger:** `monkeypatch.setattr` on the `combat_modifier_collector` module replaces `collect_combat_modifiers` with a raising stub. Calls the real `engine._collect_team_modifiers()`. **Good — exercises the real error-handling code path.**

- **Assertion quality:**
  - `assert result is None` — behavioral: degraded modifier stack. **Good.**
  - `assert error_records` (at least one ERROR log) — log level check. **Good.**
  - `assert "(3, 4)" in msg` and `assert "[0, 1]" in msg` — **string format assertions on log message content.** Fragile to log formatting changes (e.g., if coordinates are logged as `hex=(3, 4)` or `x=3, y=4`). The contract being tested (hex + empire IDs in the error log) is valid, but the assertion method (string-inclusion of Python repr format) is brittle.

- **Robustness:** Moderate. The log-level and result-None checks are robust. The string-format checks would fail on log formatting refactors.

- **Missing edge cases:**
  1. No test for the success path (collector works normally, returns modifiers).
  2. No test for when the engine's `_galaxy` attribute is None (truthy check may fail differently).
  3. No test for multiple collectors raising.
  4. Only one test method — narrow scope.

- **Rating: ADEQUATE** — Tests the right code path but relies on brittle log-string assertions and exercises only one failure mode. See MAJ-002.

---

### test_design_validator.py (Augmented — 281 lines, PROJ-381: lines 231–281)

- **PROJ-381 additions:** `TestSimValidatorFailureSurfacesAsResultError` (1 test) + `TestDesignValidationResultHasIssues` (3 tests).

- **Exercised paths (PROJ-381):**
  - `ShipDesignValidator.validate_design` raises → `is_valid = False` with "Sim validation failed" error
  - `DesignValidationResult.has_issues` for clean, warning-only, error-only states

- **Mock vs real trigger:** Patches `ShipDesignValidator` on its source module with `_Boom` stub that raises `RuntimeError`. Calls the real `DesignValidator.validate()` which goes through the real try/except at line 92–93. **Good — triggers the real catch block.**

- **Assertion quality:**
  - `assert result.is_valid is False` — behavioral. **Good.**
  - `assert any("Sim validation failed" in err for err in result.errors)` — string-inclusion in error list. **Moderately brittle** — the error message phrase "Sim validation failed" comes from the production catch block's `result.add_error(...)`. However, looking at the source code (line 92–93): the catch only does `logger.warning(...)` — it does NOT call `result.add_error()`. The test assertion on "Sim validation failed" in errors would fail against the current production code. This may indicate the test was written for a fix that hasn't been applied yet (similar to the `process_full_turn` boundary). **Flag: potential mismatch between test expectation and current production code.**
  - `assert result.has_issues is False/True` — boolean property. **Excellent.**

- **Robustness:** The `has_issues` tests are maximally robust. The sim-validator test's string assertion is brittle, and the monkeypatch depends on the lazy import path inside `validate()` — fragile to import restructuring.

- **Missing edge cases:**
  - No test for when `Ship.from_dict()` raises (the outer try/except at line 76).
  - No test for when the sim validator returns partial results but doesn't crash.

- **Rating: ADEQUATE** — The `has_issues` tests are strong. The sim-validator crash test uses string-match and depends on lazy-import path. See MIN-001.

---

### test_game_session.py (Augmented — 317 lines, PROJ-381: lines 271–317)

- **PROJ-381 additions:** `TestGameSessionInitializationErrorBoundary` (1 test).

- **Exercised paths:**
  - `GameInitializer.initialize` raises → `SessionInitializationError` with `__cause__` chaining
  - Session lands in deterministic null-object state: `galaxy=None`, `empires=[]`, `systems=[]`, `human_player_ids=[]`, `active_empire=None`

- **Mock vs real trigger:** `monkeypatch.setattr` on `GameInitializer.initialize` raises `ValidationException`. Session is constructed via `__new__` + direct `__init__` call in a `pytest.raises` context. **Excellent — exercises the real `__init__` error handling.**

- **Assertion quality:**
  - `assert isinstance(exc_info.value.__cause__, ValidationException)` — exception chaining. **Excellent.**
  - `assert session.galaxy is None` — identity check. **Excellent.**
  - `assert session.empires == []`, `assert session.systems == []`, etc. — identity/value checks on all null-object attributes. **Excellent.**
  - No string-match assertions. All structural.

- **Robustness:** Very high. Every assertion is on a stable, semantic contract (attribute equality/identity). Would survive major refactors as long as the null-object contract holds.

- **Missing edge cases:**
  - No test for partial initialization failure (exception after some attributes are set but before others — though the null-object pattern likely sets all defaults before init logic runs).
  - No test for calling `to_dict()` on a null-object session.

- **Rating: STRONG** — Exemplary test. Uses `pytest.raises`, checks `__cause__`, verifies every null-object attribute independently. Model for error-boundary tests.

---

### test_star_generation_config.py (Augmented — 267 lines, PROJ-381: lines 223–267)

- **PROJ-381 additions:** `TestStarGenerationConfigCatchNarrowing` (3 tests).

- **Exercised paths:**
  1. `ValueError` from loader → propagates (not swallowed by defaults fallback)
  2. `KeyError` from loader → propagates (not swallowed)
  3. `FileNotFoundError` from loader → returns defaults (stays in catch tuple)

- **Mock vs real trigger:** `@patch` on `AstrophysicsLoader` with side_effect exceptions. Calls the real `get_star_generation_config()`. **Good.**

- **Assertion quality:**
  - `with pytest.raises(ValueError, match="bad config dict")` — exception type + message. **Excellent — `pytest.raises` with match is the gold standard.**
  - `with pytest.raises(KeyError)` — exception type. **Good.**
  - `assert config.type_weights["MAIN_SEQUENCE"] == 0.525` — default value preserved. **Good.**

- **Robustness:** Very high. The `pytest.raises(match=...)` pattern checks both type and message without being fragile (it uses substring matching). The defaults test checks structural values.

- **Missing edge cases:**
  - No test for `OSError` or other IO-adjacent exceptions (should they also fall back?).
  - No test for JSON with valid structure but semantically invalid values (e.g., negative probabilities).

- **Rating: STRONG** — The `pytest.raises(ValueError, match=...)` in `test_value_error_in_loader_propagates` is the best-written assertion in this review. Tests both narrowing (ValueError/KeyError propagate) and retaining (FileNotFoundError returns defaults).

---

### test_turn_engine_snapshot_integration.py (Augmented — 169 lines, PROJ-381: lines 139–169)

- **PROJ-381 additions:** `TestEnginePhaseErrorContextEnrichment` (1 test).

- **Exercised paths:**
  - `EnginePhaseError` raised during turn processing → context dict includes `turn_number` and `save_path`
  - Pre-existing context keys (`phase_name`, `tick`) preserved

- **Mock vs real trigger:** `_make_engine_with_failing_harvester(fresh_registries)` monkeypatches the harvesting engine to raise `RuntimeError("boom")`. The real `process_turn` hits this, wraps it as `EnginePhaseError`, and the exception is caught by `pytest.raises(EnginePhaseError)`. **Good.**

- **Assertion quality:**
  - `ctx.get("turn_number") == 17` — exact context key-value. **Excellent.**
  - `ctx.get("save_path") == "/tmp/proj381-b2-fake"` — exact context key-value. **Excellent.**
  - `ctx.get("phase_name") is not None` — existence check. **Good.**
  - `"tick" in ctx` — existence check. **Good.**
  - No string-match assertions on the exception message. All checks on structured `context` dict.

- **Robustness:** Very high. The assertions target the structured `context` dictionary, which is the semantic contract for error metadata.

- **Missing edge cases:**
  - No test for when `save_path` is `None` (not provided) — context should either omit the key or set it to `None`.
  - No test for when `session` is `None` (not provided).
  - No test for when the harvesting engine raises an `EnginePhaseError` directly (does it get re-wrapped?).

- **Rating: STRONG** — Clean, focused test that verifies error context enrichment through the real turn-processing pipeline.

---

### test_simulation_adapter.py (Augmented — 410 lines, PROJ-381: lines 372–410)

- **PROJ-381 additions:** `TestSimulationAdapterBattleContextPreservation` (1 test).

- **Exercised paths:**
  - `SimulationException` from `run_battle` → re-raised as `BattleResolutionError` with `fleet_ids`, `empire_ids`, `hex_coord` in context
  - `__cause__` chain preserved

- **Mock vs real trigger:** Creates real `_BoomSim(SimulationException)` subclass, patches `run_battle` to raise it. Calls real `resolver.resolve_battle()`. **Excellent — the test creates a real exception subclass, not a mock.**

- **Assertion quality:**
  - `with pytest.raises(BattleResolutionError) as exc_info` — exception type. **Good.**
  - `ctx.get("fleet_ids") == [1, 2]` — exact list. **Excellent.**
  - `ctx.get("empire_ids") == [7, 9]` — exact list. **Excellent.**
  - `ctx.get("hex_coord") == (3, 4)` — exact tuple. **Excellent.**
  - `isinstance(exc_info.value.__cause__, _BoomSim)` — exception chaining. **Excellent.**

- **Robustness:** Very high. All assertions on structured context data and exception types.

- **Missing edge cases:**
  - No test for when only one fleet has `owner_id` or `hex_coord`.
  - No test for when `run_battle` raises a non-`SimulationException` (e.g., `TypeError`).
  - No test for empty fleets list.

- **Rating: STRONG** — Comprehensive structured-context assertions, real exception subclass creation, proper `__cause__` verification.

---

### test_turn_state_snapshot.py (Augmented — 221 lines, PROJ-381: lines 181–205)

- **PROJ-381 additions:** `test_dump_crash_snapshot_logs_oserror_without_raising` (1 test).

- **Exercised paths:**
  - `dump_crash_snapshot` when `save_json` returns `False` → logs ERROR, does NOT raise

- **Mock vs real trigger:** Patches `save_json` to return `False`. Calls the real `dump_crash_snapshot`. **Good.**

- **Assertion quality:**
  - `any("Failed to write crash snapshot" in rec.message for rec in caplog.records)` — **exact log message string match.** Fragile to log message wording changes. The method could change the message to "Could not write crash snapshot" or "Crash snapshot write failed" and the test would break despite the behavior being unchanged (logs error, doesn't raise).
  - The behavior "does not raise" is implicitly tested by the test completing without exception. **Good.**

- **Robustness:** Moderate. The log-message string check is fragile. A better approach would be to assert on log level + presence of path/phase info in the records, or to use a regex pattern.

- **Missing edge cases:**
  - No test for when `save_json` itself raises an exception (should it propagate? be caught?).
  - No test for when the output directory doesn't exist.

- **Rating: ADEQUATE** — Tests the right behavior (log-and-continue) but uses a fragile log-message string assertion. See MAJ-004.

---

### test_base_command_handler.py (Augmented — 406 lines, PROJ-381: entire file updated for ERR-01-003)

- **PROJ-381 changes:** Updated to expect `ValidationException` (instead of `ValueError`) and asserts on the error `code` field and `context` data.

- **Exercised paths (PROJ-381-relevant):**
  - `_resolve_fleet_required` fleet not found → `ValidationException` with `MISSING_ENTITY` code
  - `_resolve_fleet_required` owner mismatch → `ValidationException` with `OWNERSHIP_MISMATCH` code
  - `_resolve_planet_optional` required but not found → `ValidationException` with `MISSING_ENTITY` code

- **Mock vs real trigger:** Uses real `BaseCommandHandler` class with `Mock()` sessions. Exercises real resolution logic in the handler methods. **Good.**

- **Assertion quality:**
  - `with pytest.raises(ValidationException, match="Fleet not found") as exc` — exception type + message. **Good.**
  - `assert exc.value.code == ErrorCode.MISSING_ENTITY.value` — structured error code. **Excellent.**
  - `assert exc.value.context.get("fleet_id") == 999` — context data. **Excellent.**
  - `assert exc.value.code == ErrorCode.OWNERSHIP_MISMATCH.value` — structured error code. **Excellent.**

- **Robustness:** Very high. Error code assertions on enum values are extremely robust. Context data checks target named fields, not string representations.

- **Missing edge cases:** Minimal — the primary failure modes (not found, wrong owner, success) are all covered.

- **Rating: STRONG** — The gold standard for structured exception assertions. Every test checks exception type, error code, and relevant context fields. Compare with `test_command_handlers.py` (MAJ-005).

---

### test_command_handlers.py (Augmented — 1918 lines, PROJ-381: lines 516–575 in `TestBaseCommandHandler`)

- **PROJ-381 additions:** `TestBaseCommandHandler` methods: `test_resolve_fleet_required_raises_when_not_found` and `test_resolve_fleet_required_validates_ownership`.

- **Exercised paths (PROJ-381):**
  1. `_resolve_fleet_required` fleet not found → `ValidationException`
  2. `_resolve_fleet_required` owner mismatch → `ValidationException`

- **Mock vs real trigger:** Same as `test_base_command_handler.py` — real `BaseCommandHandler` with `Mock()` sessions. **Good.**

- **Assertion quality:**
  - `with pytest.raises(ValidationException) as exc_info` — exception type check. **Good.**
  - `assert "Fleet not found" in str(exc_info.value)` — **string representation check only.** Does not verify error code or context data. **Weak compared to counterpart in `test_base_command_handler.py`.**
  - `assert "does not belong" in str(exc_info.value)` — same issue.

- **Robustness:** Weak for error handling tests. The `str(exc_info.value)` approach only checks the exception's string representation, not its structured fields (`code`, `context`). If the error message wording changes (e.g., "Fleet 999 not found" → "Fleet id=999 does not exist"), the test breaks without testing the semantic contract (error code `MISSING_ENTITY`, context containing `fleet_id`).

- **Missing edge cases:** Same as `test_base_command_handler.py` — but the assertions are weaker.

- **Rating: WEAK (PROJ-381 assertions only)** — The tests correctly check for `ValidationException` type, but then fall back to string matching instead of asserting on the structured error code and context. The exact same behavior is tested in `test_base_command_handler.py` with robust code+context assertions. The duplication with differing assertion quality is a maintenance hazard. See MAJ-005.

---

## Findings

### CRITICAL — None

No tests mock exception classes. No tests bypass the error boundary. No tests use `patch('module.ExceptionClass')`. All 11 files properly trigger real failure paths via stub providers, monkeypatched dependencies, or MagicMock side_effects.

---

### MAJ-001: test_strategy_turn_error_boundary.py — missing bare-exception escape test

The UI error boundary in `process_full_turn` catches `TurnFailedError` and `EnginePhaseError`. It does NOT catch other exception types (e.g., `RuntimeError`, `TypeError`, `ValueError`) that could escape the facade's `process_turn`. The B-5 audit finding is about the game crashing when *any* exception escapes — the fix narrowed the catch to two exception types, leaving other exceptions to still crash the game. There should be a test verifying the behavior when a non-standard exception escapes (e.g., a mock that raises `RuntimeError` — does the boundary catch it via a broad handler, or does it crash?).

**Suggested fix:** Add a test that sets `mock_facade.process_turn.side_effect = RuntimeError("unexpected")` and verifies either:
- The boundary catches it (broad except), or
- It propagates (documented as intentional).

**Files:** `tests/integration/ui/test_strategy_turn_error_boundary.py`

---

### MAJ-002: test_conflict_resolution_modifier_logging.py — brittle log string assertions

The test asserts `"(3, 4)" in msg` and `"[0, 1]" in msg` to verify hex coordinates and empire IDs appear in the error log. These match Python's `str()` / `repr()` formatting of tuples and lists. A refactor to `f"hex={x},{y}"` or `f"empires=[0, 1]"` (same information, different string) would break the test with no behavioral change.

**Suggested fix:** Use `caplog.records` and check `record.args` or structured logging fields, or use a regex tolerant of formatting variations:
```python
assert "3" in msg and "4" in msg  # coordinates are present regardless of format
```

**Files:** `tests/unit/strategy/engine/test_conflict_resolution_modifier_logging.py`

---

### MAJ-003: test_background.py — missing ImageException-passthrough test

The test verifies that a non-`ImageException` (`RuntimeError`) is wrapped as `ImageUnexpectedError`. However, there is no test verifying that when the provider raises an `ImageException` (the expected error type), it is NOT wrapped — it passes through unchanged. This is a distinct code path that should be verified.

**Suggested fix:** Add a stub provider that raises `ImageException("expected")` and assert `isinstance(call.error, ImageException)` but `not isinstance(call.error, ImageUnexpectedError)`.

**Files:** `tests/unit/ui/services/image/test_background.py`

---

### MAJ-004: test_turn_state_snapshot.py — brittle log message string assertion

`test_dump_crash_snapshot_logs_oserror_without_raising` asserts on exact log message `"Failed to write crash snapshot"`. A wording change breaks the test despite the behavior (log error, don't raise) being unchanged.

**Suggested fix:** Assert on log level (`assert any(r.levelno == logging.ERROR for r in caplog.records)`) and that the method did not raise. Optionally check that the message contains the snapshot path or a failure-related keyword with a case-insensitive regex.

**Files:** `tests/unit/strategy/turn_engine/test_turn_state_snapshot.py`

---

### MAJ-005: test_command_handlers.py — weak string-match assertions vs test_base_command_handler.py code+context assertions

The PROJ-381 tests in `test_command_handlers.py` (`TestBaseCommandHandler` class) assert only on `str(exc_info.value)` for string inclusion (`"Fleet not found"`, `"does not belong"`). The counterpart file `test_base_command_handler.py` tests the exact same methods with robust assertions on `exc.value.code == ErrorCode.MISSING_ENTITY.value` and `exc.value.context.get("fleet_id")`. This duplication with differing assertion quality means:

1. One test file is fragile (word change → break).
2. The other test file already does it correctly — the weak tests are redundant.
3. Maintenance burden: two files to update if behavior changes.

**Suggested fix:** Either upgrade the `test_command_handlers.py` assertions to match `test_base_command_handler.py`'s code+context pattern, or remove the duplicate tests if `test_base_command_handler.py` already covers the same paths.

**Files:**
- `tests/unit/strategy/test_command_handlers.py` (lines 537–575)
- `tests/unit/strategy/engine/test_base_command_handler.py` (lines 73–96)

---

### MIN-001: test_design_validator.py — potential test-production mismatch

`test_sim_validator_exception_marks_result_invalid` asserts that `result.errors` contains `"Sim validation failed"`. The production code at `design_validator.py:92–93` catches the exception but only logs a warning — it does NOT call `result.add_error()`. The test may be targeting a planned fix rather than current code, or the assertion may fail against the current production implementation. **Verify that the production code has been updated before accepting this test as passing.**

**Files:** `tests/unit/strategy/services/test_design_validator.py` (line 278–281), `game/strategy/services/design_validator.py` (lines 92–93)

---

### MIN-002: test_strategy_turn_error_boundary.py — complex mock setup in helper

`_make_state_manager_with_screen()` constructs 15+ mock attributes across `screen`, `session`, `ui`, `empires`. While well-organized in a helper, the complexity means a screen attribute rename in production requires updating this helper. The dependency surface is large.

**Files:** `tests/integration/ui/test_strategy_turn_error_boundary.py` (lines 21–58)

---

### MIN-003: test_conflict_resolution_modifier_logging.py — single test, narrow scope

Only one test method covers one failure mode (collector raises `RuntimeError`). No success-path test, no test for multiple collectors, no test for `_galaxy is None`.

**Files:** `tests/unit/strategy/engine/test_conflict_resolution_modifier_logging.py`

---

### MIN-004: test_strategy_turn_error_boundary.py — dialog body assertions test copy text

The assertion `assert "rolled back" in body.lower() or "preserved" in body.lower()` tests the rollout reassurance line of the user-facing dialog. While testing user-visible text is valid, this is a copy-level detail that changes for localization, UX review, or rephrasing. Consider asserting on structural properties instead (e.g., that `body` is non-empty and contains `phase_name` from the error context).

**Files:** `tests/integration/ui/test_strategy_turn_error_boundary.py` (line 118)

---

## Quality Rankings (Summary)

| File | Rating | Strongest Aspect | Weakest Aspect |
|------|--------|-----------------|----------------|
| test_strategy_turn_error_boundary.py | STRONG | Both dialog + cleanup paths tested | Missing bare-exception escape test; fragile UI string checks |
| test_background.py | STRONG | All type/enum assertions, no strings | Missing ImageException passthrough test |
| test_conflict_resolution_modifier_logging.py | ADEQUATE | Tests real catch path | Brittle log-string format; only one test |
| test_design_validator.py (PROJ-381) | ADEQUATE | has_issues tests are robust | Sim-validator test may not match current prod code |
| test_game_session.py (PROJ-381) | STRONG | Every null-object attribute verified; __cause__ checked | — |
| test_star_generation_config.py (PROJ-381) | STRONG | `pytest.raises(ValueError, match=...)` is gold standard | — |
| test_turn_engine_snapshot_integration.py (PROJ-381) | STRONG | Clean context dict assertions | — |
| test_simulation_adapter.py (PROJ-381) | STRONG | Exact list/tuple context assertions; real exception subclass | — |
| test_turn_state_snapshot.py (PROJ-381) | ADEQUATE | Tests the right behavior (log, don't raise) | Brittle log message string assertion |
| test_base_command_handler.py (PROJ-381) | STRONG | Error code + context assertions on every test | — |
| test_command_handlers.py (PROJ-381) | WEAK | Correct exception type check | String-match only; inferior to test_base_command_handler.py counterpart |
