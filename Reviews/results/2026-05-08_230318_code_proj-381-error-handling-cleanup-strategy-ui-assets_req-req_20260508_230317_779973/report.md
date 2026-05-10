# PROJ-381 Error Handling Cleanup — Code Review Report

**Request ID:** req_20260508_230317_779973
**Review Type:** code (delegated by Claude Code)
**Date:** 2026-05-08
**Review Mode:** normal (8-agent full-spectrum swarm)
**Scope:** Production files across strategy, ui, assets, core layers (6 commits on `feat/03c-phase-aware-execution`)
**Parent Request:** None (initial review)
**No checkout SHA — this is a branch review (not 03c detached worktree)

## Executive Summary

PROJ-381's error-handling cleanup is **substantially complete** across the 27 in-scope audit items. The implementation follows documented patterns for exception hierarchy, error boundaries, JSON persistence, and test coverage. **One CRITICAL finding** requires remediation before subsequent PROJ-NNN projects can proceed: the B-5 UI error dialog bypasses Pattern #31 (StrategyModalWindow) and does not block strategy-screen input.

The 27-item claim of completion is **genuine but imperfect**: 25 of 27 items have substantive fixes; 2 (stale docstrings in `handlers/base.py`, `CommandRegistry.register()` missed `ValueError` site) are incomplete. The 6-commit claim of "no findings deferred" is validated — every finding was addressed, though some fixes are pro-forma (5 `tkinter_utils.py` broad-catch comments).

**Pre-existing failures confirmed**: 3 spot-checked test files (20 failures total) are all pre-existing relative to PROJ-381. No new exception types leak into test paths.

## Review Methodology

8 specialized review agents analyzed 50+ files across 4 layers. Each agent read reference documentation (`docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`, `docs/05_ERROR_HANDLING.md`) and produced a findings report. Agents covered: B-5 UI error boundary, new exceptions, audit findings root-cause (2 parts), test quality, broad-catch sites, architecture/rules compliance, and pre-existing failure spot-check.

## Findings Summary

| Severity | Count | Key Areas |
|----------|-------|-----------|
| CRITICAL | 3 | B-5 modal bypass, missed ValueError site, test assertion gaps |
| MAJOR | 14 | Docstring drift, missing properties, boilerplate comments, test brittleness, log gaps |
| MINOR | 18 | Comment quality, context key naming, LOC ceiling, narrow test scope |
| INFO | 7 | Compliance confirmations, pre-existing failure validation |

### CRITICAL Findings

#### CRIT-001: B-5 error dialog bypasses StrategyModalWindow (Rule 3 + Pattern #31)
**File:** `game/ui/screens/strategy_game_state_manager.py:312-317`
**Summary:** `_show_turn_failed_dialog()` creates a raw `pygame_gui.windows.UIMessageWindow` instead of a `StrategyModalWindow` subclass. This bypasses Pattern #31 modal tracking: no `register_modal()` call, no input blocking. A player can click through the error dialog, issue fleet commands, or advance the turn again while the error is visible.
**Recommendation:** Create a `TurnFailedDialog` class inheriting from `StrategyModalWindow`. The `StrategyScreen.ui` holds a reference to `StrategyWindowManager` — thread it through.

#### CRIT-002: `CommandRegistry.register()` still uses bare `ValueError`
**File:** `game/strategy/engine/commands/registry.py:191`
**Summary:** The duplicate-registration guard raises plain `ValueError` with no `ErrorCode` and no `context` dict. `CommandSpec.__post_init__` was properly migrated (ERR-01-002) but `register()` was missed. Callers catching `ValidationException` from registration won't catch this.
**Recommendation:** Replace with `ValidationException(code=ErrorCode.DUPLICATE_COMMAND.value, context={"command_name": name, ...})`.

#### CRIT-003: `test_command_handlers.py` ValidationException tests missing code/context assertions
**File:** `tests/unit/strategy/test_command_handlers.py:551-620`
**Summary:** Three PROJ-381 tests check that `ValidationException` is raised but assert only on `str(exc)` for string inclusion — they never verify `code` or `context`. The counterpart `test_base_command_handler.py` does this correctly. A regression dropping the ErrorCode would pass these tests undetected.
**Recommendation:** Add `assert exc.value.code == ErrorCode.MISSING_ENTITY.value` and context field assertions matching `test_base_command_handler.py` pattern.

### MAJOR Findings

#### MAJ-001: TurnFailedError docstring claims properties that don't exist
**File:** `game/core/exceptions.py:235-237`
**Summary:** Docstring says `tick`, `turn_number`, and `original_type` are "surfaced as properties." Only `phase_name` (line 240) and `recoverable` (line 245) exist. The UI reads these from the raw context dict — functionally correct but the class doesn't deliver the advertised interface.
**Recommendation:** Add the 3 missing `@property` definitions or correct the docstring.

