# PROJ-322: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Test Review

- Review directory: `Reviews/results/2026-05-02_204633_test-review/`
- OpenCode CONFIRMED candidates for this tier (P1): 93 - 51 from category-level shard reports (CAT-4: 13 + CAT-5: 14 + CAT-6: 17 + CAT-7: 7) + 42 cross-shard cluster members (APC-001: 16 + APC-002: 11 + APC-003: 8 + DUP-001..3: 3 + HLP-001..4: 4)
- Independently verified: 111
- Needs-rework: 4
- Rejected: 1
- Out-of-scope: 3

The verified-item count exceeds the OpenCode CONFIRMED count because the OpenCode counts in `SUMMARY.md` count the cross-shard clusters (APC/DUP/HLP) once per cluster, while the verifier expanded each cluster into per-file checklist items (e.g., APC-001 = 16 individual files, APC-002 = 10 verified files, APC-003 = 8 files, plus 3 DUP + 4 HLP cluster-level entries). The 115 P1 items in `candidates.json` reflect the per-file/per-cluster expansion.

Claimed total LOC for the P1 tier (sum of `loc_affected` across V + NR items): approximately 9,629 LOC of test-side rewrites and consolidations. There is no separate "claimed vs verified" gap at the LOC level for P1 because the verifier kept all V + NR items at their reviewed LOC scope; rejected (1 item, 40 LOC) and out-of-scope (3 items, ~145 LOC) churn was excluded from this project before the per-phase totals above were computed.

**One-sentence summary:** P1 (CAT-4/5/6/7 + APC/DUP/HLP cross-shard clusters): test quality and performance debt - duplicate tests, expensive fixtures, brittle mocking, sleep-based waits, and cross-file anti-patterns including 16 `__new__` bypass-init UI test files and source-inspection guards.

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
