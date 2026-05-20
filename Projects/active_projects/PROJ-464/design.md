# PROJ-464: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Audit

- **Audit directory:** `Reviews/results/2026-05-19_223900_type-audit/`
- **Bundle counts:** Audit verified: 51 total (across all 3 sibling projects) | This bundle: 12 verified, 1 uncertain (TYP-SR resolved → included as Protocol seam), 0 deferred | Project siblings: PROJ-462 (foundation), PROJ-463 (domain)
- **Layer coverage:** ui, unknown/top-level
- **Severity breakdown:** 0 CRITICAL, ~10 MAJOR (StrategyScreen/BattleScreen/list-filter/builder Any returns, StrategyRenderer Protocol seam, 2 UI type-ignores, missing UI/top-level returns, implicit-Optional), ~2 MINOR (bulk UI display getters, _to_tuple), 2 STRATEGIC (strict-mode migration: unknown/top-level, ui)
- **Sequencing:** Last of the three. Consumes types produced by PROJ-462 (core protocols) and PROJ-463 (strategy/facade). UI strict-mode is the largest single layer (~1,084 errors, majority external `pygame_gui`).
- **Rejected here:** TYP-APP (`game/app.py` Game scene accessor proxies) stays `-> Any` — intentionally loose for `Game.__new__(Game)` tests; see findings/verification_report.md.

## Initial Analysis
[Findings from Phase A code review - what was discovered about the codebase]

## Swarm Findings Summary
Combined analysis from individual agent reports in `findings/`.

### Architecture
[Key architecture points relevant to implementation]

### Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

### Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

### Opportunities Discovered
- [Opportunity 1]

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
