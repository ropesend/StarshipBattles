# Prospective Projects Summary

## Sweep Source
- **Review:** 2026-02-11_sweep_full-codebase-sweep
- **Total Findings:** 396 (44 Critical, 156 Major, 144 Minor, 52 Info)
- **Findings Assigned to Projects:** 396 / 396
- **Unassigned Findings:** 0

## Proposed Projects

| # | Project | Findings | Critical | Major | Minor | Info | Scope | Execution Order |
|---|---------|----------|----------|-------|-------|------|-------|-----------------|
| 1 | [Architecture Layer Violations](architecture_layer_violations/proposal.md) | 52 | 9 | 14 | 24 | 5 | Large | 1st |
| 2 | [God Class Decomposition](god_class_decomposition/proposal.md) | 19 | 0 | 15 | 0 | 4 | Medium | 2nd |
| 3 | [Legacy Dead Code Eradication](legacy_dead_code_eradication/proposal.md) | 65 | 6 | 24 | 26 | 9 | Large | 3rd |
| 4 | [Duplication Elimination](duplication_elimination/proposal.md) | 59 | 9 | 26 | 19 | 5 | Large | 4th |
| 5 | [Consistency Standardization](consistency_standardization/proposal.md) | 79 | 5 | 27 | 35 | 12 | Large | 5th |
| 6 | [Test Coverage: Core and Simulation](test_coverage_core_simulation/proposal.md) | 51 | 8 | 22 | 14 | 7 | Medium | 6th |
| 7 | [Test Coverage: Strategy and UI](test_coverage_strategy_ui/proposal.md) | 71 | 7 | 28 | 26 | 10 | Large | 7th |

## Execution Order Recommendation

1. **Architecture Layer Violations** (52 findings, 9 Critical) -- Fix first because layer violations are the most fundamental structural issue. They prevent headless testing, create circular imports, and block proper testability. Every other project benefits from clean layer boundaries.

2. **God Class Decomposition** (19 findings, 15 Major) -- Fix second because decomposing god classes is easier once layer boundaries are clean. However, this project heavily overlaps with existing PROJ-86 through PROJ-89 and may already be covered. Evaluate overlap before starting.

3. **Legacy Dead Code Eradication** (65 findings, 6 Critical) -- Fix third or in parallel with god class work. Removing dead code is purely subtractive and safe. Doing it before consistency and duplication work means less code to standardize and deduplicate.

4. **Duplication Elimination** (59 findings, 9 Critical) -- Fix fourth. Some duplications exist because of layer violations (can't share code across boundaries), so fixing layers first may naturally resolve some. The 21 UNK findings need investigation before fixing.

5. **Consistency Standardization** (79 findings, 5 Critical) -- Fix fifth. Consistency work is most effective after dead code is removed (fewer files to standardize) and layer violations are fixed (clear conventions per layer). This is the largest project by finding count but most findings are simple.

6. **Test Coverage: Core and Simulation** (51 findings, 8 Critical) -- Fix sixth. Can run in parallel with any of the above, but tests are more valuable after the code is cleaned up (less risk of writing tests for code that will be refactored or deleted).

7. **Test Coverage: Strategy and UI** (71 findings, 7 Critical) -- Fix last. Depends on stable lower layers and benefits from all other cleanup being complete. UI tests in particular are more meaningful after god classes are decomposed and legacy code is removed.

**Parallelization opportunities:**
- Projects 3 (Legacy) and 4 (Duplication) can run in parallel since they rarely touch the same files
- Projects 6 and 7 (Test Coverage) can run in parallel with each other and with most other projects
- Project 5 (Consistency) can run in parallel with test coverage projects

## Coverage Analysis
- Findings covered: **396/396 (100%)**
- No findings intentionally excluded

## Overlap Notes

The sweep found significant overlap with 14 existing active projects:

| Existing Project | Overlapping Proposed Project(s) | Overlap Level |
|-----------------|-------------------------------|---------------|
| PROJ-106 (Architecture Layer Violations) | Architecture Layer Violations | **Full overlap** |
| PROJ-90 (Untangle Circular Dependencies) | Architecture Layer Violations | Significant |
| PROJ-92 (Clean Up Circular Dependency Artifacts) | Architecture Layer Violations | Significant |
| PROJ-91 (Unify Resource/State Logic) | Architecture Layer Violations | Partial |
| PROJ-93 (Update Protocol Layer Type Annotations) | Architecture Layer Violations, Consistency | Partial |
| PROJ-86 (Critical UI Tier) | God Class Decomposition | **Full overlap** |
| PROJ-87 (Strategy Data Tier) | God Class Decomposition | **Full overlap** |
| PROJ-88 (Simulation Core Tier) | God Class Decomposition | **Full overlap** |
| PROJ-89 (Remaining UI Tier) | God Class Decomposition | **Full overlap** |
| PROJ-109 (Legacy Cleanup) | Legacy Dead Code Eradication | **Full overlap** |
| PROJ-58 (Eradicate Backward Compat Shims) | Legacy Dead Code Eradication | Partial (may be complete) |
| PROJ-108 (Duplication Elimination) | Duplication Elimination | **Full overlap** |
| PROJ-107 (Consistency and API Standardization) | Consistency Standardization | **Full overlap** |
| PROJ-95 (Resource API Consistency) | Consistency, Duplication, Legacy | Partial |
| PROJ-94 (Resource API Cleanup) | Legacy Dead Code Eradication | Partial |
| PROJ-110 (Test Coverage - Core Systems) | Test Coverage: Core and Simulation | **Full overlap** |
| PROJ-111 (Test Coverage - UI and Framework) | Test Coverage: Strategy and UI | **Full overlap** |
| PROJ-105 (Visual Regression Testing) | Test Coverage: Strategy and UI | Partial |

**Recommendation:** Several existing projects (PROJ-106 through PROJ-111) appear to have been created from an earlier iteration of similar analysis. These prospective projects should either supersede those existing projects (incorporating their existing work) or be used to validate and extend them. The God Class Decomposition project (proposed #2) is almost entirely covered by PROJ-86 through PROJ-89 and may not need a separate project.
