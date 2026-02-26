# PROJ-235: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-26 | Project initialized | Starting point for Reduce complexity: filter_ships (CC 36) |
| 2026-02-26 | Function is REFACTORABLE (not skipped) | Multi-agent analysis confirmed: pure function, excellent test coverage (46 tests), clear invariants, single caller |
| 2026-02-26 | Extract `_passes_boolean_filter` helper | Pattern repeats 8+ times, contributes 32+ CC; generic helper reduces to ~4 CC |
| 2026-02-26 | Extract `_get_ship_status` helper | Centralizes status determination; makes ordering invariant explicit |
| 2026-02-26 | Extract `_passes_status_filter` helper | Encapsulates order-sensitive logic (destroyed > derelict > damaged > undamaged) |
| 2026-02-26 | Extract `_passes_capability_filters` helper | Groups all capability filters (warp, spaceyard, cargo, special abilities) |
| 2026-02-26 | Keep lazy imports inside `_passes_capability_filters` | Circular import avoidance is intentional per existing code comments |
| 2026-02-26 | Add 4+ test cases before refactoring | Safety analysis identified gaps: combined filters, both-sides-disabled, status priority |
| 2026-02-26 | 4-phase approach | Phase 1: Tests, Phase 2: Extract helpers, Phase 3: Refactor main, Phase 4: Verify |

## Detailed Rationale

### Why Extract Helper Functions (Not Restructure)?

The constraints specify "Prefer extracting helper methods over restructuring." The function's complexity comes from repetition, not from inherently complex logic. Extracting helpers:
1. Preserves the existing algorithm
2. Makes each filter category testable in isolation
3. Reduces CC through code reuse, not logic changes

### Why Status Order Matters

The status checks MUST be in this order:
1. `not ship.is_alive` (destroyed) - FIRST
2. `ship.is_derelict` - SECOND
3. `ship.is_damaged()` - THIRD
4. undamaged - LAST (catch-all)

A derelict ship is also damaged (by definition), so checking damaged first would misclassify derelict ships. Similarly, destroyed ships might have derelict or damaged flags set.

### Why Add Tests First (Phase 1)?

Safety analysis identified test coverage gaps:
- No tests for combined filters (status + capability together)
- No tests verifying both-sides-disabled returns empty
- No tests for status priority edge cases

Adding these tests BEFORE refactoring ensures we can detect any behavioral regressions.
