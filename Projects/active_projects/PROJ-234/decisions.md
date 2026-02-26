# PROJ-234: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-26 | Project initialized | Starting point for Reduce complexity: filter_ships (CC 36) |
| 2026-02-26 | Proceed with refactoring (not skip) | Complexity is additive (independent filters), not irreducible. Good test coverage. Single caller. |
| 2026-02-26 | Extract predicate functions approach | Each filter already isolated in code blocks. Helpers preserve optimization. Clean comprehension result. |
| 2026-02-26 | Add tests before refactoring (Phase 1) | Safety analysis found gaps. Tests document expected behavior and provide regression safety. |
| 2026-02-26 | Create generic `_passes_binary_filter()` | Pattern repeats 4+ times. Single helper reduces duplication and is easier to test. |
| 2026-02-26 | Move late import to module level | Repeated imports inside loop inefficient. Use TYPE_CHECKING guard to avoid circular import. |

---

## Detailed Decision Records

### Decision 1: Refactorable Assessment

**Date:** 2026-02-26
**Decision:** Proceed with refactoring (not skip)

**Rationale:**
- Complexity is additive (independent filter checks), not tangled state machine
- Good test coverage exists (19 test methods)
- Single production caller with controlled interface
- Pure function with no side effects

**Alternative considered:** Skip if complexity were irreducible (e.g., genuine state machine)

---

### Decision 2: Extract Predicate Functions Approach

**Date:** 2026-02-26
**Decision:** Extract 5-6 helper functions, one per filter category

**Rationale:**
- Each filter type is already isolated in its own code block
- Helpers can preserve the both-true optimization
- Main function becomes simple comprehension
- Matches existing codebase patterns

**Alternative considered:** Filter chain/strategy pattern - rejected as over-engineering for this case

---

### Decision 3: Add Tests Before Refactoring

**Date:** 2026-02-26
**Decision:** Phase 1 adds edge case tests before any code changes

**Rationale:**
- Safety analysis identified gaps (both-false filters, empty filter_state)
- Tests provide regression safety net
- Documents expected behavior before changes

---

### Decision 4: Keep Late Import Pattern (Modified)

**Date:** 2026-02-26
**Decision:** Move late import to module level with TYPE_CHECKING guard

**Rationale:**
- Current repeated imports inside loop are inefficient
- TYPE_CHECKING avoids circular import at runtime
- Single import location is cleaner

---

### Decision 5: Generic Binary Filter Helper

**Date:** 2026-02-26
**Decision:** Create reusable `_passes_binary_filter()` for warp/spaceyard/special patterns

**Rationale:**
- Pattern repeats 4+ times with minor variations
- Single helper reduces duplication
- Easier to test the pattern once
