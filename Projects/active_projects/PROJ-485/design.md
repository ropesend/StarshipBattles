# PROJ-485: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Audit
- **Audit directory:** `Reviews/results/2026-05-20_210635_legacy-audit/`
- **Bundle counts:** Audit verified: 17 (across all sibling projects) | This bundle: 3 verified, 0 uncertain, 0 INFO, 0 deferred
- **Sibling projects:** PROJ-484, PROJ-486, PROJ-487, PROJ-488, PROJ-489, PROJ-490
- **Cluster identity:** carrier_dead_methods — three legacy static methods on `CarrierAIController` retained for pre-QA-C tests
- **Severity breakdown:** 0 CRITICAL, 3 MAJOR, 0 MINOR

## Initial Analysis
`CarrierAIController` has three methods that the audit's verifier confirmed are dead production code:

- `_find_tactical_launch_ability(self, ship, target_filter)` — `game/ai/carrier_controller.py:358-390`. Header comment: "Legacy ability-lookup helper (kept for test fixtures)." Modern equivalent: `_sum_launch_rate`. 0 production callers (grep-verified across `game/`).
- `_pop_fighter_cvs(cls, ship, count)` — `game/ai/carrier_controller.py:255-263`. Docstring: "retained for the pre-QA-C integration tests"; "new code should use `_pop_cvs_within_budget`." 0 production callers.
- `_pop_cvs(cls, ship, count)` — `game/ai/carrier_controller.py:265-300`. Docstring: "retained for the pre-QA-C tests and the fighter-recovery-test setup paths"; "new tactical launches go through `_pop_cvs_within_budget`." 0 direct production callers; only reached via `_pop_fighter_cvs` (transitively dead).

### Architecture
Production launch and CV-popping flow:
- Ability lookup: `_sum_launch_rate` (modern aggregation over launchable abilities; replaces the single-ability `_find_tactical_launch_ability` lookup).
- CV popping: `_pop_cvs_within_budget` (mass-budget-aware; replaces count-based `_pop_cvs` and `_pop_fighter_cvs`).

### Key Patterns to Reuse
- **Mass-budget popping**: `_pop_cvs_within_budget` is the canonical CV-popping path. Any test that needs CV pop behavior should call this directly with an appropriate budget.
- **Aggregated launch rate**: `_sum_launch_rate` aggregates across all launchable abilities — strictly more general than the legacy single-ability lookup.

### Dependencies & Risks
1. **Test introspection coverage** — Some tests may exist solely to introspect the dead methods' internal logic. If a test asserts behavior that the modern surface doesn't directly expose (e.g. "fighter-only count-based pop"), the test itself may be testing the legacy behavior. Either rewrite to assert against the modern surface's equivalent contract, or accept that the test goes away with the method.
2. **`_pop_cvs` depends on `_pop_fighter_cvs`** — Order of deletion: tests first, then `_pop_fighter_cvs` (frees `_pop_cvs` from its sole caller), then `_pop_cvs`. Or delete all three in the same PR after migrating tests.

### Opportunities Discovered
- ~83 LOC of dead code in a single file makes this a clean targeted PR.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
