# PROJ-230: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-26 | Project initialized | Starting point for Reduce complexity: filter_ships (CC 36) |
| 2026-02-26 | Function is refactorable | CC 36 has clear repeated patterns, single caller, excellent test coverage |
| 2026-02-26 | Extract 5 predicate functions | One helper per filter dimension; status filter has unique semantics |
| 2026-02-26 | Require test fortification first | Status hierarchy mutual exclusivity is critical invariant needing explicit tests |
| 2026-02-26 | Preserve late imports | Keep FleetCapabilityCalculator imports inside helpers to avoid circular import risk |

---

## Detailed Decisions

### Decision 1: Function is Refactorable

**Date:** 2026-02-26

**Context:**
- CC 36 is well above threshold of 20
- Function has clear repeated patterns (5 filter pair blocks)
- Single caller with excellent test coverage
- Pure function with no side effects

**Alternatives Considered:**
1. Skip - complexity is inherent to the filtering logic
2. Refactor - extract helper functions to reduce complexity

**Rationale:**
The complexity is NOT irreducible. The 5 filter pair blocks follow an identical pattern that can be extracted. The status cascade can be converted to a classification approach. Test coverage is sufficient to catch regressions.

---

### Decision 2: Extract 5 Predicate Functions

**Date:** 2026-02-26

**Context:**
Structure analysis identified 5 distinct filter dimensions:
1. Warp capability
2. Spaceyard capability
3. Cargo presence
4. Special abilities (loop)
5. Status (cascade)

**Alternatives Considered:**
1. Single generic `_passes_boolean_filter()` helper with callback
2. Five specific `_passes_X_filter()` helpers
3. Data-driven filter configuration

**Rationale:**
Option 2 (specific helpers) chosen because:
- Status filter has unique semantics that don't fit generic pattern
- Specific helpers are more readable and debuggable
- Each helper can be tested in isolation
- Avoids over-abstraction for 5 call sites

---

### Decision 3: Require Test Fortification First

**Date:** 2026-02-26

**Context:**
Safety analysis identified critical test gaps:
- No test for status hierarchy mutual exclusivity
- No test for empty inputs
- No test for order preservation
- Only 2 of 5 special capabilities tested

**Rationale:**
The status filter mutual exclusivity is a critical invariant. The current `continue` statements are subtle and could be broken during refactoring. Adding explicit tests creates a safety net that catches regressions immediately.

---

### Decision 4: Preserve Late Imports

**Date:** 2026-02-26

**Context:**
The original function uses late imports to avoid circular dependencies:
```python
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
```

**Alternatives Considered:**
1. Move imports to module level
2. Keep imports inside helpers (same as original)

**Rationale:**
Option 2 chosen to minimize risk. The late imports work correctly in the original code. Moving them could introduce import order issues. The performance impact of repeated imports is negligible (Python caches).
