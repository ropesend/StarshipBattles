# PROJ-409 Verification Report

**Date:** 2026-05-09
**Branch:** `feat/03c-phase-aware-execution`
**Scope:** Tier 5 closure of two PROJ-395 deferrals (MAJ-013 + MAJ-014).

## MAJ-014 — Defensive raw `EnginePhaseError` catch (actively deleted)

**Closure mode:** Active deletion per CLAUDE.md Rule 4 (no fallbacks for scenarios that can't happen).

PROJ-381 Phase 3 made `StrategySessionFacade.process_turn` the sole converter from `EnginePhaseError` → `TurnFailedError`. PROJ-408 C-02 added direct unit coverage on the conversion (`tests/unit/strategy/facade/test_strategy_session_facade.py::TestProcessTurnErrorConversion`), proving the path is watertight. The defensive `except EnginePhaseError` branch in `StrategyGameStateManager.process_full_turn` was therefore provably dead code.

**Production change** (`game/ui/screens/strategy_game_state_manager.py`):
- Removed `EnginePhaseError` from the import at the former line 19.
- Deleted the entire `except EnginePhaseError as e:` block (former lines 149-158, ~10 LOC).
- Tightened `_show_turn_failed_dialog` signature to `TurnFailedError` only.

**TDD evidence:** `TestProcessFullTurnErrorBoundary` in `tests/unit/ui/screens/test_strategy_game_state_manager.py` — `test_raw_engine_phase_error_propagates_uncaught` failed against pre-fix code (the catch swallowed it) and passed after. `test_turn_failed_error_opens_dialog_clears_overlay_skips_autosave` pins the canonical contract.

**Integration tests updated:** `tests/integration/ui/test_strategy_turn_error_boundary.py` now injects `TurnFailedError` (matching production after facade conversion). `TestRealTurnEngineFailureWiring` runs the genuine `EnginePhaseError` from a real `TurnEngine` through the same conversion before it reaches the UI boundary — preserves the spirit of MAJ-003 (real engine, real wrapping chain) under the new architectural contract.

**Tests:** 24/24 unit, 9/9 integration boundary, 37/37 broader UI turn suite. Commit `c0ff79f92`.

## MAJ-013 — EventBus Pattern #10 shim (ratified — already actively closed)

**Closure mode:** Ratified — already actively closed by PROJ-390.

The original PROJ-381 review (`Reviews/results/2026-05-08_230318_code_proj-381-error-handling-cleanup-strategy-ui-assets_req-req_20260508_230317_779973/findings/07_architecture_rules_report.md:101-103`) identified MAJ-013 as the module-level `log_event()` / `set_event_handler()` / `get_event_handler()` "compatibility shim" at the former `game/core/event_logging.py:57-88`. **PROJ-390 retired that shim** — see the docstring at `game/core/event_logging.py:30-32` and `Projects/active_projects/PROJ-390/plan.md:21`.

Verified by Grep: only `EventBus` is imported across `game/core/__init__.py:105`, `game/simulation/combat/attack_contract.py:44`, `game/simulation/combat/weapon_firing_system.py:29`, and `game/strategy/engine/game_session.py:59`. Zero call sites remain for the deleted module-level functions. The four remaining `Pattern #10` references in the codebase (`projectile.py`, `empire.py`, `fleet.py`, `builder/event_bus.py`) are PROJ-382 Phase 2 *constructor-injection* breadcrumbs — the canonical Pattern #10 implementation, not the retired shim. The PROJ-395 reviewer flagged `event_logging.py` because it was in scope but did not pick up that PROJ-390 had already closed the finding. No code change needed.

## Cross-reference and validators

`Projects/active_projects/PROJ-395/decisions.md` updated with the closure pointer to PROJ-409 commit `c0ff79f92`. `python Projects/scripts/validate_audit_ready.py PROJ-395` PASSES (no regression). `validate_audit_ready.py PROJ-409` PASSES.
