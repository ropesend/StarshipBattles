# PROJ-470: Pattern conformance - facade read-path, modal, event-bus + doc/hygiene drift (2026-05-20)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-470` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-470 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Critical - Facade read-path gap | Deferred -> PROJ-472 | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Major - SettingsWindow, EventBus (FAC-003 deferred -> PROJ-472) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Minor - TypeGuards (scoped), source_kind enum, doc-drift (LOC triage out-of-scope) | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Strategic - Document 3 undocumented patterns | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Codex-audit remediation (4 verified findings) | Complete | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-05-20
**Active Phase:** Complete (pending audit/user verification)
**Last Action:** Implemented surviving items (MOD-001, EVT-001, ENUM-001, TG-003, DOC-032/036, UP-001/002/006) via TDD; ran one-round Codex audit; remediated all 4 verified Codex findings in Phase 5. `validate_audit_ready.py PROJ-470` PASSES.
**Next Action:** Orchestrator commit + user verification
**Blockers:** None

## SCOPE REVISION (2026-05-20, Protocol 06 — dual independent+Codex review)
- **Phase 1 (all FAC items) DEFERRED to PROJ-472** "Facade read-path migration". The facade read-path gap is a deliberately-deferred architecture migration (PROJ-382 / U1–U3) spanning ~93 `game/ui/` files, not a cleanup CRITICAL. Captured in PROJ-472 plan/design/decisions per Protocol 07.
- **Phase 2 Task 2.1 (FAC-003 StrategyScreen.session) DEFERRED to PROJ-472** — same migration program.
- **Phase 3 Task 3.5 (LOC-ceiling triage of 10 files) OUT-OF-SCOPE** — decomposition program, not a conformance fix; logged for a future project.
- **TypeGuards scoped per-site:** TG-003 swapped (proven equivalent); TG-001/TG-002/TG-004 KEEP isinstance (serialization / behavior-branching / value-affecting + duck-typed guards are broader). See decisions.md.
- See `decisions.md` for full rationale.

## Overview
Created from the pattern-audit at `Reviews/results/2026-05-20_075227_pattern-audit/` after an independent third-pass re-verification (15 of the audit's actionable findings survived; 3 undocumented-pattern items were deferred, 3 were confirmed out-of-scope). The bundle covers Pattern #5 (Facade/Delegate) read-path bypasses, Pattern #31 (Strategy Modal Window) non-conformance, Pattern #10 (Event Bus) drift, Pattern #2 (Protocol+TypeGuard) same-layer isinstance drift, Pattern #29 (source_kind enum), three doc-drift entries, a LOC-ceiling triage, and three undocumented-pattern doc-adds. **Notable risk:** Phase 1 includes the CRITICAL Pattern #5 facade read-path gap (135+ UI import sites, write-path-only half-facade) — this is a structural architectural decay, scoped here as policy + static-guard + first migration slice, not a full 135-site migration in one pass.

## Goals
- **Phase 1 (Critical):** Close the Pattern #5 facade read-path gap — decide and implement the read-path policy (add read DTOs or formally document UI-safe read types), add a read-path static guard, and migrate/exempt the densest BuildQueue/fleet bypass sites.
- **Phase 2 (Major):** Migrate the 4 `StrategyScreen.session` read-path consumers behind the facade; convert `SettingsWindow` to subclass `StrategyModalWindow`; fix the stale `EventBus` docstring path and reconcile Pattern #10 doc.
- **Phase 3 (Minor):** Replace 4 same-layer concrete `isinstance` checks with existing TypeGuards; add a `StrEnum`/`Literal` for `IAbilitySource.source_kind`; reconcile Pattern #32 and Pattern #36 doc-drift entries; triage the 69 LOC-ceiling files (prioritize top-10; full decomposition is a separate future project).
- **Phase 4 (Strategic):** Document 3 undocumented patterns (HabitabilityFactor Registry, AbilityMetadataRegistry, RoleRegistry) in `docs/02_PATTERNS.md`.

## Scope
**In:** Pattern-areas — `facade` (#5), `strategy_modal` (#31), `event_bus` (#10), `protocol_typeguard` (#2), `ability_stat` (#29), `doc_drift` (#32, #36), `loc` (triage), `undocumented` (UP-001/UP-002/UP-006). Layers: ui, strategy, core.
**Out:**
- 3 UNCERTAIN undocumented-pattern items deferred to a future audit: UP-003 PerPlayerUiState and UP-005 FacadeSessionState (already documented under Pattern #11), UP-004 Declarative Dispatch Table (recurs in only 2 registries, below the 3+ promotion bar). See `findings/verification_report.md`.
- 3 OUT_OF_SCOPE items the audit's own verifier disputed (MAJ-H1 simulation_adapter registry injection — correct pattern; MAJ-H4 RaceSetup/NewGameSetup screens — not strategy modals) and the Pattern #3 `component_layers.py` legacy-save fallback (accepted convention). See `findings/verification_report.md`.
- Full decomposition of all 69 LOC-ceiling files (Phase 3 only triages + prioritizes top-10).
- Pattern #30 (superseded by #31) is excluded by the audit.

## Key Files
| File | Items |
|------|-------|
| `game/ui/screens/strategy_screen.py` | FAC-003 (session property) |
| `game/ui/panels/build_queue_controller.py` | FAC-002 (dense bypass) |
| `game/ui/screens/build_queue_screen.py` | FAC-002 (runtime import) |
| `game/ui/screens/fleet_data_source.py` | FAC-002 (FleetCapabilityCalculator) |
| `game/ui/screens/settings_window.py` | MOD-001 (StrategyModalWindow) |
| `game/ui/screens/builder/event_bus.py` | EVT-001 (stale path) |
| `game/strategy/data/order_types.py` | TG-001 (isinstance) |
| `game/strategy/facade/dto/fleet_dto.py` | TG-002 (isinstance chain) |
| `game/core/protocols/strategy_entities.py` | ENUM-001 (source_kind) |
| `docs/02_PATTERNS.md` | EVT-001, DOC-032, DOC-036, UP doc-adds |

## Related Documents
- [design.md](design.md) - Source-audit summary and risk notes
- [decisions.md](decisions.md) - Full decisions log (incl. Codex consult)
- [findings/verification_report.md](findings/verification_report.md) - Independent re-verification (verified/rejected/uncertain/out-of-scope)
- [findings/source_audit.md](findings/source_audit.md) - Pointer to the source pattern-audit
- [findings/bundling_decisions.md](findings/bundling_decisions.md) - Bundling rationale + UNCERTAIN resolutions
- Patterns in scope: [Pattern #2](../../../docs/02_PATTERNS.md#2-protocol-typeguard), [#5](../../../docs/02_PATTERNS.md#5-facade-delegate), [#10](../../../docs/02_PATTERNS.md#10-event-bus), [#29](../../../docs/02_PATTERNS.md#29-universal-ability-source), [#31](../../../docs/02_PATTERNS.md#31-strategy-modal-window-base-class), [#32](../../../docs/02_PATTERNS.md#32-compositional-construction), [#36](../../../docs/02_PATTERNS.md#36-re-export-shim)

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