#### MAJ-002: docs/05_ERROR_HANDLING.md hierarchy tree is stale
**File:** `docs/05_ERROR_HANDLING.md:32-60`
**Summary:** The exception hierarchy tree omits all 4 PROJ-381 exceptions. `ImageUnexpectedError` is mentioned in prose at line 74 but not in the tree.
**Recommendation:** Add `SessionInitializationError`, `TurnFailedError`, `BattleResolutionError` under `StrategyException`; add `ImageUnexpectedError` under `ImageException`.

#### MAJ-003: Regression test mocks exception class rather than triggering real failure
**File:** `tests/integration/ui/test_strategy_turn_error_boundary.py:84-118`
**Summary:** The test sets `screen._facade.process_turn.side_effect = EnginePhaseError(...)` — verifies the catch clause but not the sub-engine→_time_phase wrapping, snapshot capture, or rollback.
**Recommendation:** Add an integration test using a real TurnEngine with a mock sub-engine via `dataclasses.replace(cfg, harvesting_engine=mock_raises_engine)`.

#### MAJ-004: TurnFailedError lacks `turn_number`/`save_path` properties despite context enrichment
**File:** `game/core/exceptions.py:227-248`, `game/ui/screens/strategy_game_state_manager.py:283-286`
**Summary:** `_time_phase()` (B-2) enriches context with `turn_number` and `save_path`, but `TurnFailedError` only exposes `phase_name`. The error dialog never states which turn number failed.
**Recommendation:** Add `turn_number` and `save_path` properties; update `_show_turn_failed_dialog` to display the turn number.

#### MAJ-005: GameSession init recovery emits no ERROR log
**File:** `game/strategy/engine/game_session.py:165-174`
**Summary:** The except block sets null-object state and re-raises `SessionInitializationError` but never calls `logger.error()`. Root cause is invisible in log files.
**Recommendation:** Add `logger.error("GameSession initialization failed: %s", e, exc_info=True)` before the re-raise.

#### MAJ-006: tkinter_utils.py broad-catch comments are pro-forma boilerplate
**File:** `game/ui/services/tkinter_utils.py:69,142,175,206,229`
**Summary:** Five broad-catch comments read `"<operation> is platform-dependent"` without enumerating expected failure types or why fallback is correct — violates docs/05 §205-206.
**Recommendation:** Rewrite following the `line 100` example: name expected TclError/RuntimeError classes and explain why returning `None`/disabling Tkinter is safe.

#### MAJ-007 to MAJ-014: Test quality issues (from Agent 5)
- **MAJ-007**: Missing bare-exception escape test in `test_strategy_turn_error_boundary.py`
- **MAJ-008**: Brittle log string assertions in `test_conflict_resolution_modifier_logging.py`
- **MAJ-009**: Missing `ImageException` passthrough test in `test_background.py`
- **MAJ-010**: Brittle log message assertion in `test_turn_state_snapshot.py`
- **MAJ-011**: `test_command_handlers.py` uses string-match only vs. `test_base_command_handler.py` code+context assertions
- **MAJ-012**: Stale docstrings in `handlers/base.py` (lines 165, 253) still reference `ValueError`
- **MAJ-013**: Pattern #10 EventBus module-level compatibility shim (pre-existing, not PROJ-381 regression)
- **MAJ-014**: Defensive raw `EnginePhaseError` catch encourages facade bypass

### Positive Validations

1. **All 4 new exceptions are raised in production** — none are dead (Agent 2)
2. **ImageUnexpectedError is fully symmetric** with `LLMUnexpectedError` in constructor shape, context key, and intent (Agent 2)
3. **JSON bypass migrations complete** — all 6 audited files use canonical `json_utils.save_json`/`load_json` (Agent 3)
4. **Exception chaining correct** — all error boundaries preserve `__cause__` via `raise from e` (Agents 1, 3, 7)
5. **B-11 null-object recovery is genuine fail-loud** — sets deterministic defaults then re-raises (Agents 1, 4, 7)
6. **B-7 modifier-collection log promoted to ERROR** with hex+empire context, validated by test (Agent 4)
7. **ERR-03-004 design validator** properly surfaces sim-validator failures as `is_valid=False` (Agent 4)
8. **No Rule 3 violations** — zero shims, fallback systems, or compatibility paths detected across all 4 error boundaries (Agent 7)
9. **No layer violations** — cross-layer imports all follow documented dependency flow (Agent 7)
10. **89 pre-existing failures confirmed** — 3 spot-checked files all verified pre-existing; no PROJ-381 exception types in tracebacks (Agent 8)

## Agent Reports

Detailed findings are in `findings/`:
- `agent1_b5_ui_error_boundary_report.md` — B-5 UI error boundary deep-dive
- `02_new_exceptions_report.md` — New exceptions assessment
- `03_audit_findings_part1_report.md` — ValueError→ValidationException + JSON bypass migrations
- `04_audit_findings_part2_report.md` — Broad-catch comments + B-11 + B-7 + ERR-03-004
- `05_test_quality_report.md` — Test quality across 11 files
- `06_broad_catch_sites_report.md` — Systematic broad-catch verification (37 except blocks, 13 files)
- `07_architecture_rules_report.md` — Architecture, patterns, Rule 3 compliance
- `08_pre_existing_failures_report.md` — Pre-existing failure spot-check (3 files, 20 failures)
