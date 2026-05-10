# PROJ-205: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

This project addresses 6 verified actionable findings (+ 1 comment fix) from the legacy code audit review (`2026-02-27_141504_general_legacy-code-audit`). The original audit produced 34 findings across 8 agents. Four verification agents independently confirmed only 7 as genuinely actionable - the remaining 27 were disputed, false positives, or non-actionable.

### Source Review
- **Review:** `Reviews/results/2026-02-27_141504_general_legacy-code-audit/report.md`
- **8 review agents** scanned entire `game/` production codebase (418 files, ~87K lines)
- **4 verification agents** skeptically examined all Critical and Major findings

### Baseline
- **Tests:** 12,743 passed, 1 skipped
- **Branch:** complexity-cycle-20

## Swarm Findings Summary

### Verification Results (Key Insight)
The verification process dramatically reduced actionable findings:
- 10 findings were **disputed as false positives** (agents misread code, missed callers, or flagged legitimate patterns)
- Both "Critical" items were **downgraded** after verification
- Notable false positives:
  - `is_vector2_like()` claimed unused but is called internally by `get_position()`
  - `ComponentCacheManager.reset()` claimed never called but IS called via wrapper in conftest
  - Formatter modules claimed "duplicate" but serve different purposes (pure functions vs stateful class)
  - AI behaviors claimed "test-only" but are instantiated in every AIController

### Architecture
- Codebase is well-organized with clean layer boundaries
- PROJ-58 (backward compat eradication) was confirmed complete
- Import graph is healthy with zero orphaned modules
- No systemic legacy rot detected

### Key Patterns to Reuse
- **Registry-path colonization tests**: `test_fleet_order_processor.py:574-636` - pattern for providing `component_registry` in tests
- **Standard test fixture pattern**: Tests use `component_registry` from conftest fixtures

### Dependencies & Risks
1. **Colonization tests (STR-002)** - 19 tests need updating. Risk: some tests may rely on legacy fleet-removal behavior in their assertions. Mitigation: carefully check each test's assertions about fleet state after colonization.
2. **AbilityManager branching (SIM-001)** - Changing branching could affect edge cases in module identity drift. Mitigation: run full test suite, not just ability manager tests.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
