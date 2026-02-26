# PROJ-246: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-26 | Project initialized | Starting point for Reduce complexity: filter_ships (CC 36) |
| 2026-02-26 | Function is refactorable (not skip) | Complexity from repeated patterns, not irreducible logic; 19 tests provide safety net |
| 2026-02-26 | Extract helpers as private module functions | Keeps related code together; underscore prefix signals internal use |
| 2026-02-26 | Create generic `_check_binary_filter()` | Pattern appears 4+ times; centralizes optimization; reduces ~30 lines |
| 2026-02-26 | Add safety tests before refactoring | Safety analysis identified gaps; tests provide safety net for refactoring |
| 2026-02-26 | Keep late imports inside helpers | Circular import avoidance requires imports stay local to functions |

---

## Detailed Decision Records

### Decision 1: Function is Refactorable

**Date:** 2026-02-26
**Decision:** Proceed with refactoring (not skip)

**Rationale:**
- The complexity comes from repeated patterns, not irreducible logic
- A state machine or parser would be irreducible; this is just repeated binary filter checks
- Test coverage is adequate (19 tests) with small gaps that can be filled
- Single production caller makes interface changes low-risk

**Alternative Considered:** Skip and add to skip list
**Why Rejected:** Clear extraction opportunities exist with low risk

---

### Decision 2: Extract Helpers as Private Module Functions

**Date:** 2026-02-26
**Decision:** Extract filter predicates as `_helper_name()` private functions in same file

**Rationale:**
- Keeps related code together for maintainability
- Underscore prefix signals internal use
- No need for separate module - these are specific to `filter_ships`

**Alternative Considered:** Create FilterPredicates class
**Why Rejected:** Over-engineering for simple stateless predicates

---

### Decision 3: Generic Binary Filter Helper

**Date:** 2026-02-26
**Decision:** Create `_check_binary_filter(filter_state, show_key, hide_key, has_property)` helper

**Rationale:**
- Pattern appears 4+ times in the function
- Centralizes the "if both True, skip check" optimization
- Reduces code by ~30 lines

**Alternative Considered:** Keep inline logic in each filter
**Why Rejected:** Defeats purpose of reducing complexity

---

### Decision 4: Add Safety Tests Before Refactoring

**Date:** 2026-02-26
**Decision:** Phase 1 adds tests for identified gaps before any code changes

**Tests to add:**
1. `test_filter_empty_ships_list` - Empty input returns empty output
2. `test_filter_with_empty_filter_state` - Missing keys default to show
3. `test_derelict_classified_as_derelict_not_damaged` - Status priority preserved
4. `test_combined_status_and_capability_filter` - Filter types interact correctly

**Rationale:**
- Safety analysis identified gaps
- Tests provide safety net for refactoring
- TDD principle: tests before changes

---

### Decision 5: Preserve Late Import Pattern

**Date:** 2026-02-26
**Decision:** Keep `FleetCapabilityCalculator` import inside helper functions, not at module level

**Rationale:**
- Original code has intentional late imports to avoid circular imports
- Moving to module level would break the build
- Each helper that needs it will import locally

**Note:** Import will appear in two helpers but this is acceptable for correctness.
