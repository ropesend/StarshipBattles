# PROJ-480: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Test Review

- **Review directory:** `Reviews/results/2026-05-20_210550_test-review/`
- **Run date:** 2026-05-20
- **Priority tier for this project:** P2 (opportunistic polish)
- **Categories included:** CAT-8 Needless Complexity, CAT-9 Simplification, CAT-10 Parametrize, CAT-11 Fragile Assertion, CAT-12 Logic-Heavy

### Item Counts (P2 tier)
| Metric | Count |
|--------|-------|
| OpenCode CONFIRMED candidates for this tier (CAT-8 + CAT-9 + CAT-10 + CAT-11 + CAT-12) | 185 |
| Independently verified by Claude (entered the plan) | 145 |
| Needs rework (entered with adjusted suggestion) | 4 |
| Rejected (false positives) | 4 |
| Out of scope (well-suited tests, intentional patterns) | 32 |

### LOC Impact
- **Review-claimed CAT-8..12 reclaimable LOC:** ~2,500 (within total ~4,800 shard-findings number)
- **Verified-only LOC (sum of `loc_affected` across V + NR items):** ~1,900

### Summary of Categories Included
CAT-8 (deeply nested patch stacks, oversized helpers, excessive mock wiring); CAT-9 (in-method imports, repeated inline definitions, unused factory fixtures); CAT-10 (clusters of structurally-identical tests ≥3 members differing only in input/output — textbook `@pytest.mark.parametrize` candidates); CAT-11 (exact dict / pixel-coordinate / list assertions brittle to formatting); CAT-12 (for-loops + conditional branches in test bodies, formula re-derivation).

## Initial Analysis

P2 is dominated by **CAT-10 (88 findings)** — most are 3-7 member clusters where tests differ only in input value. These are mechanical refactors but high-volume; sequencing CAT-10 as Phase 3 (after CAT-9 simplification clears repeated boilerplate that would otherwise tangle the parametrize) makes the work cleaner.

Several P2 findings overlap with P0 / P1 cleanup:
- CAT-9 wrapping CAT-2 lambdas in `test_workshop_screen.py` is mostly subsumed when PROJ-478 Phase 2 deletes the underlying tests.
- DUP-002 (P1) absorbs S14-F010 inline duplicate (P2 CAT-9).
- DUP-005 + HLP-006 (P1) absorbs `_make_empire` cluster setup that touches multiple P2 CAT-9 items.

Coordination notes are flagged inline in each task with `_(coord)_` so the implementer doesn't double-touch a file. Sequencing the projects P0 → P1 → P2 maximizes those absorptions.

## Swarm Findings Summary
Combined analysis from 16 shard verification reports + cross-shard cluster verification in `.agent_reports/2026-05-20_210550_test-review/`.

### Architecture
- **Existing `_make_*` factory patterns** appear in many test files but aren't consistently used by all tests in their own file (Task 1.8, Task 1.16, Task 1.21, Task 1.23). Phase 1 sweeps these up.
- **`patch.multiple`** is the canonical Python pattern for collapsing multi-patch stacks; Phase 2 applies it broadly.
- **Pre-computed reference values** (from engineering notes or formula docs) are preferred over re-derived expected values inside test bodies (Phase 5 Tasks 5.7, 5.17). When the test recomputes the production formula, the test can't catch a production bug in that formula.

### Key Patterns to Reuse
- **`@pytest.mark.parametrize`** with `(input, expected)` tuples — Phase 3 baseline pattern.
- **`scope="module"` fixtures returning MagicMock** instead of real pygame_gui.UIManager — see `test_empire_treasury_panel.py` for the established pattern (Task 1.17 generalizes it).
- **Seeded RNG** with deterministic assertions instead of stochastic branching (Tasks 5.9, 5.11) — eliminates flaky-test risk.

### Dependencies & Risks
1. **Coordination with PROJ-478 and PROJ-479**: ~10 P2 tasks reference cross-project work. Sequence P0 → P1 → P2 to maximize absorption; otherwise some P2 work is wasted effort or has merge conflicts.
2. **CAT-10 verifier discipline**: verification rejected CAT-10 clusters with <3 members and clusters where members exercise different pipeline stages (e.g., S06-F005 superweapon per-weapon, S02-F005 pipeline unification ability classes). Don't force parametrize on those.
3. **CAT-12 logic-heavy rewrites** that touch integration tests (Tasks 5.11-5.13) may surface real non-determinism. Be ready to investigate test failures rather than restoring the retry loops.

### Opportunities Discovered
- Phase 3 (CAT-10) is the highest-volume, lowest-risk phase. Knocking out the 55 parametrize clusters as a batch yields the largest single LOC reduction in this project (~1,200 LOC).
- Phase 5 (CAT-12) flushes out hidden test-suite non-determinism — several integration tests "pass" today only because of silent-pass guards or retry loops. Removing those will reveal real bugs to fix.
- Phase 4 (CAT-11) per-task LOC delta is tiny but each one materially improves test readability and refactor-resistance.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
