# PROJ-382: Pattern conformance — Facade integrity, EventBus injection, doc drift, LOC sweep (2026-05-07)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-382` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-382 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Critical — Facade bypass eradication (Pattern #5) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Major — Pattern #2/#10/#31 + naming + conv | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Minor — CQRS/#7/#12 fixes + doc drift | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Strategic — Pattern doc-adds | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. LOC ceiling sweep (5 non-PROJ files) | Complete (4/5; Task 5.4 deferred) | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-05-08
**Active Phase:** All phases complete (closeout).
**Last Action:** Phase 5 LOC sweep — 4 of 5 files decomposed; Task 5.4 (superweapon_order_processor) deferred per `findings/verification_report.md`.
**Next Action:** Final regression + closeout commit.
**Blockers:** None

## Overview
This project applies the verified findings from the 2026-05-07 pattern audit. After a third skeptical pass against `docs/02_PATTERNS.md`, 21 audit findings (+ 6 user-included uncertain items) survived as in-scope work, plus 5 LOC ceiling files not already covered by an active PROJ. The project's defining risk is the 2 CRITICAL Pattern #5 (Facade) bypass sites in `build_queue_screen.py` and `empire_build_queue_window.py` — these decay silently without an AST static-guard, which Phase 1 includes.

## Goals
- Phase 1: Eliminate the 4 facade-bypass dispatch sites and the public `self.session` propagation chain that enables them; install AST static-guard against regression.
- Phase 2: Restore Pattern #2 TypeGuard usage at one site, Pattern #10 EventBus injection in Empire/Fleet/projectile, Pattern #31 modal-window base class for `DesignSelectorWindow`, and rename builder `EventBus` → `WorkshopEventBus` to remove the long-standing naming collision; replace one hardcoded superweapon list with the registry; clean up empty `simulation/components/__init__.py`.
- Phase 3: Replace bare `json` with `json_utils` in 3 sites + remove 1 unused import; remove `GameSession.handle_command` tautology guard; route `superweapon_command_handlers.py` import via canonical `handlers/base.py`; tighten `ProductionSpawner` to require `registries=`; reconcile Pattern #23 (5 → 6 phases) and Pattern #7 (canonical path) doc drift.
- Phase 4: Promote the recurring "Re-Export Shim" pattern to `docs/02_PATTERNS.md` (4+ confirmed sites); document the strategy-config singleton-accessor variant in Pattern #12.
- Phase 5: Decompose 5 LOC-ceiling-violating files in `game/` that are not already covered by an active PROJ.

## Scope
**In:** Findings from `Reviews/results/2026-05-07_220452_pattern-audit/` that survived independent verification, by layer + pattern-area:
- `ui/` — Pattern #5 facade bypass, Pattern #31 modal window base, Pattern #10 EventBus naming, Pattern #12 json import, undocumented re-export shim sites.
- `strategy/` — Pattern #5 session leakage root, Pattern #6 tautology, Pattern #7 shim import path, Pattern #10 dual-path event logging in Empire/Fleet, Pattern #12 json + ProductionSpawner DI tightening, doc-drift on Pattern #23 + #7.
- `simulation/` — Pattern #2 TypeGuard miss, Pattern #10 module-level `log_event` in projectile, hardcoded superweapon list, empty `components/__init__.py`, planetary.py LOC split, battle_engine.py LOC split.
- `docs/02_PATTERNS.md` — Pattern #23 + #7 reconciliation, Re-Export Shim doc-add, Pattern #12 singleton-accessor clarification.

**Out:**
- VER-001 / PAT-02-001 (`GameSession.get_default_registry_provider`) — DISPUTED in audit's own verifier; Pattern #3 limits restriction to simulation layer. See `findings/verification_report.md`.
- U1, U2, U3 — UI imports of `strategy.engine.commands` (~127), `strategy.services.*` (40), `strategy.systems.*` (26). Deferred to a future dedicated PROJ — see `findings/bundling_decisions.md`.
- LOC ceiling files already covered by active PROJs (race_summary_panel.py, battle_screen.py, ship_detail_panel.py, production_engine.py, workshop_event_router.py, build_queue_panel_factory.py, battle_panels.py, registry.py, spec_compiler.py).
- 13 REJECTED items (already documented intentional, intra-layer isinstance, audit-misreads, etc.) — see `findings/verification_report.md`.

## Key Files
| Component | File Path |
|-----------|-----------|
| Facade-bypass dispatch (Phase 1) | `game/ui/screens/build_queue_screen.py` |
| Facade-bypass dispatch (Phase 1) | `game/ui/screens/empire_build_queue_window.py` |
| Session leakage root (Phase 1) | `game/ui/screens/strategy_screen.py` |
| Session propagator (Phase 1) | `game/ui/screens/strategy_build_queue_manager.py` |
| Session propagator (Phase 1) | `game/ui/screens/strategy_windows/build_queue_windows.py` |
| Empire/Fleet event logging (Phase 2) | `game/strategy/data/empire.py`, `game/strategy/data/fleet.py` |
| Projectile event logging (Phase 2) | `game/simulation/entities/projectile.py` |
| Builder EventBus rename (Phase 2) | `game/ui/screens/builder/event_bus.py` (+ ~15 importers) |
| Pattern doc reconciliation (Phase 3) | `docs/02_PATTERNS.md` (#23 + #7 entries) |
| Re-Export Shim doc-add (Phase 4) | `docs/02_PATTERNS.md` |
| LOC ceiling decomposition (Phase 5) | `game/simulation/components/abilities/planetary.py`, `game/simulation/systems/battle_engine.py`, `game/strategy/services/fleet_navigation_service.py`, `game/strategy/engine/superweapon_order_processor.py`, `game/strategy/engine/conflict_resolution_engine.py` |

## Related Documents
- [design.md](design.md) — Source-audit summary, risk notes, layer/pattern coverage.
- [decisions.md](decisions.md) — Bundling rationale + Phase D user decisions.
- [findings/verification_report.md](findings/verification_report.md) — Verified / Rejected / Uncertain / Out-of-scope tables.
- [findings/source_audit.md](findings/source_audit.md) — Pointer to the source audit.
- [findings/bundling_decisions.md](findings/bundling_decisions.md) — Phase D interactive bundling record.
- Pattern entries this project touches: `docs/02_PATTERNS.md` patterns #2, #3, #5, #6, #7, #10, #12, #23, #31.

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
