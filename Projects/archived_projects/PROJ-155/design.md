# PROJ-155: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [test-suite-cleanup-v3](../../Reviews/results/2026-02-16_105410_general_test-suite-cleanup-v3/)
- **Type:** General Review (Test Suite Cleanup)
- **Date:** 2026-02-16
- **Report:** [View Full Report](../../Reviews/results/2026-02-16_105410_general_test-suite-cleanup-v3/report.md)
- **Agents Used:** 8 review agents + 4 validation agents

## Initial Analysis

### Review Scope
8 agents analyzed the entire test suite (~860 files, ~235K lines). 4 independent validation agents then verified each finding with line-by-line skeptical analysis.

### Key Statistics
- **Total removal candidates identified:** ~85 items
- **CONFIRMED for removal after validation:** 47 items across 4 validation reviews
- **DISPUTED (should keep):** 30 items — validators proved these provide real value
- **MODIFIED (partial removal):** 32 items — merge unique tests first, then delete

### Validation Corrections
The validation reviews caught several dangerous false positives:
1. `test_physics_formulas.py` (731 lines) — NOT dead code; formula specification tests
2. `test_singleton.py` (313 lines) — thread safety tests are non-negotiable
3. `test_config_edge_cases.py` (104 lines) — 14 unique boundary/constraint tests, not 3
4. `logger/test_levels.py` (119 lines) — 10 of 11 tests are unique setup/config tests
5. All repro_*.py files — unique bug scenario coverage not in proper test suite
6. `test_fleet_order_transfer.py` — complementary to, not duplicate of, test_transfer_order.py

## Architecture

### Test Directory Structure
```
tests/
├── unit/
│   ├── core/           # Foundation tests (keep: test_singleton, test_config_edge_cases, etc.)
│   ├── simulation/     # MAIN test location (old framework cleanup needed)
│   ├── entities/       # OLD dir — subsets of simulation/entities/ (delete)
│   ├── combat/         # OLD dir — subsets of simulation/ (mostly delete)
│   ├── services/       # OLD dir — subsets of simulation/services/ (delete)
│   ├── components/     # OLD dir — subsets of simulation/components/ (delete)
│   ├── ai/             # Keep all 4 controller test files + adapter files
│   ├── strategy/       # Remove scaffolds/duplicates, keep unique tests
│   ├── ui/             # Remove over-mocked tests, keep edge cases
│   ├── research/       # Delete research_controls/ (zero production code)
│   ├── refactor/       # RENAME to modifiers/ — all 23 files are legitimate
│   ├── builder/        # Partial cleanup (empty stubs)
│   ├── systems/        # Partial cleanup (one-time verification tests)
│   ├── performance/    # Remove scripts, keep reproduce_scaling.py
│   └── regressions/    # Remove test_crash_regressions.py
├── integration/        # ALL CLEAN — no changes needed
└── simulation_tests/   # ALL CLEAN — no changes needed
```

### Key Patterns

**Old Directory Migration Pattern:**
The codebase underwent a test reorganization where tests moved from topic-based directories (combat/, entities/, services/) to a simulation/ mega-directory. The OLD directories still exist and contain strict subsets of the newer, more comprehensive simulation/ tests. Validation confirmed this via spot-checking 6 old-vs-new pairs.

**Edge Cases File Pattern:**
Many `_edge_cases.py` files are actually trivial import-existence scaffolds (21-37 lines) that should be deleted. But some (like `test_config_edge_cases.py`, `test_profiling_edge_cases.py`) contain genuinely unique boundary condition tests that MUST be kept.

**Merge-Before-Delete Pattern:**
For MODIFIED findings, the implementation must:
1. Read both source and target files
2. Identify the unique tests in the source
3. Copy them to the target file with appropriate imports
4. Run the target file's tests to verify
5. Only then delete the source file

## Dependencies & Risks

1. **Phase 3 (Old Directory Trees)** — Highest risk. Validation review 4 warned that old files sometimes use real game objects (integration-style) while new files use MagicMock (unit-style). File-by-file verification is essential.
   - **Mitigation:** Delete one file at a time, run tests after each deletion.

2. **Phase 2 (Merge operations)** — Medium risk. If unique tests rely on source-file-specific fixtures, they may need adaptation when moved.
   - **Mitigation:** Read both files carefully before merging. Verify each merged test passes individually.

3. **conftest.py deletions** — 3 conftest files (builder, systems, ai) have fixture imports that the validation review claims are unused. Need to verify before deletion.
   - **Mitigation:** Deferred to future project. Only delete the 5 confirmed-empty files.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
