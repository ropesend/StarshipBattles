# PROJ-154: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [test-suite-cleanup-v3](../../Reviews/results/2026-02-16_105410_general_test-suite-cleanup-v3/)
- **Type:** General Review (Test Suite Cleanup)
- **Date:** 2026-02-16
- **Report:** [View Full Report](../../Reviews/results/2026-02-16_105410_general_test-suite-cleanup-v3/report.md)
- **Validation:** [Validation Review 1 (UI + Strategy)](../../Reviews/results/2026-02-16_105410_general_test-suite-cleanup-v3/findings/validation_1_ui_strategy.md)

## Initial Analysis

The code review (v3) identified ~85 removal candidates across the test suite totaling ~28,600 lines. A detailed validation review of 28 findings (14 UI + 14 Strategy) found:

- **12 CONFIRMED** for full removal — files that test nothing real, are strict duplicates, or are empty scaffolds
- **6 DISPUTED** (should keep) — tests that appear trivial but provide genuine value (import smoke tests, regression tests, interface contracts, accessibility checks, complementary coverage)
- **10 MODIFIED** (partial removal) — files with a mix of valuable and duplicate/trivial tests

### Categories of Dead Code Found

1. **MagicMock-only tests** (UI-1, UI-4, UI-11 partial, UI-14 partial): Tests that create MagicMock objects, set attributes, and assert those same attributes. Zero game code is ever called.

2. **Empty scaffolds** (STR-4, STR-5, STR-6, STR-7): Files named "edge_cases" or "errors" that contain only 2-3 import-existence checks. Scaffolds created during TDD that were never populated with actual tests.

3. **Strict duplicates** (STR-2, STR-10): Older test files that are strict subsets of newer, more comprehensive versions. Every test in the older file has an equivalent in the newer one.

4. **Partial duplicates** (UI-2, UI-6, UI-7, UI-8, STR-1, STR-3): Files where some tests overlap with better tests elsewhere, but a few tests are unique. Requires migration before deletion.

5. **Trivially obvious constants** (UI-5, UI-9 partial, UI-13 partial): Tests that assert static integer class attributes are positive (`assert X > 0`). These constants cannot silently become zero or negative.

6. **One-time verification** (STR-14 partial): Legacy cleanup checks (`not hasattr(engine, '_old_method')`) that served their purpose when the refactor happened and no longer provide ongoing value.

## Key Patterns to Reuse

- **Test migration pattern**: Read source, adapt test to target file's patterns (real objects vs mocks), add to appropriate test class, verify, delete source
- **Partial edit pattern**: Identify specific test methods/classes to remove, delete them, clean up empty classes and unused imports, verify remaining tests still pass

## Dependencies & Risks

1. **Pre-existing failures**: 145 tests are failing BEFORE this project starts. These are NOT our regressions. Risk: confusion about whether a failure is pre-existing or newly introduced. Mitigation: track that the failure count stays at 145, not higher.

2. **STR-1 migration complexity**: Merging 16 tests across 3 new interface classes is the largest migration. Risk: import issues or test fixture differences. Mitigation: carefully follow the target file's existing patterns.

3. **UI-7 surgical removal**: Removing 14 tests from a 408-line file while keeping 6 requires careful editing. Risk: accidentally breaking kept tests by removing shared fixtures. Mitigation: run targeted tests after each removal.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
