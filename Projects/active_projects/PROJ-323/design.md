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

PROJ-323 is the largest project by item count (159 items) but the lowest priority (P2 polish). The work is mechanical: simplify imports, parametrize identical-pattern test clusters (3+ members), flatten nested patches, replace fragile assertions, and replace reimplemented production logic with reference values. No architecture is at stake; the value is reduced LOC and improved readability of the test suite.

41 of 159 items were obsoleted by upstream PROJ-321/322 work — the target test file no longer existed by the time PROJ-323 reached the task. Each obsolete-skipped item is documented in the relevant `phase_N_checklist.md` with `_(skipped — upstream project already deleted target file)_` notation, preserving the audit trail rather than silently removing the row.

Pass 1 landed 27 substantive refactors across all 5 phases before the worker hit its context budget at ~340 tool uses. Pass 2 closed the Phase 3 parametrize sweep (24 deferred → 23 substantive + 1 documented-rationale) and the Phase 5 logic-heavy work (19 deferred → 9 substantive + 10 leave-as-is/documented-intent). The ≥3-member parametrize threshold rule (per OpenCode plan-review) meant Tasks 3.15, 3.27, 3.37 were correctly left as-is rather than being wrapped in unnecessary `@pytest.mark.parametrize` indirection over 2-test clusters.

## Swarm Findings Summary
Combined analysis from individual agent reports in `findings/`.

### Architecture

The standard refactoring patterns landed throughout:

- `@pytest.mark.parametrize` consolidation for identical-pattern clusters (Phase 3, CAT-10).
- `patch.multiple` for flattening nested patches (Phase 2, CAT-8).
- Reference-value comparison instead of reimplemented production logic (Phase 5, CAT-12).
- Semantic comparisons (e.g., set issubset, structural equality) instead of fragile `any()` scans over loosely-typed collections (Phase 4, CAT-11).

Cross-project disjointness: the PROJ-323 manifest has zero overlap with the PROJ-322 manifest (verified by OpenCode plan-review I-003). The 36 files overlapping with PROJ-321 were handled by the obsoletion-check pattern documented in `plan.md` Cross-Project Dependencies — a per-task pre-flight `ls <target-path>` check before starting work catches the upstream-deletion case cleanly.

### Key Patterns to Reuse

- **Parametrize threshold rule (≥3 truly identical members)**: see `tests/unit/research/tech_tree/test_cycle_detection.py` for a 3-test cycle detection cluster collapsed into one parametrized test; see `tests/unit/strategy/data/test_defense_isolation.py` for class-level parametrize across Attack/Defense.
- **Reference value over production call** for stable expecteds: see `tests/unit/simulation/projectile/test_projectile_manager.py` for hardcoded reference values with derivation comments in docstrings (Tasks 5.18, 5.19, 5.23).
- **Soft-assertion regression guard**: see `tests/regression/test_deprecated_code_removed.py` (Task 4.2) for converting hard count-based assertions to advisory soft assertions that preserve the regression signal without failing the build on expected additions.
- **Module-level fixture preference**: ~40 method-level imports were hoisted to module scope in `tests/unit/core/test_protocols.py` (Task 1.X), as method-level imports in test files (used in production for circular-dependency avoidance) carry no benefit and harm readability.

### Dependencies & Risks

1. **Cross-project file overlap with PROJ-321** — 41 PROJ-323 tasks were correctly marked obsolete because the upstream PROJ-321 deleted the target file. Mitigation: per-task pre-flight `ls <target-path>` check before starting work. Worked cleanly throughout both passes.
2. **Below-threshold parametrize trap** — auto-applying parametrize to any 2-test cluster would harm readability by introducing indirection without consolidation benefit. Mitigation: ≥3-member rule enforced per plan-review (Tasks 3.15, 3.27, 3.37 correctly left as-is).
3. **Reference-value staleness** — hardcoded expected values can go stale when production logic changes. Mitigation: every reference value carries a derivation docstring naming the production version it was validated against, so a future maintainer can re-derive on a production change.

### Opportunities Discovered

- The parametrize sweep collapsed many test files significantly (e.g., `test_superweapon_handler_validation.py` 5+5 handler classes merged via class-level parametrize). The remaining `test_command_handlers.py` 11-handler cluster (Task 3.34) was deferred with rationale: pulling all 11 into a class-level parametrize would lose per-class organization aligned with production structure. A future style decision could reconsider.
- The pattern of method-level imports for circular-dependency avoidance is rare in test files but common in production. Hoisting test imports to module-level was safe in all observed cases — no test file exercises a circular-import scenario that requires deferred binding.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
