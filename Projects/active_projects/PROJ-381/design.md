# PROJ-381: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Audit

**Audit directory:** `Reviews/results/2026-05-07_220225_error-audit/`
**Audit date:** 2026-05-07
**Skill:** `ocode-error-audit` (OpenCode), with internal verifier pass

**Bundle counts:**
- Audit-reported total: 28 unique findings (1 CRITICAL + 13 MAJOR + 14 MINOR)
- Audit verifier confirmed: all CRITICAL + 5 sampled MAJOR (0 false-positives in sample)
- This bundle: **26 verified** independently + **1 user-included** from UNCERTAIN = **27 actionable**
- Rejected: 1 (ERR-03-005 — comments preceding `except` line communicate intent clearly enough that the verifier dropped it)
- Out-of-scope: 2 (B-8 schema validation is caller responsibility; LLM-2 verbose log has no actual leak per audit's own evidence)
- Project siblings created in this run: none (V<30 → single-project bundle per protocol)

**Layer coverage:** strategy (20), ui (5), assets (1), simulation (1).

**Severity breakdown of this bundle:** 1 CRITICAL + 14 MAJOR + 12 MINOR (= 27).

**Phase mapping:** Phase 1 = the CRITICAL boundary fix; Phase 2 = the 14 MAJOR items (broad-except hygiene + 1 JSON bypass + 1 ValueError raise + 3 cross-layer wrappers); Phase 3 = the 12 MINOR items (4 ValueError raises + 4 JSON bypasses + 1 over-broad tuple + 1 comment-format + 3 context-enrichment + 1 image parity).

### Risk Notes — CRITICAL boundary findings

**B-5 (`game/ui/screens/strategy_game_state_manager.py:122-128`) — Crash-and-rollback path**

`process_full_turn()` is currently `try/finally` with **no `except` clause**. The full failure path the verifier traced:

```
TurnEngine._time_phase() raises EnginePhaseError(T001)
  → TurnEngine.process_turn() executes snapshot rollback (state preserved), re-raises
  → GameSession.process_turn() logs and re-raises
  → StrategySessionFacade.process_turn() passthrough (no wrap, no catch)
  → StrategyGameStateManager.process_full_turn() ← GAP HERE (no except)
  → advance_turn() (no except)
  → strategy_screen.advance_turn() (no except)
  → pygame event loop
  → app.py main() top-level crash handler → crash.log → game exits
```

**State integrity:** preserved (TurnEngine rolls back from snapshot before re-raising).
**User experience:** raw crash with crash log on disk; the user never sees what failed or why.

The fix is local to `process_full_turn()` — no architectural change required, no rewriting of the call chain, no facade-level work strictly necessary (Phase 3's B-4 makes the facade conversion *cleaner* but doesn't change the resolved-error contract). Phase 1 ships the fix in isolation; Phase 3 polishes the layering.

## Initial Analysis

This project is a planning artifact derived entirely from the source audit + an independent four-batch re-verification. No new code analysis was performed in this skill — the audit's existing work + the verifier reports are the inputs.

## Swarm Findings Summary

Verification reports live at `.agent_reports/2026-05-07_220225_error-audit/verification_batch{1,2,3,4}.md` (disposable scratch). The aggregated, signed-off claims are recorded in `findings/verification_report.md`.

### Architecture

The codebase has strong error-handling fundamentals (per the source audit's positive-findings section):
- Zero bare `except:` clauses across 749 production files.
- Zero generic `raise Exception()` — all raises use domain-specific subclasses of `GameException`.
- All 21 turn phases route through `TurnEngine._time_phase()` which wraps any non-`EnginePhaseError` exception as `EnginePhaseError(T001)` with phase_name + tick context and `from e` chaining.
- Snapshot-and-rollback works correctly in `TurnEngine.process_turn()`.
- `LLMBackgroundCall._run()` wraps non-`LLMException` provider escapes as `LLMUnexpectedError`.
- 64 of 75 broad-except sites already carry the canonical `# Intentional broad catch:` comment.

The audit's findings sit on the *edges* of this strong pattern: a single missing UI catch, comment hygiene on the remaining 11 broad-except sites, a handful of JSON file-I/O calls that bypass `json_utils`, and the absence of `ImageUnexpectedError` parity for `ImageBackgroundCall`.

### Key Patterns to Reuse

- **Canonical broad-catch comment:** `# Intentional broad catch: <reason>` on the same line as `except Exception:`. Documented in `docs/05_ERROR_HANDLING.md` § Broad Catch Rule. Used throughout most of the codebase already; this project closes the remaining gaps.
- **`json_utils.load_json(path, default={})` / `save_json(path, data)`:** canonical helpers in `game/core/json_utils.py`. Atomic write via temp-file for `save_json`; graceful default for `load_json`.
- **`LLMUnexpectedError` pattern:** `game/services/llm/background.py:285-307` and `game/core/exceptions.py:309-331`. Phase 2 mirrors this pattern as `ImageUnexpectedError` in `game/ui/services/image/background.py`.
- **`EnginePhaseError(T001)` wrapping:** `game/strategy/engine/turn_engine.py:_time_phase`. Source-of-truth for cross-layer error propagation in turn processing.
- **`ValidationException` + `ErrorCode` constants:** `game/core/exceptions.py` + `game/core/error_codes.py`. Replaces stdlib `ValueError` raises in handlers/registry.

### Dependencies & Risks

1. **B-10 / `ImageUnexpectedError` is exposed in `__all__`:** the new exception class is part of the public exception surface and must be exported from `game.core.exceptions.__all__` for downstream code to catch it. Mirror the LLM counterpart's export and update `docs/05_ERROR_HANDLING.md:74` in the same change.
2. **B-11 null-object state:** when `GameInitializer.initialize()` fails, the recovery path must leave `GameSession` attributes assigned to deterministic empty values rather than `None` — UI code already references `session.galaxy`, `session.empires`, etc., and a null-attribute access would cascade to `AttributeError`. Use empty-galaxy / empty-empires constructors rather than `None`.
3. **B-4 vs B-5 ordering:** Phase 1's fix catches `EnginePhaseError` directly. Phase 3's B-4 fix re-wraps that as a facade-level `TurnFailedError`. When B-4 lands, Phase 1's `except EnginePhaseError` must be updated to `except TurnFailedError`. The decisions log records this as a planned cross-phase coupling.
4. **ERR-04-007 risk-acceptance:** removing `ValueError`/`KeyError` from `star_generation_config.py:192`'s catch tuple means a malformed config now raises rather than silently returning defaults. The user accepted this trade in Phase D Step 3.

### Opportunities Discovered

- The `_time_phase` context-enrichment fix (B-2 in Phase 3) and the per-battle context preservation (B-6 in Phase 3) together make crash-dumps much more useful for production debugging — turn_number, save_path, fleet_ids, hex_coord all become available without needing to re-run with logging tweaks.
- After B-10 lands, Pattern #19 in `docs/05_ERROR_HANDLING.md` reaches 7/7 compliance (currently 6/7).

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
