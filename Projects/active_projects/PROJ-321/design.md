# PROJ-321: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Test Review

- **Review directory:** `Reviews/results/2026-05-02_204633_test-review/`
- **Item counts:** OpenCode CONFIRMED candidates for this tier: 78 (CAT-1=32 + CAT-2=36 + CAT-3=10 from SUMMARY tallies) | Independently verified: 79 | Needs-rework: 1 | Rejected: 3 | Out-of-scope: 3
- **LOC scope:** Claimed total LOC across all P0 items in candidates.json: 5,038 | Verified-only LOC (V + NR): 5,038
- **Summary:** P0 (CAT-1/2/3): tests with zero or negative value - trivial-pass bodies, tests that exercise no production code, and dead test files (repro scripts, empty placeholders).

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
