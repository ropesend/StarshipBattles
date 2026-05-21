# PROJ-470: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Audit

- **Audit directory:** `Reviews/results/2026-05-20_075227_pattern-audit/`
- **Bundle counts:** Audit verified (its own internal pass): 2 critical + 3 major + 11 minor confirmed | This bundle: 15 verified, 3 uncertain (all resolved to Defer), 0 deferred-to-another-project | Project siblings: none (single-project run; V=15 < 30 per Protocol 18).
- **Layer + pattern-area coverage:** ui, strategy, core. Pattern-areas: facade (#5), strategy_modal (#31), event_bus (#10), protocol_typeguard (#2), ability_stat (#29), doc_drift (#32, #36), loc (triage), undocumented (UP-001/UP-002/UP-006).
- **Severity breakdown:** 2 CRITICAL (Pattern #5 facade read-path gap), 3 MAJOR (Pattern #5 session bypass, Pattern #31 SettingsWindow, Pattern #10 EventBus), 7 MINOR (4 Pattern #2 TypeGuards, 1 Pattern #29 enum, 2 doc-drift, 1 LOC triage), 3 STRATEGIC (undocumented-pattern doc-adds).

### Risk Notes (CRITICAL pattern-bypass findings)

The Pattern #5 facade read-path gap is the structural risk in this project. The `StrategySessionFacade` enforces the **write path** (commands route through `facade.handle_command()`, protected by `tests/static_guards/test_facade_bypass_guard.py`), but there is **no equivalent guard for the read path** — 135+ `game/ui/` import sites pull strategy data/engine objects directly (`BuildQueueSource`, `FleetCapabilityCalculator`, `CarriedVehicle`, deployed-group dataclasses, `ContainableKind`, etc.). This makes the facade a write-path-only half-facade. Without a read-path static guard, every new UI screen will continue to reach past the facade and the boundary erodes silently. **Phase 1 is therefore scoped as policy + read-path static guard + first migration slice — not a full 135-site sweep in one pass** (per the Codex consult, scoping FAC-001 as "policy + first slice" prevents it from dominating the whole project). The full migration of the remaining sites proceeds incrementally under the guard, and if large enough should be decomposed into its own project.

Independent-verification correction: the audit's `raw/protocol_registry.json` omitted the `is_fleet`/`is_planet`/`is_storm`/`is_star_system` TypeGuards, but they DO exist in `game/core/protocols/strategy_entities.py:415-445`. This makes the Pattern #2 (TG-001..004) fixes tractable drop-in replacements rather than scope-expanding "add a TypeGuard first" work.

## Initial Analysis

See `findings/verification_report.md` for the full independent re-verification (a third pass with a different reader than the audit's Phase-1 reviewers and its internal verifier). Every VERIFIED item below was confirmed against live code; every OUT_OF_SCOPE item was confirmed as a non-issue or already filtered by the audit's own `verification.md`.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale, including the single Codex planning consult that advised on bundling and the UNCERTAIN-item resolutions.
