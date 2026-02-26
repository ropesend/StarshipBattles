# PROJ-241: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-26 | Project initialized | Starting point for Reduce complexity: filter_ships (CC 36) |
| 2026-02-26 | Proceed with refactoring | Function's complexity stems from regular repeating pattern (6 filter categories). Ideal for predicate extraction. |
| 2026-02-26 | Add tests before refactoring | Safety analysis identified 6 test coverage gaps. Adding tests first ensures regressions are caught. |
| 2026-02-26 | Use predicate extraction pattern | Each filter category becomes a `_passes_X_filter()` function returning bool. Main function becomes list comprehension. |
| 2026-02-26 | Separate status classification | Create `_classify_ship_status()` helper separate from `_passes_status_filter()`. Makes mutual exclusivity invariant explicit. |
| 2026-02-26 | Keep helpers in same file | Single caller pattern. Helpers are private implementation details (use `_` prefix). |
| 2026-02-26 | Preserve late imports | `FleetCapabilityCalculator` imported inside conditionals to avoid circular imports. Keep this pattern in extracted helpers. |

## Detailed Decision Records

### D1: Refactoring Approach

**Context:** `filter_ships` has CC 36, well above the 20 threshold.

**Options Considered:**
1. Skip function - add to complexity skip list
2. Inline simplification only - flatten conditionals, use guard clauses
3. Full predicate extraction - extract each filter category to helper

**Decision:** Option 3 - Full predicate extraction

**Rationale:**
- The 36 CC comes from 6 independent filter categories, each adding ~6 branches
- The pattern is highly regular and repeats identically across categories
- Extracting to predicates is mechanical and low-risk
- The function is pure with no side effects
- Good test coverage exists (39 tests)

### D2: Test-First Approach

**Context:** Safety analysis found 6 test coverage gaps.

**Gaps Identified:**
1. Combined filter interactions (multiple categories together)
2. Both-True filter pairs (verifying no-op behavior)
3. All-False status filters (should return empty list)
4. Empty ships list input
5. Multiple special capabilities simultaneously
6. Status priority edge cases (destroyed vs damaged)

**Decision:** Add these tests in Phase 1 before any code changes.

**Rationale:** Tests act as safety net. If we break invariants during extraction, tests will catch it. Adding tests first also documents expected behavior.

### D3: Status Filter Design

**Context:** Status cascade is highest-risk area. Current code:
```python
if not ship.is_alive:
    if not filter_state.get('show_destroyed', True):
        continue
    result.append(ship)
    continue  # Prevents double-classification
```

**Decision:** Separate into two helpers:
- `_classify_ship_status(ship) -> str` - returns 'destroyed'/'derelict'/'damaged'/'undamaged'
- `_passes_status_filter(ship, filter_state) -> bool` - uses classification

**Rationale:**
- Classification logic is isolated and testable independently
- Filter lookup becomes a simple dict lookup
- Eliminates risk of double-append bugs
- Makes mutual exclusivity invariant explicit in code

### D4: File Organization

**Context:** Where to put 6-7 new helper functions?

**Options:**
1. New `fleet_filter_helpers.py` module
2. Keep in `fleet_report_filters.py` as private functions

**Decision:** Option 2 - Keep in same file with `_` prefix

**Rationale:**
- Single production caller (`FleetListViewModel`)
- Helpers are implementation details of `filter_ships`
- No reuse need from other modules
- Reduces module proliferation
