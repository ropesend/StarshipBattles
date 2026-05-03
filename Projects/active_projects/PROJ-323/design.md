# PROJ-323: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Test Review

- **Review directory:** `Reviews/results/2026-05-02_204633_test-review/`
- **Priority tier:** P2 (CAT-8, CAT-9, CAT-10, CAT-11, CAT-12)
- **Item counts:** OpenCode CONFIRMED candidates for this tier: 119 (CAT-8=22 + CAT-9=24 + CAT-10=37 + CAT-11=13 + CAT-12=23) | Independently verified: 156 | Needs-rework: 3 | Rejected: 1 | Out-of-scope: 6
- **Claimed total LOC vs verified-only LOC:** All 159 surviving items carry a `loc_affected` total of approximately **10,735 LOC** (CAT-8=3089, CAT-9=1619, CAT-10=4614, CAT-11=335, CAT-12=1078). No P2-tier items were filtered out at the LOC step; the verified-only LOC equals the claimed LOC for surviving items.

P2 (CAT-8/9/10/11/12): nice-to-have improvements — needless complexity, micro-simplifications, parametrize opportunities, fragile assertions, and tests that reimplement production logic.

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
