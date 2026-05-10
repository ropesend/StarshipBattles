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
This was a deletion-only project; no production code or behavior changed. 12 files were deleted whole (including `test_modifier_logic.py` 103 LOC, `test_testruncard_propulsion.py` 229 LOC, `test_unified_entry_guard.py` ~700 LOC, `test_system_tree_panel.py` 664 LOC) plus 1 file was relocated to `tests/regression/` (`tests/repro_issues/test_bug_12_energy_gen.py` → `tests/regression/test_generator_crew_requirement_design.py`). Whole-suite test count went from 16332 → 16306 (net -26 tests after counting overlaps with downstream PROJ-322/323 work). 3 false-positive CAT-2 claims in shard 08 (`test_facade_indices.py`, `test_selection.py`, `test_controllable_adapter_edge_cases.py`) were correctly REJECTED during third-pass verification — these files actually import real production classes despite the source review's claim. See findings/verification_report.md for details.

## Swarm Findings Summary
Combined analysis from individual agent reports in `findings/`.

### Architecture
PROJ-321 is the upstream project of PROJ-322 + PROJ-323. Its 12 whole-file deletions correctly invalidated 17 PROJ-322 tasks (target file no longer existed) and 41 PROJ-323 tasks. Each downstream worker re-checked file existence before each task and marked obsolete-skipped accordingly. The execution order PROJ-321 → PROJ-322 → PROJ-323 was strictly enforced.

### Key Patterns to Reuse
- **Skeptical third-pass verification** before destructive operations: PROJ-321 reused the OpenCode test-review's third-pass output but added a Claude-skeptical pre-implementation pass that caught 3 false-positive CAT-2 claims and 12 file path errors before any deletion happened.
- **Cross-project obsoletion check pattern**: every PROJ-322/323 task has a "verify file still exists" pre-step because PROJ-321 deletions are upstream. Future cleanup projects with sibling tiers should adopt the same pattern.

### Dependencies & Risks
1. **Test pollution risk** (mitigated): the first sharded test run after PROJ-321 cherry-pick had 4 flaky failures in `tests/integration/strategy/test_mutual_join_rendezvous.py`. They cleared on re-run alone or in the full suite. This is pre-existing flakiness in pytest-xdist parallel execution, NOT caused by PROJ-321 deletions (verified via baseline run at parent commit).

### Opportunities Discovered
- The 12 whole-file deletions revealed that several "test files" had no game imports at all (e.g., `test_modifier_logic.py` reimplemented production logic locally with zero `from game...` imports). A linter rule could prevent this in the future.
- The relocation pattern (Task 3.5: `test_bug_12_energy_gen.py` → `tests/regression/test_generator_crew_requirement_design.py`) demonstrates that some tests classified as "dead code" by automated review actually have regression-guard value if renamed/relocated to make their intent explicit.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
