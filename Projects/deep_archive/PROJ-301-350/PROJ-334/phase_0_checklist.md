# PROJ-334 Phase 0 — Coverage gap audit

**Status:** Pending
**Goal:** Produce `findings/coverage_gap_audit.md` enumerating per-symbol coverage status. Gates Phase 1 scope.

## Task 0.1: Enumerate production symbols
- [ ] List every public function / method in `pathfinding.py` (per `design.md` table).
- [ ] List every public + private-but-load-bearing function/method in `galaxy_system_generator.py` (per `design.md` table).

## Task 0.2: Map existing tests to symbols
- [ ] For each row in `tests/unit/strategy/pathfinding/test_*.py`, identify which symbol(s) it exercises.
- [ ] For each row in `tests/unit/strategy/data/test_intrinsic_rng_determinism.py`, identify which symbol(s) it exercises.
- [ ] Record `<symbol> -> [test class.method, ...]` mapping.

## Task 0.3: Compute gap-list
- [ ] For each symbol, mark coverage as Covered / Partial / Uncovered.
- [ ] For Partial rows, name the specific edge case missing.
- [ ] For each Uncovered/Partial row, cross-reference to the candidate test name in `phase_1_checklist.md`.

## Task 0.4: Write `findings/coverage_gap_audit.md`
- [ ] Two tables: pathfinding-coverage and generator-coverage.
- [ ] Each row: Symbol | Status | Existing test(s) | Gap | Phase 1 test name.

## Verification
- [ ] Audit committed before any Phase 1 test work begins.
- [ ] Phase 1 candidate list pruned to match audit findings.
