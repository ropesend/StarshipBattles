# PROJ-466: Error handling cleanup - session-init crash + exception hygiene (2026-05-20)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-466` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-466 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Critical session-init boundary | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Major exception-hygiene fixes | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Minor hardening | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Codex-audit remediation | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-05-20 22:45
**Active Phase:** All phases complete (1-4)
**Last Action:** Phase 4 (Codex-audit remediation) complete: fixed the new-game session-init composition bug, tightened the run_battle test, added the load_planet_image OSError test (+ stellar-fallback OSError parity), restored minefield missing-file WARNING. Full suite green (23473 passed).
**Next Action:** None — ready for orchestrator commit + user verification.
**Blockers:** None

## Overview
Created from the error-audit at `Reviews/results/2026-05-20_065518_error-audit/` after an independent third-pass re-verification that read each cited `file:line` in the live source. 27 findings survived verification across the ui, strategy, simulation, services, core, and assets layers. The standout is **1 CRITICAL boundary failure**: `GameSession(...)` construction sites in `screen_router.py` (and the controller callback) have no `SessionInitializationError` guard, so a galaxy-generation failure crashes the application instead of surfacing a recoverable error dialog (crash-and-corruption-adjacent UX risk). The remaining work is mechanical generic-exception-to-domain-exception swaps and small logging/repr hardening.

## Goals
- **Phase 1:** Close the 1 CRITICAL + 1 coupled MAJOR boundary failure by guarding `SessionInitializationError` at all `GameSession(...)` construction sites and the setup-controller callback, with a regression test exercising the crash path.
- **Phase 2:** Replace 10 MAJOR generic builtin raises / gratuitous broad catches / silent swallows with domain exceptions and explicit handling (replay serialization, strategy data validators, battle_runner, happiness_engine, modifier_icon_service, battle_state_viewer) plus merge `BattleResolutionError` context into the `EnginePhaseError` wrapper.
- **Phase 3:** Apply 15 MINOR hardening items: domain-exception swaps in `fleet_write_service`/`component_activation_state`, LLM/Image DTO `__repr__` overrides, `%r`->`%s` worker logs, `asset_manager` OSError parity + manifest log level, silent-swallow logging, `roles.py` base class, `json_utils` file-I/O swap, duplicate Tk root, and a `satellite_controller` debug log.

## Scope
**In:** Categories `cross_layer_boundary`, `generic_raise`, `broad_except_no_comment`, `error_chaining`, `logging_consistency`, `llm_context_security` (repr/log hardening), `json_bypass` (file-I/O) across the ui/strategy/simulation/services/core/assets layers — see `findings/verification_report.md` for the per-item table.
**Out:** All 128 broad-except sites with valid `# Intentional` comments (scanner false positives); in-memory `json.loads`/`json.dumps`; `app.py:520` deliberate crash-handler diagnostic; the `request_id` doc-only recommendation; `strategy_detail_formatter.py:355` (REJECTED — comment already documents intent). 3 borderline MINOR items deferred to a future audit (`construction_queue.py:186`, `strategy_screen_assets.py:76`, `star_list_window.py:395`) — see `findings/verification_report.md` and `findings/bundling_decisions.md`.

## Key Files
| File | Items |
|------|-------|
| `game/strategy/data/component_activation_state.py` | 2 |
| `game/strategy/data/fleet_capability_calculator.py` | 1 (2 sites) |
| `game/simulation/replay/replay_serialization.py` | 3 |
| `game/services/llm/types.py` | 2 |
| `game/assets/asset_manager.py` | 2 |
| `game/screen_router.py` | 1 (CRITICAL, 2 sites) |
| `game/ui/screens/new_game_setup_controller.py` | 1 |
| `game/strategy/engine/turn_engine.py` | 1 |
| `game/ui/services/modifier_icon_service.py` | 1 |
| `game/ui/screens/battle_state_viewer.py` | 1 |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/verification_report.md](findings/verification_report.md) - Independent re-verification of every audit claim
- [findings/source_audit.md](findings/source_audit.md) - Pointer to the source error-audit
- [findings/bundling_decisions.md](findings/bundling_decisions.md) - Bundling rationale and per-item decisions

## Verification
- [x] All phase checklists complete (Phases 1-4)
- [x] All tests passing (full suite: 23473 passed, 0 failed)
- [x] Audit passed (one-round Codex audit; 4 findings VERIFIED + remediated in Phase 4, 1 REJECTED)
- [ ] User verified
