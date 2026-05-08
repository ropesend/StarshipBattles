# PROJ-381: Error handling cleanup — strategy/ui/assets/sim (2026-05-07)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-381` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-381 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Critical — UI error boundary | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Major — broad-except hygiene, JSON bypass, cross-layer wrappers | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Minor — context enrichment, comment-format, ValueError narrowing, image parity | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-08
**Active Phase:** Phase 1
**Last Action:** Project created from `2026-05-07_220225_error-audit` after independent verification (4 parallel verifier agents)
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
Created from the error-audit at `Reviews/results/2026-05-07_220225_error-audit/` (28 unique findings; 26 verified by independent re-check, 1 user-included from UNCERTAIN, 1 rejected as false positive, 2 out-of-scope). 27 actionable items span the strategy (20), ui (5), assets (1), and simulation (1) layers. **Includes 1 CRITICAL boundary failure (B-5)** — turn-processing crashes propagate unhandled to the top-level crash handler instead of an in-game error dialog. Snapshot rollback works correctly; the gap is purely the missing UI-level `except EnginePhaseError`.

## Goals
- **Phase 1:** Close the CRITICAL UI error boundary so an `EnginePhaseError` produces a modal dialog instead of a hard crash. Add a regression test that exercises the failure path.
- **Phase 2:** Wrap or document 14 MAJOR items — 8 broad-except sites missing canonical `# Intentional broad catch:` comments (one of which silently swallows validation errors), 1 JSON-bypass file-I/O site, 1 generic `ValueError` raise, 2 cross-layer boundary fixes (`ImageUnexpectedError` parity, `GameSession.__init__` rollback boundary), and 1 context-enrichment fix (silent modifier swallow).
- **Phase 3:** Polish 12 MINOR items — 4 JSON-bypass file-I/O sites, 4 generic `ValueError` raises, 1 over-broad exception tuple, 1 comment-format normalization, 3 cross-layer context-enrichment improvements, 1 `ImageBackgroundCall` `wait()` parity addition.

## Scope
**In:**
- All findings VERIFIED in `findings/verification_report.md` (26 items) plus ERR-04-007 (UNCERTAIN, user-included)
- Layers: strategy, ui, assets, simulation
- Categories: broad_except_no_comment, json_bypass, generic_raise (ValueError → ValidationException), cross_layer_boundary, error_chaining, logging_consistency

**Out:**
- ERR-03-005 (`transfer_dialog.py:383`) — REJECTED by verifier; preceding-line comments communicate intent clearly. See `findings/verification_report.md`.
- B-8 (DesignLoadResult schema validation) and LLM-2 (verbose `call.error` log line) — OUT_OF_SCOPE. Audit's own evidence shows no actual leak / caller-responsibility design.
- DISPUTED / INCONCLUSIVE items in source audit's `findings/verification.md` (none for this audit).
- In-memory `json.loads(s)` / `json.dumps(obj)` calls per audit guidance.

## Key Files
| Component | File Path | Items |
|-----------|-----------|-------|
| Turn engine + boundary | `game/strategy/engine/turn_engine.py` | 3 (ERR-03-001, ERR-03-002, B-2) |
| Turn snapshot | `game/strategy/engine/turn_state_snapshot.py` | 2 (ERR-02-003, ERR-02-005) |
| Design validator | `game/strategy/services/design_validator.py` | 2 (ERR-03-003, ERR-03-004) |
| Image background | `game/ui/services/image/background.py` | 2 (B-10, LLM-3) |
| Galaxy generators | `game/strategy/data/galaxy_system_generator.py` + `galaxy_warp_generator.py` | 3 (ERR-04-003, ERR-04-004, ERR-04-008) |
| UI error boundary | `game/ui/screens/strategy_game_state_manager.py` | 1 CRITICAL (B-5) |
| Conflict resolution | `game/strategy/engine/conflict_resolution_engine.py` | 1 (B-7) |
| Game session init | `game/strategy/engine/game_session.py` | 1 (B-11) |
| Facade | `game/strategy/facade/strategy_session_facade.py` | 1 (B-4) |
| Sim adapter | `game/strategy/adapters/simulation_adapter.py` | 1 (B-6) |
| Exceptions | `game/core/exceptions.py` | 1 (B-10 — new `ImageUnexpectedError`) |

## Related Documents
- [design.md](design.md) — Source-audit summary, layer/severity breakdown, CRITICAL risk notes
- [decisions.md](decisions.md) — Bundling rationale and per-decision rows
- [findings/verification_report.md](findings/verification_report.md) — Independent re-verification results (Verified / Rejected / Uncertain / Out-of-scope)
- [findings/source_audit.md](findings/source_audit.md) — Pointer to the originating error-audit
- [findings/bundling_decisions.md](findings/bundling_decisions.md) — Phase D interactive bundling record

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (`python Tools/test_sharded/test_sharded.py`)
- [ ] Audit passed (`grep -rn "except:" game/` returns nothing in modified files; no new `except Exception` without `# Intentional broad catch:` comment)
- [ ] User verified
