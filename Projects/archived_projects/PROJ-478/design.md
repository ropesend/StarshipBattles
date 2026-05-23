# PROJ-478: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Test Review

- **Review directory:** `Reviews/results/2026-05-20_210550_test-review/`
- **Run date:** 2026-05-20
- **Priority tier for this project:** P0 (dead-trivial cleanup)
- **Categories included:** CAT-1 Trivial Pass, CAT-2 Tests Nothing Real, CAT-3 Dead Test Code

### Item Counts (P0 tier)
| Metric | Count |
|--------|-------|
| OpenCode CONFIRMED candidates for this tier (CAT-1 + CAT-2 + CAT-3) | 58 |
| Independently verified by Claude (entered the plan) | 44 |
| Needs rework (entered with adjusted suggestion) | 9 |
| Rejected (false positives) | 0 |
| Out of scope (intentional patterns / conftest advisory / deletion guards) | 5 |

### LOC Impact
- **Review-claimed CAT-1/2/3 reclaimable LOC:** ~620 (within total ~4,800 shard-findings number)
- **Verified-only LOC (sum of `loc_affected` across V + NR items):** ~580

### Summary of Categories Included
CAT-1 (vacuous assertions, import smoke tests, structural hasattr checks, `assert True` markers); CAT-2 (lambda replaces production method, `__new__` bypass + manual attribute wiring, phantom-method patches, documentation tests); CAT-3 (empty test classes, TDD-pending guards whose helper hasn't shipped).

## Initial Analysis

OpenCode's 16-shard audit reviewed 1,476 test files across 391,324 LOC, producing 305 Phase-1 claims and 322 verified findings (94% confirmation rate). The P0 tier — the highest-severity dead/trivial work — is dominated by **two patterns**:

1. **Workshop screen lambda-replacement cluster** (S01-F001..F013): a single file (`test_workshop_screen.py`) contains 13 CAT-2 tests that bypass `WorkshopScreen.__init__` and replace production methods with inline lambdas. Three of these 13 patch *phantom* methods that don't exist in production (the test name has a leading underscore, the production method doesn't). The phantom-method tests need rewriting, not just deletion, because deletion would leave save_ship / load_ship / on_select_target_pressed without coverage.

2. **Structural / smoke / hasattr clusters** (multiple shards): public-API surface tests like `isinstance(X, property)`, `assert callable(method)`, `assert not hasattr(module, "deleted_symbol")`. The last form is a legitimate CAT-3 regression guard (10 of the 322 verified findings were re-tagged as such during verification) and stays in the codebase; the first two are pure tautology and should be deleted.

## Swarm Findings Summary
Combined analysis from 16 shard verification reports + cross-shard cluster verification in `.agent_reports/2026-05-20_210550_test-review/`.

### Architecture
- Workshop screen and Race Browser Dialog both use `__new__` + manual attribute wiring patterns. **PROJ-322 / PROJ-347 explicitly document this pattern as intentional** for some UI test files; those documented files were excluded from this project as `intentional_smoke_test` per verification.
- Conftest files with no test functions are normal pytest structure (SUMMARY caveat #5). These were excluded as `conftest_advisory` rather than removed.

### Key Patterns to Reuse
- **Real construction + mocked dependencies**: see `tests/fixtures/ui_widget_factory.py:bypass_init` for the canonical UI-widget construction pattern. Phase 2 rewrites should adopt this when replacing lambda-replacement tests.
- **`@pytest.mark.skip`** for TDD-pending guards: see existing skip markers in `tests/regression/`. Phase 3 Task 3.2 uses this.

### Dependencies & Risks
1. **Phantom-method rewrites (Phase 2 Task 2.1)** depend on knowing the real production method signature. If `save_ship` / `load_ship` / `on_select_target_pressed` have changed shape since the review (2026-05-20), the rewrite plan needs adjustment.
2. **Codex tooling relocations (Phase 1 Task 1.20, Phase 2 Tasks 2.3 + 2.4)** require choosing the target directory. `tests/static_guards/` and `tests/projects/` are both established locations; pick the one the team already uses for agent-tooling validation.

### Opportunities Discovered
- The CAT-2 workshop-screen cluster is by far the largest single-file CAT-2 set (~150 LOC across 13 tests). Tackling it first delivers the highest visible LOC reduction.
- Three "documentation-linting" test files (codex consult, interagent discussion, codex project config) together account for ~280 LOC of `tests/unit/` that should not be in `tests/unit/`. Relocating them (rather than deleting) preserves their utility while clarifying the tests/ layout.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
