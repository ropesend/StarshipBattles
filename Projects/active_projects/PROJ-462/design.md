# PROJ-462: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Audit

- **Audit directory:** `Reviews/results/2026-05-19_223900_type-audit/`
- **Bundle counts:** Audit verified: 51 total (across all 3 sibling projects) | This bundle: 17 verified, 1 uncertain (resolved → included with carve-out), 0 deferred | Project siblings: PROJ-463 (domain), PROJ-464 (presentation)
- **Layer coverage:** core, engine, research, services, assets
- **Severity breakdown:** 3 CRITICAL (Vector2, validate_enum, collision None-guard), ~9 MAJOR (formula_evaluator, registry, state_machine, core entity/mutator protocols, json_utils implicit-Optional), 5 STRATEGIC (strict-mode migration: research, services, assets, engine, core)
- **Sequencing:** This is the dependency root. The Vector2 fix (Phase 1.1) and core-protocol narrowing resolve ~130 downstream mypy errors in PROJ-463/PROJ-464; this project should be implemented first.

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
